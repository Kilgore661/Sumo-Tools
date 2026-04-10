from __future__ import annotations

import sys

from .runner import build_single_parser, execute_single_run, validate_k_args


def main() -> None:
    parser = build_single_parser()
    typed_argv = sys.argv[1:]
    args = parser.parse_args()
    validate_k_args(parser, args)
    execute_single_run(args, typed_argv, module_name="src.analysis.equelo.expt2")
