# -*- coding: utf-8 -*-
"""BVH-Bibliothek: einlesen, loeschen, in Blender oeffnen.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.

UMBAU 27.08.2026 (Befund `freie-funktionen`): vier freie Funktionen. Eine davon
(`_copy_bvh_to_results`) gehoerte gar nicht hierher — sie kopiert die fertige
BVH in den Ergebnisordner und wird ausschliesslich von
`pipelines/auftragslauf.py` gerufen, an vier Stellen und jedesmal mit einem
Import IN der Funktion. Sie steht jetzt als `dienste/ergebnisablage.Ergebnisablage`
dort, wo sie hingehoert.
"""

import subprocess
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ..models import BVHFile
from ..projekt_temp import ProjektTemp


class Bibliotheksendpunkte:
    """Die drei Aktionen der BVH-Bibliothek — alle drei NUR per POST."""

    #: Name des Hilfsskripts, das Blender die Datei laden laesst.
    BLENDER_SKRIPT = 'mocapnet_load_bvh.py'

    @staticmethod
    def _suchorte():
        return [settings.MOCAPNET_ROOT / 'output',
                settings.BLENDER_BVH_DIR,
                Path(settings.MEDIA_ROOT) / 'output']

    @staticmethod
    @require_POST
    def einlesen(request):
        """Verzeichnisse nach BVH-Dateien durchsuchen und aufnehmen.

        NUR POST (17.08.2026). Diese Route hat als einzige der drei
        Bibliotheks-Aktionen keinen Methodenschutz gehabt und ist dabei
        aufgefallen, dass der Leistungstest sie mit einem GET anfuhr: 35
        Abfragen, 7.067 BVH-Koepfe gelesen, Datenbank geschrieben. Ein
        `<img src="/library/scan/">` auf einer fremden Seite hat damit einen
        vollen Neuaufbau der Bibliothek ausgeloest — die
        `GleicherUrsprung`-Middleware prueft nur schreibende METHODEN, und GET
        gehoert nicht dazu.

        Die drei Aufrufstellen (`browser.html` 2x, `test_mocapnet.html`) sind
        deshalb von `<a href>` auf ein kleines POST-Formular umgestellt.
        """
        neu = 0
        for ordner in Bibliotheksendpunkte._suchorte():
            if not ordner.exists():
                continue
            for pfad in ordner.rglob('*.bvh'):
                _, angelegt = BVHFile.objects.get_or_create(
                    path=str(pfad),
                    defaults={
                        'name': pfad.name,
                        'source': ('mocapnet' if 'MocapNET' in str(pfad)
                                   else 'imported'),
                    })
                if angelegt:
                    neu += 1
        messages.success(request, '%d new BVH files found.' % neu)
        return redirect('library')

    @staticmethod
    @require_POST
    def loeschen(request, pk):
        """Einen Eintrag aus der Bibliothek nehmen — die Datei bleibt liegen.

        `require_POST` seit 15.08.2026: Das war ein `<a href>` in browser.html —
        ein LINK, der einen Datenbankeintrag loescht. Zwei Wege dorthin, ohne
        dass jemand klickt: die Verweis-Vorschau des Browsers, und eine fremde
        Seite mit `<img src="http://127.0.0.1:8081/library/5/delete/">`. Die
        Middleware `ui/same_origin.py` prueft nur UNSICHERE Methoden — ein GET
        geht durch. Das Template schickt jetzt ein Formular mit CSRF-Marke.
        """
        eintrag = get_object_or_404(BVHFile, pk=pk)
        eintrag.delete()
        messages.success(request, 'Removed %s from library.' % eintrag.name)
        return redirect('library')

    @staticmethod
    @require_POST
    def in_blender_oeffnen(request, pk):
        """Eine BVH-Datei in Blender oeffnen.

        `require_POST` seit 15.08.2026, aus demselben Grund wie bei `loeschen`:
        Ein GET-Link, der ein Programm auf diesem Rechner startet, laesst sich
        von einer fremden Seite aus ausloesen (`<img src=…>`), weil GET die
        Gleiche-Herkunft-Pruefung nicht durchlaeuft.
        """
        eintrag = get_object_or_404(BVHFile, pk=pk)
        skript = Bibliotheksendpunkte._skript_schreiben(eintrag)
        subprocess.Popen([str(settings.BLENDER_EXE), '--python', skript])
        messages.success(request, 'Opening %s in Blender...' % eintrag.name)
        return redirect('library')

    @staticmethod
    def _skript_schreiben(eintrag):
        """Das Blender-Hilfsskript — Pfade ueber `repr`, nicht eingesetzt.

        Ins Projekt statt nach System-Temp auf C: (Projektregel,
        Vorgeschichte: rund 100 GB Datenmuell dort). Der Name ist bewusst
        fest — das Skript wird bei jedem Aufruf ueberschrieben.
        """
        inhalt = ('\nimport bpy\n\n'
                  '# Import BVH\n'
                  'bpy.ops.import_anim.bvh(filepath=%s)\n'
                  'print("BVH loaded:", %s)\n'
                  % (repr(str(eintrag.path)), repr(str(eintrag.name))))
        pfad = str(ProjektTemp.verzeichnis()
                   / Bibliotheksendpunkte.BLENDER_SKRIPT)
        with open(pfad, 'w') as datei:
            datei.write(inhalt)
        return pfad
