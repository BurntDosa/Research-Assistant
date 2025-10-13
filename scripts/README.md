# Release Scripts

This directory contains scripts for creating release packages.

## create_release_zip.py

Creates a distributable ZIP file of the Research Assistant project.

### Usage

```bash
python scripts/create_release_zip.py [repo_path] [output_path] [version]
```

**Arguments:**
- `repo_path` - Path to the repository root (default: current directory)
- `output_path` - Path where the ZIP file should be created (default: current directory)
- `version` - Version string for the release (default: v1.0.1)

**Example:**

```bash
# Create a release zip in the current directory
python scripts/create_release_zip.py . . v1.0.1

# Create a release zip for v1.0.2
python scripts/create_release_zip.py . . v1.0.2
```

### What's Included in the ZIP

The script includes:
- All Python source files (`.py`)
- Documentation files (`.md`, `LICENSE`)
- Configuration files (`requirements.txt`, `.env.example`, `.gitignore`)
- All package structure and `__init__.py` files

### What's Excluded

The script excludes:
- `.git` directory and git files
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`venv/`, `.venv/`)
- IDE-specific files (`.vscode/`, `.idea/`)
- Actual environment files (`.env`, but includes `.env.example`)
- Build artifacts and distributions
- Other temporary files

### Output

The script creates a ZIP file named `Research-Assistant-{version}.zip` containing all files in a `Research-Assistant/` subdirectory, ready for distribution.

Example output structure:
```
Research-Assistant-v1.0.1.zip
└── Research-Assistant/
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── LICENSE
    ├── main.py
    ├── requirements.txt
    ├── src/
    │   ├── agents/
    │   ├── apps/
    │   └── utils/
    └── ...
```

## Notes

- Always test the generated ZIP by extracting it and verifying the contents
- The ZIP size is typically around 110-120 KB (compressed)
- Make sure to update the version number for each new release
- See `RELEASE_ZIP_CONTENTS.md` for detailed information about the release package
