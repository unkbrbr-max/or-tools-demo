from typing import Sequence

import pandas as pd

from constants import AMOUNT_COLUMN, DETAIL_LEADING_COLUMNS


class ExcelWriter:
    """見つかった解の一覧をExcelファイル(Summary/Detailsシート)として出力する。"""

    def write(self, df: pd.DataFrame, solutions: Sequence[Sequence[int]], path: str) -> None:
        """solutions(各要素はdfの行インデックス集合)をSummaryシートとDetailsシートに分けてpathへ書き出す。"""
        summary_rows, detail_rows = self._build_rows(df=df, solutions=solutions)

        summary_df = pd.DataFrame(summary_rows)
        details_df = pd.concat(detail_rows, ignore_index=True) if detail_rows else pd.DataFrame()

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            details_df.to_excel(writer, sheet_name="Details", index=False)

    def _build_rows(self, df: pd.DataFrame, solutions: Sequence[Sequence[int]]):
        """解ごとにSummary用の集計行とDetails用の明細DataFrameを組み立てる。"""
        summary_rows = []
        detail_rows = []

        for solution_no, indexes in enumerate(solutions, start=1):
            indexes = list(indexes)
            result = df.iloc[indexes].copy()

            result.insert(0, "source_index", indexes)
            result.insert(0, "solution_no", solution_no)

            remaining_columns = [c for c in result.columns if c not in DETAIL_LEADING_COLUMNS]
            result = result[DETAIL_LEADING_COLUMNS + remaining_columns]

            summary_rows.append({
                "solution_no": solution_no,
                "件数": len(indexes),
                "合計": result[AMOUNT_COLUMN].sum(),
                "indexes": ",".join(map(str, indexes)),
            })

            detail_rows.append(result)

        return summary_rows, detail_rows
