from typing import Sequence

import pandas as pd

from config import AMOUNT_COLUMN, TITLE_COLUMN

# Detailsシートで先頭に固定する列の並び順(数値の右にタイトルを表示する)
DETAIL_LEADING_COLUMNS = ["solution_no", "target", "source_index", AMOUNT_COLUMN, TITLE_COLUMN]

# 1件の解: 目標値ごとの(target, 対象行インデックス一覧)のリスト
Solution = Sequence[tuple[int, Sequence[int]]]


class ExcelWriter:
    """見つかった解の一覧をExcelファイル(Summary/Detailsシート)として出力する。"""

    def write(self, df: pd.DataFrame, solutions: Sequence[Solution], path: str) -> None:
        """solutions(各要素は目標値ごとの(target, 対象行インデックス一覧)のリスト)をSummary/Detailsシートに分けてpathへ書き出す。"""
        summary_rows, detail_rows = self._build_rows(df=df, solutions=solutions)

        summary_df = pd.DataFrame(summary_rows)
        details_df = pd.concat(detail_rows, ignore_index=True) if detail_rows else pd.DataFrame()

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            details_df.to_excel(writer, sheet_name="Details", index=False)

    def _build_rows(self, df: pd.DataFrame, solutions: Sequence[Solution]):
        """解ごと・目標値ごとにSummary用の集計行とDetails用の明細DataFrameを組み立てる。"""
        summary_rows = []
        detail_rows = []

        for solution_no, groups in enumerate(solutions, start=1):
            for target, indexes in groups:
                indexes = list(indexes)
                result = df.iloc[indexes].copy()

                result.insert(0, "source_index", indexes)
                result.insert(0, "target", target)
                result.insert(0, "solution_no", solution_no)

                remaining_columns = [c for c in result.columns if c not in DETAIL_LEADING_COLUMNS]
                result = result[DETAIL_LEADING_COLUMNS + remaining_columns]

                summary_rows.append({
                    "solution_no": solution_no,
                    "target": target,
                    "件数": len(indexes),
                    "合計": result[AMOUNT_COLUMN].sum(),
                    "indexes": ",".join(map(str, indexes)),
                })

                detail_rows.append(result)

        return summary_rows, detail_rows
