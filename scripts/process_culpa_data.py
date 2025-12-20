#!/usr/bin/env python3
"""
Script to process CULPA ratings data and prepare it for indexing.
This script handles the culpa_ratings.csv file with real professor ratings.
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_culpa_ratings(csv_path: str) -> pd.DataFrame:
    """
    Load CULPA ratings from CSV file.

    Expected format (from Colin's scraping):
    - professor_name (or prof_name, or name)
    - rating (or score)

    Args:
        csv_path: Path to culpa_ratings.csv

    Returns:
        DataFrame with professor ratings
    """
    print(f"Loading CULPA ratings from: {csv_path}")
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df)} professor ratings")
    print(f"Columns: {df.columns.tolist()}")

    # Normalize column names to handle different formats
    column_mapping = {}

    # Map professor name column
    for col in ["prof_name", "name", "professor", "instructor"]:
        if col in df.columns:
            column_mapping[col] = "professor_name"
            break

    # Map rating column
    for col in ["score", "rating_score", "culpa_rating"]:
        if col in df.columns:
            column_mapping[col] = "rating"
            break

    if column_mapping:
        df = df.rename(columns=column_mapping)
        print(f"Renamed columns: {column_mapping}")

    return df


def process_culpa_ratings(df: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
    """
    Process and clean CULPA ratings data from Colin's scraping.

    Format: professor_name, rating (two columns only)

    Args:
        df: Input DataFrame
        output_path: Optional path to save processed data

    Returns:
        Processed DataFrame
    """
    print("\nProcessing CULPA ratings...")

    # Check for required columns
    required_cols = ['professor_name', 'rating']
    for col in required_cols:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found")
            print(f"Available columns: {df.columns.tolist()}")
            print("\nPlease ensure the CSV has 'professor_name' and 'rating' columns")
            raise ValueError(f"Missing required column: {col}")

    # Clean data
    df_clean = df.copy()

    # Clean professor names
    if 'professor_name' in df_clean.columns:
        # Remove leading/trailing whitespace
        df_clean['professor_name'] = df_clean['professor_name'].str.strip()
        # Remove empty names
        df_clean = df_clean[df_clean['professor_name'].notna()]
        df_clean = df_clean[df_clean['professor_name'] != '']

    # Remove rows with missing ratings
    if 'rating' in df_clean.columns:
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=['rating'])
        print(f"Removed {initial_count - len(df_clean)} rows with missing ratings")

    # Convert rating to float and validate range
    if 'rating' in df_clean.columns:
        df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')
        df_clean = df_clean.dropna(subset=['rating'])

        # CULPA ratings should be 0-5
        invalid_ratings = df_clean[(df_clean['rating'] < 0) | (df_clean['rating'] > 5)]
        if len(invalid_ratings) > 0:
            print(f"Warning: Found {len(invalid_ratings)} ratings outside 0-5 range")
            print(f"  Will clamp to valid range")
            df_clean['rating'] = df_clean['rating'].clip(0, 5)

    # Add empty columns for future integration
    if 'course_code' not in df_clean.columns:
        df_clean['course_code'] = ''
    if 'tags' not in df_clean.columns:
        df_clean['tags'] = ''
    if 'semester' not in df_clean.columns:
        df_clean['semester'] = 'Spring 2025'  # Based on Colin's scraping

    # Remove duplicates (same professor, keep highest rating)
    if len(df_clean) > len(df_clean['professor_name'].unique()):
        print(f"\nFound duplicate professors, keeping highest rating for each")
        df_clean = df_clean.sort_values('rating', ascending=False)
        df_clean = df_clean.drop_duplicates(subset=['professor_name'], keep='first')

    # Statistics
    if 'rating' in df_clean.columns:
        print(f"\nRating statistics:")
        print(f"  Total professors: {len(df_clean)}")
        print(f"  Mean rating: {df_clean['rating'].mean():.2f}")
        print(f"  Median rating: {df_clean['rating'].median():.2f}")
        print(f"  Min rating: {df_clean['rating'].min():.2f}")
        print(f"  Max rating: {df_clean['rating'].max():.2f}")
        print(f"  Std deviation: {df_clean['rating'].std():.2f}")

        # Rating distribution
        print(f"\n  Ratings >= 4.0: {len(df_clean[df_clean['rating'] >= 4.0])} ({len(df_clean[df_clean['rating'] >= 4.0])/len(df_clean)*100:.1f}%)")
        print(f"  Ratings 3.0-3.9: {len(df_clean[(df_clean['rating'] >= 3.0) & (df_clean['rating'] < 4.0)])}")
        print(f"  Ratings < 3.0: {len(df_clean[df_clean['rating'] < 3.0])}")

    # Save processed data
    if output_path:
        df_clean.to_csv(output_path, index=False)
        print(f"\nSaved processed data to: {output_path}")

    return df_clean


def match_courses_to_professors(
    culpa_df: pd.DataFrame,
    courses_data: dict = None
) -> pd.DataFrame:
    """
    Match course codes to professors if course data is available.

    Args:
        culpa_df: DataFrame with professor ratings
        courses_data: Optional dict with course information

    Returns:
        DataFrame with course_code column added
    """
    print("\nMatching courses to professors...")

    # If we have course data, try to match
    if courses_data:
        # This would be implemented based on the structure of courses_data
        # For now, we'll add a placeholder
        print("Course matching not yet implemented")
        print("Will need course data structure from Spring semester scraping")

    # For now, if no course_code column, add empty one
    if 'course_code' not in culpa_df.columns:
        culpa_df['course_code'] = ''
        print("Added empty course_code column (to be filled later)")

    return culpa_df


def create_professor_index_config(
    culpa_csv_path: str,
    output_config_path: str = "data/culpa_index_config.json"
):
    """
    Create an index configuration file for CULPA ratings.

    Args:
        culpa_csv_path: Path to processed CULPA CSV
        output_config_path: Path to save config JSON
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
            "ratings_file": culpa_csv_path
        }
    }

    with open(output_config_path, 'w') as f:
        json.dump(config, indent=2, fp=f)

    print(f"\nCreated index config: {output_config_path}")
    print("To build the index, run:")
    print(f"  python scripts/build_index.py {output_config_path}")


def generate_statistics_report(df: pd.DataFrame, output_path: str = None):
    """
    Generate a statistics report for the CULPA ratings.

    Args:
        df: DataFrame with professor ratings
        output_path: Optional path to save report
    """
    report = []
    report.append("=" * 60)
    report.append("CULPA Ratings Statistics Report")
    report.append("=" * 60)
    report.append(f"\nTotal Professors: {len(df)}")

    if 'rating' in df.columns:
        report.append(f"\nRating Distribution:")
        report.append(f"  Mean:   {df['rating'].mean():.2f}")
        report.append(f"  Median: {df['rating'].median():.2f}")
        report.append(f"  Std:    {df['rating'].std():.2f}")
        report.append(f"  Min:    {df['rating'].min():.2f}")
        report.append(f"  Max:    {df['rating'].max():.2f}")

        # Rating ranges
        report.append(f"\nRating Ranges:")
        for lower in [0, 1, 2, 3, 4]:
            upper = lower + 1
            count = len(df[(df['rating'] >= lower) & (df['rating'] < upper)])
            pct = count / len(df) * 100
            report.append(f"  {lower}.0-{upper}.0: {count:4d} ({pct:5.1f}%)")

        # Top rated professors
        report.append(f"\nTop 10 Rated Professors:")
        top_profs = df.nlargest(10, 'rating')
        for idx, row in top_profs.iterrows():
            prof_name = row.get('professor_name', 'Unknown')
            rating = row.get('rating', 0)
            report.append(f"  {prof_name}: {rating:.2f}")

    if 'course_code' in df.columns and df['course_code'].notna().any():
        report.append(f"\nCourses with Ratings: {df['course_code'].notna().sum()}")

    report.append("\n" + "=" * 60)

    report_text = "\n".join(report)
    print(report_text)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(report_text)
        print(f"\nReport saved to: {output_path}")


def main():
    """Main function."""
    print("=" * 60)
    print("CULPA Ratings Data Processor")
    print("=" * 60)

    # Default paths
    culpa_csv = "documents/culpa_ratings.csv"
    processed_csv = "data/processed/culpa_ratings_processed.csv"
    report_path = "data/processed/culpa_statistics.txt"

    # Check if input file exists
    if not Path(culpa_csv).exists():
        print(f"\nError: CULPA ratings file not found: {culpa_csv}")
        print("\nPlease ensure culpa_ratings.csv is in the documents/ folder")
        print("Or provide the path as an argument:")
        print(f"  python {sys.argv[0]} path/to/culpa_ratings.csv")
        sys.exit(1)

    # Allow custom path from command line
    if len(sys.argv) > 1:
        culpa_csv = sys.argv[1]

    try:
        # Create output directory
        Path("data/processed").mkdir(parents=True, exist_ok=True)

        # Load data
        df = load_culpa_ratings(culpa_csv)

        # Process data
        df_processed = process_culpa_ratings(df, processed_csv)

        # Match courses (if available)
        df_processed = match_courses_to_professors(df_processed)

        # Generate statistics
        generate_statistics_report(df_processed, report_path)

        # Create index config
        create_professor_index_config(processed_csv)

        print("\n" + "=" * 60)
        print("✓ Processing complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the processed data:")
        print(f"   cat {processed_csv}")
        print("\n2. Build the vector index:")
        print("   python scripts/build_index.py data/culpa_index_config.json")
        print("\n3. Test the system:")
        print("   python scripts/tests/test_rag.py")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
