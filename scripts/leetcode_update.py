import re
from pathlib import Path

import requests


LEETCODE_USERNAME = "AbdulStack"
SVG_FILE = Path("assets/leetcode-dashboard.svg")

GRAPHQL_URL = "https://leetcode.com/graphql"

QUERY = """
query getUserStats($username: String!) {
  allQuestionsCount {
    difficulty
    count
  }

  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com/"
}


def get_leetcode_stats():
    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": QUERY,
            "variables": {
                "username": LEETCODE_USERNAME
            }
        },
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data.get("errors"):
        raise RuntimeError(
            f"LeetCode API error: {data['errors']}"
        )

    result = data.get("data")

    if not result:
        raise RuntimeError("No data received from LeetCode.")

    matched_user = result.get("matchedUser")

    if not matched_user:
        raise RuntimeError(
            f"LeetCode user '{LEETCODE_USERNAME}' was not found."
        )

    # -----------------------------
    # Total questions on LeetCode
    # -----------------------------

    totals = {}

    for item in result["allQuestionsCount"]:
        totals[item["difficulty"]] = item["count"]

    # -----------------------------
    # User solved statistics
    # -----------------------------

    solved = {}

    for item in matched_user["submitStatsGlobal"]["acSubmissionNum"]:
        solved[item["difficulty"]] = item["count"]

    return {
        "all_solved": solved.get("All", 0),

        "easy_solved": solved.get("Easy", 0),
        "easy_total": totals.get("Easy", 0),

        "medium_solved": solved.get("Medium", 0),
        "medium_total": totals.get("Medium", 0),

        "hard_solved": solved.get("Hard", 0),
        "hard_total": totals.get("Hard", 0),
    }


def update_svg(stats):
    if not SVG_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {SVG_FILE}"
        )

    svg = SVG_FILE.read_text(encoding="utf-8")

    # --------------------------------
    # Total Solved
    # x=485 y=245
    # --------------------------------

    svg, total_changes = re.subn(
        r'(<text x="485" y="245".*?>\s*)\d+(\s*</text>)',
        rf'\g<1>{stats["all_solved"]}\g<2>',
        svg,
        count=1,
        flags=re.DOTALL
    )

    # --------------------------------
    # Easy
    # x=1110 y=183
    # --------------------------------

    svg, easy_changes = re.subn(
        r'(<text x="1110" y="183".*?>\s*)\d+\s*/\s*\d+(\s*</text>)',
        rf'\g<1>{stats["easy_solved"]} / {stats["easy_total"]}\g<2>',
        svg,
        count=1,
        flags=re.DOTALL
    )

    # --------------------------------
    # Medium
    # x=1110 y=241
    # --------------------------------

    svg, medium_changes = re.subn(
        r'(<text x="1110" y="241".*?>\s*)\d+\s*/\s*\d+(\s*</text>)',
        rf'\g<1>{stats["medium_solved"]} / {stats["medium_total"]}\g<2>',
        svg,
        count=1,
        flags=re.DOTALL
    )

    # --------------------------------
    # Hard
    # x=1110 y=299
    # --------------------------------

    svg, hard_changes = re.subn(
        r'(<text x="1110" y="299".*?>\s*)\d+\s*/\s*\d+(\s*</text>)',
        rf'\g<1>{stats["hard_solved"]} / {stats["hard_total"]}\g<2>',
        svg,
        count=1,
        flags=re.DOTALL
    )

    total_changes_count = (
        total_changes
        + easy_changes
        + medium_changes
        + hard_changes
    )

    if total_changes_count != 4:
        raise RuntimeError(
            f"Expected 4 SVG updates, "
            f"but only made {total_changes_count}."
        )

    SVG_FILE.write_text(svg, encoding="utf-8")

    print("===================================")
    print("LeetCode Dashboard Updated")
    print("===================================")
    print(f"Username     : {LEETCODE_USERNAME}")
    print(f"Total Solved : {stats['all_solved']}")
    print(
        f"Easy         : "
        f"{stats['easy_solved']} / {stats['easy_total']}"
    )
    print(
        f"Medium       : "
        f"{stats['medium_solved']} / {stats['medium_total']}"
    )
    print(
        f"Hard         : "
        f"{stats['hard_solved']} / {stats['hard_total']}"
    )


def main():
    print(
        f"Fetching LeetCode statistics "
        f"for {LEETCODE_USERNAME}..."
    )

    stats = get_leetcode_stats()

    update_svg(stats)


if __name__ == "__main__":
    main()
