from pathlib import Path

# 入力データのCSVパス
CSV_FILE = Path("data/input.csv")
# 結果を書き出すExcelファイルのパス
OUTPUT_FILE = Path("data/result.xlsx")
# 探索を打ち切るまでに集める解の最大件数のデフォルト
DEFAULT_LIMIT = 100
# CP-SATソルバーの並列探索ワーカー数
NUM_SEARCH_WORKERS = 4

# 数値を表すCSV列名
AMOUNT_COLUMN = "数値"
# タイトルを表すCSV列名
TITLE_COLUMN = "タイトル"
# Detailsシートで先頭に固定する列の並び順(数値の右にタイトルを表示する)
DETAIL_LEADING_COLUMNS = ["solution_no", "source_index", AMOUNT_COLUMN, TITLE_COLUMN]
