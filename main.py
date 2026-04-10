"""
ScreenZen — Screenshot Super-Organizer
Entry point for the application.
"""

import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
    from screenzen.app import ScreenZenApp
except ImportError as e:
    print("\n" + "="*50)
    print(f" ERROR: Missing Dependency -> {e}")
    print("="*50)
    print("\nIt looks like you're trying to run ScreenZen without the virtual environment.")
    print("\nPlease use the following commands to run the app correctly:")
    print("\n[Git Bash]:")
    print("  source venv/Scripts/activate")
    print("  python main.py")
    print("\n[Command Prompt]:")
    print("  run.bat")
    print("\n" + "="*50 + "\n")
    sys.exit(1)


def main():
    """Launch the ScreenZen application."""
    app = ScreenZenApp()
    app.mainloop()


if __name__ == "__main__":
    main()
