import os
import json
from hindsight_service import hindsight_service
from agent import agent

def run_test_suite():
    print("="*60)
    print("  LEDGERMIND VERIFICATION SUITE: HINDSIGHT MEMORY LOOP (INR ₹)")
    print("="*60)

    # Reset memories
    hindsight_service.reset_memories()

    # Load test invoices
    with open(os.path.join(os.path.dirname(__file__), "data", "invoices.json"), "r") as f:
        invoices = json.load(f)

    inv1 = invoices[0]  # Acme Industrial (₹3,500 freight)
    inv2 = invoices[1]  # Acme Industrial (₹3,500 freight - recurring)
    inv3 = invoices[2]  # NovaTech (₹12,000 unit price increase)

    print("\n[STEP 1] Testing Stateless Baseline (Without Memory) on Invoice 1...")
    res1_nomem = agent.evaluate_invoice(inv1, use_memory=False)
    print(f"Decision: {res1_nomem['decision']}")
    print(f"Reasoning: {res1_nomem['reasoning']}")
    assert res1_nomem["decision"] == "FLAGGED"
    print(">>> PASS: Stateless LLM flagged discrepancy due to amnesia.")

    print("\n[STEP 2] Simulating Human Approval & Retaining Precedent in Hindsight...")
    mem = hindsight_service.retain_precedent(
        vendor_name=inv1["vendor_name"],
        invoice_id=inv1["id"],
        discrepancy_type=inv1["discrepancy_type"],
        discrepancy_amount=inv1["discrepancy_amount"],
        precedent_note="Authorized expedited air-freight surcharge up to ₹4,000 during Q3 warehouse relocation project.",
        approved_by="Sarah Jenkins (Finance Lead)"
    )
    print(f"Memory Retained: ID={mem['id']}")
    print(f"Stored Rule: {mem['rule']}")
    assert len(hindsight_service.get_all_memories()) == 1
    print(">>> PASS: Hindsight memory successfully retained.")

    print("\n[STEP 3] Testing LedgerMind WITH Hindsight Memory on Invoice 2...")
    res2_mem = agent.evaluate_invoice(inv2, use_memory=True)
    print(f"Decision: {res2_mem['decision']}")
    print(f"Confidence: {res2_mem['confidence']*100}%")
    print(f"Summary: {res2_mem['summary']}")
    print(f"Cited Memory: {res2_mem['reasoning']}")
    assert res2_mem["decision"] == "AUTO_APPROVED"
    print(">>> PASS: LedgerMind successfully recalled precedent and AUTO-APPROVED Invoice 2!")

    print("\n[STEP 4] Testing Safety Guardrail on Unauthorized Price Increase (Invoice 3)...")
    res3_audit = agent.evaluate_invoice(inv3, use_memory=True)
    print(f"Decision: {res3_audit['decision']}")
    print(f"Reasoning: {res3_audit['reasoning']}")
    assert res3_audit["decision"] == "REJECTED_AUDIT"
    print(">>> PASS: Agent strictly rejected unauthorized price increase without precedent.")

    print("\n" + "="*60)
    print("  ALL VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("  Hindsight memory loop in INR (₹) is 100% operational.")
    print("="*60)

if __name__ == "__main__":
    run_test_suite()
