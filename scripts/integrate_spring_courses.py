#!/usr/bin/env python3
"""
Script to integrate Spring semester course data.
This will process course names, descriptions, and match them with professor ratings.
"""

import sys
from pathlib import Path
import pandas as pd
import json
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_spring_courses(courses_file: str) -> pd.DataFrame:
    """
    Load Spring semester course data.
    
    Expected format (JSON or CSV):
    - course_code: e.g., "COMS 4111"
    - course_name: e.g., "Introduction to Databases"
    - description: Course description text
    - instructor: Professor name(s)
    - credits: Number of credits
    
    Args:
        courses_file: Path to courses data file
        
    Returns:
        DataFrame with course information
    """
    print(f"Loading Spring courses from: {courses_file}")
    
    file_path = Path(courses_file)
    
    if file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif file_path.suffix == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    print(f"Loaded {len(df)} courses")
    print(f"Columns: {df.columns.tolist()}")
    
    return df


def normalize_professor_name(name: str) -> str:
    """
    Normalize professor name for matching.
    
    Args:
        name: Professor name
        
    Returns:
        Normalized name
    """
    if pd.isna(name):
        return ""
    
    # Convert to lowercase
    name = str(name).lower().strip()
    
    # Remove titles
    name = re.sub(r'\b(prof|professor|dr|mr|ms|mrs)\b\.?', '', name)
    
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def match_professors_to_courses(
    courses_df: pd.DataFrame,
    culpa_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Match CULPA professor ratings to course data.
    
    Args:
        courses_df: DataFrame with course information
        culpa_df: DataFrame with professor ratings
        
    Returns:
        Merged DataFrame with courses and ratings
    """
    print("\nMatching professors to courses...")
    
    # Normalize professor names in both dataframes
    courses_df['instructor_normalized'] = courses_df.get('instructor', '').apply(normalize_professor_name)
    culpa_df['professor_normalized'] = culpa_df.get('professor_name', '').apply(normalize_professor_name)
    
    # Merge on normalized names
    merged = courses_df.merge(
        culpa_df,
        left_on='instructor_normalized',
        right_on='professor_normalized',
        how='left'
    )
    
    # Count matches
    matched = merged['rating'].notna().sum()
    total = len(merged)
    print(f"Matched {matched}/{total} courses to professor ratings ({matched/total*100:.1f}%)")
    
    # Clean up
    merged = merged.drop(columns=['instructor_normalized', 'professor_normalized'], errors='ignore')
    
    return merged


def create_course_documents(courses_df: pd.DataFrame, output_dir: str = "data/processed"):
    """
    Create text documents from course data for RAG indexing.
    
    Args:
        courses_df: DataFrame with course information
        output_dir: Directory to save documents
    """
    print("\nCreating course documents...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create one document per course
    documents = []
    
    for idx, row in courses_df.iterrows():
        course_code = row.get('course_code', 'UNKNOWN')
        course_name = row.get('course_name', '')
        description = row.get('description', '')
        instructor = row.get('instructor', '')
        credits = row.get('credits', '')
        rating = row.get('rating', None)
        
        # Build document text
        doc_text = f"Course: {course_code} - {course_name}\n\n"
        
        if instructor:
            doc_text += f"Instructor: {instructor}"
            if rating and not pd.isna(rating):
                doc_text += f" (CULPA Rating: {rating:.2f}/5.0)"
            doc_text += "\n\n"
        
        if credits:
            doc_text += f"Credits: {credits}\n\n"
        
        if description:
            doc_text += f"Description:\n{description}\n"
        
        documents.append({
            'course_code': course_code,
            'text': doc_text,
            'metadata': {
                'course_code': course_code,
                'course_name': course_name,
                'instructor': instructor,
                'credits': credits,
                'rating': rating if not pd.isna(rating) else None,
                'semester': 'Spring 2025',
                'doc_type': 'course_description'
            }
        })
    
    # Save as JSON
    output_file = output_path / "spring_courses.json"
    with open(output_file, 'w') as f:
        json.dump(documents, indent=2, fp=f)
    
    print(f"Created {len(documents)} course documents")
    print(f"Saved to: {output_file}")
    
    # Also save as text files for easy reading
    text_dir = output_path / "spring_courses_txt"
    text_dir.mkdir(exist_ok=True)
    
    for doc in documents[:10]:  # Save first 10 as examples
        course_code = doc['course_code'].replace(' ', '_')
        text_file = text_dir / f"{course_code}.txt"
        with open(text_file, 'w') as f:
            f.write(doc['text'])
    
    print(f"Saved example text files to: {text_dir}")
    
    return documents


def create_combined_index_config(
    culpa_csv: str,
    courses_json: str,
    output_config: str = "data/combined_index_config.json"
):
    """
    Create index configuration for both CULPA ratings and course data.
    
    Args:
        culpa_csv: Path to CULPA ratings CSV
        courses_json: Path to courses JSON
        output_config: Path to save config
    """
    config = {
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 600,
        "chunk_overlap": 100,
        "vector_db": {
            "type": "chroma",
            "persist_directory": "./vector_db"
        },
        "professor_ratings": {
            "collection_name": "culpa_professor_ratings",
            "ratings_file": culpa_csv
        },
        "course_descriptions": {
            "collection_name": "spring_courses",
            "courses_file": courses_json
        }
    }
    
    with open(output_config, 'w') as f:
        json.dump(config, indent=2, fp=f)
    
    print(f"\nCreated combined index config: {output_config}")


def generate_course_statistics(courses_df: pd.DataFrame):
    """
    Generate statistics about the course data.
    
    Args:
        courses_df: DataFrame with course information
    """
    print("\n" + "=" * 60)
    print("Spring Semester Course Statistics")
    print("=" * 60)
    
    print(f"\nTotal Courses: {len(courses_df)}")
    
    # Courses with ratings
    if 'rating' in courses_df.columns:
        with_ratings = courses_df['rating'].notna().sum()
        print(f"Courses with Professor Ratings: {with_ratings} ({with_ratings/len(courses_df)*100:.1f}%)")
        
        if with_ratings > 0:
            print(f"\nRating Statistics (for matched courses):")
            print(f"  Mean:   {courses_df['rating'].mean():.2f}")
            print(f"  Median: {courses_df['rating'].median():.2f}")
            print(f"  Min:    {courses_df['rating'].min():.2f}")
            print(f"  Max:    {courses_df['rating'].max():.2f}")
    
    # Department distribution
    if 'course_code' in courses_df.columns:
        courses_df['department'] = courses_df['course_code'].str.extract(r'^([A-Z]+)')[0]
        dept_counts = courses_df['department'].value_counts().head(10)
        print(f"\nTop 10 Departments:")
        for dept, count in dept_counts.items():
            print(f"  {dept}: {count} courses")
    
    print("=" * 60)


def main():
    """Main function."""
    print("=" * 60)
    print("Spring Semester Course Integration")
    print("=" * 60)
    
    # Check for required files
    culpa_csv = "data/processed/culpa_ratings_processed.csv"
    
    if not Path(culpa_csv).exists():
        print(f"\nError: Processed CULPA ratings not found: {culpa_csv}")
        print("Please run process_culpa_data.py first:")
        print("  python scripts/process_culpa_data.py")
        sys.exit(1)
    
    # Get courses file from command line or use default
    if len(sys.argv) > 1:
        courses_file = sys.argv[1]
    else:
        # Look for common filenames
        possible_files = [
            "documents/spring_courses.json",
            "documents/spring_courses.csv",
            "data/raw/spring_courses.json",
            "data/raw/spring_courses.csv"
        ]
        
        courses_file = None
        for f in possible_files:
            if Path(f).exists():
                courses_file = f
                break
        
        if not courses_file:
            print("\nError: Spring courses file not found")
            print("Please provide the path as an argument:")
            print(f"  python {sys.argv[0]} path/to/spring_courses.json")
            print("\nExpected file format (JSON or CSV) with columns:")
            print("  - course_code")
            print("  - course_name")
            print("  - description")
            print("  - instructor")
            print("  - credits")
            sys.exit(1)
    
    try:
        # Load data
        culpa_df = pd.read_csv(culpa_csv)
        courses_df = load_spring_courses(courses_file)
        
        # Match professors to courses
        merged_df = match_professors_to_courses(courses_df, culpa_df)
        
        # Generate statistics
        generate_course_statistics(merged_df)
        
        # Create course documents
        documents = create_course_documents(merged_df)
        
        # Create combined index config
        create_combined_index_config(
            culpa_csv,
            "data/processed/spring_courses.json"
        )
        
        print("\n" + "=" * 60)
        print("✓ Integration complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the course documents:")
        print("   cat data/processed/spring_courses.json")
        print("\n2. Build the combined index:")
        print("   python scripts/build_index.py data/combined_index_config.json")
        print("\n3. Update API to use new data")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



