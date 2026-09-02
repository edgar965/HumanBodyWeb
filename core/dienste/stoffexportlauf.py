# -*- coding: utf-8 -*-
"""Stoffexportlauf — der Kleider-Export von der Anfrage bis zur Antwort.

Herausgeloest aus `core/cloth_export_api.py` (Befund `freie-funktionen`,
Kriterium 1): sieben Funktionen auf Modulebene, keine Klasse. Der Zielpfad
selbst steht schon laenger in `Stoffexportziel`; hier kommen die uebrigen
Entscheidungen dazu.

DREI DINGE, DIE HIER ENTSCHIEDEN WERDEN
=======================================
1. **Der Ausgabeordner.** Erst die Studio-Einstellung (`studio_video_output`),
   und nur wenn die auf ein wirkliches Verzeichnis zeigt. Sonst
   `MEDIA_ROOT/cloth_exports` — ein Export darf nicht daran scheitern, dass in
   den Einstellungen ein Pfad von einem anderen Rechner steht.
2. **Der Motor** (`motoren()`). Ein unbekannter Name wird abgelehnt, statt im
   Unterprozess auf einen Fehler zu laufen, den niemand zuordnen kann.
3. **Der Unterschied zwischen „Anfrage kaputt" und „Szene nicht rechenbar".**
   Ein gescheiterter MOTOR bekommt Status 200 mit dem Log: Die Anfrage war in
   Ordnung, die Szene ging nicht. Ein 500 wuerde die Oberflaeche eine Stoerung
   melden lassen, wo der Nutzer sein Log braucht.
"""

import logging
import os

from django.conf import settings
from django.http import JsonResponse

from ..safe_paths import PfadAbgelehnt
from .stoffexportziel import Stoffexportziel

logger = logging.getLogger(__name__)


class Stoffexportlauf:
    """Ein Exportlauf: Motor pruefen, Szene lesen, Ziel bilden, antworten."""

    #: Die Motoren, die `collision.export_mp4` kennt.
    #:
    #: DIE LISTE STAND BIS ZUM 01.09.2026 ZWEIMAL — hier und in
    #: `collision/__init__.py`. Zwei Listen fuer dieselbe Sache heisst:
    #: Ein fuenfter Motor wird an einer Stelle eingetragen und an der
    #: anderen vergessen, und die Ablehnung kommt dann aus dem falschen
    #: Grund. Jetzt fragt diese Seite die andere.
    #:
    #: Gelesen wird ERST BEIM PRUEFEN, nicht beim Import: `collision`
    #: zieht numpy und die Szenenklassen nach, und der Django-Start soll
    #: das nicht bezahlen.
    ERSATZMOTOR = 'blender_eevee'
    ERSATZGUETE = 'medium'
    ERSATZORDNER = 'cloth_exports'

    @staticmethod
    def motoren():
        u"""Die gueltigen Motornamen — aus `collision.Motorwahl`."""
        from collision import Motorwahl
        return Motorwahl.namen()

    def __init__(self, rumpf):
        self.rumpf = rumpf
        self.motor = rumpf.get('engine', Stoffexportlauf.ERSATZMOTOR)
        self.guete = rumpf.get('quality', Stoffexportlauf.ERSATZGUETE)
        self.ziel = Stoffexportziel(rumpf, self.motor)

    # ------------------------------------------------------------- Einstellung

    @staticmethod
    def einstellungen():
        try:
            from ..models import AppSettings
            return AppSettings.load()
        except Exception:
            logger.warning('AppSettings nicht lesbar — Kleider-Export rechnet '
                           'mit Vorgaben', exc_info=True)
            return None

    @staticmethod
    def ausgabeordner():
        stand = Stoffexportlauf.einstellungen()
        gewaehlt = (stand.ui_prefs or {}).get('studio_video_output') if stand else None
        if gewaehlt and os.path.isdir(gewaehlt):
            return gewaehlt
        return os.path.join(str(settings.MEDIA_ROOT),
                            Stoffexportlauf.ERSATZORDNER)

    # ------------------------------------------------------------------ Pruefen

    def motorfehler(self):
        """Antwort, wenn der Motor unbekannt ist — sonst `None`."""
        if self.motor in Stoffexportlauf.motoren():
            return None
        return JsonResponse({'ok': False,
                             'error': f'unknown engine {self.motor}'}, status=400)

    def szene(self):
        """`(szene, None)` oder `(None, Fehlerantwort)`."""
        try:
            from collision.bridge import payload_to_scene_input
        except Exception as fehler:
            logger.exception('export_cloth: collision-Paket nicht importierbar')
            return None, JsonResponse(
                {'ok': False, 'error': f'import failed: {fehler}'}, status=500)
        try:
            return payload_to_scene_input(self.rumpf), None
        except Exception as fehler:
            logger.exception('payload_to_scene_input failed')
            return None, JsonResponse(
                {'ok': False, 'error': f'payload decode failed: {fehler}'},
                status=400)

    def zielpfad(self):
        """Vollstaendiger Ausgabepfad — oder eine 403-Antwort mit dem Grund."""
        try:
            ordner = self.ziel.ordner(Stoffexportlauf.ausgabeordner())
        except PfadAbgelehnt as fehler:
            return None, JsonResponse(
                {'ok': False, 'error': f'output_dir abgelehnt: {fehler}'},
                status=403)
        try:
            name = self.ziel.dateiname()
        except PfadAbgelehnt as fehler:
            return None, JsonResponse(
                {'ok': False, 'error': f'filename abgelehnt: {fehler}'},
                status=403)
        os.makedirs(ordner, exist_ok=True)
        return os.path.join(ordner, name), None

    # ----------------------------------------------------------------- Antwort

    def antwort(self, ergebnis, pfad, sekunden):
        gemeinsam = {'engine': self.motor, 'quality': self.guete,
                     'elapsed_sec': sekunden}
        if not ergebnis.get('ok'):
            return JsonResponse({'ok': False, **gemeinsam,
                                 'log': ergebnis.get('log', ''),
                                 'error': 'engine failed — see log'}, status=200)
        return JsonResponse({'ok': True, **gemeinsam, 'output': pfad,
                             'url': Stoffexportziel.adresse(pfad),
                             'duration_sec': ergebnis.get('duration_sec', 0)})
