# LedgerMind — Autonomous FinOps Precedent Engine

> **Biomimetic Agent Memory for Accounts Payable & Vendor Discrepancy Resolution**  
> Powered by **Vectorize Hindsight** and **Groq**.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/backend-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Vectorize Hindsight](https://img.shields.io/badge/memory-Vectorize%20Hindsight-indigo.svg)](https://hindsight.vectorize.io/)
[![Groq](https://img.shields.io/badge/llm-Groq-orange.svg)](https://groq.com/)
[![Currency: INR](https://img.shields.io/badge/Currency-INR%20(%E2%82%B9)-emerald.svg)](https://en.wikipedia.org/wiki/Indian_rupee)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Executive Summary

In enterprise finance operations, up to **20% of supplier invoices** trigger discrepancy flags against Purchase Orders—due to emergency freight surcharges, statutory green cesses, or seasonal delivery adjustments. 

Traditional Enterprise Resource Planning (ERP) systems are rigidly binary: either an invoice matches 100%, or it is frozen. Accounts Payable (AP) specialists waste hours chasing managers over recurring exceptions that were already authorized weeks prior. Standard LLMs suffer from complete session amnesia, repeatedly asking the same questions and providing generic advice.

**LedgerMind** solves this institutional amnesia. Powered by **Vectorize Hindsight**, LedgerMind retains human managerial approval decisions as persistent business precedents. When recurring invoices arrive, the agent recalls past authorizations, evaluates policy boundaries, and auto-approves compliant discrepancies with full audit citations in seconds.

---

## 🧠 Biomimetic Memory Architecture (Vectorize Hindsight)

LedgerMind leverages Hindsight’s 3-layer biomimetic memory structure:

```
+-----------------------------------------------------------------------------------+
|                               HINDSIGHT MEMORY LAYERS                             |
+-----------------------------------------------------------------------------------+
| 1. WORLD FACTS       | Static vendor metadata, contract payment terms, PO rules.  |
|                      | e.g. "Acme Industrial is Net-30 vendor under PO-4401."     |
+----------------------+------------------------------------------------------------+
| 2. EXPERIENCES       | Episodic logs of human exception approvals.                |
|                      | e.g. "Sarah Jenkins approved ₹3,500 rush freight on Oct 12"|
+----------------------+------------------------------------------------------------+
| 3. MENTAL MODELS     | Synthesized business precedent policies.                   |
|                      | e.g. "Acme freight surcharges <₹4,000 permitted for Q3."   |
+-----------------------------------------------------------------------------------+
```

---

## ⚡ The 60-Second Demo Story: Before vs After

| Interaction Stage | Stateless Baseline (Without Memory) | LedgerMind (With Vectorize Hindsight) |
| :--- | :--- | :--- |
| **Invoice #1 (First Encounter)** | Flags ₹3,500 freight fee; requests human review. | Flags fee; Human approves: *"Authorized rush freight up to ₹4,000 for Q3 warehouse move."* |
| **Invoice #2 (Recurring Surcharge)** | **Amnesia:** Flags the exact same ₹3,500 fee again, freezing payment for another 48 hours. | **Auto-Approved (96% Confidence):** Recalls precedent set by Sarah Jenkins; releases payment instantly. |
| **Invoice #3 (Unauthorized Hike)** | Cannot distinguish between authorized exception and hostile pricing changes. | **Strict Intercept:** Rejects ₹12,000 unit price increase as a contract violation with zero precedent. |

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/your-username/ledgermind.git
cd ledgermind

python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Add your API keys (or leave `MOCK_MODE=true` to test locally with zero configuration):

```env
GROQ_API_KEY=your_groq_api_key_here
HINDSIGHT_API_KEY=your_hindsight_api_key_here
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io/v1
GROQ_MODEL=llama-3.3-70b-versatile
MOCK_MODE=false
PORT=5000
```

### 3. Run Verification Test Suite

Verify that the memory retention and recall loops work:

```bash
python test_flow.py
```

### 4. Launch the Web Application

```bash
python app.py
```

Open your browser and navigate to: **`http://localhost:5000`**

---

## 🛠️ REST API Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/invoices` | Retrieve all queued invoices with current lifecycle state. |
| `POST` | `/api/evaluate` | Evaluate an invoice (`use_memory: true/false`). |
| `POST` | `/api/approve` | Retain a human approval exception in Hindsight. |
| `GET` | `/api/memories` | Inspect all retained institutional memories. |
| `POST` | `/api/reset` | Reset demo state back to Day 0 for clean presentations. |

---

## 👥 Engineering & Research Squad

* **Lead Architect & AI Systems:** System design, Flask REST API, Hindsight biomimetic memory orchestration, Groq integration.
* **Frontend Lead:** FinOps responsive dashboard, Tailwind CSS components, memory inspection drawer.
* **Integration & QA:** Real-time state synchronization, end-to-end verification tests.
* **FinOps Research Lead:** Synthetic corporate dataset design, business exception scenarios.
* **Media & Documentation:** Technical whitepaper, video production, and architectural documentation.

---

## 📄 License

Distributed under the MIT License.
