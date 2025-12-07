from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Health Check
# -----------------------------
@app.route("/health")
def health():
    return "OK"

# -----------------------------
# Home – AI Chat UI
# -----------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Rwanda Mountain Tea – AI Assistant</title>
        <style>
            body { font-family: Arial; background: #f4f6f8; }
            .container { width: 450px; margin: 40px auto; background: white; padding: 20px; border-radius: 10px; }
            .bot { background: #e6f2ff; padding: 10px; margin: 5px 0; border-radius: 8px; }
            .user { background: #d1ffe0; padding: 10px; margin: 5px 0; border-radius: 8px; text-align: right; }
            input, button { width: 100%; padding: 10px; margin-top: 10px; }
            button { background: #1b5e20; color: white; border: none; border-radius: 5px; }
            #chat { height: 300px; overflow-y: scroll; border:1px solid #ccc; padding:10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h3>Rwanda Mountain Tea – AI Order Assistant</h3>
            <div id="chat"></div>
            <input id="msg" placeholder="Type your message..." />
            <button onclick="send()">Send</button>
        </div>

        <script>
        function send() {
            const msg = document.getElementById("msg").value;
            if(msg.trim() === '') return;
            const chat = document.getElementById("chat");
            chat.innerHTML += `<div class="user">${msg}</div>`;
            document.getElementById("msg").value = '';

            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({message: msg})
            })
            .then(r => r.json())
            .then(d => {
                chat.innerHTML += `<div class="bot">${d.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
            });
        }
        </script>
    </body>
    </html>
    """

# -----------------------------
# AI Chat Backend
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").lower()

        if "order" in msg:
            reply = "✅ Your tea order has been captured and sent to Rwanda Mountain Tea team."
        elif "price" in msg:
            reply = "💰 Pricing depends on tea grade and export destination."
        else:
            reply = "Hello! I am Rwanda Mountain Tea’s AI assistant. How can I help you?"

        return jsonify({"reply": reply})
    except Exception:
        return jsonify({"reply": "⚠️ Server error. Try again."})

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
    import pandas as pd
    rows = []
    if os.path.exists("orders.csv"):
        df = pd.read_csv("orders.csv")
        rows = df.to_dict(orient="records")
    else:
        rows = []

    # HTML table
    html = "<html><head><title>RMT Dashboard</title><script src='https://cdn.jsdelivr.net/npm/chart.js'></script></head><body>"
    html += "<h2>Orders Dashboard</h2>"
    html += "<canvas id='chart' width='600' height='400'></canvas>"
    html += "<table border='1'><tr><th>Time</th><th>Buyer</th><th>Product</th><th>Quantity</th></tr>"
    for r in rows:
        html += f"<tr><td>{r['Time']}</td><td>{r['Buyer']}</td><td>{r['Product']}</td><td>{r['Quantity']}</td></tr>"
    html += "</table>"

    # Chart.js script
    html += """
    <script>
    const ctx = document.getElementById('chart').getContext('2d');
    const labels = """ + str([r['Time'] for r in rows]) + """;
    const data = """ + str([int(r['Quantity']) for r in rows]) + """;
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quantity Ordered',
                data: data,
                backgroundColor: 'rgba(27, 94, 32, 0.7)'
            }]
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
    </script></body></html>
    """
    return html

# -----------------------------
# WhatsApp Webhook
# -----------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").lower()
    if "order" in msg:
        return "✅ Your tea order has been received and is being processed."
    return "Hello from Rwanda Mountain Tea AI assistant."

# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
