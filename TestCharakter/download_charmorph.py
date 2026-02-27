"""Download CharMorphPlugin character data into TestCharakter/.

Usage:
    python download_charmorph.py                  # Extract ALL characters, activate mb_male
    python download_charmorph.py --switch mb_female   # Switch active character (from cache)
    python download_charmorph.py --list               # List cached characters

Extracts character data from the last CharMorphPlugin git commit (69e914e)
into charmorph_data/{name}/ and copies the active character to data/humanBody/
so humanbody_core can load it.

Characters:
    mb_male    - 7 body types (Caucasian, African, Anime, Asian, Dwarf, Elf, Latin)
    mb_female  - 6 body types (Caucasian, African, Anime, Asian, Elf, Latin)
    antonia    - 1 body type (Default), different morph structure

    reom is skipped (no faces.npy -> cannot render).
"""
import json
import os
import shutil
import sys
import tarfile
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path

PARENT_REPO = Path(r'A:\3DTools')
DEST = Path(__file__).resolve().parent
CHARMORPH_COMMIT = '69e914e'

# Characters with faces.npy (renderable)
CHARACTERS = ['mb_male', 'mb_female', 'antonia']
DEFAULT_CHARACTER = 'mb_male'

# Cache directory for all extracted characters
CACHE_DIR = DEST / 'charmorph_data'

# Active character data directory (read by test_character_api.py)
ACTIVE_DIR = DEST / 'data' / 'humanBody'


def clean_active():
    """Remove active character data (data/humanBody/)."""
    if ACTIVE_DIR.exists():
        shutil.rmtree(ACTIVE_DIR)
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)


def clean_all():
    """Remove all extracted files, keeping scripts and reference code."""
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


def extract_character(name):
    """Extract one character from git into charmorph_data/{name}/."""
    char_prefix = f'CharMorphPlugin/data/characters/{name}/'
    cache_path = CACHE_DIR / name

    if cache_path.exists():
        shutil.rmtree(cache_path)
    cache_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ['git', '-C', str(PARENT_REPO), 'archive', '--format=tar',
             '-o', tmp_path, CHARMORPH_COMMIT, char_prefix],
            check=True,
        )

        with tarfile.open(tmp_path, 'r') as tar:
            for member in tar.getmembers():
                if not member.name.startswith(char_prefix):
                    continue
                rel = member.name[len(char_prefix):]
                if not rel:
                    continue

                # Only extract data files relevant for humanbody_core
                should_extract = False
                if rel.startswith('morphs/'):
                    should_extract = True
                elif rel in ('faces.npy', 'config.yaml', 'morphs_meta.yaml',
                             'morphs_meta_fantasy.yaml'):
                    should_extract = True
                elif rel.startswith('weights/'):
                    should_extract = True
                elif rel.startswith('joints/'):
                    should_extract = True

                if not should_extract:
                    continue

                dest_path = cache_path / rel
                if member.isdir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as src:
                        with open(dest_path, 'wb') as dst:
                            dst.write(src.read())
                    print(f'  {name}/{rel}')

    finally:
        os.unlink(tmp_path)

    # Verify
    faces = cache_path / 'faces.npy'
    l1_dir = cache_path / 'morphs' / 'L1'
    if faces.exists():
        import numpy as np
        arr = np.load(str(faces))
        print(f'  -> faces.npy: {arr.shape[0]} faces, shape={arr.shape}')
    else:
        print(f'  -> WARNING: no faces.npy!')

    if l1_dir.exists():
        types = [f.stem for f in sorted(l1_dir.glob('*.npy'))]
        print(f'  -> L1 body types: {types}')


def activate_character(name):
    """Copy character data from cache to active directory (data/humanBody/)."""
    cache_path = CACHE_DIR / name
    if not cache_path.exists():
        print(f'ERROR: Character "{name}" not found in cache.')
        print(f'Available: {list_cached()}')
        return False

    print(f'Activating character: {name}')
    clean_active()

    # Copy all data files
    for src_path in cache_path.rglob('*'):
        if src_path.is_file():
            rel = src_path.relative_to(cache_path)
            dst_path = ACTIVE_DIR / rel
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)

    # Update commit_info.json with active character
    info_path = DEST / 'commit_info.json'
    if info_path.exists():
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        info['character'] = name
        info['message'] = f'CharMorphPlugin {name} character'
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

    print(f'  -> {name} is now the active character')
    return True


def list_cached():
    """Return list of cached character names."""
    if not CACHE_DIR.exists():
        return []
    return sorted(d.name for d in CACHE_DIR.iterdir()
                  if d.is_dir() and (d / 'faces.npy').exists())


def extract_humanbody_core():
    """Extract humanbody_core module from v0.53 (first version with humanbody_core).

    The CharMorphPlugin commit (69e914e) predates humanbody_core, so we use
    v0.53 (b884619) which has a compatible MorphData that can load CharMorphPlugin data.
    """
    CORE_COMMIT = 'b884619'  # v0.53
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
    args = sys.argv[1:]

    # --list: show cached characters
    if '--list' in args:
        cached = list_cached()
        if cached:
            print(f'Cached characters: {cached}')
            # Check which is active
            info_path = DEST / 'commit_info.json'
            if info_path.exists():
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                print(f'Active: {info.get("character", "unknown")}')
        else:
            print('No characters cached. Run without arguments to extract all.')
        return

    # --switch <name>: switch active character from cache
    if '--switch' in args:
        idx = args.index('--switch')
        if idx + 1 >= len(args):
            print('Usage: download_charmorph.py --switch <character_name>')
            print(f'Available: {list_cached()}')
            return
        name = args[idx + 1]
        if activate_character(name):
            print(f'\nDone! Switched to {name}.')
            print('Call /api/character-test/reload/ to refresh the test page.')
        return

    # Default: extract ALL characters + humanbody_core
    print(f'Extracting CharMorphPlugin characters from commit {CHARMORPH_COMMIT}...')
    print(f'Characters: {CHARACTERS}')

    print('\nCleaning old TestCharakter files...')
    clean_all()

    # Extract each character into cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for name in CHARACTERS:
        print(f'\nExtracting {name}...')
        extract_character(name)

    print('\nExtracting humanbody_core module (v0.53)...')
    extract_humanbody_core()

    print('\nCreating settings.yaml...')
    create_settings_yaml()

    # Save commit info
    info = {
        'full_hash': CHARMORPH_COMMIT,
        'short_hash': CHARMORPH_COMMIT[:7],
        'message': f'CharMorphPlugin {DEFAULT_CHARACTER} character',
        'version': 'CharMorphPlugin',
        'date': '2026-02-26',
        'downloaded_at': datetime.now().isoformat(),
        'source': 'charmorph',
        'character': DEFAULT_CHARACTER,
        'available_characters': CHARACTERS,
    }
    info_path = DEST / 'commit_info.json'
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    # Activate default character
    print(f'\nActivating default character: {DEFAULT_CHARACTER}')
    activate_character(DEFAULT_CHARACTER)

    # Summary
    print('\n' + '='*60)
    print('SUMMARY')
    print('='*60)
    cached = list_cached()
    for name in cached:
        cache_path = CACHE_DIR / name
        l1_dir = cache_path / 'morphs' / 'L1'
        if l1_dir.exists():
            types = [f.stem for f in sorted(l1_dir.glob('*.npy'))]
        else:
            types = ['?']
        marker = ' <-- ACTIVE' if name == DEFAULT_CHARACTER else ''
        print(f'  {name}: {len(types)} body type(s) {types}{marker}')

    print(f'\nTo switch: python download_charmorph.py --switch <name>')
    print(f'Then call: /api/character-test/reload/')
    print(f'\nDone!')


if __name__ == '__main__':
    main()
