# 依赖安装指南

## 🔧 问题诊断

之前的错误是 `grpcio` 需要编译，但缺少 Python.h。

## 🎯 解决方案（选择一个）

### 方案 1: 使用 FAISS（最简单，推荐）✅

FAISS 更轻量，不需要 grpcio，安装快：

```bash
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot

# 安装核心依赖
pip install sentence-transformers faiss-cpu beautifulsoup4 lxml

# 修改配置使用 FAISS
```

然后修改 `data/full_index_config.json`：
```json
"vector_db": {
  "type": "faiss",  // 改成 faiss
  "persist_directory": "./vector_db"
}
```

### 方案 2: 使用预编译的 ChromaDB

```bash
pip install chromadb==0.4.15 --no-build-isolation
```

如果还是失败，试试：
```bash
pip install chromadb --only-binary :all:
```

### 方案 3: 使用 Conda（最稳定）

```bash
# 创建新环境（可选但推荐）
conda create -n pathwise python=3.9
conda activate pathwise

# 安装依赖
conda install -c conda-forge sentence-transformers chromadb
conda install -c conda-forge beautifulsoup4 lxml pypdf pandas
```

### 方案 4: 最小安装（测试用）

只安装必要的包，暂时跳过 vector DB：

```bash
pip install pandas numpy sentence-transformers beautifulsoup4 lxml pypdf
```

然后先处理数据，等需要构建 vector DB 时再装。

## ✅ 验证安装

运行这个检查哪些包已安装：

```bash
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot
python << 'EOF'
import sys
packages = {
    'sentence_transformers': 'Embeddings',
    'chromadb': 'ChromaDB (optional)',
    'faiss': 'FAISS (optional)',
    'pandas': 'Data processing',
    'pypdf': 'PDF processing',
    'bs4': 'HTML processing'
}

print("Package Status Check:")
print("=" * 60)
for package, desc in packages.items():
    try:
        __import__(package)
        print(f"✅ {package:20s} - {desc}")
    except ImportError:
        print(f"❌ {package:20s} - {desc} (NOT INSTALLED)")
print("=" * 60)
EOF
```

## 🚀 我的推荐流程

### Step 1: 安装基础包（快速）

```bash
pip install pandas numpy beautifulsoup4 lxml pypdf tqdm
```

### Step 2: 安装 embeddings（可能需要几分钟）

```bash
pip install sentence-transformers
```

### Step 3: 选择 Vector DB

**选项 A - FAISS（推荐，快速）**：
```bash
pip install faiss-cpu
```

**选项 B - ChromaDB（功能更多）**：
```bash
# 先试这个
pip install chromadb --only-binary :all:

# 如果失败，用 conda
conda install -c conda-forge chromadb
```

## 🐛 常见问题

### Q1: sentence-transformers 安装很慢

```bash
# 使用清华镜像加速
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers
```

### Q2: grpcio 编译失败

```bash
# 跳过 ChromaDB，使用 FAISS
pip install faiss-cpu

# 或安装预编译的 grpcio
pip install grpcio --only-binary :all:
```

### Q3: 权限错误

```bash
pip install --user sentence-transformers faiss-cpu
```

### Q4: 依赖冲突

```bash
# 创建新的 conda 环境
conda create -n pathwise python=3.9
conda activate pathwise
pip install -r requirements.txt
```

## 📦 完整依赖列表（requirements-minimal.txt）

如果你想最小化安装，我创建了一个精简版：

```bash
# 保存这个为 requirements-minimal.txt
pandas>=1.4.0
numpy>=1.21.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
pypdf>=3.0.0
tqdm>=4.62.0
```

安装：
```bash
pip install -r requirements-minimal.txt
```

## 🎯 快速开始（跳过 API）

如果你只想测试 RAG 核心功能，不需要 FastAPI：

```bash
# 只安装 RAG 核心依赖
pip install sentence-transformers faiss-cpu pandas pypdf beautifulsoup4 lxml

# 测试数据处理
python scripts/process_culpa_data.py documents/culpa_ratings.csv

# 测试文档扫描
python scripts/index_programs.py
```

## ✅ 成功标志

安装成功后，这个命令应该能运行：

```bash
python -c "from sentence_transformers import SentenceTransformer; print('✅ Ready to build RAG system!')"
```

## 🆘 如果都不行

最后的方案 - 使用 Docker：

```bash
# 创建 Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EOF

# 构建并运行
docker build -t pathwise .
docker run -it pathwise bash
```

---

## 推荐执行顺序

1. **先试方案 1（FAISS）** - 最快最简单
2. 如果需要 ChromaDB 功能，试方案 2
3. 如果都不行，用方案 3（Conda）
4. 实在不行，用方案 4 先测试数据处理

选好方案后告诉我，我可以帮你继续！

