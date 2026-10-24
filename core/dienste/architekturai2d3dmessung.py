# -*- coding: utf-8 -*-
"""Architekturai2d3dmessung — was für 2d-3d-AI gemessen ist, mit Quelle (24.10.2026), für Hilfe → Architektur → 2d-3d-AI.

Zwei Arten: **von der Platte beim Aufruf** (Netzvergleich Tripo/Hunyuan gegen die Wahrheit, Zeiten des Bildgenerators und von Hunyuan, Pakete der Umgebung python10) und **festgehalten mit Datum**
(Werte, die im Browser gemessen wurden — die Umriss-Deckung auf `/2d-3d-AI/<job>/` — und die Zählung der Garderobe über die API). Festgehaltenes trägt `quelle`; die Seite zeigt sie.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Architekturai2d3dmessung']


class Architekturai2d3dmessung:
    #: Umriss-Deckung (Schnitt / Vereinigung) Rendering ↔ Foto, je Perspektive vorne, links, rechts, hinten — im Chrome auf der Jobseite abgelesen, 24.10.2026 (`Ai2d3dvergleich`).
    DECKUNG = (
        {'job': 'OlesiaWalk', 'figur': 'Wahrheit (Gegenprobe)', 'mittel': 97.9, 'je': (97.0, 98.3, 97.8, 98.5)},
        {'job': 'Matt1', 'figur': 'Wahrheit (Gegenprobe)', 'mittel': 98.5, 'je': None},
        {'job': 'OlesiaWalk', 'figur': 'Messlatte A (Tripo → Mesh3D-AI)', 'mittel': 86.8, 'je': (86.7, 86.7, 85.6, 88.0)},
    )
    DECKUNG_QUELLE = 'Chrome, /2d-3d-AI/olesiawalk/ und /matt1/, 24.10.2026 — Maske Foto: Abstand zum Grund > 9; Rendering: zweiter Durchgang auf Grün'
    #: Der erste Versuch derselben Messung (Schwelle 36 auf beiden Bildern) — warum die Gegenprobe Pflicht ist.
    FEHLMESSUNG = ('Erste Fassung der Messung: Wahrheit 51,5 %, Messlatte A 55,7 % — die Schwelle 36 warf 91.049 von 529.623 Figurpixeln weg (schwarzes Shirt, dunkle Jeans); '
                   'gemessen mit _wegwerf/ai2d3d/maske_messen.py an Olesia1_vorne.jpg.')
    #: Garderobe und Posen der Charakter-Seite (`/api/character/genesis9-figur/garderobe/` und `…/posen/`), gezählt 24.10.2026 mit `_wegwerf/ai2d3d/vorrat_zaehlen.py`.
    VORRAT = {'stuecke': 631, 'kleidung': 544, 'requisit': 55, 'haar': 32, 'posen': 216, 'posengruppen': 12, 'quelle': 'API der Charakter-Seite, gezählt 24.10.2026'}
    PAKETE = ('torch', 'nvdiffrast', 'pytorch3d', 'timm', 'transformers')

    @staticmethod
    def _json(pfad):
        try:
            return json.loads(Path(pfad).read_text(encoding='utf-8'))
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as fehler:
            logger.warning('Architekturai2d3dmessung: %s nicht lesbar (%s)', pfad, fehler)
            return None

    @classmethod
    def netzvergleich(cls):
        """Tripo3D und Hunyuan3D-2mv aus Edgars vier Fotos von OlesiaWalk gegen die Wahrheit (`_bild3d/OlesiaWalk_tripovergleich/vergleich.json`, gerechnet 23.10.2026)."""
        d = cls._json(Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_bild3d' / 'OlesiaWalk_tripovergleich' / 'vergleich.json')
        if not d:
            return None
        zeilen = []
        for schluessel, name in (('tripo', 'Tripo3D'), ('hunyuan', 'Hunyuan3D-2mv')):
            v = d.get(schluessel) or {}
            n, w = v.get('netz_zu_wahrheit') or {}, v.get('wahrheit_zu_netz') or {}
            zeilen.append({'name': name, 'dreiecke': v.get('dreiecke'), 'n_mittel': n.get('mittel'), 'n_p95': n.get('p95'), 'w_mittel': w.get('mittel'), 'w_p95': w.get('p95'),
                           'ueber20': round(100 * v['wahrheit_ueber_20mm'], 1) if v.get('wahrheit_ueber_20mm') is not None else None})
        return {'job': d.get('job'), 'punkte': d.get('punkte'), 'zeilen': zeilen}

    @classmethod
    def zeiten(cls):
        """Ein Bildersatz und ein Hunyuan-Netz der künstlichen Tripo-Netze (`_bild3d/Damira0_0001`), so wie die Kette sie ablegt."""
        probe = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_bild3d' / 'Damira0_0001'
        bilder, netz = cls._json(probe / 'bilder' / 'bilder.json') or {}, cls._json(probe / 'netz.json') or {}
        return {'bilder_s': bilder.get('dauer_s'), 'groesse': bilder.get('groesse'), 'yfov': bilder.get('yfov_grad'), 'netz_s': netz.get('dauer_s'),
                'flaechen': netz.get('flaechen'), 'modell': netz.get('formmodell')}

    @classmethod
    def pakete(cls):
        """Fassungen der Pakete in python10 aus den Namen der `*.dist-info`-Ordner (nichts importiert)."""
        ordner = Path(settings.TOOLS_ROOT) / 'python10' / 'Lib' / 'site-packages'
        aus = {}
        for name in cls.PAKETE:
            treffer = sorted(ordner.glob('%s-*.dist-info' % name))
            aus[name] = treffer[-1].name[len(name) + 1:-len('.dist-info')] if treffer else None
        return aus
