"""Mutation-score gate for the CI pipeline.

Reads the stats file written by `mutmut export-cicd-stats`, prints the score,
appends it to the GitHub job summary, and fails if it is below the minimum.

Usage: python scripts/check_mutation.py <min_score_percent>
"""

import json
import os
from pathlib import Path
import sys

STATS = Path("mutants/mutmut-cicd-stats.json")


def main() -> int:
    minimum = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    stats = json.loads(STATS.read_text())
    print(json.dumps(stats, indent=2))

    detected = stats.get("killed", 0) + stats.get("timeout", 0) + stats.get("segfault", 0)
    considered = stats.get("total", 0) - stats.get("skipped", 0) - stats.get("not_checked", 0)
    score = 100.0 * detected / considered if considered else 0.0

    line = f"Mutation score: {score:.2f}% ({detected}/{considered} detected), minimum {minimum}%"
    print(line)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(
                f"### Mutation testing\n\n{line}\n\n```json\n{json.dumps(stats, indent=2)}\n```\n"
            )

    if score < minimum:
        print(f"FAIL: mutation score {score:.2f}% is below {minimum}%")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
