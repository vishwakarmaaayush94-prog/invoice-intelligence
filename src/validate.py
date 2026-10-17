def check_items(invoice):
    """True if the sum of qty * price over all items equals the subtotal."""
    items_sum = 0
    for item in invoice["items"]:
        items_sum += item["qty"] * item["price"]
    return abs(items_sum - invoice["subtotal"]) < 0.01


def check_total(invoice):
    """True if subtotal + gst equals the total."""
    return abs(invoice["subtotal"] + invoice["gst"] - invoice["total"]) < 0.01


def validate(invoice):
    """Return a list of problems. An empty list means everything is fine."""
    problems = []

    # first make sure the numbers exist, so the checks below never see None
    for key in ["subtotal", "gst", "total"]:
        if invoice[key] is None:
            problems.append(f"missing field: {key}")
    if problems:
        return problems

    if not check_items(invoice):
        problems.append("items do not add up to subtotal")
    if not check_total(invoice):
        problems.append("subtotal + gst does not equal total")
    return problems


if __name__ == "__main__":
    good = {"items": [{"name": "Webcam", "qty": 2, "price": 100.0}],
            "subtotal": 200.0, "gst": 36.0, "total": 236.0}
    bad = {"items": [{"name": "Webcam", "qty": 2, "price": 100.0}],
           "subtotal": 200.0, "gst": 36.0, "total": 999.0}
    broken = {"items": [], "subtotal": None, "gst": 0.0, "total": None}
    print(validate(good))     # expect: []
    print(validate(bad))      # expect: one problem listed
    print(validate(broken))   # expect: ['missing field: subtotal', 'missing field: total']

    # real invoice
    from extract import extract, extract_items
    text = open("data/text/invoice_001.txt", encoding="utf-8").read()
    invoice = extract(text)
    invoice["items"] = extract_items(text)
    print(validate(invoice))   # expect: []