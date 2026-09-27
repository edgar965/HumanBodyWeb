# -*- coding: utf-8 -*-
"""Meshoptionen — was der Reiter „Mesh" einstellen lässt, mit Vorgaben und Verfügbarkeit.

Edgar (26.09.2026): „Optionen auswählen (mach Vorschlag)" — „Mache die Auswahl Hunyuan3D
und Trellis auswählbar", später „bei Hunyuan3D auch Textur Malerei" und (26.09.2026,
abends) alle drei besprochenen Mehrbild-Wege zugleich als Option: Fotogewicht je Bild
(live in der Textur-Vorschau), Hunyuan3D-2mv (echtes Multiview-Formmodell) und Fusion
(mehrere Einzelnetze gewichtet gemittelt). Der Vorschlag steht als Tabelle `KATALOG`
(Seite und Lauf lesen dieselbe); `pruefen` lässt nur bekannte Schlüssel und Werte durch,
alles andere fällt auf die Vorgabe (ein altes Formular oder ein Tippfehler startet sonst
einen Lauf mit `None`-Werten).

Formmodelle (Gewichte unter `settings.HF_HOME_DIR`, Umgebung `settings.MESH_PYTHON`):
    trellis2       TRELLIS.2-4B (Microsoft, MIT) — ein Bild, bis 1536³, EIGENE PBR-Textur
                   (gelernt, `o_voxel.postprocess.to_glb`) — voll verdrahtet.
    hunyuan3d_2    Hunyuan3D-2.0 (Tencent, Forschungslizenz — NICHT in EU/UK/Südkorea, Edgar
                   26.09.2026: „downloade auch Hunyuan3D, das ist für Forschung") —
                   `hy3dgen.shapegen` für die Form, bei „ki"/„fotos_ki" zusätzlich Hunyuan3Ds
                   EIGENE Multiview-Diffusions-Texturmalerei (`hy3dgen.texgen`, Edgar
                   26.09.2026: „bei Hunyuan3D auch Textur Malerei"). Braucht die von Hand
                   kompilierte `custom_rasterizer`-Erweiterung; fehlt sie, fällt der Runner
                   automatisch auf die Fotos zurück (`_run_mesh.py::fototextur_vertexfarben`).
    hunyuan3d_2mv  Hunyuan3D-2mv — ECHTES Multiview-Formmodell: bis zu vier Fotos
                   (vorne/hinten/links/rechts) gehen GEMEINSAM in einen Formlauf
                   (`hy3dgen.shapegen.preprocessors.MVImageProcessorV2`, Schlüssel
                   front/back/left/right). Dieselbe Texturmalerei wie hunyuan3d_2.
    hunyuan3d_21   Gewichte werden heruntergeladen, aber NOCH NICHT verdrahtet (eigenes
                   `hy3dgen`) — `NICHT_VERDRAHTET`, im Katalog als „in Vorbereitung" markiert.

`mehrbildmodus` (unabhängig vom Formmodell): „einzelbild" (Vorgabe, nur das „vorne"-Bild
bestimmt die Form) oder „fusion" (je Bild ein eigener Formlauf mit dem gewählten
Formmodell, per Fotogewicht zu einem Netz gemittelt — `_run_mesh.py::form_fusion`,
SDF-Averaging + Marching Cubes; keine geerbte PBR/Texturmalerei danach, nur Fotos).
Jedes Bild trägt zusätzlich ein `gewicht` (0–100, Vorgabe 100) und optional einen
`bereich` (Rechteck-Ausschnitt) — beide wirken auf die Textur-Projektion IMMER, auf die
Form nur bei `mehrbildmodus=fusion`.
"""

import os
from pathlib import Path

from django.conf import settings

__all__ = ['Meshoptionen']


class Meshoptionen:
    #: Die Rollen eines Fotos (Auswahl je Bild auf der Seite).
    ROLLEN = [
        ('auto', 'Automatisch'),
        ('vorne', 'Vorne'),
        ('hinten', 'Hinten'),
        ('links', 'Links'),
        ('rechts', 'Rechts'),
        ('gesicht', 'Nahaufnahme Gesicht'),
        ('detail', 'Nur Textur (Detail)'),
        ('aus', 'Nicht verwenden'),
    ]

    #: Welche HF-Ablage ein Formmodell braucht (`models--<org>--<name>` in hf_home/hub).
    GEWICHTE = {
        'trellis2': ['microsoft/TRELLIS.2-4B', 'microsoft/TRELLIS-image-large', 'timm/vit_large_patch16_dinov3.lvd1689m'],
        'hunyuan3d_2': ['tencent/Hunyuan3D-2'],
        'hunyuan3d_2mv': ['tencent/Hunyuan3D-2mv'],
        'hunyuan3d_21': ['tencent/Hunyuan3D-2.1'],
    }
    #: Noch kein Runner-Code (`_run_mesh.py`) — im Katalog wählbar, aber gesperrt.
    NICHT_VERDRAHTET = ('hunyuan3d_21',)

    KATALOG = [
        {'schluessel': 'formmodell', 'titel': 'Formmodell', 'art': 'wahl', 'vorgabe': 'trellis2', 'werte': [
            ('trellis2', 'TRELLIS.2 (Microsoft, 4B) — ein Bild, sehr fein, eigene PBR-Textur'),
            ('hunyuan3d_2', 'Hunyuan3D-2.0 — ein Bild, eigene Texturmalerei oder Fotos (Forschungslizenz)'),
            ('hunyuan3d_2mv', 'Hunyuan3D-2mv — mehrere Ansichten fließen in die Form ein (Forschungslizenz)'),
            ('hunyuan3d_21', 'Hunyuan3D-2.1 — ein Bild (in Vorbereitung)'),
        ], 'hinweis': 'Hunyuan3D: Tencent-Forschungslizenz, gilt nicht in der EU/UK/Südkorea.'},
        {'schluessel': 'verwendung', 'titel': 'Kopf/Körper', 'art': 'wahl', 'vorgabe': 'ganz', 'werte': [
            ('ganz', 'Ganze Figur'),
            ('koerper', 'Körper — Kopf kommt aus einem anderen Lauf'),
            ('kopf', 'Kopf / Gesicht — für den Kopf eines anderen Laufs'),
        ], 'hinweis': 'Nur eine Kennzeichnung, sie ändert den Lauf NICHT. Sie sagt, wozu dieses '
                      'Netz dienen soll, wenn Kopf und Körper aus verschiedenen Läufen kommen '
                      '(„Mesh to 3D" nimmt beide Netze getrennt entgegen). Jederzeit änderbar — '
                      'in der Tabellenspalte „Kopf/Körper" auch ohne neuen Lauf.'},
        {'schluessel': 'mehrbildmodus', 'titel': 'Mehrere Fotos', 'art': 'wahl',
         'vorgabe': 'einzelbild', 'werte': [
            ('einzelbild', 'Nur „Vorne" bestimmt die Form (Vorgabe)'),
            ('fusion', 'Je Foto ein eigenes Netz, per Fotogewicht gemittelt (langsamer, gröber)'),
        ], 'hinweis': 'Fusion rechnet die Form je gewichtetem Foto neu und mittelt — deutlich '
                      'länger, gröberes Ergebnis, danach nur Foto-Textur (keine KI-Textur). '
                      '**Die Feinheit kommt dann vom Fusion-Gitter, nicht von „Flächen":** '
                      'bei 96³ hat das Ergebnis rund 8.000–15.000 Flächen, ganz gleich, was '
                      'oben eingestellt ist (gemessen 27.09.2026). Und die Fotos brauchen '
                      'eine gesetzte Rolle (Vorne/Hinten/Links/Rechts) — mit weniger als '
                      'zwei davon läuft der gewöhnliche Einzelbildweg.'},
        {'schluessel': 'aufloesung', 'titel': 'Auflösung', 'art': 'wahl', 'vorgabe': 'hoch', 'werte': [
            ('schnell', 'Schnell — TRELLIS 512³ / Hunyuan Octree 256'),
            ('mittel', 'Mittel — TRELLIS 1024³ / Hunyuan Octree 384'),
            ('hoch', 'Hoch — TRELLIS 1536³ / Hunyuan Octree 512 (braucht Textur 4096 + 500.000 Flächen)'),
            ('sehr_hoch', 'Sehr hoch — nur Hunyuan3D (Octree 768); TRELLIS.2 rechnet wie „Hoch"'),
        ], 'hinweis': 'Eine hohe Auflösung will auch eine große Textur und viele Flächen: '
                      '1536³ mit nur 2048 px und 100.000 Flächen gab bei TRELLIS.2 dunkle '
                      'Flecken über den ganzen Körper (9,3 % Lücken beim Texturbacken statt '
                      '0,1 %), weil der UV-Atlas in tausende winzige Inseln zerfällt.'},
        {'schluessel': 'freistellen', 'titel': 'Hintergrund', 'art': 'wahl', 'vorgabe': 'auto', 'werte': [
            ('auto', 'Automatisch freistellen (BiRefNet)'),
            ('alpha', 'Alphakanal der Datei verwenden'),
        ]},
        {'schluessel': 'maskenkante', 'titel': 'Maskenkante', 'art': 'wahl', 'vorgabe': 'hart', 'fein': True,
         'werte': [
            ('hart', 'Halbdurchsichtiges begradigen (Vorgabe)'),
            ('weich', 'Rohe Wahrscheinlichkeit des Freistellers'),
        ], 'hinweis': 'BiRefNet gibt eine weiche Maske aus. Am Gesichtsfoto lagen 7,5 % aller '
                      'Pixel im Graubereich — alle an fliegenden Haarsträhnen, und beide '
                      'Formmodelle bauen daraus freischwebende Fetzen. „Hart" spreizt den '
                      'Bereich 35–65 % auf 0/100 %, lässt aber einen schmalen Saum stehen.'},
        {'schluessel': 'straehnen', 'titel': 'Feine Ausläufer öffnen (Radius)', 'art': 'zahl',
         'vorgabe': 4, 'min': 0, 'max': 16, 'schritt': 1, 'fein': True,
         'hinweis': 'Entfernt vor dem Formlauf alles aus der Maske, was dünner ist als dieser '
                    'Radius (bezogen auf eine Bildkante von 1024 px) — fliegende Haarsträhnen, '
                    'aus denen beide Formmodelle ihre weißen Zapfen bauen. **Bei einer '
                    'Nahaufnahme des Kopfes lohnt 8**: Drei Läufe am selben Gesichtsfoto gaben '
                    '4,42 → 3,91 → 3,36 Oberfläche je Höhe² (Radius 0/4/8), und erst bei 8 sind '
                    'die Zapfen auch im Bild weg. Höher NICHT pauschal einstellen: Am '
                    'Ganzkörperfoto nimmt Radius 4 nur 0,04 % der Silhouette, Radius 8 aber '
                    'schon ein Fingerglied. Eine Haarerkennung wäre hier der falsche Hebel — sie '
                    'findet den kompakten Haarblock, nicht die Strähnen (nur 10 % der '
                    'halbdurchsichtigen Pixel liegen in ihrer Haarklasse).'},
        {'schluessel': 'bildrand', 'titel': 'Rand um das Motiv (%)', 'art': 'zahl',
         'vorgabe': 0, 'min': 0, 'max': 30, 'schritt': 5, 'fein': True,
         'hinweis': 'Luft rundum, bevor das Foto ins Formmodell geht. Der Zuschnitt legt das '
                    'Quadrat sonst genau auf das Motiv, und die Silhouette berührt alle vier '
                    'Bildränder (am Damira-Kopf gemessen: Material von Zeile 0 bis 2665 bei '
                    'Bildhöhe 2666). Dann weiß das Modell nicht, wo das Haar aufhört, und zieht '
                    'es als senkrechte Vorhänge nach unten weiter — die „Eiszapfen" seitlich am '
                    'Kopf. Hunyuan3D gibt seinem eigenen Vorverarbeiter dafür 15 %. '
                    '**Achtung bei „Textur: Fotos":** Die Projektion passt das Foto über die '
                    'Netz-Spanne ein und kennt den Rand nicht — dort 0 lassen, sonst sitzt die '
                    'Farbe um genau diesen Anteil verschoben.'},
        {'schluessel': 'fetzen', 'titel': 'Kleinteile entfernen (%)', 'art': 'zahl', 'vorgabe': 1,
         'min': 0, 'max': 50, 'schritt': 0.5, 'fein': True,
         'hinweis': 'Teilkörper unter diesem Anteil der größten zusammenhängenden Fläche fallen '
                    'weg — 0 schaltet ab. Das gibt dem Gesicht sein Flächenbudget zurück: Ein '
                    'Kopf mit rekonstruierten Haaren hatte die 4- bis 10-fache Oberfläche eines '
                    'ganzen Körpernetzes, und das Flächenziel verteilt sich darauf.'},
        {'schluessel': 'kopfanteil', 'titel': 'Kopfanteil für „Gesicht" (%)', 'art': 'zahl',
         'vorgabe': 0, 'min': 0, 'max': 99, 'schritt': 1, 'fein': True,
         'hinweis': 'AUS (0), weil der Lauf vom 27.09.2026 das Gegenteil brachte: Ein Foto mit '
                    'der Rolle „Nahaufnahme Gesicht" färbt damit die obersten so viel Prozent der '
                    'Netzhöhe — aber der quadratische Zuschnitt des Freistellers umfasst Kopf, '
                    'Hals und Schulteransatz, ein fester Höhenanteil trifft ihn nicht, und das '
                    'Gesicht landet verschoben und verwaschen auf dem Kopf (Vergleichsbilder in '
                    'mesh-laeufe.md). Wer es ausprobieren will, stellt hier einen Wert ein. Sauber '
                    'geht es nur über Gesichtslandmarken — das macht der Reiter „Mesh to 3D".'},
        {'schluessel': 'textur', 'titel': 'Textur', 'art': 'wahl', 'vorgabe': 'fotos_ki', 'werte': [
            ('fotos_ki', 'Fotos aufprojiziert, Lücken aus der Modelltextur'),
            ('fotos', 'Nur Fotos (Lücken aufgefüllt)'),
            ('ki', 'Nur die Textur des Formmodells (TRELLIS.2: PBR; Hunyuan3D: eigene Texturmalerei)'),
            ('malerei', 'Hunyuan3D malt die Textur — auch auf einer TRELLIS.2-Form'),
            ('keine', 'Keine (grau)'),
        ], 'hinweis': 'Hunyuan3D ohne kompilierte Rasterizer-Erweiterung fällt bei „ki"/„fotos_ki" '
                      'automatisch auf die Fotoprojektion zurück. **„fotos_ki" heißt bei '
                      'Hunyuan3D trotzdem Malerei** (die Fotos kommen nur zum Zug, wenn sie '
                      'scheitert) — wer wirklich projizieren will, nimmt „fotos", zahlt das '
                      'aber mit Punktfarben statt einer UV-Textur. **„Hunyuan3D malt"** ist '
                      'die Kombination, nach der die Form von TRELLIS.2 kommt (auf 1024 px '
                      'konditioniert) und die Textur von Hunyuan3D: die feinere Form mit '
                      'einer echten UV-Textur statt TRELLIS.2s Voxel-PBR.'},
        {'schluessel': 'relief', 'titel': 'Relief aus den Fotos', 'art': 'wahl', 'vorgabe': 'aus', 'werte': [
            ('aus', 'Aus'),
            ('an', 'Feinstruktur der Fotos als Normal Map'),
        ], 'hinweis': 'Poren, Härchen und Lippenrillen kann die FORM nicht tragen — bei '
                      'Hunyuan3D steckt die ganze Gestalt in 3072 Latents, und das Foto sieht '
                      'das Modell als 37 × 37 Merkmalsraster. Im Foto sind sie aber da. Diese '
                      'Option holt das Feine (Hochpass) aus den Fotos und legt es als Normal '
                      'Map an die Textur: Das Netz bleibt glatt, die Beleuchtung wird fein. '
                      'Braucht eine UV-Textur, wirkt also nicht bei Textur „fotos" (Punktfarben). '
                      'Was im Foto FARBE ist (Sommersprossen, Muttermale), wird dabei zu Relief '
                      '— deshalb die Stärke zurückhaltend halten.'},
        {'schluessel': 'relief_staerke', 'titel': 'Relief-Stärke (%)', 'art': 'zahl', 'vorgabe': 100,
         'min': 0, 'max': 400, 'schritt': 10, 'fein': True,
         'hinweis': '100 % = die gemessene Fotostruktur. Höher übertreibt die Schattierung, '
                    '0 schaltet das Relief aus.'},
        {'schluessel': 'gesicht', 'titel': 'Gesicht', 'art': 'wahl', 'vorgabe': 'an', 'werte': [
            ('an', 'Nahaufnahme für Form und Textur des Kopfes nutzen'),
            ('textur', 'Nahaufnahme nur für die Textur'),
            ('aus', 'Nahaufnahme nicht nutzen'),
        ]},
        {'schluessel': 'texturgroesse', 'titel': 'Texturgröße', 'art': 'wahl', 'vorgabe': '4096', 'werte': [
            ('2048', '2048 × 2048'), ('4096', '4096 × 4096'),
        ]},
        {'schluessel': 'flaechen', 'titel': 'Flächen', 'art': 'wahl', 'vorgabe': '500000', 'werte': [
            ('100000', '100.000'), ('300000', '300.000'), ('500000', '500.000'), ('1000000', '1 Mio.'),
        ]},
        {'schluessel': 'hoehe_cm', 'titel': 'Höhe (cm)', 'art': 'zahl', 'vorgabe': 170, 'min': 1, 'max': 100000,
         'hinweis': 'Das Netz wird auf diese Höhe skaliert, Füße auf 0, Y oben.'},
        {'schluessel': 'formate', 'titel': 'Ausgabe', 'art': 'mehrfach', 'vorgabe': ['glb', 'obj'], 'werte': [
            ('glb', 'GLB (Textur eingebettet)'), ('obj', 'OBJ + MTL + PNG'), ('ply', 'PLY (Punktfarben)'),
        ]},
        {'schluessel': 'seed', 'titel': 'Seed', 'art': 'zahl', 'vorgabe': 42, 'min': 0, 'max': 2 ** 31 - 1},

        # --- Feineinstellungen (`fein`: im Formular in einem zugeklappten Bereich) -------
        # Bis 27.09.2026 standen diese Werte fest im Runner. Edgar: „Es gibt doch sicherlich
        # Einstellungen für alle Jobs - mach die im UI sichtbar und einstellbar vor dem Lauf."
        # Jeder Wert ist an der Pipeline nachgelesen, nicht geraten: TRELLIS.2 aus seiner
        # `pipeline.json` (`steps` 12, `guidance_strength` 7,5) und `o_voxel.postprocess
        # .to_glb`, Hunyuan3D aus `Hunyuan3DDiTFlowMatchingPipeline.__call__`
        # (`num_inference_steps` 50, `guidance_scale` 5,0).
        {'schluessel': 'schritte', 'titel': 'Rechenschritte', 'art': 'zahl', 'vorgabe': 0,
         'min': 0, 'max': 200, 'fein': True,
         'hinweis': '0 = Vorgabe des Modells (TRELLIS.2 12, Hunyuan3D 50). Mehr Schritte: '
                    'feiner und deutlich langsamer.'},
        {'schluessel': 'fuehrung', 'titel': 'Bildtreue (Guidance)', 'art': 'zahl', 'vorgabe': 0,
         'min': 0, 'max': 30, 'schritt': 0.5, 'fein': True,
         'hinweis': '0 = Vorgabe des Modells (TRELLIS.2 7,5, Hunyuan3D 5,0). Höher hält sich '
                    'enger ans Foto, kann aber Artefakte verstärken.'},
        {'schluessel': 'netzaufbau', 'titel': 'Netz neu aufbauen (nur TRELLIS.2)', 'art': 'wahl',
         'vorgabe': 'remesh', 'fein': True, 'werte': [
            ('remesh', 'Ja — Dual Contouring, gleichmäßige Dreiecke (Vorgabe)'),
            ('direkt', 'Nein — das Rohnetz nur vereinfachen'),
        ], 'hinweis': 'Ohne Neuaufbau bleibt die Voxeltreppe im Netz, dafür sitzt die Textur '
                      'genauer (sie wird auf das Rohnetz zurückprojiziert).'},
        {'schluessel': 'aufbau_band', 'titel': 'Aufbau-Band (Voxel)', 'art': 'zahl', 'vorgabe': 1,
         'min': 1, 'max': 8, 'fein': True,
         'hinweis': 'Wie weit der Neuaufbau um die Rohfläche herum rechnet (`remesh_band`). '
                    'Breiter schließt Löcher, rundet aber ab.'},
        {'schluessel': 'aufbau_anziehen', 'titel': 'Auf die Rohfläche ziehen', 'art': 'zahl',
         'vorgabe': 0, 'min': 0, 'max': 1, 'schritt': 0.1, 'fein': True,
         'hinweis': '`remesh_project`: 0 = das neu aufgebaute Netz bleibt glatt, 1 = jeder Punkt '
                    'wird auf die Rohfläche zurückgezogen (schärfer, aber auch zackiger).'},
        {'schluessel': 'fusion_gitter', 'titel': 'Fusion-Gitter', 'art': 'wahl', 'vorgabe': '96',
         'fein': True, 'werte': [
            ('64', '64³ — grob, schnell'), ('96', '96³ (Vorgabe)'), ('128', '128³ — feiner, langsamer'),
        ], 'hinweis': 'Nur bei „Mehrere Fotos: Fusion" — das gemeinsame Gitter, auf dem die '
                      'Einzelnetze gemittelt werden.'},
    ]

    @classmethod
    def eintrag(cls, schluessel):
        for e in cls.KATALOG:
            if e['schluessel'] == schluessel:
                return e
        raise KeyError(schluessel)

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: (list(e['vorgabe']) if isinstance(e['vorgabe'], list) else e['vorgabe'])
                for e in cls.KATALOG}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit gültigen Werten — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            erlaubt = [w for w, _ in e.get('werte', [])]
            if e['art'] == 'wahl' and str(wert) in erlaubt:
                aus[e['schluessel']] = str(wert)
            elif e['art'] == 'mehrfach' and isinstance(wert, list):
                gewaehlt = [w for w in erlaubt if w in wert]
                aus[e['schluessel']] = gewaehlt or aus[e['schluessel']]
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except (TypeError, ValueError):
                    continue
                if e.get('min', zahl) <= zahl <= e.get('max', zahl):
                    aus[e['schluessel']] = int(zahl) if float(zahl).is_integer() else zahl
        if 'glb' not in aus['formate']:
            aus['formate'] = ['glb', *aus['formate']]  # die Vorschau der Seite liest das GLB
        return aus

    @classmethod
    def rolle_pruefen(cls, rolle):
        return rolle if rolle in dict(cls.ROLLEN) else 'auto'

    @staticmethod
    def gewicht_pruefen(wert):
        try:
            zahl = float(wert)
        except (TypeError, ValueError):
            return 100
        return int(max(0, min(100, zahl)))

    @staticmethod
    def bereich_pruefen(wert):
        """`[x0,y0,x1,y1]` normiert 0..1, x0<x1 und y0<y1 — sonst `None` (ganzes Bild)."""
        if not isinstance(wert, (list, tuple)) or len(wert) != 4:
            return None
        try:
            x0, y0, x1, y1 = (float(w) for w in wert)
        except (TypeError, ValueError):
            return None
        x0, x1 = sorted((max(0.0, min(1.0, x0)), max(0.0, min(1.0, x1))))
        y0, y1 = sorted((max(0.0, min(1.0, y0)), max(0.0, min(1.0, y1))))
        if x1 - x0 < 0.01 or y1 - y0 < 0.01:
            return None
        return [x0, y0, x1, y1]

    # --------------------------------------------------------- Verfügbarkeit

    @staticmethod
    def _hf_da(repo):
        ordner = Path(settings.HF_HOME_DIR) / 'hub' / ('models--' + repo.replace('/', '--')) / 'snapshots'
        return ordner.is_dir() and any(ordner.iterdir())

    @classmethod
    def verfuegbar(cls):
        """`{formmodell: grund_oder_leer}` — leer heißt bereit."""
        umgebung = os.path.isfile(settings.MESH_PYTHON)
        aus = {}
        for modell, repos in cls.GEWICHTE.items():
            if modell in cls.NICHT_VERDRAHTET:
                aus[modell] = 'In Vorbereitung — noch kein Runner-Code'
                continue
            fehlt = [r for r in repos if not cls._hf_da(r)]
            if not umgebung:
                aus[modell] = 'Umgebung python10_mesh fehlt'
            elif fehlt:
                aus[modell] = 'Gewichte fehlen: %s' % ', '.join(fehlt)
            else:
                aus[modell] = ''
        return aus

    @classmethod
    def katalog(cls):
        """Der Katalog für die Seite, mit Verfügbarkeit je Formmodell."""
        frei = cls.verfuegbar()
        aus = []
        for e in cls.KATALOG:
            neu = dict(e, werte=[{'wert': w, 'text': t, **({'fehlt': frei[w]} if frei.get(w) else {})}
                                 for w, t in e.get('werte', [])], fein=bool(e.get('fein')))
            aus.append(neu)
        return {'optionen': aus, 'rollen': [{'wert': w, 'text': t} for w, t in cls.ROLLEN]}
