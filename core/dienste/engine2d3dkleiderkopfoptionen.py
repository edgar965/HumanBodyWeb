# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopfoptionen — die Gruppe `kopf` der Optionen von „2D3D Kleider": der eigene Kopf-Lauf (07.10.2026).

Edgar (07.10.2026): „ok, mach einen extra Kopf lauf, extrahiere dazu die bilder vom Kopf, von alle drei seiten … Kopf Lauf als extra schritt und extra UI. Per Check box (default an)
anwählbar. wenn das ausgewählt ist, erstellst und zeigst du die 3 Kopf Bilder im UI und rechnest den Kopf extra."

Warum: Hunyuan3D sieht jedes Bild nur als 518-px-Raster (`mesh-qualitaet.md`); auf einem Ganzkörperfoto bleiben dem Kopf rund 50 px. Der Schritt „kopf" schneidet den Kopf aus den drei
vorbereiteten Fotos (`Engine2d3dKleiderkopfausschnitt`), rechnet daraus ein eigenes Kopfnetz (`Engine2d3dKleiderkopfnetz`) und die Körper-Kette setzt es ein (`Meshfigurkopfnetz`, wie bei
„Mesh to 3D"). Das Häkchen ist `rechnen`; ohne Häkchen entfällt der Schritt im vollen Lauf (ausdrücklich gestartet läuft er immer) und die Körper-Kette nimmt kein Kopfnetz.
`modell` und `flaechen` sind die Wahl für den Kopflauf — Vorgaben nach dem guten Lauf vom 27.09.2026 (`…13.23.11`: Hunyuan3D-2, 300.000 Flächen).
"""

__all__ = ['Engine2d3dKleiderkopfoptionen']


class Engine2d3dKleiderkopfoptionen:
    KATALOG = [
        {'schluessel': 'rechnen', 'titel': 'Kopf extra rechnen (Ausschnitte aus den drei Fotos)', 'art': 'haken', 'vorgabe': 'an', 'an': 'an', 'aus': 'aus',
         'hinweis': 'Angehakt: Der Schritt „Kopf“ schneidet den Kopf aus den drei vorbereiteten Fotos (vorne, hinten, Seite), zeigt die Ausschnitte unten und rechnet daraus ein eigenes '
                    'Kopfnetz; die Körper-Kette setzt es für das Gesicht ein. Hunyuan3D sieht jedes Bild nur als 518-px-Raster — auf einem Ganzkörperfoto bleiben dem Kopf rund 50 px, im Ausschnitt '
                    'das Siebenfache (am Foto abgelesen, nicht gemessen). Ohne Häkchen entfällt der Schritt im vollen Lauf; über „Kopf rechnen“ läuft er auch dann.'},
        {'schluessel': 'modell', 'titel': 'Modell für den Kopf', 'art': 'wahl', 'vorgabe': 'hunyuan3d_2mv', 'werte': [
            ('hunyuan3d_2mv', 'Hunyuan3D-2mv — die drei Ausschnitte fließen gemeinsam in die Form ein'),
            ('hunyuan3d_2', 'Hunyuan3D-2.0 — nur der vordere Ausschnitt (so lief der gute Kopf vom 27.09.2026)'),
            ('trellis2', 'TRELLIS.2 — nur der vordere Ausschnitt, kein Tencent-Lizenzvorbehalt'),
        ], 'hinweis': 'Welches den besseren Kopf gibt, ist nicht gemessen: der gute Lauf vom 27.09.2026 war Hunyuan3D-2.0 aus EINEM Gesichtsfoto, der Ganzkörperlauf von „Edgar - Hunyan“ '
                      'Hunyuan3D-2mv. Tencent-Forschungslizenz (beide Hunyuan-Werte), gilt nicht in der EU/UK/Südkorea. TRELLIS.2 (07.10.2026 ergänzt, Edgar: „mach den gleichen Kopf '
                      'schritt wie Hunyan … kann man das auch mit trellis machen") läuft denselben Mesh-Runner (`mesh_formmodelle.form_trellis2`) wie der Schritt „netz“, nur mit dem '
                      'Kopfausschnitt statt der Ganzkörperfotos — bislang nur in einem eigenständigen Testauftrag erprobt, nicht über diesen Schritt.'},
        {'schluessel': 'flaechen', 'titel': 'Flächen des Kopfnetzes', 'art': 'wahl', 'vorgabe': '300000', 'werte': [
            ('100000', '100.000'), ('200000', '200.000'), ('300000', '300.000 (Vorgabe, wie der Lauf vom 27.09.2026)'), ('500000', '500.000'),
        ], 'hinweis': 'Der Kopf trägt das Flächenbudget allein; je mehr Flächen, desto länger das UV-Auspacken der Texturmalerei (gemessen, parallel zu einem anderen GPU-Lauf: '
                      '100.000 Flächen 408 s, 200.000 Flächen 1.020 s).'},
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @staticmethod
    def _erlaubt(eintrag):
        """Die Werte, die ein Feld annehmen darf: bei einer Wahl die Liste, bei einem Häkchen `aus` und `an`."""
        if eintrag['art'] == 'haken':
            return [eintrag['aus'], eintrag['an']]
        return [w for w, _ in eintrag['werte']]

    @classmethod
    def katalog(cls):
        aus = []
        for e in cls.KATALOG:
            werte = [{'wert': w, 'text': t} for w, t in e.get('werte', [])]
            aus.append(dict(e, werte=werte, fein=bool(e.get('fein'))))
        return {'optionen': aus}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit erlaubten Werten — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is not None and str(wert) in cls._erlaubt(e):
                aus[e['schluessel']] = str(wert)
        return aus
