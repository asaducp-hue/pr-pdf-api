from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import base64
import os


def generate_grn(data):

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))

    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    css_file = os.path.join(static_dir, "purchase_order.css")
    logo_file = os.path.join(static_dir, "logo.png")

    # ---------------------------------------------------------
    # Embed Logo as Base64
    # ---------------------------------------------------------
    logo_path = None

    if os.path.exists(logo_file):

        with open(logo_file, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode("ascii")

        logo_path = f"data:image/png;base64,{logo_b64}"

    else:
        print(f"[GRN] logo not found at: {logo_file}")

    # ---------------------------------------------------------
    # Load Jinja2 Template
    # ---------------------------------------------------------
    env = Environment(
        loader=FileSystemLoader(templates_dir)
    )

    template = env.get_template("grn.html")

    # ---------------------------------------------------------
    # GRN Header Information
    # ---------------------------------------------------------
    company_name = data.get("company_name", "")
    company_address = data.get("company_address", "")
    factory_address = data.get("factory_address", "")
    company_phone = data.get("company_phone", "")
    company_email = data.get("company_email", "")
    company_ntn = data.get("company_ntn", "")
    company_strn = data.get("company_strn", "")

    po_no = data.get("po_no", "")
    receipt_date = data.get("receipt_date", "")

    gross_weight = data.get("gross_weight", "")
    tare_weight = data.get("tare_weight", "")
    total_weight = data.get("total_weight", "")

    supplier = data.get("supplier", "")

    business_unit_address = data.get(
        "business_unit_address", ""
    )

    business_unit_phone = data.get(
        "business_unit_phone", ""
    )

    created_by = data.get("created_by", "")
    created_by_designation = data.get(
        "created_by_designation", ""
    )

    updated_by = data.get("updated_by", "")
    updated_by_designation = data.get(
        "updated_by_designation", ""
    )

    remarks = data.get("remarks", "")
    status_name = data.get("status_name", "")
    gr_no = data.get("gr_no", "")
    measure_name = data.get("measure_name", "")
    

    # ---------------------------------------------------------
    # Items
    # ---------------------------------------------------------
    items = []

    total_order_quantity = 0
    total_received_quantity = 0

    for i, item in enumerate(
        data.get("items", []),
        start=1
    ):

        order_quantity = item.get(
            "order_quantity",
            0
        ) or 0

        received_quantity = item.get(
            "received_quantity",
            0
        ) or 0

        # ---------------------------------------------
        # Calculate Total Order Quantity
        # ---------------------------------------------
        try:
            total_order_quantity += float(
                order_quantity
            )
        except (TypeError, ValueError):
            pass

        # ---------------------------------------------
        # Calculate Total Received Quantity
        # ---------------------------------------------
        try:
            total_received_quantity += float(
                received_quantity
            )
        except (TypeError, ValueError):
            pass

        items.append({
            "sr_no": item.get(
                "sr_no",
                i
            ),

            "item_code": item.get(
                "item_code",
                ""
            ),

            "item_name": item.get(
                "item_name",
                ""
            ),

            "unit": item.get(
                "unit",
                ""
            ),

            "size": item.get(
                "size",
                ""
            ),

            "order_quantity": order_quantity,

            "received_quantity": received_quantity,
        })

    # ---------------------------------------------------------
    # Format Total Quantities
    # ---------------------------------------------------------
    if total_order_quantity == int(
        total_order_quantity
    ):
        total_order_quantity_display = str(
            int(total_order_quantity)
        )
    else:
        total_order_quantity_display = (
            f"{total_order_quantity:,.2f}"
        )

    if total_received_quantity == int(
        total_received_quantity
    ):
        total_received_quantity_display = str(
            int(total_received_quantity)
        )
    else:
        total_received_quantity_display = (
            f"{total_received_quantity:,.2f}"
        )

    # ---------------------------------------------------------
    # Render HTML
    # ---------------------------------------------------------
    html = template.render(

        # Company
        company_name=company_name,
        company_address=company_address,
        factory_address=factory_address,
        company_phone=company_phone,
        company_email=company_email,
        company_ntn=company_ntn,
        company_strn=company_strn,

        # GRN
        po_no=po_no,
        receipt_date=receipt_date,

        gross_weight=gross_weight,
        tare_weight=tare_weight,
        total_weight=total_weight,

        # Supplier
        supplier=supplier,

        # Business Unit
        business_unit_address=business_unit_address,
        business_unit_phone=business_unit_phone,

        # Users
        created_by=created_by,
        created_by_designation=created_by_designation,

        updated_by=updated_by,
        updated_by_designation=updated_by_designation,

        # GRN Information
        remarks=remarks,
        status_name=status_name,
        gr_no=gr_no,
        measure_name=measure_name,

        # Items
        items=items,

        # Totals
        total_order_quantity=(
            total_order_quantity_display
        ),

        total_received_quantity=(
            total_received_quantity_display
        ),

        # Logo
        logo_path=logo_path,
    )

    # ---------------------------------------------------------
    # Generate PDF using Playwright / Chromium
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
    # Return PDF to FastAPI
    # ---------------------------------------------------------
    return Response(

        content=pdf,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
                "attachment; filename=grn.pdf"
        },
    )