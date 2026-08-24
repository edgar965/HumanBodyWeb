# -*- coding: utf-8 -*-
"""BVH-Bibliothek: einlesen, loeschen, in Blender oeffnen.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.
"""

from ..models import BVHFile
from ..projekt_temp import ProjektTemp
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from pathlib import Path
import subprocess


def _copy_bvh_to_results(bvh_path, video_name, pipeline):
    """Copy BVH file to the shared Results directory.
    Filename: {video_stem}_{pipeline}.bvh, overwrites if exists.
    Returns the destination path."""
    import shutil
    results_dir = Path(settings.BVH_RESULTS_DIR)
    results_dir.mkdir(parents=True, exist_ok=True)
    video_stem = video_name.rsplit('.', 1)[0]
    dest = results_dir / f'{video_stem}_{pipeline}.bvh'
    shutil.copy2(str(bvh_path), str(dest))
    return str(dest)


@require_POST
def scan_bvh_files(request):
    """Scan directories for BVH files and add to library.

    NUR POST (17.08.2026). Diese Route hat als einzige der drei
    Bibliotheks-Aktionen keinen Methodenschutz gehabt und ist dabei aufgefallen,
    dass der Leistungstest sie mit einem GET anfuhr: 35 Abfragen, 7.067
    BVH-Koepfe gelesen, Datenbank geschrieben. Ein `<img src="/library/scan/">`
    auf einer fremden Seite hat damit einen vollen Neuaufbau der Bibliothek
    ausgeloest — die `GleicherUrsprung`-Middleware prueft nur schreibende
    METHODEN, und GET gehoert nicht dazu.

    Die drei Aufrufstellen (`browser.html` 2x, `test_mocapnet.html`) sind
    deshalb von `<a href>` auf ein kleines POST-Formular umgestellt.
    """
    scan_dirs = [
        settings.MOCAPNET_ROOT / 'output',
        settings.BLENDER_BVH_DIR,
        Path(settings.MEDIA_ROOT) / 'output',
    ]

    count = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for bvh_path in scan_dir.rglob('*.bvh'):
            _, created = BVHFile.objects.get_or_create(
                path=str(bvh_path),
                defaults={
                    'name': bvh_path.name,
                    'source': 'mocapnet' if 'MocapNET' in str(bvh_path) else 'imported',
                }
            )
            if created:
                count += 1

    messages.success(request, f'{count} new BVH files found.')
    return redirect('library')


@require_POST
def delete_bvh(request, pk):
    """Delete a BVH file.

    `require_POST` seit 15.08.2026: Das war ein `<a href>` in browser.html — ein
    LINK, der einen Datenbankeintrag löscht. Zwei Wege dorthin, ohne dass jemand
    klickt: die Verweis-Vorschau des Browsers, und eine fremde Seite mit
    `<img src="http://127.0.0.1:8081/library/5/delete/">`. Die Middleware
    `ui/same_origin.py` prüft nur UNSICHERE Methoden — ein GET geht durch. Das
    Template schickt jetzt ein Formular mit CSRF-Marke.
    """
    bvh = get_object_or_404(BVHFile, pk=pk)
    # Only delete from DB, keep file on disk
    bvh.delete()
    messages.success(request, f'Removed {bvh.name} from library.')
    return redirect('library')


@require_POST
def open_in_blender(request, pk):
    """Open a BVH file in Blender.

    `require_POST` seit 15.08.2026, aus demselben Grund wie bei `delete_bvh`:
    Ein GET-Link, der ein Programm auf diesem Rechner startet, lässt sich von
    einer fremden Seite aus auslösen (`<img src=…>`), weil GET die
    Gleiche-Herkunft-Prüfung nicht durchläuft."""
    bvh = get_object_or_404(BVHFile, pk=pk)
    bvh_path = bvh.path.replace('\\', '/')

    blender_exe = str(settings.BLENDER_EXE)

    # Create a temporary Python script for Blender
    # Sanitize path: use repr() to prevent injection via special chars
    safe_path = repr(str(bvh.path))
    safe_name = repr(str(bvh.name))
    script_content = f'''
import bpy

# Import BVH
bpy.ops.import_anim.bvh(filepath={safe_path})
print("BVH loaded:", {safe_name})
'''
    # Ins Projekt statt nach System-Temp auf C: (Projektregel, Vorgeschichte:
    # rund 100 GB Datenmüll dort). Der Name ist bewusst fest — es ist ein
    # Hilfsskript für Blender, das bei jedem Aufruf überschrieben wird.
    script_path = str(ProjektTemp.verzeichnis() / 'mocapnet_load_bvh.py')
    with open(script_path, 'w') as f:
        f.write(script_content)

    subprocess.Popen([blender_exe, '--python', script_path])
    messages.success(request, f'Opening {bvh.name} in Blender...')
    return redirect('library')
