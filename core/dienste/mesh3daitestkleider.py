# -*- coding: utf-8 -*-
"""Mesh3daitestkleider — Kleider und Bestandteile eines Tests von Mesh3D-AI, je Stück wählbar aus zwei Wegen (17.10.2026 nachts).

Edgar: „Kleider und assets — können wir beide Optionen bauen? Per Option umschalten auf b oder a … Nach dem Bauen müsste ich im Ergebnis View festlegen können, ob ich ein Kleidungsstück in der ersten Option
oder zweiten Option haben möchte. Also Toggle für jedes Kleidungsstück für beide Optionen und Button zum übernehmen von Option a oder b in das End-Modell, mit speichern des Modells“.

    a  Katalog: ein Stück der Garderobe, auf der vorhergesagten Figur gebaut (gewählt durch Messung gegen das Stück aus dem Netz — `ProjektTemp/_wegwerf/mesh3dai_kleider_katalog.py`)
    b  aus dem Netz: das Objekt, das ein voller Mesh-3D-Lauf auf derselben Datei ausgeschnitten hat, in die Ruhelage der vorhergesagten Figur übertragen (`mesh3dai_kleider.py`)

Ablage `_test/<kennung>/kleider_<geschlecht>/stuecke.json` (+ `a|b/<id>/anzeige/`, Format `Mesh3daiflaechennetz`). Die Wahl steht in `einstellung.json` des Tests:
`kleider_vorgabe` (`a` | `b`, Vorgabe `b` — Weg a gibt es nur, wo der Katalog etwas gefunden hat) und `kleider_wahl` `{geschlecht: {id: 'a' | 'b' | 'aus'}}` (nur, was vom Nutzer abweicht).
Wirksam je Stück: die eigene Wahl, sonst die Vorgabe, sonst der andere Weg, sonst „aus“ — ein Weg, den das Stück nicht hat, gilt nie.
"""

import json
import logging
import re

from ..atomic_write import AtomarSchreiber
from .mesh3daiflaechennetz import Mesh3daiflaechennetz
from .mesh3daitest import Mesh3daitest

logger = logging.getLogger(__name__)

__all__ = ['Mesh3daitestkleider']


class Mesh3daitestkleider:
    WEGE = ('a', 'b')
    WAHLEN = ('a', 'b', 'aus')
    VORGABE = 'b'
    ID = re.compile(r'^[a-z0-9_]{1,64}$')

    @classmethod
    def ordner(cls, kennung, geschlecht):
        p = Mesh3daitest.pfad(kennung)
        if p is None or geschlecht not in Mesh3daitest.GESCHLECHTER:
            return None
        return p / ('kleider_%s' % geschlecht)

    @staticmethod
    def einstellung(p):
        try:
            wert = json.loads((p / 'einstellung.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            wert = {}
        return wert if isinstance(wert, dict) else {}

    @classmethod
    def einstellung_aendern(cls, p, **felder):
        """Liest `einstellung.json`, setzt die Felder, schreibt in einem Zug (`geschlecht` und die Kleiderwahl teilen sich die Datei)."""
        wert = cls.einstellung(p)
        wert.update(felder)
        AtomarSchreiber.json_schreiben(p / 'einstellung.json', wert)
        return wert

    @classmethod
    def vorgabe(cls, p):
        v = cls.einstellung(p).get('kleider_vorgabe')
        return v if v in cls.WEGE else cls.VORGABE

    @classmethod
    def wirksam(cls, stueck, eigene, vorgabe):
        """Der Weg, den das Stück zeigt: eigene Wahl, sonst Vorgabe, sonst der andere Weg, sonst „aus“."""
        da = [w for w in cls.WEGE if isinstance(stueck.get(w), dict) and not stueck[w].get('fehler')]
        if eigene == 'aus':
            return 'aus'
        for w in (eigene, vorgabe, *cls.WEGE):
            if w in da:
                return w
        return 'aus'

    @classmethod
    def liste(cls, kennung, geschlecht):
        """`{vorgabe, quelle, grund, stuecke: [{id, name, art, region, a, b, wahl, eigene_wahl}]}` oder None (Test fehlt). Ohne Ablage: leere Liste mit Grund."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None:
            return None
        p = ordner.parent
        vorgabe = cls.vorgabe(p)
        try:
            kopf = json.loads((ordner / 'stuecke.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {'vorgabe': vorgabe, 'stuecke': [], 'quelle': None,
                    'grund': 'Für diesen Test sind noch keine Kleider gerechnet (ProjektTemp/_wegwerf/mesh3dai_kleider.py).'}
        eigene = ((cls.einstellung(p).get('kleider_wahl') or {}).get(geschlecht) or {})
        stuecke = []
        for st in kopf.get('stuecke') or []:
            eintrag = {k: st.get(k) for k in ('id', 'name', 'art', 'region', 'bewegung', 'kontakt', 'a', 'b')}
            for weg in cls.WEGE:
                # Eine Adresse nur, wo ein Anzeigenetz liegt — „Haut a“ ist die Figur selbst und hat keins (`mesh3dai_kleider_haut.py`).
                if isinstance(eintrag.get(weg), dict) and not eintrag[weg].get('fehler') and (ordner / weg / st['id'] / 'anzeige' / 'netz.npz').is_file():
                    eintrag[weg] = dict(eintrag[weg], netz='/api/mesh3dai/test/%s/kleid/%s/%s/%s' % (kennung, geschlecht, weg, st['id']))
            eintrag['eigene_wahl'] = eigene.get(st['id'])
            eintrag['wahl'] = cls.wirksam(st, eintrag['eigene_wahl'], vorgabe)
            stuecke.append(eintrag)
        return {'vorgabe': vorgabe, 'stuecke': stuecke, 'quelle': kopf.get('quelle'), 'grund': kopf.get('grund'), 'gerechnet': kopf.get('gerechnet'),
                'katalog': kopf.get('katalog')}

    @classmethod
    def wahl_setzen(cls, kennung, geschlecht, stueck, wahl):
        """Wahl EINES Stücks; `stueck` = None und `wahl` ∈ {a, b}: alle Stücke auf diesen Weg (eigene Wahlen fallen weg, die Vorgabe wird dieser Weg). False bei ungültiger Eingabe."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None or wahl not in cls.WAHLEN:
            return False
        p = ordner.parent
        alle = dict(cls.einstellung(p).get('kleider_wahl') or {})
        if stueck is None:
            if wahl not in cls.WEGE:
                return False
            alle[geschlecht] = {}
            cls.einstellung_aendern(p, kleider_wahl=alle, kleider_vorgabe=wahl)
            return True
        if not cls.ID.match(str(stueck)):
            return False
        je = dict(alle.get(geschlecht) or {})
        je[str(stueck)] = wahl
        alle[geschlecht] = je
        cls.einstellung_aendern(p, kleider_wahl=alle)
        return True

    @classmethod
    def vorgabe_setzen(cls, kennung, vorgabe):
        p = Mesh3daitest.pfad(kennung)
        if p is None or vorgabe not in cls.WEGE:
            return False
        cls.einstellung_aendern(p, kleider_vorgabe=vorgabe)
        return True

    @classmethod
    def stueck_ordner(cls, kennung, geschlecht, weg, stueck):
        """Ordner des Stücks relativ zu `mesh3dai/` (für `Mesh3daiflaechennetz`) oder None — alle Teile kommen aus der Adresse und werden geprüft."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None or weg not in cls.WEGE or not cls.ID.match(str(stueck)):
            return None
        if not (ordner / weg / stueck / 'anzeige' / 'netz.npz').is_file():
            return None
        return '_test/%s/kleider_%s/%s/%s' % (kennung, geschlecht, weg, stueck)

    @classmethod
    def paket(cls, kennung, geschlecht, weg, stueck):
        modell = cls.stueck_ordner(kennung, geschlecht, weg, stueck)
        return Mesh3daiflaechennetz.paket(modell) if modell else None

    @classmethod
    def bild(cls, kennung, geschlecht, weg, stueck, name):
        modell = cls.stueck_ordner(kennung, geschlecht, weg, stueck)
        return Mesh3daiflaechennetz.bild(modell, name) if modell else None
