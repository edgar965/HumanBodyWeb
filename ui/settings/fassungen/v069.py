# -*- coding: utf-8 -*-
"""Fassung 0.69 (12.10.2026) — Mesh-3D (Netz → Genesis-Modell), Mesh to 3D mit Größe aus den Gelenken und viel schneller, Blend-Import, eindeutige Meldung bei unerreichbarem Server."""

FASSUNG = {
    'version': '0.69',
    'date': '2026-10-12',
    'title': 'Mesh-3D: ein Netz wird zum Genesis-Modell (neue Seite mit Jobs); Mesh to 3D: Größe aus den Gelenken und '
    'deutlich schneller; Blend-Import: Finger, Maßstab, Haut ohne Blender; klare Meldung, wenn der Server nicht antwortet',
    'author': 'edgar965',
    'body_md': (
        '- **Mesh-3D** (Dashboard → Mesh-3D): Ein Netz (blend, glb, obj, fbx) wird als Auftrag zum Genesis-Modell. '
        'Zwei Wege: „teile" (die Blender-Kette) und „netz" (eine verschmolzene GLB, „Mesh to 3D" auf dem ganzen Netz). '
        'Schritt „Pose" (SAM 3D Body am Rendering) und Schritt „Segmentierung" (Sapiens2, Hautton aus Gesicht und '
        'Händen statt aus der Robe). Die Jobseite öffnet schnell (Vorschau statt 67-MB-Netz), bietet Kopie mit und ohne '
        'Daten, Upload von Dateien und Ordnern, Quelle ändern und Umbenennen. Beide 3D-Ansichten lassen sich in Höhe '
        'und Breite einstellen (Regler oder Ziehgriff; „volle Breite" ist die Vorgabe).\n'
        '- **Mesh to 3D, Größe**: Die Figur war 18 cm zu klein und stand auf Zehenspitzen, weil die Größenregler '
        'nie frei waren. Neu: ein Maßterm aus den Segmentlängen der Gelenke, die SAM-Tiefe aus der Mitte der Dicke '
        'statt dem Median, eine SAM-Kalibrierung (`manage.py sam_kalibrieren`) und vier Regionen-Regler (Oberarm, '
        'Schulterpartie, Taille, Hüfte; Vorgabe aus). Am Auftrag „Edgar" sank der Gelenkrest von 61–190 auf 3–16 mm.\n'
        '- **Mesh to 3D, Tempo**: Textur-Suche auf der GPU (Schritt 822 → 302 s), Netz einmal ablegen (11,3 → 0,7 s), '
        'Proben und Hautkarte einmal rechnen, Anpassungsschritt als CUDA-Graph (104 → 16 ms), ein Runner-Prozess für '
        'alle Schritte. Ganzer Import „netz" 762 → 321 s. Ein Modell im Charakter lädt schneller (Antwortvorrat '
        'trägt die Fassung als Inhalts-Hash statt der Änderungszeit).\n'
        '- **2D3D Kleider**: Schritt „Pose" (SAM 3D Body findet die Gelenke am Foto, Maßstab und Landmarken für die '
        'Körper-Kette).\n'
        '- **Blend-Import**: Finger- und Handanpassung mit Griff fürs Requisit (Katana), Maßstab nach der Gesamthöhe, '
        'Unterkleid-Regler gegen Haut in der Hose, Haut backen ohne Blender (Einstellungen → Charakter → Backen: Lokal '
        'oder Blender, Rechnung auf der GPU), Daz-Geograft und Scham-Messung, Import abbrechen und löschen.\n'
        '- **Genesis 9**: Anatomie-Stücke als eigene Klassen (Penis, Vagina, Anus), Formregler bis ×2, Material-Popup '
        'je Teil, Retarget mit Haltungsbezug und Hüftverankerung.\n'
        '- **Server nicht erreichbar**: Statt „Failed to fetch" oder „500 … <html>" meldet jede Seite jetzt in einem '
        'deutschen Satz, dass der Server nicht antwortet (mit Adresse und Hinweis auf den Neustart), bzw. dass der '
        'Server einen Fehler hatte (mit Verweis auf Hilfe → Logs → Exceptions).\n'
        '- **Hilfe**: Architektur → MeshTo3D (Klassen, Optionen, Zeiten) und Recherche (Human 3D, Modelle Internet) '
        'nachgezogen.\n'
    ),
}
