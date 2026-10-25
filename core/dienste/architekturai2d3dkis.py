# -*- coding: utf-8 -*-
"""Architekturai2d3dkis — die KIs der Foto-Kette von 2d-3d-AI, je eine Grafik (`Architekturai2d3dnetzbild`), für Hilfe → Architektur → 2d-3d-AI (24.10.2026).

Edgar: „Mach die KopfKI, Haut KI rein, für alle KIs eine einzelne Grafik wie diese: Neuronale Netz - Figur“. Die Gewichte je Teil stehen in `architekturai2d3dnetze.json`, gelesen aus den
Gewichtsdateien selbst (`ProjektTemp/_wegwerf/ai2d3d/netze_vermessen.py`: .safetensors-Kopf, .pt mit mmap, .tflite über `MediapipeTorch.tflite`); Breiten und Blockzahlen aus den Formen
dort und aus den Ports (Datei und Zeile im Text). Fehlt die Datei, gibt es keine Grafik und einen Befund — keine Zahl von Hand.
"""
import json
from pathlib import Path

from .architekturai2d3dnetzbild import Architekturai2d3dnetzbild

__all__ = ['Architekturai2d3dkis']


class Architekturai2d3dkis:
    DATEI = Path(__file__).with_name('architekturai2d3dnetze.json')

    @classmethod
    def lesen(cls):
        return json.loads(cls.DATEI.read_text(encoding='utf-8'))

    @staticmethod
    def _summe(netz, *praefixe):
        return sum(v['gewichte'] for g, v in netz['gruppen'].items() if g.startswith(praefixe))

    @staticmethod
    def _de(n):
        return f'{int(n):,}'.replace(',', '.')

    @classmethod
    def kontext(cls):
        daten = cls.lesen()
        netze = {n['name']: n for n in daten['netze']}
        aus = [cls._sapiens(netze['Sapiens2 0.4B Segmentierung']), cls._sam(netze['SAM 3']), cls._vitpose(netze['ViTPose-H WholeBody']),
               cls._mediapipe(netze['MediaPipe face_detector.tflite'], netze['MediaPipe face_landmarks_detector.tflite']), cls._haut(netze['Haut-KI (Mesh3D-AI Stufe 2)'])]
        for k in aus:
            k['svg'] = Architekturai2d3dnetzbild.svg(k['kennung'], k['titel'], k['untertitel'], k['spalten'], k['fuss'])
        return {'kis': aus, 'gemessen': daten['gemessen'], 'skript': daten['skript']}

    @classmethod
    def _sapiens(cls, n):
        s = lambda *p: cls._summe(n, *p)  # noqa: E731
        return {'kennung': 'ki-sapiens', 'titel': 'Sapiens2 0.4B — Körperteile und Kleider je Pixel (29 Klassen)',
                'untertitel': 'Ein Foto auf dem Weg durch das Netz; die große Zahl: so viele Zahlen trägt ein Feld bzw. Pixel nach der Schicht. Violett: vortrainiert (Meta), hier nicht trainiert.',
                'wo': 'KopfKI.Fotosegmente — jedes Foto und jedes Rendering (Kopf: Haut, Haar, Bart; Körper: Umriss, Haut, Kleider; Prüfung: dieselben Gruppen auf Foto und Rendering)',
                'spalten': [
                    {'art': 'eingabe', 'titel': 'Foto', 'zahl': 3, 'wort': 'Zahlen je Pixel', 'kreise': ('R', 'G', 'B', ''), 'zeilen': ['1.024 × 768 Pixel']},
                    {'art': 'versteckt', 'titel': 'Felder', 'zahl': 1024, 'wort': 'Zahlen je Feld', 'zeilen': ['16 × 16 Pixel je Feld', '64 × 48 = 3.072 Felder', '+ 1 + 8 Merktokens'],
                     'gewichte': s('backbone.patch_embed', 'backbone.cls_token', 'backbone.storage_tokens', 'backbone.rope_embed')},
                    {'art': 'rueckgrat', 'titel': 'Blöcke 1–24', 'zahl': 1024, 'wort': 'Zahlen je Feld', 'zeilen': ['Transformer', 'Aufmerksamkeit über', 'alle Felder (64 je Kopf)'],
                     'gewichte': s('backbone.blocks', 'backbone.ln1')},
                    {'art': 'versteckt', 'titel': 'Kopf', 'zahl': 64, 'wort': 'Zahlen je Pixel', 'zeilen': ['4 Entfaltungen ×2', '1.024→512→256→128→64', '64 × 48 → 1.024 × 768'],
                     'gewichte': s('decode_head.deconv', 'decode_head.conv_layers')},
                    {'art': 'ausgabe', 'titel': 'Klassen', 'zahl': 29, 'wort': 'Werte je Pixel', 'zeilen': ['Haut je Körperteil,', 'Haar, Upper/Lower', 'Clothing, Socke, Schuh'],
                     'gewichte': s('decode_head.conv_seg')},
                    {'art': 'danach', 'titel': 'Fotosegmente', 'zeilen': ['Masken je Foto:', 'Person, Haut, Haar,', 'Kleider je Klasse;', 'Bart, Ohr: SAM 3']}],
                'fuss': ['Summe %s Gewichte (sapiens2_0.4b_seg.safetensors, gelesen)' % cls._de(n['gewichte']),
                         'Port Sapiens2Torch (python14, auf der Karte): an allen vier EdgarTrip-Fotos 100 % gleiche Etiketten wie das Original (24.10.2026)']}

    @classmethod
    def _sam(cls, n):
        s = lambda *p: cls._summe(n, *p)  # noqa: E731
        benutzt = s('detector.')
        return {'kennung': 'ki-sam3', 'titel': 'SAM 3 — Maske zu einem Wort („beard“, „moustache“, „hair“, „ear“)',
                'untertitel': 'Bild und Wort laufen getrennt durch zwei vortrainierte Rümpfe (Meta) und treffen sich in der Fusion; je Anfrage eine Maske.',
                'wo': 'KopfKI.Fotosegmente (Bart, Schnurrbart, Haar, Ohren) und KopfKI.Kopfohren (Ohr auf Foto UND Rendering)',
                'spalten': [
                    {'art': 'eingabe', 'titel': 'Foto + Wort', 'zahl': 3, 'wort': 'Zahlen je Pixel', 'kreise': ('R', 'G', 'B', ''), 'zeilen': ['1.008 × 1.008 Pixel', 'Wort, z. B. „ear“']},
                    {'art': 'rueckgrat', 'titel': 'Bild-ViT', 'zahl': 1024, 'wort': 'Zahlen je Feld', 'zeilen': ['14 × 14 Pixel je Feld', '72 × 72 = 5.184 Felder', '32 Blöcke'],
                     'gewichte': s('detector.backbone.vision_backbone.trunk')},
                    {'art': 'versteckt', 'titel': 'Hals', 'zahl': 256, 'wort': 'Zahlen je Feld', 'zeilen': ['4 Maßstäbe', '×4 ×2 ×1 ×½'], 'gewichte': s('detector.backbone.vision_backbone.convs')},
                    {'art': 'rueckgrat', 'titel': 'Text', 'zahl': 1024, 'wort': 'Zahlen je Wortteil', 'zeilen': ['24 Schichten', 'auf 256 verkleinert'],
                     'gewichte': s('detector.backbone.language_backbone')},
                    {'art': 'versteckt', 'titel': 'Fusion', 'zahl': 256, 'wort': 'Zahlen je Anfrage', 'zeilen': ['Encoder 6 Schichten', 'Decoder 6 Schichten', '200 Anfragen'],
                     'gewichte': s('detector.transformer', 'detector.geometry_encoder', 'detector.dot_prod_scoring')},
                    {'art': 'ausgabe', 'titel': 'Masken', 'zahl': 200, 'wort': 'Anfragen', 'zeilen': ['je Anfrage Maske', 'und Wert', 'Pixel-Decoder 256'],
                     'gewichte': s('detector.segmentation_head')},
                    {'art': 'danach', 'titel': 'Fotosegmente', 'zeilen': ['Masken der Treffer', '→ Bart, Haar, Ohr', 'im Foto']}],
                'fuss': ['Benutzt %s Gewichte (Bilderkennung, „detector“); die Datei sam3.pt hat %s — %s davon gehören zum Video-Teil („tracker“), hier nicht geladen' % (
                    cls._de(benutzt), cls._de(n['gewichte']), cls._de(n['gewichte'] - benutzt)),
                         'Port Sam3Torch (python14): Masken-IoU 1,0000 gegen das Original (24.10.2026); Maße aus Sam3Torch/modell.py (ViT 1008 px, Patch 14, 32 Blöcke, Text 24 Schichten, 6 + 6)']}

    @classmethod
    def _vitpose(cls, n):
        s = lambda *p: cls._summe(n, *p)  # noqa: E731
        return {'kennung': 'ki-vitpose', 'titel': 'ViTPose-H WholeBody — 133 Punkte des Körpers',
                'untertitel': 'Ein Ausschnitt um die Person auf dem Weg durch das Netz; violett vortrainiert (COCO-WholeBody), hier nicht trainiert.',
                'wo': 'KoerperKI_Fotos.Fotogelenke — Fotos (Gelenkziele der Einpassung) und seit heute auch Renderings (Koerperpruefung: Gelenke Foto ↔ Rendering)',
                'spalten': [
                    {'art': 'eingabe', 'titel': 'Ausschnitt', 'zahl': 3, 'wort': 'Zahlen je Pixel', 'kreise': ('R', 'G', 'B', ''), 'zeilen': ['Kasten der Person', '256 × 192 Pixel']},
                    {'art': 'versteckt', 'titel': 'Felder', 'zahl': 1280, 'wort': 'Zahlen je Feld', 'zeilen': ['16 × 16 Pixel je Feld', '16 × 12 = 192 Felder'],
                     'gewichte': s('backbone.patch_embed', 'backbone.pos_embed')},
                    {'art': 'rueckgrat', 'titel': 'Blöcke 1–32', 'zahl': 1280, 'wort': 'Zahlen je Feld', 'zeilen': ['Transformer', '16 Köpfe'], 'gewichte': s('backbone.blocks', 'backbone.last_norm')},
                    {'art': 'versteckt', 'titel': 'Kopf', 'zahl': 256, 'wort': 'Zahlen je Pixel', 'zeilen': ['2 Entfaltungen ×2', '1.280→256→256', '16 × 12 → 64 × 48'],
                     'gewichte': s('keypoint_head.deconv')},
                    {'art': 'ausgabe', 'titel': 'Wärmekarten', 'zahl': 133, 'wort': 'Karten 64 × 48', 'zeilen': ['17 Körper, 6 Füße,', '68 Gesicht, 42 Hände'],
                     'gewichte': s('keypoint_head.final_layer')},
                    {'art': 'danach', 'titel': 'Posenpunkte', 'zeilen': ['höchster Wert je Karte', '→ 12 Gelenke', 'Schulter … Knöchel', 'mit Zuversicht']}],
                'fuss': ['Summe %s Gewichte (vitpose-h-wholebody.pth, gelesen)' % cls._de(n['gewichte']),
                         'Port VitposeTorch (python14): höchstens 1,05 px Abstand zum Original (24.10.2026); Punktnummern aus VitposeTorch/punkte.py (0–16 Körper, 17–22 Füße, 23–90 Gesicht, 91–132 Hände)']}

    @classmethod
    def _mediapipe(cls, finder, punkte):
        return {'kennung': 'ki-mediapipe', 'titel': 'MediaPipe Face Landmarker — 478 Gesichtspunkte (zwei kleine Netze)',
                'untertitel': 'Erst findet ein Netz das Gesicht, dann liest ein zweites die Punkte aus dem gedrehten Ausschnitt; beide aus face_landmarker.task (Google), hier nicht trainiert.',
                'wo': 'KopfKI (Fotoziele, Kopfpruefung, Kopfbildangleich) — auf dem Foto UND auf dem Rendering des Kopfs: „Detektor auf beiden Seiten“',
                'spalten': [
                    {'art': 'eingabe', 'titel': 'Foto', 'zahl': 3, 'wort': 'Zahlen je Pixel', 'kreise': ('R', 'G', 'B', ''), 'zeilen': ['Seiten gehalten', 'auf 128 × 128']},
                    {'art': 'versteckt', 'titel': 'Finder', 'zahl': 896, 'wort': 'Anker', 'zeilen': ['Faltungen', '%d Operatoren' % 164, 'je Anker 16 + 1 Werte'], 'gewichte': finder['gewichte']},
                    {'art': 'danach', 'titel': 'Ausschnitt', 'zeilen': ['Gesicht gedreht', 'ausgeschnitten', '256 × 256 Pixel']},
                    {'art': 'versteckt', 'titel': 'Punktnetz', 'zahl': 1434, 'wort': 'Zahlen', 'zeilen': ['Faltungen, PReLU', '%d Operatoren' % 471], 'gewichte': punkte['gewichte']},
                    {'art': 'ausgabe', 'titel': 'Gesichtspunkte', 'zahl': 478, 'wort': 'Punkte (x, y, z)', 'zeilen': ['+ Gesicht ja/nein']},
                    {'art': 'danach', 'titel': 'KopfKI', 'zeilen': ['Lage je Foto', 'Fehler in % des', 'Augenabstands,', 'Foto ↔ Rendering']}],
                'fuss': ['Summe %s Gewichte (face_detector.tflite %s + face_landmarks_detector.tflite %s, gelesen)' % (
                    cls._de(finder['gewichte'] + punkte['gewichte']), cls._de(finder['gewichte']), cls._de(punkte['gewichte'])),
                         'Port MediapipeTorch (python14): eigener TFLite-Leser, dasselbe Netz auf der Karte; Ein- und Ausgänge aus den .tflite-Dateien (128 × 128 → 896 × 16; 256 × 256 → 1.434)']}

    @classmethod
    def _haut(cls, n):
        s = lambda *p: cls._summe(n, *p)  # noqa: E731
        kopf = s('haut.kopf')
        letzte = 64 * 3 + 3
        return {'kennung': 'ki-haut', 'titel': 'Haut-KI (Mesh3D-AI Stufe 2, Netz „haut“) — Farbe je Texel aus Punkten der Fotos',
                'untertitel': 'Ein Texel der Hautkacheln auf dem Weg durch das Netz; trainiert von der Mesh3D-AI-Sitzung (Lauf 2026.10.24.04.19_hautwechsel), hier nur benutzt.',
                'wo': 'KopfKI.Fotohaut.ki — Kopf (nurfotos_kopf: nur Punkte des Kopfs) und Körper (nurfotos_koerper: Kopf + Körper); danach Feinzeichnung/Bart (Kopf) bzw. Texel aus den Fotos (Körper)',
                'spalten': [
                    {'art': 'eingabe', 'titel': 'Nachbarn', 'zahl': 9, 'wort': 'Zahlen je Punkt', 'kreise': ('t', 'n', 'F', ''),
                     'zeilen': ['64 Punkte aus den Fotos', 'um den Texel: Lage 3,', 'Farbe − Mittel 3, Farbe 3']},
                    {'art': 'versteckt', 'titel': 'Punktschicht', 'zahl': 64, 'wort': 'Zahlen je Punkt', 'zeilen': ['9 → 32 → 64', 'dieselbe für jeden', 'Nachbarn'], 'gewichte': s('haut.punkt')},
                    {'art': 'figur', 'titel': 'Bündeln', 'zahl': 128, 'wort': 'Zahlen je Texel', 'zeilen': ['Max + Mittel', 'über die Nachbarn']},
                    {'art': 'versteckt', 'titel': 'Ortsgedächtnis', 'zahl': 28, 'wort': 'Zahlen je Texel', 'zeilen': ['Lage in Ruhe + Art', '14 Feinheiten × 2', 'Streuwert-Tafel'],
                     'gewichte': s('haut.ort')},
                    {'art': 'versteckt', 'titel': 'Kopf', 'zahl': 64, 'wort': 'Zahlen je Texel', 'zeilen': ['128 + 21 + 28 = 177', '→ 128 → 64', '(21: Versatz, Farbe', 'Stufe 1, Art …)'],
                     'gewichte': kopf - letzte},
                    {'art': 'ausgabe', 'titel': 'Farbe', 'zahl': 3, 'wort': 'Zahlen je Texel', 'zeilen': ['Korrektur der', 'Grundfarbe', '(skala · tanh)'], 'gewichte': letzte},
                    {'art': 'danach', 'titel': 'Anpassen', 'zeilen': ['Kopf: Falten, Bart', 'aus den Fotos', 'Körper: Texel aus', 'den Fotos, KI nur', 'wo keins Haut sieht']}],
                'fuss': ['Netz „haut“ %s Gewichte, davon %s in der Tafel des Ortsgedächtnisses (Datei netz.pt: vier Netze form/farbe/deckung/haut, %s)' % (
                    cls._de(s('haut.')), cls._de(s('haut.ort')), cls._de(n['gewichte'])),
                         'Aufbau aus mesh3dai_stufe2_netz.py und mesh3dai_stufe2_ort.py (gelesen). Die Tafel fragt nur Lage + Art ab: ein nie trainierter Job bekommt an derselben '
                         'Körperstelle, was die Trainingsjobs dort trugen (Docstring Stufe2ort, 23.10.2026)']}
