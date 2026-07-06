
from fastapi.responses import Response
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import os, json, qrcode

def generate_purchase_requisition(data):
    company_name = data.get("company_name","")
    company_address = data.get("company_address","")
    pr_no = data.get("pr_no","")
    request_date = data.get("request_date","")
    requested_by = data.get("requested_by", "")
    department = data.get("department", "")
    business_unit = data.get("business_unit", "")
    status = data.get("status", "")
    approved_by = data.get("approved_by", "")
    approved_date = data.get("approved_date","")
    items = data.get("items",[])

    qr_data = {
    "company_name": company_name,
    "company_address": company_address,
    "pr_no": pr_no,
    "request_date": request_date,
    "requested_by": requested_by,
    "department": department,
    "business_unit": business_unit,
    "status": status,
    "approved_by": approved_by,
    "approved_date": approved_date
}

    qr = qrcode.QRCode(version=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=6,
                       border=2)
    qr.add_data(json.dumps(qr_data, separators=(",",":")))
    qr.make(fit=True)

    qr_buffer = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=0.9*inch, height=0.9*inch)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(595,842),
                            rightMargin=30,leftMargin=30,
                            topMargin=30,bottomMargin=30)

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

    story.append(Paragraph("<b><font size=18>PURCHASE REQUISITION</font></b>", title))
    story.append(Spacer(1,20))

    info = Table([
    ["PR No", pr_no],
    ["Request Date", request_date],
    ["Requested By", requested_by],
    ["Department", department],
    ["Business Unit", business_unit],
    ["Status", status],
    ["Approved By", approved_by],
    ["Approved Date", approved_date]
], colWidths=[140,340])

    info.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)
    ]))
    story += [info, Spacer(1,25)]

    table_data=[["Sr#","Item Name","Quantity"]]
    total_quantity=0
    for i,item in enumerate(items, start=1):
        qty=float(item.get("quantity",0) or 0)
        total_quantity += qty
        table_data.append([
            str(item.get("sr_no", i)),
            item.get("item_name",""),
            str(item.get("quantity",""))
        ])

    table=Table(table_data,colWidths=[60,320,120])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9EAD3")),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("ALIGN",(1,1),(1,-1),"LEFT"),
        ("BOTTOMPADDING",(0,0),(-1,0),10)
    ]))
    story += [table, Spacer(1,15)]

    tq = int(total_quantity) if total_quantity.is_integer() else total_quantity
    total = Table([["Total Quantity", str(tq)]], colWidths=[380,120])
    total.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(0,0),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
        ("ALIGN",(1,0),(1,0),"CENTER")
    ]))
    story += [total, Spacer(1,40)]

    sign=Table([
        ["Prepared By","Approved By"],
        ["\n\n____________________","\n\n____________________"],
        [requested_by,approved_by]
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
        headers={"Content-Disposition":f"attachment; filename=Purchase_Requisition_{pr_no}.pdf"}
    )
