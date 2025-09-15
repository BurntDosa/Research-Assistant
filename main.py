#!/usr/bin/env python3
"""
Research Discovery Hub - Main Entry Point

Modern Research Assistant with AI-powered literature discovery using Google Gemini 2.5 Flash
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the Research Discovery Hub"""
    print("🔬 Research Discovery Hub")
    print("=" * 50)
    print("🚀 Starting Enhanced Gradio Interface...")
    print()
    
    try:
        from src.apps.app_gradio_new import main as gradio_main
        gradio_main()
    except ImportError as e:
        print(f"❌ Error: Missing dependencies - {e}")
        print("\n💡 Please install requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()