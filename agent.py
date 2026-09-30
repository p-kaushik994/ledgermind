import os
import json
from dotenv import load_dotenv
from hindsight_service import hindsight_service

load_dotenv()


class LedgerMindAgent:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.client = None

        if self.groq_api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"[Groq Init Error] {e}")

    def evaluate_invoice(self, invoice, use_memory=True):
        """
        Evaluates an invoice with or without Hindsight memory context.
        Returns clean, simple, human-readable explanations.
        """
        vendor = invoice.get("vendor_name", "Unknown")
        po_amt = invoice.get("po_amount", 0.0)
        inv_amt = invoice.get("invoice_amount", 0.0)
        disc_amt = invoice.get("discrepancy_amount", 0.0)
        disc_type = invoice.get("discrepancy_type", "None")

        # Case 0: Exact Match (No Discrepancy)
        if disc_amt <= 0.0 or disc_type.lower() == "none":
            return {
                "decision": "MATCHED",
                "status_badge": "Verified Match",
                "confidence": 1.0,
                "summary": "Everything matches the Purchase Order 100%.",
                "reasoning": f"Billed ₹{inv_amt:,.2f} matches PO ₹{po_amt:,.2f} exactly. No extra fees.",
                "memory_recalled": None,
                "used_memory": use_memory
            }

        # Case 1: Evaluated WITHOUT MEMORY (The Stateless LLM baseline)
        if not use_memory:
            return {
                "decision": "FLAGGED",
                "status_badge": "Flagged (Amnesia)",
                "confidence": 0.50,
                "summary": f"Extra fee of ₹{disc_amt:,.2f} detected.",
                "reasoning": "I have no memory of past approvals. Because I cannot remember previous decisions, payment is frozen. A manager must manually review this again.",
                "memory_recalled": None,
                "used_memory": False
            }

        # Case 2: Evaluated WITH HINDSIGHT MEMORY
        recall_result = hindsight_service.recall_precedents(vendor, disc_type, inv_amt)

        # Sub-case A: Precedent FOUND in Hindsight
        if recall_result.get("matched"):
            mem = recall_result["memory"]
            approver = mem.get("approved_by", "Finance Lead")
            date_logged = mem.get("timestamp", "Recent")
            rule_text = mem.get("precedent_note", mem.get("rule", ""))

            return {
                "decision": "AUTO_APPROVED",
                "status_badge": "Auto-Approved",
                "confidence": recall_result.get("confidence", 0.95),
                "summary": f"Matches past approval by {approver}.",
                "reasoning": f"This extra ₹{disc_amt:,.2f} fee was already approved by {approver} for: '{rule_text}'. Payment is cleared automatically.",
                "memory_recalled": mem,
                "used_memory": True
            }

        # Sub-case B: Hostile Price Increase (Strict Reject)
        if "price increase" in disc_type.lower():
            return {
                "decision": "REJECTED_AUDIT",
                "status_badge": "Strict Reject",
                "confidence": 0.98,
                "summary": f"Unauthorized ₹{disc_amt:,.2f} price increase.",
                "reasoning": "The supplier raised unit prices without approval. No past rule allows price hikes. Escalated to procurement.",
                "memory_recalled": None,
                "used_memory": True
            }

        # Sub-case C: First-time Encounter (New exception requiring human precedent)
        return {
            "decision": "FLAGGED",
            "status_badge": "New Fee (Needs Precedent)",
            "confidence": 0.65,
            "summary": f"First time seeing {disc_type}.",
            "reasoning": "No past approval rule found for this vendor. Please review and save a rule to automate this in the future.",
            "memory_recalled": None,
            "used_memory": True
        }

agent = LedgerMindAgent()
