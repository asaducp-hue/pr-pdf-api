from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os

def generate_purchase_order(data):

    # Load HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("purchase_order.html")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "static", "logo.png")
    css_file = os.path.join(base_dir, "static", "purchase_order.css")

    # Amounts
    total_amount = float(data.get("total_amount", 0) or 0)
    discount_amount = float(data.get("discount_amount", 0) or 0)
    gst_amount = float(data.get("gst_amount", 0) or 0)
    net_amount = float(data.get("net_amount", 0) or 0)

    # Render HTML
    html = template.render(
        company_name=data.get("company_name", ""),
        company_address=data.get("company_address", ""),
        po_no=data.get("po_no", ""),
        po_date=data.get("po_date", ""),
        supplier=data.get("supplier", ""),
        total_amount=f"{total_amount:,.2f}",
        discount_amount=f"{discount_amount:,.2f}",
        gst_amount=f"{gst_amount:,.2f}",
        net_amount=f"{net_amount:,.2f}",
        items=data.get("items", []),
        logo_path=logo_path
    )

    # Generate PDF
    pdf = HTML(
        string=html,
        base_url=base_dir
    ).write_pdf(
        stylesheets=[CSS(filename=css_file)]
    )

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=Purchase_Order.pdf"
        }
    )