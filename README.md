# or_tool_demo

CSVの数値データから、合計が指定した目標値と一致する組み合わせをCP-SATソルバー(OR-Tools)で探索し、結果をExcelに出力するツールです。

## セットアップ手順

1. [python.org](https://www.python.org/downloads/) からPython 3.12以上をダウンロードしてインストール
   1. バージョン（3.12以上）のDownload > Windows installerの順でダウンロード
   2. ダウンロードファイルを右クリック > 管理者として実行
   3. インストーラの最初の画面で **「Add python.exe to PATH」** にチェック
   4. Install Now
2. このリポジトリ一式をコピー
3. コマンドプロンプトでリポジトリのフォルダに移動し、`setup.bat` をダブルクリックで実行

## 実行方法

セットアップ後は `run.bat`をダブルクリック実行してください。

- `target`: 合計を一致させたい目標合計値
- `limit`: 収集する解の最大件数(省略時は`src\constants.py`の`DEFAULT_LIMIT`)

結果は `data\result.xlsx` に出力されます(Summaryシート・Detailsシート)。

## データ

`data\input.csv` に `タイトル`, `数値` の2列でデータを用意してください。

```
"タイトル","数値"
"タイトル001",2314606
"タイトル002",7866936
```

## その他
### 探索負荷軽減／高速化したいとき
`src/constants.py`の`NUM_SEARCH_WORKERS`の値を変更してください。
値が小さいほど並列の探索数が減り、負荷が軽減されます。
値が大きいほど並列の探索数が増えることで、短時間での探索を期待できますが負荷が増します。