# copilot --server --port 4321 を立ち上げてから実行すること
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient({
        "cli_url": "localhost:4321"
    })
    await client.start()

    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})

    print(response.data.content)

    await client.stop()

asyncio.run(main())
