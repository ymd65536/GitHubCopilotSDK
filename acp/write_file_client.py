import os
import asyncio
from acp import Client, connect_to_agent, text_block, PROTOCOL_VERSION
from acp.exceptions import RequestError
from acp.schema import (
    WriteTextFileResponse, 
    AgentMessageChunk, 
    TextContentBlock,
    ClientCapabilities,
    FileSystemCapability,
    Implementation
)

class MyClient(Client):
    async def session_update(self, session_id, update, **kwargs):
        if isinstance(update, AgentMessageChunk):
            content = update.content
            if isinstance(content, TextContentBlock):
                print(content.text, end="", flush=True)

    async def write_text_file(self, content, path, session_id, **kwargs):
        print(f"\n\n[Request] AI wants to write to: {path}")
        loop = asyncio.get_running_loop()
        confirm = await loop.run_in_executor(None, lambda: input("Allow writing this file? (y/n): "))
        if confirm.lower() != 'y':
            raise Exception("User denied file write permission")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return WriteTextFileResponse()

    async def ext_method(self, method: str, params: dict) -> dict:
        """
        SDKで明示的に定義されていないメソッド（エージェント独自のコマンド）を処理する
        """
        # エージェントが 'create' という名前で送ってきた場合
        if method == "create" or "write" in method:
            print(f"\n[Hooked Custom Tool] Method: {method}, Params: {params}")
            
            # 引数からパスと内容を抽出（エージェントによってキー名が異なる場合があります）
            path = params.get("path") or params.get("filename")
            content = params.get("content") or params.get("text")
            
            if path and content:
                # 既存の書き込みロジックを再利用
                result = await self.write_text_file(
                    content=content,
                    path=path,
                    session_id="current-session"
                )
                return {} # 成功時は空の辞書を返す（schema上のAnyに対応）
        
        # それ以外はエラーを返す
        raise RequestError.method_not_found(method)


async def main():
    PORT = 4321
    try:
        reader, writer = await asyncio.open_connection('localhost', PORT)
    except Exception as e:
        print(f"接続失敗: {e}")
        return

    client_impl = MyClient()
    # connect_to_agent(client, input_stream, output_stream)
    # SDK内部の ClientSideConnection の型チェックを通すための標準的な呼び出し
    conn = connect_to_agent(client_impl, writer, reader)

    print("Initializing...")
    await conn.initialize(
        protocol_version=PROTOCOL_VERSION,
        client_capabilities=ClientCapabilities(
            fs=FileSystemCapability(write_text_file=True)
        ),
        client_info=Implementation(name="my-client", version="0.1.0"),
    )

    print("Creating session...")
    try:
        # Copilot CLI が Internal Error を出す主な原因: 
        # 1. mcp_servers が None (デフォルト) だと落ちる場合がある -> 空リストを明示
        # 2. cwd がコンテナ内の絶対パスとして無効 -> コンテナ側のルートに近いパスを試す
        session = await conn.new_session(
            mcp_servers=[], 
            cwd="/" # いったんルートか "/tmp" など、確実に存在する絶対パスで試す
        )
        print(f"Session ID: {session.session_id}")
    except Exception as e:
        # ここでまだ Internal error が出るなら、サーバー側のログに「どのフィールドが不正か」出ているはずです
        print(f"Session Creation Failed: {e}")
        return

    await conn.prompt(
        session_id=session.session_id,
        prompt=[text_block("createツール を使って hello.txt を作成してください。")]
    )
    
    await asyncio.sleep(10)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
