"""
Trading Agent Dashboard - FastAPI Server
Connects your existing agents to a web interface
"""

from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# Initialize Your Agents
# ========================================

def init_agents():
    """Load your existing agents"""
    try:
        from trading_system.agents.technical_agent import TechnicalAnalysisAgent
        from trading_system.agents.whale_agent import WhaleIntelligenceAgent
        from trading_system.agents.macro_agent import MacroIntelligenceAgent
        from trading_system.agents.news_agent import NewsSentimentAgent
        
        return {
            "technical": TechnicalAnalysisAgent(),
            "whale": WhaleIntelligenceAgent(),
            "macro": MacroIntelligenceAgent(),
            "news": None,  # Add when ready
        }
    except ImportError as e:
        logger.warning(f"Could not load all agents: {e}")
        return {}

AGENTS = init_agents()

# ========================================
# WebSocket Manager
# ========================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket connected ({len(self.active_connections)} total)")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# ========================================
# Request Models
# ========================================

class AnalyzeRequest(BaseModel):
    symbol: str = "BTC-USD"
    timeframe: str = "1d"

class WhaleRequest(BaseModel):
    coin: str = "BTC"

# ========================================
# FastAPI App
# ========================================

app = FastAPI(
    title="Trading Agent Dashboard",
    version="1.0.0",
    description="Web dashboard for your multi-agent trading system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading Agent Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "✅ Healthy",
        "agents_loaded": len(AGENTS),
        "agent_names": list(AGENTS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/analyze")
async def analyze_symbol(request: AnalyzeRequest):
    """Analyze a symbol using Technical Agent"""
    try:
        if AGENTS.get("technical"):
            result = await AGENTS["technical"].run(
                symbol=request.symbol,
                timeframe=request.timeframe
            )
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Technical agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whale/{coin}")
async def whale_activity(coin: str = "BTC"):
    """Get whale activity for a coin"""
    try:
        if AGENTS.get("whale"):
            result = await AGENTS["whale"].run(coin=coin)
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Whale agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Whale error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/macro")
async def macro_data():
    """Get macro indicators"""
    try:
        if AGENTS.get("macro"):
            result = await AGENTS["macro"].run()
            return {"status": "success", "data": result}
        return {"status": "success", "message": "Macro agent not loaded", "data": {}}
    except Exception as e:
        logger.error(f"Macro error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# WebSocket
# ========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ========================================
# Startup
# ========================================

@app.on_event("startup")
async def startup():
    logger.info("🚀 Trading Dashboard API started!")
    logger.info(f"📊 Agents loaded: {list(AGENTS.keys())}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Trading Dashboard API stopped!")
