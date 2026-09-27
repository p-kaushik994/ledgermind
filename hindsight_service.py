import os
import json
import uuid
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "memory_bank.json")

class HindsightService:
    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
        self.api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io/v1").rstrip("/")
        self.mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true" or not self.api_key
        self._ensure_memory_file()

    def _ensure_memory_file(self):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def _load_local_memories(self):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_local_memories(self, memories):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2)

    def retain_precedent(self, vendor_name, invoice_id, discrepancy_type, discrepancy_amount, precedent_note, approved_by="Human Finance Lead"):
        """
        Retains an approved human exception as an institutional memory in Hindsight.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        memory_id = f"MEM-{str(uuid.uuid4())[:8].upper()}"

        memory_payload = {
            "id": memory_id,
            "vendor_name": vendor_name,
            "invoice_id": invoice_id,
            "discrepancy_type": discrepancy_type,
            "discrepancy_amount": discrepancy_amount,
            "precedent_note": precedent_note,
            "approved_by": approved_by,
            "timestamp": timestamp,
            "rule": f"{vendor_name}: Exception authorized for '{discrepancy_type}' up to ₹{discrepancy_amount:,.2f}. Justification: {precedent_note}",
            "type": "EXPERIENCE_AND_MENTAL_MODEL"
        }

        # Try Live Hindsight API if not in pure mock mode
        if not self.mock_mode and self.api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                hindsight_body = {
                    "document": f"Vendor: {vendor_name}. Precedent: Approved exception for {discrepancy_type} amounting to ₹{discrepancy_amount:,.2f}. Reason: {precedent_note}. Approved by: {approved_by}.",
                    "metadata": {
                        "vendor_name": vendor_name,
                        "discrepancy_type": discrepancy_type,
                        "invoice_id": invoice_id,
                        "approved_by": approved_by
                    }
                }
                res = requests.post(f"{self.api_url}/memories", headers=headers, json=hindsight_body, timeout=5)
                if res.status_code in [200, 201]:
                    print(f"[Hindsight Live] Successfully retained memory: {memory_id}")
            except Exception as e:
                print(f"[Hindsight Live Error] Falling back to local retention: {e}")

        # Always persist locally for transparent UI inspection and offline resilience
        memories = self._load_local_memories()
        memories.insert(0, memory_payload)
        self._save_local_memories(memories)
        return memory_payload

    def recall_precedents(self, vendor_name, discrepancy_type, invoice_amount=None):
        """
        Recalls matching institutional precedents from Hindsight for a given vendor and discrepancy.
        """
        # If live Hindsight is active, attempt semantic search
        if not self.mock_mode and self.api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                query_body = {
                    "query": f"Precedents, exceptions, and approval rules for {vendor_name} regarding {discrepancy_type}.",
                    "top_k": 3
                }
                res = requests.post(f"{self.api_url}/memories/search", headers=headers, json=query_body, timeout=5)
                if res.status_code == 200:
                    api_data = res.json()
                    if api_data.get("results"):
                        top_hit = api_data["results"][0]
                        return {
                            "matched": True,
                            "confidence": 0.94,
                            "source": "Hindsight Cloud API",
                            "memory": {
                                "id": top_hit.get("id", "HINDSIGHT-LIVE"),
                                "rule": top_hit.get("content") or top_hit.get("document"),
                                "approved_by": top_hit.get("metadata", {}).get("approved_by", "Authorized Approver"),
                                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                        }
            except Exception as e:
                print(f"[Hindsight Recall Error] Falling back to local engine: {e}")

        # Local Biomimetic Recall Engine
        memories = self._load_local_memories()
        vendor_clean = vendor_name.lower().strip()
        type_clean = discrepancy_type.lower().strip()

        matched_memory = None
        for mem in memories:
            mem_vendor = mem.get("vendor_name", "").lower().strip()
            mem_type = mem.get("discrepancy_type", "").lower().strip()

            # Exact vendor + discrepancy match
            if mem_vendor == vendor_clean and (mem_type == type_clean or type_clean in mem_type):
                matched_memory = mem
                break

        if matched_memory:
            return {
                "matched": True,
                "confidence": 0.96,
                "source": "Hindsight Memory Engine",
                "memory": matched_memory
            }

        return {
            "matched": False,
            "confidence": 0.0,
            "source": "Hindsight Memory Engine",
            "memory": None
        }

    def get_all_memories(self):
        return self._load_local_memories()

    def reset_memories(self):
        self._save_local_memories([])
        return True

hindsight_service = HindsightService()
