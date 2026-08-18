import importlib
import sys


def test_parser2_import_does_not_replace_stdout() -> None:
    before = sys.stdout

    importlib.import_module("src.infra.parser.parser2")

    assert sys.stdout is before
