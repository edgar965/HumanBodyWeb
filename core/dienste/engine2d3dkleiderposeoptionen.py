# -*- coding: utf-8 -*-
"""Engine2d3dKleiderposeoptionen — die Gruppe `pose` der Optionen von „2D3D Kleider": die Pose aus dem Foto (11.10.2026).

Anlass: der Auftrag „Modigliani" (`2026.10.11.14.32.44`, liegender Akt, ein Foto). Die Körper-Kette findet an einem solchen Netz keine Pose (MediaPipe: 1 von 33 Punkten) und hielt das
3,62 lange Netz für Zentimeter (`Meshfigurscan.einheit_anpassen`). Der Schritt „pose" findet die Gelenke am FOTO (SAM 3D Body, `_run_sam3dpose.py`), legt sie ins Netz und leitet daraus den Maßstab ab;
die Körper-Kette nimmt beides, wenn das Häkchen `rechnen` an ist (`Engine2d3dKleiderpose.fuer_koerper`). Konzept und Proben: `Docu/konzepte/2026-10-11_gemaelde-schnelldurchlauf-und-freie-pose-konzept.md`.

`drehung` ist eine WAHL, keine Automatik: gemessen an den vier Läufen der Probe trennt kein Maß die Drehungen (Gelenke in der Silhouette 11–12 von 12 in jeder, Silhouetten-IoU des SAM-Körpers 0,31–0,38).
`weglassen`: verdeckte Gliedmaßen schätzt SAM — am Gemälde hing der verdeckte linke Arm vor dem Bauch statt hinter dem Kopf; ein Gelenk, das nicht stimmt, gehört nicht in die Landmarken.
"""

__all__ = ['Engine2d3dKleiderposeoptionen']


class Engine2d3dKleiderposeoptionen:
    GELENKE = (
        ('left-elbow', 'Linker Ellbogen'), ('left-wrist', 'Linkes Handgelenk'), ('right-elbow', 'Rechter Ellbogen'), ('right-wrist', 'Rechtes Handgelenk'),
        ('left-knee', 'Linkes Knie'), ('left-ankle', 'Linker Knöchel'), ('right-knee', 'Rechtes Knie'), ('right-ankle', 'Rechter Knöchel'),
    )
    KATALOG = [
        {'schluessel': 'rechnen', 'titel': 'Pose aus dem Foto rechnen (Gelenke und Maßstab für die Körper-Kette)', 'art': 'haken', 'vorgabe': 'aus', 'an': 'an', 'aus': 'aus',
         'hinweis': 'Angehakt: Der Schritt „Pose“ findet die Gelenke der Person am vorbereiteten Foto (SAM 3D Body), legt sie ins Netz und leitet daraus den Maßstab ab; die Körper-Kette nimmt beides statt '
                    'der Erkennung am Netz. Gedacht für Gemälde und freie Posen (liegend, sitzend), an denen die Erkennung am Netz nichts findet. Ohne Häkchen entfällt der Schritt im vollen Lauf '
                    '(über „Pose rechnen“ läuft er trotzdem) und die Körper-Kette arbeitet wie bisher.'},
        {'schluessel': 'drehung', 'titel': 'Drehung des Fotos für SAM 3D Body', 'art': 'wahl', 'vorgabe': '0', 'werte': [
            ('0', '0° — die Person steht aufrecht im Foto (Vorgabe)'),
            ('90', '90° gegen den Uhrzeigersinn'),
            ('180', '180°'),
            ('270', '270° gegen den Uhrzeigersinn'),
        ], 'hinweis': 'SAM 3D Body erwartet eine aufrechte Person. Liegt sie im Foto, wählt man die Drehung, die sie aufstellt — die Karte zeigt alle vier Drehungen mit den gefundenen Gelenken. '
                      'Eine automatische Wahl gibt es nicht: an den vier Läufen der Probe (liegender Akt) trennte kein Maß die richtige Drehung von den falschen.'},
        {'schluessel': 'weglassen', 'titel': 'Diese Gelenke nicht verwenden', 'art': 'mehrfach', 'vorgabe': [], 'werte': list(GELENKE),
         'hinweis': 'Verdeckte Gliedmaßen schätzt SAM 3D Body — am Gemälde „Modigliani“ hing der verdeckte linke Arm vor dem Bauch, im Bild liegt er hinter dem Kopf. Ein angehaktes Gelenk fällt aus den '
                    'Landmarken; der Arm ist dann frei und wird nur von der Fläche des Netzes gehalten.'},
        {'schluessel': 'masstab', 'titel': 'Maßstab aus der Pose (statt Einheitenregel)', 'art': 'haken', 'vorgabe': 'an', 'an': 'an', 'aus': 'aus',
         'hinweis': 'Angehakt: Das Netz wird mit dem Faktor aus der Pose in Meter umgerechnet (Meter je Pixel nach SAM 3D Body × Pixel je Netzeinheit). Aus: die Einheitenregel der Körper-Kette (längste Achse '
                    'über 3 gilt als Zentimeter) — sie hält ein liegendes Netz von 3,6 Einheiten für 3,6 cm.'},
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: (list(e['vorgabe']) if isinstance(e['vorgabe'], list) else e['vorgabe']) for e in cls.KATALOG}

    @staticmethod
    def _erlaubt(eintrag):
        """Die Werte, die ein Feld annehmen darf: bei einem Häkchen `aus` und `an`, sonst die Liste."""
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
        """Nur bekannte Schlüssel mit erlaubten Werten — der Rest wird Vorgabe; `weglassen` behält nur bekannte Gelenke, in der Reihenfolge des Katalogs."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['art'] == 'mehrfach':
                if isinstance(wert, list):
                    aus[e['schluessel']] = [w for w in cls._erlaubt(e) if w in wert]
            elif str(wert) in cls._erlaubt(e):
                aus[e['schluessel']] = str(wert)
        return aus
