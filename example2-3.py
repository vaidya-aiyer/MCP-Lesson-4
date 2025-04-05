# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import subprocess
import time
import os
from Foundation import NSBundle
from AppKit import NSWorkspace, NSApplication, NSApp
from ScriptingBridge import SBApplication
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str, size: int = 100) -> str:
    """Create a thumbnail from an image and add it to Freeform"""
    print("CALLED: create_thumbnail(image_path: str, size: int = 100) -> str:")
    try:
        # Open and resize the image
        img = PILImage.open(image_path)
        img.thumbnail((size, size))
        
        # Save the thumbnail
        thumbnail_path = f"thumbnail_{os.path.basename(image_path)}"
        img.save(thumbnail_path)
        
        # Add the thumbnail to Freeform
        script = f'''
        tell application "Freeform"
            activate
            tell front document
                make new image with properties {{file:"{os.path.abspath(thumbnail_path)}"}}
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return f"Thumbnail created and added to Freeform: {thumbnail_path}"
    except Exception as e:
        return f"Error creating thumbnail: {str(e)}"

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

@mcp.tool()
def open_freeform() -> str:
    """Open Freeform application and create a new document"""
    print("CALLED: open_freeform() -> str:")
    try:
        # Just open Freeform
        subprocess.run(['open', '-a', 'Freeform'], check=True)
        return """Freeform opened. Please follow these steps:
1. Press Command+N (⌘N) to create a new board
2. Wait for the new board to open"""
    except Exception as e:
        return f"Error opening Freeform: {str(e)}"

@mcp.tool()
def draw_rectangle(x: int, y: int, width: int, height: int) -> str:
    """Draw a rectangle in Freeform at specified coordinates"""
    print("CALLED: draw_rectangle(x: int, y: int, width: int, height: int) -> str:")
    try:
        # Activate Freeform
        subprocess.run(['open', '-a', 'Freeform'], check=True)
        return """Please follow these steps to draw a rectangle:
1. Click Insert > Rectangle in the menu bar
2. Click and drag on the board to draw the rectangle
3. Use the blue handles to adjust the size if needed"""
    except Exception as e:
        return f"Error activating Freeform: {str(e)}"

@mcp.tool()
def add_text_in_freeform(x: int, y: int, text: str) -> str:
    """Add text to Freeform at specified coordinates"""
    print("CALLED: add_text_in_freeform(x: int, y: int, text: str) -> str:")
    try:
        # Activate Freeform
        subprocess.run(['open', '-a', 'Freeform'], check=True)
        return f"""Please follow these steps to add text:
1. Click Insert > Text Box in the menu bar
2. Click where you want to add the text
3. Type: {text}"""
    except Exception as e:
        return f"Error activating Freeform: {str(e)}"

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
