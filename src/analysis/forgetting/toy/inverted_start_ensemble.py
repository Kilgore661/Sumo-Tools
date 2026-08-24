"""Command-line entry point for the TI versus T0 ensemble."""

from .constant_start_ensemble import main


if __name__ == "__main__":
    main(default_initialization="inverted")
