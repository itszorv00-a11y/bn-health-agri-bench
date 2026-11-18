import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def figure_accuracy(stats: dict, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    entries = [k for k in stats["aggregate"] if k.endswith("::bn") or k.endswith("::en")]
    if not entries:
        raise SystemExit("no annotated aggregate results; run eval + annotation first")
    labels = sorted({k.rsplit("::", 1)[0] for k in entries})
    x = range(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 3.5))
    for offset, language, color in ((-width / 2, "bn", COLORS[0]), (width / 2, "en", COLORS[1])):
        ys, err_lo, err_hi = [], [], []
        for label in labels:
            entry = stats["aggregate"].get(f"{label}::{language}")
            if entry:
                acc, (lo, hi) = entry["accuracy_at_least_partial"], entry["accuracy_ci95"]
            else:
                acc, lo, hi = 0.0, 0.0, 0.0
            ys.append(acc)
            err_lo.append(acc - lo)
            err_hi.append(hi - acc)
        ax.bar([i + offset for i in x], ys, width, yerr=[err_lo, err_hi],
               capsize=3, label=language, color=color)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("accuracy (>= partial)")
    ax.set_ylim(0, 1)
    ax.legend(title="question language")
    fig.tight_layout()
    fig.savefig(out / "fig1_accuracy_by_language.pdf")
    fig.savefig(out / "fig1_accuracy_by_language.png", dpi=300)
    plt.close(fig)


def figure_gaps(stats: dict, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gaps = stats.get("language_gaps", {})
    if not gaps:
        raise SystemExit("no paired language gaps in stats")
    models = sorted(gaps)
    fig, ax = plt.subplots(figsize=(5, 3))
    for i, model in enumerate(models):
        entry = gaps[model]
        ax.errorbar(entry["mean_gap"], i,
                    xerr=[[entry["mean_gap"] - entry["ci95"][0]],
                          [entry["ci95"][1] - entry["mean_gap"]]],
                    fmt="o", color=COLORS[i % len(COLORS)], capsize=3,
                    label=f"{model} (p={entry['permutation_p']:.3f})")
    ax.axvline(0, color="gray", lw=1, ls="--")
    ax.set_xlabel("bn - en correctness gap (paired, 0-2 scale)")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=8)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "fig2_language_gap.pdf")
    fig.savefig(out / "fig2_language_gap.png", dpi=300)
    plt.close(fig)


def figure_errors(stats: dict, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    per_model = stats.get("errors", {}).get("per_model", {})
    if not per_model:
        raise SystemExit("no error tags in stats")
    models = sorted(per_model)
    tags = sorted({t for m in models for t in per_model[m]})
    matrix = np.zeros((len(models), len(tags)))
    for i, model in enumerate(models):
        for j, tag in enumerate(tags):
            matrix[i, j] = per_model[model].get(tag, 0)
    fig, ax = plt.subplots(figsize=(0.6 * max(len(tags), 6), 0.5 * len(models) + 1.5))
    im = ax.imshow(matrix, aspect="auto", cmap="Blues")
    ax.set_xticks(range(len(tags)))
    ax.set_xticklabels(tags, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(out / "fig3_error_heatmap.pdf")
    fig.savefig(out / "fig3_error_heatmap.png", dpi=300)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate paper figures from stats")
    parser.add_argument("--stats", default="data/results/stats.json")
    parser.add_argument("--out", default="figures/")
    args = parser.parse_args()
    from src.utils.io import load_json
    stats = load_json(args.stats)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    figure_accuracy(stats, out)
    figure_gaps(stats, out)
    figure_errors(stats, out)
    print(f"figures written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
