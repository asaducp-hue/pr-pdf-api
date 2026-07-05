from fastapi import FastAPI
from fastapi.responses import Response
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import os

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Purchase Requisition PDF API Running"}


@app.get("/purchase-requisition")
def purchase_requisition():

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(595,842),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    story = []

    #################################################
    # Company Header
    #################################################

    logo_path = "logo.png"

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=0.9*inch, height=0.9*inch)
    else:
        logo = Paragraph("", styles["Normal"])

    title = styles["Heading1"]
    title.alignment = TA_CENTER

    company = Paragraph(
        """
        <b>ILLHAQ Steel Engineering (Private) Limited</b><br/>
        B Block Model Town, Lahore
        """,
        styles["Title"]
    )

    header = Table([
        [logo, company]
    ], colWidths=[80,430])

    story.append(header)
    story.append(Spacer(1,20))

    #################################################
    # Report Title
    #################################################

    story.append(Paragraph(
        "<b><font size=18>PURCHASE REQUISITION</font></b>",
        title
    ))

    story.append(Spacer(1,20))

    #################################################
    # Header Information
    #################################################

    info = Table([
        ["PR No", "PR-000001"],
        ["Request Date", "29-06-2026"],
        ["Requested By", "Malik Riaz"],
        ["Status", "Approved"],
        ["Approved By", "Asad"],
        ["Approved Date", "04-07-2026"]
    ], colWidths=[140,340])

    info.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,-1),8)
    ]))

    story.append(info)

    story.append(Spacer(1,25))

    #################################################
    # Items
    #################################################

    data = [
        ["Sr#", "Item Name", "Quantity"],
        ["1","Steel Plates","4"],
        ["2","MS Sheet","3"]
    ]

    table = Table(data, colWidths=[60,320,120])

    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D9EAD3")),
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("ALIGN",(1,1),(1,-1),"LEFT"),
        ("BOTTOMPADDING",(0,0),(-1,0),10)
    ]))

    story.append(table)

    story.append(Spacer(1,15))

    #################################################
    # Total Quantity
    #################################################

    total = Table([
        ["Total Quantity", "7"]
    ], colWidths=[380,120])

    total.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(0,0),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
        ("ALIGN",(1,0),(1,0),"CENTER")
    ]))

    story.append(total)

    story.append(Spacer(1,40))

    #################################################
    # Signatures
    #################################################

    sign = Table([
        ["Prepared By","Approved By"],
        ["\n\n____________________","\n\n____________________"],
        ["Malik Riaz","Asad"]
    ], colWidths=[250,250])

    sign.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")
    ]))

    story.append(sign)

    #################################################

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=Purchase_Requisition_PR-000001.pdf"
        }
    )