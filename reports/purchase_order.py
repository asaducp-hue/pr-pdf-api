from fastapi.responses import Response
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import os, json, qrcode

def generate_purchase_order(data):
    company_name = data.get("company_name","")
    company_address = data.get("company_address","")
    po_no = data.get("po_no","")
    po_date = data.get("po_date","")
    pr_no = data.get("pr_no","")
    supplier = data.get("supplier","")
    prepared_by = data.get("prepared_by","")

    total_amount = float(data.get("total_amount",0) or 0)
    discount_amount = float(data.get("discount_amount",0) or 0)
    gst_amount = float(data.get("gst_amount",0) or 0)
    net_amount = float(data.get("net_amount",0) or 0)

    items = data.get("items",[])

    qr_data = {
        "company_name": company_name,
        "company_address": company_address,
        "po_no": po_no,
        "po_date": po_date,
        "pr_no": pr_no,
        "supplier": supplier,
        "total_amount": total_amount,
        "net_amount": net_amount
    }

    qr = qrcode.QRCode(version=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=6,
                       border=2)
    qr.add_data(json.dumps(qr_data,separators=(",",":")))
    qr.make(fit=True)

    qr_buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer,width=0.9*inch,height=0.9*inch)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=(595,842),
                            rightMargin=30,
                            leftMargin=30,
                            topMargin=30,
                            bottomMargin=30)

    styles = getSampleStyleSheet()
    title = styles["Heading1"]
    title.alignment = TA_CENTER

    story=[]

    logo_path="logo.png"
    logo = Image(logo_path,width=0.9*inch,height=0.9*inch) if os.path.exists(logo_path) else Paragraph("",styles["Normal"])

    company = Paragraph(f"<b>{company_name}</b><br/>{company_address}", styles["Title"])

    header = Table([[logo,company,qr_image]], colWidths=[80,350,80])
    header.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(2,0),(2,0),"RIGHT")
    ]))
    story += [header, Spacer(1,20)]

    story.append(Paragraph("<b><font size=18>PURCHASE ORDER</font></b>", title))
    story.append(Spacer(1,20))

    info = Table([
        ["PO No", po_no],
        ["PO Date", po_date],
        ["PR No", pr_no],
        ["Supplier", supplier]
    ], colWidths=[140,340])

    info.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)
    ]))
    story += [info, Spacer(1,25)]

    table_data=[["Sr#","Item Name","Quantity","Unit Price","Line Total"]]

    for i,item in enumerate(items,start=1):
        table_data.append([
            str(item.get("sr_no",i)),
            item.get("item_name",""),
            str(item.get("quantity","")),
            f'{float(item.get("unit_price",0) or 0):,.2f}',
            f'{float(item.get("line_total",0) or 0):,.2f}'
        ])

    table=Table(table_data,colWidths=[45,210,70,90,100])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9EAD3")),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("ALIGN",(1,1),(1,-1),"LEFT"),
        ("BOTTOMPADDING",(0,0),(-1,0),10)
    ]))
    story += [table, Spacer(1,15)]

    totals = Table([
        ["Total Amount", f"{total_amount:,.2f}"],
        ["Discount", f"{discount_amount:,.2f}"],
        ["GST", f"{gst_amount:,.2f}"],
        ["Net Amount", f"{net_amount:,.2f}"]
    ], colWidths=[380,120])

    totals.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
        ("ALIGN",(1,0),(1,-1),"RIGHT")
    ]))
    story += [totals, Spacer(1,40)]

    sign=Table([
        ["Prepared By","Approved By"],
        ["\n\n____________________","\n\n____________________"],
        [prepared_by,""]
    ], colWidths=[250,250])

    sign.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")
    ]))
    story.append(sign)

    doc.build(story)

    pdf=buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition":f"attachment; filename=Purchase_Order_{po_no}.pdf"}
    )
