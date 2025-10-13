#!/bin/bash
# Launch Research Discovery Hub
# Requires API key configuration on first run

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "🔬 Research Discovery Hub"
echo "=================================================="
echo "🚀 Starting application..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv_gemini" ]; then
    source venv_gemini/bin/activate
fi

# Launch the application
python main.py
