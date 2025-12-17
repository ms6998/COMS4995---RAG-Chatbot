# CULPA 数据和春季课程集成指南

这个指南说明如何集成你同学添加的真实 CULPA 评分数据和春季课程信息。

## 📊 你同学已经完成的工作

根据 Pull Request #1，你的同学已经：

1. ✅ 从 Columbia CULPA 获取了真实的教授评分数据
2. ✅ 创建了 `culpa_ratings.csv` 文件（包含教授名字和评分）
3. ✅ 获取了春季学期的课程列表（包括课程名称和描述）

## 🔄 集成步骤

### 步骤 1: 处理 CULPA 评分数据

```bash
# 确保 culpa_ratings.csv 在 documents/ 文件夹中
ls documents/culpa_ratings.csv

# 运行处理脚本
python scripts/process_culpa_data.py

# 这会：
# - 清理和验证数据
# - 生成统计报告
# - 创建处理后的 CSV 文件
# - 生成索引配置文件
```

**输出文件**：
- `data/processed/culpa_ratings_processed.csv` - 清理后的评分数据
- `data/processed/culpa_statistics.txt` - 统计报告
- `data/culpa_index_config.json` - 索引配置

### 步骤 2: 集成春季课程数据

如果你的同学已经提供了春季课程数据文件：

```bash
# 假设课程数据在 documents/spring_courses.json
python scripts/integrate_spring_courses.py documents/spring_courses.json

# 这会：
# - 加载课程信息（课程代码、名称、描述、教授）
# - 将课程与 CULPA 评分匹配
# - 创建课程文档用于 RAG 索引
# - 生成组合索引配置
```

**期望的课程数据格式** (JSON 或 CSV):

```json
[
  {
    "course_code": "COMS 4111",
    "course_name": "Introduction to Databases",
    "description": "Introduction to database systems...",
    "instructor": "John Smith",
    "credits": 3
  }
]
```

或 CSV:
```csv
course_code,course_name,description,instructor,credits
COMS 4111,Introduction to Databases,"Introduction to...",John Smith,3
```

### 步骤 3: 构建新的向量索引

```bash
# 使用 CULPA 数据构建索引
python scripts/build_index.py data/culpa_index_config.json

# 或者，如果有课程数据，使用组合配置
python scripts/build_index.py data/combined_index_config.json
```

### 步骤 4: 测试新数据

```bash
# 测试 RAG 系统
python scripts/test_rag.py

# 启动 API 服务器
python scripts/start_server.py

# 测试 API
python tests/test_api.py
```

## 📝 数据格式说明

### CULPA 评分数据格式

你同学的 `culpa_ratings.csv` 应该包含：

```csv
professor_name,rating
John Smith,4.8
Jane Doe,4.5
...
```

**可选字段**（如果有的话）：
- `course_code` - 课程代码
- `tags` - 学生反馈标签
- `num_reviews` - 评价数量

### 春季课程数据格式

从 Columbia 课程目录获取的数据应该包含：

**必需字段**：
- `course_code` - 课程代码（如 "COMS 4111"）
- `course_name` - 课程名称
- `instructor` - 教授名字

**可选字段**：
- `description` - 课程描述
- `credits` - 学分数
- `prerequisites` - 先修课程
- `schedule` - 上课时间
- `location` - 上课地点

## 🔧 自定义处理脚本

如果你的数据格式不同，可以修改 `process_culpa_data.py`:

```python
# 在 load_culpa_ratings 函数中
def load_culpa_ratings(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    
    # 如果列名不同，重命名
    df = df.rename(columns={
        'prof_name': 'professor_name',  # 如果原列名是 prof_name
        'score': 'rating'                # 如果原列名是 score
    })
    
    return df
```

## 📊 查看数据统计

处理完数据后，查看统计报告：

```bash
# CULPA 评分统计
cat data/processed/culpa_statistics.txt

# 示例输出：
# ============================================================
# CULPA Ratings Statistics Report
# ============================================================
# Total Professors: 150
# 
# Rating Distribution:
#   Mean:   4.12
#   Median: 4.20
#   Std:    0.45
#   Min:    2.80
#   Max:    5.00
# ...
```

## 🔗 将新数据集成到 API

新数据会自动集成到现有 API 端点：

### 1. 查询教授评分

```bash
curl -X POST "http://localhost:8000/professors" \
  -H "Content-Type: application/json" \
  -d '{
    "course_codes": ["COMS 4111", "COMS 4701"]
  }'
```

现在会返回真实的 CULPA 评分！

### 2. 查询春季课程

如果集成了课程数据，可以查询：

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What courses are offered in Spring 2025 for machine learning?"
  }'
```

### 3. 生成规划（带真实评分）

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "program": "MS Computer Science",
      "catalog_year": 2023,
      "target_graduation": "Spring 2026",
      "preference": "best_professors"
    }
  }'
```

现在会使用真实的 CULPA 评分推荐教授！

## 🎯 下一步工作

### 优先级 1: 完成数据集成

- [ ] 确认 `culpa_ratings.csv` 格式正确
- [ ] 运行 `process_culpa_data.py`
- [ ] 检查统计报告
- [ ] 重新构建向量索引

### 优先级 2: 添加春季课程

- [ ] 从你同学那里获取春季课程数据文件
- [ ] 确认数据格式（JSON 或 CSV）
- [ ] 运行 `integrate_spring_courses.py`
- [ ] 验证课程-教授匹配

### 优先级 3: 添加学位要求文档

- [ ] 获取官方学位要求 PDF/HTML
- [ ] 放入 `data/raw/` 文件夹
- [ ] 更新 `index_config.json`
- [ ] 重新构建索引

## 🐛 常见问题

### Q1: CULPA 数据列名不匹配

**问题**：`KeyError: 'professor_name'`

**解决**：
```python
# 在 process_culpa_data.py 中添加列名映射
df = df.rename(columns={
    'prof': 'professor_name',
    'score': 'rating'
})
```

### Q2: 教授名字匹配不上

**问题**：课程和评分无法匹配

**原因**：名字格式不一致（"John Smith" vs "Smith, John"）

**解决**：使用 `normalize_professor_name` 函数，或手动清理数据

### Q3: 课程代码格式不统一

**问题**：有的是 "COMS4111"，有的是 "COMS 4111"

**解决**：
```python
# 标准化课程代码
def normalize_course_code(code):
    # 移除空格
    code = code.replace(' ', '')
    # 添加空格在字母和数字之间
    return re.sub(r'([A-Z]+)(\d+)', r'\1 \2', code)
```

### Q4: 数据太大，索引构建很慢

**解决**：
```python
# 在 config.py 中
CHUNK_SIZE = 400  # 减小
batch_size = 16   # 减小批处理大小
```

## 📞 协作建议

### 与你的同学协调

1. **数据格式标准化**：
   - 统一列名
   - 统一课程代码格式
   - 统一教授名字格式

2. **分工**：
   - 你：RAG 系统和 API
   - 同学：数据爬取和清理
   - 合作：数据集成和测试

3. **Git 工作流**：
   ```bash
   # 拉取同学的更改
   git pull origin main
   
   # 处理数据
   python scripts/process_culpa_data.py
   
   # 提交你的更改
   git add .
   git commit -m "Integrate CULPA ratings data"
   git push origin mingjun
   ```

## 📚 参考文件

- `scripts/process_culpa_data.py` - CULPA 数据处理
- `scripts/integrate_spring_courses.py` - 课程数据集成
- `src/rag/indexer.py` - 索引构建逻辑
- `src/api/app.py` - API 端点

## 🎉 完成后的效果

集成完成后，你的系统将：

1. ✅ 使用真实的 CULPA 评分（150+ 教授）
2. ✅ 包含春季学期课程信息
3. ✅ 准确匹配课程和教授
4. ✅ 提供基于真实数据的推荐

这将大大提升项目的实用性和演示效果！🚀

---

有问题随时查阅这个指南或询问。祝集成顺利！


