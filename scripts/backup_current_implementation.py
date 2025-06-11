#!/usr/bin/env python3
"""
Backup Current Module Implementation

This script creates a backup of the current module implementation
before starting the refactoring process.
"""

import os
import shutil
import datetime
import json
from pathlib import Path

def create_backup():
    """Create a comprehensive backup of the current implementation"""
    
    # Create backup directory with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/module_implementation_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating backup in: {backup_dir}")
    
    # Files and directories to backup
    backup_items = {
        'routes': {
            'source': 'app/routes/modules.py',
            'description': 'Main module routes file'
        },
        'models': {
            'source': 'app/models/module.py',
            'description': 'Module database models'
        },
        'templates': {
            'source': 'app/templates/modules/',
            'description': 'Module templates directory'
        },
        'static_css': {
            'source': 'app/static/css/',
            'description': 'CSS files for modules'
        },
        'static_js': {
            'source': 'app/static/js/',
            'description': 'JavaScript files for modules'
        },
        'seed_data': {
            'source': 'app/seed_data.py',
            'description': 'Database seed data'
        },
        'macros': {
            'source': 'app/templates/macros/',
            'description': 'Template macros'
        }
    }
    
    # Create backup manifest
    manifest = {
        'backup_date': datetime.datetime.now().isoformat(),
        'backup_reason': 'Pre-refactoring backup of module system',
        'items': {},
        'git_commit': get_git_commit_hash(),
        'notes': [
            'This backup was created before major refactoring of the module system',
            'Issues identified: Quiz inconsistencies, template complexity, route complexity',
            'Refactoring plan available in MODULE_REFACTORING_PLAN.md'
        ]
    }
    
    # Backup each item
    for item_name, item_info in backup_items.items():
        source_path = Path(item_info['source'])
        dest_path = backup_dir / item_name
        
        try:
            if source_path.is_file():
                # Copy file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                manifest['items'][item_name] = {
                    'type': 'file',
                    'source': str(source_path),
                    'destination': str(dest_path),
                    'description': item_info['description'],
                    'size': source_path.stat().st_size,
                    'status': 'success'
                }
                print(f"✓ Backed up file: {source_path}")
                
            elif source_path.is_dir():
                # Copy directory
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                manifest['items'][item_name] = {
                    'type': 'directory',
                    'source': str(source_path),
                    'destination': str(dest_path),
                    'description': item_info['description'],
                    'file_count': count_files_in_dir(source_path),
                    'status': 'success'
                }
                print(f"✓ Backed up directory: {source_path}")
                
            else:
                manifest['items'][item_name] = {
                    'source': str(source_path),
                    'description': item_info['description'],
                    'status': 'not_found',
                    'error': 'Source path does not exist'
                }
                print(f"⚠ Warning: {source_path} not found")
                
        except Exception as e:
            manifest['items'][item_name] = {
                'source': str(source_path),
                'description': item_info['description'],
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ Error backing up {source_path}: {e}")
    
    # Save manifest
    manifest_path = backup_dir / 'backup_manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Create README for the backup
    readme_content = f"""
# Module Implementation Backup

**Backup Date:** {manifest['backup_date']}
**Git Commit:** {manifest['git_commit']}

## Purpose

This backup was created before major refactoring of the module system to preserve the current implementation.

## Issues Identified

1. **Quiz System Inconsistencies**
   - Mixed client-side and server-side implementations
   - Hardcoded quiz questions in templates
   - Database synchronization issues

2. **Template Complexity**
   - Large monolithic templates (800+ lines)
   - Mixed concerns (HTML, CSS, JavaScript)
   - Code duplication across modules

3. **Route Handler Complexity**
   - Single file with 828 lines
   - Multiple responsibilities in single functions
   - Inconsistent error handling

## Backup Contents

"""
    
    for item_name, item_info in manifest['items'].items():
        status_icon = "✓" if item_info['status'] == 'success' else "✗" if item_info['status'] == 'error' else "⚠"
        readme_content += f"- {status_icon} **{item_name}**: {item_info['description']}\n"
    
    readme_content += f"""

## Restoration Instructions

To restore this backup:

1. Stop the application
2. Copy files from this backup to their original locations
3. Restart the application
4. Run database migrations if needed

## Files Modified During Refactoring

Keep track of which files are modified during refactoring:

- [ ] app/routes/modules.py
- [ ] app/models/module.py
- [ ] app/templates/modules/
- [ ] app/static/css/
- [ ] app/static/js/
- [ ] app/seed_data.py

## Notes

{chr(10).join(f'- {note}' for note in manifest['notes'])}

---

*Generated by backup_current_implementation.py*
"""
    
    readme_path = backup_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n✓ Backup completed successfully!")
    print(f"📁 Backup location: {backup_dir.absolute()}")
    print(f"📄 Manifest: {manifest_path}")
    print(f"📖 README: {readme_path}")
    
    return backup_dir

def get_git_commit_hash():
    """Get the current git commit hash"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return 'unknown'

def count_files_in_dir(directory):
    """Count files in a directory recursively"""
    try:
        return sum(1 for _ in Path(directory).rglob('*') if _.is_file())
    except Exception:
        return 0

if __name__ == '__main__':
    print("🔄 Starting backup of current module implementation...")
    backup_dir = create_backup()
    print(f"\n🎉 Backup process completed!")
    print(f"\nNext steps:")
    print(f"1. Review the backup in: {backup_dir}")
    print(f"2. Start the refactoring process")
    print(f"3. Refer to MODULE_REFACTORING_PLAN.md for implementation details")