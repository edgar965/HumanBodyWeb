# -*- coding: utf-8 -*-
"""Architekturai2d3dstand — der gebaute Stand der Foto-Kette am Beispiel EdgarTrip: Einpassung und Prüfung über das Rendering, gelesen aus den Ergebnisdateien der Läufe, dazu die
Änderungen eines Tages (24.10.2026, für Hilfe → Architektur → 2d-3d-AI; Edgar: „die Änderungen von heute sind nicht drin“).

Gelesen wird beim Aufruf aus `ProjektTemp/_wegwerf/ai2d3d/kopf/`: `nurfotos_einpassen.json` (Größe, Volumen, Deckung, Kameras) und je gemessenem Stand `koerperpruefung_<stand>.json`
(`koerperpruefung_lauf.py`: Deckung Foto ↔ Rendering je Gruppe, Gelenke in mm). Fehlt eine Datei, fehlt die Zeile — keine Zahl von Hand.
"""
import json
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturai2d3dstand']


class Architekturai2d3dstand:
    #: (Stand, Was gemessen wurde) — in der Reihenfolge des Tages
    STAENDE = (('lauf6_katalog', 'Kleider als Katalogstücke (Mesh3D-AI Weg a), 18:27 — wieder verworfen'),
               ('lauf6_schalen', 'Kleider ausgeschnitten, Fotoschale Fassung 1 (18:35)'),
               ('lauf6_schalen2', 'Fassung 2: Bereich je Stück, Höhe nur am Umriss, Fahnen weg (18:46)'),
               ('lauf6_schalen3', 'dazu: Kostüm-Kennzeichen (Stofftiefe), Haut unter Stoff weg, Kragen ohne Hals'),
               ('lauf6_schalen4', 'Fassung 3: Höhe gegen den Umriss des Stücks statt der ganzen Person'),
               ('lauf6_schalen5', 'Fassung 4: höchste Stoffdicke je Art (Setzung: Shirt 3 cm, Hose 1,5 cm, Socken 8 mm)'),
               ('lauf6_gewichte', 'Hautgewichte der Stücke als 0…255 abgelegt — vorher 0…1, beim Ablegen auf 0 abgeschnitten: die Stücke standen in der Ruhelage'),
               ('lauf6_seite', 'gemessen auf dem Rendering DER JOBSEITE (Ai2d3dseitenbild) statt dem eigenen Python-Renderer — derselbe Stand wie die Zeile davor'),
               ('lauf6_seite2', 'Jobseite: Haut unter den Stücken weg (Testfigur ohne Verdeckungsmaske gebaut), Fotoschale Fassung 5 (Stoff mindestens 6 mm über der Haut)'),
               ('lauf6_messpunkte', 'derselbe Stand, gemessen MIT der Form: 40 Randpunkte des Umrisses je Foto (Koerpermesspunkte) — 48 der Abweichungen sind Form, die vorher keine Messung sah'),
               ('lauf7_formziele', 'Randpunkte als Ziel der Einpassung (Term rand, Stoffkorridor), Runde gilt nur, wenn der Formrest sinkt — Formrest 30,3 → 7,1 mm, aber der Kopf 3,8 % zu schmal'),
               ('lauf8_kopfbild', 'dazu 400 Kopfpunkte der KopfKI als Ziel (Term kopfbild) und Kopftor 5 mm — Kopf wieder wie lauf6, Formrest 8,9 mm'),
               ('form1_nachfuehren', '25.10.: Maße aus den Fotos (Term masse), eine Haltung (vier Läufe Haltung je Foto: 10,7–11,8 mm), jede Runde erst nach Nachführen der Haltung an der '
                                     'gebauten Figur geprüft — Formrest 7,9 mm, Kopfmitte 1,1–1,5 mm'),
               ('form2_dichte', '25.10.: Volumen als Korridor der Dichtegrenze 1.000–1.070 kg/m³ statt Ziel bei 1.000 (Form 1 lag bei 999 und war an allen Maßlinien breiter) — '
                                'Formrest 6,66 mm, Kopfmitte ≤ 2,6 mm, 1.053 kg/m³; Abnahmetabelle 42 grün / 59 rot'),
               ('form3_stufeb_jefoto', '25.10.: Haltung je Foto nur in Stufe B, an der fertigen Figur (Start = gemeinsame Haltung, Wirbelsäule frei) — Formrest 6,66 → 6,25 mm, '
                                       'Deckung 0,870 → 0,884, Kopfmitte ≤ 1,6 mm; Abnahmetabelle 47 grün / 53 rot'),
               ('kleider1_saum', '25.10.: Kleider-Etikett je Knochen mit einem Saum statt je Punkt — 45 grün / 54 rot, Kragen 3.jpg +46 mm (verworfen)'),
               ('kleider2_hintergrund', '25.10.: Kleider-Etikett nur aus Fotos, in denen der Punkt auf der Person landet (Hintergrund ist kein Gegenbeleg) — Socken 1.654 → 2.642 cm², '
                                        'im Rückenbild ohne hautfarbene Flecken; 48 grün / 52 rot'),
               ('haar1_person', '25.10.: dieselbe Regel für das Haar — Hinterkopf blieb kahl, Haar am Hals in den Profilen +7 mm schlechter (verworfen)'),
               ('haut1_dicke', '25.10.: Stoffdicke im Korridor des Auftrags (Hose ≤ 8, Socken ≤ 4 mm statt 15/8; Mindestdicke je Art höchstens die Obergrenze) — Socken 4/4 mm ohne '
                               'durchstechende Haut, 48 grün / 52 rot, 208 Abweichungen'),
               ('farbe1_fotobalance', '25.10.: neues Messwerk Farbe (Farbregionen: ΔE76 der Medianfarben je Region × Foto, Grenze 5, Gegenprobe Oberteil +25 → rot); Körperhaut in der Farbe '
                                      'der Fotos (die KI wird angeglichen, nicht die Fotos: Faktor KI ÷ Foto R/G/B 0,90/1,07/1,40) — Farbe 46/50 → 70 grün / 26 rot, Umriss 48/52'),
               ('hals1_regler', '25.10., zweite Runde: 21 Halsregler frei (fielen durch das RMS-Sieb `wirkung_mm` ≥ 5) — Hals besser, aber Umriss 38 grün / 64 rot, Kopfmitte bis 3,0 mm; '
                                'Formrest der Einpassung 5,75 mm (verworfen, Stand farbe1 wiederhergestellt)'),
               ('hals2_deckung', '25.10.: dazu das Tor „Deckung darf nicht fallen“ (lehnte Runde 2 ab) — Kopf ≤ 1,4 mm, aber Hals auf der Seite unverändert, Umriss 44 grün / 57 rot '
                                 '(verworfen; das Tor bleibt)'),
               ('schenkel1_regler', '25.10.: 19 Oberschenkelregler frei (`Ortsregler`, gesperrt durch das RMS-Sieb) — Maß „Oberschenkel Mitte“ nur 163,1 → 159,8 mm bei Soll 142,3; '
                                    'Lauf abgebrochen (Testordner gelöscht), verworfen'),
               ('farbe1_wieder3', '25.10.: Stand Farbe 1, Figur jetzt im Jobordner `figur/` mit eigener Schnittstelle `/api/2d3dai/<job>/figur/` (Edgar: „das ist doch eine andere '
                                  'Pipeline“) — Seitenbilder deckungsgleich mit farbe1_wieder2'))
    GRUPPEN = ('person', 'oberteil', 'hose', 'fuesse', 'haut', 'haar')
    #: Änderungen am 24.10.2026 (Edgars Aufträge in Anführungszeichen; Messwerte mit Quelle in den Regeln `ai2d3d.md` und im Code)
    HEUTE = (
        ('Körpergröße je Job', '„körpergröße kann ich angeben im Job oben“, „pro Job fest“ — Feld auf der Testseite, job.json `koerpergroesse_m`; Term `hoehe` der Einpassung.'),
        ('Perspektive', '„mach B“ — Lochkamera je Foto, Brennweite aus EXIF/XMP; die orthografische Einpassung hatte die Figur auf 1,435 m geschrumpft.'),
        ('Drehung der Profile', 'der Körperweg drehte die Kamera andersherum als die KopfKI — Profile seitenverkehrt; Test an die Kopfdrehung gebunden.'),
        ('Gewicht', '„ca. 86 kg“ — job.json `koerpergewicht_kg`, Term `volumen` (Dichte 1.000 kg/m³ als Setzung); dazu Term `kopfform`, der den Kopf der KopfKI festhält.'),
        ('Knopf „Rig“', 'die Knochen der Figur in Feld 2 ein- und ausblenden.'),
        ('Kopf im Körperweg', 'Haar mit dem Kopf versetzt (saß 14 cm zu tief), Kopfkachel aus der Haut-KI nur mit dem Kopf (wich 29 sRGB-Stufen ab).'),
        ('Körperhaut aus den Fotos', '„warum kannst du nicht dieselbe Logik anwenden wie bei meinem Kopf?“ — jeder gesehene Hauttexel aus dem Foto (Koerperhautbild), die KI nur, wo kein Foto Haut sieht.'),
        ('Messung über das Rendering', '„Warum wendest du das verfahren vom Kopf nicht an?“ — Koerperbild + Koerperpruefung: dieselben Detektoren auf Foto und Rendering.'),
        ('Kleider', 'ausgeschnitten wie der Kostüm-Weg von Mesh3D-AI („nicht mehr mit Katalogstücken“); Fehler gesucht und in Fassungen gemessen (Tabelle oben).'),
        ('Karte „Foto Vorlage - Ergebnis“', 'je Foto eine Zeile, links Vorlage, rechts Ergebnis — erst die Körper (gleiche Höhe), dann die Köpfe.'),
        ('Stift', 'Name eines Tests auf seiner Seite ändern, wie bei Mesh3D-AI (name.json im Testordner).'),
        ('Abnahme über das Rendering', '„Passe deine testmethoden an, das musst du doch selber herausfinden, dass die nicht übereinstimmen“ — statt einer Deckungszahl je Gruppe jede '
                                       'Abweichung als Fleck mit Fläche, Tiefe und Ort (Koerperabweichung), alle 133 ViTPose-Punkte mit Versatz und Maßstab (Punktabweichung), Grenzen '
                                       '(Koerperabnahme) und ein Fehlerbild je Foto; Gegenprobe in jedem Lauf: Foto gegen Foto besteht, um 3 cm verschoben fällt es durch.'),
        ('Hautgewichte der Stücke', 'die Abnahme zeigte Shirt und Hose 12 cm zu hoch; Ursache: die Gewichte gingen als 0…1 in eine uint8-Ablage und wurden bei 99 % der Punkte 0 — '
                                    'die Stücke folgten der Haltung nicht (daher auch Socken-Fetzen und der Stab an der Uhr).'),
        ('Abnahme misst die Jobseite', 'die Seite rendert die Figur aus der Kamera jedes Fotos (window.__ai2d3d.seitenbilder(), Ai2d3dseitenbild → <Job>/abnahme/seite_<n>.png), '
                                       'koerperpruefung_lauf.py --seite misst diese Bilder. Der eigene Python-Renderer zeigte weder das Anatomie-Stück noch das Licht der Seite.'),
        ('Haut unter Stoff auf der Jobseite', 'Ai2d3dtestfigur baute den Körper ohne die Verdeckungsmasken der Stücke (alle 64.632 Dreiecke) — jetzt wie die Mesh3D-AI-Testseite.'),
        ('Messpunkte des Körpers', '„warum erkennst du nicht die Formunterschiede … Erkläre mir, was du misst“ — die Abnahme hatte kein Maß für die Form (Gelenke liegen bei schlankem und rundem '
                                   'Körper gleich, Umriss-Streifen blieben unter der Fleckgrenze 20 mm). Neu: 23 ViTPose-Punkte + 40 Randpunkte an 20 Linien quer zu Hals, Rumpf, Armen, Beinen '
                                   '(Koerpermesspunkte), Grenze 10 mm je Rand, Gegenprobe Umriss 12 mm schmaler; Testzeile auf der Jobseite unter den drei Ansichten (Ai2d3dmesspunkte).'),
        ('Messpunkte in der Pipeline', '„fixe!“ — „mach das in die Pipeline hinein“: die Randpunkte sind Ziel der Einpassung (Term rand), eine Runde gilt nur mit sinkendem Formrest; '
                                       'Fotolicht auf der Seite, kein Anatomie-Stück unter der Hose, Rückenhaar aus allen vier Fotos, Kette nurfotos_kette.py.'),
        ('Kopf festgehalten', '„der kopf war gut, bitte diesen nicht kaputt machen, jetzt ist er viel enger“ — der Term rand hatte den Bildmaßstab um 3,8 % gesenkt; jetzt halten 400 '
                              'Kopfpunkte der KopfKI Lage und Größe (Term kopfbild), eine Runde mit Kopfmitte über 5 mm gilt nicht.'),
        ('Maße aus den Fotos', '„am anfang die bilder auswerten, maße berechnen, so wie du das mit dem Kopf gemacht hast“ — Fotomasse: Breite (vorn/hinten) und Tiefe (Profile) an 20 Linien, '
                               'Mittel über die Fotos, Kleider (Farbe, Säume, Stoffzugabe am Saum) und Haare; Modellmasse: dieselben Maße am Querschnitt der Figur in Ruhe, Term masse.'),
        ('Abnahmetabelle Region × Foto', 'Auftrag EdgarTrip: jeder Randpixel mit Vorzeichen je Region und Art (Haut, Stoff, Haar), Grenzen Haut 5/15 mm, Stoff 8 mm, Haar 5 mm; '
                                         'Gegenprobe Kamera 3 % kleiner → Kopf rot, Unterarm 2 cm versetzt → Arm rot, an allen vier Fotos bestanden.'),
    )

    @staticmethod
    def ordner():
        return Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'ai2d3d' / 'kopf'

    @classmethod
    def _lesen(cls, name):
        datei = cls.ordner() / name
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def einpassung(cls):
        e = cls._lesen('nurfotos_einpassen.json')
        if not e:
            return None
        deckung = [m['deckung'] for m in (e.get('nachher') or {}).values()]
        return {'gerechnet': e.get('gerechnet'), 'soll_m': e.get('koerpergroesse_soll_m'), 'gewicht_kg': e.get('koerpergewicht_kg'), 'volumen_soll': e.get('volumen_soll_m3'),
                'figur': e.get('figur_nachher'), 'gueltig': e.get('gueltig'), 'deckung': round(sum(deckung) / len(deckung), 3) if deckung else None,
                'kameras': e.get('kameras_nachher') or {}, 'runden': [(r['runde'], r['deckung_mittel'], r['figur'], r['uebernommen']) for r in e.get('runden', [])]}

    @classmethod
    def pruefungen(cls):
        aus = []
        for stand, text in cls.STAENDE:
            p = cls._lesen('koerperpruefung_%s.json' % stand)
            if p and p.get('mittel'):
                aus.append({'stand': stand, 'text': text, 'gerechnet': p.get('gerechnet'), 'deckung': [p['mittel']['deckung'].get(g) for g in cls.GRUPPEN],
                            'gelenke_mm': p['mittel'].get('gelenke_mm_median'), 'abnahme': cls._abnahme(p)})
        return aus

    @staticmethod
    def _abnahme(p):
        """Zahl der Abweichungen über den Grenzen (`Koerperabnahme`, seit 24.10.2026 abends); ältere Stände haben keine."""
        a = p.get('abnahme')
        return {'fehler': len(a['fehler']), 'anzahl': a['anzahl'], 'erste': [f['text'] for f in a['fehler'][:5]]} if a else None
