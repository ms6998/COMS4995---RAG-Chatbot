#!/usr/bin/env python3
"""
Script to test the RAG system with sample queries.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import create_vector_store
from src.rag.retriever import RAGRetriever, ProfessorRatingsRetriever


def test_requirements_retrieval():
    """Test degree requirements retrieval."""
    print("\n" + "="*60)
    print("Testing Degree Requirements Retrieval")
    print("="*60)

    # Initialize components
    print("\nInitializing embedder...")
    embedder = EmbeddingGenerator()

    print("Connecting to vector store...")
    vector_store = create_vector_store(
        store_type="chroma",
        collection_name="degree_requirements",
        embedding_dim=embedder.embedding_dim,
        persist_directory="./vector_db"
    )

    print("Creating retriever...")
    retriever = RAGRetriever(embedder, vector_store, top_k=3)

    # Test queries
    test_queries = [
        "What are the core courses for MS in Computer Science?",
        "How many credits are required for the Data Science program?",
        "What is the GPA requirement for graduation?",
        "Can I transfer credits from another university?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Q: {query}")

        results = retriever.retrieve(query, k=3)

        if results:
            print(f"\nFound {len(results)} relevant documents:")
            for j, result in enumerate(results, 1):
                print(f"\n{j}. Similarity: {result['similarity']:.3f}")
                print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
                print(f"   Program: {result['metadata'].get('program', 'N/A')}")
                print(f"   Text: {result['text'][:150]}...")
        else:
            print("No results found.")

    # Test context formatting
    print(f"\n--- Context Formatting Test ---")
    query = test_queries[0]
    results = retriever.retrieve(query, k=2)
    context = retriever.format_context_for_llm(results)
    print(f"\nFormatted context for: {query}")
    print(context[:500] + "...\n")


def test_professor_ratings():
    """Test professor ratings retrieval."""
    print("\n" + "="*60)
    print("Testing Professor Ratings Retrieval")
    print("="*60)

    # Initialize components
    print("\nInitializing embedder...")
    embedder = EmbeddingGenerator()

    print("Connecting to professor ratings store...")
    vector_store = create_vector_store(
        store_type="chroma",
        collection_name="professor_ratings",
        embedding_dim=embedder.embedding_dim,
        persist_directory="./vector_db"
    )

    print("Creating professor retriever...")
    prof_retriever = ProfessorRatingsRetriever(embedder, vector_store)

    # Test courses
    test_courses = ["COMS 4111", "COMS 4701", "IEOR 4150"]

    for course_code in test_courses:
        print(f"\n--- {course_code} ---")
        professors = prof_retriever.get_professors_for_course(course_code, k=3)

        if professors:
            print(f"Found {len(professors)} professors:")
            for prof in professors:
                print(f"  • {prof_retriever.format_professor_info(prof)}")
        else:
            print(f"No ratings found for {course_code}")

    # Test best professor selection
    print(f"\n--- Best Professors ---")
    for course_code in test_courses:
        best = prof_retriever.get_best_professor_for_course(course_code)
        if best:
            print(f"{course_code}: {prof_retriever.format_professor_info(best)}")


def main():
    """Main function."""
    print("\n" + "="*60)
    print("PathWise RAG System Test")
    print("="*60)

    # Check if indices exist
    vector_db_path = Path("./vector_db")
    if not vector_db_path.exists():
        print("\n✗ Error: Vector database not found!")
        print("Please run 'python scripts/build_index.py' first to build the indices.")
        sys.exit(1)

    try:
        # Run tests
        test_requirements_retrieval()
        test_professor_ratings()

        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



