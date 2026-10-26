"""Draw the one-round diagram for the report (figures/round_diagram.png).

    uv run --project llm-trust-breaking python judging-panel/scripts/round_diagram.py

Boxes the monitor can see (public record) are filled; private steps have a dashed outline.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "figures" / "round_diagram.png"

PUBLIC = dict(face="#dbe8f6", edge="#2f6db5", style="solid")
PRIVATE = dict(face="white", edge="#7a7a7a", style="dashed")
PAIR = dict(face="#fdf0dc", edge="#c7781a", style="dashed")

STEPS = [
    ("1. Private plan", "intended scores\n+ reasoning", PRIVATE),
    ("2. Private messages", "secret pair only\n1 each, ≤ 50 words", PAIR),
    ("3. Announcements", "in turn: preliminary\nscores + justification", PUBLIC),
    ("4. Final scores", "1–5 for each\nother dish", PUBLIC),
    ("5. Inspector", "reveals each dish's\ntrue quality", PUBLIC),
    ("6. Reflection", "private notes =\nmemory for next round", PRIVATE),
]

W, H, GAP = 1.8, 1.0, 0.38


def main():
    fig, ax = plt.subplots(figsize=(11, 2.9))
    for i, (title, body, st) in enumerate(STEPS):
        x = i * (W + GAP)
        ax.add_patch(FancyBboxPatch((x, 0), W, H, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=st["face"], ec=st["edge"], ls=st["style"], lw=1.6))
        ax.text(x + W / 2, H * 0.72, title, ha="center", va="center", fontsize=8.8, weight="bold")
        ax.text(x + W / 2, H * 0.32, body, ha="center", va="center", fontsize=8.5, color="#333333")
        if i < len(STEPS) - 1:
            ax.add_patch(FancyArrowPatch((x + W + 0.04, H / 2), (x + W + GAP - 0.04, H / 2),
                                         arrowstyle="-|>", mutation_scale=12, color="#444444"))

    # loop back from reflection to the next round's plan
    last_x = (len(STEPS) - 1) * (W + GAP) + W / 2
    y_loop = -0.32
    ax.plot([last_x, last_x, W / 2], [-0.03, y_loop, y_loop], color="#888888", lw=1.1)
    ax.add_patch(FancyArrowPatch((W / 2, y_loop), (W / 2, -0.03), arrowstyle="-|>", mutation_scale=12,
                                 color="#888888", lw=1.1))
    ax.text((last_x + W / 2) / 2, y_loop - 0.16, "next round (4 rounds per game)", ha="center", va="center",
            fontsize=8.5, color="#555555")

    # legend
    total = len(STEPS) * (W + GAP) - GAP
    for k, (label, st) in enumerate([("public: shown to the monitor", PUBLIC),
                                     ("private: never shown to the monitor", PRIVATE),
                                     ("private, secret-pair conditions only", PAIR)]):
        lx = k * total / 3
        ax.add_patch(FancyBboxPatch((lx, 1.28), 0.28, 0.18, boxstyle="round,pad=0.01,rounding_size=0.03",
                                    fc=st["face"], ec=st["edge"], ls=st["style"], lw=1.4))
        ax.text(lx + 0.38, 1.37, label, va="center", fontsize=8.5)

    ax.set_xlim(-0.1, total + 0.1)
    ax.set_ylim(-0.6, 1.6)
    ax.axis("off")
    fig.tight_layout()
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=250, bbox_inches="tight")
    print(f"written {OUT}")


if __name__ == "__main__":
    main()
