from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import base64
import os


def generate_purchase_order(data):

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))

    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    css_file = os.path.join(static_dir, "purchase_order.css")
    logo_file = os.path.join(static_dir, "logo.png")  # e.g. pdf-api\static\logo.png

    # Embed the logo as a base64 data URI rather than a file:// path.
    # Headless Chromium can be inconsistent about loading local file://
    # resources when the HTML is injected via set_content() instead of an
    # actual navigation, and file:// URIs also break silently if the path
    # has the wrong slashes on Windows. A data URI sidesteps both issues.
    logo_path = None
    if os.path.exists(logo_file):
        with open(logo_file, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("ascii")
        logo_path = f"data:image/png;base64,{logo_b64}"
    else:
        print(f"[purchase_order] logo not found at: {logo_file}")

    # ---------------------------------------------------------
    # Load Jinja2 template
    # ---------------------------------------------------------
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("purchase_order.html")

    # ---------------------------------------------------------
    # Amounts
    # ---------------------------------------------------------
    total_amount = float(data.get("total_amount", 0) or 0)
    discount_amount = float(data.get("discount_amount", 0) or 0)
    gst_amount = float(data.get("gst_amount", 0) or 0)
    net_amount = float(data.get("net_amount", 0) or 0)
    shipping_amount = float(data.get("shipping_amount", 0) or 0)

    gst_rate = data.get("gst_rate", "")  # e.g. "18" -> shown as "CS18%"
    tax_label = f"{gst_rate}" if gst_rate not in ("", None) else data.get("tax_label", "")

    # ---------------------------------------------------------
    # Items
    # ---------------------------------------------------------
    items = []
    total_qty = 0

    for i, item in enumerate(data.get("items", []), start=1):

        qty = item.get("quantity", 0) or 0
        try:
            total_qty += float(qty)
        except (TypeError, ValueError):
            pass

        items.append({
            "sr_no": item.get("sr_no", i),
            "item_code": item.get("item_code", ""),
            "item_name": item.get("item_name", ""),
            "size": item.get("size", ""),
            "quantity": qty,
            "unit": item.get("unit", ""),
            "unit_price": f'{float(item.get("unit_price", 0) or 0):,.2f}',
            "line_total": f'{float(item.get("line_total", 0) or 0):,.2f}',
        })

    # Trim trailing ".0" for whole-number quantities, like the sample ("10" not "10.0")
    if total_qty == int(total_qty):
        total_qty_display = str(int(total_qty))
    else:
        total_qty_display = f"{total_qty:,.2f}"

    # ---------------------------------------------------------
    # Render HTML
    # ---------------------------------------------------------
    html = template.render(
        company_name=data.get("company_name", ""),
        company_address=data.get("company_address", ""),
        factory_address=data.get("factory_address", ""),
        company_phone=data.get("company_phone", ""),
        company_email=data.get("company_email", ""),
        company_ntn=data.get("company_ntn", ""),
        company_strn=data.get("company_strn", ""),
        is_gst=data.get("is_gst", ""),
        created_by=data.get("created_by", ""),
        created_by_designation=data.get("created_by_designation", ""),
        approved_by=data.get("approved_by", ""),
        approved_by_designation=data.get("approved_by_designation", ""),
        ceo=data.get("ceo", ""),

        copy_label=data.get("copy_label", "Original"),

        po_no=data.get("po_no", ""),
        po_date=data.get("po_date", ""),

        supplier=data.get("supplier", ""),
        supplier_address=data.get("supplier_address", ""),
        supplier_phone=data.get("supplier_phone", ""),
        supplier_ntn=data.get("supplier_ntn", ""),
        supplier_strn=data.get("supplier_strn", ""),
        attn=data.get("attn", ""),
        designation=data.get("designation", ""),

        business_unit_address=data.get("business_unit_address", ""),
        business_unit_phone=data.get("business_unit_phone", ""),

        shipping_terms=data.get("shipping_terms", ""),
        shipping_amount=f"{shipping_amount:,.2f}" if shipping_amount else "0",
        delivery_date=data.get("delivery_date", ""),
        other_amount=data.get("other_amount", ""),
        shipping_method=data.get("shipping_method", ""),
        collection=data.get("collection", ""),
        reference=data.get("reference", ""),
        payment_terms=data.get("payment_terms", ""),
        required_qty=data.get("required_qty", ""),
        remarks=data.get("remarks", ""),
        generated_date=data.get("generated_date", ""),

        total_amount=f"{total_amount:,.2f}",
        discount_amount=f"{discount_amount:,.2f}",
        gst_amount=f"{gst_amount:,.2f}",
        net_amount=f"{net_amount:,.2f}",
        tax_label=tax_label,
        total_qty=total_qty_display,

        items=items,
        logo_path=logo_path,
    )

    # ---------------------------------------------------------
    # Generate PDF using Playwright / Chromium
    # ---------------------------------------------------------
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_content(html, wait_until="networkidle")
        page.add_style_tag(path=css_file)

        pdf = page.pdf(
            format="A4",
            print_background=True,
            margin={
                "top": "14mm",
                "right": "12mm",
                "bottom": "16mm",
                "left": "12mm",
            },
        )

        browser.close()

    # ---------------------------------------------------------
    # Return PDF directly to FastAPI
    # ---------------------------------------------------------
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=Purchase_Order.pdf"
        },
    )