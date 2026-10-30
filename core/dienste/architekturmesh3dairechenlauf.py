# -*- coding: utf-8 -*-
"""Architekturmesh3dairechenlauf — Abschnitt „Rechnen per Knopf: die Kette im Projekt“ der Seite Hilfe → Architektur → Mesh3DAI (24.10.2026).

Edgar, 24.10.2026: „update /hilfe/architektur/mesh3dai/ mit dem genauen Code, inkl. Kopf KI und allen Änderungen der letzten Tage“. Aus dem Code gelesen beim Aufruf:
die Schritte (`Mesh3dairechenlauf.SCHRITTE`, Aufruf genau so, wie der Arbeitsprozess ihn startet), die Netze (`Mesh3daikifassungen`), die Testfälle der Kostüm-Prüfung
(`mesh3dai/mesh3dai_kostuem_pruefung.py`: `FASSUNG`, `TEXTE` und die Zeilen `#:` darüber, per `ast` — kein Import des Rechencodes in den Server), der jüngste fertige Rechenlauf eines Tests
(`_test/<k>/rechnen/stand.json`) und dessen jüngste Prüfung (`_test/<k>/kostuem/lauf_*.json`). Von Hand: `NEU` (Änderungen der letzten Tage, Zahlen aus `.claude/rules/mesh3dai-rechenlauf.md`).
"""

import ast
import json
import re
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3dairechenlauf']


class Architekturmesh3dairechenlauf:
    #: (Datum, was, gemessen) — Quelle `.claude/rules/mesh3dai-rechenlauf.md` und die Docstrings der genannten Klassen
    NEU = (
        ('23.10.2026', 'Rechencode ins Projekt (`A:\\3DTools\\mesh3dai\\`, 185 Module aus `_wegwerf/`), Rechnen per Knopf mit festen Schritten, Warteschlange (ein Lauf zur Zeit), Netze in '
                       '`ki_fassungen.json`', 'OlesiaWalk per Klick 921 s, edgar_knopf 458 s'),
        ('23.10.2026', 'Kostüm-Weg A: Kleider und Haar aus dem Mesh erkennen (Sapiens2 + SAM 3), ausschneiden, an die Stelle des Eingangs auf die Figur legen (Rückhäutung), Hautmasken; '
                       'Kostüm-Prüfung mit Testfällen (Fassungen 1–5)', 'Hose edgar_knopf „Loch im Stück“ 5 → 0'),
        ('23.10.2026', 'Haut aus der KI (Stufe 2) im Rechenlauf; Zuordnung der Kacheln nach UV-Lage', 'edgar_knopf Hautton ΔE 16,2 → 4,3'),
        ('24.10.2026', 'Haltung aus Gelenken und Enden als CUDA-Graph (`Ikgraph`, 3.000 Schritte, Finger/Zehen/Gesicht Gewicht 0,05); Testfälle „Haltung folgt der KI“ und „Flecken in der Haut“ '
                       '(Fassung 6)', 'Hauptgelenke an 12 Tests 47,4 → 29,1 mm, Hose edgar_knopf Durchstich 40,1 → 6,5 %'),
        ('24.10.2026', 'Testfall „Gesicht wie der Eingang“ (Fassung 7, `Kostuemgesicht`); Kopfnetz gemessen und allein NICHT eingesetzt; Schritt „kopf“ = Kopfnetz + `Kopfangleich`',
         'edgar_knopf Gesichtsmaße 4 → 0 von 11 rot'),
        ('24.10.2026', 'Kostüm-Prüfung auf der Karte statt im GL-Kontext je Bild: ein Renderer je Bildgröße und eine Szene je Messung (`Kostuemrender`, jedes Netz einmal hochgeladen); '
                       'Fenstersumme der Flecken als zwei Streifen statt 31×31-Kern', 'Schritt „kleider“ edgar_knopf 121 → 54 s (py-spy aktiv 112 → 47 s), 694 von 707 Messwerten gleich'),
        ('24.10.2026', 'Haut-KI im Bildraum (`Hautnetz`, `KoerperKI_alle`): gesehene Haut abgeholt, ungesehene erzeugt; Lauf hautki_rand eingesetzt', 'echte Haut der Tripo-Jobs 15,84 sRGB (Stufe 2: 14,86)'),
        ('24.10.2026 abends', 'Skriptdienst: ein Dauerprozess je Umgebung rechnet die Skripte der Kette; Fehler behoben — ein Modul, das während eines Auftrags geändert wurde, blieb alt im Speicher',
         'baron, ed_mesh, ed_mesh1 prüften mit Fassung 13 statt 14 (Dienst seit 18:12:38, Prüfung geändert 18:14:23)'),
        ('24.10.2026 abends', 'Kostüm-Prüfung Fassung 13–15: Kostümfarbe und Durchsicht ohne die Fehlalarme an ballerina_bunt; neue Testfälle „Glied im Eingang“, „Knochenlängen der KI“, '
                              '„Erkennung wie die Bildmodelle“', 'Glied im Eingang rot: ballerina_pilz 7 von 12, ballerina_bunt 6, baron 3, edgar_knopf 0'),
        ('24.10.2026 abends', 'Haut-KI: Prüfung „Hautton und Tattoos folgen dem Eingang“ (`Hautkitoene`) und Training mit umgefärbter Haut (`Hautfaerbung`: grau, weiß, gelb, dunkel, Tattoos)',
         'hautki_rand 6 von 12 rot → hautki_toene 3 von 12 (gelb ΔE 20,6 → 7,4); ballerina_bunt „Hautton der Figur“ 17,9 → 13,0; Tattoos noch 0,28 — nicht eingesetzt'),
        ('24.10.2026 nachts', 'Erkennung: Regel „Farbe gegen Stimme“ (eine Kostüm-Insel wird nur Haut, wenn mehr Fläche im Hautton liegt, als die Bildmodelle Kostüm sahen) gebaut und gegen die Wahrheit gemessen',
         'an den sechs Tripo-Jobs kein Gewinn, echte Haut → Kostüm +0,1 bis +0,8 Punkte — aus'),
        ('24.10.2026 nachts', 'Vorstufe: Testfall „Knochenlängen in der Haltung“ (`Haltungslaengen`) und Training mit Längenverlust in der Haltung (`--laenge`, Abbildung A-Pose → Haltung je Wolke)',
         'acht Tests Ø je Glied 12,5 → 8,8 mm, rot 6 → 4 von 8, Gelenklage 20,2 → 19,7 mm — nicht eingesetzt'),
        ('24.10.2026 nachts', 'Kostüm-Prüfung Fassung 16: „Lage des Gesichts wie der Eingang“ (`Kostuemgesichtslage`); Ursache „Kopf im Hut“: das Netz der Vorstufe liest den Kopf am oberen Ende der Wolke ab',
         'rot an 8 von 27 Tests (randy 85, zauberer 67 mm); Kopfbedeckung als Augmentierung (`Hutaugment`) in zwei Runden — unter Hüten halbiert, Kronen schlechter — nicht eingesetzt'),
        ('24.10.2026 nachts', 'Längen-Netz der Vorstufe eingesetzt (`vorstufe_mia` = apose9_mia_laenge); Netz des alten Wegs als eigener Schlüssel `vorstufe` in den KI-Fassungen',
         'Gelenklage der Tripo-Jobs 20,2 → 19,7 mm; Haut-KI hautki_toene an randy/n1_n2: Hautton besser, Zeichnung schlechter — nicht eingesetzt'),
        ('24.10.2026 nachts', 'Kostüm-Prüfung Fassung 17: „Form des Körpers wie der Eingang“, „Gelenke wie der Eingang“ (`Kostuemmesspunkte`, Rechnung von 2d-3d-AI: ViTPose und 40 Randpunkte je Ansicht); '
                              'Zeile „Messpunkte des Körpers“ auf der Testseite', 'randy_tropical vor dem Schritt „lage“: Form 95 von 117 rot, Gelenke 81 von 92'),
        ('24.10.2026 nachts', 'Schritt „lage“ (`Lageangleich`): Versatz der Gelenke aus den Messpunkten in die Ziele der Winkelanpassung; eine Runde gilt nur, wenn die Messpunkte besser werden UND '
                              'das Skelett folgt (Rest ≤ +5 mm) — die erste Fassung ohne diese Bedingung verdrehte bei randy Becken und Bein',
         'randy: Form 12, Gelenke 29 rot, Haltung 19 mm (erste Fassung 19 / 17 / 50 mm, Haut durch Stück 12 → 9)'),
        ('24.10.2026 nachts', 'Kostüm-Prüfung Fassung 18: „Blickrichtung wie der Eingang“ (`Kostuemblick`, Gesichtsfinder von MediaPipe je Ansicht gegen die Augen der Figur); die Vorstufe dreht ein '
                              'Netz, das nicht zur Kamera blickt (`Vorstufenblick`)', 'zauberer_fantasy 124° rot, ballerina_bunt 6°, edgar_knopf 1° (Augen von ViTPose allein: ballerina 132°, Fehlalarm)'),
        ('24.10.2026 nachts', 'Ganze Kette in python14 und in einem Prozess (Skriptdienst, `Stimmenschritt`; Kopf und Lage rufen die Haltung im selben Prozess); open3d durch `Netzausduennung` (GPU) ersetzt',
         'Gegenprobe randy: acht Schritte bitgleich zu python10; Vorschau 61 s → 0,1–1,0 s'),
        # 26.10.2026 (Edgar: „aktualisiere … mit den neuen Sachen“) — Quelle: Tagebuch 2026-10-25_mesh3dai-koerper-in-die-aussenmasse-und-haut-relativ.md, 2026-10-25_haut-ton-ki-je-koerperteil.md,
        # 2026-10-26_mesh3dai-alles-auf-der-karte.md; Docstring `Koerperangleich` (Fassung 6)
        ('25.10.2026', 'Schritt „koerper“ (`Koerperangleich`) nach „lage“: Körperregler, Daz-Proportionen und Haltung gegen Umriss, Haut, Boden, Kopfform und Lage des Gesichts, jede Runde an der echten '
                       'Formung; übernommen nur, was an der gebauten Figur besser ist', 'zauberer_fantasy ab „figur“: Prio 1 128 → 73 rot, Umriss und Lage des Gesichts grün, Gelenke 33 von 92 rot'),
        ('25.10.2026', 'Kostüm-Prüfung bis Fassung 21 (Hautton zurückbelichtet, Entlichtung wie die Wahrheit, Haut durch Stück im Tanz, Glieder — die Fassungen stehen unten); Stab nie Haut '
                       '(Farbregel und „Stück in Hautfarbe“ ohne Requisiten)', 'Zahlen je Fassung in der Fassungsgeschichte'),
        ('25.10.2026', 'Haut-KI im Ton des Eingangs (Bauart relativ 2, Abholanteil) und Ton-KI je Körperteil (`KoerperKI_alle`, Prüfung `Hautkitoene` Fassung 5)',
         'ballerina_bunt Hautton 20,1 → 13,9 (relativ 2); Ton-KI: Tonfälle grün, echter Eingang an OlesiaSitzend und Rainy schlechter — beides nicht eingesetzt'),
        ('25.10.2026', 'MIA-Nachbau in python14 (`mesh3dai_miaeigen*`, Dauerprozess über `Miadienst`; Rückfall das Original in python11_mia); Sapiens2, SAM 3 und ViTPose als python14-Ports', '—'),
        ('26.10.2026 nachts', 'Eigenregler-KI Fassung 1 (je Punkt ein kleines Netz für Gewicht und Korrektur, Anfasser per Ausgleichsrechnung)',
         'sechs Tripo-Jobs: nichts tun 6,87 mm, KI 7,28 mm — schlechter als nichts tun, nicht angewandt'),
        ('26.10.2026', 'Schritt „koerper“ Fassung 6: die Anfasser der Körper-Eigenregler (Katalog von 2d-3d-AI) als zweite Stellgröße neben den Reglern (`Koerperangleichstellen`)',
         'randy, trocken: 389 Anfasser bewegt, übernommen Runde 2'),
        ('26.10.2026', 'Auf der Karte statt CPU: Rendern in torch (`Kostuemraster` statt pyrender), Löcher und Inseln (`Kostuemmaske`), ViTPose-Bild, Formmass2-Tafeln; Wartepunkte entfernt, '
                       'Körper und Kopf als CUDA-Graph — Abschnitt „Auf der Karte“', 'koerper 115 → 60 s, kopf 103 → 63 s, bitgleich; Rendern 0,08–0,47 → 0,02–0,03 s je Bild'),
        ('26.10.2026', 'Reproduzierbar: `Determinismus` (torch deterministisch, cuBLAS, feste Samen, PYTHONHASHSEED) in jedem Prozess der Kette',
         'ohne: derselbe Code in zwei Prozessen 862 von 2.275 Werten verschieden (koerper); mit: 0'),
        ('26.10.2026', 'Augen im Skriptdienst: der Zwischenspeicher der Augäpfel (`Koerperanhaenge`) kannte die Eigenregler nicht — ein Bau mit gleichen Daz-Werten bekam die Augen des vorigen',
         'EdgarTrip im Dienst 247 statt 226 Abnahmefehler (gemessen von der 2d-3d-AI-Sitzung)'),
    )

    @staticmethod
    def _json(p):
        try:
            return json.loads(Path(p).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def kontext(cls):
        from .architekturmesh3daiklassen import Architekturmesh3daiklassen
        from .mesh3daikifassungen import Mesh3daikifassungen
        from .mesh3dairechenlauf import Mesh3dairechenlauf
        f = Mesh3daikifassungen.lesen()
        schritte = []
        for nr, (s, text, argumente) in enumerate(Mesh3dairechenlauf.SCHRITTE, start=1):
            schritte.append({'nr': nr, 'schluessel': s, 'text': text, 'aufruf': 'python14 ' + ' '.join(argumente), 'skript': Architekturmesh3daiklassen.skript(argumente),
                             'fassungen': sorted(set(re.findall(r'\{(\w+)\}', ' '.join(argumente))) & set(f))})
        tests = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_test'
        return {'schritte': schritte, 'fassungen': [{'schluessel': k, 'wert': v, 'text': Mesh3daikifassungen.TEXTE.get(k, '')} for k, v in f.items()],
                'lauf': cls.letzter_lauf(tests), 'pruefung': cls.pruefung(), 'neu': cls.NEU, 'haut': Mesh3dairechenlauf.HAUT,
                'klassen': Architekturmesh3daiklassen.kontext(Mesh3dairechenlauf.SCHRITTE)}

    @classmethod
    def letzter_lauf(cls, tests):
        """Der jüngste fertige Rechenlauf eines Tests: Dauer je Schritt, dazu dessen jüngste Kostüm-Prüfung."""
        beste = None
        for datei in tests.glob('*/rechnen/stand.json'):
            s = cls._json(datei)
            if s and s.get('status') == 'fertig' and s.get('ende') and (beste is None or s['ende'] > beste[0]['ende']):
                beste = (s, datei.parent.parent)
        if beste is None:
            return None
        s, ordner = beste
        laeufe = sorted(ordner.glob('kostuem/lauf_*.json'))
        bericht = cls._json(laeufe[-1]) if laeufe else None
        nachher = (bericht or {}).get('nachher') or {}
        return {'kennung': s.get('kennung'), 'ende': s.get('ende'), 'dauer_s': s.get('dauer_s'), 'ab': s.get('ab'),
                'schritte': [{'schluessel': x.get('schluessel'), 'dauer_s': x.get('dauer_s'), 'uebernommen': x.get('uebernommen', False)} for x in s.get('schritte', [])],
                'pruefung_datei': laeufe[-1].name if laeufe else None, 'prio': nachher.get('prio'),
                'tests': [{'name': n, 'prio': z.get('prio'), 'rot': z.get('nachher'), 'von': z.get('pruefungen'), 'fehler': '; '.join((z.get('fehlertexte') or [])[:2])}
                          for n, z in sorted((nachher.get('tests') or {}).items(), key=lambda kv: (kv[1].get('prio', 9), kv[0]))]}

    @staticmethod
    def _konstanten(koerper):
        """Konstanten `NAME = …` und (seit 30.10.2026, `Kostuemfalten`) `A, B = x, y`."""
        aus = {}
        for k in koerper:
            if not isinstance(k, ast.Assign) or len(k.targets) != 1:
                continue
            ziel = k.targets[0]
            if isinstance(ziel, ast.Name):
                aus[ziel.id] = k.value
            elif isinstance(ziel, ast.Tuple) and isinstance(k.value, ast.Tuple) and len(ziel.elts) == len(k.value.elts):
                aus.update({n.id: w for n, w in zip(ziel.elts, k.value.elts, strict=True) if isinstance(n, ast.Name)})
        return aus

    @classmethod
    def _wert(cls, knoten, quelle, ordner, klasse=None):
        """Wert eines Ausdrucks im Quelltext, ohne Import des Rechencodes: Literale, `**Klasse.TEXTE` in einem Wörterbuch (seit Prüfung Fassung 15 stehen Testfälle in eigenen Klassen — die
        Klasse über ihren Import `from <modul> import <Klasse>` in `ordner/<modul>.py`, rekursiv: seit Fassung 18 trägt `Kostuemmesspunkte.TEXTE` selbst `**Kostuemblick.TEXTE`), Namen (Konstanten
        der Klasse oder des Moduls), `Klasse.KONSTANTE` und `'…' % (…)`. Seit 25.10.2026 schreibt `Kostuemtanz.TEXTE = {NAME: (1, '… %d Bilder …' % (Kostuemtanzbilder.BILDER, DURCH_MM, ROT_MIN))}`
        — mit Literalen allein fiel der ganze Abschnitt aus („malformed node or string … Name(id='NAME')“, gefunden 26.10.2026)."""
        baum = ast.parse(quelle)
        module = {a.asname or a.name: n.module for n in baum.body if isinstance(n, ast.ImportFrom) and n.module for a in n.names}
        namen = cls._konstanten(baum.body)
        namen.update(cls._konstanten(klasse.body) if klasse is not None else {})

        def auswerten(k):
            if isinstance(k, ast.Constant):
                return k.value
            if isinstance(k, ast.Name) and k.id in namen:
                return auswerten(namen[k.id])
            if isinstance(k, ast.Attribute) and isinstance(k.value, ast.Name) and k.value.id in module:
                fremd = (ordner / (module[k.value.id] + '.py')).read_text(encoding='utf-8')
                kl = next(c for c in ast.parse(fremd).body if isinstance(c, ast.ClassDef) and c.name == k.value.id)
                return cls._wert(cls._konstanten(kl.body)[k.attr], fremd, ordner, kl)
            # `*`, `-`, `/` seit 30.10.2026: ein Text rechnet `100 * ANTEIL_MAX` — ohne sie fiel der ganze Abschnitt aus („Rechenlauf: ValueError: Testfälle: 100 * ANTEIL_MAX“)
            rechnung = {ast.Mod: lambda a, b: a % b, ast.Add: lambda a, b: a + b, ast.Mult: lambda a, b: a * b, ast.Sub: lambda a, b: a - b, ast.Div: lambda a, b: a / b}
            if isinstance(k, ast.BinOp) and type(k.op) in rechnung:
                return rechnung[type(k.op)](auswerten(k.left), auswerten(k.right))
            if isinstance(k, ast.UnaryOp) and isinstance(k.op, ast.USub):
                return -auswerten(k.operand)
            if isinstance(k, (ast.Tuple, ast.List)):
                return (tuple if isinstance(k, ast.Tuple) else list)(auswerten(e) for e in k.elts)
            if isinstance(k, ast.Dict):
                aus = {}
                for schl, wert in zip(k.keys, k.values, strict=True):
                    if schl is None:
                        aus.update(auswerten(wert))
                    else:
                        aus[auswerten(schl)] = auswerten(wert)
                return aus
            raise ValueError('Testfälle: %s nicht lesbar (Zeile %s)' % (ast.unparse(k)[:80], getattr(k, 'lineno', '?')))
        return auswerten(knoten)

    @staticmethod
    def pruefung():
        """Testfälle der Kostüm-Prüfung aus dem Quelltext (ast, ohne Import): Fassung, Fassungsgeschichte (Zeilen `#:` vor `FASSUNG`), Prio und Text je Testfall."""
        datei = Path(settings.TOOLS_ROOT) / 'mesh3dai' / 'mesh3dai_kostuem_pruefung.py'
        quelle = datei.read_text(encoding='utf-8')
        klasse = next(k for k in ast.parse(quelle).body if isinstance(k, ast.ClassDef) and k.name == 'Kostuempruefung')
        werte, zeile_fassung = {}, None
        for k in klasse.body:
            if isinstance(k, ast.Assign) and len(k.targets) == 1 and isinstance(k.targets[0], ast.Name) and k.targets[0].id in ('FASSUNG', 'TEXTE'):
                werte[k.targets[0].id] = Architekturmesh3dairechenlauf._wert(k.value, quelle, datei.parent, klasse)
                if k.targets[0].id == 'FASSUNG':
                    zeile_fassung = k.lineno
        zeilen = quelle.splitlines()[klasse.lineno:zeile_fassung - 1] if zeile_fassung else []
        geschichte = []
        for z in zeilen:
            z = z.strip()
            if z.startswith('#:'):
                text = z[2:].strip()
                if geschichte and not re.match(r'^\d+ \(', text):
                    geschichte[-1] += ' ' + text
                else:
                    geschichte.append(text)
        return {'fassung': werte.get('FASSUNG'), 'geschichte': geschichte, 'datei': datei.name,
                'tests': [{'name': n, 'prio': p, 'text': t} for n, (p, t) in sorted((werte.get('TEXTE') or {}).items(), key=lambda kv: kv[1][0])]}
