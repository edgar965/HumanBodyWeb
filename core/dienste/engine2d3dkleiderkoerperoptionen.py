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
            'hinweis': 'Nach dem Körper prüft das Tor die Rumpftiefe der Figur gegen das Netz (Soll ≥ 75 %) und zählt die Regler am Anschlag (Soll ≤ 8; Regler, die überwiegend in Hand, Fingern oder Zehen wirken, zählen nicht). Bei „anhalten“ endet der Schritt dort mit '
                       'der Meldung — die späteren Teilschritte (Gesicht, Textur, Vorschau, Frisur) laufen dann nicht, und ohne sie gibt es keine Kleiderstücke (`genesis_ende.npz`). Gemessen: '
                       'Randy 58 % und 14 Regler, Generisch 70 % und 15 — bei Personen mit Shirt stehen oft Gelenkregler (Handgelenk, Knöchel, Schienbein) am Anschlag, ohne dass der Körper kaputt ist.',
        },
        {
            'schluessel': 'naht',
            'titel': 'Kopf an den Körper nähen',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — die Kappe am Hals des Kopfnetzes fällt weg, ein Band aus Dreiecken verbindet Körper- und Kopfring (Vorgabe)'),
                ('aus', 'Aus — Körper und Kopf werden nur an der Ebene getrennt, die Kappe des Kopfnetzes bleibt, zwischen beiden klafft eine Lücke (Stand bis 07.10.2026)'),
            ],
            'hinweis': 'Wirkt nur mit einem Kopfnetz (Schritt „Kopf“, Häkchen an). Das Kopfnetz aus dem Kopf-Ausschnitt endet am Hals in einer geschlossenen, geneigten Kappe; ohne Naht blieb ihr vorderer Teil als '
                       'Innenfläche im Hals und zwischen Körper und Kopf stand eine Lücke (`Meshfigurnaht`). Das Band folgt dem Körperring an der Schnittebene (bis 10 cm von der Halsachse — ein Hemdkragen zählt mit) '
                       'und dem offenen Rand der Halsröhre. Ob es die Figur verbessert, ist gemessen offen: `Edgar - Hunyan Kopf` stand mit Naht bei 10, ohne bei 9 Reglern am Anschlag.',
        },
        {
            'schluessel': 'landmarkmorphe',
            'titel': 'Brauen-, Mund- und Nasenmorph aus den Landmarken',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — im Schritt „Rest“ entstehen drei neue Morphe (Brauen, Mund, Nase), die den Rest über die Reglergrenzen hinaus holen (Vorgabe)'),
                ('aus', 'Aus — nur die Regler und der Rest-Morph (Stand bis 07.10.2026)'),
            ],
            'hinweis': 'Die Gesichtsregler für Lippen und Nase stehen bei einem Netz wie „Edgar 10“ zu zwei Dritteln am Anschlag, und die Landmarken der Figur liegen 1,5 bis 3,3 mm neben denen des Netzes '
                       '(innerer Mundspalt 2,8 gegen 0,4 mm). Je Bereich entsteht ein Gauß-Feld über die Landmarken (`Meshfigurlandmarkmorphe`: Ziel = Netz-Landmarke auf der Netzfläche, '
                       'höchstens 8 mm je Landmarke), abgelegt als eigener Morph mit eigenem Regler (Wert 1,0 in der Stellung). Nur mit Netz-Landmarken; das Gesichtsoval (Haar, Bart) bleibt draußen. '
                       'Die Lider sind seit 08.10.2026 nicht mehr im Morph: das Kopfnetz hat gemalte, halb geschlossene Augen, und die Lidränder darauf zu ziehen setzte die Lider auf die Augäpfel (weißer Augapfel stand darunter heraus).',
        },
        {
            'schluessel': 'regionen',
            'titel': 'Regionen-Regler (Hals, Unterarm, Handgelenk, Oberschenkel, Unterschenkel, Knöchel)',
            'art': 'wahl',
            'vorgabe': 'aus',
            'werte': [
                ('aus', 'Aus — nur die Daz-Regler und der Rest-Morph (Vorgabe)'),
                ('an', 'An — acht benannte Regler (`eigen:region_*`, −2 … 2) stehen in der Körperstufe der Anpassung zur Wahl'),
            ],
            'hinweis': 'Die Anpassung lässt Daz-Regler an ihre Grenze laufen, wo der Körper des Netzes mehr verlangt (an zwei Läufen desselben Fotos je 9 Regler am Anschlag: Hals, Unterarm, Handgelenk, Oberschenkel, Unterschenkel, Knöchel). '
                       'Der Rest landet im Eigenmorph, der eine Verschiebung je Käfigpunkt ist und keinen Namen hat. Mit „An“ kommen Regler dazu, die die Punkte um die Achse eines Gliedes (Gelenk zu Gelenk) nach außen oder '
                       'innen rücken (`G9koerperregionen`: weicher Rand entlang der Achse und quer dazu, links/rechts getrennt, 0,5–1,0 cm je Einheit, höchstens ±2). Sie sind Variablen der Körperstufe, also Teil der '
                       'Ableitung (Reglersatz `regionen`, einmal je Grundfigur gebaut). Gemessen am Foto von `Hunyan-Best` (08.10.2026, ein Lauf mit gegen zwei Läufe ohne): 9 Regler am Anschlag mit wie ohne (zwei Daz-Regler wurden frei, zwei andere liefen an), '
                       'Rest nach dem Eigenmorph 0,92 gegen 0,92–0,93 mm, Abstand Figur↔Netz 2,06 gegen 2,03–2,08 mm RMS. Etwas besser nur die Haut des Körpers (3,85 gegen 3,98–3,99 mm, Deckung 0,966 gegen 0,960), '
                       'die Kleiderstücke minimal höher (0,091 gegen 0,086–0,089; kleiner ist besser, im Rahmen der Streuung). Das Ziel, Regler vom Anschlag zu holen, ist nicht erreicht — darum Vorgabe aus.',
        },
        {
            'schluessel': 'spielraum',
            'titel': 'Spielraum der Körperregler über Dazʼ Grenze',
            'art': 'wahl',
            'vorgabe': 'aus',
            'werte': [
                ('aus', 'Aus — Dazʼ Grenze ±100 % (Vorgabe)'),
                ('150', '150 % — die Anpassung darf die Körperformregler bis ±150 % stellen'),
                ('200', '200 % — bis ±200 %'),
            ],
            'hinweis': 'Genesis klemmt jeden Formregler bei ±100 % (Dazʼ Grenze; Daz Studio kennt dafür „Limits off“). Am Foto von `Hunyan-Best` standen 9 Regler am Anschlag; '
                       'ein Test ohne Lauf (gleiche Verformung des Körpers mit kleinster Reglersumme, Abweichung 0,7 mm) holte vier davon weg — `Mass Forearms`, `Mass Hands`, `Mass Shins`, `Under Neck Height` '
                       '(sich überlappende Regler heben sich auf und laufen an die Grenze) —, aber fünf blieben auf ±100 %: `Neck Depth back`, `Glute Crease`, `Mass Wrist`, `Taper Shin B`, `Thigh Depth`. '
                       'Das Netz verlangt dort mehr, als Daz hergibt. Mit Spielraum rechnen Genesis (`G9reglergrenzen.SPIELRAUM`, Faktor 2), die Ableitung der Anpassung und das Tor mit den weiteren Grenzen; '
                       'nur ausdrücklich gestellte Werte gehen darüber hinaus, Formelwerte bleiben an Dazʼ Grenze. Ohne die Option wie bisher. Der Spielraum gilt nur für die Körperbereiche der Anpassung '
                       '(Stufe 3: Hals, Brust, Taille, Hüfte, Rücken, Arme, Hände, Beine, Füße) — nicht für Größen (`Proportion…`), Körpertypen, Charaktere und Posensteuerungen. '
                       'Der Schieber im Bedienfeld zeigt einen Wert über 100 % an und reicht dann bis 200 %.',
        },
        {
            'schluessel': 'kopfstreckung',
            'titel': 'Kopfnetz senkrecht strecken (%)',
            'art': 'zahl',
            'vorgabe': 0,
            'min': 0,
            'max': 25,
            'schritt': 1,
            'hinweis': 'Das Kopfnetz aus dem Kopf-Ausschnitt ist an Edgars Fotos um rund 11 % zu flach (Kamera über Kopfnetz-Landmarken gegen Foto-Landmarken angepasst: Streckung 1,111; Gesichtshöhe −15 und Nase–Kinn −16 mm, '
                       'die Breiten stimmen auf 1–2 mm). Mit 11 sank der Profil-RMS gegen das Seitenfoto von 7,5 auf 1,7 mm und der mittlere Maßfehler von 9,5 auf 7,2 %; die Breiten wurden dabei 5 mm kleiner, weil die '
                       'Einpassung einen Maßstab für Breite und Höhe wählt. 0 = aus (Vorgabe): der Wert hängt vom Foto, ein falscher Wert verlängert ein richtiges Gesicht. Wirkt nur mit Kopfnetz (Schritt „Kopf“, Häkchen an) '
                       'und erst, wenn „Körper“ neu rechnet; `kopf/mesh.glb` bleibt, die Kette bekommt `kopf/mesh_gestreckt_<Zehntelprozent>.glb`.',
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
        if roh.get('naht') in ('an', 'aus'):
            aus['naht'] = roh['naht']
        if roh.get('landmarkmorphe') in ('an', 'aus'):
            aus['landmarkmorphe'] = roh['landmarkmorphe']
        if roh.get('regionen') in ('an', 'aus'):
            aus['regionen'] = roh['regionen']
        if roh.get('spielraum') in ('aus', '150', '200'):
            aus['spielraum'] = roh['spielraum']
        for e in cls.KATALOG:
            if e['art'] == 'zahl' and roh.get(e['schluessel']) is not None:
                try:
                    aus[e['schluessel']] = round(min(e['max'], max(e['min'], float(roh[e['schluessel']]))), 3)
                except (TypeError, ValueError):
                    pass                    # unlesbar → bleibt die Vorgabe
        return aus
