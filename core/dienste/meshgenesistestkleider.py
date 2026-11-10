# -*- coding: utf-8 -*-
"""Meshgenesistestkleider — Kleider und Bestandteile eines Tests von Mesh-Genesis, je Stück wählbar aus mehreren Wegen (17.10.2026 nachts; KI-Wege 20.10.2026).

Edgar: „Kleider und assets — können wir beide Optionen bauen? Per Option umschalten auf b oder a … Nach dem Bauen müsste ich im Ergebnis View festlegen können, ob ich ein Kleidungsstück in der ersten Option
oder zweiten Option haben möchte. Also Toggle für jedes Kleidungsstück für beide Optionen und Button zum übernehmen von Option a oder b in das End-Modell, mit speichern des Modells“.

    a  Katalog: ein Stück der Garderobe, auf der vorhergesagten Figur gebaut (gewählt durch Messung gegen das Stück aus dem Netz — `ProjektTemp/_wegwerf/meshgenesis_kleider_katalog.py`)
    b  aus dem Netz: das Objekt, das ein voller Mesh-3D-Lauf auf derselben Datei ausgeschnitten hat, in die Ruhelage der vorhergesagten Figur übertragen (`meshgenesis_kleider.py`)
    k, s, h  aus der KI von Mesh-Genesis (`Meshgenesistestkikleider`: geschnitten, GarmentCode-Schnitt, Frisur) — eigene Zeilen aus `ki.json`

Ablage `_test/<kennung>/kleider_<geschlecht>/stuecke.json` (+ `a|b/<id>/anzeige/`, Format `Meshgenesisflaechennetz`) und `ki.json` (+ `k|s|h/<id>/anzeige/`). Die Wahl steht in `einstellung.json` des Tests:
`kleider_vorgabe` (`ki` | `a` | `b`, Vorgabe `ki` — Edgar 19.10.2026: „das Ergebnis soll direkt aus der KI kommen“) und `kleider_wahl` `{geschlecht: {id: weg | 'aus'}}` (nur, was vom Nutzer abweicht).
Wirksam je Stück: die eigene Wahl; sonst bei Vorgabe `ki` die KI-Zeilen in ihrer Reihenfolge (`ki_vorgabe`) ohne die Wege aus der Bibliothek (h, seit 20.10.2026 nur auf eigene Wahl),
die Zeilen des Mesh-3D-Laufs aus (die Haut: Haut der Figur); bei Vorgabe a/b die
Zeilen des Mesh-3D-Laufs wie bisher, die KI-Zeilen aus. Ein Weg, den das Stück nicht hat, gilt nie.
"""

import json
import logging
import re

from ..atomic_write import AtomarSchreiber
from .meshgenesisflaechennetz import Meshgenesisflaechennetz
from .meshgenesistest import Meshgenesistest
from .meshgenesistestkikleider import Meshgenesistestkikleider
from .meshgenesistestkleidspeichern import Meshgenesistestkleidspeichern

logger = logging.getLogger(__name__)

__all__ = ['Meshgenesistestkleider']


class Meshgenesistestkleider:
    WEGE = ('a', 'b') + Meshgenesistestkikleider.WEGE
    WAHLEN = WEGE + ('aus',)
    VORGABEN = ('ki', 'a', 'b')
    VORGABE = 'ki'
    ID = re.compile(r'^[a-z0-9_]{1,64}$')

    @classmethod
    def ordner(cls, kennung, geschlecht):
        p = Meshgenesistest.pfad(kennung)
        if p is None or geschlecht not in Meshgenesistest.GESCHLECHTER:
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
                return next((w for w in (Meshgenesistestkikleider.WEGE if folge is None else folge) if w in da and w not in Meshgenesistestkikleider.AUS_DER_BIBLIOTHEK), 'aus')
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
            kopf = {'stuecke': [], 'quelle': None, 'grund': 'Für diesen Test sind die Wege a/b nicht gerechnet (ProjektTemp/_wegwerf/meshgenesis_kleider.py).'}
        ki_zeilen, ki_info = Meshgenesistestkikleider.zeilen(ordner, kennung, geschlecht)
        eigene = ((cls.einstellung(p).get('kleider_wahl') or {}).get(geschlecht) or {})
        stuecke = []
        for st in kopf.get('stuecke') or []:
            eintrag = {k: st.get(k) for k in ('id', 'name', 'art', 'region', 'bewegung', 'kontakt', 'a', 'b')}
            eintrag['quelle'] = 'mesh3d'
            for weg in ('a', 'b'):
                # Eine Adresse nur, wo ein Anzeigenetz liegt — „Haut a“ ist die Figur selbst und hat keins (`meshgenesis_kleider_haut.py`).
                if isinstance(eintrag.get(weg), dict) and not eintrag[weg].get('fehler') and (ordner / weg / st['id'] / 'anzeige' / 'netz.npz').is_file():
                    eintrag[weg] = dict(eintrag[weg], netz='/api/meshgenesis/test/%s/kleid/%s/%s/%s' % (kennung, geschlecht, weg, st['id']))
            stuecke.append(eintrag)
        stuecke += ki_zeilen
        for eintrag in stuecke:
            eintrag['eigene_wahl'] = eigene.get(eintrag['id'])
            eintrag['wahl'] = cls.wirksam(eintrag, eintrag['eigene_wahl'], vorgabe)
        # Name und Kategorie in der Garderobe (22.10.2026, `Meshgenesistestkleidspeichern`)
        Meshgenesistestkleidspeichern.ergaenzen(stuecke, cls.einstellung(p), geschlecht)
        return {'vorgabe': vorgabe, 'stuecke': stuecke, 'quelle': kopf.get('quelle'), 'grund': kopf.get('grund'), 'gerechnet': kopf.get('gerechnet'),
                'katalog': kopf.get('katalog'), 'ki': ki_info, 'wege_texte': Meshgenesistestkikleider.TEXTE, 'kategorien': Meshgenesistestkleidspeichern.kategorien(),
                'ohne_eingang': cls.ohne_eingang(ordner)}

    @staticmethod
    def ohne_eingang(ordner):
        """Die Glieder der Figur, die das Netz des Eingangs nicht hat (`meshgenesis_kostuem_ohneeingang.py`, Schritt „kleider“, 31.10.2026) — `{knochen: [Namen], …}` oder None."""
        try:
            wert = json.loads((ordner / 'ohne_eingang.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return wert if isinstance(wert, dict) and isinstance(wert.get('knochen'), list) else None

    @classmethod
    def speichern_setzen(cls, kennung, geschlecht, stueck, name, kategorie):
        """Name und/oder Kategorie EINES Stücks für die Übernahme (`None` = unverändert, '' = Vorgabe). `ValueError` mit Grund; False bei unbekanntem Test oder Stück."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None or not cls.ID.match(str(stueck)):
            return False
        n, k = Meshgenesistestkleidspeichern.pruefen(name, kategorie)
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
        p = Meshgenesistest.pfad(kennung)
        if p is None or vorgabe not in cls.VORGABEN:
            return False
        cls.einstellung_aendern(p, kleider_vorgabe=vorgabe)
        return True

    @classmethod
    def stueck_ordner(cls, kennung, geschlecht, weg, stueck):
        """Ordner des Stücks relativ zu `meshgenesis/` (für `Meshgenesisflaechennetz`) oder None — alle Teile kommen aus der Adresse und werden geprüft."""
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None or weg not in cls.WEGE or not cls.ID.match(str(stueck)):
            return None
        if not (ordner / weg / stueck / 'anzeige' / 'netz.npz').is_file():
            return None
        return '_test/%s/kleider_%s/%s/%s' % (kennung, geschlecht, weg, stueck)

    @classmethod
    def paket(cls, kennung, geschlecht, weg, stueck, stufe=0):
        """`stufe` 1: die Haut aus dem Netz (Zeile „Haut“ b, Körper auf dem Käfig) wie die Figur auf Netzstufe 1 (`Meshgenesisflaechennetzfein`); Stücke bleiben, wie sie sind."""
        modell = cls.stueck_ordner(kennung, geschlecht, weg, stueck)
        return Meshgenesisflaechennetz.paket(modell, stufe=stufe) if modell else None

    @classmethod
    def bild(cls, kennung, geschlecht, weg, stueck, name):
        modell = cls.stueck_ordner(kennung, geschlecht, weg, stueck)
        return Meshgenesisflaechennetz.bild(modell, name) if modell else None
