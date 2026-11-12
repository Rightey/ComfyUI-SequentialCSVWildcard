import os
import re
import csv
from typing import Tuple

class SequentialCSVWildcard:
    """
    Load a prompt from a CSV and expand {opt1|opt2|opt3} style
    wildcards sequentially using a seed (set to increment).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "csv_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Full path to your .csv file"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "control_after_generate": True   # <-- this is the important part
                }),
                "column": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1
                }),
                "has_header": ("BOOLEAN", {
                    "default": True
                }),
                "wrap": ("BOOLEAN", {
                    "default": True
                }),
            },
            "optional": {
                "prefix": ("STRING", {"default": "", "multiline": True}),
                "suffix": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("prompt", "used_index", "total_rows")
    FUNCTION = "process"
    CATEGORY = "prompt/csv"

    def process(
        self,
        csv_path: str,
        seed: int,
        column: int,
        has_header: bool,
        wrap: bool,
        prefix: str = "",
        suffix: str = "",
    ) -> Tuple[str, int, int]:

        if not csv_path or not os.path.isfile(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        rows = []
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if has_header and i == 0:
                    continue
                if row:
                    rows.append(row)

        if not rows:
            raise ValueError("CSV contains no data rows")

        total = len(rows)

        # Use the seed as the sequential index
        if wrap:
            used_index = seed % total
        else:
            if seed >= total:
                raise IndexError(
                    f"seed/index {seed} is out of range (CSV has {total} rows). "
                    "Enable 'wrap' or lower the seed."
                )
            used_index = seed

        row = rows[used_index]

        if column >= len(row):
            raise IndexError(
                f"column {column} does not exist in row {used_index} "
                f"(row has only {len(row)} columns)"
            )

        text = row[column].strip()

        def sequential_replacer(match: re.Match) -> str:
            options = [opt.strip() for opt in match.group(1).split("|")]
            if not options:
                return ""
            return options[used_index % len(options)]

        expanded = re.sub(r"\{([^{}]+)\}", sequential_replacer, text)
        final_prompt = f"{prefix}{expanded}{suffix}".strip()

        return (final_prompt, used_index, total)

NODE_CLASS_MAPPINGS = {
    "SequentialCSVWildcard": SequentialCSVWildcard,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SequentialCSVWildcard": "CSV Sequential Wildcard Prompt",
}