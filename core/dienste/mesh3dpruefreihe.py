# -*- coding: utf-8 -*-
"""Mesh3dpruefreihe — die Prüfreihe der Testaufträge von Mesh-3D: geht an den Jobs im Reiter „Testaufträge“ etwas kaputt, wenn die Pipeline sich ändert? (13.10.2026)

Edgar: „Kannst du dir Testcases bauen, die checken, dass an den Jobs im ‚Test‘-Bereich nichts kaputt geht bei Änderungen, die du an der Pipeline machst?" Anlass: die Mindestluft unter dem Stoff (`kleidungsluft_mm` 4 für jeden Weg „netz“, eingeführt für die Haut-durch-Strümpfe der Ballerina) hat Edgars Hände
aufgerissen — Daumen und kleiner Finger rissen als Lappen auf, weil Uhr und als Zubehör gelesene Flächen am Handgelenk als Stoff zählten. Keine Messung meldete es; Edgar sah es.

Aufbau (wie `Engine2d3dKleiderpruefreihe`): je Testauftrag Sollwerte in `core/daten/mesh3dpruefreihe.json` (`aufnehmen` schreibt sie aus dem jetzigen Stand — nur auf ausdrücklichen Wunsch, nachdem man den Stand angesehen und für gut befunden hat), die Messwerte kommen aus
`Mesh3dmesswerte` (gelesen aus dem, was der letzte Lauf abgelegt hat), die Regeln stehen hier (`REGELN`: je Wert eine Art und eine Toleranz). Ein Wert, den es im Soll gibt und den der Lauf nicht lieferte, ist „nicht gemessen“ und zählt als nicht bestanden.

    manage.py mesh3d_pruefreihe                 prüft die gespeicherten Ergebnisse (Sekunden, keine Grafikkarte)
    manage.py mesh3d_pruefreihe --rechnen       rechnet jeden Testauftrag als Kopie neu (Grafikkarte, je Auftrag 6–20 Minuten, nacheinander) und prüft die Kopie gegen das Soll des Originals
    manage.py mesh3d_pruefreihe --aufnehmen     schreibt das Soll aus dem jetzigen Stand
"""

import json
import logging
import time
from datetime import date
from pathlib import Path

from django.conf import settings

from ..daten.blendimportablage import Blendimportablage
from .mesh3dmesswerte import Mesh3dmesswerte
from .mesh3dreiter import Mesh3dreiter

logger = logging.getLogger('core')

__all__ = ['Mesh3dpruefreihe']


class Mesh3dpruefreihe:
    DATEI = Path(settings.BASE_DIR) / 'core' / 'daten' / 'mesh3dpruefreihe.json'
    #: Reiter, dessen Aufträge die Reihe bilden.
    REITER = 'test'
    #: Wert → (Art, relative Toleranz, absolute Toleranz). `max`: ist ≤ Soll·(1+rel)+abs · `min`: ist ≥ Soll·(1−rel)−abs · `nahe`: |ist − Soll| ≤ |Soll|·rel+abs · `gleich`.
    #: Die Toleranzen sind Setzungen aus der Streuung der Läufe (`meshfigur-tempo.md`: Figur→Netz 3,4–6,8 mm bei GLEICHEN Eingaben; bei Edgar 2,40–2,62), nicht aus einer Wahrheit.
    REGELN = {
        'status': ('gleich', 0, 0),
        'fehler': ('gleich', 0, 0),
        'hoehe_cm': ('nahe', 0.0, 1.5),
        'figur_netz_mm': ('max', 0.25, 0.4),
        'netz_figur_mm': ('max', 0.25, 0.5),
        'hand_verformung_mm': ('max', 0.20, 0.8),
        'hand_untergrenze': ('max', 0.0, 0),
        'kleidung_flaechen': ('nahe', 0.08, 0),
        'kleidung_unterkante_m': ('max', 0.0, 0.006),
        'zubehoer_flaechen': ('nahe', 0.15, 20),
        'hautband_art': ('gleich', 0, 0),
        'haar_flaechen': ('nahe', 0.10, 20),
        'teile': ('gleich', 0, 0),
        'griff_seiten': ('gleich', 0, 0),
        'animation_gewaehlt': ('gleich', 0, 0),
        'animation_spitzen': ('max', 0.30, 0.0005),
        'animation_max_dehnung': ('max', 0.50, 20),
    }
    #: Regeln OHNE Soll: sie gelten für JEDEN Testauftrag, auch für ein neues Modell, das noch niemand angesehen und aufgenommen hat (Edgar: kein Handgriff für neue Modelle). Wert → (verlangter Wert, was sonst
    #: schiefgelaufen ist). Hier steht nur, was LOGISCH so sein muss (fertig, kein Fehlerfeld, keine Untergrenze an der Hand, keine Fläche in zwei Objekten, die Animationswahl ist die mit den wenigsten Spitzen) —
    #: keine Zahl aus einem Modell; Zahlen (Abstände, Flächen) brauchen ein Soll. Ein Wert, den der Lauf nicht lieferte (Auftrag älter als die Messung), ist hier „offen“, kein Fehler.
    INVARIANTEN = {
        'status': ('fertig', 'der Auftrag ist nicht fertig gelaufen'),
        'fehler': ([], 'ein Abschnitt des Ergebnisses meldet einen Fehler'),
        'hand_untergrenze': (0, 'Handpunkte tragen eine Untergrenze unter Stoff (die Hand liegt nie unter Stoff)'),
        'abnahme_doppelt': (0, 'Flächen stehen in zwei Objekten'),
        'animation_wahl_beste': (True, 'die Animationsprüfung hat nicht die Gewichte mit den wenigsten Spitzen gewählt'),
    }
    #: Stände, in denen ein Auftrag (noch) nichts zu prüfen gibt: angelegt und nie gestartet (`neu`) oder gerade am Rechnen (`laeuft`). Das ist „offen“, kein Fehler — `gescheitert` und `angehalten` bleiben welche.
    NOCH_KEIN_ERGEBNIS = {'neu': 'noch nicht gerechnet', 'laeuft': 'rechnet gerade'}
    #: Was eine Regel verletzt, in einem Satz — der Befehl druckt es hinter „FEHL“.
    ERKLAERUNG = {
        'hand_verformung_mm': 'die Hand ist verformt (Eigenmorph reißt Finger auf?)',
        'hand_untergrenze': 'Handpunkte tragen eine Untergrenze unter Stoff (die Hand liegt nie unter Stoff)',
        'kleidung_unterkante_m': 'die Unterkante der Kleidung liegt höher als im Soll (Saum fehlt?)',
        'zubehoer_flaechen': 'Zubehör (Uhr, Schmuck) hat deutlich mehr oder weniger Flächen',
        'fehler': 'ein Abschnitt des Ergebnisses meldet einen Fehler',
    }

    # ------------------------------------------------------------------ Soll

    @classmethod
    def laden(cls):
        """`{importkennung: {name, soll, …}}` aus der Datei."""
        try:
            return json.loads(cls.DATEI.read_text(encoding='utf-8')).get('auftraege') or {}
        except (OSError, ValueError):
            return {}

    @classmethod
    def testauftraege(cls):
        """Die Kennungen des Reiters „Testaufträge“, die es noch gibt."""
        zuordnung = Mesh3dreiter.zuordnung()
        return [k for k in Blendimportablage.alle() if zuordnung.get(k) == cls.REITER]

    @classmethod
    def verwaist(cls, kennungen=None):
        """`[(Kennung, Name)]` der Einträge im Soll, zu denen es keinen Testauftrag mehr gibt (gelöscht oder in einen anderen Reiter verschoben). Eine Prüfung, deren Auftrag fehlt, lief nie — und stand trotzdem in der Datei: am 14.10.2026 galten zwei von drei Soll-Aufträgen (Edgar, Zauberer) nicht mehr,
        und die Reihe meldete „alles bestanden“, ohne sie je zu prüfen."""
        vorhanden = set(cls.testauftraege() if kennungen is None else kennungen)
        return sorted((k, (e or {}).get('name') or k) for k, e in cls.laden().items() if k not in vorhanden)

    @classmethod
    def aufnehmen(cls, kennungen=None, hinweis='', auch=()):
        """Das Soll aus dem jetzigen Stand schreiben (nur Werte, die sich messen ließen) → `{kennung: Zahl der Werte}`. `auch`: Kennungen WEITERER Läufe desselben Auftrags (Kopien der Prüfreihe) — bei Regeln der Art `max` gilt der größte, bei `min` der kleinste
        Wert aller Läufe: die Läufe streuen bei gleichen Eingaben (Ballerina Figur→Netz 3,68 gegen 5,76 mm, Zauberer-Hand 26 bis 42 mm), und ein Soll aus dem glücklichsten Lauf schlüge bei jedem zweiten Lauf Alarm."""
        alt = cls.laden()
        neu, zahl = dict(alt), {}
        for k in kennungen or cls.testauftraege():
            m = Mesh3dmesswerte(k)
            soll = {n: v for n, v in m.alle().items() if n in cls.REGELN and v is not None}
            if not soll:
                continue
            for weitere in auch:
                for n, v in Mesh3dmesswerte(weitere).alle().items():
                    art = cls.REGELN.get(n, ('',))[0]
                    if n in soll and art in ('max', 'min') and isinstance(v, (int, float)) and isinstance(soll[n], (int, float)):
                        soll[n] = max(soll[n], v) if art == 'max' else min(soll[n], v)
            neu[k] = {'name': (m.stand.get('quelle') or {}).get('name') or k, 'soll': soll, 'aufgenommen': date.today().isoformat(), 'hinweis': hinweis or alt.get(k, {}).get('hinweis', '')}
            zahl[k] = len(soll)
        cls.DATEI.write_text(json.dumps({'fassung': 1, 'auftraege': neu}, ensure_ascii=False, indent=1, sort_keys=True), encoding='utf-8')
        return zahl

    # ------------------------------------------------------------------ Vergleich

    @classmethod
    def bewerten(cls, ist, soll):
        """`[(name, ist, soll, ok, erklaerung)]` für alle Werte im Soll. `None` im Ist (nicht gemessen) besteht nicht."""
        zeilen = []
        for name, s in sorted(soll.items()):
            if name not in cls.REGELN:
                continue
            v = ist.get(name)
            ok = v is not None and cls.einhalten(name, v, s)
            zeilen.append((name, v, s, ok, '' if ok else ('nicht gemessen' if v is None else cls.ERKLAERUNG.get(name, 'außerhalb der Toleranz'))))
        return zeilen

    @classmethod
    def einhalten(cls, name, ist, soll):
        art, rel, absolut = cls.REGELN[name]
        if art == 'gleich':
            return ist == soll
        if art == 'max':
            return ist <= soll * (1 + rel) + absolut
        if art == 'min':
            return ist >= soll * (1 - rel) - absolut
        return abs(ist - soll) <= abs(soll) * rel + absolut

    @classmethod
    def invarianten(cls, ist, ausser=()):
        """`[(name, ist, verlangt, ok, erklaerung)]` für die Regeln ohne Soll (`INVARIANTEN`); `ok` ist `None` („offen“), wenn der Lauf den Wert nicht lieferte. Was im Soll steht (`ausser`), wird dort schon bewertet."""
        zeilen = []
        for name, (verlangt, erklaerung) in cls.INVARIANTEN.items():
            if name in ausser:
                continue
            v = ist.get(name)
            if v is None:
                zeilen.append((name, v, verlangt, None, 'offen (nicht gemessen)'))
            elif name == 'status' and v in cls.NOCH_KEIN_ERGEBNIS:
                zeilen.append((name, v, verlangt, None, 'offen (%s)' % cls.NOCH_KEIN_ERGEBNIS[v]))
            else:
                ok = v == verlangt
                zeilen.append((name, v, verlangt, ok, '' if ok else erklaerung))
        return zeilen

    @classmethod
    def pruefen(cls, kennung, messkennung=None):
        """`(zeilen, ok)` — die Messwerte von `messkennung` (Vorgabe: der Auftrag selbst) gegen das Soll von `kennung` UND gegen die Regeln ohne Soll. `ok` heißt: keine Zeile ist `False` (eine „offene“ Zeile verletzt nichts)."""
        soll = (cls.laden().get(kennung) or {}).get('soll') or {}
        ist = Mesh3dmesswerte(messkennung or kennung).alle()
        zeilen = cls.bewerten(ist, soll) + cls.invarianten(ist, ausser=soll)
        return zeilen, bool(zeilen) and all(z[3] is not False for z in zeilen)

    @classmethod
    def name(cls, kennung):
        """Der Name des Auftrags für die Ausgabe: der aus dem Soll, sonst der der Quelle, sonst die Kennung."""
        eintrag = cls.laden().get(kennung) or {}
        if eintrag.get('name'):
            return eintrag['name']
        return ((Blendimportablage(kennung).stand() or {}).get('quelle') or {}).get('name') or kennung

    # ------------------------------------------------------------------ Neu rechnen

    @staticmethod
    def kopieren(kennung):
        """`(Kennung der Kopie, ab)` — die Kopie OHNE Ergebnis (mit Netz, `Mesh3dkopie.ohne_ergebnis`), solange die Quelldatei des Auftrags noch da ist (dann rechnet die Kopie von vorn, `ab` ist `None`). Fehlt sie (am 14.10.2026 beim ersten `--rechnen` der Zauberer: „Die Datei … gibt es nicht mehr“,
        8 von 12 Netz-Aufträgen haben ihre Quelle verloren), beim Weg „netz“ die Kopie MIT Daten, gerechnet ab der Segmentierung — das Netz auf Menschenhöhe liegt als `arbeit/koerper.glb` im Importordner. Beim Weg „teile“ (Blender liest die Datei) bleibt der Fehler."""
        from pathlib import Path

        from .mesh3dkopie import Mesh3dkopie

        kopierer = Mesh3dkopie(kennung)
        datei = (kopierer.stand.get('quelle') or {}).get('datei')
        if datei and Path(datei).exists():
            return kopierer.ohne_ergebnis(), None
        if kopierer.stand.get('weg') == 'netz' and kopierer.quelle.arbeit('koerper.glb').is_file():
            return kopierer.mit_daten(), 'segmentierung'
        return kopierer.ohne_ergebnis(), None              # wirft mit dem Grund (Datei fehlt)

    @classmethod
    def neu_rechnen(cls, kennung, melden=None, warten_s=3600, takt_s=15):
        """Einen Testauftrag als KOPIE neu rechnen (der Auftrag selbst bleibt unberührt) → die Kennung der Kopie. Sie steht im Reiter „Testaufträge“ und heißt „<Name> Kopie …“; gelöscht wird sie nicht (Aufräumen ist Sache des Nutzers)."""
        from .blendimportarbeiter import Blendimportarbeiter

        melden = melden or (lambda text: None)
        kopie, ab = cls.kopieren(kennung)
        Mesh3dreiter.erben(kennung, kopie)
        ablage = Blendimportablage(kopie)
        stand = ablage.stand()
        stand['einstellungen']['vergleichsvariante'] = 'aus'            # die Reihe misst die Hauptausgabe; eine zweite kostete je Auftrag vier Minuten Grafikkarte
        ablage.stand_schreiben(stand)
        Blendimportarbeiter.starten(ablage, ab=ab)
        melden('%s: Kopie %s gestartet' % (kennung, kopie))
        ende = time.monotonic() + warten_s
        while time.monotonic() < ende:
            time.sleep(takt_s)
            s = ablage.stand() or {}
            if s.get('status') in ('fertig', 'gescheitert', 'angehalten') and not Blendimportarbeiter.lebt(ablage):
                break
        melden('%s: Kopie %s: %s' % (kennung, kopie, (ablage.stand() or {}).get('status')))
        return kopie
