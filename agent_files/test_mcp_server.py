from fastmcp import Client
import asyncio

async def test_deployed_server():
    # Connect to a running server
    async with Client("http://localhost:8001/sse/") as client:
        await client.ping()
        
        # Test with real network transport
        tools = await client.list_tools()
        print('tools', tools)
        assert len(tools) > 0
        
        result = await client.call_tool("get_remaining_time_and_submissions")
        print('get_remaining_time_and_submissions', result)

        # write a test.cpp file to the server
        with open('/server/test.cpp', 'w') as f:
            f.write('int main() { return 0; }')

        result = await client.call_tool("submit_solution", {"file_path": "/server/test.cpp"})
        print('submit_solution', result)

if __name__ == "__main__":
    asyncio.run(test_deployed_server())