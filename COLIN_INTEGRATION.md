# Colin 数据集成快速指南

根据 Colin 的 PR #1 调整的集成步骤。

## 📊 Colin 提供的数据

从 PR #1 可以看到：

1. **culpa_ratings.csv** - CULPA 评分数据
   - 格式：`professor_name, rating`（两列）
   - 来源：Columbia Directory of Courses (Spring 2025)
   - 包含所有春季有课的教授

2. **春季课程数据**（准备添加）
   - 课程代码、名称、描述
   - 可能在 Colin 的 notebook 中间步骤

## 🚀 快速集成步骤

### 方法 1: 使用自动化脚本（推荐）

```bash
# 1. 运行合并工具
python scripts/merge_colin_data.py

# 选择选项 2 (Interactive merge)
# 它会自动：
# - 获取 Colin 的分支
# - 列出所有数据文件
# - 让你选择要复制哪些文件
```

### 方法 2: 手动合并

```bash
# 1. 获取 Colin 的分支
git fetch origin colin

# 2. 查看他添加了什么文件
git diff --name-only HEAD origin/colin | grep -E "culpa|course|document"

# 3. 复制数据文件
git checkout origin/colin -- documents/culpa_ratings.csv
# 如果有其他文件也复制
git checkout origin/colin -- documents/spring_courses.json

# 4. 查看文件内容
head documents/culpa_ratings.csv
```

## 🔧 处理数据

### 步骤 1: 处理 CULPA 评分

```bash
python scripts/process_culpa_data.py documents/culpa_ratings.csv
```

**脚本已优化，支持**：
- ✅ 自动识别列名（`professor_name`, `prof_name`, `name` 等）
- ✅ 自动识别评分列（`rating`, `score` 等）
- ✅ 清理重复教授（保留最高评分）
- ✅ 验证评分范围（0-5）
- ✅ 生成详细统计报告
- ✅ 添加学期信息（Spring 2025）

**输出**：
- `data/processed/culpa_ratings_processed.csv` - 清理后的数据
- `data/processed/culpa_statistics.txt` - 统计报告
- `data/culpa_index_config.json` - 索引配置

### 步骤 2: 查看统计报告

```bash
cat data/processed/culpa_statistics.txt
```

预期输出：
```
============================================================
CULPA Ratings Statistics Report
============================================================

Total Professors: 150

Rating Distribution:
  Mean rating: 3.95
  Median rating: 4.02
  Min rating: 2.80
  Max rating: 4.95
  Std deviation: 0.45

  Ratings >= 4.0: 95 (63.3%)
  Ratings 3.0-3.9: 48
  Ratings < 3.0: 7

Top 10 Rated Professors:
  John Smith: 4.95
  ...
```

### 步骤 3: 集成春季课程（当 Colin 添加后）

```bash
# 当 Colin 添加课程数据后
python scripts/integrate_spring_courses.py documents/spring_courses.json
```

这会：
- ✅ 加载课程数据
- ✅ 匹配教授名字到 CULPA 评分
- ✅ 创建课程文档（用于 RAG）
- ✅ 生成课程统计报告

### 步骤 4: 重新构建索引

```bash
# 只有 CULPA 数据
python scripts/build_index.py data/culpa_index_config.json

# 或者，如果也有课程数据
python scripts/build_index.py data/combined_index_config.json
```

### 步骤 5: 测试集成

```bash
# 测试 RAG 组件
python scripts/test_rag.py

# 应该能看到真实的 CULPA 评分
# 启动 API
python scripts/start_server.py

# 在新终端测试
curl -X POST "http://localhost:8000/professors" \
  -H "Content-Type: application/json" \
  -d '{"course_codes": ["COMS 4111"]}'
```

## 📋 数据格式说明

### CULPA 评分格式（Colin 的格式）

```csv
professor_name,rating
John Smith,4.8
Jane Doe,4.5
Robert Johnson,3.9
```

**字段**：
- `professor_name`: 教授全名
- `rating`: CULPA 评分（0-5）

**处理脚本会自动**：
- 清理空白字符
- 移除缺失数据
- 验证评分范围
- 处理重复教授
- 添加学期标签

### 春季课程格式（Colin 准备添加）

**JSON 格式**：
```json
[
  {
    "course_code": "COMS 4111",
    "course_name": "Introduction to Databases",
    "description": "Introduction to fundamental concepts...",
    "instructor": "John Smith",
    "credits": 3
  }
]
```

**或 CSV 格式**：
```csv
course_code,course_name,description,instructor,credits
COMS 4111,Introduction to Databases,"Introduction to...",John Smith,3
```

## 🔍 验证集成

### 1. 检查数据文件

```bash
# 检查评分数据
wc -l data/processed/culpa_ratings_processed.csv
head -20 data/processed/culpa_ratings_processed.csv

# 检查向量数据库
ls -lh vector_db/
```

### 2. 测试 API 查询

```python
# test_culpa_integration.py
import requests

# 测试教授查询
response = requests.post(
    "http://localhost:8000/professors",
    json={"course_codes": ["COMS 4111", "COMS 4701"]}
)

print(response.json())
# 应该返回真实的 CULPA 评分
```

### 3. 测试规划生成

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "program": "MS Computer Science",
      "catalog_year": 2023,
      "preference": "best_professors"
    }
  }'

# 应该使用真实的 CULPA 评分推荐教授
```

## 🐛 故障排除

### 问题 1: 找不到 Colin 的分支

```bash
# 确保 remote 正确
git remote -v

# 应该看到 origin 指向 ms6998/COMS4995---RAG-Chatbot

# 重新获取
git fetch origin
git branch -r | grep colin
```

### 问题 2: 列名不匹配

如果 Colin 的 CSV 列名不同：

```bash
# 查看实际的列名
head -1 documents/culpa_ratings.csv

# 处理脚本会自动识别这些变体：
# - professor_name, prof_name, name, professor, instructor
# - rating, score, rating_score, culpa_rating
```

如果还是不匹配，手动添加映射：

```python
# 在 process_culpa_data.py 中的 load_culpa_ratings 函数
column_mapping = {
    'Colin_的_列名': 'professor_name',
    'Colin_的_评分列': 'rating'
}
df = df.rename(columns=column_mapping)
```

### 问题 3: 评分范围异常

如果看到警告：
```
Warning: Found 5 ratings outside 0-5 range
Will clamp to valid range
```

这是正常的，脚本会自动修正到 0-5 范围。

### 问题 4: 重复教授

```
Found duplicate professors, keeping highest rating for each
```

这也是正常的，脚本会自动处理。

## 📊 预期结果

集成完成后，你的系统将：

1. **真实数据**: 
   - 150+ 个教授的真实 CULPA 评分
   - 春季学期的实际课程列表

2. **更准确的推荐**:
   - 基于真实学生评价
   - 反映当前学期情况

3. **更好的演示**:
   - 可以展示真实数据
   - 与 Columbia 实际情况一致

## 🤝 与 Colin 协作

### 你负责

- ✅ 运行集成脚本
- ✅ 处理数据格式问题
- ✅ 构建向量索引
- ✅ 测试 API 功能
- ✅ 更新文档

### Colin 负责

- ✅ 提供 CULPA 评分数据（已完成）
- 🔄 添加春季课程数据
- 🔄 提供学位要求文档
- 🔄 数据质量验证

### 沟通检查清单

- [ ] 确认 culpa_ratings.csv 格式
- [ ] 确认春季课程数据何时ready
- [ ] 确认学位要求文档来源
- [ ] 协调数据更新频率
- [ ] 测试集成结果

## 📈 下一步

1. **立即做**：
   ```bash
   python scripts/merge_colin_data.py
   python scripts/process_culpa_data.py documents/culpa_ratings.csv
   python scripts/build_index.py data/culpa_index_config.json
   python scripts/test_rag.py
   ```

2. **等 Colin 添加课程数据后**：
   ```bash
   python scripts/integrate_spring_courses.py documents/spring_courses.json
   python scripts/build_index.py data/combined_index_config.json
   ```

3. **持续优化**：
   - 调整检索参数
   - 优化教授匹配算法
   - 添加更多元数据

---

有问题随时查阅这个指南！🚀

