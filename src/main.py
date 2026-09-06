import argparse
from datetime import datetime

import pandas as pd
from ortools.sat.python import cp_model

from config import AMOUNT_COLUMN, CSV_FILE, DEFAULT_LIMIT, NUM_SEARCH_WORKERS, OUTPUT_FILE
from excel_writer import ExcelWriter
from solution_collector import SolutionCollector


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する(目標合計値はスペース区切りで複数指定可。件数上限はconfig.iniのlimitを使う)。"""
    parser = argparse.ArgumentParser(description="数値の組み合わせ探索")
    parser.add_argument(
        "--target",
        type=str,
        nargs="+",
        required=True,
        help="目標合計値(スペース区切りで複数指定可。各値の中のカンマは桁区切りとして無視される。"
        "複数指定すると、行が重複しない組み合わせを目標ごとに探索する)",
    )
    args = parser.parse_args()
    args.target = [int(value.replace(",", "")) for value in args.target]
    return args


def find_combinations(
    amounts: list[int], targets: list[int], limit: int, callback=None
) -> list[list[tuple[int, list[int]]]]:
    """amountsの部分集合から、targetsの各値に合計が一致するグループを、行の重複なしにlimit件まで探索する。

    戻り値は解のリストで、各解は[(target, その目標に割り当てられた行インデックス一覧), ...]という形式。
    """
    model = cp_model.CpModel()
    n = len(amounts)
    m = len(targets)
    # variables[k * n + i] が「行iを目標targets[k]のグループに割り当てるか」を表す
    variables = [model.NewBoolVar(f"x_{k}_{i}") for k in range(m) for i in range(n)]
    # used[k] が「目標targets[k]に対して実際に組み合わせを割り当てるか」を表す
    # (Falseの場合、その目標には行を割り当てず、Summaryは空行として出力する)
    used = [model.NewBoolVar(f"used_{k}") for k in range(m)]

    for k, target in enumerate(targets):
        group_sum = sum(amounts[i] * variables[k * n + i] for i in range(n))
        group_count = sum(variables[k * n + i] for i in range(n))
        model.Add(group_sum == target).OnlyEnforceIf(used[k])
        model.Add(group_count >= 1).OnlyEnforceIf(used[k])
        model.Add(group_count == 0).OnlyEnforceIf(used[k].Not())

    # 少なくとも1つの目標値には組み合わせが割り当てられている必要がある
    model.AddBoolOr(used)

    for i in range(n):
        model.Add(sum(variables[k * n + i] for k in range(m)) <= 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = NUM_SEARCH_WORKERS
    solver.parameters.enumerate_all_solutions = True

    def decode(flat_indexes: list[int]) -> list[tuple[int, list[int]]]:
        groups: list[list[int]] = [[] for _ in range(m)]
        for idx in flat_indexes:
            k, i = divmod(idx, n)
            groups[k].append(i)
        return [(targets[k], groups[k]) for k in range(m)]

    wrapped_callback = None
    if callback is not None:
        wrapped_callback = lambda solution_no, flat_indexes: callback(solution_no, decode(flat_indexes))

    collector = SolutionCollector(variables, limit=limit, callback=wrapped_callback)
    solver.Solve(model, collector)

    return [decode(flat_indexes) for flat_indexes in collector.solutions]


def print_solution(df: pd.DataFrame, solution_no: int, groups: list[tuple[int, list[int]]]) -> None:
    """見つかった解1件分を、目標値ごとに区切って標準出力に表示する(find_combinationsのcallbackとして渡す)。"""
    print("=" * 30)
    print(f"解: {solution_no}")
    for target, indexes in groups:
        print(f"--- target={target} ---")
        if not indexes:
            print("(組み合わせなし)")
            continue
        print(df.iloc[indexes])


def main() -> None:
    """CSVを読み込み、目標数値に一致する組み合わせを探索してExcelに出力する。"""
    args = parse_args()

    df = pd.read_csv(CSV_FILE)
    df[AMOUNT_COLUMN] = df[AMOUNT_COLUMN].astype(str).str.replace(",", "", regex=False).astype(int)
    amounts = df[AMOUNT_COLUMN].tolist()

    solutions = find_combinations(
        amounts,
        targets=args.target,
        limit=DEFAULT_LIMIT,
        callback=lambda solution_no, groups: print_solution(df, solution_no, groups),
    )

    if not solutions:
        print("見つかりませんでした")
        return

    now = datetime.now()
    date_dir = OUTPUT_FILE.parent / now.strftime("%Y%m%d")
    output_path = date_dir / f"{OUTPUT_FILE.stem}_{now.strftime('%Y%m%d_%H%M%S')}{OUTPUT_FILE.suffix}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ExcelWriter().write(df=df, solutions=solutions, path=str(output_path))
    print(f"処理完了: {output_path}")


if __name__ == "__main__":
    main()
