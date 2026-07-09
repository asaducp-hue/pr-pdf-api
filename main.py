from fastapi import FastAPI, Body

from reports.purchase_requisition import generate_purchase_requisition
from reports.purchase_order import generate_purchase_order

app = FastAPI()


@app.get("/")
def home():
    return {"message": "ERP PDF Service Running"}


@app.post("/generate-pdf")
def generate_pdf(data: dict = Body(...)):

    invoice_type = data.get("invoice_type", "").upper()

    if invoice_type == "PURCHASE_REQUISITION":
        return generate_purchase_requisition(data)

    elif invoice_type == "PURCHASE_ORDER":
        return generate_purchase_order(data)

    return {
        "error": "Unsupported invoice type"
    }