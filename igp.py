from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import base64
import os


def generate_igp(data):

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))

    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    css_file = os.path.join(
        static_dir,
        "purchase_order.css"
    )

    logo_file = os.path.join(
        static_dir,
        "logo.png"
    )

    # ---------------------------------------------------------
    # Embed Logo as Base64
    # ---------------------------------------------------------
    logo_path = None

    if os.path.exists(logo_file):

        with open(logo_file, "rb") as f:
            logo_b64 = base64.b64encode(
                f.read()
            ).decode("ascii")

        logo_path = (
            f"data:image/png;base64,{logo_b64}"
        )

    else:
        print(
            f"[IGP] logo not found at: {logo_file}"
        )

    # ---------------------------------------------------------
    # Load Jinja2 Template
    # ---------------------------------------------------------
    env = Environment(
        loader=FileSystemLoader(templates_dir)
    )

    template = env.get_template("igp.html")

    # ---------------------------------------------------------
    # Company Information
    # ---------------------------------------------------------
    company_name = data.get(
        "company_name", ""
    )

    company_address = data.get(
        "company_address", ""
    )

    factory_address = data.get(
        "factory_address", ""
    )

    company_phone = data.get(
        "company_phone", ""
    )

    company_email = data.get(
        "company_email", ""
    )

    company_ntn = data.get(
        "company_ntn", ""
    )

    company_strn = data.get(
        "company_strn", ""
    )

    # ---------------------------------------------------------
    # IGP Information
    # ---------------------------------------------------------
    igp_no = data.get(
        "igp_no", ""
    )

    po_no = data.get(
        "po_no", ""
    )

    receipt_date = data.get(
        "receipt_date", ""
    )

    vehicle_no = data.get(
        "vehicle_no", ""
    )

    driver_name = data.get(
        "driver_name", ""
    )

    driver_contact = data.get(
        "driver_contact", ""
    )

    challan_no = data.get(
        "challan_no", ""
    )

    # ---------------------------------------------------------
    # Weight Information
    # ---------------------------------------------------------
    gross_weight = data.get(
        "gross_weight", ""
    )

    tare_weight = data.get(
        "tare_weight", ""
    )

    total_weight = data.get(
        "total_weight", ""
    )

    measure_name = data.get(
        "measure_name", ""
    )

    # ---------------------------------------------------------
    # Supplier
    # ---------------------------------------------------------
    supplier = data.get(
        "supplier", ""
    )

    # ---------------------------------------------------------
    # Business Unit
    # ---------------------------------------------------------
    business_unit_address = data.get(
        "business_unit_address", ""
    )

    business_unit_phone = data.get(
        "business_unit_phone", ""
    )

    # ---------------------------------------------------------
    # Users
    # ---------------------------------------------------------
    created_by = data.get(
        "created_by", ""
    )

    created_by_designation = data.get(
        "created_by_designation", ""
    )

    updated_by = data.get(
        "updated_by", ""
    )

    updated_by_designation = data.get(
        "updated_by_designation", ""
    )

    # ---------------------------------------------------------
    # Other Information
    # ---------------------------------------------------------
    remarks = data.get(
        "remarks", ""
    )

    status_name = data.get(
        "status_name", ""
    )

    # ---------------------------------------------------------
    # Items
    # ---------------------------------------------------------
    items = []

    total_quantity = 0

    for i, item in enumerate(
        data.get("items", []),
        start=1
    ):

        qty = item.get(
            "grn_qty",
            0
        ) or 0

        # -----------------------------------------------------
        # Calculate Total Quantity
        # -----------------------------------------------------
        try:
            total_quantity += float(qty)
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

            "quantity": qty,

        })

    # ---------------------------------------------------------
    # Format Total Quantity
    # ---------------------------------------------------------
    if total_quantity == int(
        total_quantity
    ):

        total_quantity_display = str(
            int(total_quantity)
        )

    else:

        total_quantity_display = (
            f"{total_quantity:,.2f}"
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

        # IGP
        igp_no=igp_no,
        po_no=po_no,
        receipt_date=receipt_date,

        # Vehicle
        vehicle_no=vehicle_no,
        driver_name=driver_name,
        driver_contact=driver_contact,
        challan_no=challan_no,

        # Weight
        gross_weight=gross_weight,
        tare_weight=tare_weight,
        total_weight=total_weight,
        measure_name=measure_name,

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

        # Other
        remarks=remarks,
        status_name=status_name,

        # Items
        items=items,

        # Total
        total_quantity=total_quantity_display,

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
    # Return PDF
    # ---------------------------------------------------------
    return Response(

        content=pdf,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
                "attachment; filename=igp.pdf"
        },
    )