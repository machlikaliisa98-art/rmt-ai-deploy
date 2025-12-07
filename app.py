import os
import pandas as pd
from flask import Flask, request, render_template
from twilio.rest import Client
from dotenv import load_dotenv
import datetime
import openai
@app.route("/health")
def health():
    return "OK"

load_dotenv()

app = Flask(__name__)

# Load keys
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = Client(TWILIO_SID, TWILIO_AUTH)
openai.api_key = OPENAI_API_KEY

ORDERS_FILE = "orders.csv"

# Send WhatsApp message
def send_whatsapp(to, message):
    client.messages.create(
        body=message,
        from_=WHATSAPP_NUMBER,
        to=to
    )

# Save orders
def save_order(customer, product, quantity):
    df = pd.read_csv(ORDERS_FILE)
    df.loc[len(df)] = [
        customer, product, quantity, "Confirmed", datetime.datetime.now()
    ]
    df.to_csv(ORDERS_FILE, index=False)

# AI reply
def ai_reply(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional sales assistant for Rwanda Mountain Tea Ltd."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message["content"]

# WhatsApp webhook
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").lower()
    sender = request.values.get("From")

    # Simple order detector
    if "order" in incoming_msg:
        product = "Black Tea"
        quantity = "1"

        save_order(sender, product, quantity)

        reply = f"✅ Order received!\nProduct: {product}\nQuantity: {quantity}\nStatus: Confirmed\nRwanda Mountain Tea"
    else:
        reply = ai_reply(incoming_msg)

    send_whatsapp(sender, reply)
    return "OK", 200

# Dashboard
@app.route("/")
def dashboard():
    df = pd.read_csv(ORDERS_FILE)

    orders_count = len(df)

    return render_template("dashboard.html",
                           tables=[df.to_html()],
                           orders_count=orders_count)

if __name__ == "__main__":
    app.run(debug=True)

