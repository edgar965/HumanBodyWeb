# -*- coding: utf-8 -*-
u"""Figurexport — die fertige Figur als GLB für Roomguest und jeden anderen Abnehmer.

WARUM (05.09.2026)
==================
Roomguest (A:\\Roomguest, Unity-Client für Browser, Android und iOS) soll die
in HumanBodyWeb gestaltete Figur spielen statt einer fremden Avatar-Bibliothek
(UMA). Der Viewer hält die Figur fertig als SkinnedMesh mit dem DEF-Skelett;
`static/viewer/viewer/figur_export.js` schreibt daraus per Three.js
GLTFExporter eine GLB (Netz, Skin, Werkstoffe mit Texturen, Haare, Garderobe)
und legt sie hier ab. Unity lädt sie zur Laufzeit (glTFast).

    POST /api/character/figur-glb/<name>/ablegen/   Feld `glb` (multipart)
                                                     -> {name, bytes, pfad}
    GET  /api/character/figur-glb/                   {figuren: [{name, bytes, geaendert}], ordner}
    GET  /api/character/figur-glb/<name>/            die Datei, model/gltf-binary

Ablage: `settings.HUMANBODY_FIGUR_EXPORT_DIR` (HumanBody/data/figur_exports,
wie `garment_exports`). Der Name kommt aus der Adresse und geht durch
`Modellpfad.geprueft` — dieselbe Prüfung wie bei Modellen und Frisuren.
"""

import logging
import os
import re
import time

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.modellpfad import Modellpfad

logger = logging.getLogger('core')


class Figurexport:
    """GLB-Dateien im Figurenordner: ablegen, auflisten, ausliefern."""

    ENDUNG = '.glb'
    FELD = 'glb'
    #: Die ersten vier Bytes jeder GLB-Datei (Magic).
    MAGIE = b'glTF'
    MAX_BYTES = 256 * 1024 * 1024
    TYP = 'model/gltf-binary'
    ZEITFORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def _ordner():
        return str(settings.HUMANBODY_FIGUR_EXPORT_DIR)

    @staticmethod
    def _pfad(name):
        """Der geprüfte Dateipfad zum Namen — oder None."""
        # Nur Buchstaben, Ziffern, Leerzeichen, Binde- und Unterstriche (wie
        # `Modelldateien.modell_sichern`).
        sauber = re.sub(r'[^\w\s\-]', '', name or '').strip()
        if not sauber:
            return None
        return Modellpfad.geprueft(Figurexport._ordner(), sauber, Figurexport.ENDUNG)

    @staticmethod
    @csrf_exempt
    @require_POST
    def ablegen(request, name):
        """Eine GLB unter dem Namen schreiben (überschreibt)."""
        pfad = Figurexport._pfad(name)
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        datei = request.FILES.get(Figurexport.FELD)
        if datei is None:
            return JsonResponse({'error': 'Feld "%s" fehlt' % Figurexport.FELD},
                                status=400)
        if datei.size > Figurexport.MAX_BYTES:
            return JsonResponse({'error': 'Zu groß: %d Bytes, erlaubt sind %d'
                                 % (datei.size, Figurexport.MAX_BYTES)}, status=400)
        inhalt = datei.read()
        if not inhalt.startswith(Figurexport.MAGIE):
            return JsonResponse({'error': 'Keine GLB-Datei (Kopf ist nicht "glTF")'},
                                status=400)
        os.makedirs(Figurexport._ordner(), exist_ok=True)
        with open(pfad, 'wb') as ziel:
            ziel.write(inhalt)
        logger.info('Figurexport: %s abgelegt (%d Bytes)', pfad, len(inhalt))
        return JsonResponse({
            'name': os.path.splitext(os.path.basename(pfad))[0],
            'bytes': len(inhalt),
            'pfad': pfad,
        })

    @staticmethod
    @require_GET
    def liste(request):
        """Alle abgelegten Figuren mit Größe und Zeitpunkt."""
        ordner = Figurexport._ordner()
        figuren = []
        if os.path.isdir(ordner):
            for dateiname in sorted(os.listdir(ordner)):
                if not dateiname.endswith(Figurexport.ENDUNG):
                    continue
                stand = os.stat(os.path.join(ordner, dateiname))
                figuren.append({
                    'name': dateiname[:-len(Figurexport.ENDUNG)],
                    'bytes': stand.st_size,
                    'geaendert': time.strftime(Figurexport.ZEITFORMAT,
                                               time.localtime(stand.st_mtime)),
                })
        return JsonResponse({'figuren': figuren, 'ordner': ordner})

    @staticmethod
    @require_GET
    def datei(request, name):
        """Die GLB einer Figur."""
        pfad = Figurexport._pfad(name)
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        if not os.path.isfile(pfad):
            return JsonResponse({'error': 'Keine Figur "%s"' % name}, status=404)
        return FileResponse(open(pfad, 'rb'), content_type=Figurexport.TYP,
                            filename=os.path.basename(pfad))
