# 环境修复快速指南

## 🔍 问题诊断

你的 Anaconda 环境有一些库损坏（torch, mkl）。

## ✅ 推荐解决方案：创建新环境（最快最稳）

### 在你的终端运行这些命令：

```bash
# 1. 创建新的干净环境
conda create -n pathwise python=3.9 -y

# 2. 激活新环境
conda activate pathwise

# 3. 安装依赖（用 conda，预编译版本）
conda install -c pytorch -c conda-forge sentence-transformers faiss-cpu pandas -y

# 4. 安装剩余依赖（用 pip）
pip install pypdf beautifulsoup4 lxml

# 5. 验证安装
python -c "import sentence_transformers, faiss, pandas; print('✅ Ready!')"
```

### 然后构建 Vector Database：

```bash
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot

# 构建索引
python scripts/build_simple_index.py

# 测试搜索
python scripts/test_simple_search.py
```

## 🎯 为什么这样做？

- ✅ 避免现有环境的冲突
- ✅ 使用预编译的包（不需要编译）
- ✅ 干净的开始
- ✅ 大约 5 分钟完成

## 📋 完整命令（复制粘贴）

```bash
# 一键创建和安装
conda create -n pathwise python=3.9 -y && \
conda activate pathwise && \
conda install -c pytorch -c conda-forge sentence-transformers faiss-cpu pandas -y && \
pip install pypdf beautifulsoup4 lxml && \
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot && \
python scripts/build_simple_index.py
```

## 🔄 以后使用

每次使用前激活环境：
```bash
conda activate pathwise
cd /Users/mingjunsun/Desktop/COMS4995---RAG-Chatbot
python scripts/start_server.py
```

## 🆘 如果还是不行

使用 Google Colab：
1. 上传 `Build_Vector_DB_Colab.ipynb` 到 Colab
2. 在云端构建 vector database
3. 下载构建好的 vector_db_simple.zip
4. 解压到项目文件夹

---

推荐先试新环境方案！应该能快速解决。


