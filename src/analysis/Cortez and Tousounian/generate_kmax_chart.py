#!/usr/bin/env python3
"""Generate a standalone Plotly chart of K_max(q, R).

Here R is the full rating span: the largest difference between any two true
ratings.  In the usual 0-to-1 Elo scoring convention, the sufficient bound is

    K_max(q, R) = ln(10)/(2q) * sech^2((1 + R)ln(10)/(2q)).

The generated HTML loads Plotly from a pinned CDN and otherwise has no external
Python dependencies.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from string import Template


PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"
MIN_PLOTTED_VALUE = 1e-300
FIXED_R_VALUES = [10.0, 100.0, 400.0]


def nonnegative_number(text: str) -> float:
    value = float(text)
    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than or equal to zero")
    return value


def positive_number(text: str) -> float:
    value = float(text)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("must be a finite number greater than zero")
    return value


def positive_integer(text: str) -> int:
    value = int(text)
    if value < 2:
        raise argparse.ArgumentTypeError("must be an integer of at least 2")
    return value


def peak_z() -> float:
    """Solve 2 z tanh(z) = 1, which locates the maximum over q."""
    z = 0.77
    for _ in range(20):
        tanh_z = math.tanh(z)
        function = 2 * z * tanh_z - 1
        derivative = 2 * tanh_z + 2 * z / math.cosh(z) ** 2
        z -= function / derivative
    return z


def log_k_max(q: float, rating_span: float) -> float:
    """Return ln(K_max), evaluated without overflowing cosh."""
    eta = 1 + rating_span
    a = math.log(10) / (2 * q)
    x = abs(a * eta)
    log_cosh = x - math.log(2) + math.log1p(math.exp(-2 * x))
    return math.log(a) - 2 * log_cosh


def k_max(q: float, rating_span: float) -> float:
    """Return K_max, flooring only values too tiny for a logarithmic plot."""
    return max(math.exp(log_k_max(q, rating_span)), MIN_PLOTTED_VALUE)


def logspace(minimum: float, maximum: float, samples: int) -> list[float]:
    log_minimum = math.log10(minimum)
    log_maximum = math.log10(maximum)
    return [
        10 ** (log_minimum + i * (log_maximum - log_minimum) / samples)
        for i in range(samples + 1)
    ]


def display_number(value: float) -> str:
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:g}"


def filename_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:g}".replace("+", "").replace("-", "minus").replace(".", "p")


def fixed_output_filename(rating_spans: list[float]) -> str:
    values = "-".join(filename_number(value) for value in rating_spans)
    return f"kmax-fixed-r-{values}.html"


def scientific(value: float, digits: int = 3) -> str:
    coefficient, exponent = f"{value:.{digits - 1}e}".split("e")
    return f"{coefficient}e{int(exponent):+d}".replace("e-", "e−").replace("e+", "e+")


def exponent_ticks(log_minimum: float, log_maximum: float) -> tuple[list[float], list[str]]:
    lower = math.floor(log_minimum)
    upper = math.ceil(log_maximum)
    span = upper - lower
    if span <= 6:
        step = 1
    elif span <= 16:
        step = 2
    elif span <= 50:
        step = 5
    else:
        step = 10

    first = math.ceil(lower / step) * step
    exponents = list(range(first, upper + 1, step))
    if not exponents:
        exponents = [lower, upper]
    values = [10.0**exponent for exponent in exponents]
    labels = [f"1e{str(exponent).replace('-', '−')}" for exponent in exponents]
    return values, labels


def build_html(
    rating_span: float,
    q_minimum: float,
    q_maximum: float,
    samples: int,
    reference_q: float,
) -> str:
    q_values = logspace(q_minimum, q_maximum, samples)
    k_values = [k_max(q, rating_span) for q in q_values]

    z = peak_z()
    eta = 1 + rating_span
    q_peak = math.log(10) * eta / (2 * z)
    k_peak = k_max(q_peak, rating_span)
    k_reference = k_max(reference_q, rating_span)
    peak_visible = q_minimum <= q_peak <= q_maximum
    reference_visible = q_minimum <= reference_q <= q_maximum

    visible_values = list(k_values)
    if peak_visible:
        visible_values.append(k_peak)
    if reference_visible:
        visible_values.append(k_reference)
    visible_logs = [math.log10(value) for value in visible_values]
    y_log_minimum = min(visible_logs) - 0.25
    y_log_maximum = max(visible_logs) + 0.25
    tick_values, tick_labels = exponent_ticks(y_log_minimum, y_log_maximum)

    r_text = display_number(rating_span)
    summary = (
        f"Interactive plot of K max against q for a full rating span R of {r_text}. "
        f"The global maximum occurs near q equals {q_peak:,.1f}, where K max is "
        f"approximately {scientific(k_peak)}."
    )

    substitutions = {
        "plotly_cdn": PLOTLY_CDN,
        "r_text": r_text,
        "summary_json": json.dumps(summary, ensure_ascii=False),
        "q_values": json.dumps(q_values, separators=(",", ":")),
        "k_values": json.dumps(k_values, separators=(",", ":")),
        "q_peak": json.dumps(q_peak),
        "k_peak": json.dumps(k_peak),
        "peak_visible": json.dumps(peak_visible),
        "reference_q": json.dumps(reference_q),
        "k_reference": json.dumps(k_reference),
        "reference_visible": json.dumps(reference_visible),
        "q_log_minimum": json.dumps(math.log10(q_minimum)),
        "q_log_maximum": json.dumps(math.log10(q_maximum)),
        "y_log_minimum": json.dumps(y_log_minimum),
        "y_log_maximum": json.dumps(y_log_maximum),
        "tick_values": json.dumps(tick_values, separators=(",", ":")),
        "tick_labels": json.dumps(tick_labels, ensure_ascii=False, separators=(",", ":")),
        "reference_annotation": json.dumps(
            f"q = {reference_q:,.4g}<br>K<sub>max</sub> ≈ {scientific(k_reference)}",
            ensure_ascii=False,
        ),
        "peak_annotation": json.dumps(
            f"maximum<br>q ≈ {q_peak:,.4g}<br>K<sub>max</sub> ≈ {scientific(k_peak)}",
            ensure_ascii=False,
        ),
    }

    template = Template(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>K max as q varies, R = $r_text</title>
  <script src="$plotly_cdn"></script>
  <style>
    :root {
      color-scheme: light dark;
      font-family: Georgia, "Times New Roman", serif;
      --foreground: light-dark(#202124, #f0f0f0);
      --series: light-dark(#2457a7, #8bb8ff);
      --accent: light-dark(#b45309, #f2a65a);
      --grid: light-dark(rgba(32, 33, 36, 0.14), rgba(240, 240, 240, 0.16));
      --muted: light-dark(rgba(32, 33, 36, 0.68), rgba(240, 240, 240, 0.68));
    }

    body {
      max-width: 64rem;
      margin: 2rem auto;
      padding: 0 1.25rem;
      color: var(--foreground);
    }

    h1 {
      margin: 0 0 0.35rem;
      line-height: 1.25;
    }

    p {
      margin: 0 0 1rem;
      color: var(--muted);
    }

    #kmax-chart {
      width: 100%;
      height: 520px;
    }

    @media (max-width: 480px) {
      body {
        margin-top: 1rem;
      }

      #kmax-chart {
        height: 430px;
      }
    }
  </style>
</head>
<body>
  <main>
    <h1>K<sub>max</sub>(q, R) for R = $r_text</h1>
    <p>
      R is the full rating span. Both axes are logarithmic; hover for values and
      use the Plotly controls at the upper right.
    </p>
    <div id="kmax-chart" role="img"></div>
  </main>

  <script>
    (() => {
      const plot = document.getElementById("kmax-chart");
      plot.setAttribute("aria-label", $summary_json);
      const styles = getComputedStyle(document.documentElement);
      const foreground = styles.getPropertyValue("--foreground").trim();
      const series = styles.getPropertyValue("--series").trim();
      const accent = styles.getPropertyValue("--accent").trim();
      const grid = styles.getPropertyValue("--grid").trim();
      const muted = styles.getPropertyValue("--muted").trim();
      const qValues = $q_values;
      const kValues = $k_values;
      const qPeak = $q_peak;
      const kPeak = $k_peak;
      const peakVisible = $peak_visible;
      const referenceQ = $reference_q;
      const kReference = $k_reference;
      const referenceVisible = $reference_visible;

      const data = [
        {
          x: qValues,
          y: kValues,
          type: "scatter",
          mode: "lines",
          line: { color: series, width: 3 },
          hovertemplate: "q = %{x:,.2f}<br>K<sub>max</sub> = %{y:.4e}<extra></extra>",
          name: "Kmax(q, R)"
        }
      ];

      if (referenceVisible) {
        data.push({
          x: [referenceQ],
          y: [kReference],
          type: "scatter",
          mode: "markers",
          marker: {
            color: accent,
            size: 10,
            symbol: "diamond",
            line: { color: foreground, width: 1 }
          },
          hovertemplate: "q = %{x:,.2f}<br>K<sub>max</sub> = %{y:.4e}<extra></extra>",
          showlegend: false
        });
      }

      if (peakVisible) {
        data.push({
          x: [qPeak],
          y: [kPeak],
          type: "scatter",
          mode: "markers",
          marker: {
            color: series,
            size: 11,
            symbol: "circle",
            line: { color: foreground, width: 1 }
          },
          hovertemplate: "maximum<br>q = %{x:,.2f}<br>K<sub>max</sub> = %{y:.4e}<extra></extra>",
          showlegend: false
        });
      }

      const shapes = [];
      const annotations = [];
      if (referenceVisible) {
        shapes.push({
          type: "line",
          x0: referenceQ,
          x1: referenceQ,
          xref: "x",
          y0: 0,
          y1: 1,
          yref: "paper",
          line: { color: muted, width: 1, dash: "dash" }
        });
        annotations.push({
          x: referenceQ,
          y: kReference,
          text: $reference_annotation,
          showarrow: true,
          arrowhead: 0,
          ax: -72,
          ay: 64,
          arrowcolor: muted,
          font: { color: foreground, size: 12 },
          bgcolor: "rgba(0,0,0,0)",
          align: "right"
        });
      }

      if (peakVisible) {
        annotations.push({
          x: qPeak,
          y: kPeak,
          text: $peak_annotation,
          showarrow: true,
          arrowhead: 0,
          ax: 84,
          ay: -58,
          arrowcolor: muted,
          font: { color: foreground, size: 12 },
          bgcolor: "rgba(0,0,0,0)",
          align: "left"
        });
      }

      const layout = {
        autosize: true,
        margin: { l: 84, r: 26, t: 76, b: 64 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: foreground, size: 12 },
        showlegend: false,
        hovermode: "closest",
        xaxis: {
          title: { text: "Elo scale q (log scale)", font: { color: foreground } },
          type: "log",
          range: [$q_log_minimum, $q_log_maximum],
          exponentformat: "e",
          showexponent: "all",
          gridcolor: grid,
          linecolor: foreground,
          tickfont: { color: muted },
          fixedrange: false
        },
        yaxis: {
          title: { text: "K<sub>max</sub>(q, $r_text)", font: { color: foreground } },
          type: "log",
          range: [$y_log_minimum, $y_log_maximum],
          tickmode: "array",
          tickvals: $tick_values,
          ticktext: $tick_labels,
          gridcolor: grid,
          linecolor: foreground,
          tickfont: { color: muted },
          fixedrange: false
        },
        shapes,
        annotations
      };

      const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
      };

      Plotly.newPlot(plot, data, layout, config);
    })();
  </script>
</body>
</html>
"""
    )
    return template.substitute(substitutions)


def build_fixed_html(
    rating_spans: list[float],
    q_minimum: float,
    q_maximum: float,
    samples: int,
    reference_q: float,
) -> str:
    """Build a comparison chart for the R values in FIXED_R_VALUES."""
    q_values = logspace(q_minimum, q_maximum, samples)
    z = peak_z()
    series_data = []
    visible_values: list[float] = []

    for rating_span in rating_spans:
        k_values = [k_max(q, rating_span) for q in q_values]
        q_peak = math.log(10) * (1 + rating_span) / (2 * z)
        k_peak = k_max(q_peak, rating_span)
        peak_visible = q_minimum <= q_peak <= q_maximum
        visible_values.extend(k_values)
        if peak_visible:
            visible_values.append(k_peak)
        series_data.append(
            {
                "ratingSpan": rating_span,
                "ratingText": display_number(rating_span),
                "kValues": k_values,
                "qPeak": q_peak,
                "kPeak": k_peak,
                "peakVisible": peak_visible,
            }
        )

    visible_logs = [math.log10(value) for value in visible_values]
    y_log_minimum = min(visible_logs) - 0.25
    y_log_maximum = max(visible_logs) + 0.25
    tick_values, tick_labels = exponent_ticks(y_log_minimum, y_log_maximum)
    r_texts = [display_number(value) for value in rating_spans]
    values_text = ", ".join(r_texts)
    summary = (
        "Interactive comparison of K max against q for full rating spans R equal to "
        f"{values_text}. Each curve has a marked maximum."
    )

    substitutions = {
        "plotly_cdn": PLOTLY_CDN,
        "values_text": values_text,
        "summary_json": json.dumps(summary, ensure_ascii=False),
        "q_values": json.dumps(q_values, separators=(",", ":")),
        "series_data": json.dumps(series_data, ensure_ascii=False, separators=(",", ":")),
        "reference_q": json.dumps(reference_q),
        "reference_visible": json.dumps(q_minimum <= reference_q <= q_maximum),
        "q_log_minimum": json.dumps(math.log10(q_minimum)),
        "q_log_maximum": json.dumps(math.log10(q_maximum)),
        "y_log_minimum": json.dumps(y_log_minimum),
        "y_log_maximum": json.dumps(y_log_maximum),
        "tick_values": json.dumps(tick_values, separators=(",", ":")),
        "tick_labels": json.dumps(tick_labels, ensure_ascii=False, separators=(",", ":")),
        "reference_label": json.dumps(f"q = {reference_q:,.4g}", ensure_ascii=False),
    }

    template = Template(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>K max comparison for fixed R values</title>
  <script src="$plotly_cdn"></script>
  <style>
    :root {
      color-scheme: light dark;
      font-family: Georgia, "Times New Roman", serif;
      --foreground: light-dark(#202124, #f0f0f0);
      --series-1: light-dark(#2457a7, #8bb8ff);
      --series-2: light-dark(#b45309, #f2a65a);
      --series-3: light-dark(#24824a, #74d58b);
      --grid: light-dark(rgba(32, 33, 36, 0.14), rgba(240, 240, 240, 0.16));
      --muted: light-dark(rgba(32, 33, 36, 0.68), rgba(240, 240, 240, 0.68));
    }

    body {
      max-width: 64rem;
      margin: 2rem auto;
      padding: 0 1.25rem;
      color: var(--foreground);
    }

    h1 {
      margin: 0 0 0.35rem;
      line-height: 1.25;
    }

    p {
      margin: 0 0 1rem;
      color: var(--muted);
    }

    #kmax-chart {
      width: 100%;
      height: 540px;
    }

    @media (max-width: 480px) {
      body {
        margin-top: 1rem;
      }

      #kmax-chart {
        height: 450px;
      }
    }
  </style>
</head>
<body>
  <main>
    <h1>K<sub>max</sub>(q, R) for fixed R values</h1>
    <p>
      R is the full rating span. The built-in values are $values_text. Both axes
      are logarithmic; hover for values and use the Plotly controls at the upper right.
    </p>
    <div id="kmax-chart" role="img"></div>
  </main>

  <script>
    (() => {
      const plot = document.getElementById("kmax-chart");
      plot.setAttribute("aria-label", $summary_json);
      const styles = getComputedStyle(document.documentElement);
      const foreground = styles.getPropertyValue("--foreground").trim();
      const grid = styles.getPropertyValue("--grid").trim();
      const muted = styles.getPropertyValue("--muted").trim();
      const colors = [1, 2, 3].map(index =>
        styles.getPropertyValue("--series-" + index).trim()
      );
      const dashes = ["solid", "dash", "dot"];
      const symbols = ["circle", "diamond", "square"];
      const qValues = $q_values;
      const seriesData = $series_data;
      const referenceQ = $reference_q;
      const referenceVisible = $reference_visible;
      const data = [];

      seriesData.forEach((item, index) => {
        data.push({
          x: qValues,
          y: item.kValues,
          type: "scatter",
          mode: "lines",
          line: {
            color: colors[index % colors.length],
            width: 3,
            dash: dashes[index % dashes.length]
          },
          hovertemplate:
            "R = " + item.ratingText +
            "<br>q = %{x:,.2f}<br>K<sub>max</sub> = %{y:.4e}<extra></extra>",
          name: "R = " + item.ratingText
        });
      });

      seriesData.forEach((item, index) => {
        if (!item.peakVisible) return;
        data.push({
          x: [item.qPeak],
          y: [item.kPeak],
          type: "scatter",
          mode: "markers",
          marker: {
            color: colors[index % colors.length],
            size: 10,
            symbol: symbols[index % symbols.length],
            line: { color: foreground, width: 1 }
          },
          hovertemplate:
            "R = " + item.ratingText + " maximum" +
            "<br>q = %{x:,.2f}<br>K<sub>max</sub> = %{y:.4e}<extra></extra>",
          showlegend: false
        });
      });

      const shapes = [];
      const annotations = [];
      if (referenceVisible) {
        shapes.push({
          type: "line",
          x0: referenceQ,
          x1: referenceQ,
          xref: "x",
          y0: 0,
          y1: 1,
          yref: "paper",
          line: { color: muted, width: 1, dash: "dash" }
        });
        annotations.push({
          x: referenceQ,
          y: 0.02,
          xref: "x",
          yref: "paper",
          text: $reference_label,
          showarrow: false,
          xanchor: "left",
          xshift: 6,
          font: { color: muted, size: 12 }
        });
      }

      const layout = {
        autosize: true,
        margin: { l: 84, r: 26, t: 70, b: 64 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: foreground, size: 12 },
        hovermode: "closest",
        legend: {
          orientation: "h",
          x: 0,
          y: 1.14,
          xanchor: "left",
          yanchor: "top",
          font: { color: foreground, size: 12 },
          bgcolor: "rgba(0,0,0,0)"
        },
        xaxis: {
          title: { text: "Elo scale q (log scale)", font: { color: foreground } },
          type: "log",
          range: [$q_log_minimum, $q_log_maximum],
          exponentformat: "e",
          showexponent: "all",
          gridcolor: grid,
          linecolor: foreground,
          tickfont: { color: muted },
          fixedrange: false
        },
        yaxis: {
          title: { text: "K<sub>max</sub>(q, R)", font: { color: foreground } },
          type: "log",
          range: [$y_log_minimum, $y_log_maximum],
          tickmode: "array",
          tickvals: $tick_values,
          ticktext: $tick_labels,
          gridcolor: grid,
          linecolor: foreground,
          tickfont: { color: muted },
          fixedrange: false
        },
        shapes,
        annotations
      };

      const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
      };

      Plotly.newPlot(plot, data, layout, config);
    })();
  </script>
</body>
</html>
"""
    )
    return template.substitute(substitutions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a standalone Plotly HTML chart of K_max(q, R)."
    )
    parser.add_argument(
        "R",
        type=nonnegative_number,
        nargs="?",
        help="full rating span; omit when using --fixed",
    )
    parser.add_argument(
        "--fixed",
        action="store_true",
        help="compare the R values listed in FIXED_R_VALUES",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output HTML path; defaults depend on the selected mode",
    )
    parser.add_argument(
        "--q-min",
        type=positive_number,
        help="minimum q; default: 100 in single mode and 10 in --fixed mode",
    )
    parser.add_argument("--q-max", type=positive_number, default=1_000_000.0)
    parser.add_argument("--samples", type=positive_integer, default=700)
    parser.add_argument(
        "--reference-q",
        type=positive_number,
        default=400.0,
        help="q value to mark with a vertical reference line; default: 400",
    )
    args = parser.parse_args()
    if args.fixed and args.R is not None:
        parser.error("R must be omitted when --fixed is used")
    if not args.fixed and args.R is None:
        parser.error("R is required unless --fixed is used")
    return args


def main() -> None:
    args = parse_args()
    q_minimum = args.q_min if args.q_min is not None else (10.0 if args.fixed else 100.0)
    if q_minimum >= args.q_max:
        raise SystemExit("error: --q-min must be less than --q-max")

    if args.fixed:
        output = args.output or Path(fixed_output_filename(FIXED_R_VALUES))
        html = build_fixed_html(
            FIXED_R_VALUES,
            q_minimum,
            args.q_max,
            args.samples,
            args.reference_q,
        )
        output.write_text(html, encoding="utf-8")
        print(f"Wrote {output.resolve()}")
        z = peak_z()
        for rating_span in FIXED_R_VALUES:
            q_peak = math.log(10) * (1 + rating_span) / (2 * z)
            k_peak = k_max(q_peak, rating_span)
            print(
                f"R = {display_number(rating_span)}: "
                f"q_peak = {q_peak:.6g}, K_max = {k_peak:.6g}"
            )
    else:
        output = args.output or Path(f"kmax-r-{filename_number(args.R)}.html")
        html = build_html(args.R, q_minimum, args.q_max, args.samples, args.reference_q)
        output.write_text(html, encoding="utf-8")

        z = peak_z()
        q_peak = math.log(10) * (1 + args.R) / (2 * z)
        k_peak = k_max(q_peak, args.R)
        print(f"Wrote {output.resolve()}")
        print(f"Global maximum: q = {q_peak:.6g}, K_max = {k_peak:.6g}")


if __name__ == "__main__":
    main()
