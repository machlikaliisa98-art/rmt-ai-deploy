from flask import Flask, request, jsonify
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
# Dashboard (All-in-One HTML)
# -----------------------------
@app.route("/dashboard")
def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Rwanda Mountain Tea Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h2>Orders Dashboard</h2>
  <canvas id="chart" width="800" height="400"></canvas>
  <table border="1" id="ordersTable">
    <tr><th>Time</th><th>Buyer</th><th>Product</th><th>Quantity</th></tr>
  </table>

<script>
async function refreshDashboard(){
  const res = await fetch('/dashboard_data');
  const d = await res.json();

  // Update chart
  chart.data.labels = d.labels;
  chart.data.datasets[0].data = d.quantities;
  chart.update();

  // Update table
  const table = document.getElementById('ordersTable');
  table.innerHTML = "<tr><th>Time</th><th>Buyer</th><th>Product</th><th>Quantity</th></tr>";
  for(let i=0;i<d.labels.length;i++){
    const row = `<tr>
      <td>${d.labels[i]}</td>
      <td>${d.buyers[i]}</td>
      <td>${d.products[i]}</td>
      <td>${d.quantities[i]}</td>
    </tr>`;
    table.innerHTML += row;
  }
}

// Initialize chart
const ctx = document.getElementById('chart').getContext('2d');
const chart = new Chart(ctx,{
  type:'bar',
  data:{
    labels: [],
    datasets:[{
      label:'Quantity Ordered',
      data:[],
      backgroundColor:'rgba(27,94,32,0.7)'
    }]
  },
  options:{scales:{y:{beginAtZero:true}}}
});

// Refresh every 5 seconds
setInterval(refreshDashboard,5000);
refreshDashboard();
</script>
</body>
</html>
"""

# -----------------------------
# Dashboard data API
# -----------------------------
@app.route("/dashboard_data")
def dashboard_data():
    labels = []
    buyers = []
    products = []
    quantities = []
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE) as f:
            next(f)  # skip header
            for line in f:
                t,b,p,q = line.strip().split(",")
                labels.append(t)
                buyers.append(b)
                products.append(p)
                quantities.append(int(q))
    return jsonify({
        "labels": labels,
        "buyers": buyers,
        "products": products,
        "quantities": quantities
    })

# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return "OK"

if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
