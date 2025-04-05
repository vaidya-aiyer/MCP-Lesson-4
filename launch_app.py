import os
import sys
import subprocess
from pathlib import Path

def launch_application():
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        # Activate virtual environment
        if sys.platform == 'win32':
            activate_script = current_dir / '.venv' / 'Scripts' / 'activate'
            python_path = current_dir / '.venv' / 'Scripts' / 'python'
        else:
            activate_script = current_dir / '.venv' / 'bin' / 'activate'
            python_path = current_dir / '.venv' / 'bin' / 'python'
        
        if not activate_script.exists():
            print("Virtual environment not found. Please run setup_env.py first.")
            return
        
        # Set up the environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = str(current_dir)
        
        # Launch the application
        subprocess.run([str(python_path), 'talk2mcp-2.py'], env=env)
    else:
        # Already in virtual environment, just run the application
        subprocess.run([sys.executable, 'talk2mcp-2.py'])

if __name__ == "__main__":
    launch_application() 