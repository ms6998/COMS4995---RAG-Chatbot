# 🚀 Colin Data Integration – Quick Start

A quick integration guide prepared based on your classmate Colin’s PR #1.

## 📦 Tools I Prepared for You

### 1. **merge_colin_data.py** – Automatically merge Colin’s data

```bash
python scripts/merge_colin_data.py

Features:
	•	Automatically fetches Colin’s branch
	•	Lists all data files
	•	Lets you choose which files to merge
	•	Intelligently copies them into your branch

⸻

2. process_culpa_data.py – Process CULPA ratings (optimized for Colin’s format)

python scripts/process_culpa_data.py documents/culpa_ratings.csv

Automatically handles:
	•	✅ Detects professor_name, rating format
	•	✅ Deduplicates professors (keeps the highest rating)
	•	✅ Validates rating range (0–5)
	•	✅ Generates a detailed statistics report
	•	✅ Prepares data for RAG indexing

⸻

3. integrate_spring_courses.py – Integrate spring courses

python scripts/integrate_spring_courses.py documents/spring_courses.json

Features:
	•	Matches courses with professors
	•	Merges CULPA ratings
	•	Creates course documents

⸻

🎯 Three-Step Integration Workflow

Step 1: Get Colin’s data

# Option A: Use the automated tool (recommended)
python scripts/merge_colin_data.py
# Choose "2" (Interactive merge)

# Option B: Manual copy
git fetch origin colin
git checkout origin/colin -- documents/culpa_ratings.csv


⸻

Step 2: Process the data

# Process CULPA ratings
python scripts/process_culpa_data.py documents/culpa_ratings.csv

# View the statistics report
cat data/processed/culpa_statistics.txt

Example expected output:

============================================================
CULPA Ratings Statistics Report
============================================================

Total Professors: 150

Rating statistics:
  Mean rating: 3.95
  Median rating: 4.02
  Min rating: 2.80
  Max rating: 4.95

  Ratings >= 4.0: 95 (63.3%)
  Ratings 3.0-3.9: 48
  Ratings < 3.0: 7

Top 10 Rated Professors:
  John Smith: 4.95
  ...


⸻

Step 3: Build the index and test

# Build the vector index
python scripts/build_index.py data/culpa_index_config.json

# Test the RAG system
python scripts/test_rag.py

# Start the API
python scripts/start_server.py

# Test in a new terminal
curl -X POST "http://localhost:8000/professors" \
  -H "Content-Type: application/json" \
  -d '{"course_codes": ["COMS 4111"]}'


⸻

🔧 Colin’s Data Format

According to his PR, the data format is:

professor_name,rating
John Smith,4.8
Jane Doe,4.5
Robert Johnson,3.9

My scripts are optimized to support:
	•	Automatic detection of column name variants
	•	Automatic trimming of whitespace and deduplication
	•	Automatic validation of rating ranges
	•	Adding a semester tag (Spring 2025)

⸻

📊 Complete Workflow Diagram

Colin’s branch (origin/colin)
    │
    ├─ documents/culpa_ratings.csv
    │
    ↓
[merge_colin_data.py] ← you run this
    │
    ↓
documents/culpa_ratings.csv (in your branch)
    │
    ↓
[process_culpa_data.py] ← then this
    │
    ├─ data/processed/culpa_ratings_processed.csv
    ├─ data/processed/culpa_statistics.txt
    └─ data/culpa_index_config.json
    │
    ↓
[build_index.py] ← build index
    │
    └─ vector_db/ (ChromaDB with real data)
    │
    ↓
[test_rag.py & start_server.py] ← testing
    │
    └─ API returns real CULPA ratings! 🎉


⸻

🎬 Video Demo Flow
	1.	Show the current system (sample data)

python scripts/test_rag.py
# Shows usage with sample data


	2.	Merge Colin’s real data

python scripts/merge_colin_data.py
# Select culpa_ratings.csv


	3.	Process and view statistics

python scripts/process_culpa_data.py documents/culpa_ratings.csv
cat data/processed/culpa_statistics.txt
# Shows 150+ real professor ratings


	4.	Rebuild the index

python scripts/build_index.py data/culpa_index_config.json
# Shows the indexing process


	5.	Test the new system

python scripts/test_rag.py
# Now using real data!


	6.	API demo

# Start the server
python scripts/start_server.py

# Query professor ratings
curl http://localhost:8000/professors \
  -d '{"course_codes": ["COMS 4111"]}'
# Returns real CULPA ratings



⸻

🐛 Common Issues

Q1: Cannot find Colin’s branch

# Check remotes
git remote -v

# You should see:
# origin  https://github.com/ms6998/COMS4995---RAG-Chatbot.git

# Fetch latest
git fetch origin
git branch -r | grep colin
# Should see origin/colin


⸻

Q2: Column names don’t match

The script automatically handles these variants:
	•	professor_name, prof_name, name, professor, instructor
	•	rating, score, rating_score, culpa_rating

If it still doesn’t match, see the troubleshooting section in COLIN_INTEGRATION.md.

⸻

Q3: No data files

# Manually inspect what files are in Colin’s branch
git ls-tree -r --name-only origin/colin | grep documents


⸻

📝 Checklist

Before merging:
	•	Ensure you are on the mingjun branch
	•	git fetch origin colin succeeds
	•	See culpa_ratings.csv in Colin’s branch

After merging:
	•	documents/culpa_ratings.csv exists
	•	File has content (wc -l documents/culpa_ratings.csv)
	•	Processing script runs successfully
	•	Statistics report looks reasonable

Testing:
	•	test_rag.py uses new data
	•	API returns real ratings
	•	Planning features recommend professors using real ratings

⸻

🤝 Next Steps with Colin
	1.	Confirm data format
	•	Tell him which formats your scripts support
	•	Confirm whether additional fields are needed
	2.	Wait for course data
	•	He mentioned having course names and descriptions
	•	Be ready with integrate_spring_courses.py
	3.	Testing and feedback
	•	Test the integrated data
	•	Report any data quality issues

⸻

📚 Related Documentation
	•	COLIN_INTEGRATION.md – Detailed integration guide
	•	INTEGRATION_GUIDE.md – General integration guide
	•	README.md – Full project documentation
	•	PROJECT_SUMMARY.md – Technical summary

⸻

🎉 After Completion

Your system will have:
	•	✅ 150+ real professor ratings
	•	✅ Spring 2025 semester data
	•	✅ Recommendations based on real data
	•	✅ A demo-ready, real-world system

Good luck with the integration! 🚀

If you have questions, check the detailed docs or ask me!

