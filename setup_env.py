import os
import sys
import subprocess
from pathlib import Path

def check_and_setup_environment():
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("Not in a virtual environment. Creating one...")
        venv_path = current_dir / '.venv'
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)])
        
        # Determine the correct pip path
        if sys.platform == 'win32':
            pip_path = venv_path / 'Scripts' / 'pip'
        else:
            pip_path = venv_path / 'bin' / 'pip'
            
        # Install required packages
        subprocess.run([str(pip_path), 'install', 'google-generativeai', 'python-dotenv', 'mcp'])
        
        print(f"Virtual environment created at {venv_path}")
        print("Please activate the virtual environment and run the script again.")
        return False
    
    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write('GEMINI_API_KEY=your_api_key_here\n')
        print("Please add your Gemini API key to the .env file")
        return False
    
    return True

if __name__ == "__main__":
    if check_and_setup_environment():
        print("Environment is properly set up!")
        print("You can now run the application.")
    else:
        print("Please follow the instructions above to set up the environment.") 