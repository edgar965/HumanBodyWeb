# -*- coding: utf-8 -*-
"""G9hautfaltenablage — die Falten-Normalenkarten (`G9hautfalten`) je Geschlecht: Stand, Dateien, Bau im Hintergrund.

Der Bau dauert gemessen 46 s je Geschlecht (17.10.2026, `ProjektTemp/_wegwerf/alter/falten_bauen.py`) und läuft
höchstens einmal je Geschlecht und Prozess, in einem eigenen Faden — die Anfrage des Browsers wartet nicht. Die Liste
(`hautfalten_<geschlecht>_v<Fassung>.json`) wird als LETZTES geschrieben: sie sagt „fertig". Ohne sie gibt es kein
Ergebnis (`stand: baut`), nie die Kacheln eines anderen Laufs (`artefakte-benennen.md`). Ein Fehler steht im Log und
im Stand (`fehler`), der nächste Abruf versucht es erneut.
"""
import json
import logging
import threading

from .g9hautfalten import G9hautfalten

logger = logging.getLogger('core')

__all__ = ['G9hautfaltenablage']


class G9hautfaltenablage:
    """`stand(geschlecht)` → `{stand: fertig|baut|fehler, kacheln: {kachel: {steigung_p99, …}}}`."""

    _schloss = threading.Lock()
    _laeuft = set()
    _fehler = {}

    @staticmethod
    def geschlecht(wert):
        return 'male' if str(wert).lower().startswith('m') else 'female'

    @classmethod
    def liste(cls, geschlecht):
        """Die geschriebene Liste oder None."""
        pfad = G9hautfalten.listenpfad(geschlecht)
        if not pfad.is_file():
            return None
        try:
            liste = json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Hautfalten: Liste %s unlesbar (%s)', pfad, fehler)
            return None
        return liste if all(G9hautfalten.bildpfad(geschlecht, k).is_file() for k in liste.get('kacheln', {})) else None

    @classmethod
    def stand(cls, geschlecht):
        """Der Stand für den Browser; stößt den Bau an, wenn es nichts gibt und keiner läuft."""
        geschlecht = cls.geschlecht(geschlecht)
        liste = cls.liste(geschlecht)
        if liste is not None:
            return {'stand': 'fertig', 'geschlecht': geschlecht, 'fassung': liste['fassung'], 'kacheln': liste['kacheln']}
        with cls._schloss:
            if geschlecht not in cls._laeuft:
                cls._laeuft.add(geschlecht)
                cls._fehler.pop(geschlecht, None)
                threading.Thread(target=cls._bauen, args=(geschlecht,), name='hautfalten-' + geschlecht, daemon=True).start()
        if geschlecht in cls._fehler:
            return {'stand': 'fehler', 'geschlecht': geschlecht, 'fehler': cls._fehler[geschlecht], 'kacheln': {}}
        return {'stand': 'baut', 'geschlecht': geschlecht, 'kacheln': {}}

    @classmethod
    def _bauen(cls, geschlecht):
        try:
            G9hautfalten(geschlecht).bauen()
        except Exception as fehler:                          # noqa: BLE001 — der Faden darf nie still sterben
            logger.exception('Hautfalten %s nicht gebaut', geschlecht)
            cls._fehler[geschlecht] = str(fehler) or type(fehler).__name__
        finally:
            with cls._schloss:
                cls._laeuft.discard(geschlecht)

    @classmethod
    def bild(cls, geschlecht, kachel):
        """Pfad der Kachel oder None — nur, wenn die Liste sie nennt."""
        geschlecht = cls.geschlecht(geschlecht)
        liste = cls.liste(geschlecht)
        if liste is None or str(int(kachel)) not in liste['kacheln']:
            return None
        return G9hautfalten.bildpfad(geschlecht, kachel)
