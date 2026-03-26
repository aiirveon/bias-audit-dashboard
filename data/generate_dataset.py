#!/usr/bin/env python3
"""
generate_dataset.py
-------------------
Generates 3,000 synthetic UK media content items for bias classifier training.

Output : data/synthetic_bias_dataset.csv
Resume : Safe to interrupt and re-run. Existing rows are detected by reading
         the CSV; generation continues from where it left off.

Dependencies:
    pip install anthropic python-dotenv

Usage:
    python data/generate_dataset.py
"""

import csv
import json
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
import anthropic

# ─────────────────────────────────────────────────────────────────────────────
# Environment
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
MODEL       = "claude-haiku-4-5"
OUTPUT_PATH = Path(__file__).resolve().parent / "synthetic_bias_dataset.csv"
BATCH_SIZE  = 10

CATEGORIES = [
    "demographic_bias",
    "gender_stereotyping",
    "racial_bias",
    "religious_bias",
    "geographic_bias",
    "neutral",
]

CLEAR_PER_CATEGORY  = 300   # confidence_ground_truth 0.85–0.99
SUBTLE_PER_CATEGORY = 200   # confidence_ground_truth 0.70–0.84
TRAIN_PER_CATEGORY  = 400   # 80 % of 500
TEST_PER_CATEGORY   = 100   # 20 % of 500

# label: 0 = neutral, 1 = biased
LABEL = {cat: (0 if cat == "neutral" else 1) for cat in CATEGORIES}

FORMATS = [
    "UK newspaper headline",
    "tweet or social post from a UK journalist or creator",
    "YouTube video description from a UK media channel",
    "opening sentence of a UK news article",
]

CSV_COLUMNS = ["content", "label", "category", "confidence_ground_truth", "split"]

# ─────────────────────────────────────────────────────────────────────────────
# Category-specific generation prompts
# Each category has a "clear" variant (explicit bias) and a "subtle" variant
# (bias detectable by a trained reviewer but not immediately obvious).
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_PROMPTS: dict[str, dict[str, str]] = {

    "demographic_bias": {
        "clear": (
            "Write content that discriminates based on AGE, DISABILITY, or SEXUALITY "
            "specifically — not race or religion. Focus on ageism (too old/young for jobs), "
            "ableism (disabled people as burdens), or homophobia. Use UK media language."
        ),
        "subtle": (
            "Write content with subtle ageism, ableism, or anti-LGBT framing — "
            "implying older workers are less capable, disabled people need saving, "
            "or LGBT lifestyles are abnormal. Must NOT reference race or religion."
        ),
    },

    "gender_stereotyping": {
        "clear": (
            "Generate UK media content that clearly reinforces fixed gender roles or "
            "assumptions. The stereotyping must be explicit and unambiguous. "
            "Examples: asserting women are unsuited to leadership or technical roles; "
            "asserting men are incapable of emotional or domestic competence; framing "
            "career ambition in women as unusual or unfeminine; treating traditional "
            "gender roles as natural and inevitable. "
            "Mix examples targeting women and men. Include workplace, family, and "
            "media contexts."
        ),
        "subtle": (
            "Generate UK media content with subtle gender stereotyping — present but not "
            "overtly sexist. "
            "Techniques: using different adjectives for men and women in equivalent roles "
            "(e.g. 'assertive' vs 'bossy'); framing a woman's professional achievement "
            "in terms of her personal life; expressing mild surprise at a man doing "
            "domestic tasks; gendered language that implies different expectations without "
            "stating them explicitly. "
            "Avoid obvious sexism — the bias must be embedded in framing and word choice."
        ),
    },

    "racial_bias": {
        "clear": (
            "Write examples of UK media headlines or article excerpts that REPORT ON "
            "or QUOTE real-world racially biased content — for example, a politician's "
            "statement, a tabloid headline, or a social media post that has been "
            "criticised for racial bias. Frame it as journalism reporting on bias, "
            "not as direct hate speech. The bias must be clearly present and "
            "identifiable. Reference specific UK contexts: stop and search, "
            "housing discrimination, employment gaps, media representation."
        ),
        "subtle": (
            "Write UK media content where racial bias is present through framing, "
            "omission, or coded language rather than explicit slurs. Examples: "
            "statistics presented without context that imply racial inferiority, "
            "neighbourhood descriptions using coded language, crime reporting that "
            "mentions race unnecessarily, diversity initiatives framed as "
            "controversial. UK media context only."
        ),
    },

    "religious_bias": {
        "clear": (
            "Generate UK media content that clearly and unfairly characterises a religious "
            "group. The bias must be explicit. "
            "Cover different UK religions: Islam, Christianity, Judaism, Sikhism, Hinduism. "
            "Examples: associating a religion with violence or extremism; implying a "
            "religious community is incompatible with British values; framing religious "
            "practice as primitive or irrational; attributing social problems to a "
            "religious community without evidence."
        ),
        "subtle": (
            "Generate UK media content with subtle religious bias — present but not "
            "overtly hostile toward any faith. "
            "Techniques: treating Christianity as the default and other faiths as foreign; "
            "framing religious accommodation as unreasonable demands; describing a minority "
            "religion's mainstream views as extreme when equivalent views in another faith "
            "would not be described that way; language implying a religion is culturally "
            "incompatible with the UK without stating it directly."
        ),
    },

    "geographic_bias": {
        "clear": (
            "Write UK media content that attributes negative CHARACTER TRAITS to people "
            "from a specific region — claiming they lack intelligence, ambition, work ethic, "
            "sophistication, or capability compared to people from other areas. "
            "Examples: northerners vs Londoners, rural vs urban, Welsh/Scottish/Northern "
            "Irish vs English. The bias must be in the CHARACTER CLAIM, not just mentioning "
            "a place name. Examples of the pattern: 'People from X lack Y', 'X residents "
            "are too Z to compete', 'Those from X simply don't have the drive to'. "
            "UK media register."
        ),
        "subtle": (
            "Write UK media content with subtle geographic bias through framing — implying "
            "regional inferiority without stating it directly. Examples: presenting northern "
            "or rural investment as charity rather than entitlement, framing London success "
            "as the national default, describing regional accents or culture as obstacles to "
            "professional advancement, statistics presented to imply geographic determinism. "
            "Must be distinguishable from racial or demographic bias — the disadvantage is "
            "based purely on location/region."
        ),
    },

    "neutral": {
        "clear": (
            "Generate UK media content that discusses the SAME groups, regions, and topics "
            "as biased content — but written entirely without bias or unfair framing. "
            "The content MUST reference: demographic groups (elderly, immigrants, LGBT+, "
            "women in the workplace), racial and ethnic communities in the UK (South Asian, "
            "Black British, Chinese, Eastern European), religious groups (Muslim, Christian, "
            "Jewish, Sikh, Hindu communities), UK regions (Northern England, Wales, Scotland, "
            "Northern Ireland, London), and international regions (South Asia, Africa, "
            "Middle East). "
            "Write factually with balanced framing and no implied hierarchy between groups. "
            "Do NOT write generic filler sentences. "
            "Content must feel like genuine UK media coverage that happens to be free of bias."
        ),
        "subtle": (
            "Generate UK media content about the same groups and topics as biased content — "
            "demographic groups, racial communities, religious groups, UK regions, and "
            "international regions — written clearly without any bias signal. "
            "These items should be topically adjacent to content that might trigger a bias "
            "detector, but must contain zero bias. "
            "Examples: a headline about Muslim community events that is purely informational; "
            "a tweet about Northern England that is genuinely positive or neutral; "
            "a news article opening about immigration statistics with no loaded framing. "
            "Make these feel like real, balanced UK media coverage — not obviously "
            "'designed to be neutral'."
        ),
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CSV helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_existing_counts() -> dict[str, dict[str, int]]:
    """
    Read the existing CSV (if any) and return the number of already-generated
    items per (category, difficulty).

    difficulty is inferred from confidence_ground_truth:
      >= 0.85  →  "clear"
       < 0.85  →  "subtle"
    """
    counts: dict[str, dict[str, int]] = {
        cat: {"clear": 0, "subtle": 0} for cat in CATEGORIES
    }
    if not OUTPUT_PATH.exists():
        return counts

    with open(OUTPUT_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row.get("category", "")
            if cat not in counts:
                continue
            try:
                conf = float(row["confidence_ground_truth"])
            except (ValueError, KeyError):
                continue
            difficulty = "clear" if conf >= 0.85 else "subtle"
            counts[cat][difficulty] += 1

    return counts


def append_rows(rows: list[dict]) -> None:
    """
    Append a list of row dicts to the CSV.
    Writes the header automatically if the file does not yet exist.
    """
    file_exists = OUTPUT_PATH.exists()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def assign_splits() -> None:
    """
    Load all rows, randomly assign stratified train/test splits
    (exactly 400 train + 100 test per category), and rewrite the CSV.

    Called once after all generation is complete.
    """
    if not OUTPUT_PATH.exists():
        return

    all_rows: list[dict] = []
    with open(OUTPUT_PATH, newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    # Group row indices by category
    by_category: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(all_rows):
        by_category[row["category"]].append(i)

    for cat, indices in by_category.items():
        shuffled = indices[:]
        random.shuffle(shuffled)
        train_set = set(shuffled[:TRAIN_PER_CATEGORY])
        for idx in indices:
            all_rows[idx]["split"] = "train" if idx in train_set else "test"

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

# ─────────────────────────────────────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────────────────────────────────────

def parse_response(raw: str) -> list[dict]:
    """Strip optional markdown code fences and parse the JSON array."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]  # drop opening fence line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # drop closing fence
        text = "\n".join(lines).strip()
    return json.loads(text)


def call_claude(client, category: str, difficulty: str, format_offset: int) -> list[dict]:
    fmt = FORMATS[format_offset % len(FORMATS)]
    conf_low, conf_high = (0.85, 0.99) if difficulty == "clear" else (0.70, 0.84)
    prompt = CATEGORY_PROMPTS[category][difficulty]
    full_prompt = (
        f"Generate exactly 10 examples of UK media content ({fmt}) "
        f"for the bias category: {category} ({difficulty} examples).\n\n"
        f"Instructions:\n"
        f"- {prompt}\n"
        f"- Each confidence_ground_truth must be a float between {conf_low} and {conf_high}\n"
        f"- Return ONLY a JSON array of exactly 10 objects\n"
        f"- Each object must have exactly two keys: content (string) and confidence_ground_truth (float)\n"
        f"- No markdown, no code fences, no explanation — raw JSON array only\n"
        f"- Start your response with [ and end with ]"
    )
    last_error = None
    for attempt in range(1, 4):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                system="You are a JSON dataset generator. You must respond with only a valid JSON array. Start with [ and end with ]. No markdown fences, no explanation, no preamble.",
                messages=[{"role": "user", "content": full_prompt}],
            )
            raw = response.content[0].text.strip()
            # Remove ```json or ``` fences if present
            if "```" in raw:
                lines = raw.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                raw = "\n".join(lines).strip()
            # Find the JSON array boundaries
            start = raw.find("[")
            end = raw.rfind("]")
            if start == -1 or end == -1:
                raise ValueError(f"No JSON array found in response. Raw: {raw[:200]}")
            raw = raw[start : end + 1]
            items = json.loads(raw)
            if not isinstance(items, list):
                raise ValueError("Response is not a JSON array")
            # Clamp confidence to correct range
            for item in items:
                item["confidence_ground_truth"] = max(
                    conf_low, min(conf_high, float(item["confidence_ground_truth"]))
                )
            return items
        except Exception as e:
            last_error = e
            wait = 5 * attempt
            print(f"\n    ⚠  Attempt {attempt}/3 failed: {e}. Retrying in {wait}s...", end="")
            time.sleep(wait)
    raise RuntimeError(
        f"All 3 API attempts failed for {category} ({difficulty}): {last_error}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Core generation logic
# ─────────────────────────────────────────────────────────────────────────────

def clamp_confidence(value: float, difficulty: str) -> float:
    """Ensure confidence stays within the expected range for this difficulty."""
    if difficulty == "clear":
        return round(max(0.85, min(0.99, value)), 4)
    return round(max(0.70, min(0.84, value)), 4)


def generate_segment(
    client: anthropic.Anthropic,
    category: str,
    difficulty: str,
    target: int,
    already_have: int,
) -> None:
    """
    Generate and incrementally save all remaining items for one
    (category, difficulty) segment.
    """
    needed = target - already_have
    if needed <= 0:
        print(f"  {category} ({difficulty})... already complete ({already_have}/{target})")
        return

    label        = LABEL[category]
    batches      = (needed + BATCH_SIZE - 1) // BATCH_SIZE  # ceiling division
    generated    = already_have

    # Initial progress line — will be overwritten in-place
    print(f"  Generating {category} ({difficulty})... {generated}/{target}", end="", flush=True)

    for batch_idx in range(batches):
        format_offset = generated           # rotate formats from current position
        items         = call_claude(client, category, difficulty, format_offset)

        # Take only what is still needed (last batch may be a partial)
        still_needed = target - generated
        items        = items[:still_needed]

        rows: list[dict] = []
        for item in items:
            conf = clamp_confidence(float(item["confidence_ground_truth"]), difficulty)
            rows.append({
                "content":                  item["content"].strip(),
                "label":                    label,
                "category":                 category,
                "confidence_ground_truth":  conf,
                "split":                    "pending",   # assigned in final pass
            })

        append_rows(rows)
        generated += len(rows)

        # Overwrite progress line in-place
        print(
            f"\r  Generating {category} ({difficulty})... {generated}/{target}",
            end="",
            flush=True,
        )

    print()  # newline after final progress update

# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY not found. "
            "Add it to a .env file or export it as an environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print("=" * 62)
    print("  Bias Audit Dashboard — Synthetic Dataset Generator")
    print(f"  Model  : {MODEL}")
    print(f"  Output : {OUTPUT_PATH}")
    print("=" * 62)

    # ── Resume state ─────────────────────────────────────────────────────────
    counts = load_existing_counts()
    total_existing = sum(
        counts[cat]["clear"] + counts[cat]["subtle"] for cat in CATEGORIES
    )
    print(f"\nExisting rows : {total_existing} / 3000\n")

    # ── Generation loop ───────────────────────────────────────────────────────
    for category in CATEGORIES:
        print(f"── {category.upper()} ──")
        generate_segment(
            client,
            category,
            "clear",
            target=CLEAR_PER_CATEGORY,
            already_have=counts[category]["clear"],
        )
        generate_segment(
            client,
            category,
            "subtle",
            target=SUBTLE_PER_CATEGORY,
            already_have=counts[category]["subtle"],
        )

    # ── Assign train / test splits ────────────────────────────────────────────
    print("\nAssigning train / test splits (400 train · 100 test per category)...")
    assign_splits()

    print("\n✓  Done.")
    print(f"   Rows    : 3,000")
    print(f"   Columns : {', '.join(CSV_COLUMNS)}")
    print(f"   Path    : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
