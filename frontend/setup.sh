#!/bin/bash

echo "🎓 Setting up PathWise Frontend..."
echo ""

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start the development server, run:"
    echo "  npm run dev"
    echo ""
    echo "The app will be available at http://localhost:3000"
else
    echo "❌ Installation failed. Please check the errors above."
    exit 1
fi
