import os
import json
import copy
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from hindsight_service import hindsight_service
from agent import agent

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "invoices.json")
BACKUP_FILE = os.path.join(os.path.dirname(__file__), "data", "invoices_seed.json")

def load_invoices():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_invoices(invoices):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(invoices, f, indent=2)

# Create a backup seed on startup if not already created
if not os.path.exists(BACKUP_FILE) and os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        seed_data = json.load(f)
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/invoices", methods=["GET"])
def get_invoices():
    invoices = load_invoices()
    return jsonify({"success": True, "invoices": invoices})

@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    data = request.json or {}
    invoice_id = data.get("invoice_id")
    use_memory = data.get("use_memory", True)

    invoices = load_invoices()
    target_invoice = None
    for inv in invoices:
        if inv["id"] == invoice_id:
            target_invoice = inv
            break

    if not target_invoice:
        return jsonify({"success": False, "error": "Invoice not found"}), 404

    # Run evaluation
    eval_result = agent.evaluate_invoice(target_invoice, use_memory=use_memory)

    # Update invoice state if decision made
    if eval_result["decision"] == "AUTO_APPROVED":
        target_invoice["status"] = "AUTO_APPROVED"
        target_invoice["evaluation"] = eval_result
        save_invoices(invoices)
    elif eval_result["decision"] == "MATCHED":
        target_invoice["status"] = "MATCHED"
        target_invoice["evaluation"] = eval_result
        save_invoices(invoices)
    else:
        target_invoice["evaluation"] = eval_result
        save_invoices(invoices)

    return jsonify({"success": True, "evaluation": eval_result, "invoice": target_invoice})

@app.route("/api/approve", methods=["POST"])
def approve_exception():
    data = request.json or {}
    invoice_id = data.get("invoice_id")
    precedent_note = data.get("precedent_note", "Approved under corporate discretion")
    approved_by = data.get("approved_by", "Sarah Jenkins (Finance Lead)")

    invoices = load_invoices()
    target_invoice = None
    for inv in invoices:
        if inv["id"] == invoice_id:
            target_invoice = inv
            break

    if not target_invoice:
        return jsonify({"success": False, "error": "Invoice not found"}), 404

    # Retain the human approval precedent in Hindsight
    memory_created = hindsight_service.retain_precedent(
        vendor_name=target_invoice["vendor_name"],
        invoice_id=invoice_id,
        discrepancy_type=target_invoice.get("discrepancy_type", "Standard Variance"),
        discrepancy_amount=target_invoice.get("discrepancy_amount", 0.0),
        precedent_note=precedent_note,
        approved_by=approved_by
    )


    
    # Update status to manually approved
    target_invoice["status"] = "MANUALLY_APPROVED"
    target_invoice["precedent_applied"] = memory_created
    save_invoices(invoices)

    return jsonify({
        "success": True,
        "message": f"Precedent permanently retained in Hindsight memory for {target_invoice['vendor_name']}.",
        "memory": memory_created,
        "invoice": target_invoice
    })

@app.route("/api/memories", methods=["GET"])
def get_memories():
    memories = hindsight_service.get_all_memories()
    return jsonify({"success": True, "memories": memories})



@app.route("/api/reset", methods=["POST"])
def reset_demo():
    """Resets memory bank and invoices to original state for clean demo rehearsals."""
    hindsight_service.reset_memories()
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            seed = json.load(f)
        save_invoices(seed)
    return jsonify({"success": True, "message": "Demo state reset to Day 0 successfully."})



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  LedgerMind: Accounts Payable Precedent Agent Running")
    print(f"  Dashboard: http://127.0.0.1:{port}")
    print(f"  Mode: {'MOCK MODE (Simulated)' if hindsight_service.mock_mode else 'LIVE CLOUD (Vectorize + Groq)'}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
