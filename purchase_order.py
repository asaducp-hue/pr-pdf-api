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

    items = []
    for i, item in enumerate(data.get("items", []), start=1):
        items.append({
        "sr_no": item.get("sr_no", i),
        "item_name": item.get("item_name", ""),
        "size": item.get("size", ""),
        "quantity": item.get("quantity", ""),
        "unit_price": f'{float(item.get("unit_price", 0) or 0):,.2f}',
        "line_total": f'{float(item.get("line_total", 0) or 0):,.2f}'
    })

    # Render HTML
    html = template.render(
        company_name=data.get("company_name", ""),
        company_address=data.get("company_address", ""),
        po_no=data.get("po_no", ""),
        po_date=data.get("po_date", ""),
        supplier=data.get("supplier", ""),
        company_phone=data.get("company_phone", ""),
        supplier_address=data.get("supplier_address", ""),
        supplier_phone=data.get("supplier_phone", ""),
        business_unit_address=data.get("business_unit_address", ""),
        business_unit_phone=data.get("business_unit_phone", ""),
        shipping_terms=data.get("shipping_terms", ""),
        remarks=data.get("remarks", ""),
        shipping_amount=data.get("shipping_amount", ""),
        delivery_date=data.get("delivery_date", ""),
        other_amount=data.get("other_amount", ""),
        shipping_method=data.get("shipping_method", ""),
        total_amount=f"{total_amount:,.2f}",
        discount_amount=f"{discount_amount:,.2f}",
        gst_amount=f"{gst_amount:,.2f}",
        net_amount=f"{net_amount:,.2f}",
        items=items,
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