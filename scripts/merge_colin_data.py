#!/usr/bin/env python3
"""
Script to merge Colin's data from his branch into the RAG system.
This script helps integrate data from the 'colin' branch.
"""

import sys
import subprocess
from pathlib import Path
import json

def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def check_git_status():
    """Check if we're in a git repo and on the right branch."""
    try:
        result = run_command("git branch --show-current", check=False)
        current_branch = result.stdout.strip()
        print(f"Current branch: {current_branch}")
        return current_branch
    except Exception as e:
        print(f"Error checking git status: {e}")
        return None


def fetch_colin_branch():
    """Fetch Colin's branch."""
    print("\n" + "="*60)
    print("Fetching Colin's branch...")
    print("="*60)
    
    try:
        run_command("git fetch origin colin")
        print("✓ Successfully fetched colin branch")
        return True
    except Exception as e:
        print(f"✗ Error fetching colin branch: {e}")
        return False


def list_colin_files():
    """List files in Colin's branch."""
    print("\n" + "="*60)
    print("Files in Colin's branch:")
    print("="*60)
    
    try:
        result = run_command("git ls-tree -r --name-only origin/colin", check=False)
        files = result.stdout.strip().split('\n')
        
        # Filter for relevant files
        relevant_files = []
        for f in files:
            if 'documents/' in f or 'culpa' in f.lower() or 'course' in f.lower():
                relevant_files.append(f)
                print(f"  {f}")
        
        return relevant_files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []


def copy_file_from_colin(file_path):
    """Copy a specific file from Colin's branch."""
    try:
        cmd = f"git checkout origin/colin -- {file_path}"
        run_command(cmd)
        print(f"✓ Copied: {file_path}")
        return True
    except Exception as e:
        print(f"✗ Error copying {file_path}: {e}")
        return False


def show_file_diff(file_path):
    """Show differences for a file."""
    try:
        cmd = f"git show origin/colin:{file_path}"
        result = run_command(cmd, check=False)
        return result.stdout
    except Exception as e:
        print(f"Error showing diff: {e}")
        return None


def interactive_merge():
    """Interactive merge process."""
    print("\n" + "="*60)
    print("Colin Data Integration Tool")
    print("="*60)
    
    # Check git status
    current_branch = check_git_status()
    if not current_branch:
        print("\nError: Not in a git repository")
        return
    
    if current_branch != "mingjun":
        print(f"\nWarning: You're on branch '{current_branch}', not 'mingjun'")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Fetch Colin's branch
    if not fetch_colin_branch():
        return
    
    # List files
    files = list_colin_files()
    
    if not files:
        print("\nNo relevant files found in colin branch")
        return
    
    print(f"\nFound {len(files)} relevant files")
    
    # Look for specific data files
    data_files = {
        'culpa_ratings': None,
        'spring_courses': None
    }
    
    for f in files:
        if 'culpa' in f.lower() and f.endswith('.csv'):
            data_files['culpa_ratings'] = f
        elif 'course' in f.lower() and (f.endswith('.json') or f.endswith('.csv')):
            data_files['spring_courses'] = f
    
    print("\n" + "="*60)
    print("Data Files Found:")
    print("="*60)
    
    for key, path in data_files.items():
        if path:
            print(f"  {key}: {path}")
        else:
            print(f"  {key}: NOT FOUND")
    
    # Copy files
    print("\n" + "="*60)
    print("Copying Files")
    print("="*60)
    
    copied_files = []
    
    for key, path in data_files.items():
        if path:
            response = input(f"\nCopy {path}? (y/n): ")
            if response.lower() == 'y':
                if copy_file_from_colin(path):
                    copied_files.append(path)
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Copied {len(copied_files)} files:")
    for f in copied_files:
        print(f"  ✓ {f}")
    
    # Next steps
    if data_files['culpa_ratings']:
        print("\n" + "="*60)
        print("Next Steps")
        print("="*60)
        print("\n1. Process CULPA ratings:")
        print(f"   python scripts/process_culpa_data.py {data_files['culpa_ratings']}")
        
        if data_files['spring_courses']:
            print("\n2. Integrate spring courses:")
            print(f"   python scripts/integrate_spring_courses.py {data_files['spring_courses']}")
        
        print("\n3. Rebuild index:")
        print("   python scripts/build_index.py data/culpa_index_config.json")
        
        print("\n4. Test the system:")
        print("   python scripts/test_rag.py")


def quick_merge():
    """Quick merge without interaction."""
    print("Quick merge mode...")
    
    # Fetch
    if not fetch_colin_branch():
        return
    
    # Try to copy common file locations
    common_paths = [
        "documents/culpa_ratings.csv",
        "documents/spring_courses.json",
        "data/culpa_ratings.csv"
    ]
    
    copied = []
    for path in common_paths:
        try:
            if copy_file_from_colin(path):
                copied.append(path)
        except:
            pass
    
    if copied:
        print(f"\n✓ Copied {len(copied)} files")
        for f in copied:
            print(f"  {f}")
    else:
        print("\n✗ No files found at common locations")
        print("Try interactive mode: python scripts/merge_colin_data.py --interactive")


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--interactive', '-i']:
        interactive_merge()
    else:
        # Check if in git repo
        if not check_git_status():
            print("Error: Not in a git repository")
            print("Run this script from the project root")
            sys.exit(1)
        
        print("Colin Data Merge Tool")
        print("\nOptions:")
        print("  1. Quick merge (automatic)")
        print("  2. Interactive merge (choose files)")
        print("  3. List files only")
        print("  4. Exit")
        
        choice = input("\nChoice (1-4): ")
        
        if choice == '1':
            quick_merge()
        elif choice == '2':
            interactive_merge()
        elif choice == '3':
            if fetch_colin_branch():
                list_colin_files()
        else:
            print("Exiting...")


if __name__ == "__main__":
    main()


