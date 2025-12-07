from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
import html
import random
import re

app = Flask(__name__)

# -----------------------------
# Initialize fake historical orders
# -----------------------------
def init_fake_orders():
    if not os.path.exists("orders.csv") or os.path.getsize("orders.csv") == 0:
        buyers = ["Alice Ltd", "Bob Exports", "Charlie Traders", "Diana Co", "Eagle Corp"]
        products = ["Green Tea", "Black Tea", "Herbal Tea"]
        with open("orders.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Buyer", "Product", "Quantity"])
            for _ in range(10):
                time = datetime.now() - timedelta(hours=random.randint(1, 48))
                buyer = random.choice(buyers)
                product = random.choice(products)
                quantity = random.randint(50, 1000)
                writer.writerow([time, buyer, product, quantity])

init_fake_orders()

# -----------------------------
# Health Check
# -----------------------------
@app.route("/health")
def health():
    return "OK"

# -----------------------------
# AI Chat Backend – dynamic parsing
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").lower()

        # Match orders like "500kg black tea"
        order_match = re.search(r'(\d+)\s*kg.*(green|black|herbal)\s*tea', msg)
        if order_match:
            quantity = order_match.group(1)
            product = order_match.group(2).title()
            return jsonify({"reply": f"✅ Your order of {quantity}kg {product} has been received and is being processed."})

        if "price" in msg or "cost" in msg:
            return jsonify({"reply": "💰 Current prices: Black Tea $5/kg, Green Tea $6/kg, Herbal Tea $7/kg."})

        if any(g in msg for g in ["hi", "hello", "hey"]):
            return jsonify({"reply": "Hello! How can I help you today?"})

        return jsonify({"reply": "I’m here to help you with orders, prices, or delivery updates."})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Server error: {e}"})

# -----------------------------
# Orders API
# -----------------------------
@app.route("/order", methods=["POST"])
def order():
    try:
        data = request.json
        name = data.get("name", "Unknown")
        product = data.get("product", "Unknown")
        quantity = int(data.get("quantity", 0))

        if not os.path.exists("orders.csv"):
            with open("orders.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Buyer", "Product", "Quantity"])

        with open("orders.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, product, quantity])

        return jsonify({"status": "success", "message": "Order saved"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():
    rows = []
    try:
        if os.path.exists("orders.csv"):
            df = pd.read_csv("orders.csv")
            df = df.dropna(subset=["Time", "Buyer", "Product", "Quantity"])
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce').fillna(0).astype(int)
            rows = df.to_dict(orient="records")
    except Exception as e:
        print("Error reading CSV:", e)
        rows = []

    html_content = "<html><head><title>RMT Dashboard</title><script src='https://cdn.jsdelivr.net/npm/chart.js'></script></head><body>"
    html_content += "<h2>Orders Dashboard</h2>"
    html_content += "<canvas id='chart' width='600' height='400'></canvas>"
    html_content += "<table border='1'><tr><th>Time</th><th>Buyer</th><th>Product</th><th>Quantity</th></tr>"

    for r in rows:
        html_content += f"<tr><td>{html.escape(str(r['Time']))}</td><td>{html.escape(str(r['Buyer']))}</td><td>{html.escape(str(r['Product']))}</td><td>{r['Quantity']}</td></tr>"

    html_content += "</table>"

    labels = [html.escape(str(r['Time'])) for r in rows]
    data = [r['Quantity'] for r in rows]

    html_content += f"""
    <script>
    const ctx = document.getElementById('chart').getContext('2d');
    const chart = new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: {labels},
            datasets: [{{
                label: 'Quantity Ordered',
                data: {data},
                backgroundColor: 'rgba(27, 94, 32, 0.7)'
            }}]
        }},
        options: {{
            responsive: true,
            scales: {{ y: {{ beginAtZero: true }} }},
            animation: {{ duration: 500 }}
        }}
    }});

    setInterval(() => {{
        fetch('/dashboard_data')
        .then(r => r.json())
        .then(d => {{
            chart.data.labels = d.labels;
            chart.data.datasets[0].data = d.data;
            chart.update();
        }});
    }}, 5000);
    </script></body></html>
    """
    return html_content

# -----------------------------
# Dashboard data API
# -----------------------------
@app.route("/dashboard_data")
def dashboard_data():
    rows = []
    if os.path.exists("orders.csv"):
        df = pd.read_csv("orders.csv")
        df = df.dropna(subset=["Time", "Buyer", "Product", "Quantity"])
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce').fillna(0).astype(int)
        rows = df.to_dict(orient="records")
    labels = [str(r['Time']) for r in rows]
    data = [r['Quantity'] for r in rows]
    return jsonify({"labels": labels, "data": data})

# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
