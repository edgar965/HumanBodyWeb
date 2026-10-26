# -*- coding: utf-8 -*-
"""Architekturmesh3daikarte — Abschnitt „Auf der Karte, ohne ständiges Warten, reproduzierbar“ der Seite Hilfe → Architektur → Mesh3DAI (26.10.2026).

Edgar, 26.10.2026: „Wichtig ist, dass ein Prozess komplett auf GPU läuft und die CPU sich nicht ständig mit der GPU abstimmen muss“, „fixe das, kette muss Reproduzierbar sein“ und
„aktualisiere dann auch die …/hilfe/architektur/mesh3dai/ seite mit den neuen Sachen“. Aus dem Code gelesen beim Aufruf (`ast`, kein Import des Rechencodes in den Server): die Schalter
`GRAPH` von `Koerperangleich` und `Kopfangleich`, die Umgebung von `Determinismus` und welche Module ihn einschalten, die erste Zeile der Bausteine; aus der Prüfung „ganze Kette zweimal“
(`ProjektTemp/_wegwerf/reproduzierbar/vergleich.json`, `laeufe_vergleich.py`) das Ergebnis je Schritt. Von Hand mit Quelle: `MESSUNGEN` und `OFFEN`
(`Docu/tagebuch/2026-10-26_mesh3dai-alles-auf-der-karte.md`, `.claude/rules/mesh3dai-karte.md`).
"""

import ast
import json
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3daikarte']


class Architekturmesh3daikarte:
    #: (Modul, Klasse) der Bausteine — Text aus dem Docstring
    BAUSTEINE = (('mesh3dai_kostuem_raster', 'Kostuemraster'), ('mesh3dai_kostuem_maske', 'Kostuemmaske'), ('mesh3dai_schrittgraph', 'Schrittgraph'),
                 ('mesh3dai_kopfschritte', 'Kopfschritte'), ('mesh3dai_determinismus', 'Determinismus'), ('mesh3dai_vorrat', 'Vorrat'), ('mesh3dai_netzvorrat', 'Netzvorrat'),
                 ('mesh3dai_ansichtraster', 'Ansichtraster'))
    #: (Was, vorher, nachher, gemessen an) — Quelle: Tagebuch 26.10.2026, Abschnitt 4 (Ketten `koerper_eigen/abstimmung_kette3.sh` … `kette6.sh`)
    MESSUNGEN = (
        ('Wartepunkte der CPU, Schritt „koerper“', '15.112', '12.102', 'randy, trocken, deterministisch; `abstimmung_messen.py` (geeicht 4 → 4, 0 → 0)'),
        ('Wartepunkte der CPU, Schritt „kopf“', '43.991', '7.642', 'edgar_knopf, trocken, deterministisch'),
        ('Starts auf der Karte, „koerper“', '2.217.535', '513.430', 'randy; mit Graph zählt eine Wiedergabe als ein Start'),
        ('Starts auf der Karte, „kopf“', '1.297.988', '550.257', 'edgar_knopf'),
        ('Dauer „koerper“ (ohne → mit Graph)', '114,9 s', '60,4 s', 'randy, Karte 35 → 61 % ausgelastet, je ein Lauf'),
        ('Dauer „kopf“ (ohne → mit Graph)', '102,8 s', '63,0 s', 'edgar_knopf, je ein Lauf'),
        ('Rechnet derselbe Code in zwei Prozessen gleich? (ohne → mit `Determinismus`)', '862 von 2.275 Werten verschieden', '0 von 2.260', 'koerper an randy; kopf an edgar_knopf 84 von 320 → 0'),
        ('Umbau alt ↔ neu und Graph ↔ ohne (deterministisch)', '—', '0 verschieden', 'koerper 0 von 2.260, kopf 0 von 320, je auch die Startmessung'),
        ('Rendern: `Kostuemraster` gegen pyrender', '0,08–0,47 s je Bild', '0,02–0,03 s je Bild', 'randy, Maske 0–3 px anders, Farbe Ø 0,01–0,49 von 255'),
        # Quelle: Tagebuch 26.10.2026, Abschnitt 7 (`ProjektTemp/_wegwerf/platte/`, Messhaken auf jedes Python-`open`, Läufe 1–4 an randy_reproduzierbar)
        ('Gelesen je Kettenlauf ohne Python-Code', '18,5 GB', '5,0 GB', 'Lauf 1 (vorher, kalt) → Lauf 4 (Vorrat, Sperre im Prozess, warmer Skriptdienst); Rest u. a. MIA 3,3 GB, Stufe 2 0,9 GB'),
        ('Eingangsnetz geöffnet und zerlegt je Lauf', '43×', '4×', 'je 1,8 s trimesh auf der CPU; `Netzvorrat`'),
        ('Python-Prozesse je Lauf', '44', '26', '38 davon waren `gpu_sperre.py hole/gib` — die Sperre läuft jetzt im Prozess'),
        ('CPU des Steuerprozesses während des Laufs', '0,75 Kerne', '0,15 Kerne', 'Nachfragen beim Skriptdienst einmal je Sekunde statt 20-mal'),
        ('Dauer der ganzen Kette', '19:45 min', '14:35 min', 'Lauf 1 kalt gegen Lauf 4 warm, je ein Lauf, 2d-3d-AI rechnete zeitweise mit'),
        ('Schritt 7: Ansichten mit pyrender → `Ansichtraster` (torch)', 'je Lauf 48–112 px je Ansicht anders', 'bitgleich in zwei Prozessen', 'gegen pyrender Farbe Ø 1,06–1,39 Stufen, Maske 1–5 px; 1,0 s statt 6,8 s'),
        ('Ganze Kette zweimal vom selben Ausgangsstand', 'ab Schritt 7 verschieden', 'alle 211 Dateien gleich', 'Lauf 3 (kalt) gegen Lauf 4 (warm), dazu die Teile-Ablage bytegleich'),
    )
    OFFEN = (
        'Welche Rechnung zwei Läufe ohne `Determinismus` trennt, ist nicht zerlegt (torch ersetzt `index_add_` u. a. im deterministischen Modus still).',
        'Was `Determinismus` an Zeit kostet, ist nicht belastbar gemessen (je ein Lauf).',
        '`Genesis9/rasternachbarn._roh` wartet je Nachbarsuche noch tausendfach (4.344 im Kopf, 7.826 in der Kostüm-Prüfung) — geteilter Code mit 2d-3d-AI, nur nach Absprache.',
        'Der Rasterer wartet je Bild auf die Zahl seiner Bildpunkte (wechselt je Dreieck) — weg nur mit festen Größen; ein Bild dauert 0,02–0,03 s.',
        'Noch je Lauf von der Platte: MIA-Gewichte 3,3 GB, Stufe-2-Netze 0,9 GB, Kopfnetz, Haut-KI; Zwischenstände zwischen den Schritten (über 800 Öffnungen, 215 Dateien geschrieben) — '
        'Weitergabe im Speicher nicht gebaut.',
        'Beim ersten Start des Skriptdienstes ~9 GB Gewichte (SAM 3, Sapiens2, ViTPose) — weg nur mit einem Dienst, der zwischen den Läufen lebt und dann ~10 GB auf der Karte hält.',
    )
    VERGLEICH = Path(r'A:\3DTools\ProjektTemp\_wegwerf\reproduzierbar\vergleich.json')

    @staticmethod
    def ordner():
        return Path(settings.TOOLS_ROOT) / 'mesh3dai'

    @classmethod
    def _klasse(cls, modul, name):
        baum = ast.parse((cls.ordner() / (modul + '.py')).read_text(encoding='utf-8'))
        return baum, next((k for k in baum.body if isinstance(k, ast.ClassDef) and k.name == name), None)

    @classmethod
    def _wert(cls, modul, klasse, feld):
        """Literal einer Klassenkonstante; Schlüssel eines Wörterbuchs dürfen andere Konstanten derselben Klasse sein (`UMGEBUNG = {SCHALTER: '1', …}`)."""
        _baum, k = cls._klasse(modul, klasse)
        felder = {z.targets[0].id: z.value for z in (k.body if k else ()) if isinstance(z, ast.Assign) and len(z.targets) == 1 and isinstance(z.targets[0], ast.Name)}

        def lesen(knoten):
            if isinstance(knoten, ast.Name) and knoten.id in felder:
                return lesen(felder[knoten.id])
            if isinstance(knoten, ast.Dict):
                return {lesen(s): lesen(w) for s, w in zip(knoten.keys, knoten.values, strict=True)}
            return ast.literal_eval(knoten)
        if feld not in felder:
            return None
        try:
            return lesen(felder[feld])
        except ValueError:
            return ast.unparse(felder[feld])

    @classmethod
    def _text(cls, modul, name):
        baum, k = cls._klasse(modul, name)
        doc = (ast.get_docstring(k) if k else None) or ast.get_docstring(baum) or ''
        absatz = doc.strip().split('\n\n')[0].replace('\n', ' ')
        return absatz[:420] + ('…' if len(absatz) > 420 else '')

    @classmethod
    def _schalter(cls):
        """Welche Module `Determinismus` einschalten, und ob der Rechenlauf ihn für jeden Schritt setzt."""
        rufer = sorted(p.name for p in cls.ordner().glob('*.py') if p.name != 'mesh3dai_determinismus.py' and 'Determinismus.' in p.read_text(encoding='utf-8'))
        lauf = Path(settings.BASE_DIR) / 'core' / 'dienste' / 'mesh3dairechenlauf.py'
        return rufer, "MESH3DAI_DETERMINISTISCH='1'" in lauf.read_text(encoding='utf-8')

    @classmethod
    def vergleich(cls):
        """Ergebnis der Prüfung „ganze Kette zweimal“ je Schritt — None, wenn sie noch nicht gerechnet hat."""
        try:
            d = json.loads(cls.VERGLEICH.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        schritte = [{'schritt': k, 'gleich': v['gleich'], 'anders': len(v['anders']), 'beispiel': '; '.join('%s — %s' % (n, r[:160]) for n, r in v['anders'][:2])}
                    for k, v in d.items() if k != 'nur']
        return {'datei': str(cls.VERGLEICH), 'schritte': schritte, 'nur': d.get('nur') or [], 'gleich': not d.get('nur') and all(s['anders'] == 0 for s in schritte)}

    @classmethod
    def kontext(cls):
        rufer, lauf_setzt = cls._schalter()
        return {
            'graph': {'koerper': cls._wert('mesh3dai_koerperangleich', 'Koerperangleich', 'GRAPH'), 'kopf': cls._wert('mesh3dai_kopfangleich', 'Kopfangleich', 'GRAPH')},
            'umgebung': cls._wert('mesh3dai_determinismus', 'Determinismus', 'UMGEBUNG') or {}, 'samen': cls._wert('mesh3dai_determinismus', 'Determinismus', 'SAMEN'),
            'rufer': rufer, 'lauf_setzt': lauf_setzt,
            'bausteine': [{'modul': m, 'klasse': k, 'text': cls._text(m, k)} for m, k in cls.BAUSTEINE if (cls.ordner() / (m + '.py')).is_file()],
            'messungen': cls.MESSUNGEN, 'offen': cls.OFFEN, 'vergleich': cls.vergleich(),
        }
