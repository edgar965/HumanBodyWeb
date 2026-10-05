# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkoerperoptionen — die Gruppe `koerper` der Optionen von „2D3D Kleider": woher die Figur kommt.

Dieselbe Katalogform wie `Iterationsoptionen`. `quelle` entscheidet den Schritt „koerper" (`Engine2d3dKleiderkoerper`):
`uebernehmen` nimmt den fertigen Fit eines Auftrags „Mesh to 3D" (`auftrag` = seine Kennung), `rechnen` rechnet
die Kette auf dem Netz dieses Auftrags. Die Feinheiten der Kette (Runden, Dämpfung, Eigenmorph …) sind die
Vorgaben von `Meshfiguroptionen`.
"""

import re

__all__ = ['Engine2d3dKleiderkoerperoptionen']


class Engine2d3dKleiderkoerperoptionen:
    KENNUNG = re.compile(r'^\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2}$')
    KATALOG = [
        {
            'schluessel': 'quelle',
            'titel': 'Figur',
            'art': 'wahl',
            'vorgabe': 'uebernehmen',
            'werte': [
                ('uebernehmen', 'Aus einem fertigen Auftrag „Mesh to 3D" übernehmen (Sekunden)'),
                ('rechnen', 'Auf dem Netz dieses Auftrags rechnen — die Kette von „Mesh to 3D" (~15 min Grafikkarte)'),
            ],
            'hinweis': 'Übernehmen: Reglerstellung, Eigenmorph, Kacheln und das Netz des Fits als 3D-Bezug der '
                       'Iterationen.',
        },
        {
            'schluessel': 'auftrag',
            'titel': 'Auftrag „Mesh to 3D" (Kennung)',
            'art': 'text',
            'vorgabe': '',
            'hinweis': 'Die Kennung der Seite, etwa 2026.09.29.15.42.36 — nur bei „übernehmen".',
        },
        {
            'schluessel': 'tor',
            'titel': 'Körper-Tor',
            'art': 'wahl',
            'vorgabe': 'anhalten',
            'werte': [
                ('anhalten', 'Anhalten — der Lauf stoppt nach dem Körper, wenn der Rumpf zu flach ist oder zu viele Regler am Anschlag stehen (Vorgabe)'),
                ('melden', 'Nur melden — der Lauf geht weiter (Gesicht, Textur, Frisur, Kleiderstücke); das Urteil steht im Ergebnis und im Protokoll'),
            ],
            'hinweis': 'Nach dem Körper prüft das Tor die Rumpftiefe der Figur gegen das Netz (Soll ≥ 75 %) und zählt die Regler am Anschlag (Soll ≤ 8). Bei „anhalten“ endet der Schritt dort mit '
                       'der Meldung — die späteren Teilschritte (Gesicht, Textur, Vorschau, Frisur) laufen dann nicht, und ohne sie gibt es keine Kleiderstücke (`genesis_ende.npz`). Gemessen: '
                       'Randy 58 % und 14 Regler, Generisch 70 % und 15 — bei Personen mit Shirt stehen oft Gelenkregler (Handgelenk, Knöchel, Schienbein) am Anschlag, ohne dass der Körper kaputt ist.',
        },
        {
            'schluessel': 'oberteil',
            'titel': 'Oberteil',
            'art': 'wahl',
            'vorgabe': 'bibliothek',
            'werte': [
                ('bibliothek', 'Genesis-T-Shirt aus der Bibliothek, in der Farbe des Fotos (Vorgabe)'),
                ('foto', 'Aus dem Netz der Fotos geschnitten (Fotostück)'),
            ],
            'hinweis': 'Das Fotostück folgt der Maske des Netzes: Saum und Ausschnitt fransen aus, der Stoff steht einige Zentimeter vom Körper ab, einen Saum gibt es nicht. Das Genesis-T-Shirt hat Saum, '
                       'Ausschnitt und Ärmelabschlüsse; seine Farbe nimmt es aus dem Foto. Es hat kurze Ärmel — bei einem langärmeligen Oberteil „Aus dem Netz geschnitten" wählen. Hose und Socken kommen weiter '
                       'aus dem Netz. Wirkt auf die Bühne vor den Iterationen und auf Runde 1.',
        },
        {
            'schluessel': 'tiefe',
            'titel': 'Rumpftiefe an das Seitenfoto angleichen',
            'art': 'wahl',
            'vorgabe': 'aus',
            'werte': [
                ('aus', 'Aus — das Netz bleibt, wie es ist (Vorgabe)'),
                ('an', 'An — die Tiefe des Rumpfs (Bauch bis Schulter) höchstens so groß wie im Seitenfoto'),
            ],
            'hinweis': 'Das Netz kann am Bauch tiefer sein als die Silhouette im Seitenfoto (Testauftrag: bei 0,50 und 0,55 der Körpergröße 33 und 29 mm), und Körper und Hemd folgen ihm. Mit „An“ '
                       'schreibt der Schritt „Körper“ vor der Kette ein abgeleitetes Netz (`arbeit/netz_tiefe.glb`), dessen Tiefe dort an das Seitenfoto angeglichen ist — nur verkleinert, die Rückseite '
                       'bleibt, die Arme bleiben; Original, Segmentierung und Netz-Ansicht bleiben unberührt. Braucht ein Seitenfoto (Rolle „rechts“ oder „links“); sonst bleibt das Netz und der Grund '
                       'steht im Zettel. Nur bei Quelle „rechnen“.',
        },
        {
            'schluessel': 'tiefe_min',
            'titel': 'Rumpftiefe: stärkste Verkleinerung (Faktor)',
            'art': 'zahl',
            'vorgabe': 0.8,
            'min': 0.5,
            'max': 1.0,
            'schritt': 0.01,
            'fein': True,
            'hinweis': 'Die Tiefe wird höchstens auf diesen Anteil verkleinert (0,8 = um höchstens ein Fünftel) — Schutz gegen ein Seitenfoto, das schlecht passt.',
        },
        {
            'schluessel': 'tiefe_toleranz',
            'titel': 'Rumpftiefe: Toleranz gegen das Foto (%)',
            'art': 'zahl',
            'vorgabe': 3,
            'min': 0,
            'max': 20,
            'schritt': 1,
            'fein': True,
            'hinweis': 'Erst wenn das Netz mehr als so viel Prozent tiefer ist als das Seitenfoto, wird es verkleinert (Perspektive und Mattierung des Fotorands machen kleine Unterschiede).',
        },
    ]
    FEIN_TITEL = 'Feineinstellungen der Rumpftiefe'

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def oberteil(cls, job):
        """Die gewählte Quelle des Oberteils eines Auftrags: `bibliothek` | `foto` (ohne gespeicherte Wahl die Vorgabe)."""
        wert = ((getattr(job, 'optionen', None) or {}).get('koerper') or {}).get('oberteil')
        return wert if wert in ('bibliothek', 'foto') else cls.vorgaben()['oberteil']

    @classmethod
    def katalog(cls):
        aus = []
        for e in cls.KATALOG:
            werte = [{'wert': w, 'text': t} for w, t in e.get('werte', [])]
            aus.append(dict(e, werte=werte, fein=bool(e.get('fein'))))
        return {'optionen': aus, 'fein_titel': cls.FEIN_TITEL}

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        wert = roh.get('quelle')
        if wert in ('uebernehmen', 'rechnen'):
            aus['quelle'] = wert
        auftrag = str(roh.get('auftrag') or '').strip()
        if cls.KENNUNG.match(auftrag):
            aus['auftrag'] = auftrag
        if aus['quelle'] == 'uebernehmen' and not aus['auftrag']:
            aus['quelle'] = 'rechnen'       # ohne Kennung scheitert „übernehmen" immer (01.10.2026: neuer Auftrag)
        if roh.get('tiefe') in ('aus', 'an'):
            aus['tiefe'] = roh['tiefe']
        if roh.get('tor') in ('anhalten', 'melden'):
            aus['tor'] = roh['tor']
        if roh.get('oberteil') in ('bibliothek', 'foto'):
            aus['oberteil'] = roh['oberteil']
        for e in cls.KATALOG:
            if e['art'] == 'zahl' and roh.get(e['schluessel']) is not None:
                try:
                    aus[e['schluessel']] = round(min(e['max'], max(e['min'], float(roh[e['schluessel']]))), 3)
                except (TypeError, ValueError):
                    pass                    # unlesbar → bleibt die Vorgabe
        return aus
