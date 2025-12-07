from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime
import pandas as pd
import html
import random

app = Flask(__name__)

# -----------------------------
# Health Check
# -----------------------------
@app.route("/health")
def health():
    return "OK"

# -----------------------------
# Home – WhatsApp-style Chat UI with Typing Effect
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
            .typing { font-style: italic; color: #555; }
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

            // Typing indicator
            const typingDiv = document.createElement("div");
            typingDiv.className = "message bot typing";
            typingDiv.innerText = "AI is typing...";
            chat.appendChild(typingDiv);
            chat.scrollTop = chat.scrollHeight;

            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({message: msg})
            })
            .then(r => r.json())
            .then(d => {
                typingDiv.remove();
                chat.innerHTML += `<div class="message bot">${d.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
            });
        }

        document.getElementById("msg").addEventListener("keydown", function(e){
            if(e.key === "Enter") send();
        });
        </script>
    </body>
    </html>
    """

# -----------------------------
# AI Chat Backend – dynamic responses
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        msg = data.get("message", "").lower()

        responses = {
            "order": [
                "✅ Your tea order has been captured and sent to our team.",
                "Got it! Your order is now in our system.",
                "Your tea order has been received. We'll process it shortly."
            ],
            "price": [
                "💰 Pricing depends on tea type and quantity.",
                "The current price for black tea is $5/kg, green tea $6/kg, herbal tea $7/kg.",
                "Pricing varies by order size. Can you tell me the quantity you want?"
            ],
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! Ready to take your tea orders.",
                "Hey! I'm Rwanda Mountain Tea’s AI assistant."
            ],
            "default": [
                "I’m here to help you with orders, prices, or delivery updates.",
                "Can you clarify your request? I can help with tea orders.",
                "I didn’t quite get that, but I can help you order tea or check prices."
            ]
        }

        if "order" in msg:
            reply = random.choice(responses["order"])
        elif "price" in msg or "cost" in msg:
            reply = random.choice(responses["price"])
        elif any(g in msg for g in ["hi", "hello", "hey"]):
            reply = random.choice(responses["greeting"])
        else:
            reply = random.choice(responses["default"])

        return jsonify({"reply": reply})
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
# Dashboard – Live chart & table
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
