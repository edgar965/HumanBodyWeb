# -*- coding: utf-8 -*-
"""Engine2d3dKleiderqualitaet — die Handwertung „Qualität …" in der Liste von „2D3D Kleider" (03.10.2026).

Edgar: „mach eine Spalte mit der Qualität des Meshes, und Qualität 3D, die ich aber manuell verändern kann" — später: „die qualität soll
eindeutig sein, also keine zwei Läufe mit gleicher Qualität. Beste Qualität: 1. falls eine Zahl dazwischenkommt, ändere die Qualitäten
anderer Läufe" und „Qualität Textur, Mesh insgesamt, Kleider, Haar, Gesicht, Körper — ALS NEUE SPALTEN".

Acht Spalten, je ein Auswahlfeld direkt in der Zeile: „–" (nicht bewertet) und der RANG 1, 2, 3 … — 1 ist der beste Lauf, jeder Rang kommt je
Spalte höchstens einmal vor. Wer einem Lauf einen Rang gibt, den schon ein anderer trägt, schiebt die anderen nach hinten
(`Engine2d3dKleiderrang`). Gespeichert wird sofort, ohne Neuberechnung — es ist eine Kennzeichnung, kein Wert, der in einen Lauf eingeht,
deshalb auch während eines Laufs. Jede Spalte ist eine eigene Rangliste: „Qualität Haar" 1 hat nichts mit „Qualität Körper" 1 zu tun.

    mesh         die Güte des Netzes aus den Fotos (Schritt „netz")
    3d           die Güte der 3D-Figur als Ganzes (Körper, Kleider, Haar)
    textur       die Textur der Figur
    mesh_gesamt  das Mesh insgesamt
    kleider      die Kleider
    haar         das Haar
    gesicht      das Gesicht
    koerper      der Körper

Die Werte stehen in eigenen Spalten des Auftrags (`Engine2d3dKleiderauftrag.qualitaet_*`), nicht in `optionen` oder `ergebnis`: Ein Lauf
schreibt beide JSON-Felder aus dem Speicher zurück und überschriebe eine Wertung, die währenddessen gesetzt wurde. Ein Duplikat bekommt keine
Wertung (`Auftragsduplikat.parameter` kopiert nur Name, Optionen und Bilder).
"""

__all__ = ['Engine2d3dKleiderqualitaet']


class Engine2d3dKleiderqualitaet:
    #: Schlüssel der Anfrage → (Spalte des Auftrags, Überschrift der Liste, Frage im Tooltip) — in der Reihenfolge der Spalten der Liste.
    FELDER = {
        'mesh': ('qualitaet_mesh', 'Qualität Mesh', 'Wie gut ist das Netz aus den Fotos?'),
        '3d': ('qualitaet_3d', 'Qualität 3D', 'Wie gut ist die 3D-Figur mit Kleidern und Haar?'),
        'textur': ('qualitaet_textur', 'Qualität Textur', 'Wie gut ist die Textur?'),
        'mesh_gesamt': ('qualitaet_mesh_gesamt', 'Qualität Mesh insgesamt', 'Wie gut ist das Mesh insgesamt?'),
        'kleider': ('qualitaet_kleider', 'Qualität Kleider', 'Wie gut sind die Kleider?'),
        'haar': ('qualitaet_haar', 'Qualität Haar', 'Wie gut ist das Haar?'),
        'gesicht': ('qualitaet_gesicht', 'Qualität Gesicht', 'Wie gut ist das Gesicht?'),
        'koerper': ('qualitaet_koerper', 'Qualität Körper', 'Wie gut ist der Körper?'),
    }
    #: Steht in `data-sort` einer Zelle ohne Rang: „nicht bewertet" sortiert ans Ende, nicht vor Rang 1.
    SORT_OHNE_RANG = 999999

    @classmethod
    def spalte(cls, schluessel):
        """Die Spalte des Auftrags zu einem Schlüssel der Anfrage — `None` bei einem unbekannten."""
        eintrag = cls.FELDER.get(schluessel)
        return eintrag[0] if eintrag else None

    @classmethod
    def normieren(cls, wert):
        """Ein Rang aus einer Anfrage: ganze Zahl ab 1, oder `None` für „nicht bewertet" (0, leer, `null`). Alles andere (Text, Bruch, negativ,
        `True`) wirft `ValueError` — eine stille Rundung würde etwas speichern, was niemand gewählt hat. Eine obere Grenze gibt es nicht: Sie hängt
        an der Zahl der bewerteten Läufe und wird beim Einordnen angewandt (`Engine2d3dKleiderrang.umordnen`)."""
        if wert is None or wert == '' or wert == 0 or wert == '0':
            return None
        if isinstance(wert, bool):
            raise ValueError('Kein Rang: %r' % (wert,))
        try:
            zahl = float(wert)
        except (TypeError, ValueError) as fehler:
            raise ValueError('Kein Rang: %r' % (wert,)) from fehler
        if zahl != int(zahl) or int(zahl) < 1:
            raise ValueError('Der Rang muss eine ganze Zahl ab 1 sein: %r' % (wert,))
        return int(zahl)

    @classmethod
    def kopftitel(cls, schluessel):
        """Tooltip der Überschrift: was die Spalte meint und wie der Rang zählt."""
        return '%s Rang 1 = der beste Lauf, jeder Rang nur einmal; ein vergebener Rang schiebt die anderen nach hinten (von Hand gesetzt).' % cls.FELDER[schluessel][2]

    @classmethod
    def titel(cls, schluessel, rang):
        """Tooltip der Zelle: der Kopftitel und der Rang des Laufs (`engine2d3dkleiderqualitaet.js` hängt denselben Satz nach jeder Änderung an)."""
        return '%s — jetzt: %s' % (cls.kopftitel(schluessel), 'nicht bewertet' if not rang else 'Rang %d' % rang)
