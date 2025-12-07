from flask import Flask, request, jsonify, render_template
import csv, os
from datetime import datetime
import re

app = Flask(__name__)

ORDERS_FILE = "orders.csv"

# Create orders.csv if missing
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Buyer", "Product", "Quantity"])

# -----------------------------
# AI Chat Backend
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").lower()

        # Parse orders like "500kg black tea"
        order_match = re.search(r'(\d+)\s*kg.*(green|black|herbal)\s*tea', msg)
        if order_match:
            quantity = order_match.group(1)
            product = order_match.group(2).title()
            return jsonify({"reply": f"✅ Your order of {quantity}kg {product} has been received!"})

        if "price" in msg or "cost" in msg:
            return jsonify({"reply": "💰 Prices: Black Tea $5/kg, Green Tea $6/kg, Herbal Tea $7/kg"})

        if any(g in msg for g in ["hi","hello","hey"]):
            return jsonify({"reply":"Hello! How can I help you today?"})

        return jsonify({"reply":"I can help you order tea, check prices or delivery updates."})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Server error: {e}"})

# -----------------------------
# Orders Endpoint
# -----------------------------
@app.route("/order", methods=["POST"])
def order():
    try:
        data = request.json
        name = data.get("name", "Unknown")
        product = data.get("product", "Unknown")
        quantity = int(data.get("quantity", 0))

        with open(ORDERS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, product, quantity])

        return jsonify({"status":"success"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# Dashboard data API
# -----------------------------
@app.route("/dashboard_data")
def dashboard_data():
    labels = []
    data = []
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE) as f:
            next(f)  # skip header
            for line in f:
                t,b,p,q = line.strip().split(",")
                labels.append(t)
                data.append(int(q))
    return jsonify({"labels": labels, "data": data})

# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
