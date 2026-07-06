"""Command-line producer for the latest parsed New Banzuke artifact."""

from .api import produce_new_banzuke


if __name__ == "__main__":
    output = produce_new_banzuke()
    print(f"Wrote New Banzuke {output.date} to {output.path}")
