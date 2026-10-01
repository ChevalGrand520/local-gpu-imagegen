"""Offline derived-record consistency check; cannot reconstruct private events."""
from pathlib import Path
import json


def verify():
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "paper/evidence/paired-windows-projection-20261001.json").read_text())
    expected = {
        "B2_F00": (1, 1, 1, 1, True, False),
        "W3_F00": (1, 1, 1, 1, True, False),
        "W3_F02": (1, 1, 1, 1, False, True),
        "B2_F02": (2, 2, 2, 2, True, False),
        "B2_FPRE": (2, 1, 1, 1, True, False),
        "W3_FPRE": (1, 0, 0, 0, False, True),
    }
    rows = data["rows"]
    if len(rows) != 6 or {r["case"] for r in rows} != set(expected):
        raise ValueError("case coverage differs")
    for row in rows:
        metrics = row["metrics"]
        actual = tuple(metrics[k] for k in ("S_proxy", "S_upstream", "A", "E_bound")) + (row["client_completion"], row["guard"])
        if actual != expected[row["case"]]:
            raise ValueError("published paired row differs: " + row["case"])
    if data["totals"] != {"operations": 6, "product_calls": 10, "proxy_posts": 8, "upstream_attempts": 6}:
        raise ValueError("totals differ")
    if sum(r["metrics"]["S_proxy"] for r in rows) != data["totals"]["proxy_posts"]:
        raise ValueError("POST sum differs")
    if sum(r["metrics"]["S_upstream"] for r in rows) != data["totals"]["upstream_attempts"]:
        raise ValueError("send sum differs")
    if data["cache_second_B2_F02_nodes"] != [str(n) for n in range(3, 10)]:
        raise ValueError("cache scope differs")
    print("PASS: six published paired rows and totals; derived consistency only, no raw-event replay")


if __name__ == "__main__":
    verify()
