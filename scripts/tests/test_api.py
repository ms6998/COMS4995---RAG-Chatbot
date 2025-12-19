"""
Simple test script for API endpoints using requests.
Run the server first, then run this script.
"""

import requests
import json


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n=== Testing /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_ask():
    """Test ask endpoint."""
    print("\n=== Testing /ask ===")

    request_data = {
        "question": "What are the core courses for MS in Computer Science?",
        "user_profile": {
            "program": "MS Computer Science",
            "catalog_year": 2023,
            "completed_courses": [],
            "preference": "balanced"
        },
        "top_k": 5
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/ask",
        json=request_data
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nQuestion: {data['question']}")
        print(f"\nAnswer: {data['answer']}")
        print(f"\nSources ({len(data['sources'])}):")
        for i, source in enumerate(data['sources'], 1):
            print(f"  {i}. {source['source']} (similarity: {source['similarity']:.3f})")
            print(f"     {source['text'][:100]}...")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_professors():
    """Test professors endpoint."""
    print("\n=== Testing /professors ===")

    request_data = {
        "course_codes": ["COMS 4111", "COMS 4701", "IEOR 4150"]
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/professors",
        json=request_data
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\nProfessor Ratings:")
        for course_code, professors in data['professors'].items():
            print(f"\n{course_code}:")
            for prof in professors:
                print(f"  • {prof['prof_name']}: {prof['rating']}/5.0 - {prof['tags']}")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_plan():
    """Test plan endpoint."""
    print("\n=== Testing /plan ===")

    request_data = {
        "user_profile": {
            "program": "MS Computer Science",
            "catalog_year": 2023,
            "target_graduation": "Spring 2026",
            "completed_courses": ["COMS 4111"],
            "preference": "best_professors"
        },
        "num_semesters": 3
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/plan",
        json=request_data
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nExplanation: {data['explanation'][:200]}...")
        print(f"\nSemesters ({len(data['semesters'])}):")
        for semester in data['semesters']:
            print(f"\n  {semester['name']} ({semester.get('total_credits', 0)} credits):")
            for course in semester['courses']:
                prof_info = f" - Prof. {course['prof']} ({course['rating']}/5.0)" if course.get('prof') else ""
                print(f"    • {course['course_code']}{prof_info}")
        print(f"\nNotes:")
        for note in data['notes']:
            print(f"  - {note}")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def main():
    """Run all tests."""

    print("="*60)
    print("PathWise API Test Suite")
    print("="*60)
    print("\nMake sure the server is running: python scripts/start_server.py")

    tests = [
        ("Health Check", test_health),
        ("Question Answering", test_ask),
        ("Professor Ratings", test_professors),
        ("Degree Planning", test_plan)
    ]

    results = []

    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\nError in {name}: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
