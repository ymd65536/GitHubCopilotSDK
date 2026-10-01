import asyncio
from copilot import CopilotClient
from copilot.session import PermissionHandler

async def main():
    client = CopilotClient()
    await client.start()

    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        model="gpt-5.4",
        streaming=True,
    )
    response = await session.send_and_wait(prompt="2 + 2はいくつだ？")
    print(response.data.content)

    await client.stop()

asyncio.run(main())
