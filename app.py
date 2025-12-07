from flask import Flask, request, jsonify
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
            .container { width: 400px; margin: 40px auto; background: white; padding: 20px; border-radius: 10px; }
            .bot { background: #e6f2ff; padding: 10px; margin: 5px 0; border-radius: 8px; }
            .user { background: #d1ffe0; padding: 10px; margin: 5px 0; border-radius: 8px; text-align: right; }
            input, button { width: 100%; padding: 10px; margin-top: 10px; }
            button { background: #1b5e20; color: white; border: none; border-radius: 5px; }
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
            const chat = document.getElementById("chat");
            chat.innerHTML += `<div class="user">${msg}</div>`;
            
            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({message: msg})
            })
            .then(r => r.json())
            .then(d => {
                chat.innerHTML += `<div class="bot">${d.reply}</div>`;
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
            reply = "Hello, I am Rwanda Mountain Tea’s AI assistant. How can I help you?"

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "System error, but server is still running."})

# -----------------------------
# Order API
# -----------------------------
@app.route("/order", methods=["POST"])
def order():
    try:
        data = request.json
        name = data.get("name")
        product = data.get("product")
        quantity = data.get("quantity")

        with open("orders.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, product, quantity])

        return jsonify({"status": "success", "message": "Order saved"})
    except:
        return jsonify({"status": "error"})

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():
    rows = []
    if os.path.exists("orders.csv"):
        with open("orders.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)

    html = "<h2>Orders Dashboard</h2><table border=1>"
    for r in rows:
        html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    html += "</table>"
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
