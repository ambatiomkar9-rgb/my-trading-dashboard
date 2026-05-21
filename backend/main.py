import os
import json
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Trading Dashboard API")

# Allow CORS for all origins (agents can reach from anywhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store agent states in memory
agent_states = {}
connected_clients = []

# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health():
    """Check if dashboard is online"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ==================== AGENT STATUS ====================
@app.post("/agent-status")
async def update_agent_status(data: dict):
    """
    Agents POST their status here
    Example:
    {
        "agent_id": "analysis_agent",
        "status": "processing",
        "task": "Analyzing INFY 4h",
        "progress": 75,
        "skills": ["technical_analysis"],
        "cpu": 32,
        "memory_mb": 450,
        "timestamp": "2024-12-19T14:30:00Z"
    }
    """
    agent_id = data.get("agent_id")
    
    # Store in memory
    agent_states[agent_id] = data
    
    # Broadcast to connected WebSocket clients
    await broadcast_agent_update(data)
    
    return {"status": "ok", "message": f"Status received for {agent_id}"}

# ==================== WEBSOCKET FOR LIVE UPDATES ====================
@app.websocket("/ws/agent-monitor")
async def websocket_endpoint(websocket: WebSocket):
    """
    Frontend connects here to get live agent updates
    Receives agent state updates every time agents POST
    """
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json(agent_states)
        
        # Keep connection alive
        while True:
            # Wait for any message (client keeps connection open)
            data = await websocket.receive_text()
            # Echo back or handle commands
            await websocket.send_json({"ack": True})
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(websocket)

async def broadcast_agent_update(data):
    """Send agent update to all connected WebSocket clients"""
    for client in connected_clients:
        try:
            await client.send_json(data)
        except Exception as e:
            print(f"Broadcast error: {e}")

# ==================== CHAT ENDPOINT ====================
@app.post("/chat")
async def chat(message: dict):
    """
    Receive chat message from frontend
    Delegate to boss agent (running locally)
    Return response
    """
    user_message = message.get("message", "")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message required")
    
    # TODO: Call your boss agent here
    # For now, return mock response
    
    response = {
        "response": f"I received: {user_message}. Boss agent will process this.",
        "timestamp": datetime.now().isoformat(),
        "agent": "boss_agent"
    }
    
    return response

# ==================== BACKTEST ENDPOINT ====================
@app.post("/backtest")
async def run_backtest(data: dict):
    """
    Run backtest and return results
    {
        "strategy": "rsi_oversold",
        "symbol": "INFY",
        "timeframe": "4h",
        "date_from": "2024-01-01",
        "date_to": "2024-12-31"
    }
    """
    strategy = data.get("strategy")
    symbol = data.get("symbol")
    
    # TODO: Call strategy agent backtest skill
    
    results = {
        "strategy": strategy,
        "symbol": symbol,
        "total_trades": 45,
        "win_rate": 72,
        "pnl": 25000,
        "sharpe": 1.87,
        "max_dd": -8.5,
        "profit_factor": 2.3,
        "status": "complete",
        "csv_file": f"backtest_{symbol}_{strategy}.csv"
    }
    
    return results

# ==================== TRADE ENDPOINT ====================
@app.post("/trade")
async def place_trade(data: dict):
    """
    Place order
    {
        "symbol": "INFY",
        "quantity": 100,
        "price": 1955,
        "stop_loss": 1920,
        "take_profit": 1985,
        "mode": "paper"
    }
    """
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    mode = data.get("mode", "paper")
    
    # TODO: Call execution agent
    
    return {
        "status": "success",
        "order_id": "12345",
        "symbol": symbol,
        "quantity": quantity,
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }

# ==================== GET STRATEGIES ====================
@app.get("/strategies")
async def get_strategies():
    """Get list of active strategies"""
    # TODO: Query from database
    
    strategies = [
        {
            "id": "rsi_oversold",
            "name": "RSI Oversold",
            "symbol": "INFY",
            "timeframe": "4h",
            "status": "running",
            "pnl": 8000,
            "win_rate": 72,
            "created_date": "2024-12-15"
        }
    ]
    
    return strategies

# ==================== SERVE FRONTEND ====================
# Get the absolute path to the frontend dist folder
BASE_DIR = Path(__file__).parent.parent
frontend_path = BASE_DIR / "frontend" / "dist"

print(f"📁 Looking for frontend at: {frontend_path}")
print(f"📁 Frontend exists: {frontend_path.exists()}")

if frontend_path.exists():
    print(f"✅ Frontend dist folder found! Serving from: {frontend_path}")
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
else:
    print(f"⚠️ Frontend dist folder not found at {frontend_path}")
    print(f"⚠️ Contents of {BASE_DIR}:")
    try:
        for item in BASE_DIR.iterdir():
            print(f"  - {item.name}")
    except:
        pass
    
    # Fallback: serve a message
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return {"detail": "Frontend not built yet", "path": str(frontend_path), "exists": frontend_path.exists()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
