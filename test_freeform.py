from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio

async def main():
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python3",
        args=["example2-3.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connected to MCP server")

            # Open Freeform
            result = await session.call_tool(
                "open_freeform",
                arguments={}
            )
            print(f"Open Freeform result: {result}")

            # Draw a rectangle
            result = await session.call_tool(
                "draw_rectangle",
                arguments={
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 150
                }
            )
            print(f"Draw rectangle result: {result}")

            # Add some text
            result = await session.call_tool(
                "add_text_in_freeform",
                arguments={
                    "x": 150,
                    "y": 150,
                    "text": "Hello from MCP!"
                }
            )
            print(f"Add text result: {result}")

            print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 