#!/bin/bash
# 快速安装脚本

echo "========================================="
echo "PathWise 依赖快速安装"
echo "========================================="

echo ""
echo "方案 1: 使用 FAISS（推荐，最快）"
echo "方案 2: 使用 ChromaDB（功能更多）"
echo "方案 3: 检查已安装的包"
echo ""
read -p "选择方案 (1/2/3): " choice

case $choice in
  1)
    echo "安装 FAISS 方案..."
    pip install sentence-transformers faiss-cpu beautifulsoup4 lxml pypdf pandas tqdm
    ;;
  2)
    echo "安装 ChromaDB 方案..."
    pip install sentence-transformers chromadb beautifulsoup4 lxml pypdf pandas tqdm --only-binary :all:
    ;;
  3)
    echo "检查已安装的包..."
    python << 'PYEOF'
packages = ['sentence_transformers', 'chromadb', 'faiss', 'pandas', 'pypdf', 'bs4']
for p in packages:
    try:
        __import__(p)
        print(f"✅ {p}")
    except:
        print(f"❌ {p}")
PYEOF
    ;;
  *)
    echo "无效选择"
    exit 1
    ;;
esac

echo ""
echo "安装完成！运行测试："
echo "python -c \"from sentence_transformers import SentenceTransformer; print('✅ Ready!')\""
