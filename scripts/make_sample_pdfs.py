"""Generate small sample PDFs so the demo is runnable out of the box.

Creates a fictional company's product guide, FAQ, and internal returns SOP.
Run once:  python scripts/make_sample_pdfs.py
"""
import os
import pymupdf  # PyMuPDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)

DOCS = {
    "product-guide.pdf": [
        (
            "Northwind Gear — Product Guide\n\n"
            "TRAILBLAZER TENT\n"
            "The Trailblazer is a 3-season, 2-person tent weighing 2.4 kg. It uses a freestanding "
            "aluminium pole structure and a 68D polyester flysheet with a 3000 mm waterproof rating. "
            "Setup takes about 5 minutes. The Trailblazer Tent comes with a 2-year limited warranty "
            "covering manufacturing defects in materials and workmanship.\n\n"
            "SUMMIT SLEEPING BAG\n"
            "The Summit is a mummy-style sleeping bag rated to -5°C (comfort) and filled with "
            "700-fill-power responsibly sourced down. It weighs 1.1 kg and packs to 20 x 30 cm.\n"
            "Care: machine wash cold on a gentle cycle with a down-specific detergent, then tumble "
            "dry on low with two clean tennis balls to restore loft. Do not dry clean. The Summit "
            "Sleeping Bag carries a 3-year warranty."
        ),
        (
            "Northwind Gear — Product Guide (continued)\n\n"
            "RANGEFINDER BACKPACK\n"
            "The Rangefinder is a 45-litre backpack with an adjustable torso, a ventilated back "
            "panel, and a rain cover included. It weighs 1.3 kg and fits carry-on dimensions for "
            "most airlines. The Rangefinder Backpack is covered by Northwind's lifetime warranty "
            "against defects.\n\n"
            "WARRANTY SUMMARY\n"
            "- Trailblazer Tent: 2 years\n"
            "- Summit Sleeping Bag: 3 years\n"
            "- Rangefinder Backpack: lifetime\n"
            "Warranty covers manufacturing defects only, not damage from misuse, accidents, or "
            "normal wear. To start a claim, contact support with your order number and photos."
        ),
    ],
    "faq.pdf": [
        (
            "Northwind Gear — Frequently Asked Questions\n\n"
            "Q: How long does shipping take?\n"
            "A: Domestic orders ship within 1 business day and arrive in 3–5 business days. "
            "Expedited 2-day shipping is available at checkout.\n\n"
            "Q: Do you ship internationally?\n"
            "A: Yes, we ship to over 40 countries. International delivery takes 7–14 business "
            "days. Duties and taxes are the customer's responsibility.\n\n"
            "Q: How do I make a warranty claim?\n"
            "A: Email support@northwindgear.example with your order number and photos of the issue. "
            "Claims are reviewed within 2 business days.\n\n"
            "Q: Can I change my order after placing it?\n"
            "A: Orders can be changed within 1 hour of placement by contacting support. After that, "
            "the order enters fulfilment and cannot be modified."
        )
    ],
    "returns-sop.pdf": [
        (
            "Northwind Gear — Returns SOP (Internal)\n\n"
            "PURPOSE\n"
            "This procedure describes how support agents process customer returns.\n\n"
            "RETURN WINDOW\n"
            "Customers may return unused items in original packaging within 30 days of delivery for "
            "a full refund. Used or damaged items are not eligible unless covered by warranty.\n\n"
            "PROCESS\n"
            "1. Verify the order is within the 30-day window.\n"
            "2. Confirm the item is unused and in original packaging.\n"
            "3. Issue an RMA number and email a prepaid return label.\n"
            "4. On receipt at the warehouse, inspect the item within 2 business days.\n"
            "5. Approve the refund. Refunds are issued to the original payment method within "
            "5–7 business days.\n\n"
            "EXCEPTIONS\n"
            "Final-sale items are not returnable. Gift returns are refunded as store credit."
        )
    ],
}


def write_pdf(path, pages):
    doc = pymupdf.open()
    for text in pages:
        page = doc.new_page(width=595, height=842)  # A4
        rect = pymupdf.Rect(60, 60, 535, 782)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv", align=0)
    doc.save(path)
    doc.close()


if __name__ == "__main__":
    for name, pages in DOCS.items():
        write_pdf(os.path.join(DATA, name), pages)
        print("wrote", os.path.join("data", name))
