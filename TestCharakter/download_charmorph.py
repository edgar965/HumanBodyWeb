"""Download CharMorphPlugin mb_male character data into TestCharakter/.

Usage:
    python download_charmorph.py

Extracts the mb_male character from the last CharMorphPlugin git commit (69e914e)
into the standard data layout so humanbody_core can load it.
"""
import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

PARENT_REPO = Path(r'A:\3DTools')
DEST = Path(__file__).resolve().parent
CHARMORPH_COMMIT = '69e914e'
CHARACTER = 'mb_male'

# What to extract from CharMorphPlugin/data/characters/mb_male/
CHAR_PREFIX = f'CharMorphPlugin/data/characters/{CHARACTER}/'

import subprocess


def clean_dest():
    """Remove old extracted files, keeping scripts and reference code."""
    keep = {
        'download_version.py', 'download_charmorph.py',
        '__init__.py', '__pycache__', '.gitignore',
        'charmorph_ref',
    }
    for entry in DEST.iterdir():
        if entry.name in keep:
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


def extract():
    """Extract mb_male data from git into TestCharakter/data/humanBody/."""
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ['git', '-C', str(PARENT_REPO), 'archive', '--format=tar',
             '-o', tmp_path, CHARMORPH_COMMIT, CHAR_PREFIX],
            check=True,
        )
        data_dir = DEST / 'data' / 'humanBody'

        with tarfile.open(tmp_path, 'r') as tar:
            for member in tar.getmembers():
                if not member.name.startswith(CHAR_PREFIX):
                    continue
                rel = member.name[len(CHAR_PREFIX):]
                if not rel:
                    continue

                # Map CharMorphPlugin paths to humanbody_core layout
                dest_path = None
                if rel.startswith('morphs/'):
                    dest_path = data_dir / rel
                elif rel == 'faces.npy':
                    dest_path = data_dir / 'faces.npy'
                elif rel == 'config.yaml':
                    dest_path = data_dir / 'config.yaml'
                elif rel == 'morphs_meta.yaml':
                    dest_path = data_dir / 'morphs_meta.yaml'
                elif rel.startswith('weights/'):
                    dest_path = data_dir / rel

                if dest_path is None:
                    continue

                if member.isdir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as src:
                        with open(dest_path, 'wb') as dst:
                            dst.write(src.read())
                    print(f'  {rel}')

    finally:
        os.unlink(tmp_path)


def extract_humanbody_core():
    """Extract humanbody_core module — from v0.53 (first version with humanbody_core).

    The CharMorphPlugin commit (69e914e) predates humanbody_core, so we use
    v0.53 (b884619) which has a compatible MorphData that can load CharMorphPlugin data.
    """
    CORE_COMMIT = 'b884619'  # v0.53 — first commit with humanbody_core
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ['git', '-C', str(PARENT_REPO), 'archive', '--format=tar',
             '-o', tmp_path, CORE_COMMIT, 'humanbody_core/'],
            check=True,
        )
        with tarfile.open(tmp_path, 'r') as tar:
            for member in tar.getmembers():
                if member.name.startswith('humanbody_core/'):
                    tar.extract(member, path=str(DEST))
                    if not member.isdir():
                        print(f'  {member.name}')
    finally:
        os.unlink(tmp_path)


def create_settings_yaml():
    """Create a minimal settings.yaml."""
    settings = DEST / 'settings.yaml'
    settings.write_text(
        'character_defaults:\n'
        '  gender:\n'
        '    min: 0\n'
        '    max: 100\n'
        '    default: 0\n'
        '  age:\n'
        '    min: 18\n'
        '    max: 100\n'
        '    default: 59\n'
        '  mass:\n'
        '    min: 45\n'
        '    max: 200\n'
        '    default: 123\n'
        '  tone:\n'
        '    min: 0\n'
        '    max: 100\n'
        '    default: 50\n'
        '  height:\n'
        '    min: 150\n'
        '    max: 200\n'
        '    default: 175\n',
        encoding='utf-8',
    )


def main():
    print(f'Extracting CharMorphPlugin {CHARACTER} from commit {CHARMORPH_COMMIT}...')

    print('Cleaning old TestCharakter files...')
    clean_dest()

    print(f'Extracting {CHARACTER} data...')
    extract()

    print('Extracting humanbody_core module...')
    extract_humanbody_core()

    print('Creating settings.yaml...')
    create_settings_yaml()

    # Save commit info
    info = {
        'full_hash': CHARMORPH_COMMIT,
        'short_hash': CHARMORPH_COMMIT[:7],
        'message': f'CharMorphPlugin {CHARACTER} character (last version)',
        'version': 'CharMorphPlugin',
        'date': '2026-02-26',
        'downloaded_at': datetime.now().isoformat(),
        'source': 'charmorph',
        'character': CHARACTER,
    }
    info_path = DEST / 'commit_info.json'
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    # Verify
    l1_dir = DEST / 'data' / 'humanBody' / 'morphs' / 'L1'
    if l1_dir.is_dir():
        types = [f.stem for f in sorted(l1_dir.glob('*.npy'))]
        print(f'\nBody types found: {types}')
    else:
        print('\nWARNING: No L1 directory found!')

    core_init = DEST / 'humanbody_core' / '__init__.py'
    if not core_init.exists():
        print('WARNING: humanbody_core/__init__.py not found!')

    print(f'\nDone! CharMorphPlugin {CHARACTER} extracted to {DEST}')
    print(f'Default body type: Caucasian')


if __name__ == '__main__':
    main()
