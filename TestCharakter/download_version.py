"""Download a specific git commit of HumanBody into TestCharakter/.

Usage:
    python download_version.py <commit_hash>

Extracts humanbody_core/ and data/ from the specified commit using
``git archive`` so the test character page can load an isolated version.

Supports two repo layouts:
  - New (>= 83e40b6): humanbody_core/ lives inside the HumanBody repo
  - Old (v0.53 etc.): humanbody_core/ lives in the parent repo (A:\\3DTools),
    morph data under HumanBody/data/
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

# Git repos
PARENT_REPO = Path(r'A:\3DTools')            # The root monorepo
HUMANBODY_REPO = PARENT_REPO / 'HumanBody'   # Subdir (has its own git identity via prefix)
# Destination (same dir as this script)
DEST = Path(__file__).resolve().parent

# Paths to extract from the HumanBody repo (new layout)
EXTRACT_PREFIXES_NEW = [
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

# Paths to extract from the parent repo (old layout)
# humanbody_core/ is at the root, data is under HumanBody/data/
EXTRACT_MAP_OLD = {
    # source prefix in archive -> dest prefix in TestCharakter
    'humanbody_core/': 'humanbody_core/',
    'HumanBody/data/humanBody/morphs/': 'data/humanBody/morphs/',
    'HumanBody/data/humanBody/faces.npy': 'data/humanBody/faces.npy',
    'HumanBody/data/humanBody/face_materials.npy': 'data/humanBody/face_materials.npy',
    'HumanBody/data/humanBody/uvs.npy': 'data/humanBody/uvs.npy',
    'HumanBody/data/humanBody/materials.json': 'data/humanBody/materials.json',
    'HumanBody/data/humanBody/skin_weights_base.json': 'data/humanBody/skin_weights_base.json',
    'HumanBody/data/humanBody/skin_weights.json': 'data/humanBody/skin_weights.json',
    'HumanBody/data/humanBody/def_skeleton.json': 'data/humanBody/def_skeleton.json',
    'HumanBody/data/humanBody/morphs_meta.yaml': 'data/humanBody/morphs_meta.yaml',
    'HumanBody/data/humanBody/config.yaml': 'data/humanBody/config.yaml',
    'HumanBody/data/humanBody/rig_bones.json': 'data/humanBody/rig_bones.json',
    'HumanBody/data/humanBody/normals.npy': 'data/humanBody/normals.npy',
    'HumanBody/settings.yaml': 'settings.yaml',
}

# Files that are typically untracked (Blender-exported) but needed at runtime.
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


def clean_dest():
    """Remove old extracted files, keeping scripts and gitignore."""
    keep = {'download_version.py', '__init__.py', '__pycache__', '.gitignore'}
    for entry in DEST.iterdir():
        if entry.name in keep:
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def _parse_version(message: str) -> str:
    """Extract version number from commit message (e.g. 'bump to v0.65' -> '0.65')."""
    m = re.search(r'v?(\d+\.\d+)', message)
    return m.group(1) if m else ''


def get_commit_info(commit_hash: str, repo: Path) -> dict:
    """Get commit metadata via git log."""
    fmt = '%H%n%h%n%s%n%ai'
    result = subprocess.run(
        ['git', '-C', str(repo), 'log', '-1', f'--format={fmt}', commit_hash],
        capture_output=True, text=True, check=True,
    )
    lines = result.stdout.strip().split('\n')
    message = lines[2]
    return {
        'full_hash': lines[0],
        'short_hash': lines[1],
        'message': message,
        'version': _parse_version(message),
        'date': lines[3],
        'downloaded_at': datetime.now().isoformat(),
    }


def _has_path_in_commit(repo: Path, commit: str, path: str) -> bool:
    """Check if a path exists in a git commit."""
    r = subprocess.run(
        ['git', '-C', str(repo), 'ls-tree', '--name-only', commit, path],
        capture_output=True, text=True,
    )
    return path.rstrip('/') in r.stdout


def detect_layout(commit_hash: str) -> str:
    """Detect whether humanbody_core is in HumanBody repo or parent repo.

    Returns 'new' if humanbody_core/ is in the HumanBody repo,
    'old' if it's in the parent repo (A:\\3DTools), or 'none'.
    """
    # Check HumanBody repo first (new layout)
    if _has_path_in_commit(HUMANBODY_REPO, commit_hash, 'humanbody_core/'):
        return 'new'

    # Check parent repo (old layout: humanbody_core/ at root alongside HumanBody/)
    if _has_path_in_commit(PARENT_REPO, commit_hash, 'humanbody_core/'):
        return 'old'

    return 'none'


def extract_new(commit_hash: str):
    """Extract from HumanBody repo (new layout: humanbody_core inside repo)."""
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ['git', '-C', str(HUMANBODY_REPO), 'archive', '--format=tar',
             '-o', tmp_path, commit_hash],
            check=True,
        )
        with tarfile.open(tmp_path, 'r') as tar:
            for member in tar.getmembers():
                if any(member.name == p.rstrip('/') or member.name.startswith(p)
                       for p in EXTRACT_PREFIXES_NEW):
                    tar.extract(member, path=str(DEST))
    finally:
        os.unlink(tmp_path)


def extract_old(commit_hash: str):
    """Extract from parent repo (old layout: humanbody_core at root, data under HumanBody/)."""
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ['git', '-C', str(PARENT_REPO), 'archive', '--format=tar',
             '-o', tmp_path, commit_hash],
            check=True,
        )
        with tarfile.open(tmp_path, 'r') as tar:
            for member in tar.getmembers():
                for src_prefix, dest_prefix in EXTRACT_MAP_OLD.items():
                    if member.name == src_prefix.rstrip('/') or member.name.startswith(src_prefix):
                        # Rewrite path: HumanBody/data/... -> data/...
                        rel = member.name[len(src_prefix):]
                        dest_path = os.path.join(str(DEST), dest_prefix.rstrip('/'),
                                                 rel) if rel else os.path.join(
                                                     str(DEST), dest_prefix.rstrip('/'))
                        if member.isdir():
                            os.makedirs(dest_path, exist_ok=True)
                        else:
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            with tar.extractfile(member) as src:
                                with open(dest_path, 'wb') as dst:
                                    dst.write(src.read())
                        break
    finally:
        os.unlink(tmp_path)


def copy_fallback_files():
    """Copy untracked data files from the live HumanBody repo if missing."""
    copied = []
    for rel_path in FALLBACK_FILES:
        dest_file = DEST / rel_path
        if dest_file.exists():
            continue
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
    print(f'Resolving commit {commit_hash}...')

    # Detect layout
    layout = detect_layout(commit_hash)

    if layout == 'new':
        repo = HUMANBODY_REPO
        print(f'  Layout: new (humanbody_core inside HumanBody repo)')
    elif layout == 'old':
        repo = PARENT_REPO
        print(f'  Layout: old (humanbody_core in parent repo A:\\3DTools)')
    else:
        # Try to get info for error message
        try:
            info = get_commit_info(commit_hash, HUMANBODY_REPO)
            name = f'{info["short_hash"]} — {info["message"]}'
        except Exception:
            try:
                info = get_commit_info(commit_hash, PARENT_REPO)
                name = f'{info["short_hash"]} — {info["message"]}'
            except Exception:
                name = commit_hash
        print(f'\nERROR: Commit {name} has no humanbody_core/ directory.')
        print('Neither in the HumanBody repo nor in the parent repo.')
        sys.exit(1)

    info = get_commit_info(commit_hash, repo)
    print(f'  Commit: {info["short_hash"]} — {info["message"]}')
    print(f'  Date:   {info["date"]}')
    if info['version']:
        print(f'  Version: v{info["version"]}')

    # Clean old files
    print('Cleaning old TestCharakter files...')
    clean_dest()

    # Extract
    print('Extracting from git archive...')
    if layout == 'new':
        extract_new(commit_hash)
    else:
        extract_old(commit_hash)

    # Copy untracked data files as fallback
    copied = copy_fallback_files()
    if copied:
        print(f'Copied {len(copied)} untracked files from current repo:')
        for f in copied:
            print(f'  + {f}')

    # Verify humanbody_core was extracted
    core_init = DEST / 'humanbody_core' / '__init__.py'
    if not core_init.exists():
        print('\nWARNING: humanbody_core/__init__.py not found after extraction!')
        sys.exit(1)

    # Save commit info
    info_path = DEST / 'commit_info.json'
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f'\nDone! Files extracted to {DEST}')
    print(f'Commit info saved to {info_path}')


if __name__ == '__main__':
    main()
