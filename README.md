# ComfyUI Sequential CSV Wildcard

A ComfyUI custom node that loads prompts from a CSV file and steps through them one row at a time, expanding `{option1|option2|option3}` wildcards in order rather than at random.

## Node: CSV Sequential Wildcard Prompt

Found under **prompt/csv**. The `seed` input is used as the row index, so setting it to **increment** walks through your CSV one row per queued generation.

### Inputs

| Input | Description |
|---|---|
| `csv_path` | Full path to your `.csv` file |
| `seed` | Row index to use. Set "control after generate" to **increment** to step through rows |
| `column` | Which column (0-based) holds the prompt text |
| `has_header` | Skip the first row if it is a header |
| `wrap` | Loop back to the first row after the last one; if off, an index past the end raises an error |
| `prefix` / `suffix` | Optional text added before / after the prompt |

### Outputs

| Output | Description |
|---|---|
| `prompt` | The final prompt string |
| `used_index` | The row index that was used |
| `total_rows` | Number of data rows in the CSV |

### Wildcards

Any `{a|b|c}` group in the prompt is replaced by one option, picked sequentially using the same index (`index % number_of_options`), so results are reproducible.

Example CSV:

```csv
prompt
a {red|blue|green} car parked on a {street|beach}
portrait of a {cat|dog} wearing a hat
```

## Installation

Install through **ComfyUI-Manager** (search for "Sequential CSV Wildcard"), or clone into your custom nodes folder:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Rightey/ComfyUI-SequentialCSVWildcard
```

No extra Python dependencies are required.
