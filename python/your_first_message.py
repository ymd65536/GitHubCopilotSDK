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
    question = "2 + 2はいくつだ？"
    response = await session.send_and_wait(prompt=question)
    answer = f"2 + 2 = {response.data.content}"

    print(question)
    print(answer)

    await client.stop()

asyncio.run(main())
