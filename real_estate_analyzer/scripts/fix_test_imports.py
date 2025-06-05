#!/usr/bin/env python3
"""Script to fix import paths in moved test files."""

import os
import re
from pathlib import Path


def fix_import_paths():
    """Fix import paths in all test files."""

    test_dirs = [
        'tests/unit',
        'tests/integration',
        'tests/refactoring'
    ]

    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue

        print(f"🔧 Fixing imports in {test_dir}/")

        for test_file in test_path.glob('*.py'):
            fix_file_imports(test_file, test_dir)


def fix_file_imports(file_path: Path, test_dir: str):
    """Fix imports in a single test file."""

    # Determine how many levels up to go to reach project root
    if test_dir == 'tests/unit':
        levels_up = 3  # tests/unit/../.. -> project root
    elif test_dir == 'tests/integration':
        levels_up = 3  # tests/integration/../.. -> project root
    elif test_dir == 'tests/refactoring':
        levels_up = 3  # tests/refactoring/../.. -> project root
    else:
        levels_up = 3

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Add sys.path setup if not present and file has src imports
        if 'from src.' in content and 'sys.path.insert' not in content:
            # Find the first import line
            lines = content.split('\n')
            first_import_idx = -1

            for i, line in enumerate(lines):
                if (line.strip().startswith('import ') or
                        line.strip().startswith('from ')) and 'sys' not in line:
                    first_import_idx = i
                    break

            if first_import_idx >= 0:
                # Insert path setup before first import
                path_setup = [
                    'import sys',
                    'from pathlib import Path',
                    '',
                    f'# Add src to path for imports',
                    f'sys.path.insert(0, str(Path(__file__).parent{"".join([".parent"] * levels_up)} / "src"))',
                    ''
                ]

                lines = lines[:first_import_idx] + \
                    path_setup + lines[first_import_idx:]
                content = '\n'.join(lines)

        # Fix src.module imports to just module imports
        content = re.sub(
            r'from src\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'from \1', content)
        content = re.sub(
            r'import src\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'import \1', content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Fixed {file_path.name}")
        else:
            print(f"   ⏭️  {file_path.name} (no changes needed)")

    except Exception as e:
        print(f"   ❌ Error fixing {file_path.name}: {e}")


def main():
    """Main function."""
    print("🚀 Fixing test imports after reorganization...")
    print("=" * 50)

    # Change to project root
    os.chdir(Path(__file__).parent.parent)

    fix_import_paths()

    print("\n✅ Import path fixing complete!")
    print("\n📋 Summary:")
    print("   - Added sys.path setup to test files as needed")
    print("   - Changed 'from src.module' to 'from module'")
    print("   - All test files should now work from their new locations")


if __name__ == "__main__":
    main()
