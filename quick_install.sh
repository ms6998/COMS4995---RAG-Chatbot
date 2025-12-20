#!/bin/bash
# Quick installation script

echo "========================================="
echo "PathWay Dependency Quick Install"
echo "========================================="

echo ""
echo "Option 1: Use ChromaDB (more features)"
echo "Option 2: Check installed packages"
echo ""
read -p "Select an option (1/2/3): " choice

case $choice in
  1)
    echo "Installing ChromaDB option..."
    pip install sentence-transformers chromadb beautifulsoup4 lxml pypdf pandas tqdm --only-binary :all:
    ;;
  2)
    echo "Checking installed packages..."
    python << 'PYEOF'
packages = ['sentence_transformers', 'chromadb', 'pandas', 'pypdf', 'bs4']
for p in packages:
    try:
        __import__(p)
        print(f"✅ {p}")
    except:
        print(f"❌ {p}")
PYEOF
    ;;
  *)
    echo "Invalid selection"
    exit 1
    ;;
esac

echo ""
echo "Installation complete! Run a test:"
echo "python -c \"from sentence_transformers import SentenceTransformer; print('✅ Ready!')\""
