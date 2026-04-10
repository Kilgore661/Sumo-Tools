from __future__ import annotations

import sys

from .runner import build_run_all_parser, execute_run_all, validate_k_args


def main() -> None:
    parser = build_run_all_parser()
    typed_argv = sys.argv[1:]
    args = parser.parse_args()
    validate_k_args(parser, args)
    execute_run_all(args, typed_argv, module_name="src.analysis.equelo.expt2.run_all")


if __name__ == "__main__":
    main()
