"""
A2A Dispatcher for GitHub Copilot Agents

このDispatcherは、Kubernetes上の複数のCopilotエージェントを自動検出し、
クライアントからのリクエストを適切なエージェントにルーティングします。

機能:
- Kubernetes Pod Watchによる自動エージェント検出
- Agent Cardに基づく能力ベースルーティング
- ローカル開発用の静的エージェントリスト対応
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(title="A2A Copilot Dispatcher")

# エージェント情報
@dataclass
class AgentInfo:
    endpoint: str
    name: str
    description: str
    capabilities: List[str]
    tools: List[Dict]

# グローバルエージェントレジストリ
agent_registry: Dict[str, AgentInfo] = {}

# リクエストモデル
class AgentRequest(BaseModel):
    capability: str
    message: str

class AgentResponse(BaseModel):
    agent: str
    endpoint: str
    response: str


async def fetch_agent_card(base_url: str) -> Optional[Dict]:
    """
    エージェントのAgent Cardを取得
    """
    url = f"{base_url}/.well-known/agent-card.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.warning(f"Failed to fetch agent card from {url}: {resp.status}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching agent card from {url}: {e}")
        return None


async def register_agent(base_url: str):
    """
    エージェントを登録
    """
    logger.info(f"[Discovery] Trying to register agent: {base_url}")
    
    card = await fetch_agent_card(base_url)
    if not card:
        logger.warning(f"[Discovery] Failed to get agent card from {base_url}")
        return
    
    name = card.get("name", "Unknown Agent")
    description = card.get("description", "")
    
    # 能力を抽出
    capabilities = []
    if "capabilities" in card and "extensions" in card["capabilities"]:
        for ext in card["capabilities"]["extensions"]:
            capabilities.append(ext.get("name", ""))
    
    # 能力がない場合はエージェント名を能力として使用
    if not capabilities:
        capabilities = [name]
    
    # ツールを抽出
    tools = card.get("tools", [])
    
    # エージェント情報を作成
    agent_info = AgentInfo(
        endpoint=base_url,
        name=name,
        description=description,
        capabilities=capabilities,
        tools=tools
    )
    
    # 各能力に対してエージェントを登録
    for cap in capabilities:
        agent_registry[cap] = agent_info
        logger.info(f"[Discovery] Registered agent '{name}' with capability '{cap}' at {base_url}")


async def discover_kubernetes_agents():
    """
    Kubernetes上のエージェントを検出（app=a2a-agent ラベル）
    
    実際の実装では kubernetes-python ライブラリを使用しますが、
    ここでは簡略化のためスタブとして実装
    """
    namespace = os.getenv("KUBERNETES_NAMESPACE", "a2a-copilot")
    logger.info(f"[Discovery] Kubernetes discovery not yet implemented for namespace: {namespace}")
    logger.info(f"[Discovery] Use static agent list from AGENT_ENDPOINTS environment variable")


async def load_static_agents():
    """
    環境変数から静的エージェントリストを読み込む
    
    AGENT_ENDPOINTS="http://weather-agent:8001,http://calculator-agent:8002"
    """
    endpoints = os.getenv("AGENT_ENDPOINTS", "")
    if not endpoints:
        logger.warning("[Discovery] No static agents configured in AGENT_ENDPOINTS")
        return
    
    for endpoint in endpoints.split(","):
        endpoint = endpoint.strip()
        if endpoint:
            await register_agent(endpoint)


async def send_to_agent(agent_endpoint: str, message: str) -> str:
    """
    エージェントにメッセージを送信
    """
    url = f"{agent_endpoint}/chat"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json={"message": message},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "No response")
                else:
                    error_text = await resp.text()
                    return f"Error: {resp.status} - {error_text}"
    except Exception as e:
        logger.error(f"Error sending to agent {agent_endpoint}: {e}")
        return f"Error communicating with agent: {str(e)}"


@app.on_event("startup")
async def startup_event():
    """
    起動時の初期化
    """
    logger.info("[Dispatcher] Starting up...")
    
    # 静的エージェントを読み込み
    await load_static_agents()
    
    # Kubernetes検出（将来の実装）
    # await discover_kubernetes_agents()
    
    logger.info(f"[Dispatcher] Registered {len(agent_registry)} agent capabilities")


@app.get("/")
async def root():
    """
    ルートエンドポイント
    """
    return {
        "service": "A2A Copilot Dispatcher",
        "version": "1.0.0",
        "agents": len(agent_registry)
    }


@app.get("/agents")
async def list_agents():
    """
    登録済みエージェントの一覧を返す
    """
    agents_list = []
    seen_endpoints = set()
    
    for cap, agent in agent_registry.items():
        if agent.endpoint not in seen_endpoints:
            agents_list.append({
                "endpoint": agent.endpoint,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tools": agent.tools
            })
            seen_endpoints.add(agent.endpoint)
    
    return agents_list


@app.post("/ask", response_model=AgentResponse)
async def ask_agent(request: AgentRequest):
    """
    能力に基づいてエージェントにリクエストを送信
    """
    capability = request.capability
    message = request.message
    
    # 能力を持つエージェントを検索
    if capability not in agent_registry:
        # 登録済みエージェントの情報を含めてエラーを返す
        available = [
            {"name": agent.name, "capabilities": agent.capabilities}
            for agent in set(agent_registry.values())
        ]
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"No agent found with capability '{capability}'",
                "registered_agents": available
            }
        )
    
    agent = agent_registry[capability]
    logger.info(f"[Request] Routing to {agent.name} at {agent.endpoint} for capability '{capability}'")
    
    # エージェントにリクエストを送信
    response_text = await send_to_agent(agent.endpoint, message)
    
    return AgentResponse(
        agent=agent.name,
        endpoint=agent.endpoint,
        response=response_text
    )


@app.get("/healthz")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "healthy", "agents": len(agent_registry)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
