import configparser
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.ini"

_DEFAULTS = {
    "csv_file": "data/input.csv",
    "output_file": "data/result.xlsx",
    "limit": "100",
    "amount_column": "数値",
}

_parser = configparser.ConfigParser(defaults=_DEFAULTS)
_parser.read(CONFIG_FILE, encoding="utf-8")
_section = _parser["DEFAULT"]

CSV_FILE = Path(_section["csv_file"])
OUTPUT_FILE = Path(_section["output_file"])
DEFAULT_LIMIT = _section.getint("limit")
AMOUNT_COLUMN = _section["amount_column"]
