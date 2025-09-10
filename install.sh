#!/bin/bash

# Slack Message Analytics Dashboard - Installation Script
# This script sets up the environment and installs all dependencies

set -e  # Exit on any error

echo "🚀 Setting up Slack Message Analytics Dashboard..."
echo "=================================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version check passed: $python_version"

# Check if pip is installed
echo "📋 Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi
echo "✅ pip3 is available"

# Create virtual environment (optional but recommended)
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️  Warning: Could not download NLTK data: {e}')
"

# Download spaCy model (optional)
echo "🤖 Downloading spaCy model..."
python -m spacy download en_core_web_sm 2>/dev/null || echo "⚠️  Warning: Could not download spaCy model (optional)"

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
echo "✅ Data directory created"

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"

# Create sample data
echo "📊 Creating sample data..."
python src/slack_data_loader.py data/sample_export.json --create-sample
echo "✅ Sample data created"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x src/app.py
chmod +x install.sh
echo "✅ Scripts are now executable"

# Run basic tests
echo "🧪 Running basic tests..."
python -c "
import sys
sys.path.append('src')

try:
    from message_analyzer import MessageAnalyzer
    from dashboard import SlackAnalyticsDashboard
    from slack_data_loader import SlackDataLoader
    
    # Test imports
    analyzer = MessageAnalyzer()
    loader = SlackDataLoader()
    
    print('✅ All modules imported successfully')
    print('✅ Basic functionality test passed')
    
except Exception as e:
    print(f'❌ Error during testing: {e}')
    sys.exit(1)
"

echo ""
echo "🎉 Installation completed successfully!"
echo "=================================================="
echo ""
echo "📖 Quick Start:"
echo "  1. Run the dashboard: python src/app.py"
echo "  2. Open your browser: http://localhost:8050"
echo "  3. Upload your Slack export or use the sample data"
echo ""
echo "🔧 Advanced options:"
echo "  - Custom port: python src/app.py --port 8080"
echo "  - Debug mode: python src/app.py --debug"
echo "  - Help: python src/app.py --help"
echo ""
echo "📚 Documentation: See README.md for detailed usage instructions"
echo ""
echo "🚀 Ready to analyze your Slack messages!"