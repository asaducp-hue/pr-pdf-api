from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import os

def generate_purchase_order(data):

    # Load HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("purchase_order.html")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "static", "logo.png")

    # Render HTML with data
    html = template.render(
        company_name=data.get("company_name", ""),
        company_address=data.get("company_address", ""),
        po_no=data.get("po_no", ""),
        po_date=data.get("po_date", ""),
        supplier=data.get("supplier", ""),
        items=data.get("items", [])
    )

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_file = os.path.join(base_dir, "static", "purchase_order.css")

    # Generate PDF
    pdf = HTML(
        string=html,
        base_url=base_dir
    ).write_pdf(
        stylesheets=[CSS(filename=css_file)]
    )

    # Return PDF
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=Purchase_Order.pdf"
        }
    )