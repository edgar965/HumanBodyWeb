# -*- coding: utf-8 -*-
"""Rechercheabschnitte — die drei Tabellen der Seite „Recherche → Human 3D" und ihre Spalten (09.10.2026).

Edgar: „baue die Tabelle um — die Teile, die wir eingebaut haben oder die sich nicht lohnen (weil veraltet oder schlecht), bitte in getrennte Tabellen unten: neue Tabelle eingebaut, neue Tabelle
veraltet/lohnt sich nicht". Welches Projekt in welche Tabelle gehört, sagt `Rechercheurteile`; hier steht nur, WELCHE SPALTEN jede Tabelle führt. Die erste Tabelle behält ihren
Speicher-Schlüssel (`hilfe-recherche-human3d`): Edgars gezogene Spaltenbreiten und die Sortierung bleiben erhalten (djangoBase merkt sie je Schlüssel und Spalte).
"""

from .rechercheurteile import Rechercheurteile

__all__ = ['Rechercheabschnitte']


class Rechercheabschnitte:
    #: Spalte → (Beschriftung, rechtsbündig, Sortierung aus, Hinweis). Die Reihenfolge je Tabelle steht in `PLAN`.
    SPALTEN = {
        'name': ('Name', False, False, 'Name des Projekts'),
        'prio': ('Prio', True, False, 'Deine Reihenfolge: ob wir das testen oder einbauen (1 = zuerst). Jede Zahl nur einmal — eine vergebene Zahl schiebt die anderen nach hinten'),
        'kategorie': ('Kategorie', False, False, 'Kategorie des Projekts (die Liste darüber zählt sie) — ein Klick auf den Spaltenkopf sortiert danach'),
        'einschaetzung': ('Einschätzung', False, False, 'Urteil vom 09.10.2026: Verbesserung (macht Vorhandenes besser), Beobachten (unreif oder unklar), Neues Feature (hätten wir nicht) — Klick öffnet die Begründung'),
        'eingebaut_als': ('Eingebaut als', False, False, 'Wo das Projekt in unserem Code steckt — Klick öffnet das Fenster'),
        'urteil': ('Urteil', False, False, 'Veraltet (überholt, nicht mehr gepflegt) oder lohnt sich nicht (unpassend, nicht nutzbar)'),
        'grund': ('Grund', False, False, 'Woran das Urteil hängt — aus README und Eckdaten, nicht ausprobiert. Klick öffnet das Fenster'),
        'kurz': ('Kurzbeschreibung', False, False, 'Ein Satz: was das Projekt tut'),
        'github': ('GitHub', False, False, 'Repository auf GitHub (öffnet in neuem Tab)'),
        'hf': ('Hugging Face', False, False, 'Demo (Space), Modell und Datensatz des Projekts bei Hugging Face — aus dem README, über die HF-Schnittstelle geprüft; Likes im Hinweis'),
        'bild': ('Hauptbild', False, True, 'Ein aussagekräftiges Bild aus dem Projekt (verkleinerte lokale Kopie) — ein Klick öffnet es groß'),
        'sterne': ('Sterne bei GitHub', True, False, 'Sterne laut GitHub-Abfrage am Stand der Seite'),
        'aktualisiert': ('Letzte Aktualisierung', False, False, 'Letzter Push ins Repository (GitHub „pushed_at“)'),
        'beschreibung': ('Beschreibung', False, False, 'Was es tut und wie'),
        'details': ('Details', False, True, 'Eingabe, Ausgabe, Modelle, Lizenz, Besonderheiten'),
        'todo': ('ToDo', False, False, 'Was wir im Projekt nicht haben — Klick öffnet ein Fenster mit mehr Infos und Bildern'),
    }

    #: Abschnitt → Speicher-Schlüssel der Tabelle, Spaltenfolge, Text bei leerer Tabelle.
    PLAN = {
        Rechercheurteile.OFFEN: {
            'key': 'hilfe-recherche-human3d',
            'spalten': ('name', 'prio', 'kategorie', 'einschaetzung', 'kurz', 'github', 'hf', 'bild', 'sterne', 'aktualisiert', 'beschreibung', 'details', 'todo'),
            'leer': 'Keine offenen Projekte — die Datei core/daten/recherche_human3d.json fehlt oder alle sind eingebaut oder abgelegt.',
        },
        Rechercheurteile.EINGEBAUT: {
            'key': 'hilfe-recherche-human3d-eingebaut',
            'spalten': ('name', 'kategorie', 'eingebaut_als', 'kurz', 'github', 'hf', 'bild', 'sterne', 'aktualisiert', 'beschreibung', 'details'),
            'leer': 'Noch nichts als eingebaut eingestuft.',
        },
        Rechercheurteile.ABGELEGT: {
            'key': 'hilfe-recherche-human3d-abgelegt',
            'spalten': ('name', 'kategorie', 'urteil', 'grund', 'kurz', 'github', 'hf', 'bild', 'sterne', 'aktualisiert', 'beschreibung', 'details'),
            'leer': 'Nichts als veraltet oder nicht lohnend eingestuft.',
        },
    }

    @classmethod
    def plan(cls, abschnitt):
        """Der Plan eines Abschnitts; ein unbekannter Name ist ein Fehler im Aufrufer, kein Grund für eine stille Vorgabe."""
        return cls.PLAN[abschnitt]

    @classmethod
    def kopf(cls, abschnitt):
        """Die Spaltenköpfe für `djangobase/_tabelle.html`."""
        kopf = []
        for key in cls.plan(abschnitt)['spalten']:
            label, num, sort_aus, titel = cls.SPALTEN[key]
            kopf.append({'label': label, 'key': key, 'num': num, 'sortAus': sort_aus, 'titel': titel})
        return kopf
