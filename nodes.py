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

    RETURN_TYPES = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("prompt", "used_index", "total_rows", "total_prompts")
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

        pattern = re.compile(r"\{([^{}]+)\}")

        # Every row expands into all of its wildcard combinations, and the
        # seed walks through them in order: all combinations of row 1,
        # then all of row 2, and so on. The first wildcard in a row changes
        # fastest. Counts are computed, never materialized, so big rows are fine.
        parsed = []  # (text, [options per group], combo count)
        for r in rows:
            if column >= len(r):
                parsed.append((None, [], 1))
                continue
            text = r[column].strip()
            groups = [[o.strip() for o in g.split("|")] for g in pattern.findall(text)]
            count = 1
            for g in groups:
                count *= len(g)
            parsed.append((text, groups, count))

        total_rows = len(rows)
        total_prompts = sum(c for _, _, c in parsed)

        if wrap:
            used_index = seed % total_prompts
        else:
            if seed >= total_prompts:
                raise IndexError(
                    f"seed/index {seed} is out of range (CSV expands to {total_prompts} prompts). "
                    "Enable 'wrap' or lower the seed."
                )
            used_index = seed

        offset = used_index
        row_i = 0
        while offset >= parsed[row_i][2]:
            offset -= parsed[row_i][2]
            row_i += 1

        text, groups, _ = parsed[row_i]
        if text is None:
            raise IndexError(
                f"column {column} does not exist in row {row_i} "
                f"(row has only {len(rows[row_i])} columns)"
            )

        picks = []
        for g in groups:
            picks.append(g[offset % len(g)])
            offset //= len(g)
        picks_iter = iter(picks)

        expanded = pattern.sub(lambda m: next(picks_iter), text)
        final_prompt = f"{prefix}{expanded}{suffix}".strip()

        return (final_prompt, used_index, total_rows, total_prompts)

NODE_CLASS_MAPPINGS = {
    "SequentialCSVWildcard": SequentialCSVWildcard,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SequentialCSVWildcard": "CSV Sequential Wildcard Prompt",
}