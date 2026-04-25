import asyncio
import os
import random
import sys
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

# 実行モード切り替え
# USE_K8S_SERVER=1 で環境変数を設定するとKubernetesサーバーへの接続を試みます
# （現在のSDKでは直接TCP接続に制限があるため、Pod内実行を推奨）
USE_K8S_SERVER = os.environ.get("USE_K8S_SERVER", "0") == "1"
COPILOT_CLI_URL = os.environ.get("COPILOT_CLI_URL", "localhost:4321")


class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    city = params.city
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": city, "temperature": f"{temp}°F", "condition": condition}

async def main():
    if USE_K8S_SERVER:
        print(f"⚠️  Kubernetes server mode is experimental")
        print(f"   Attempting to connect to {COPILOT_CLI_URL}...")
        print(f"   Note: Direct TCP connection may not work with current SDK.")
        print(f"   Recommended: Run this script inside the Kubernetes Pod using:")
        print(f"   kubectl exec -it <pod-name> -n copilot-sdk -- python /path/to/script.py\n")
    else:
        print("Starting local copilot client...")

    # ローカルCLIを起動（Kubernetes Pod内でも同じ方法を使用）
    client = CopilotClient()
    await client.start()

    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        streaming=True,
        tools=[get_weather],
    )

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()

    session.on(handle_event)

    print("🌤️  Weather Assistant (type 'exit' to quit)")
    print("   Try: 'What's the weather in Paris?' or 'Compare weather in NYC and LA'\n")

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            break

        if user_input.lower() == "exit":
            break

        sys.stdout.write("Assistant: ")
        await session.send_and_wait(user_input)
        print("\n")

    await client.stop()

asyncio.run(main())
