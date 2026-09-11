from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import base64
import os


def generate_sales_invoice(data):

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))

    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    css_file = os.path.join(static_dir, "purchase_order.css")
    logo_file = os.path.join(static_dir, "logo.png")

    # ---------------------------------------------------------
    # Logo
    # ---------------------------------------------------------
    logo_path = None

    if os.path.exists(logo_file):
        with open(logo_file, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("ascii")

        logo_path = f"data:image/png;base64,{logo_b64}"
    else:
        print(f"[sales_order] logo not found at: {logo_file}")

    # ---------------------------------------------------------
    # Load Jinja2 template
    # ---------------------------------------------------------
    env = Environment(
        loader=FileSystemLoader(templates_dir)
    )

    template = env.get_template("sales_invoice.html")

    # ---------------------------------------------------------
    # Amounts
    # ---------------------------------------------------------
    total_amount = float(
        data.get("total_amount", 0) or 0
    )

    discount_amount = float(
        data.get("discount_amount", 0) or 0
    )

    gst_amount = float(
        data.get("gst_amount", 0) or 0
    )

    net_amount = float(
        data.get("net_amount", 0) or 0
    )

    shipping_amount = float(
        data.get("shipping_amount", 0) or 0
    )

    # PL/SQL sends values such as "18%"
    gst_rate = data.get("gst_rate", "") or ""

    tax_label = gst_rate

    # ---------------------------------------------------------
    # Items
    # ---------------------------------------------------------
    items = []
    total_qty = 0

    for i, item in enumerate(
        data.get("items", []),
        start=1
    ):

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

            "unit_price": (
                f'{float(item.get("unit_price", 0) or 0):,.2f}'
            ),

            "line_total": (
                f'{float(item.get("line_total", 0) or 0):,.2f}'
            ),
        })

    # ---------------------------------------------------------
    # Total Quantity Display
    # ---------------------------------------------------------
    if total_qty == int(total_qty):
        total_qty_display = str(int(total_qty))
    else:
        total_qty_display = f"{total_qty:,.2f}"

    # ---------------------------------------------------------
    # Render HTML
    # ---------------------------------------------------------
    html = template.render(

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------
        company_name=data.get(
            "company_name", ""
        ),

        company_address=data.get(
            "company_address", ""
        ),

        factory_address=data.get(
            "factory_address", ""
        ),

        company_phone=data.get(
            "company_phone", ""
        ),

        company_email=data.get(
            "company_email", ""
        ),

        company_ntn=data.get(
            "company_ntn", ""
        ),

        company_strn=data.get(
            "company_strn", ""
        ),

        is_gst=data.get(
            "gst_option", ""
        ),

        # -----------------------------------------------------
        # Quotation
        # -----------------------------------------------------
        quotation_no=data.get(
            "quotation_no", ""
        ),

        quotation_date=data.get(
            "quotation_date", ""
        ),

        valid_until=data.get(
            "valid_until", ""
        ),

        # -----------------------------------------------------
        # Customer
        # -----------------------------------------------------
        customer_name=data.get(
            "customer_name", ""
        ),

        customer_address=data.get(
            "customer_address", ""
        ),

        customer_phone=data.get(
            "customer_phone", ""
        ),

        customer_ntn=data.get(
            "customer_ntn", ""
        ),

        customer_strn=data.get(
            "customer_strn", ""
        ),

        attn=data.get(
            "attn", ""
        ),

        designation=data.get(
            "designation", ""
        ),

        # -----------------------------------------------------
        # Users
        # -----------------------------------------------------
        prepared_by=data.get(
            "prepared_by", ""
        ),

        created_by_designation=data.get(
            "created_by_designation", ""
        ),

        created_by_phone=data.get(
                    "created_by_phone", ""
                ),

        updated_by=data.get(
            "updated_by", ""
        ),

        updated_by_designation=data.get(
            "updated_by_designation", ""
        ),

        # -----------------------------------------------------
        # Amounts
        # -----------------------------------------------------
        total_amount=f"{total_amount:,.2f}",

        discount_amount=f"{discount_amount:,.2f}",

        gst_amount=f"{gst_amount:,.2f}",

        net_amount=f"{net_amount:,.2f}",

        tax_label=tax_label,

        shipping_amount=(
            f"{shipping_amount:,.2f}"
            if shipping_amount
            else "0"
        ),

        # -----------------------------------------------------
        # Remarks
        # -----------------------------------------------------
        remarks=data.get(
            "remarks", ""
        ),

        # -----------------------------------------------------
        # Items
        # -----------------------------------------------------
        total_qty=total_qty_display,

        items=items,

        # -----------------------------------------------------
        # Logo
        # -----------------------------------------------------
        logo_path=logo_path,
    )

    # ---------------------------------------------------------
    # Generate PDF
    # ---------------------------------------------------------
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.set_content(
            html,
            wait_until="networkidle"
        )

        page.add_style_tag(
            path=css_file
        )

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
    # Return PDF
    # ---------------------------------------------------------
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=sales_order.pdf"
        },
    )