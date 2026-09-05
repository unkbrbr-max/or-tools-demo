import argparse

import pandas as pd
from ortools.sat.python import cp_model

from config import AMOUNT_COLUMN, CSV_FILE, DEFAULT_LIMIT, NUM_SEARCH_WORKERS, OUTPUT_FILE
from excel_writer import ExcelWriter
from solution_collector import SolutionCollector


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する(目標合計値のみ受け取る。件数上限はconfig.iniのlimitを使う)。"""
    parser = argparse.ArgumentParser(description="数値の組み合わせ探索")
    parser.add_argument("--target", type=int, default=0, help="目標合計値")
    return parser.parse_args()


def find_combinations(amounts: list[int], target: int, limit: int, callback=None) -> list[tuple[int, ...]]:
    """amountsの部分集合のうち合計がtargetと一致する組み合わせをlimit件まで探索する。"""
    model = cp_model.CpModel()
    variables = [model.NewBoolVar(f"x_{i}") for i in range(len(amounts))]

    model.Add(sum(amount * var for amount, var in zip(amounts, variables)) == target)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = NUM_SEARCH_WORKERS
    solver.parameters.enumerate_all_solutions = True

    collector = SolutionCollector(variables, limit=limit, callback=callback)
    solver.Solve(model, collector)

    return collector.solutions


def print_solution(df: pd.DataFrame, solution_no: int, indexes: list[int]) -> None:
    """見つかった解1件分の対象行を標準出力に表示する(find_combinationsのcallbackとして渡す)。"""
    print("=" * 30)
    print(f"解: {solution_no}")
    print(df.iloc[indexes])


def main() -> None:
    """CSVを読み込み、目標数値に一致する組み合わせを探索してExcelに出力する。"""
    args = parse_args()

    df = pd.read_csv(CSV_FILE)
    amounts = df[AMOUNT_COLUMN].astype(int).tolist()

    solutions = find_combinations(
        amounts,
        target=args.target,
        limit=DEFAULT_LIMIT,
        callback=lambda solution_no, indexes: print_solution(df, solution_no, indexes),
    )

    if not solutions:
        print("見つかりませんでした")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ExcelWriter().write(df=df, solutions=solutions, path=str(OUTPUT_FILE))
    print("処理完了")


if __name__ == "__main__":
    main()
