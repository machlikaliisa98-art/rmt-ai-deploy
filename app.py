from flask import Flask, request, jsonify, render_template
import csv
from datetime import datetime
import os

app = Flask(__name__)

# -----------------------------
# Health Check
# -----------------------------
@app.route("/health")
def health():
    return "OK"

# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():
    return """
    <h2>Rwanda Mountain Tea – AI Order Automation</h2>
    <p>System running successfully.</p>
    """

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():
    orders = []
    if os.path.exists("orders.csv"):
        with open("orders.csv", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                orders.append(row)

    html = "<h2>Orders Dashboard</h2><table border=1>"
    for row in orders:
        html += "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>"
    html += "</table>"
    return html

# -----------------------------
# Web Order API
# -----------------------------
@app.route("/order", methods=["POST"])
def order():
    data = request.json
    name = data.get("name")
    product = data.get("product")
    quantity = data.get("quantity")

    with open("orders.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), name, product, quantity])

    return jsonify({
        "status": "success",
        "message": "Order received successfully"
    })

# -----------------------------
# WhatsApp Webhook Simulation
# -----------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").lower()

    if "order" in msg:
        reply = "✅ Your tea order has been received and is being processed."
    else:
        reply = "Hello from Rwanda Mountain Tea AI assistant."

    return reply

# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
