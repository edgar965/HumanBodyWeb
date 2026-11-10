# -*- coding: utf-8 -*-
"""Meshgenesistestkikleider — die Kleider eines Tests, die die KI selbst erzeugt (20.10.2026 nachts, Konzept `Docu/konzepte/2026-10-19_meshgenesis-kleider-und-haar-erzeugen-konzept.md`).

Edgar: „baue die Ausgänge für Kleider in der KI!“ → „warum nicht alle 4?“. Drei Wege neben a (Katalog) und b (Mesh-3D-Lauf), alle aus der KI von Mesh-Genesis:
    k  aus dem Netz geschnitten — die Grenze zieht der Zerlegungskopf, Geometrie und Textur kommen aus dem Netz, übertragen auf die Figur der KI (`ProjektTemp/_wegwerf/meshgenesis_kikleider.py`)
    s  Schnitt — der Schnittkopf liest Katalogstück, Form und Regler aus dem geschnittenen Stück, GarmentCode baut und drapiert es (`meshgenesis_schnitt_anwenden.py`)
    h  Frisur — die Frisur der Garderobe mit den nächsten Maßen zum Haarkopf der KI (`meshgenesis_kikleider.py`, Teil 4)
Dazu zwei VERGLEICHSLINIEN zum Schnitt s (20.10.2026, Edgar: „baue: Die Vergleichslinien Schnittdeutung und NeuralTailor“), auf demselben Stück, mit derselben Drapierung und demselben Abstand
(`meshgenesis_schnittweg.py`, `meshgenesis_schnittvergleich.py`) — wählbar, aber nie Vorgabe und nie im Ergebnis der Jobseite (das zeigt nur, was die KI von Mesh-Genesis ausgibt):
    d  Schnittdeutung — Maße des Stücks → Regler über die umgekehrten GarmentCode-Formeln (Messung, keine KI)
    n  NeuralTailor — fremde KI (Korosteleva 2022, MIT, vortrainiert): Schnittteile und Nähte aus der Punktwolke des Stücks
Ablage `_test/<kennung>/kleider_<g>/ki.json` (eine Zeile je Stück, `quelle: 'ki'`, `ki_vorgabe` = Reihenfolge der Wege) + `k|s|h|d|n/<id>/anzeige/` — eigene Datei, weil `meshgenesis_kleider.py`
`stuecke.json` je Lauf neu schreibt. `ki.json` schreibt `Kikleiderliste` (Wege k, s, h); die Einträge der Vergleichslinien liest diese Klasse aus ihren Ordnern dazu — die Kleiderkette schreibt
`ki.json` neu, ohne sie zu kennen. Grundjob-Proben haben dieselbe Ablage unter `<Job>/kleider_ki/<nnnn>/kleider/` (`Meshgenesisprobenkleider`).
"""

import json
import logging

logger = logging.getLogger(__name__)

__all__ = ['Meshgenesistestkikleider']


class Meshgenesistestkikleider:
    #: f (21.10.2026, Edgar: „Option 3 … mach das!“): Schnitt aus der Fläche — Nähte vom Körper (Bang), flachgelegt nach Dumery, GarmentCode näht und drapiert
    #: (`GarmentCode/flaechenlauf.py`, `ProjektTemp/_wegwerf/meshgenesis_flaeche_lauf.py`); Vorgabe vor s, wo das Stück einen Schnitt hat (`Kikleiderliste.vorgabe`)
    #: g (21.10.2026, Edgar: „das muss GENAU so ausschauen wie am Ziel“): der Schichtkopf gibt die Stücke selbst aus — Deckung und Abstand je Punkt des Genesis-Käfigs, gegen die Zielstücke trainiert
    #: (`ProjektTemp/_wegwerf/meshgenesis_schicht_*.py`, Konzept `Docu/konzepte/2026-10-21_meshgenesis-kleider-wie-das-ziel-konzept.md`); Vorgabe vor den anderen Wegen seiner Art (`Kikleiderliste.G_VORN`)
    KI = ('k', 's', 'h', 'f', 'g')
    VERGLEICH = ('d', 'n')
    WEGE = KI + VERGLEICH
    #: Wege, deren Netz aus der Bibliothek kommt (h: ein fertiges Garderobe-Stück, die KI wählt nur nach ihren Haarmaßen) — die Vorgabe „KI“ nimmt sie nie von selbst, nur auf eigene Wahl
    #: (Edgar 20.10.2026 an DamiraAlt: „wie kann es sein, dass ich so perfekte Haare habe?? die sollen doch nicht aus der Bibliothek kommen, sondern aus GarmentCode oder KI Ergebnis??“).
    AUS_DER_BIBLIOTHEK = ('h',)
    TEXTE = {'k': 'KI: aus dem Netz geschnitten', 's': 'KI: Schnitt (GarmentCode)', 'h': 'Bibliothek: Frisur der Garderobe nach den Haarmaßen der KI',
             'd': 'Vergleich: Schnittdeutung (Messung, keine KI)', 'n': 'Vergleich: NeuralTailor (fremde KI)',
             'f': 'KI: Schnitt aus der Fläche (Nähte vom Körper, flachgelegt, GarmentCode näht und drapiert)',
             'g': 'KI: Schicht auf dem Körper (Form des Stücks aus dem Schichtkopf, gegen die Zielstücke trainiert)'}

    @staticmethod
    def lesen(ordner):
        """`ki.json` des Geschlechtsordners oder None."""
        try:
            wert = json.loads((ordner / 'ki.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return wert if isinstance(wert, dict) else None

    @staticmethod
    def _eintrag(datei):
        try:
            e = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return {k: v for k, v in e.items() if k not in ('id', 'name', 'art', 'region', 'bewegung')} if isinstance(e, dict) else None

    @classmethod
    def zeilen(cls, ordner, kennung, geschlecht, adresse=None):
        """Die Zeilen der KI mit Adressen der Anzeigenetze (nur wo eins liegt). `adresse` (Format mit `{weg}`, `{id}`) — Vorgabe die Netze eines Tests."""
        kopf = cls.lesen(ordner)
        if not kopf:
            return [], None
        adresse = adresse or '/api/meshgenesis/test/%s/kleid/%s/{weg}/{id}' % (kennung, geschlecht)
        anatomie = cls._anatomie(ordner, geschlecht)
        aus = []
        for st in kopf.get('stuecke') or []:
            eintrag = {k: st.get(k) for k in ('id', 'name', 'art', 'region', 'bewegung', 'quelle', 'ki_vorgabe', *cls.KI)}
            eintrag['quelle'] = 'ki'
            for weg in cls.VERGLEICH:
                if (ordner / weg / st['id'] / 'eintrag.json').is_file():
                    eintrag[weg] = cls._eintrag(ordner / weg / st['id'] / 'eintrag.json')
            for weg in cls.WEGE:
                e = eintrag.get(weg)
                if isinstance(e, dict) and not e.get('fehler') and (ordner / weg / st['id'] / 'anzeige' / 'netz.npz').is_file():
                    eintrag[weg] = dict(e, netz=adresse.format(weg=weg, id=st['id']))
                if isinstance(eintrag.get(weg), dict) and anatomie is not None:
                    eintrag[weg] = cls._anatomie_tragen(eintrag[weg], anatomie, st.get('art'))
            aus.append(eintrag)
        info = {k: kopf.get(k) for k in ('gerechnet', 'grund', 'zerlegung', 'ausschnitt', 'quelle_ki', 'schnitt_lauf', 'probe')}
        return aus, info

    @staticmethod
    def _regel():
        """`Kleideranatomie` und `Kleiderverdeckung` aus der Kette (`A:/3DTools/meshgenesis`, nur numpy)."""
        from django.conf import settings
        import sys
        mesh = str(settings.TOOLS_ROOT / 'meshgenesis')
        if mesh not in sys.path:
            sys.path.insert(0, mesh)
        from meshgenesis_kleider_anatomie import Kleideranatomie
        from meshgenesis_kleider_verdeckung import Kleiderverdeckung
        return Kleideranatomie, Kleiderverdeckung

    @classmethod
    def _anatomie(cls, ordner, geschlecht):
        """bool je Dreieck der Figur: die Anatomie im Anzeigenetz neben der Kleiderliste (`<Test>/form_<g>/`, bei Foto-Genesis `<Job>/figur/form_<g>/`) — None ohne Netz."""
        import numpy as np
        try:
            with np.load(ordner.parent / ('form_%s' % geschlecht) / 'anzeige' / 'netz.npz') as z:
                return z['etikett'] == cls._regel()[0].ETIKETT
        except (OSError, KeyError, ValueError):
            return None

    @classmethod
    def _anatomie_tragen(cls, e, anatomie, art):
        """`traegt_anatomie` je Weg nach DER Regel (`Kleideranatomie.getragen`, 08.11.2026 — vorher entschieden das zwei weitere Regeln im Browser). Trägt das Stück sie, steht die ganze
        Anatomie in seiner Maske (der Kostüm-Weg schreibt sie schon so, `Kleideranatomie.verdecken`; die anderen Wege bekommen sie hier), damit die stehende Figur dasselbe zeigt wie die bewegte."""
        regel, verdeckung = cls._regel()
        maske = verdeckung.dekodieren(e.get('verdeckt'), len(anatomie))
        getragen = bool(e.get('verdeckt')) and regel.getragen(anatomie, maske, art)
        e = dict(e, traegt_anatomie=getragen)
        if getragen and not maske[anatomie].all():
            e['verdeckt'] = verdeckung.kodieren(maske | anatomie)
        return e
