import glob
import json
import os
import re
from datetime import datetime

TEXT_DIR = "data/text"


def parse_date(text):
    """Find a date in any of our 3 styles and return it as YYYY-MM-DD."""
    patterns = [
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y"),
        (r"\d{1,2} [A-Za-z]{3} \d{4}", "%d %b %Y"),
    ]
    for pattern, fmt in patterns:
        m = re.search(pattern, text)
        if m:
            return datetime.strptime(m.group(), fmt).date().isoformat()
    return None


def extract(text):
    """Pull the main fields out of one invoice's text."""
    result = {}

    m = re.search(r"Vendor:\s*(.+)", text)                 # layout A
    if not m:
        m = re.search(r"^(.+?)\s+TAX INVOICE", text, re.M)  # layout B
    result["vendor"] = m.group(1).strip() if m else None

    m = re.search(r"INV-\d+", text)
    result["invoice_no"] = m.group() if m else None

    result["date"] = parse_date(text)

    m = re.search(r"Subtotal:\s*([\d.]+)", text)
    result["subtotal"] = float(m.group(1)) if m else None

    m = re.search(r"GST 18%:\s*([\d.]+)", text)
    result["gst"] = float(m.group(1)) if m else 0.0         # no GST line = 0

    m = re.search(r"^Total:\s*([\d.]+)", text, re.M)
    result["total"] = float(m.group(1)) if m else None
    return result


# Load the answer key
with open("data/ground_truth.json") as f:
    truth = {row["file"].replace(".pdf", ".txt"): row for row in json.load(f)}

fields = ["vendor", "invoice_no", "date", "subtotal", "gst", "total"]
correct = {k: 0 for k in fields}
mistakes = []

for path in sorted(glob.glob(f"{TEXT_DIR}/*.txt")):
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        found = extract(f.read())
    for k in fields:
        if found[k] == truth[name][k]:
            correct[k] += 1
        else:
            mistakes.append((name, k, found[k], truth[name][k]))

n = len(truth)
print("Accuracy per field:")
for k in fields:
    print(f"  {k:<11} {correct[k]}/{n}  ({100 * correct[k] / n:.0f}%)")

print(f"\nMistakes: {len(mistakes)}")
for name, k, got, want in mistakes[:10]:
    print(f"  {name} | {k} | got {got!r} | expected {want!r}")
    