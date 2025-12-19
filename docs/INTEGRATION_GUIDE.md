# CULPA Data and Spring Course Integration Guide

This guide explains how to integrate the real CULPA rating data and Spring course information added by your classmate.

## 📊 Work Already Completed by Your Classmate

According to Pull Request #1, your classmate has:

1. ✅ Retrieved real professor rating data from Columbia CULPA  
2. ✅ Created the `culpa_ratings.csv` file (containing professor names and ratings)  
3. ✅ Obtained the Spring semester course list (including course names and descriptions)

## 🔄 Integration Steps

### Step 1: Process CULPA Rating Data

```bash
# Make sure culpa_ratings.csv is in the documents/ folder
ls documents/culpa_ratings.csv

# Run the processing script
python scripts/process_culpa_data.py

# This will:
# - Clean and validate the data
# - Generate a statistics report
# - Create a processed CSV file
# - Generate an index configuration file

Output files:
	•	data/processed/culpa_ratings_processed.csv – cleaned rating data
	•	data/processed/culpa_statistics.txt – statistics report
	•	data/culpa_index_config.json – index configuration

Step 2: Integrate Spring Course Data

If your classmate has already provided the Spring course data file:

# Assume course data is in documents/spring_courses.json
python scripts/integrate_spring_courses.py documents/spring_courses.json

# This will:
# - Load course information (course code, name, description, professor)
# - Match courses with CULPA ratings
# - Create course documents for the RAG index
# - Generate a combined index configuration

Expected course data format (JSON or CSV):

[
  {
    "course_code": "COMS 4111",
    "course_name": "Introduction to Databases",
    "description": "Introduction to database systems...",
    "instructor": "John Smith",
    "credits": 3
  }
]

Or CSV:

course_code,course_name,description,instructor,credits
COMS 4111,Introduction to Databases,"Introduction to...",John Smith,3

Step 3: Build the New Vector Index

# Build index using only CULPA data
python scripts/build_index.py data/culpa_index_config.json

# Or, if course data is included, use the combined config
python scripts/build_index.py data/combined_index_config.json

Step 4: Test the New Data

# Test the RAG system
python scripts/test_rag.py

# Start the API server
python scripts/start_server.py

# Test the API
python tests/test_api.py

📝 Data Format Notes

CULPA Rating Data Format

Your classmate’s culpa_ratings.csv should contain:

professor_name,rating
John Smith,4.8
Jane Doe,4.5
...

Optional fields (if available):
	•	course_code – course code
	•	tags – student feedback tags
	•	num_reviews – number of reviews

Spring Course Data Format

Data obtained from the Columbia course catalog should include:

Required fields:
	•	course_code – course code (e.g., “COMS 4111”)
	•	course_name – course name
	•	instructor – professor name

Optional fields:
	•	description – course description
	•	credits – number of credits
	•	prerequisites – prerequisites
	•	schedule – class time
	•	location – class location

🔧 Customizing Processing Scripts

If your data format differs, you can modify process_culpa_data.py:

# In the load_culpa_ratings function
def load_culpa_ratings(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Rename columns if they differ
    df = df.rename(columns={
        'prof_name': 'professor_name',  # if original column is prof_name
        'score': 'rating'               # if original column is score
    })

    return df

📊 Viewing Data Statistics

After processing, view the statistics report:

# CULPA rating statistics
cat data/processed/culpa_statistics.txt

Example output:

============================================================
CULPA Ratings Statistics Report
============================================================
Total Professors: 150

Rating Distribution:
  Mean:   4.12
  Median: 4.20
  Std:    0.45
  Min:    2.80
  Max:    5.00
...

🔗 Integrating the New Data into the API

The new data will be automatically integrated into existing API endpoints.

1. Query Professor Ratings

curl -X POST "http://localhost:8000/professors" \
  -H "Content-Type: application/json" \
  -d '{
    "course_codes": ["COMS 4111", "COMS 4701"]
  }'

This will now return real CULPA ratings.

2. Query Spring Courses

If course data is integrated:

curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What courses are offered in Spring 2025 for machine learning?"
  }'

3. Generate a Plan (with Real Ratings)

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

This will now recommend professors using real CULPA ratings.

🎯 Next Steps

Priority 1: Complete Data Integration
	•	Verify culpa_ratings.csv format
	•	Run process_culpa_data.py
	•	Review statistics report
	•	Rebuild the vector index

Priority 2: Add Spring Courses
	•	Obtain Spring course data file from your classmate
	•	Verify data format (JSON or CSV)
	•	Run integrate_spring_courses.py
	•	Validate course–professor matching

Priority 3: Add Degree Requirement Documents
	•	Obtain official degree requirement PDF/HTML
	•	Place in data/raw/ folder
	•	Update index_config.json
	•	Rebuild index

🐛 Common Issues

Q1: CULPA Data Column Name Mismatch

Issue: KeyError: 'professor_name'

Solution:

df = df.rename(columns={
    'prof': 'professor_name',
    'score': 'rating'
})

Q2: Professor Names Do Not Match

Issue: Courses and ratings cannot be matched
Cause: Inconsistent name formats (“John Smith” vs. “Smith, John”)
Solution: Use normalize_professor_name or manually clean data

Q3: Inconsistent Course Code Formats

Issue: “COMS4111” vs. “COMS 4111”
Solution:

def normalize_course_code(code):
    code = code.replace(' ', '')
    return re.sub(r'([A-Z]+)(\d+)', r'\1 \2', code)

Q4: Large Data Causes Slow Indexing

Solution:

CHUNK_SIZE = 400
batch_size = 16

📞 Collaboration Suggestions

Coordinating with Your Classmate
	1.	Standardize data formats:
	•	Column names
	•	Course code formats
	•	Professor name formats
	2.	Division of labor:
	•	You: RAG system and API
	•	Classmate: data scraping and cleaning
	•	Joint: data integration and testing
	3.	Git workflow:

git pull origin main
python scripts/process_culpa_data.py
git add .
git commit -m "Integrate CULPA ratings data"
git push origin mingjun



📚 Reference Files
	•	scripts/process_culpa_data.py – CULPA data processing
	•	scripts/integrate_spring_courses.py – course data integration
	•	src/rag/indexer.py – index building logic
	•	src/api/app.py – API endpoints

🎉 Final Result

After integration, your system will:
	1.	✅ Use real CULPA ratings (150+ professors)
	2.	✅ Include Spring semester course information
	3.	✅ Accurately match courses and professors
	4.	✅ Provide recommendations based on real data

This will significantly improve the project’s practicality and demo quality.

⸻

If you have questions, refer to this guide or ask for help. Good luck with the integration.
