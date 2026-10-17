import json
import os
import random
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

random.seed(7)  # different seed from the clean set, so these invoices are different

N_INVOICES = 40
OUT_DIR = "data/messy"
os.makedirs(OUT_DIR, exist_ok=True)

VENDORS = [
    "Sharma Electronics Pvt Ltd", "Patel Office Supplies", "Mehta Traders",
    "Nova Tech Solutions", "Kapoor Stationery Mart", "Singh Hardware Co",
    "Bluewave Networks LLP", "Desai Furniture House",
]
# (product name, min price, max price)
PRODUCTS = [
    ("Laptop", 35000, 60000), ("Mouse", 300, 1200), ("Keyboard", 500, 3000),
    ("Monitor", 7000, 20000), ("Printer", 6000, 18000), ("Office Chair", 3000, 9000),
    ("USB Cable", 100, 500), ("Router", 1500, 6000), ("Pen Drive", 400, 1200),
    ("Webcam", 1200, 4000),
]
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"]

# The messy part: real invoices use many different words for the same thing
TOTAL_LABELS = ["Total:", "Amount Due:", "Grand Total:", "Total Payable:"]
VENDOR_LABELS = ["Vendor:", "From:", "Supplier:", "Billed by:"]
DATE_LABELS = ["Date:", "Invoice Date:", "Issued on:", "Dated:"]


def money(x):
    """Amount as text: thousand commas, and 'Rs. ' in front half of the time."""
    text = f"{x:,.2f}"
    if random.random() < 0.5:
        text = "Rs. " + text
    return text


def make_data(i):
    """Create the 'true' content of one invoice."""
    vendor = random.choice(VENDORS)
    d = date(2026, 1, 1) + timedelta(days=random.randint(0, 280))
    date_fmt = random.choice(DATE_FORMATS)

    items = []
    for name, lo, hi in random.sample(PRODUCTS, random.randint(1, 5)):
        items.append({"name": name, "qty": random.randint(1, 5),
                      "price": random.randrange(lo, hi, 10)})

    subtotal = sum(it["qty"] * it["price"] for it in items)
    gst = round(subtotal * 0.18, 2) if random.random() < 0.7 else 0.0
    return {
        "file": f"invoice_{i:03d}.pdf",
        "invoice_no": f"INV-{1000 + i}",
        "vendor": vendor,
        "date": d.isoformat(),
        "date_text": d.strftime(date_fmt),
        "items": items,
        "subtotal": float(subtotal),
        "gst": gst,
        "total": round(subtotal + gst, 2),
    }


def draw_pdf(inv, layout):
    """Draw the invoice on a PDF page, using messy labels and amounts."""
    c = canvas.Canvas(f"{OUT_DIR}/{inv['file']}", pagesize=A4)
    w, h = A4

    # pick this invoice's own words for each label
    vendor_label = random.choice(VENDOR_LABELS)
    date_label = random.choice(DATE_LABELS)
    total_label = random.choice(TOTAL_LABELS)

    if layout == "A":  # title left, details below it
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, h - 60, "INVOICE")
        c.setFont("Helvetica", 11)
        c.drawString(50, h - 100, f"{vendor_label} {inv['vendor']}")
        c.drawString(50, h - 118, f"Invoice No: {inv['invoice_no']}")
        c.drawString(50, h - 136, f"{date_label} {inv['date_text']}")
    else:              # vendor name big on top, details on the right
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, h - 60, inv["vendor"])
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(w - 50, h - 60, "TAX INVOICE")
        c.setFont("Helvetica", 11)
        c.drawRightString(w - 50, h - 100, f"No. {inv['invoice_no']}")
        c.drawRightString(w - 50, h - 118, f"{date_label} {inv['date_text']}")

    # item table (kept clean for now)
    y = h - 190
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(300, y, "Qty")
    c.drawString(380, y, "Price")
    c.drawString(470, y, "Amount")
    c.setFont("Helvetica", 11)
    y -= 20
    for it in inv["items"]:
        c.drawString(50, y, it["name"])
        c.drawString(300, y, str(it["qty"]))
        c.drawString(380, y, f"{it['price']:.2f}")
        c.drawString(470, y, f"{it['qty'] * it['price']:.2f}")
        y -= 18

    # totals, with messy amounts
    y -= 15
    c.drawString(380, y, f"Subtotal: {money(inv['subtotal'])}")
    if inv["gst"] > 0:
        y -= 18
        c.drawString(380, y, f"GST 18%: {money(inv['gst'])}")
    y -= 22
    c.setFont("Helvetica-Bold", 12)
    c.drawString(380, y, f"{total_label} {money(inv['total'])}")
    c.save()


truth = []
for i in range(1, N_INVOICES + 1):
    inv = make_data(i)
    draw_pdf(inv, random.choice(["A", "B"]))
    truth.append(inv)

with open("data/messy_truth.json", "w") as f:
    json.dump(truth, f, indent=2)

print(f"Created {N_INVOICES} messy invoices in {OUT_DIR} and data/messy_truth.json")