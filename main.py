from fastapi import FastAPI, Body
from reports.purchase_requisition import generate_purchase_requisition

app = FastAPI()


@app.get("/")
def home():
    return {"message": "ERP PDF Service Running"}


@app.post("/generate-pdf")
def generate_pdf(data: dict = Body(...)):

    invoice_type = data.get("invoice_type", "").upper()

    if invoice_type == "PURCHASE_REQUISITION":
        return generate_purchase_requisition(data)

    return {
        "error": "Unsupported invoice type"
    }