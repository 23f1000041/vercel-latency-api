from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data (list of records)
with open("q-vercel-latency.json") as f:
    telemetry = json.load(f)

@app.post("/api/latency")
def latency_metrics(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    response = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]

        # Handle uptime field safely
        if "uptime" in records[0]:
            uptimes = [r["uptime"] for r in records]
        elif "is_up" in records[0]:
            uptimes = [1 if r["is_up"] else 0 for r in records]
        elif "up" in records[0]:
            uptimes = [r["up"] for r in records]
        else:
            uptimes = [1 for _ in records]  # fallback (assume up)

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies),
        }

    return response

