# -*- coding: utf-8 -*-
"""Fassung 0.67 (05.10.2026) — 2D3D Kleider ausgebaut, Garderobe pflegen, Genesis-Kleid bleibt."""

FASSUNG = {
    'version': '0.67',
    'date': '2026-10-05',
    'title': '2D3D Kleider: Vorbereitung, Segmentierung, Kleiderstücke und Nachbesserung mit KI; '
    'Garderobe: Umbenennen, Löschen und Icons; Genesis-Modelle behalten ihr GarmentCode-Kleid',
    'author': 'edgar965',
    'body_md': (
        '- **2D3D Kleider**: Die Schritte Vorbereitung (Zuschnitt, Körper senkrecht stellen über '
        'die Mittelachse) und Segmentierung (Sapiens, alle 28 Klassen und 12 Einstellungen in der '
        'Oberfläche) laufen einzeln startbar vor dem Netz. Der Schritt „Kleiderstücke“ baut Oberteil, '
        'Hose und Socken aus dem Netz als Genesis-Stücke und misst sie; die Bühne trägt sie schon '
        'vor Runde 1. Netzansicht auf der Bühne auch für Aufträge ohne Körperkette; Netz an die '
        'Silhouette des Seitenfotos angleichen (Netztiefe).\n'
        '- **Nachbesserungen mit KI**: Block unten auf jeder Auftragsseite (Wahl der KI lokal oder '
        'remote, Stufe, Anzahl der Iterationen); je Iteration sieht die KI Vorlage und letzte Runde '
        'und schreibt Rezept und Kommentar, der Server rechnet die Runde. Reiter „Bewertung“, '
        'Qualitätsrang je Spalte, Kopie eines Auftrags mit oder ohne Daten.\n'
        '- **Iterationen und Render**: Automatische Iterationen mit Befundmessung, Texturschichten '
        '(Foto, Decal, Falten), Blender-Haarknoten, Drapieren mit Newton statt Blender, Renderwahl '
        'Mitsuba oder pyrender, Rundenauswahl, Animationsexport. Jeder Auftrag rendert auch ohne '
        'eigenes Rezept ein Video (allgemeines Rezept). Das Haar der Vorlage wird als Genesis-Frisur '
        'umgebaut (Haarlinie, Hülle, Haarkappe, gemessene Haarfarbe).\n'
        '- **Fotobacken**: Die Achsentabelle spiegelte den Körper links/rechts — die Fotos lagen '
        'vertauscht auf dem Körper. Pixal3D läuft im GPU-Modus ohne Arbeitsspeicher (Pixal-Prozess '
        '130 s statt etwa 303 s), Fäden im Rohnetz werden entfernt; TRELLIS.2 mit allen zwölf '
        'Sampler-Reglern im Abschnitt „Mesh“.\n'
        '- **Garderobe (Genesis 9)**: Im Kontextmenü „Umbenennen …“ und „Löschen …“ (Umbenennen ändert '
        'nur den Anzeigenamen; ein eigenes Stück geht in einen Papierkorb, ein Daz-Stück wird '
        'ausgeblendet). Eigene Stücke bekommen ein gerendertes Icon; ihr Zubehör steht unter '
        '„Requisiten“. Kleidung – Generisch ohne Stückgrenze.\n'
        '- **Hilfe → Recherche → Human 3D**: 1.043 GitHub-Projekte als Tabelle mit Hauptbild, '
        'Prio-Spalte und ToDo-Fenster.\n'
        '- **Figurfilm**: Film aus Genesis 9 mit Stoff, Haar und Zubehör, Hände, Mimik-Regler, '
        'Standfilm.\n'
        '- **Behoben**: Damira1 und jedes andere Genesis-Modell zeigte nach dem Speichern auf den '
        'geteilten Arbeitsordner `kleid_genesis9`, den jeder Genesis-Kleidbau neu schreibt — am '
        '30.09. ersetzte ein Bau für eine 172-cm-Figur Damiras Babydoll (167 cm). Das Speichern '
        'kopiert die GarmentCode-Stücke eines Genesis-Modells jetzt in einen eigenen Szenenordner, '
        'wie es für HumanBody-Szenen schon galt. Ein vorher gespeichertes Modell braucht dafür '
        'einmal Speichern.\n'
    ),
}
