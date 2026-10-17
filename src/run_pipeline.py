import glob
import json
import os

from extract import extract, extract_items
from validate import validate


def process_invoice(text):
    """Text of one invoice in, one finished invoice dictionary out."""
    invoice = extract(text)                    # vendor, invoice_no, date, subtotal, gst, total
    invoice["items"] = extract_items(text)     # add the item rows
    invoice["problems"] = validate(invoice)    # add the list of problems ([] means all fine)
    return invoice


def run_all():
    """Process every invoice text file and return a list of results."""
    results = []
    for path in sorted(glob.glob("data/text/*.txt")):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        invoice = process_invoice(text)
        invoice["file"] = os.path.basename(path).replace(".txt", ".pdf")
        results.append(invoice)
    return results


def load_truth():
    """Load the answer key as a dictionary: {'invoice_001.pdf': {...}, ...}"""
    with open("data/ground_truth.json") as f:
        rows = json.load(f)
    return {row["file"]: row for row in rows}


def score(results, truth):
    """Count how many invoices got each field right."""
    fields = ["vendor", "invoice_no", "date", "subtotal", "gst", "total", "items"]
    correct = {field: 0 for field in fields}
    for invoice in results:
        answer = truth[invoice["file"]]
        for field in fields:
            if invoice[field] == answer[field]:
                correct[field] += 1
    return correct


def save_results(results):
    """Write all results to data/extracted.json."""
    with open("data/extracted.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    results = run_all()
    truth = load_truth()
    correct = score(results, truth)

    print("Accuracy per field:")
    for field, count in correct.items():
        print(f"  {field:<11} {count}/{len(results)}")

    flagged = [r["file"] for r in results if r["problems"]]
    print(f"\nInvoices flagged by validation: {len(flagged)}")

    save_results(results)
    print("Saved data/extracted.json")