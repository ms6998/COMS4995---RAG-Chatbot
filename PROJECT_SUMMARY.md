# PathWise - 项目总结

## 项目概述

**PathWise** 是一个基于 RAG (Retrieval-Augmented Generation) 的智能学位顾问系统，专门为工程学位学生提供：
- 学位要求问答
- 个性化学期规划
- 基于教授评分的课程推荐

## 技术架构

### 核心组件

```
┌─────────────────────────────────────────────────┐
│                  FastAPI Server                  │
│                   (API Layer)                    │
└────────────┬────────────────────────┬────────────┘
             │                        │
    ┌────────▼────────┐      ┌───────▼────────┐
    │  RAG Retriever  │      │  LLM Interface │
    │                 │      │  (GPT-4/Claude)│
    └────────┬────────┘      └────────────────┘
             │
    ┌────────▼────────┐
    │  Vector Store   │
    │ (Chroma/FAISS)  │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │    Embeddings   │
    │ (Sentence-BERT) │
    └─────────────────┘
```

### 模块说明

#### 1. Document Processing (`src/rag/document_processor.py`)
- **功能**：文档提取、清理和分块
- **支持格式**：PDF, HTML, TXT
- **分块策略**：
  - 大小：600 tokens
  - 重叠：100 tokens
  - 保留句子完整性
- **元数据提取**：
  - 项目名称
  - 目录年份
  - 课程代码（自动识别）

#### 2. Embeddings (`src/rag/embeddings.py`)
- **默认模型**：`sentence-transformers/all-MiniLM-L6-v2`
- **维度**：384
- **备选方案**：OpenAI `text-embedding-ada-002`
- **优化**：批处理和余弦相似度计算

#### 3. Vector Store (`src/rag/vector_store.py`)
- **支持后端**：
  - ChromaDB（默认，持久化）
  - FAISS（高性能，内存优化）
- **功能**：
  - 语义搜索
  - 元数据过滤
  - 批量插入

#### 4. Retriever (`src/rag/retriever.py`)
- **RAGRetriever**：学位要求检索
  - Top-K 检索（默认 k=5）
  - 相似度阈值过滤
  - 上下文格式化（带引用）
- **ProfessorRatingsRetriever**：教授评分检索
  - 按课程代码查询
  - 评分排序
  - 最佳教授推荐

#### 5. Indexer (`src/rag/indexer.py`)
- **DocumentIndexer**：索引构建器
- **配置驱动**：JSON 配置文件
- **批处理**：高效的批量索引

#### 6. LLM Interface (`src/rag/llm_interface.py`)
- **支持的提供商**：
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude)
- **Prompt 模板**：
  - 学位 Q&A
  - 规划生成
- **输出格式**：自然语言 + 结构化 JSON

#### 7. API Server (`src/api/app.py`)
- **框架**：FastAPI
- **端点**：
  - `GET /health`：健康检查
  - `POST /ask`：问答
  - `POST /plan`：生成规划
  - `POST /professors`：教授查询
- **验证**：Pydantic 模型
- **CORS**：跨域支持

## 数据流程

### 索引构建流程

```
Raw Documents → Document Processor → Chunks → Embeddings → Vector Store
     (PDF)            ↓                ↓          ↓             ↓
                  Clean Text      600 tokens   384-dim     ChromaDB
                  + Metadata      overlapping   vectors     Index
```

### 查询流程（Q&A）

```
User Question
    ↓
Generate Query Embedding
    ↓
Vector Search (Top-K)
    ↓
Retrieve Relevant Chunks
    ↓
Format Context with Citations
    ↓
Build LLM Prompt
    ↓
Generate Answer
    ↓
Return with Sources
```

### 规划流程

```
User Profile → Retrieve Requirements → Extract Course List
                                            ↓
                                     Query Prof Ratings
                                            ↓
                                   Format Context
                                            ↓
                                   Planning Prompt
                                            ↓
                                   LLM Generation
                                            ↓
                              Parse JSON + Explanation
                                            ↓
                              Semester-by-Semester Plan
```

## 关键特性实现

### 1. 源引用系统
```python
# 每个检索结果包含：
{
    'text': '...',
    'metadata': {
        'source': 'bulletin.pdf',
        'program': 'MS CS',
        'catalog_year': 2023
    },
    'similarity': 0.85
}
```

### 2. 元数据过滤
```python
# 按项目和年份过滤
filter_dict = {
    'program': 'MS Computer Science',
    'catalog_year': 2023
}
results = retriever.retrieve(query, filter_dict=filter_dict)
```

### 3. 教授优化
```python
# 自动选择最高评分教授
best_prof = prof_retriever.get_best_professor_for_course("COMS 4111")
# Output: Prof. Smith (4.8/5.0) - "very clear, organized"
```

### 4. 结构化输出
```python
# LLM 生成 JSON 格式的规划
{
    "semesters": [
        {
            "name": "Fall 2024",
            "courses": [
                {
                    "course_code": "COMS 4111",
                    "prof": "Smith",
                    "rating": 4.8,
                    "category": "core"
                }
            ]
        }
    ],
    "notes": ["Planning assumptions..."]
}
```

## 性能优化

### Embedding 生成
- 批处理：32 samples/batch
- 缓存：向量存储持久化
- 模型大小：~100MB（本地模型）

### 检索优化
- Top-K 限制：避免过多结果
- 相似度阈值：过滤低相关度结果
- 元数据索引：快速过滤

### API 性能
- 异步处理（FastAPI）
- 连接复用
- 响应缓存（可选）

## 测试覆盖

### 单元测试
- 文档处理和分块
- 向量存储操作
- 检索准确性

### 集成测试
- 端到端 RAG pipeline
- API 端点测试
- 错误处理

### 测试数据
- 2个学位项目（MS CS, MS DS）
- 20个教授评分记录
- 4个测试查询

## 安全和隐私

### 数据处理
- 本地向量存储（无外部上传）
- API key 安全存储（config.py，已 gitignore）
- 无用户数据持久化

### API 安全
- CORS 配置
- 输入验证（Pydantic）
- 错误处理和日志记录

### 免责声明
- 所有响应包含免责声明
- 推荐官方顾问确认
- 评分数据来源说明

## 扩展可能性

### 短期改进（1-2周）
1. **前端界面**
   - Streamlit 快速原型
   - 或 React 完整 web 应用

2. **更多数据**
   - 爬取 Rate My Professors
   - 添加更多项目要求

3. **可视化**
   - Mermaid 图表生成
   - 课程依赖关系图

### 中期改进（1-2个月）
1. **Fine-tuning**
   - 在学位要求数据上微调
   - RLHF 优化回答质量

2. **高级规划**
   - 先修课程验证
   - 时间冲突检测
   - 学期负载平衡

3. **用户系统**
   - 认证和授权
   - 保存的规划
   - 个性化推荐

### 长期改进（3-6个月）
1. **多模态支持**
   - 解析流程图
   - 课程关系可视化
   - 语音交互

2. **实时集成**
   - 大学课程目录 API
   - 实时教授评分
   - 课程可用性查询

3. **AI Agent**
   - 主动提醒（截止日期）
   - 课程推荐系统
   - 职业路径规划

## 项目统计

### 代码规模
- Python 文件：~15
- 总代码行数：~2500
- 测试覆盖：核心模块

### 依赖项
- 核心依赖：15个
- 主要框架：
  - FastAPI
  - LangChain
  - ChromaDB
  - Sentence-Transformers

### 文档
- README.md：完整文档
- QUICKSTART.md：快速入门
- 内联文档：所有模块

## 项目时间线（实际）

- **Day 1-2**：架构设计和依赖选择 ✅
- **Day 3-4**：RAG 核心模块实现 ✅
- **Day 5**：教授评分集成 ✅
- **Day 6-7**：API 端点开发 ✅
- **Day 8**：示例数据和测试 ✅
- **Day 9-10**：文档和优化 ✅

## 学习收获

### 技术收获
1. **RAG 系统设计**：
   - 文档分块策略
   - 向量数据库选择
   - 检索-生成协同

2. **LLM 集成**：
   - Prompt engineering
   - 结构化输出解析
   - 错误处理

3. **API 设计**：
   - FastAPI 最佳实践
   - 异步处理
   - 数据验证

### 领域知识
1. **学位要求复杂性**：
   - 多层次要求（核心、选修、track）
   - 先修关系
   - 政策变化

2. **教授评分**：
   - 数据质量挑战
   - 偏差和公平性
   - 多维度评估

## 参考资源

### 技术文档
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [Sentence-Transformers](https://www.sbert.net/)

### 论文
- RAG: [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- Dense Passage Retrieval: [DPR Paper](https://arxiv.org/abs/2004.04906)

### 课程相关
- COMS 4995: Applied Machine Learning
- Lecture 10: Industry Trends
- Lecture 11: Recent Trends in RL for LLMs

## 总结

PathWise 成功实现了一个完整的 RAG 系统，展示了：
- ✅ 实际问题解决（学位规划）
- ✅ 现代 ML 技术应用（RAG, Embeddings）
- ✅ 工程最佳实践（模块化、测试、文档）
- ✅ 可扩展架构设计

该系统可以作为更大规模学术顾问平台的原型，或适配到其他需要知识检索和规划的领域。

---

**项目负责人**：Mingjun Sun  
**完成日期**：2025年12月  
**用于课程**：COMS 4995 - Applied Machine Learning

