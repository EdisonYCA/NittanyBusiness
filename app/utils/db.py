from app import get_db

def get_user_type(email):
    db = get_db()
    buyer = db.execute("SELECT * FROM Buyers WHERE email = ?", [email]).fetchone()
    seller = db.execute("SELECT * FROM Sellers WHERE email = ?", [email]).fetchone()

    if buyer:
        return "Buyer"
    if seller:
        return "Seller"
    return "Helpdesk"