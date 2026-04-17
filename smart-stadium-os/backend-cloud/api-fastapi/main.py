from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import redis.asyncio as redis
from typing import List, Dict
import datetime

app = FastAPI(title="Smart Stadium AI API", version="1.0.0")

# Redis configuration (in prod this points to ElastiCache / MemoryDB)
REDIS_HOST = "redis-stadium"
REDIS_PORT = 6379

class TelemetryData(BaseModel):
    camera_id: str
    zone_id: str
    occupancy: int
    timestamp: int

class AlertPayload(BaseModel):
    zone_id: str
    severity: str
    message: str

# Connect to Redis
async def get_redis():
    # Provide fallback for local testing without redis
    try:
        return await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    except Exception:
        print("WARNING: Redis not connected")
        return None

@app.post("/api/v1/telemetry")
async def ingest_edge_telemetry(data: TelemetryData):
    """ Edge nodes call this to update density and flow for a specific zone. """
    r = await get_redis()
    if r:
        # 1. Update current density cache
        await r.hset("stadium_density", data.zone_id, data.occupancy)
        
        # 2. Publish to Websocket cluster (Pub/Sub)
        update_str = f"{data.zone_id}:{data.occupancy}"
        await r.publish("zone_updates", update_str)
        
        # 3. Anomaly / Threshold Detection (Basic example)
        # If capacity > 500, broadcast a critical safety alert
        if data.occupancy > 500:
            await r.publish("system_alerts", f"CRITICAL|{data.zone_id}|Overcrowding detected: {data.occupancy}")
            
    return {"status": "success", "processed_at": datetime.datetime.utcnow().isoformat()}

@app.get("/api/v1/zones/density")
async def get_all_densities():
    """ Dashboard API to retrieve the entire current stadium density map. """
    r = await get_redis()
    if r:
        density_map = await r.hgetall("stadium_density")
        return {"stadium_density": density_map}
    return {"stadium_density": {"North_Concourse": 420, "Gate_C": 50, "Food_Hall": 1200}}

@app.get("/api/v1/routing/optimal")
async def get_optimal_route(start: str, destination: str):
    """
    AI Routing logic: uses current density metrics to calculate the path of least resistance.
    """
    # Pseudo-logic: query graph, weight edges by density.
    # We mock the response for the prototype.
    return {
        "start": start,
        "destination": destination,
        "recommended_route": [start, "Corridor_B", "Gate_A_Express", destination],
        "estimated_wait_time_minutes": 2,
        "reason": "Corridor_A heavily congested (1200 pax)."
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "stadium-api"}
