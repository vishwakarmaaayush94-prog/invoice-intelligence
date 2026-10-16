import re
from datetime import datetime


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

    m = re.search(r"Vendor:\s*(.+)", text)                  # layout A
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


def parse_item_line(line):
    """'Office Chair 2 3350.00 6700.00'
    becomes {'name': 'Office Chair', 'qty': 2, 'price': 3350.0}"""
    parts = line.split()                 # break the line into pieces
    return {
        "name": " ".join(parts[:-3]),    # everything except the last 3 pieces
        "qty": int(parts[-3]),           # third from the end, as a whole number
        "price": float(parts[-2]),       # second from the end, as a decimal number
    }


def get_item_lines(text):
    """Return only the lines between the 'Item' header and the 'Subtotal' line."""
    result = []
    collecting = False                   # the switch starts OFF
    for line in text.splitlines():
        if line.startswith("Subtotal"):
            collecting = False           # switch OFF
        if collecting:
            result.append(line)          # keep this line
        if line.startswith("Item"):
            collecting = True            # switch ON
    return result


def extract_items(text):
    """Return a list of item dictionaries for one invoice."""
    items = []
    for line in get_item_lines(text):
        items.append(parse_item_line(line))
    return items


if __name__ == "__main__":
    import json

    truth = json.load(open("data/ground_truth.json"))
    with open("data/text/invoice_001.txt", encoding="utf-8") as f:
        mine = extract_items(f.read())
    print(mine)
    print(mine == truth[0]["items"])