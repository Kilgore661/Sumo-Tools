from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_RUN_DIR = Path("files/output/toy_elo_predictive_convergence_sweep/20260706_101659_seed1")


def parse_ints(value: str) -> set[int]:
    return {int(part.strip()) for part in value.split(",") if part.strip()}


def read_points(
    path: Path,
    *,
    x_column: str,
    y_column: str,
    only_converged: bool,
    exclude_players: set[int],
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if only_converged and row.get("converged") != "1":
                continue
            if not row.get(x_column) or not row.get(y_column):
                continue
            player_count = int(row[x_column])
            if player_count in exclude_players:
                continue
            points.append((float(player_count), float(row[y_column])))
    return points


def solve_3x3(matrix: list[list[float]], vector: list[float]) -> tuple[float, float, float]:
    rows = [matrix[i][:] + [vector[i]] for i in range(3)]
    for pivot_index in range(3):
        best_row = max(
            range(pivot_index, 3),
            key=lambda row_index: abs(rows[row_index][pivot_index]),
        )
        if abs(rows[best_row][pivot_index]) < 1e-12:
            raise ValueError("cannot fit quadratic: normal-equation matrix is singular")
        rows[pivot_index], rows[best_row] = rows[best_row], rows[pivot_index]

        pivot = rows[pivot_index][pivot_index]
        for column in range(pivot_index, 4):
            rows[pivot_index][column] /= pivot

        for row_index in range(3):
            if row_index == pivot_index:
                continue
            factor = rows[row_index][pivot_index]
            for column in range(pivot_index, 4):
                rows[row_index][column] -= factor * rows[pivot_index][column]

    return rows[0][3], rows[1][3], rows[2][3]


def fit_quadratic(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    if len(points) < 3:
        raise ValueError("need at least three points to fit a quadratic")

    n = float(len(points))
    sx = sum(x for x, _ in points)
    sx2 = sum(x**2 for x, _ in points)
    sx3 = sum(x**3 for x, _ in points)
    sx4 = sum(x**4 for x, _ in points)
    sy = sum(y for _, y in points)
    sxy = sum(x * y for x, y in points)
    sx2y = sum(x**2 * y for x, y in points)

    matrix = [
        [sx4, sx3, sx2],
        [sx3, sx2, sx],
        [sx2, sx, n],
    ]
    vector = [sx2y, sxy, sy]
    return solve_3x3(matrix, vector)


def predict(x: float, coefficients: tuple[float, float, float]) -> float:
    a, b, c = coefficients
    return a * x * x + b * x + c


def r_squared(points: list[tuple[float, float]], coefficients: tuple[float, float, float]) -> float:
    mean_y = sum(y for _, y in points) / len(points)
    ss_tot = sum((y - mean_y) ** 2 for _, y in points)
    ss_res = sum((y - predict(x, coefficients)) ** 2 for x, y in points)
    return 1.0 if ss_tot == 0.0 else 1.0 - ss_res / ss_tot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fit y = a*n^2 + b*n + c from a toy Elo summary.csv.")
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=DEFAULT_RUN_DIR,
        help="Run directory containing summary.csv.",
    )
    parser.add_argument("--summary", type=Path, default=None, help="Path to summary.csv.")
    parser.add_argument("--x-column", default="players")
    parser.add_argument("--y-column", default="first_stable_event")
    parser.add_argument("--include-unconverged", action="store_true")
    parser.add_argument(
        "--exclude-players",
        default="10",
        help="Comma-separated player counts to exclude. Defaults to 10.",
    )
    parser.add_argument(
        "--include-all-players",
        action="store_true",
        help="Ignore --exclude-players and fit all rows.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary_path = args.summary or args.run_dir / "summary.csv"
    exclude_players = set() if args.include_all_players else parse_ints(args.exclude_players)
    points = read_points(
        summary_path,
        x_column=args.x_column,
        y_column=args.y_column,
        only_converged=not args.include_unconverged,
        exclude_players=exclude_players,
    )
    coefficients = fit_quadratic(points)
    r2 = r_squared(points, coefficients)
    a, b, c = coefficients

    print(f"Read {len(points)} points from {summary_path}")
    print(f"x: {args.x_column}")
    print(f"y: {args.y_column}")
    print(f"excluded players: {sorted(exclude_players)}")
    print()
    print(f"f(n) = {a:.15g} n^2 + {b:.15g} n + {c:.15g}")
    print(f"R^2 = {r2:.15g}")
    print()
    print("points:")
    for x, y in points:
        print(f"  n={int(x):>4} y={y:>10.3f} fitted={predict(x, coefficients):>10.3f}")


if __name__ == "__main__":
    main()
