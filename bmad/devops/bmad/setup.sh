#!/bin/bash

# BMAD (Business Multi-Agent DevOps) Setup Script
echo "🚀 BMAD System Setup"
echo "===================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv bmad_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source bmad_env/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Make launcher executable
echo "🔧 Making launcher executable..."
chmod +x bmad.py

# Test installation
echo "🧪 Testing installation..."
python3 bmad.py help

echo ""
echo "✅ BMAD System setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Activate the virtual environment:"
echo "   source bmad_env/bin/activate"
echo ""
echo "2. Start using BMAD:"
echo "   python3 bmad.py help"
echo "   python3 bmad.py product-owner help"
echo "   python3 bmad.py backend help"
echo ""
echo "🎯 Ready to develop CoPilot with BMAD agents!"