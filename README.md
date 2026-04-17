# 🏟️ Smart Stadium OS (v2.1.0)
### Enterprise-Grade Crowd Intelligence & Neural Pathfinding

Smart Stadium OS is a production-ready Digital Twin system designed to manage large-scale crowd dynamics in real-time. By combining high-frequency telemetry with time-series forecasting and AI-enhanced graph routing, the system ensures visitor safety and operational efficiency during high-capacity events.

---

## 🏗️ System Architecture

```text
[ Digital Twin Frontend ] <--- (WS: AI_STATE_TICK) --- [ FastAPI Neural Core ]
      (React + Vite)                                       (Python 3.11)
            |                                                    |
            +------------ (HTTP: /route) ------------------------+
            |                                                    |
            +------------ (HTTP: /alert) ------------------------+
                                                                 |
    [ Google Cloud Platform ] <----------------------------------+
    (Cloud Run + Logging)
```

### Key Components:
- **Neural Core**: Multi-threaded simulation engine for crowd dynamics.
- **A* Intelligence**: Weighted graph traversal factoring in future congestion.
- **Digital Twin UI**: Glass-morphic operational radar with ARIA accessibility.
- **Safety Layer**: Real-time anomaly detection and emergency broadcast.

---

## 🧠 AI Capabilities

### 1. Multi-Step Forecasting (Prophet-style)
The system uses a weighted rolling window algorithm (LSTM-inspired) to project crowd density 10 minutes into the future. It factors in:
- **Seasonality**: Time-of-day crowd scale bias.
- **Flow Momentum**: Instantaneous net inflow/outflow velocity.
- **History**: EMA-smoothed historical density buffers.

### 2. Anomaly Detection
Every operational tick executes a **Z-Score statistical audit** on all nodes. Sudden spikes (Z > 2.5) trigger immediate `CRITICAL` alerts and automated staff dispatch recommendations.

### 3. Neural A* Routing
Unlike standard navigation, our router uses a **dynamic penalty cost function**:
`Cost = Distance + (Current_Density × 0.6) + (Predicted_Density × 0.4) + Risk_Tier_Penalty`
This ensures visitors are routed away from zones *before* they become congested.

---

## 🛠️ Tech Stack & Integration

- **Backend**: FastAPI, Pydantic v2, Uvicorn, NumPy/Statistics.
- **Frontend**: React 18, Tailwind-grade custom CSS, Lucide Icons.
- **GCP**: Cloud Run (Autoscaling), Cloud Logging & Monitoring.
- **Testing**: Pytest (8+ high-coverage test cases).

---

## 🚀 Deployment & Local Setup

### 1. Local Development
```bash
# Backend Setup
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8080 --reload

# Frontend Setup
cd frontend
npm install
npm run dev
```

### 2. Production Build (Standard)
```bash
# Build frontend
cd frontend && npm run build
# Move artifacts
mv dist ../backend/static
```

### 3. One-Command Cloud Deploy
```bash
gcloud run deploy smart-stadium-system --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --project smart-stadium-system
```

---

## 🛡️ Security & Enterprise Standards
- **Rate Limiting**: Sliding-window middleware prevents API exhaustion.
- **Validation**: Strict Pydantic schemas for all user-facing inputs.
- **Observability**: Integrated Cloud Logging with operational tracing.
- **Accessibility**: Full ARIA support for high-contrast radar operations.

---

**Developed for the Global Hackathon | Enterprise Track**
*Solving the challenges of urban crowd management through Real-Time AI.*
