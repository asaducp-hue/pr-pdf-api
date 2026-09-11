from fastapi import FastAPI, Body


from purchase_order import generate_purchase_order
from purchase_order_dup import generate_purchase_order_dup
from purchase_requisition import generate_purchase_requisition
from grn import generate_grn
from igp import generate_igp
from quotation import generate_quotation
from quotation_dup import generate_quotation_dup
from sales_order import generate_sales_order
from sales_order_dup import generate_sales_order_dup
from sales_invoice import generate_sales_invoice

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
    elif invoice_type == "PURCHASE_REQUISITION":
        return generate_purchase_requisition(data)
    elif invoice_type == "GRN":
        return generate_grn(data)
    elif invoice_type == "IGP":
        return generate_igp(data)
    elif invoice_type == "SALES_QUOTATION":
        return generate_quotation(data)
    elif invoice_type == "SALES_QUOTATION_DUP":
        return generate_quotation_dup(data)
    elif invoice_type == "SALES_ORDER":
            return generate_sales_order(data)
    elif invoice_type == "SALES_ORDER_DUP":
                return generate_sales_order_dup(data)
    elif invoice_type == "SALES_INVOICE":
                    return generate_sales_invoice(data)

    return {
        "error": "Unsupported invoice type"
    }