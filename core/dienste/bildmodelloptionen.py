# -*- coding: utf-8 -*-
"""Bildmodelloptionen — die Schritte eines Bildmodell-Auftrags und die Wahl je Schritt.

Edgar (19.09.2026): „auf der Seite soll man die verschiedenen Optionen /
Alternativen für einzelne Schritte einstellen können." Jeder Schritt hat
hier seine Felder mit Alternativen; `katalog()` liefert sie der Seite
samt Verfügbarkeit (ein Schätzer ohne Gewichte steht ausgegraut mit Grund),
`vorgaben()` den Ausgangszustand, `pruefen(roh)` nimmt nur Bekanntes an.

Die Schritte laufen in dieser Reihenfolge (`SCHRITTE`); ein Auftrag kann
ab jedem Schritt neu anlaufen (`ab=`), z. B. nach geänderter Einordnung der
Bilder oder anderer Reglerwahl, ohne die Schätzer erneut zu bemühen.
"""

from .bildmodellbildtypen import Bildmodellbildtypen
from .bildmodellkatalog import Bildmodellkatalog
from .bildmodellpersonkatalog import Bildmodellpersonkatalog

__all__ = ['Bildmodelloptionen']


class Bildmodelloptionen:
    SCHRITTE = [
        ('sichtung', 'Zuschnitt und Sichtung'),
        ('schaetzung', 'Schätzung (Körper)'),
        # 22.09.2026: eigene Pipeline für den Kopf (`Bildmodellkopf`: MICA, PyMAF-X, FaceBuilder,
        # mehrere Fotos) — ihr FLAME-Kopf geht ins Zielnetz und in den Kopf-Fit.
        ('kopf', 'Kopf (FLAME-Pipeline)'),
        ('ziel', 'Zielnetz'),
        ('anpassung', 'Anpassung der Regler'),
        ('rest', 'Restmorph'),
        ('vorschau', 'Vorschau rendern'),
        ('textur', 'Textur aus den Bildern'),
        ('speichern', 'Modell speichern'),
    ]
    #: Wo die Datei je Schritt in der Kette steht — für `ab=`.
    REIHENFOLGE = [s for s, _ in SCHRITTE]
    #: Einzelschritte außerhalb der Kette — nur auf ausdrückliche Nennung in `schritte`,
    #: nie in einem Lauf „ab …": `gvhmr` = SMPL-X mit GVHMR für EIN Bild (Knopf je Kachel,
    #: `optionen.gvhmr_bild`, 20.09.2026 — `Bildmodellgvhmr`); `flame` = der FLAME-Kopf für
    #: EIN Kopfbild (Knopf „Kopf (FLAME)", dasselbe Feld — `Bildmodellflame`).
    EINZELN = ('gvhmr', 'flame')
    #: Felder, die `pruefen` nicht kennt und die ein Start vom Auftrag übernimmt, wenn
    #: der Rumpf sie nicht mitbringt: Popup-Proportionen, Testfall, gezogene Linien,
    #: Bildtypen-Vorgaben für hochgeladene Dateien (19.09.2026 — die Linien gingen sonst
    #: beim ersten Start verloren).
    DURCHREICHEN = ('proportionen_linien', 'bildtypen')
    BLEIBEN = ('proportionen', 'testfall') + DURCHREICHEN

    #: Felder je Schritt: (feld, anzeige, [(wert, anzeige, erklaerung)], vorgabe)
    FELDER = Bildmodellkatalog.FELDER
    ZAHLENFELDER = {'groesse_cm': (100.0, 250.0)}
    DAEMPFUNG = {'gering': 0.02, 'mittel': 0.1, 'stark': 0.5}
    GLAETTUNG = {'wenig': 3, 'mittel': 6, 'viel': 12}
    #: Angaben zur Person (Edgar, 19.09.2026: „Alter, Größe, Gewicht, Tonus, Haar").
    #: Größe und Gewicht formen das Zielnetz (`G9koerpergewicht`), Haar geht ins
    #: Modell; Alter und Tonus haben in den Starter Essentials keinen Regler und
    #: werden mit dem Modell abgelegt.
    PERSON = {'alter': (0.0, 120.0), 'groesse_cm': (100.0, 250.0), 'gewicht_kg': (20.0, 250.0),
              'tonus': (0.0, 100.0)}
    #: Proportionen (Edgar, 19.09.2026: Popup „wo ich diese anpassen kann") — cm je
    #: Schlüssel aus `G9proportionen.MASSE`; sie formen das Zielnetz vor der Anpassung.
    PROPORTION_CM = (0.5, 120.0)

    # ------------------------------------------------------------ Katalog

    @classmethod
    def vorgaben(cls):
        aus = {}
        for felder in cls.FELDER.values():
            for feld, _, _, vorgabe in felder:
                aus[feld] = vorgabe
        aus['groesse_cm'] = None
        aus['person'] = {}
        aus['proportionen'] = {}
        aus['testfall'] = {}
        return aus

    @classmethod
    def proportionen_pruefen(cls, roh):
        """`{schluessel: cm}` — nur bekannte, formbare Maße im Bereich `PROPORTION_CM`."""
        from Genesis9.proportionen import G9proportionen

        roh = roh if isinstance(roh, dict) else {}
        lo, hi = cls.PROPORTION_CM
        aus = {}
        for k, v in roh.items():
            if not G9proportionen.FORMBAR.get(k):
                continue
            try:
                w = float(v) if v not in (None, '') else None
            except TypeError, ValueError:
                w = None
            if w is not None and lo <= w <= hi:
                aus[k] = round(w, 1)
        return aus

    @classmethod
    def person_pruefen(cls, roh):
        """`{alter, groesse_cm, gewicht_kg, tonus, haar}` — nur Zahlen im Bereich, Haar als Kennung."""
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for feld, (lo, hi) in cls.PERSON.items():
            w = roh.get(feld)
            try:
                w = float(w) if w not in (None, '') else None
            except TypeError, ValueError:
                w = None
            if w is not None:
                aus[feld] = min(hi, max(lo, w))
        haar = roh.get('haar')
        if isinstance(haar, str) and haar.strip():
            aus['haar'] = haar.strip()[:80]
        return aus

    @classmethod
    def testfall_pruefen(cls, roh):
        """`{figur}` — eine Referenzfigur aus dem Genesis-9-Katalog (Edgar, 19.09.2026:
        „Testcase … das Ursula9-Modell zum Vergleich mit dem, was du erzeugt hast")."""
        roh = roh if isinstance(roh, dict) else {}
        figur = roh.get('figur')
        if not isinstance(figur, str) or not figur.strip():
            return {}
        figur = figur.strip()[:80]
        if figur not in {f['name'] for f in Bildmodellpersonkatalog.testfiguren()}:
            return {}
        return {'figur': figur}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Felder mit bekannten Werten; Rest Vorgabe."""
        aus = cls.vorgaben()
        roh = roh if isinstance(roh, dict) else {}
        for felder in cls.FELDER.values():
            for feld, _, werte, _ in felder:
                w = roh.get(feld)
                if w in {v for v, _, _ in werte}:
                    aus[feld] = w
        for feld, (lo, hi) in cls.ZAHLENFELDER.items():
            try:
                w = float(roh.get(feld)) if roh.get(feld) not in (None, '') else None
            except TypeError, ValueError:
                w = None
            aus[feld] = min(hi, max(lo, w)) if w is not None else None
        aus['person'] = cls.person_pruefen(roh.get('person'))
        aus['proportionen'] = cls.proportionen_pruefen(roh.get('proportionen'))
        aus['testfall'] = cls.testfall_pruefen(roh.get('testfall'))
        for feld in cls.DURCHREICHEN:
            # Geprüft beim Schreiben (`Bildmodellfotolinien.linien_pruefen`, `Bildmodellbildtypen.
            # vorgaben_pruefen`); hier nur durchreichen — der Lauf prüft `job.optionen` erneut.
            if isinstance(roh.get(feld), dict):
                aus[feld] = roh[feld]
        return aus

    @classmethod
    def katalog(cls):
        """Für die Seite: Schritte, Felder, Alternativen, Verfügbarkeit."""
        verfuegbar = Bildmodellkatalog.verfuegbarkeit()
        schritte = []
        for schluessel, name in cls.SCHRITTE:
            felder = []
            for feld, anzeige, werte, vorgabe in cls.FELDER.get(schluessel, []):
                alternativen = []
                for wert, text, erklaerung in werte:
                    stand = verfuegbar.get((feld, wert), (True, ''))
                    alternativen.append(
                        {
                            'wert': wert,
                            'anzeige': text,
                            'erklaerung': erklaerung,
                            'verfuegbar': stand[0],
                            'grund': stand[1],
                        }
                    )
                felder.append(
                    {'feld': feld, 'anzeige': anzeige, 'vorgabe': vorgabe, 'alternativen': alternativen}
                )
            schritte.append({'schluessel': schluessel, 'name': name, 'felder': felder})
        return {
            'schritte': schritte,
            'zahlenfelder': list(cls.ZAHLENFELDER),
            'person': {feld: list(grenzen) for feld, grenzen in cls.PERSON.items()},
            'haare': Bildmodellpersonkatalog.haare(),
            'proportionen': Bildmodellpersonkatalog.proportionen(),
            'proportion_cm': list(cls.PROPORTION_CM),
            'bildtypen': Bildmodellbildtypen.katalog(),
            'testfiguren': Bildmodellpersonkatalog.testfiguren(),
        }

    # ----------------------------------------------------- Verfügbarkeit

    @classmethod
    def vergessen(cls):
        Bildmodellkatalog.vergessen()
