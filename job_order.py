from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import base64
import os


def generate_job_order(data):

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))

    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    css_file = os.path.join(
        static_dir,
        "job_order.css"
    )

    logo_file = os.path.join(
        static_dir,
        "logo.png"
    )

    # ---------------------------------------------------------
    # Logo
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
            f"[job_order] logo not found at: {logo_file}"
        )

    # ---------------------------------------------------------
    # Load Jinja2 Template
    # ---------------------------------------------------------
    env = Environment(
        loader=FileSystemLoader(templates_dir)
    )

    template = env.get_template(
        "job_order.html"
    )

    # ---------------------------------------------------------
    # Material
    # Single material - no loop
    # ---------------------------------------------------------
    material = data.get(
        "material",
        ""
    ) or ""

    material_size = data.get(
        "size",
        ""
    ) or ""

    material_guage = data.get(
        "guage",
        ""
    ) or ""

    material_color = data.get(
        "color",
        ""
    ) or ""

    # ---------------------------------------------------------
    # Items
    # ---------------------------------------------------------
    items = []

    total_qty = 0

    for i, item in enumerate(
        data.get("items", []),
        start=1
    ):

        qty = item.get(
            "qty",
            0
        ) or 0

        try:
            total_qty += float(qty)

        except (
            TypeError,
            ValueError
        ):
            pass

        items.append({

            "sr_no": item.get(
                "sr_no",
                i
            ),

            "description": item.get(
                "description",
                ""
            ),

            "size": item.get(
                "size",
                ""
            ),

            "qty": qty,

            "remarks": item.get(
                "remarks",
                ""
            ),
        })

    # ---------------------------------------------------------
    # Minimum Item Rows
    # ---------------------------------------------------------
    MIN_ITEM_ROWS = 10

    while len(items) < MIN_ITEM_ROWS:

        items.append({

            "sr_no": len(items) + 1,

            "description": "",

            "size": "",

            "qty": "",

            "remarks": "",
        })

    # ---------------------------------------------------------
    # Total Quantity Display
    # ---------------------------------------------------------
    if total_qty == int(total_qty):

        total_qty_display = str(
            int(total_qty)
        )

    else:

        total_qty_display = (
            f"{total_qty:,.2f}"
        )

    # ---------------------------------------------------------
    # Render HTML
    # ---------------------------------------------------------
    html = template.render(

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------
        company_name=data.get(
            "company_name",
            ""
        ),

        company_address=data.get(
            "company_address",
            ""
        ),

        company_phone=data.get(
            "company_phone",
            ""
        ),

        company_email=data.get(
            "company_email",
            ""
        ),

        company_ntn=data.get(
            "company_ntn",
            ""
        ),

        company_strn=data.get(
            "company_strn",
            ""
        ),

        # -----------------------------------------------------
        # Factory
        # -----------------------------------------------------
        factory_name=data.get(
            "factory_name",
            ""
        ),

        factory_address=data.get(
            "factory_address",
            ""
        ),

        factory_phone=data.get(
            "factory_phone",
            ""
        ),

        factory_email=data.get(
            "factory_email",
            ""
        ),

        factory_ntn=data.get(
            "factory_ntn",
            ""
        ),

        factory_strn=data.get(
            "factory_strn",
            ""
        ),

        # -----------------------------------------------------
        # Copy
        # -----------------------------------------------------
        copy_label=data.get(
            "copy_label",
            "Original"
        ),

        # -----------------------------------------------------
        # Job Order
        # -----------------------------------------------------
        order_no=data.get(
            "order_no",
            ""
        ),

        job_order_entitlement_person=data.get(
            "job_order_entitlement_person",
            ""
        ),

        customer_name=data.get(
            "customer_name",
            ""
        ),

        order_date=data.get(
            "order_date",
            ""
        ),

        delivery_date=data.get(
            "delivery_date",
            ""
        ),

        # -----------------------------------------------------
        # Ship To
        # -----------------------------------------------------
        ship_to_company=data.get(
            "ship_to_company",
            ""
        ),

        ship_to_address=data.get(
            "ship_to_address",
            ""
        ),

        ship_to_name=data.get(
            "ship_to_name",
            ""
        ),

        ship_to_phone=data.get(
            "ship_to_phone",
            ""
        ),

        # -----------------------------------------------------
        # Material
        # NOTE: kwarg names must match the template's variable
        # names exactly ({{ material_size }}, {{ material_guage }},
        # {{ material_color }}). Previously these were passed as
        # size=/guage=/color=, which the template never referenced,
        # so those cells always rendered blank.
        # -----------------------------------------------------
        material=material,

        material_size=material_size,

        material_guage=material_guage,

        material_color=material_color,

        # -----------------------------------------------------
        # Users
        # -----------------------------------------------------
        created_by=data.get(
            "created_by",
            ""
        ),

        created_by_designation=data.get(
            "created_by_designation",
            ""
        ),

        created_by_phone=data.get(
            "created_by_phone",
            ""
        ),

        approved_by=data.get(
            "approved_by",
            ""
        ),

        approved_by_designation=data.get(
            "approved_by_designation",
            ""
        ),

        approved_by_phone=data.get(
            "approved_by_phone",
            ""
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
                "attachment; filename=job_order.pdf"
        },
    )
