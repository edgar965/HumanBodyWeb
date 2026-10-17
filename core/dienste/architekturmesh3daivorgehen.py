# -*- coding: utf-8 -*-
"""Architekturmesh3daivorgehen — wie der Datensatz und das Training von Mesh3D-AI entstanden sind, für Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar: „schreibe deine vorgehensweise von gerade eben darunter mit möglichst vielen Details, z.B. Posen, Trainingsschritte, Dauer je schritt, je pose usw".
Beim Aufruf GELESEN: die Proben (`3DObjects/mesh3dai/<ordner>/proben.json`), der jüngste Lauf (`lauf_ergebnis.json`: Verlauf je Epoche, Maße je Gruppe) und je Probe Fehler und
Abstand zur nächsten Trainingspose (`Mesh3daidaten.proben`, `Mesh3daivergleich`). Von Hand, jede Zahl mit Quelle: die Einstellungen des Trainingsskripts (`TRAINING`), die Zeiten je Schritt
(`SCHRITTE`, gemessen) und die Befunde unterwegs (`BEFUNDE`).
"""

from pathlib import Path

import numpy as np

__all__ = ['Architekturmesh3daivorgehen']


class Architekturmesh3daivorgehen:
    #: Die Einstellungen des heutigen Trainings, gelesen aus `ProjektTemp/_wegwerf/mesh3dai_form_alle.py`, `mesh3dai_stimmen_netz.py`, `mesh3dai_formnetz.py` (16.10.2026 abends).
    TRAINING = (
        ('Verlust', 'Stimmen: Abstand der gestimmten Ziele (138 Gelenke + 138 Enden) in m, dazu ein Zug auf die Stimmen nahe am Ziel (Gauß 0,10 m) und Kreuzentropie auf die Gewichte × 0,01 '
         '(`--aufmerk`); plus 1 × Formmaß (Δ Regler × Wirkung → mittlere Verschiebung der Körperpunkte + 0,01 × Δ², Abschnitt 3)'),
        ('Ausgabe', 'bis 16.10.2026 morgens 414 freie Zahlen (138 Punkte × 3); dann Daz-Winkel in ihren Grenzen; seit dem Nachmittag Stimmen je Punkt und danach die Anpassung der Daz-Winkel '
         '(Abschnitt 5); seit dem Abend dazu 815 Formregler'),
        ('Optimierer', 'AdamW, Lernrate 0,001, Gewichtszerfall 0,0001; Lernratenplan OneCycle bis 0,002, 10 % Anlauf'),
        ('Epochen · Batch', 'Formlauf 200 Epochen · 8 Proben je Schritt — bei 620 Trainingsproben 77 Schritte je Epoche, 15.400 zusammen'),
        ('Schritte', 'Epochen × (Trainingsproben ÷ 8, abgerundet — der Rest fällt je Epoche weg, wechselnd). Bis 16.10.2026 rechnete der Lernratenplan mit aufgerundeten Schritten (siehe Befunde)'),
        ('Rechengenauigkeit', 'bfloat16 (autocast) auf der GPU, Gradienten auf Norm 5 begrenzt'),
        ('Augmentierung', 'je Schritt neu: Drehung um die Hochachse ±5°, Versatz ±2 cm (x, z) und ±1 cm (y), Farbrauschen σ 0,02; dazu Drehung bis ±30° um eine zufällige Achse durch (0; 0,85; 0) '
         'und eine Zufallsfarbe je Teil (ein Fünftel der Proben ganz grau, Rauschen σ 0,04); je Schritt eine neue Auswahl von 4.096 der 16.384 Punkte'),
        ('Auswertung', 'ohne Augmentierung (also mit den flachen Teilfarben des Datensatzes), vier feste Punktauswahlen gemittelt; im Lauf alle 20 Epochen mit einer Auswahl'),
        ('Ausgangspunkt', 'Stimme = Punkt + 0,1 × Versatz (ein frisches Netz stimmt jedes Ziel auf die Punkte selbst); Formkopf: letzte Schicht × 0,1, Verschiebung 0 — er startet bei der Grundfigur'),
    )

    #: Zeiten je Probe, gemessen. (Schritt, Was, Dauer, Quelle)
    SCHRITTE = (
        ('Plan', '176 Posen festlegen, `proben.json` schreiben, veraltete Ordner beiseitelegen (nichts gelöscht)', '4 s für alle', 'neu_haar.log, 15.10.2026'),
        ('Retarget', 'BVH-Datei → Genesis 9 auf der Stellung von Ursula1 (`Retargetdaten`, derselbe Weg wie Studio und Mesh-3D)',
         '0,01 s aus der Ablage neben der Datei; ohne Ablage 0,7 s je Bewegungsdatei', 'mesh3dai_probe_zeiten.py 16.10.2026; mesh3dai.md 14.10.2026'),
        ('Weltmatrizen', '138 Knochen im Bild der Bewegung (`G9tanzhaut.matrizen`)', '0,003–0,006 s', 'mesh3dai_probe_zeiten.py, 16.10.2026'),
        ('Häuten', '411.420 Punkte aller Teile, lineare Hautmischung (4 Knochen je Punkt), keine Gelenkkorrekturen (JCM), kein Stoff; dann ausrichten: Blick +Z, Hüfte in die Mitte, Füße auf den Boden',
         '0,17–0,19 s', 'mesh3dai_probe_zeiten.py, 16.10.2026'),
        ('Sichtbarkeit', 'Außenfläche bestimmen: jedes der 446.852 Dreiecke in Kennfarbe, 26 Richtungen (Ecken, Kanten, Flächen eines Würfels), orthografisch 2.048 × 2.048 px, '
         'pyrender auf der GPU ohne Kantenglättung; Dreiecke unter 4 px über die Tiefe (Toleranz 0,5 mm + Neigung)',
         '7,3–8,6 s (0,28–0,33 s je Ansicht) — 94–96 % der Zeit einer Probe', 'mesh3dai_probe_zeiten.py, 16.10.2026'),
        ('Abtasten', '16.384 Punkte auf den sichtbaren Dreiecken, nach Fläche gewichtet: Lage, Normale, Teilfarbe, Teil', '0,09 s', 'mesh3dai_probe_zeiten.py, 16.10.2026'),
        ('Schreiben', '`soll.npz` (138 Rig-Punkte), `eingabe.npz` (zuletzt — ihr Vorhandensein heißt „fertig"), für die 50 Proben der Seite `eingabe.glb`', 'nicht einzeln gemessen', ''),
        ('Datensatz gesamt', '176 Proben mit 5 Arbeitern nebeneinander (niedrige Priorität, eine GPU): je Probe und Arbeiter 12,9–20,0 s', '553 s (3,1 s je Probe Wandzeit)', 'neu_haar.log, lauf_0.log, 15.10.2026'),
        ('Anzeigeflächen', '`flaeche.npz` je Probe NUR für die Seite (das Training liest sie nicht). Bis 15.10. rechnete das die Sichtbarkeit ein zweites Mal; seit 16.10. übernimmt es sie aus `sicht.npz`',
         'vorher 521 s für 176 (14–17,8 s je Probe und Arbeiter) · jetzt 8 s für 54 neue Proben', 'neu_haar.log 15.10.; posen50.log 16.10.2026'),
        ('Datensatz 50 Posen (16.10.)', '54 neue Proben (49 Training + 5 Prüfposen) mit 5 Arbeitern; A-Pose, alte Prüfposen und Spagat-Bilder lagen schon vor',
         '155 s (2,9 s je Probe Wandzeit; 11,4–16,4 s je Probe und Arbeiter)', 'posen50.log, lauf_0.log, 16.10.2026'),
        ('Training', '120 Epochen, 2.040 Schritte auf der GPU', '77 s (0,64 s je Epoche, ≈ 38 ms je Schritt einschließlich der Zwischenprüfungen) + 8 s Start', 'lauf.log 2026.10.15.11.59_dgcnn'),
        ('Kette gesamt', 'Plan → Datensatz → Anzeigeflächen → GPU-Sperre → Training', '1.163 s', 'neu_haar.log, 15.10.2026'),
    )

    #: Befunde unterwegs (Datum, Befund, Stand).
    BEFUNDE = (
        ('15.10.', 'pyrender rechnet die Tiefe auch bei der orthografischen Kamera mit der perspektivischen Formel um (1,6–1,9 m daneben); dazu mischte die 4-fache Kantenglättung die Kennfarben — '
         'die Außenfläche hatte Löcher (Gesichtshaut vorn 11,1 % statt 85,7 %).', 'behoben: Sichtbarkeit Fassung 2'),
        ('15.10.', 'Das Strähnenhaar war auf 25 % ausgedünnt — der Start zeigte Kopfhaut zwischen den Strähnen.', 'behoben: Fassung 3, alles Haar'),
        ('15.10.', 'Der Neubau schob `flaeche.npz` beiseite — 10 Minuten lang zeigte die Seite nur Punktwolken, die Ansichtsknöpfe wirkten nicht.', 'behoben: alte Fläche bleibt, Ersatz in einem Zug'),
        ('16.10.', 'Die Sichtbarkeit wurde je Probe ZWEIMAL gerechnet (Datensatz und Anzeigeflächen): 553 + 521 s.', 'behoben: `sicht.npz`, Anzeigeflächen 8 s für 54 Proben'),
        ('16.10.', 'Der Lernratenplan rechnete mit aufgerundeten Schritten (141 Proben: 2.160 statt 2.040, 50 Proben: 840 statt 720) — die Lernrate endete nicht am Minimum '
         '(≈ 2·10⁻⁵ bzw. ≈ 1,2·10⁻⁴). Alle Läufe vor `posen50_plan_*` haben den Fehler.', 'behoben im Trainingsskript'),
        ('16.10.', 'Beide Hände zusammen bekommen 3–7 % der Punkte (Spagat Bild 47: 507 von 16.384, Stehpose: 1.091) — das Netz sieht davon ein Viertel, also rund 130–270 Punkte für 42 Rig-Punkte.',
         'gemessen, mesh3dai_probe_zeiten.py'),
        ('16.10.', 'Auf nie trainierten Posen folgt der Fehler des Netzes dem Abstand zur nächsten Trainingspose (Korrelation 0,99, Lauf 2026.10.15.11.59 mit 141 Posen) — das Netz holt im Kern '
         'die ähnlichste gesehene Pose.', 'gemessen, mesh3dai_naechste_trainingspose.py'),
        ('16.10.', 'Mit 50 sehr verschiedenen Posen (Sitzen, Liegen, kopfüber) lernt dasselbe Netz nicht einmal das Training: 141 mm nach 120 Epochen (mit berichtigtem Lernratenplan 141,7), 74,7 mm nach '
         '480 Epochen (121 s); die Prüfposen bleiben bei 170 mm. Die Ausrichtung ist dabei überall eindeutig (Hüftlinie waagerecht, Median 143 von 144 mm). Grundprobe OHNE Augmentierung, 480 Epochen: '
         'Training 58,8 mm, Verlust im Trainingsmodus aber 212 mm — Vermutung (nicht gemessen): BatchNorm bei Batch 8 und Dropout stören das Lernen bei so verschiedenen Posen.',
         'gemessen, posen50_gegenlauf.log, posen50_grundprobe.log (Lauf unter `_diagnose/`)'),
        ('16.10.', 'Auf denselben 10 alten Prüfposen: 165,7 mm (141 Posen, 15.10.) gegen 144 / 156 / 150 mm (50 Posen, drei Läufe). Bodenposen viel besser (Walk Bild 577: 638 → 203–223 mm), '
         'Stehposen schlechter (Walk 01_01: 70 → 140–158 mm) — im neuen Training stehen nur 6 Stehposen.', 'gemessen, mesh3dai_pruefposen_einzeln.py'),
        ('16.10.', 'Edgar: „wie kannst du mit Genesis-Reglern so kaputte Finger kriegen?" — das Netz gab freie Punkte aus, das Ergebnisfeld häutete eine Näherung ohne Knochenlängen und Grenzen. '
         'Jetzt Daz-Winkel in den Grenzen + Vorwärtskinematik; dabei gefunden: schon die Zielposen aus dem Retarget verletzen die Daz-Grenzen (Abschnitt 5).',
         'gebaut: `--ausgabe kanaele`, Ergebnisfeld genau gehäutet; Retarget offen'),
        ('16.10.', 'Zwei Abkürzungen des Netzes (Lauf `stimmen_alle4`, Gelenke Training / Prüfposen in mm): original 11,0 / 64,3 · grau 82,6 / 117,6 · Teilfarben vertauscht 208,8 / 230,0 · '
         'Zufallsfarbe je Punkt 268,9 / 235,1 · 90° gedreht 244,5 / 207,1 · 180° 378,5 / 319,7. Es las die Teile an ihrer flachen Farbe ab und kannte nur Figuren, die zur Kamera schauen — Testnetze tragen echte Texturen.',
         'gemessen, mesh3dai_farbe_dreh_pruefen.py'),
        ('16.10.', 'Gegenlauf mit Zufallsfarben und Drehung bis ±180° um die Hochachse (240 Epochen, 541 s): alle Varianten gleichauf (Training 82,7–93,7, Prüfposen 162,8–177,2 mm) — die Abkürzungen sind weg, '
         'das Netz insgesamt viel schlechter; der Verlust fiel bis zum Ende. Vermutung: zu wenig Schritte für „jede Richtung“. Der Formlauf trainiert deshalb Zufallsfarben, aber nur ±30°.',
         'gemessen, Lauf `_diagnose/…15.13_stimmen_alle4_farbe_gieren`, ein Lauf, eine Saat'),
        ('16.10.', 'Ursula1 setzt drei Regler, die nicht im Katalog stehen (`facs_ctrl_EyeRestingFocalPoint`, `body_ctrl_BreastsHangForward`, `CTRLBreastsIn-Out`) — sie fallen aus dem Soll der Form.',
         'gemeldet im Lauf (`fremde_regler`)'),
        ('16.10.', 'Formkopf im Formlauf (lineare Näherung, mm, Training / Prüfung): Epoche 20 49,3 / 64,3 · 40 46,3 / 59,6 · 60 42,1 / 56,9 · 80 47,4 / 63,6 · 100 35,0 / 50,4 — bis Epoche 80 auf der Höhe '
         'der „mittleren Form“ (50,0 / 63,8, auf der CPU nachgerechnet), danach darunter. Endstand: Abschnitt 3.', 'gemessen, lauf.log des Formlaufs, mesh3dai_form_basis.py'),
    )

    @staticmethod
    def posen(ordner):
        """Woher die Posen kommen: je Ordner der BVH-Dateien Zahl der Dateien und der Proben je Gruppe."""
        import json
        liste = json.loads((ordner / 'proben.json').read_text(encoding='utf-8'))
        tabelle = {}
        for e in liste:
            herkunft = Path(e['bvh']).parent.name if e.get('bvh') else 'Ruhelage'
            z = tabelle.setdefault(herkunft, {'herkunft': herkunft, 'dateien': set(), 'training': 0, 'pruefung': 0, 'spagat': 0, 'beispiel': e['name']})
            if e.get('bvh'):
                z['dateien'].add(Path(e['bvh']).name)
            z[e['gruppe']] = z.get(e['gruppe'], 0) + 1
        zeilen = [dict(z, dateien=len(z['dateien'])) for z in tabelle.values()]
        return {'zeilen': zeilen, 'gesamt': len(liste), 'je_gruppe': {g: sum(z[g] for z in zeilen) for g in ('training', 'pruefung', 'spagat')}}

    @staticmethod
    def lauf(lauf_ordner, ergebnis):
        """Maße je Gruppe und der Verlauf aus `lauf_ergebnis.json`."""
        if not ergebnis:
            return None
        masse = ergebnis.get('maße') or {}
        namen = {'training': 'Training', 'pruefung': 'Prüfposen (nie trainiert)', 'spagat': 'Spagat-Bilder 101–125 (nie trainiert)'}
        gruppen = [dict(m, name=namen.get(g, g), proben=(ergebnis.get('proben') or {}).get(g)) for g, m in masse.items()]
        return {'name': lauf_ordner.name, 'epochen': ergebnis.get('epochen'), 'dauer_s': ergebnis.get('dauer_s'), 'parameter': ergebnis.get('parameter'),
                'punkte': ergebnis.get('punkte_je_probe'), 'sicht': ergebnis.get('sicht_fassung'), 'gruppen': gruppen,
                'verlauf': [v for v in ergebnis.get('verlauf') or [] if 'pruefung_mm' in v or v.get('epoche', 0) <= 3]}

    @staticmethod
    def analyse(daten):
        """Netz gegen nächste Trainingspose je Gruppe (Korrelation über die Proben) und die Prüfposen einzeln; `daten` = `Mesh3daidaten.proben(job)`."""
        if not daten:
            return None
        gruppen = []
        for g, name in (('training', 'Training (nächste ANDERE Trainingspose)'), ('pruefung', 'Prüfposen'), ('spagat', 'Spagat-Bilder 101–125')):
            p = [x for x in daten['proben'] if x['gruppe'] == g and x['kennzahlen'].get('naechste_pose_mm') is not None]
            if not p:
                continue
            netz = np.array([x['kennzahlen']['mittel_mm'] for x in p])
            nn = np.array([x['kennzahlen']['naechste_pose_mm'] for x in p])
            r = float(np.corrcoef(netz, nn)[0, 1]) if len(p) > 2 else None
            gruppen.append({'name': name, 'proben': len(p), 'netz': round(float(netz.mean()), 1), 'naechste': round(float(nn.mean()), 1),
                            'mittlere': round(float(np.mean([x['kennzahlen'].get('mittlere_pose_mm', np.nan) for x in p])), 1),
                            'korrelation': None if r is None else round(r, 2), 'besser': int((netz < nn).sum())})
        pruef = sorted(({'nr': x['id'], 'name': x['name'], 'netz': x['kennzahlen']['mittel_mm'], 'naechste': x['kennzahlen'].get('naechste_pose_mm'),
                         'naechste_nr': x['kennzahlen'].get('naechste_pose_nr'), 'mittlere': x['kennzahlen'].get('mittlere_pose_mm')}
                        for x in daten['proben'] if x['gruppe'] == 'pruefung'), key=lambda z: -(z['naechste'] or 0))
        namen = {x['id']: x['name'] for x in daten['proben']}
        for z in pruef:
            z['naechste_name'] = namen.get(z['naechste_nr'], '')
        return {'gruppen': gruppen, 'pruefposen': pruef, 'lauf': daten['lauf']['name']}
