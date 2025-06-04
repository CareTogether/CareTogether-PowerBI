import sys 
import subprocess
from pathlib import Path

def validate_structure():
    base_path = Path('.')
    
    required_paths = [
        base_path / 'CareTogether.Report',
        base_path / 'CareTogether.Report' / '.pbi',
        base_path / 'CareTogether.Report' / 'definition',
        base_path / 'CareTogether.Report' / 'StaticResources',
        base_path / 'CareTogether.Report' / '.platform',
        base_path / 'CareTogether.Report' / 'definition.pbir',
        base_path / 'CareTogether.SemanticModel',
        base_path / 'CareTogether.SemanticModel' / '.pbi',
        base_path / 'CareTogether.SemanticModel' / 'definition',
        base_path / 'CareTogether.SemanticModel' / '.platform',
        base_path / 'CareTogether.SemanticModel' / 'definition.pbism',
        base_path / 'CareTogether.SemanticModel' / 'diagramLayout.json',
        base_path / 'CareTogether.pbip'
    ]

    missing_paths = []

    for path in required_paths:
        if not path.exists():
            missing_paths.append(str(path))

    if missing_paths:
        print('❌ Invalid structure. The following. Missing paths:')
        for m in missing_paths:
            print(f" - {m}")
            sys.exit(1)
    else:
        print('✅ Project structure is correct.')

def is_git_ignored(filepath: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "check-ignore", str(filepath)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and result.stdout.strip() == str(filepath)
    except Exception as e:
        print(f"⚠️ Warning: Could not check git ignore status for {filepath}: {e}")
        return False

def check_file_integrity():
    root_path = Path(".")
    search_paths = [
        root_path / "CareTogether.Report",
        root_path / "CareTogether.SemanticModel",
    ]

    file_types = {
        "tmdl": [],
        "json": [],
        "pbism": [],
        "pbip": [],
    }

    file_types["pbip"].extend(root_path.glob("*.pbip"))

    for base in search_paths:
        if not base.exists():
            print(f"⚠️ Warning: Directory not found: {base.resolve()}")
            continue
        for ext in ("tmdl", "json", "pbism"):
            file_types[ext].extend(base.rglob(f"*.{ext}"))

    # Filtra arquivos ignorados pelo git
    for ext in file_types:
        files = file_types[ext]
        filtered = [f for f in files if not is_git_ignored(f)]
        file_types[ext] = filtered

    total_errors = 0

    for ext, files in file_types.items():
        print(f"\n🔍 Checking .{ext} files...")
        errors = 0

        if not files:
            print(f"⚠️ No .{ext} files found.")
            continue

        for file in files:
            try:
                content = file.read_text(encoding="utf-8").strip()
                if len(content) < 10:
                    print(f"⚠️ File too small or empty: {file}")
                    errors += 1
            except Exception as e:
                print(f"❌ Failed to read {file}: {e}")
                errors += 1

        if errors > 0:
            print(f"❌ {errors} issue(s) found in .{ext} files.")
        else:
            print(f"✅ All .{ext} files passed integrity check.")

        total_errors += errors

    if total_errors > 0:
        print(f"\n❌ Integrity check failed: {total_errors} file(s) may be corrupted or invalid.")
        sys.exit(1)
    else:
        print("\n✅ All files passed integrity check.")


if __name__ == '__main__':
    validate_structure()
    check_file_integrity()