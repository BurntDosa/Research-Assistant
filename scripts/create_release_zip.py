#!/usr/bin/env python3
"""
Script to create a release ZIP file for Research Assistant.
This ZIP file includes all necessary files for users to download and run the project.
"""

import os
import zipfile
from pathlib import Path

def create_release_zip(repo_path, output_path, version="v1.0.1"):
    """
    Create a release ZIP file with all project files.
    
    Args:
        repo_path: Path to the repository root
        output_path: Path where the ZIP file should be created
        version: Version string for the release
    """
    # Define files and directories to exclude
    exclude_patterns = {
        '.git',
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        '.env',  # Exclude actual .env files (but include .env.example)
        '.vscode',
        '.idea',
        '*.egg-info',
        'dist',
        'build',
        '.pytest_cache',
        '.mypy_cache',
    }
    
    # Files that should be included (if they exist)
    include_files = {
        'README.md',
        'LICENSE',
        'requirements.txt',
        'main.py',
        '.env.example',
        '.gitignore',
        'CHANGELOG.md',
        'RELEASE_NOTES.md',
        'SECURITY.md',
        'API_KEY_INCIDENT.md',
        'IMMEDIATE_ACTION_REQUIRED.md',
    }
    
    repo_path = Path(repo_path)
    zip_name = f"Research-Assistant-{version}.zip"
    zip_path = Path(output_path) / zip_name
    
    print(f"Creating release ZIP: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # First, explicitly add root-level important files that start with dot
        root_dot_files = ['.env.example', '.gitignore']
        for dot_file in root_dot_files:
            dot_file_path = repo_path / dot_file
            if dot_file_path.exists():
                arcname = f"Research-Assistant/{dot_file}"
                zipf.write(dot_file_path, arcname)
                print(f"  Added: {arcname}")
        
        # Add all other files and package structure
        for root, dirs, files in os.walk(repo_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns and not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(repo_path)
                
                # Skip the zip file itself if it exists in the repo
                if file.endswith('.zip'):
                    continue
                
                # Skip excluded files
                if any(pattern in str(rel_path) for pattern in exclude_patterns):
                    continue
                if file.endswith(('.pyc', '.pyo', '.pyd')):
                    continue
                # Allow .env.example and .gitignore but skip other dot files
                if file.startswith('.') and file not in {'.env.example', '.gitignore'}:
                    continue
                
                # Add file to zip with proper folder structure
                arcname = f"Research-Assistant/{rel_path}"
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print(f"\n✅ Release ZIP created successfully: {zip_path}")
    print(f"📦 ZIP size: {zip_path.stat().st_size / (1024*1024):.2f} MB")
    
    return zip_path


if __name__ == "__main__":
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = sys.argv[2] if len(sys.argv) > 2 else "."
    version = sys.argv[3] if len(sys.argv) > 3 else "v1.0.1"
    
    create_release_zip(repo_path, output_path, version)
