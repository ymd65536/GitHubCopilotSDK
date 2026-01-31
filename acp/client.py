import asyncio
import logging
from acp import (
    PROTOCOL_VERSION,
    Client,
    connect_to_agent,
    text_block,
)
from acp.schema import (
    ClientCapabilities,
    Implementation,
    AgentMessageChunk,
    TextContentBlock,
)

# ログ設定（通信内容が見えるように INFO に設定）
logging.basicConfig(level=logging.INFO)

class MyClient(Client):
    """サーバーからの通知を綺麗に表示するハンドラ"""
    
    async def session_update(self, session_id, update, **kwargs):
        # サーバーからのメッセージの断片を受け取った場合
        if isinstance(update, AgentMessageChunk):
            content = update.content
            if isinstance(content, TextContentBlock):
                # end="" で改行を抑制し、リアルタイムに表示
                print(content.text, end="", flush=True)
        
        # 思考プロセス（Thought）なども流れてくる場合があります
        elif isinstance(update, AgentThoughtChunk):
            # 思考中は少し薄く表示するなど工夫もできます
            pass

async def main():
    # Dockerで公開しているIPとポート
    HOST = 'localhost'
    PORT = 4321

    print(f"Connecting to ACP server at {HOST}:{PORT}...")
    
    try:
        # 1. TCP接続を確立
        reader, writer = await asyncio.open_connection(HOST, PORT)
        
        # 2. SDKの接続管理クラスを作成
        client_impl = MyClient()
        # connect_to_agent は内部で ClientSideConnection を生成します
        conn = connect_to_agent(client_impl, writer, reader)

        # 3. プロトコルの初期化 (initialize)
        print("Initializing...")
        await conn.initialize(
            protocol_version=PROTOCOL_VERSION,
            client_capabilities=ClientCapabilities(),
            client_info=Implementation(
                name="my-custom-client", 
                version="0.1.0"
            ),
        )

        # 4. セッションの作成 (new_session)
        print("Creating session...")
        # Copilot CLI の場合、mcp_servers は空でも動くことが多いです
        session = await conn.new_session(mcp_servers=[], cwd="/")
        session_id = session.session_id
        print(f"Session created: {session_id}")

        # 5. 質問の送信 (prompt)
        user_input = "PythonでHello Worldを書くコードを教えて"
        print(f"\nUser: {user_input}")
        
        await conn.prompt(
            session_id=session_id,
            prompt=[text_block(user_input)],
        )
        
        print("\n\nDone.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'writer' in locals():
            writer.close()
            await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
