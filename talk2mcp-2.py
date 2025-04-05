import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import google.generativeai as genai
from concurrent.futures import TimeoutError
from functools import partial

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure the Gemini API
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('models/gemini-2.0-flash')

max_iterations = 3
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: model.generate_content(prompt)          ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def handle_math_query(session, query):
    """Handle mathematical queries"""
    global iteration, last_response, iteration_response
    
    while iteration < max_iterations:
        print(f"\n--- Iteration {iteration + 1} ---")
        if last_response is None:
            current_query = query
        else:
            # If we've already gotten a result, format it as a final answer
            if "TextContent" in str(last_response):
                result_values = []
                for content in last_response.content:
                    if hasattr(content, 'text'):
                        result_values.append(content.text)
                return f"FINAL_ANSWER: [{', '.join(result_values)}]"
            
            current_query = current_query + "\n\n" + " ".join(iteration_response)
            current_query = current_query + "  What should I do next?"

        # Get model's response with timeout
        print("Preparing to generate LLM response...")
        prompt = f"{system_prompt}\n\nQuery: {current_query}"
        try:
            response = await generate_with_timeout(prompt)
            response_text = response.text.strip()
            print(f"LLM Response: {response_text}")
            
            if response_text.startswith("FINAL_ANSWER:"):
                print(f"Final answer found: {response_text}")
                return response_text
            
            if response_text.startswith("FUNCTION_CALL:"):
                _, function_info = response_text.split(":", 1)
                parts = [p.strip() for p in function_info.split("|")]
                func_name, params = parts[0], parts[1:]
                
                try:
                    # Find the matching tool
                    tool = next((t for t in tools if t.name == func_name), None)
                    if not tool:
                        raise ValueError(f"Unknown tool: {func_name}")

                    # Prepare arguments
                    arguments = {}
                    if 'properties' in tool.inputSchema:
                        param_names = list(tool.inputSchema['properties'].keys())
                        for i, param in enumerate(params):
                            if i < len(param_names):
                                # Convert parameter to appropriate type
                                param_type = tool.inputSchema['properties'][param_names[i]].get('type', 'string')
                                if param_type == 'integer':
                                    param = int(param)
                                elif param_type == 'number':
                                    param = float(param)
                                arguments[param_names[i]] = param

                    # Call the tool
                    result = await session.call_tool(func_name, arguments=arguments)
                    result_text = str(result)
                    print(f"Tool result: {result_text}")
                    
                    # If this is an ASCII calculation, format it as a final answer
                    if func_name == "strings_to_chars_to_int":
                        result_values = []
                        for content in result.content:
                            if hasattr(content, 'text'):
                                result_values.append(content.text)
                        return f"FINAL_ANSWER: [{', '.join(result_values)}]"
                    
                    iteration_response.append(result_text)
                    last_response = result
                    
                except Exception as e:
                    print(f"Error executing function: {e}")
                    iteration_response.append(f"Error: {str(e)}")
                    last_response = f"Error: {str(e)}"
            
            iteration += 1
            
        except Exception as e:
            print(f"Failed to get LLM response: {e}")
            break
    
    return "FINAL_ANSWER: [Error: Max iterations reached]"

async def handle_freeform_query(session, query):
    """Handle Freeform-related queries"""
    try:
        if "open" in query.lower():
            # Open Freeform
            result = await session.call_tool(
                "open_freeform",
                arguments={}
            )
            print(f"Open Freeform result: {result}")
            
        if "rectangle" in query.lower():
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
            
        if "text" in query.lower():
            # Add text
            result = await session.call_tool(
                "add_text_in_freeform",
                arguments={
                    "x": 150,
                    "y": 150,
                    "text": "Hello from MCP!"
                }
            )
            print(f"Add text result: {result}")
            
        return "Operations completed successfully"
    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    reset_state()  # Reset at the start of main
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python3",
            args=["example2-3.py"]  # Using example2-3.py which has both math and Freeform tools
        )

        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                print("Session created, initializing...")
                await session.initialize()
                
                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                global tools  # Make tools available globally
                tools = tools_result.tools
                print(f"Successfully retrieved {len(tools)} tools")

                # Create tools description
                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                    except Exception as e:
                        print(f"Error processing tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                tools_description = "\n".join(tools_description)
                
                # Create system prompt
                global system_prompt
                system_prompt = f"""You are an agent that can perform both mathematical calculations and Freeform operations. You have access to various tools.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [result]

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- Do not repeat function calls with the same parameters

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: open_freeform
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

                while True:
                    # Get user input
                    query = input("\nEnter your query (or 'quit' to exit): ")
                    if query.lower() == 'quit':
                        break
                        
                    # Determine query type and handle accordingly
                    if any(word in query.lower() for word in ['freeform', 'rectangle', 'text', 'draw']):
                        result = await handle_freeform_query(session, query)
                    else:
                        result = await handle_math_query(session, query)
                    
                    print(f"\nResult: {result}")
                    reset_state()  # Reset state for next query

    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
    
