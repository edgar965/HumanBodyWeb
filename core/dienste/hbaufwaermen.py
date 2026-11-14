# -*- coding: utf-8 -*-
u"""Hbaufwaermen — die HumanBody-Merker (Hautgewichte, Morphs) nach dem
Serverstart im Hintergrund fuellen.

BEFUND (Edgar, 22.09.2026 nachts: „immer noch 20 s bis zum laden der Seite
bvh Studio!!", dann „lade die tools beim start der Seite und halte die immer
im Speicher, refresh soll nur das Modell refreshen"): Jeder BVH-Studio-Start
ruft `Studiostart.starten()` → `character_core.humanbodyDatenLaden()` —
unabhaengig davon, ob das Projekt ueberhaupt eine HumanBody-Figur enthaelt
(TechnoDance ist reines Genesis 9). Im Log gemessen, frisch nach einem
Serverneustart: `/api/character/skin-weights/` 6,91 s, `/api/character/
morphs/` 4,27 s — beide mit einem eigenen Prozess-Zwischenspeicher
(`Skingewichte._propagiert_json`, `Testkern._morphdaten`), der beim
Neustart LEER ist und von der erstbesten Anfrage kalt gefuellt wird. Diese
Anfrage haelt dabei einen Anfrage-Thread ueber Sekunden fest — genau dann,
wenn parallel die eigentlich noetigen Genesis-9-Netz- und Retarget-Anfragen
laufen (dieselbe Fehlerklasse wie `G9aufwaermen`, siehe dort: „Jeder
Serverstart leert alle Merker im Prozess").

Deshalb, wie bei Genesis 9, ein Faden aus `core.apps.CoreConfig.ready()`, der
GENAU die Aufrufe vorab macht, die `Skelettdaten.hautgewichte`/
`Netzendpunkte.regler` je selbst machen wuerden — derselbe Zwischenspeicher,
derselbe Schluessel, garantierter Treffer. Ein Seiten-Refresh trifft den
Merker danach IMMER warm; „neu laden" baut dann nur noch die Figur, nicht
die Grunddaten.

Laeuft nur im Serverprozess des Autoreloaders (`RUN_MAIN`), nicht im
Beobachter, nicht bei `manage.py test`/`migrate` — siehe `G9aufwaermen.
angebracht`, dieselbe Regel.
"""
import logging
import threading
import time

logger = logging.getLogger('core')

__all__ = ['Hbaufwaermen']


class Hbaufwaermen:
    u"""Ein Faden, der die HumanBody-Merker (Hautgewichte, Morphs) fuellt."""

    _faden = None

    @classmethod
    def starten(cls):
        if cls._faden is not None and cls._faden.is_alive():
            return cls._faden
        cls._faden = threading.Thread(target=cls.laufen, name='hb-aufwaermen',
                                      daemon=True)
        cls._faden.start()
        return cls._faden

    @classmethod
    def schritte(cls):
        u"""`[(name, funktion)]` — genau die Aufrufe der echten Endpunkte."""
        from .charakterdaten import Charakterdaten
        from .skingewichte import Skingewichte
        from ..api.testfigur.testkern import Testkern
        return [
            # `Skelettdaten.hautgewichte` mit der Vorgabe (VORGABE_KOERPERTYP
            # 'Female_Caucasian' -> 'female') — derselbe Aufruf wie im View.
            ('hautgewichte female',
             lambda: Skingewichte.propagiert_json('female', Charakterdaten.unterteiler('female'))),
            # `Netzendpunkte.regler` (`/api/character/morphs/`) — vom Browser
            # ausschliesslich wegen `skin_colors` aufgerufen (`character_core.
            # js loadSkinColors`), zieht aber `Testkern.morphdaten()` mit.
            ('morphs', Testkern.morphdaten),
            # Karten-Kerne von Figur und Retarget (14.11.2026, Edgar: „auch kalt muss der torch umbau besser sein“): CUDA lädt jeden Kern erst beim ersten Aufruf, 40–90 ms
            # je Kern; das erste Retarget nach dem Start brauchte 1,6–2,1 s statt 0,25 s. Ein Retarget eines BVH mit zwei Bildern lädt alle — die Pirouette (457 Bilder)
            # danach 0,265 s DEF / 0,497 s Genesis 9 wie warm (`ProjektTemp/_wegwerf/hb_torch/retarget_vorlauf_probe.py`).
            ('figur mit Regler', cls._figur),
            ('retarget def', lambda: cls._retarget('def')),
            ('retarget genesis9', lambda: cls._retarget('genesis9')),
        ]

    @staticmethod
    def _figur():
        from .charakterdaten import Charakterdaten
        zustand = Charakterdaten.zustand('Female_Caucasian')
        namen = [m['name'] if isinstance(m, dict) else m for m in zustand.get_morph_list()][:2]
        for name in namen:
            zustand.set_morph(name, 0.3)
        zustand.compute()

    @staticmethod
    def _retarget(ziel):
        from django.conf import settings
        from .retargetdaten import Retargetdaten
        Retargetdaten(str(settings.OBJECTS_ROOT / 'animations' / 'bvh' / 'Mixamo' / 't_pose.bvh'), ziel=ziel)._rechnen()

    @classmethod
    def laufen(cls):
        t0 = time.time()
        zeiten = []
        for name, schritt in cls.schritte():
            t = time.time()
            try:
                schritt()
            except Exception as fehler:  # noqa: BLE001 — ein Schritt darf scheitern
                logger.warning('HumanBody aufwärmen, %s: %s', name, fehler)
                continue
            zeiten.append('%s %.1f s' % (name, time.time() - t))
        logger.info('HumanBody aufgewärmt in %.1f s: %s', time.time() - t0,
                    ', '.join(zeiten))
