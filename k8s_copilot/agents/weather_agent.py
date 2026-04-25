"""
Weather Agent for A2A Architecture

GitHub Copilot SDKを使用して天気情報を提供するエージェント
"""

import asyncio
import json
import logging
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(title="Weather Agent")

# グローバルCopilotセッション
copilot_session = None

# リクエストモデル
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


# カスタムツール: get_weather
class WeatherParams(BaseModel):
    city: str = Field(description="City name (e.g., Tokyo, Paris, New York)")

@define_tool(description="Get current weather information for a city")
async def get_weather(params: WeatherParams) -> dict:
    """
    Get current weather information for a city.
    
    This is a mock implementation that returns simulated weather data.
    In production, this would call a real weather API.
    """
    city = params.city
    
    # モック天気データ
    mock_weather = {
        "Tokyo": {"temp": 18, "condition": "Cloudy"},
        "Paris": {"temp": 15, "condition": "Rainy"},
        "New York": {"temp": 12, "condition": "Sunny"},
        "London": {"temp": 10, "condition": "Foggy"},
        "Sydney": {"temp": 25, "condition": "Sunny"},
    }
    
    weather = mock_weather.get(city, {"temp": 20, "condition": "Unknown"})
    return {"city": city, "temperature": f"{weather['temp']}°C", "condition": weather['condition']}


async def initialize_copilot():
    """
    Copilotクライアントとセッションを初期化
    """
    global copilot_session
    
    logger.info("[Weather Agent] Initializing Copilot client...")
    
    try:
        client = CopilotClient()
        copilot_session = await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            streaming=False,
            tools=[get_weather],
        )
        logger.info("[Weather Agent] Copilot session created successfully")
    except Exception as e:
        logger.error(f"[Weather Agent] Failed to initialize Copilot: {e}")
        copilot_session = None


@app.on_event("startup")
async def startup_event():
    """
    起動時の初期化
    """
    await initialize_copilot()


@app.get("/")
async def root():
    """
    ルートエンドポイント
    """
    return {
        "name": "Weather Agent",
        "description": "Provides weather information for cities worldwide",
        "status": "ready" if copilot_session else "initializing"
    }


@app.get("/.well-known/agent-card.json")
async def agent_card():
    """
    Agent Cardを返す（エージェント検出用）
    """
    return {
        "name": "Weather Agent",
        "description": "Provides weather information for cities worldwide",
        "version": "1.0.0",
        "capabilities": {
            "extensions": [
                {
                    "name": "weather",
                    "description": "Get weather information for cities"
                }
            ]
        },
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "parameters": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., Tokyo, Paris, New York)"
                    }
                }
            }
        ]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    メッセージを受信してCopilotで処理
    """
    if not copilot_session:
        return ChatResponse(response="Error: Copilot session not initialized")
    
    message = request.message
    logger.info(f"[Weather Agent] Received message: {message}")
    
    try:
        # Copilotにメッセージを送信してレスポンスを取得
        response = await copilot_session.send_and_wait(message)
        
        # SessionEventオブジェクトからcontentを取得
        if hasattr(response, 'data') and hasattr(response.data, 'content'):
            response_text = response.data.content
        elif hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        logger.info(f"[Weather Agent] Response: {response_text[:100]}...")
        return ChatResponse(response=response_text)
    
    except Exception as e:
        logger.error(f"[Weather Agent] Error processing message: {e}")
        return ChatResponse(response=f"Error: {str(e)}")


@app.get("/healthz")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {
        "status": "healthy" if copilot_session else "unhealthy",
        "tools": ["get_weather"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
