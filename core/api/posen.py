# -*- coding: utf-8 -*-
"""Posen: auflisten, lesen, verwalten.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

DABEI GEFUNDEN (27.08.2026): DIE PFADPRUEFUNG WAR EIN ZEICHENKETTENVERGLEICH
============================================================================
`_check_pose_path` prueft mit

    if str(rp).startswith(str(root_resolved)):

Genau diese Schreibweise ist im Projekt am 12.08.2026 ueberall ersetzt worden:
Ein Nachbarverzeichnis mit gleichem Namensanfang besteht sie. `poseData` und
`poseData_evil` beginnen gleich — der zweite Ordner haette also geloescht und
umbenannt werden koennen. `Path.is_relative_to` vergleicht Pfadteile statt
Zeichen und kennt diesen Fall nicht.

UMBAU 27.08.2026 (Befund `freie-funktionen`): drei freie Funktionen, dazu eine
Funktion IN einer Funktion und ein `logging.getLogger` mitten im Rumpf.
"""

import logging
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.anfragerumpf import Anfragerumpf

logger = logging.getLogger('core')


class Posen:
    """Die Posendateien unter `poseData/<kategorie>/<name>.json`."""

    #: Die A-Pose ohne Datei — nur mit Absatz traegt sie Knochen.
    RUHELAGE = 'ruhelage'
    #: Wie `Skelettdaten.VORGABE_KOERPERTYP`.
    VORGABE_KOERPERTYP = 'Female_Caucasian'

    @staticmethod
    def wurzel():
        return Path(str(settings.HUMANBODY_DATA_DIR)).parent / 'poseData'

    @classmethod
    def _geprueft(cls, kategorie, name):
        """Der aufgeloeste Pfad — oder None, wenn er die Wurzel verlaesst."""
        wurzel = cls.wurzel().resolve()
        try:
            ziel = (cls.wurzel() / kategorie / ('%s.json' % name)).resolve()
        except OSError, ValueError:
            # Kategorie oder Name kommen aus dem Anfragerumpf; ein Pfad, den
            # das Betriebssystem nicht aufloesen kann, ist eine ABGELEHNTE
            # Eingabe — und die will man sehen, wenn jemand sie probiert.
            logger.warning('[pose-manage] Pfad nicht aufloesbar: %s/%s', kategorie, name, exc_info=True)
            return None
        return ziel if ziel.is_relative_to(wurzel) else None

    # --------------------------------------------------------------- Lesen

    @staticmethod
    @require_GET
    def liste(request):
        """Die Posen von CharMorph/MB-Lab, nach Kategorie."""
        from humanbody_core.pose import list_poses

        # Ohne die Dateipfade — die gehen den Browser nichts an.
        return JsonResponse(
            {
                'categories': {
                    kategorie: [{'id': p['id'], 'name': p['name']} for p in posen]
                    for kategorie, posen in list_poses().items()
                }
            }
        )

    @staticmethod
    @require_GET
    def pose(request, pose_id):
        """Die Quaternionen EINER Pose, auf DEF-Knochennamen abgebildet.

        Hiess bis zum 17.08.2026 `get_pose`. Umbenannt wegen
        `namens-dubletten` (Kriterium 7): Fuer „lesen" gab es im Projekt zwei
        Schreibweisen — `get_…` hier, `…_load` bei `studio_project_load`. Die
        Mehrheit der Endpunkte stellt die Sache vor die Taetigkeit
        (`studio_project_list`, `cloth_preset_list`), also gilt die. Der
        URL-PFAD bleibt unveraendert, das Frontend ruft ihn direkt auf.

        MIT ABSATZ (11.09.2026, Edgar: „das Programm soll die Pose
        ändern"): `?winkel_grad=&sprengung_grad=&hebung_cm=&plateau_cm=`
        rechnet die Fussbeugung eines Absatzschuhs in die Pose ein
        (`dienste/absatzpose.py`), `body_type` waehlt das Skelett. Die
        Pose `ruhelage` ist die A-Pose ohne Datei — mit Absatz traegt sie
        nur die Fuesse. `hebung_m` sagt dem Betrachter, wie hoch die Figur
        dafuer steht; eine Pose selbst kennt keine Verschiebung.
        """
        from humanbody_core.pose import load_pose

        from ..dienste.absatzpose import Absatzpose
        from ..dienste.charakterdaten import Charakterdaten

        if pose_id == Posen.RUHELAGE:
            knochen = {}
        else:
            try:
                knochen = load_pose(pose_id).def_bones
            except FileNotFoundError:
                return JsonResponse({'error': 'Pose not found: %s' % pose_id}, status=404)
        geschlecht = Charakterdaten.geschlecht_zu(request.GET.get('body_type', Posen.VORGABE_KOERPERTYP))
        absatz = Absatzpose.aus_anfrage(request.GET, geschlecht)
        if absatz is not None:
            knochen = absatz.einrechnen(knochen)
        return JsonResponse(
            {
                'pose_id': pose_id,
                'bones': knochen,  # {DEF-Name: [w,x,y,z]}
                'threejs': Absatzpose.to_threejs(knochen),  # {DEF-Name: [x,y,z,w]}
                'absatz': absatz.beschreibung() if absatz else None,
                'hebung_m': absatz.hebung_m if absatz else 0.0,
                # Die reinen Fussdeltas, damit der Betrachter sie bei einer
                # laufenden Animation je Bild nachmischt (`posenabsatz.js`).
                'absatz_deltas': (Absatzpose.to_threejs(absatz.deltas()) if absatz else {}),
            }
        )

    # ----------------------------------------------------------- Verwalten

    @staticmethod
    @csrf_exempt
    @require_POST
    def verwalten(request):
        """Posendateien umbenennen oder loeschen.

        POST /api/character/pose-manage/
        { action: "rename"|"delete", category, name, new_name }
        { action: "save", name, bones: {DEF-Name: [x, y, z, w]} }  (17.10.2026)

        `save` legt die Stellung einer Figur als neue Pose unter `poseData/eigene/`
        ab (`Posenablage`) — die Kategorie bestimmt der Server, nie der Betrachter.
        """
        daten, fehler = Anfragerumpf.lesen(request)
        if fehler:
            return fehler
        aktion = daten.get('action', '')
        kategorie = daten.get('category', '')
        name = daten.get('name', '')
        logger.info('[pose-manage] action=%s, category=%s, name=%s', aktion, kategorie, name)
        if aktion == 'save':
            return Posen._speichern(name, daten.get('bones'))
        if aktion == 'delete':
            return Posen._loeschen(kategorie, name)
        if aktion == 'rename':
            return Posen._umbenennen(kategorie, name, daten.get('new_name', '').strip())
        return JsonResponse({'error': 'Unknown action: %s' % aktion}, status=400)

    @staticmethod
    def _speichern(name, drehungen):
        from ..dienste.posenablage import Posenablage, PosenFehler

        try:
            ergebnis = Posenablage.speichern(Posen.wurzel(), name, drehungen)
        except PosenFehler as fehler:
            return JsonResponse({'error': fehler.text}, status=fehler.kennzahl)
        return JsonResponse({'ok': True, **ergebnis})

    @staticmethod
    def _loeschen(kategorie, name):
        """Seit 17.10.2026 in den Papierkorb `poseData/.trash/` statt von der Platte (`Posenordner`)."""
        from ..dienste.posenablage import PosenFehler
        from ..dienste.posenordner import Posenordner

        if not kategorie or not name:
            return JsonResponse({'error': 'category + name required'}, status=400)
        try:
            return JsonResponse(Posenordner.loeschen(Posen.wurzel(), f'{kategorie}/{name}'))
        except PosenFehler as fehler:
            return JsonResponse({'error': fehler.text}, status=fehler.kennzahl)

    @staticmethod
    def _umbenennen(kategorie, name, neuer_name):
        from ..dienste.posenordner import Posenordner

        if not kategorie or not name or not neuer_name:
            return JsonResponse({'error': 'category, name, new_name required'}, status=400)
        if f'{kategorie}/{name}' in Posenordner.FESTE_POSEN or '/' in neuer_name or neuer_name.startswith('.'):
            return JsonResponse({'error': f'„{name}" lässt sich so nicht umbenennen.'}, status=409)
        alt = Posen._geprueft(kategorie, name)
        neu = Posen._geprueft(kategorie, neuer_name)
        if not alt or not alt.is_file():
            return JsonResponse({'error': 'Pose not found'}, status=404)
        if not neu:
            return JsonResponse({'error': 'Invalid new path'}, status=400)
        if neu.exists():
            return JsonResponse({'error': '%s.json exists already' % neuer_name}, status=409)
        alt.rename(neu)
        logger.info('[pose-manage] Renamed: %s -> %s', alt, neu)
        return JsonResponse({'ok': True, 'new_name': neuer_name})
