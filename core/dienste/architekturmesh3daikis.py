# -*- coding: utf-8 -*-
"""Architekturmesh3daikis — Abschnitt „Die KIs der Kette“ der Seite Hilfe → Architektur → Mesh3DAI (24.10.2026 abends).

Edgar: „passe auch deine Doku an … Mach die KopfKI, Haut KI rein, für alle KIs eine einzelne Grafik wie diese: Neuronale Netz - Figur; eine übergeordnete Grafik mit Kästchen und Ablauf, wie die KIs
aufgerufen werden“. Aus dem Code und den Dateien gelesen beim Aufruf: die Schritte (`Mesh3dairechenlauf.SCHRITTE`), welches Netz jeder Schritt nimmt (`ki_fassungen.json`), und je Netz der Steckbrief
(`3DObjects/mesh3dai/netzsteckbriefe.json`, geschrieben von `mesh3dai/mesh3dai_netzsteckbrief.py` aus den Gewichtsdateien — der Server lädt kein torch). Von Hand: `KIS` (was hinein- und
herausgeht, Wörter für die Bausteine — aus den Docstrings der Netze) und `FREMD` (Werkzeuge, die keine eigene KI sind).
"""

import json
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3daikis']


class Architekturmesh3daikis:
    #: je KI-Schlüssel: Titel, Eingang, Ausgang, Wort je Baustein (erstes Glied des Gewichtsnamens), Klasse im Rechencode
    KIS = {
        'vorstufe_mia': {'titel': 'Netz der Vorstufe (Rig in der A-Pose)', 'klasse': 'Stimmnetz (mesh3dai_stimmen_netz.py)',
                         'eingang': '4.096 Punkte der A-Pose-Wolke nach Make-It-Animatable, je Punkt x, y, z, r, g, b', 'ausgang': '276 Ziele (138 Gelenke + Enden) als Stimmen je Punkt'},
        'haltung': {'titel': 'Haltungs-KI', 'klasse': 'Stimmnetz + Formkopf (mesh3dai_formnetz.py)',
                    'eingang': '4.096 Punkte des Netzes in seiner Pose (x, y, z, r, g, b)', 'ausgang': 'Gelenke + Enden (Stimmen); die Winkelanpassung legt daraus die Daz-Winkel der Figur'},
        'formkopf': {'titel': 'Form-KI', 'klasse': 'Stimmnetz + Formkopf mit Reglergrenzen (mesh3dai_kopfformnetz.py)',
                     'eingang': '4.096 Punkte der A-Pose-Wolke', 'ausgang': '1.318 Genesis-Formregler, durch die Bauart in ihren Grenzen'},
        'zerlegung': {'titel': 'Zerlegungs-KI', 'klasse': 'Stimmnetz mit Zerlegungskopf (mesh3dai_kleidmodul*.py)',
                      'eingang': '4.096 Punkte der A-Pose-Wolke', 'ausgang': 'Art je Punkt (11: Haut, Haar, Oberteil, Hose …) und 8 Haarmaße'},
        'kopfnetz': {'titel': 'Kopf-KI', 'klasse': 'Kopfnetz (mesh3dai_kopfnetz_modell.py)',
                     'eingang': 'Merkmal des Kopfs aus dem Eingang (10.202 Zahlen)', 'ausgang': '523 Kopfregler — Start der Angleichung an das Mesh (Kopfangleich)'},
        'hautki': {'titel': 'Haut-KI im Bildraum', 'klasse': 'Hautnetz (KoerperKI_alle/hautnetz.py)',
                   'eingang': 'beobachtete Haut je Texel der fünf Hautkacheln (1024²): Farbe, Gewicht, gültig, Kachel, uv, Grundton — 15 Kanäle',
                   'ausgang': 'Haut je Texel (sRGB): gesehene Stellen abgeholt (Mischmaske m × Gewicht, Lichtkorrektur g), ungesehene erzeugt (e)'},
        'stufe2': {'titel': 'Stufe 2 (Gedächtnis je Körperstelle)', 'klasse': 'Stufe2netz (mesh3dai_stufe2.py)',
                   'eingang': 'Tripo-Punkte auf dem Käfig der Figur', 'ausgang': 'Form, Farbe, Deckung und Haut je Käfigstelle; die Haut nur, wenn keine Haut-KI im Bildraum eingetragen ist'},
    }
    WORTE = {'k1': 'Kantenfaltung 1', 'k2': 'Kantenfaltung 2', 'k3': 'Kantenfaltung 3', 'mitte': 'punktweise', 'kopf': 'Kopf', 'form': 'Formkopf', 'haar': 'Haarmaße',
             'grenze_unten': 'Grenzen', 'grenze_oben': 'Grenzen', 'ein': 'Eingangsblock', 'ab': 'abwärts (4 Halbierungen)', 'auf': 'aufwärts', 'licht': 'Licht g', 'eingang': 'Merkmal',
             'farbe': 'Gedächtnis Farbe', 'deckung': 'Gedächtnis Deckung', 'haut': 'Gedächtnis Haut'}
    #: je Schritt: (Art, Name) der Beteiligten — Art „ki“ (Schlüssel in ki_fassungen), „fremd“ (fertiges Modell eines anderen), „rechnung“ (eigener Code ohne Gewichte)
    BETEILIGT = {
        'rig': (('fremd', 'Make-It-Animatable'), ('ki', 'vorstufe_mia')),
        'haltung': (('ki', 'haltung'),),
        'form': (('ki', 'formkopf'),),
        'figur': (('rechnung', 'Genesis-Figur aus den Reglern'),),
        'anpassen': (('rechnung', 'Winkelanpassung'),),
        'haltung2': (('rechnung', 'Winkelanpassung an Gelenke + Enden'),),
        'segmentierung': (('fremd', 'Sapiens2'), ('fremd', 'SAM 3')),
        'zerlegung': (('ki', 'zerlegung'),),
        'kopf': (('ki', 'kopfnetz'), ('fremd', 'MediaPipe'), ('rechnung', 'Kopfangleich')),
        # 26.10.2026 nachgetragen (die Schritte gibt es seit 24./25.10.): Lageangleich misst über Kostuemmesspunkte (ViTPose), Koerperangleich das Gesicht über Kostuemgesicht (MediaPipe)
        'lage': (('fremd', 'ViTPose'), ('rechnung', 'Lageangleich')),
        'koerper': (('fremd', 'MediaPipe'), ('rechnung', 'Koerperangleich')),
        'haut': (('ki', 'hautki'), ('ki', 'stufe2'), ('rechnung', 'Entlichtung')),
        'kleider': (('rechnung', 'Kostüm-Weg A: erkennen, schneiden, auflegen'), ('fremd', 'ViTPose'), ('fremd', 'MediaPipe'), ('rechnung', 'Kostüm-Prüfung')),
    }

    @classmethod
    def kontext(cls):
        from .architekturmesh3daiablaufbild import Architekturmesh3daiablaufbild
        from .architekturmesh3dainetzbild import Architekturmesh3dainetzbild
        from .mesh3daikifassungen import Mesh3daikifassungen
        from .mesh3dairechenlauf import Mesh3dairechenlauf
        f = Mesh3daikifassungen.lesen()
        datei = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / 'netzsteckbriefe.json'
        try:
            steck = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            steck = {'kis': {}}
        schritte = [{'nr': i, 'schluessel': s, 'text': text, 'beteiligt': [{'art': a, 'name': n, 'titel': cls.KIS.get(n, {}).get('titel', n) if a == 'ki' else n,
                                                                              'lauf': f.get(n) if a == 'ki' else None} for a, n in cls.BETEILIGT.get(s, ())]}
                    for i, (s, text, _arg) in enumerate(Mesh3dairechenlauf.SCHRITTE, start=1)]
        kis = []
        for k, beschr in cls.KIS.items():
            sb = steck['kis'].get(k) or {}
            veraltet = sb.get('lauf') != f.get(k)
            spalten = cls.spalten(sb) if sb.get('bausteine') and not veraltet else []
            kis.append(dict(beschr, schluessel=k, lauf=f.get(k), gewichte=sb.get('gewichte'), mb=sb.get('mb'), fehler=sb.get('fehler') or (
                'Steckbrief von Lauf %s, eingesetzt ist %s — mesh3dai_netzsteckbrief.py neu laufen lassen' % (sb.get('lauf'), f.get(k)) if sb and veraltet else None),
                in_schritt=[s['nr'] for s in schritte if any(b['name'] == k for b in s['beteiligt'])],
                bild=Architekturmesh3dainetzbild.svg(beschr, spalten) if spalten else None, messung=cls.messung(k, f.get(k))))
        return {'schritte': schritte, 'kis': kis, 'ablauf': Architekturmesh3daiablaufbild.svg(schritte), 'steckbrief_datei': str(datei), 'steckbrief_stand': steck.get('gerechnet')}

    @classmethod
    def messung(cls, k, lauf):
        """Haut-KI: Messung des eingesetzten Laufs und des jüngsten Laufs daneben (`lauf_ergebnis.json`: echte Haut der Tripo-Jobs, Prüfung „Hautton und Tattoos folgen dem Eingang“) → [(Name, Wert)]."""
        if k != 'hautki':
            return []
        ordner = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_hautki' / 'laeufe'
        laeufe = sorted(p.name for p in ordner.glob('*') if (p / 'lauf_ergebnis.json').is_file())
        aus = []
        for name in dict.fromkeys([lauf] + laeufe[-1:]):
            try:
                m = json.loads((ordner / str(name) / 'lauf_ergebnis.json').read_text(encoding='utf-8'))['messung']
            except (OSError, ValueError, KeyError):
                continue
            wer = 'eingesetzt' if name == lauf else 'jüngster Lauf, nicht eingesetzt'
            e = m.get('echt_mittel') or {}

            def de(x):
                return '—' if x is None else ('%s' % x).replace('.', ',')
            aus.append(('%s (%s): echte Haut der Tripo-Jobs, Fehler sRGB (0–255)' % (name, wer), 'neu %s · Stufe 2 %s' % (de(e.get('neu')), de(e.get('bisher')))))
            t = m.get('toene')
            if not t:                                   # nachträglich gemessen (`mesh3dai_hautki_toene_lauf.py`): die jüngste Fassung der Prüfung
                dateien = sorted((ordner.parent / 'toene').glob('%s_toene*.json' % name))
                t = json.loads(dateien[-1].read_text(encoding='utf-8')) if dateien else None
            if t:
                teile = ['%s %s/%s' % (fall, de(v.get('ton_gesehen')), de(v.get('ton_ungesehen'))) for fall, v in t['mittel'].items() if fall != 'Tattoos']
                tat = t['mittel'].get('Tattoos', {}).get('tattoo_kontrast')
                aus.append(('%s: Hautton und Tattoos folgen dem Eingang (ΔE gesehen/ungesehen ≤ %s, Tattoo-Kontrast ≥ %s)' % (name, de(t.get('ton_max')), de(t.get('tattoo_min'))),
                            '%d von %d rot · %s · Tattoos %s' % (t['rot'], t['von'], ' · '.join(teile), de(tat))))
        return aus

    @classmethod
    def spalten(cls, sb):
        """Bausteine nach dem ersten Glied des Namens zusammenfassen → [(Wort, Gewichte, Kette der Kanäle)]."""
        aus = []
        for b in sb['bausteine']:
            erst = b['name'].split('.')[0]
            if aus and aus[-1]['erst'] == erst:
                z = aus[-1]
            else:
                z = {'erst': erst, 'wort': cls.WORTE.get(erst, erst), 'gewichte': 0, 'kette': []}
                aus.append(z)
            z['gewichte'] += b['gewichte']
            if b['ein'] is not None:
                if not z['kette']:
                    z['kette'].append(b['ein'])
                z['kette'].append(b['aus'])
        # Grenzen (oben/unten) zu einer Spalte
        zusammen = []
        for z in aus:
            if zusammen and zusammen[-1]['wort'] == z['wort']:
                zusammen[-1]['gewichte'] += z['gewichte']
            else:
                zusammen.append(z)
        return zusammen
