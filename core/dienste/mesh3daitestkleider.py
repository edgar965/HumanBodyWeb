# -*- coding: utf-8 -*-
"""Mesh3daitestkleider — Kleider und Bestandteile eines Tests von Mesh3D-AI, je Stück wählbar aus mehreren Wegen (17.10.2026 nachts; KI-Wege 20.10.2026).

Edgar: „Kleider und assets — können wir beide Optionen bauen? Per Option umschalten auf b oder a … Nach dem Bauen müsste ich im Ergebnis View festlegen können, ob ich ein Kleidungsstück in der ersten Option
oder zweiten Option haben möchte. Also Toggle für jedes Kleidungsstück für beide Optionen und Button zum übernehmen von Option a oder b in das End-Modell, mit speichern des Modells“.

    a  Katalog: ein Stück der Garderobe, auf der vorhergesagten Figur gebaut (gewählt durch Messung gegen das Stück aus dem Netz — `ProjektTemp/_wegwerf/mesh3dai_kleider_katalog.py`)
    b  aus dem Netz: das Objekt, das ein voller Mesh-3D-Lauf auf derselben Datei ausgeschnitten hat, in die Ruhelage der vorhergesagten Figur übertragen (`mesh3dai_kleider.py`)
    k, s, h  aus der KI von Mesh3D-AI (`Mesh3daitestkikleider`: geschnitten, GarmentCode-Schnitt, Frisur) — eigene Zeilen aus `ki.json`

Ablage `_test/<kennung>/kleider_<geschlecht>/stuecke.json` (+ `a|b/<id>/anzeige/`, Format `Mesh3daiflaechennetz`) und `ki.json` (+ `k|s|h/<id>/anzeige/`). Die Wahl steht in `einstellung.json` des Tests:
`kleider_vorgabe` (`ki` | `a` | `b`, Vorgabe `ki` — Edgar 19.10.2026: „das Ergebnis soll direkt aus der KI kommen“) und `kleider_wahl` `{geschlecht: {id: weg | 'aus'}}` (nur, was vom Nutzer abweicht).
Wirksam je Stück: die eigene Wahl; sonst bei Vorgabe `ki` die KI-Zeilen in ihrer Reihenfolge (`ki_vorgabe`) ohne die Wege aus der Bibliothek (h, seit 20.10.2026 nur auf eigene Wahl),
die Zeilen des Mesh-3D-Laufs aus (die Haut: Haut der Figur); bei Vorgabe a/b die
Zeilen des Mesh-3D-Laufs wie bisher, die KI-Zeilen aus. Ein Weg, den das Stück nicht hat, gilt nie.
"""

import json
import logging
import re

from ..atomic_write import AtomarSchreiber
from .mesh3daiflaechennetz import Mesh3daiflaechennetz
from .mesh3daitest import Mesh3daitest
from .mesh3daitestkikleider import Mesh3daitestkikleider
from .mesh3daitestkleidspeichern import Mesh3daitestkleidspeichern

logger = logging.getLogger(__name__)

__all__ = ['Mesh3daitestkleider']


class Mesh3daitestkleider:
    WEGE = ('a', 'b') + Mesh3daitestkikleider.WEGE
    WAHLEN = WEGE + ('aus',)
    VORGABEN = ('ki', 'a', 'b')
    VORGABE = 'ki'
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
        return v if v in cls.VORGABEN else cls.VORGABE

    @classmethod
    def wirksam(cls, stueck, eigene, vorgabe):
        """Der Weg, den das Stück zeigt (Kopf der Datei)."""
        da = [w for w in cls.WEGE if isinstance(stueck.get(w), dict) and not stueck[w].get('fehler')]
        if eigene == 'aus':
            return 'aus'
        if eigene in da:
            return eigene
        ki = stueck.get('quelle') == 'ki'
        if vorgabe == 'ki':
            if ki:          # nie ein Stück aus der Bibliothek (h) von selbst — auch nicht, wenn eine ältere `ki.json` es vorn führt
                # eine LEERE Folge heißt „die KI baut diese Art nicht“ (`ki_aus`, Schichtkopf) — nur eine fehlende Folge (ältere `ki.json`) nimmt alle Wege
                folge = stueck.get('ki_vorgabe')
                return next((w for w in (Mesh3daitestkikleider.WEGE if folge is None else folge) if w in da and w not in Mesh3daitestkikleider.AUS_DER_BIBLIOTHEK), 'aus')
            if stueck.get('art') == 'haut':          # eine Figur ohne Haut gibt es nicht: die Haut der Figur
                return next((w for w in ('a', 'b') if w in da), 'aus')
            return 'aus'
        if ki:
            return 'aus'
        return next((w for w in (vorgabe, 'a', 'b') if w in da), 'aus')

    @classmethod
    def liste(cls, kennung, geschlecht):
        """`{vorgabe, quelle, grund, stuecke: [{id, name, art, region, a, b, k, s, h, wahl, eigene_wahl, quelle}], ki}` oder None (Test fehlt)."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None:
            return None
        p = ordner.parent
        vorgabe = cls.vorgabe(p)
        try:
            kopf = json.loads((ordner / 'stuecke.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            kopf = {'stuecke': [], 'quelle': None, 'grund': 'Für diesen Test sind die Wege a/b nicht gerechnet (ProjektTemp/_wegwerf/mesh3dai_kleider.py).'}
        ki_zeilen, ki_info = Mesh3daitestkikleider.zeilen(ordner, kennung, geschlecht)
        eigene = ((cls.einstellung(p).get('kleider_wahl') or {}).get(geschlecht) or {})
        stuecke = []
        for st in kopf.get('stuecke') or []:
            eintrag = {k: st.get(k) for k in ('id', 'name', 'art', 'region', 'bewegung', 'kontakt', 'a', 'b')}
            eintrag['quelle'] = 'mesh3d'
            for weg in ('a', 'b'):
                # Eine Adresse nur, wo ein Anzeigenetz liegt — „Haut a“ ist die Figur selbst und hat keins (`mesh3dai_kleider_haut.py`).
                if isinstance(eintrag.get(weg), dict) and not eintrag[weg].get('fehler') and (ordner / weg / st['id'] / 'anzeige' / 'netz.npz').is_file():
                    eintrag[weg] = dict(eintrag[weg], netz='/api/mesh3dai/test/%s/kleid/%s/%s/%s' % (kennung, geschlecht, weg, st['id']))
            stuecke.append(eintrag)
        stuecke += ki_zeilen
        for eintrag in stuecke:
            eintrag['eigene_wahl'] = eigene.get(eintrag['id'])
            eintrag['wahl'] = cls.wirksam(eintrag, eintrag['eigene_wahl'], vorgabe)
        # Name und Kategorie in der Garderobe (22.10.2026, `Mesh3daitestkleidspeichern`)
        Mesh3daitestkleidspeichern.ergaenzen(stuecke, cls.einstellung(p), geschlecht)
        return {'vorgabe': vorgabe, 'stuecke': stuecke, 'quelle': kopf.get('quelle'), 'grund': kopf.get('grund'), 'gerechnet': kopf.get('gerechnet'),
                'katalog': kopf.get('katalog'), 'ki': ki_info, 'wege_texte': Mesh3daitestkikleider.TEXTE, 'kategorien': Mesh3daitestkleidspeichern.kategorien()}

    @classmethod
    def speichern_setzen(cls, kennung, geschlecht, stueck, name, kategorie):
        """Name und/oder Kategorie EINES Stücks für die Übernahme (`None` = unverändert, '' = Vorgabe). `ValueError` mit Grund; False bei unbekanntem Test oder Stück."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None or not cls.ID.match(str(stueck)):
            return False
        n, k = Mesh3daitestkleidspeichern.pruefen(name, kategorie)
        p = ordner.parent
        alle = dict(cls.einstellung(p).get('kleider_speichern') or {})
        je = dict(alle.get(geschlecht) or {})
        sp = dict(je.get(str(stueck)) or {})
        if name is not None:
            sp['name'] = n
        if kategorie is not None:
            sp['kategorie'] = k
        sp = {s: w for s, w in sp.items() if w}
        if sp:
            je[str(stueck)] = sp
        else:
            je.pop(str(stueck), None)
        alle[geschlecht] = je
        cls.einstellung_aendern(p, kleider_speichern=alle)
        return True

    @classmethod
    def wahl_setzen(cls, kennung, geschlecht, stueck, wahl):
        """Wahl EINES Stücks; `stueck` = None und `wahl` ∈ VORGABEN: alle Stücke nach dieser Vorgabe (eigene Wahlen fallen weg). False bei ungültiger Eingabe."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None:
            return False
        p = ordner.parent
        alle = dict(cls.einstellung(p).get('kleider_wahl') or {})
        if stueck is None:
            if wahl not in cls.VORGABEN:
                return False
            alle[geschlecht] = {}
            cls.einstellung_aendern(p, kleider_wahl=alle, kleider_vorgabe=wahl)
            return True
        if wahl not in cls.WAHLEN or not cls.ID.match(str(stueck)):
            return False
        je = dict(alle.get(geschlecht) or {})
        je[str(stueck)] = wahl
        alle[geschlecht] = je
        cls.einstellung_aendern(p, kleider_wahl=alle)
        return True

    @classmethod
    def vorgabe_setzen(cls, kennung, vorgabe):
        p = Mesh3daitest.pfad(kennung)
        if p is None or vorgabe not in cls.VORGABEN:
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
