# -*- coding: utf-8 -*-
"""Engine2d3dKleidermeshoptionen — die Gruppe `mesh` der Optionen von „2D3D Kleider": das Interface von TRELLIS.2 (02.10.2026).

Edgar (02.10.2026): „Mach einen extra Abschnitt für Mesh. Es sollen die Parameter erscheinen von [dem Hugging-Face-Space
TRELLIS]" — und, als sich herausstellte, dass dieser Space TRELLIS v1 ist: „suche in hugging face nach einem v.2
interface" — dann: „das UI für Mesh bitte direkt unter den Bildern so wie das UI von der Hugging face seite". Vorlage ist
`huggingface.co/spaces/microsoft/TRELLIS.2` (`app.py`, gelesen am 02.10.2026), Reihenfolge wie dort:

    Resolution · Seed · Randomize Seed · Decimation Target · Texture Size        hier `aufloesung`, `seed`, `seed_zufall`,
                                                                                 `flaechen`, `texturgroesse`
    Advanced Settings: Stage 1 Sparse Structure, 2 Shape, 3 Material, je          hier `ss_*`, `form_*`, `tex_*`
        Guidance Strength, Guidance Rescale, Sampling Steps, Rescale T
    Multi-Image: `mehrbild` (Form), `mehrbild_textur`                            Fork `opsiclear-admin/Trellis.2.multiview`,
                                                                                 Runner `mesh_trellismehrbild.py`, Vorgabe aus

Die Stufenwerte sind die der `pipeline.json` von `microsoft/TRELLIS.2-4B` (`sparse_structure_sampler`, `shape_slat_sampler`,
`tex_slat_sampler`) — dieselben, die der Space voreinstellt. Bis dahin reichte der Runner nur `schritte` und `fuehrung`
(Katalog der Seite „Mesh") an Stage 1 UND 2 gemeinsam durch und ließ Stage 3 fest. Der Runner liest diese Gruppe in
`VideoToBVH/wrappers/mesh_trellisregler.py`.

`Aufloesung`, `flaechen` und `texturgroesse` standen bis zum 02.10.2026 in der Gruppe `netz` (`Engine2d3dKleideroptionen.UEBERNAHME`
holt den gespeicherten Wert von dort, solange die Gruppe `mesh` ihn nicht selbst hat). `Engine2d3dKleidernetz.beschreibung` legt
die Gruppe über die der Gruppe `netz`; `seed` ersetzt dort den unsichtbaren der Seite „Mesh".
"""

__all__ = ['Engine2d3dKleidermeshoptionen']

#: Welche Felder zu welchem Modell gehören (`gilt` im Katalog; das Formular blendet die übrigen aus, gespeichert wird alles).
TRELLIS = ['trellis2']
PIXAL = ['pixal3d', 'pixal3d_mv']


def _stufenfelder(stufen):
    """Vier Regler je Stufe, Titel und Bereiche wie im Space (Guidance 1–10, Rescale 0–1, Schritte 1–50, Rescale T 1–6)."""
    felder = []
    for vor, titel, fuehrung, rescale, schritte, rescale_t in stufen:
        felder += [
            {'schluessel': vor + '_fuehrung', 'titel': titel + ' — Guidance Strength', 'art': 'zahl',
             'vorgabe': fuehrung, 'min': 1, 'max': 10, 'schritt': 0.1, 'fein': True, 'gilt': TRELLIS,
             'hinweis': 'Vorgabe %s. Höher hält sich enger ans Foto, zu hoch übersteuert (1 = ohne Guidance).'
                        % fuehrung},
            {'schluessel': vor + '_rescale', 'titel': titel + ' — Guidance Rescale', 'art': 'zahl',
             'vorgabe': rescale, 'min': 0, 'max': 1, 'schritt': 0.01, 'fein': True, 'gilt': TRELLIS,
             'hinweis': 'Vorgabe %s. Gleicht die Streuung des Ergebnisses an die ohne Guidance an — gegen das '
                        'Übersteuern.' % rescale},
            {'schluessel': vor + '_schritte', 'titel': titel + ' — Sampling Steps', 'art': 'zahl',
             'vorgabe': schritte, 'min': 1, 'max': 50, 'schritt': 1, 'fein': True, 'gilt': TRELLIS,
             'hinweis': 'Vorgabe %d. Mehr Schritte rechnen entsprechend länger; ob sie das Netz glätten, ist '
                        'nicht gemessen.' % schritte},
            {'schluessel': vor + '_rescale_t', 'titel': titel + ' — Rescale T', 'art': 'zahl',
             'vorgabe': rescale_t, 'min': 1, 'max': 6, 'schritt': 0.1, 'fein': True, 'gilt': TRELLIS,
             'hinweis': 'Vorgabe %s. Legt mehr der Schritte an den Anfang (grobe Form), weniger ans Ende.'
                        % rescale_t},
        ]
    return felder


def _pixalfelder():
    """Was Pixal3D zusätzlich kennt (`mesh_pixal3d`): das Sichtfeld der Kamera und den Umgang mit dem Grafikspeicher."""
    return [
        {'schluessel': 'pixal_fov', 'titel': 'Pixal3D — Sichtfeld der Kamera (rad)', 'art': 'zahl', 'vorgabe': 0.0,
         'min': 0, 'max': 2, 'schritt': 0.01, 'fein': True, 'gilt': PIXAL,
         'hinweis': '0 = MoGe-2 schätzt es am Foto (Vorgabe). Von Hand: die Autoren nennen 0,2 rad, wenn das Ergebnis verzerrt '
                    'wirkt. Beim Mehrbild gilt das Sichtfeld für alle Ansichten, geschätzt wird es am Foto „vorne".'},
        {'schluessel': 'pixal_speicher', 'titel': 'Pixal3D — Grafikspeicher', 'art': 'wahl', 'vorgabe': 'auto',
         'fein': True, 'gilt': PIXAL, 'werte': [
             ('auto', 'Automatisch — alles auf der GPU, wenn mindestens 24 GB frei sind, sonst stufenweise'),
             ('sparsam', 'Sparsam — die Modelle kommen stufenweise auf die GPU (laut Autoren etwa 10–12 GB, langsamer)'),
             ('voll', 'Voll — alle Modelle auf der GPU (laut Autoren etwa 18 GB, schneller)'),
         ], 'hinweis': 'Die Zahlen der Autoren (Kommentar in `inference.py`); der gemessene Spitzenwert steht im auftrag.log.'},
    ]


def _mehrbildfelder():
    """Multi-Image wie im Community-Space `opsiclear-admin/Trellis.2.multiview` („Structure Algorithm" / „Texture Algorithm"),
    dort ebenfalls unter Advanced Settings. Im Space stehen stochastic/multidiffusion; hier kommt „aus" als Vorgabe dazu."""
    hinweis = ('Experimentell: der Community-Fork (MIT) schreibt selbst, dass es bei verschiedenen Posen oder uneinheitlichen '
               'Details nicht immer gut geht — unsere Fotos können verschiedene Armhaltungen zeigen. Genommen werden die '
               'Fotos der Rollen vorne, hinten, links und rechts mit Gewicht über 0 (vorne zuerst); bei weniger als zwei '
               'Ansichten bleibt es beim Foto „vorne". Die Fotos haben keine Kameraangaben, es wird nur ihr Inhalt gemittelt '
               'bzw. reihum benutzt. Nicht gemessen, ob das Netz davon besser wird.')
    werte = [('stochastic', 'stochastic — jeder Schritt sieht ein anderes Foto, Rechenzeit wie mit einem Foto'),
             ('multidiffusion', 'multidiffusion — jeder Schritt mittelt alle Fotos, Rechenzeit je Schritt N + 1 statt 2 '
                                'Modellaufrufe')]
    return [
        {'schluessel': 'mehrbild', 'titel': 'Multi-Image — Structure Algorithm (Stage 1 und 2)', 'art': 'wahl',
         'vorgabe': 'aus', 'fein': True, 'gilt': TRELLIS, 'werte': [('aus', 'Aus — nur das Foto „vorne" (Vorgabe)')] + werte,
         'hinweis': hinweis},
        {'schluessel': 'mehrbild_textur', 'titel': 'Multi-Image — Texture Algorithm (Stage 3)', 'art': 'wahl',
         'vorgabe': 'multidiffusion', 'fein': True, 'gilt': TRELLIS, 'werte': werte,
         'hinweis': 'Gilt nur, wenn Multi-Image oben an ist. Vorgabe wie im Space: multidiffusion.'},
    ]


class Engine2d3dKleidermeshoptionen:
    #: Je Stufe: Schlüsselvorsatz, Titel wie im Space, Guidance Strength, Guidance Rescale, Sampling Steps,
    #: Rescale T.
    STUFEN = (
        ('ss', 'Stage 1 · Sparse Structure', 7.5, 0.7, 12, 5.0),
        ('form', 'Stage 2 · Shape', 7.5, 0.5, 12, 3.0),
        ('tex', 'Stage 3 · Material', 1.0, 0.0, 12, 3.0),
    )
    FEIN_TITEL = 'Advanced Settings — die Sampler der drei Stufen und Multi-Image'
    #: Das Feld, nach dem das Formular die Felder mit `gilt` ein- und ausblendet (`Meshoptionenformular`).
    GILT_NACH = 'modell'
    KATALOG = [
        {'schluessel': 'modell', 'titel': 'Modell', 'art': 'wahl', 'vorgabe': 'trellis2', 'werte': [
            ('trellis2', 'TRELLIS.2 — ein Foto (Vorgabe)'),
            ('pixal3d', 'Pixal3D — ein Foto, Merkmale per Rückprojektion (Tencent ARC)'),
            ('pixal3d_mv', 'Pixal3D Mehrbild — vorne/hinten/links/rechts mit Kameras'),
        ], 'hinweis': 'TRELLIS.2 (Microsoft, MIT) ist das Modell des Space `microsoft/TRELLIS.2`. Pixal3D (TencentARC, MIT, '
                      'SIGGRAPH 2026) baut auf TRELLIS.2 auf, legt die Bildmerkmale aber pixelgenau in das 3D-Gitter und kennt '
                      'einen echten Mehrbild-Modus. Es läuft in einer eigenen Umgebung (`python10_pixal`) und braucht eigene '
                      'Gewichte (46 GB). Die Felder unten wechseln mit dem Modell. Ob Pixal3D auf unseren Fotos besser wird, '
                      'ist nicht gemessen.'},
        {'schluessel': 'aufloesung', 'titel': 'Resolution', 'art': 'wahl', 'vorgabe': 'hoch', 'werte': [
            ('schnell', '512 — schnell (Pixal3D: 1024)'),
            ('mittel', '1024'),
            ('hoch', '1536 — Vorgabe (braucht Textur 4096 und viele Flächen)'),
        ], 'hinweis': 'Voxelauflösung von TRELLIS.2 (pipeline_type 512, 1024_cascade, 1536_cascade); Pixal3D kennt nur 1024 und '
                      '1536 (schnell und mittel rechnen dort mit 1024). Eine hohe Auflösung '
                      'will auch eine große Textur und viele Flächen: 1536 mit nur 2048 px und 100.000 Flächen gab '
                      'dunkle Flecken über den ganzen Körper (9,3 % Lücken beim Texturbacken statt 0,1 %, gemessen '
                      '27.09.2026).'},
        {'schluessel': 'seed', 'titel': 'Seed', 'art': 'zahl', 'vorgabe': 42, 'min': 0, 'max': 2 ** 31 - 1,
         'hinweis': 'Dieselben Fotos und derselbe Seed geben ein ähnliches, aber nicht bitgleiches Netz (die '
                    'Grafikkarte rechnet nicht reproduzierbar). Der Space nimmt 0.'},
        {'schluessel': 'seed_zufall', 'titel': 'Randomize Seed', 'art': 'wahl', 'vorgabe': 'aus', 'werte': [
            ('aus', 'Nein — der feste Seed (Vorgabe)'),
            ('an', 'Ja — jeder Lauf würfelt neu (der benutzte Seed steht im auftrag.log)'),
        ], 'hinweis': 'Im Space ist es voreingestellt an. Hier aus, damit zwei Läufe mit denselben '
                      'Einstellungen vergleichbar bleiben.'},
        {'schluessel': 'flaechen', 'titel': 'Decimation Target (Flächen)', 'art': 'zahl', 'vorgabe': 100000,
         'min': 100000, 'max': 1000000, 'schritt': 10000,
         'hinweis': 'Die Flächenzahl, auf die `to_glb` das Netz bringt. Der Space: 100.000–500.000, Vorgabe 300.000. '
                    'Hier 100.000: Mit 500.000 baute TRELLIS.2 senkrechte Fäden („Eiszapfen") über die ganze '
                    'Netzhöhe (102.448 von 461.656 Flächen gegen 8 von 96.598, gemessen 01.10.2026).'},
        {'schluessel': 'texturgroesse', 'titel': 'Texture Size', 'art': 'wahl', 'vorgabe': '4096', 'werte': [
            ('1024', '1024 × 1024'), ('2048', '2048 × 2048'), ('3072', '3072 × 3072'), ('4096', '4096 × 4096'),
        ], 'hinweis': 'Der Space: 1024–4096, Vorgabe 2048. Hier 4096, weil der UV-Atlas bei 1536 tausende Inseln hat '
                      '(siehe Resolution).'},
    ] + _stufenfelder(STUFEN) + _mehrbildfelder() + _pixalfelder()

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def katalog(cls):
        aus = []
        for e in cls.KATALOG:
            werte = [{'wert': w, 'text': t} for w, t in e.get('werte', [])]
            aus.append(dict(e, werte=werte, fein=bool(e.get('fein'))))
        return {'optionen': aus, 'fein_titel': cls.FEIN_TITEL, 'gilt_nach': cls.GILT_NACH}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit Werten im Bereich des Space — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['art'] == 'wahl':
                if str(wert) in [w for w, _ in e['werte']]:
                    aus[e['schluessel']] = str(wert)
                continue
            try:
                zahl = float(wert)
            except (TypeError, ValueError):
                continue
            if e['min'] <= zahl <= e['max']:
                aus[e['schluessel']] = int(round(zahl)) if isinstance(e['vorgabe'], int) else zahl
        return aus
