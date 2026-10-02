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

Die Stufenwerte sind die der `pipeline.json` von `microsoft/TRELLIS.2-4B` (`sparse_structure_sampler`, `shape_slat_sampler`,
`tex_slat_sampler`) — dieselben, die der Space voreinstellt. Bis dahin reichte der Runner nur `schritte` und `fuehrung`
(Katalog der Seite „Mesh") an Stage 1 UND 2 gemeinsam durch und ließ Stage 3 fest. Der Runner liest diese Gruppe in
`VideoToBVH/wrappers/mesh_trellisregler.py`.

`Aufloesung`, `flaechen` und `texturgroesse` standen bis zum 02.10.2026 in der Gruppe `netz` (`Engine2d3dKleideroptionen.UEBERNAHME`
holt den gespeicherten Wert von dort, solange die Gruppe `mesh` ihn nicht selbst hat). `Engine2d3dKleidernetz.beschreibung` legt
die Gruppe über die der Gruppe `netz`; `seed` ersetzt dort den unsichtbaren der Seite „Mesh".
"""

__all__ = ['Engine2d3dKleidermeshoptionen']


def _stufenfelder(stufen):
    """Vier Regler je Stufe, Titel und Bereiche wie im Space (Guidance 1–10, Rescale 0–1, Schritte 1–50, Rescale T 1–6)."""
    felder = []
    for vor, titel, fuehrung, rescale, schritte, rescale_t in stufen:
        felder += [
            {'schluessel': vor + '_fuehrung', 'titel': titel + ' — Guidance Strength', 'art': 'zahl',
             'vorgabe': fuehrung, 'min': 1, 'max': 10, 'schritt': 0.1, 'fein': True,
             'hinweis': 'Vorgabe %s. Höher hält sich enger ans Foto, zu hoch übersteuert (1 = ohne Guidance).'
                        % fuehrung},
            {'schluessel': vor + '_rescale', 'titel': titel + ' — Guidance Rescale', 'art': 'zahl',
             'vorgabe': rescale, 'min': 0, 'max': 1, 'schritt': 0.01, 'fein': True,
             'hinweis': 'Vorgabe %s. Gleicht die Streuung des Ergebnisses an die ohne Guidance an — gegen das '
                        'Übersteuern.' % rescale},
            {'schluessel': vor + '_schritte', 'titel': titel + ' — Sampling Steps', 'art': 'zahl',
             'vorgabe': schritte, 'min': 1, 'max': 50, 'schritt': 1, 'fein': True,
             'hinweis': 'Vorgabe %d. Mehr Schritte rechnen entsprechend länger; ob sie das Netz glätten, ist '
                        'nicht gemessen.' % schritte},
            {'schluessel': vor + '_rescale_t', 'titel': titel + ' — Rescale T', 'art': 'zahl',
             'vorgabe': rescale_t, 'min': 1, 'max': 6, 'schritt': 0.1, 'fein': True,
             'hinweis': 'Vorgabe %s. Legt mehr der Schritte an den Anfang (grobe Form), weniger ans Ende.'
                        % rescale_t},
        ]
    return felder


class Engine2d3dKleidermeshoptionen:
    #: Je Stufe: Schlüsselvorsatz, Titel wie im Space, Guidance Strength, Guidance Rescale, Sampling Steps,
    #: Rescale T.
    STUFEN = (
        ('ss', 'Stage 1 · Sparse Structure', 7.5, 0.7, 12, 5.0),
        ('form', 'Stage 2 · Shape', 7.5, 0.5, 12, 3.0),
        ('tex', 'Stage 3 · Material', 1.0, 0.0, 12, 3.0),
    )
    FEIN_TITEL = 'Advanced Settings — die Sampler der drei Stufen'
    KATALOG = [
        {'schluessel': 'aufloesung', 'titel': 'Resolution', 'art': 'wahl', 'vorgabe': 'hoch', 'werte': [
            ('schnell', '512 — schnell'),
            ('mittel', '1024'),
            ('hoch', '1536 — Vorgabe (braucht Textur 4096 und viele Flächen)'),
        ], 'hinweis': 'Voxelauflösung von TRELLIS.2 (pipeline_type 512, 1024_cascade, 1536_cascade). Eine hohe Auflösung '
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
    ] + _stufenfelder(STUFEN)

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def katalog(cls):
        aus = []
        for e in cls.KATALOG:
            werte = [{'wert': w, 'text': t} for w, t in e.get('werte', [])]
            aus.append(dict(e, werte=werte, fein=bool(e.get('fein'))))
        return {'optionen': aus, 'fein_titel': cls.FEIN_TITEL}

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
