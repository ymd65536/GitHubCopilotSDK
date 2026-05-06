"""
Calculator Agent for A2A Architecture

GitHub Copilot SDKを使用して計算機能を提供するエージェント
"""

import asyncio
import json
import logging
import os
import re
from typing import Optional

from opentelemetry import metrics as otel_metrics
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, Field
from starlette.responses import Response

from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_telemetry(service_name: str) -> None:
    """OTEL_EXPORTER_OTLP_ENDPOINT が設定されている場合、Aspire Dashboard へトレースとメトリクスを送信する。"""
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp_endpoint:
        logger.info(f"[{service_name}] OTEL_EXPORTER_OTLP_ENDPOINT not set, skipping telemetry setup")
        return

    resource = Resource(attributes={"service.name": service_name})

    # Traces (.NET の .WithTracing(...).AddOtlpExporter() 相当)
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # Metrics (.NET の .WithMetrics(...).AddOtlpExporter() 相当)
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    prometheus_reader = PrometheusMetricReader()
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader, prometheus_reader])
    otel_metrics.set_meter_provider(meter_provider)

    logger.info(f"[{service_name}] OpenTelemetry configured: {otlp_endpoint}")


# FastAPIアプリケーション
app = FastAPI(title="Calculator Agent")
setup_telemetry("Calculator Agent")
FastAPIInstrumentor.instrument_app(app)

# グローバルCopilotセッション
copilot_session = None

# リクエストモデル
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


# カスタムツール: calculate
class CalculateParams(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '15 * 23 + 100')")

@define_tool(description="Calculate a mathematical expression")
async def calculate(params: CalculateParams) -> dict:
    """
    Calculate a mathematical expression.
    
    Supports basic arithmetic operations: +, -, *, /, **, (), etc.
    """
    expression = params.expression
    
    try:
        # セキュリティのため、安全な文字のみを許可
        if not re.match(r'^[\d\s\+\-\*\/\(\)\.\*\*]+$', expression):
            return {"error": f"Invalid characters in expression: {expression}"}
        
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": f"Error calculating '{expression}': {str(e)}"}


# カスタムツール: convert_currency
class CurrencyConvertParams(BaseModel):
    amount: float = Field(description="Amount to convert")
    from_currency: str = Field(description="Source currency code (e.g., USD, JPY, EUR)")
    to_currency: str = Field(description="Target currency code (e.g., USD, JPY, EUR)")

@define_tool(description="Convert currency from one type to another")
async def convert_currency(params: CurrencyConvertParams) -> dict:
    """
    Convert currency from one type to another.
    
    This is a mock implementation with hardcoded exchange rates.
    In production, this would call a real currency API.
    """
    amount = params.amount
    from_currency = params.from_currency
    to_currency = params.to_currency
    
    # モック為替レート (対USD)
    rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "JPY": 110.0,
        "GBP": 0.73,
        "AUD": 1.35,
    }
    
    if from_currency not in rates or to_currency not in rates:
        return {
            "error": f"Unsupported currency. Supported: {', '.join(rates.keys())}"
        }
    
    # USD経由で換算
    usd_amount = amount / rates[from_currency]
    result = usd_amount * rates[to_currency]
    
    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "result": round(result, 2)
    }


async def initialize_copilot():
    """
    Copilotクライアントとセッションを初期化
    """
    global copilot_session
    
    logger.info("[Calculator Agent] Initializing Copilot client...")
    
    try:
        client = CopilotClient()
        copilot_session = await client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            streaming=False,
            tools=[calculate, convert_currency],
        )
        logger.info("[Calculator Agent] Copilot session created successfully")
    except Exception as e:
        logger.error(f"[Calculator Agent] Failed to initialize Copilot: {e}")
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
        "name": "Calculator Agent",
        "description": "Provides calculation and currency conversion capabilities",
        "status": "ready" if copilot_session else "initializing"
    }


@app.get("/.well-known/agent-card.json")
async def agent_card():
    """
    Agent Cardを返す（エージェント検出用）
    """
    return {
        "name": "Calculator Agent",
        "description": "Provides calculation and currency conversion capabilities",
        "version": "1.0.0",
        "capabilities": {
            "extensions": [
                {
                    "name": "calculator",
                    "description": "Perform calculations and currency conversions"
                }
            ]
        },
        "tools": [
            {
                "name": "calculate",
                "description": "Calculate a mathematical expression",
                "parameters": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression (e.g., '15 * 23 + 100')"
                    }
                }
            },
            {
                "name": "convert_currency",
                "description": "Convert currency from one type to another",
                "parameters": {
                    "amount": {
                        "type": "number",
                        "description": "Amount to convert"
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency code (USD, EUR, JPY, GBP, AUD)"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency code (USD, EUR, JPY, GBP, AUD)"
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
    logger.info(f"[Calculator Agent] Received message: {message}")
    
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
        
        logger.info(f"[Calculator Agent] Response: {response_text[:100]}...")
        return ChatResponse(response=response_text)
    
    except Exception as e:
        logger.error(f"[Calculator Agent] Error processing message: {e}")
        return ChatResponse(response=f"Error: {str(e)}")


@app.get("/metrics")
async def metrics():
    """
    Prometheusメトリクスエンドポイント
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {
        "status": "healthy" if copilot_session else "unhealthy",
        "tools": ["calculate", "convert_currency"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
