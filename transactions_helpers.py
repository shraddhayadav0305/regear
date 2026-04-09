def map_payment_method(raw_method):
    if not raw_method:
        return "UPI"
    method = str(raw_method).strip().lower()
    if method in ["upi"]:
        return "UPI"
    if method in ["wallet", "paytm", "phonepe", "gpay"]:
        return "Wallet"
    if method in ["card", "credit_card", "creditcard", "debit_card", "debitcard", "netbanking", "net_banking"]:
        return "Card"
    return method.title()


def map_transaction_status(raw_status):
    if not raw_status:
        return "failed"
    status = str(raw_status).strip().lower()
    if status in ["completed", "success", "paid"]:
        return "completed"
    if status in ["refunded", "refund"]:
        return "refunded"
    return "failed"


def calculate_gst(base_amount):
    try:
        amount = float(base_amount)
    except (ValueError, TypeError):
        amount = 0.0
    return round(amount * 0.18, 2)


def calculate_total(base_amount):
    try:
        amount = float(base_amount)
    except (ValueError, TypeError):
        amount = 0.0
    return round(amount + calculate_gst(amount), 2)
