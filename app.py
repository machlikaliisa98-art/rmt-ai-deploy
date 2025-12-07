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
# Home – WhatsApp-style Chat UI
# -----------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Rwanda Mountain Tea – AI Assistant</title>
        <style>
            body { font-family: Arial; background: #e5ddd5; }
            .container { width: 400px; margin: 20px auto; background: #f0f0f0; border-radius: 10px; display: flex; flex-direction: column; }
            .chat-header { background: #075e54; color: white; padding: 15px; border-radius: 10px 10px 0 0; font-weight: bold; text-align: center; }
            .chat-body { flex: 1; padding: 10px; overflow-y: scroll; height: 400px; background: #ece5dd; }
            .message { padding: 8px 12px; margin: 5px 0; border-radius: 20px; max-width: 80%; }
            .bot { background: white; color: black; align-self: flex-start; }
            .user { background: #dcf8c6; color: black; align-self: flex-end; }
            .chat-footer { display: flex; border-top: 1px solid #ccc; }
            .chat-footer input { flex: 1; padding: 10px; border: none; border-radius: 0; }
            .chat-footer button { padding: 10px; background: #25d366; border: none; color: white; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="chat-header">Rwanda Mountain Tea – AI Assistant</div>
            <div id="chat" class="chat-body"></div>
            <div class="chat-footer">
                <input id="msg" placeholder="Type a message..." />
                <button onclick="send()">Send</button>
            </div>
        </div>

        <script>
        function send() {
            const input = document.getElementById("msg");
            const msg = input.value.trim();
            if(!msg) return;
            input.value = '';

            const chat = document.getElementById("chat");
            chat.innerHTML += `<div class="message user">${msg}</div>`;
            chat.scrollTop = chat.scrollHeight;

            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({message: msg})
            })
            .then(r => r.json())
            .then(d => {
                chat.innerHTML += `<div class="message bot">${d.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
            });
        }

        // Optional: send message on Enter key
        document.getElementById("msg").addEventListener("keydown", function(e){
            if(e.key === "Enter") send();
        });
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

    html = "<html><head><title>RMT Dashboard</title><script src='https://cdn.jsdelivr.net/npm/chart.js'></script></head><body>"
    html += "<h2>Orders Dashboard</h2>"
    html += "<canvas id='chart' width='600' height='400'></canvas>"
    html += "<table border='1'><tr><th>Time</th><th>Buyer</th><th>Product</th><th>Quantity</th></tr>"
    for r in rows:
        html += f"<tr><td>{r['Time']}</td><td>{r['Buyer']}</td><td>{r['Product']}</td><td>{r['Quantity']}</td></tr>"
    html += "</table>"

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
