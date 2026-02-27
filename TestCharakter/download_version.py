"""Download a specific git commit of HumanBody into TestCharakter/.

Usage:
    python download_version.py <commit_hash>

Extracts humanbody_core/ and data/ from the specified commit using
``git archive`` so the test character page can load an isolated version.
"""
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

# HumanBody git repo
HUMANBODY_REPO = Path(r'A:\3DTools\HumanBody')
# Destination (same dir as this script)
DEST = Path(__file__).resolve().parent

# Paths to extract from the archive
EXTRACT_PREFIXES = [
    'humanbody_core/',
    'data/humanBody/morphs/',
    'data/humanBody/faces.npy',
    'data/humanBody/face_materials.npy',
    'data/humanBody/uvs.npy',
    'data/humanBody/materials.json',
    'data/humanBody/skin_weights_base.json',
    'data/humanBody/skin_weights.json',
    'data/humanBody/def_skeleton.json',
    'data/humanBody/morphs_meta.yaml',
    'data/humanBody/config.yaml',
    'data/humanBody/rig_bones.json',
    'data/humanBody/normals.npy',
    'settings.yaml',
]


def clean_dest():
    """Remove old extracted files, keeping download_version.py and __init__.py."""
    keep = {'download_version.py', '__init__.py', '__pycache__'}
    for entry in DEST.iterdir():
        if entry.name in keep:
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def get_commit_info(commit_hash: str) -> dict:
    """Get commit metadata via git log."""
    fmt = '%H%n%h%n%s%n%ai'
    result = subprocess.run(
        ['git', '-C', str(HUMANBODY_REPO), 'log', '-1', f'--format={fmt}', commit_hash],
        capture_output=True, text=True, check=True,
    )
    lines = result.stdout.strip().split('\n')
    return {
        'full_hash': lines[0],
        'short_hash': lines[1],
        'message': lines[2],
        'date': lines[3],
        'downloaded_at': datetime.now().isoformat(),
    }


def extract_commit(commit_hash: str):
    """Use git archive to extract files from a specific commit."""
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # git archive outputs a tar of the entire tree at that commit
        subprocess.run(
            ['git', '-C', str(HUMANBODY_REPO), 'archive', '--format=tar',
             '-o', tmp_path, commit_hash],
            check=True,
        )

        with tarfile.open(tmp_path, 'r') as tar:
            for member in tar.getmembers():
                # Only extract files matching our prefixes
                if any(member.name == p.rstrip('/') or member.name.startswith(p)
                       for p in EXTRACT_PREFIXES):
                    tar.extract(member, path=str(DEST))
    finally:
        os.unlink(tmp_path)


# Files that are typically untracked (Blender-exported) but needed at runtime.
# If git archive didn't extract them, copy from the current working directory.
FALLBACK_FILES = [
    'data/humanBody/faces.npy',
    'data/humanBody/face_materials.npy',
    'data/humanBody/uvs.npy',
    'data/humanBody/materials.json',
    'data/humanBody/skin_weights_base.json',
    'data/humanBody/skin_weights.json',
    'data/humanBody/def_skeleton.json',
    'data/humanBody/rig_bones.json',
    'data/humanBody/normals.npy',
    'data/humanBody/config.yaml',
    'data/humanBody/morphs_meta.yaml',
]


def copy_fallback_files():
    """Copy untracked data files from the live HumanBody repo if missing."""
    copied = []
    for rel_path in FALLBACK_FILES:
        dest_file = DEST / rel_path
        if dest_file.exists():
            continue  # Already extracted from git archive
        src_file = HUMANBODY_REPO / rel_path
        if src_file.exists():
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dest_file))
            copied.append(rel_path)
    return copied


def main():
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <commit_hash>')
        sys.exit(1)

    commit_hash = sys.argv[1]
    print(f'Downloading HumanBody commit {commit_hash}...')

    # Get commit info first (validates the hash)
    info = get_commit_info(commit_hash)
    print(f'  Commit: {info["short_hash"]} — {info["message"]}')
    print(f'  Date:   {info["date"]}')

    # Clean old files
    print('Cleaning old TestCharakter files...')
    clean_dest()

    # Extract
    print('Extracting from git archive...')
    extract_commit(commit_hash)

    # Copy untracked data files as fallback
    copied = copy_fallback_files()
    if copied:
        print(f'Copied {len(copied)} untracked files from current repo:')
        for f in copied:
            print(f'  + {f}')

    # Save commit info
    info_path = DEST / 'commit_info.json'
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f'Done! Files extracted to {DEST}')
    print(f'Commit info saved to {info_path}')


if __name__ == '__main__':
    main()
