# -*- coding: utf-8 -*-
"""Engine2d3dKleidersegmentierungsoptionen — die Gruppe `segmentierung` der Optionen von „2D3D Kleider" (04.10.2026).

Der Schritt „Segmentierung" (`Engine2d3dKleidersegmentierung`) steht nach dem Netz und ist OPTIONAL (Edgar, 04.10.2026: „baue das ein in den 2d3dKleider jobs — optional nach der Mesh
erzeugung"). Eine Option: `verwenden`. Sie hat zwei Wirkungen, die zusammengehören:

- „an": Der Schritt läuft im vollen Lauf mit (Sapiens-Segmentierung der vorbereiteten Fotos, 6–15 s, 5,9 GB Grafikspeicher; beim ersten Mal lädt er 4,7 GB Gewichte), und der Schritt
  „kleidung" der Körper-Kette (`Meshfigurkleidung`) nimmt die Etiketten statt Farbe und Lage für die Kleidungsmaske.
- „aus" (Vorgabe): Der Schritt wird im vollen Lauf übersprungen und die Maske bleibt, wie sie war. Ausdrücklich gestartet („Segmentierung starten" oder „ab Segmentierung") läuft er immer —
  die Überlagerungen zeigen dann, was Sapiens in den Fotos sieht, ohne dass die Kleidung davon abhängt.
"""

__all__ = ['Engine2d3dKleidersegmentierungsoptionen']


class Engine2d3dKleidersegmentierungsoptionen:
    KATALOG = [
        {'schluessel': 'verwenden', 'titel': 'Kleidung aus der Segmentierung (Sapiens)', 'art': 'wahl', 'vorgabe': 'aus', 'werte': [
            ('aus', 'Aus — Kleidung nach Farbe und Lage (Vorgabe)'),
            ('an', 'An — Sapiens zerlegt die Fotos, die Kleidungsmaske folgt den Etiketten'),
        ], 'hinweis': 'Sapiens (Meta, Körperteil-Modell 1B, nicht kommerziell: CC BY-NC 4.0) zerlegt jedes vorbereitete Foto in Oberteil, Hose, Socken/Schuhe, Zubehör und Haut; die Etiketten '
                      'werden mit derselben Projektion wie die Fotofarbe auf die Flächen des Netzes gelegt, verdeckte Flächen stimmen nicht ab. Wo kein Foto hinsieht (Innenseiten, Schritt, '
                      'Achseln), gilt weiter die Regel nach Farbe und Lage. Gemessen im Probelauf an Edgars Fotos (04.10.2026): die Regel hatte Ärmel 2–4 cm zu kurz und Socken 3–9 cm zu '
                      'niedrig, Hosensaum und Shirt/Shorts-Grenze stimmten innerhalb ± 2 cm; Ende zu Ende, bis zum Fotostück, ist es nicht gemessen. Die Maske wirkt erst, wenn der Schritt '
                      '„Körper“ mit Quelle „rechnen“ danach läuft (übernommene Körper haben keine eigene Maske). Beim ersten Lauf lädt der Schritt 4,7 GB Gewichte.'},
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

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
            if wert is not None and str(wert) in [w for w, _ in e['werte']]:
                aus[e['schluessel']] = str(wert)
        return aus
