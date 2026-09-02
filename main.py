from fastapi import FastAPI, Body


from purchase_order import generate_purchase_order
from purchase_order_dup import generate_purchase_order_dup

app = FastAPI()


@app.get("/")
def home():
    return {"message": "ERP PDF Service Running"}


@app.post("/generate-pdf")
def generate_pdf(data: dict = Body(...)):

    invoice_type = data.get("invoice_type", "").upper()

    if invoice_type == "PURCHASE_ORDER":
        return generate_purchase_order(data)
    elif invoice_type == "PURCHASE_ORDER_DUP":
        return generate_purchase_order_dup(data)

    return {
        "error": "Unsupported invoice type"
    }