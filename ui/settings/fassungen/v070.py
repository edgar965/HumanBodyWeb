# -*- coding: utf-8 -*-
"""Fassung 0.70 (17.10.2026) — Mesh3D-AI (Netz → Genesis-Skelett und Form, mit Vorstufe Rig → A-Pose), Mesh-3D mit Gelenkkorrekturen, Genesis 9 mit allen Reglern, „Alter“ und den Morph-Familien."""

FASSUNG = {
    'version': '0.70',
    'date': '2026-10-17',
    'title': 'Mesh3D-AI: eine KI macht aus einem Netz Skelett und Form, zuerst gerigt und in die A-Pose gebracht; Mesh-3D mit '
    'Gelenkkorrekturen und Bestandteilen; Genesis 9 mit allen Reglern, Sammelregler „Alter“ und den Morphs aus HumanBody, '
    'MakeHuman, SMPL-X und UMA',
    'author': 'edgar965',
    'body_md': (
        '- **Mesh3D-AI** (Dashboard → Mesh3D-AI): Training einer KI „Netz → Genesis-Modell“ — Tabelle der Jobs, Seite je Job '
        'mit Start · Ziel · Ergebnis in fünf Zeilen (ganzer Körper, nur Körper, Gesicht, Hände/Füße, Kleider), acht '
        'Ansichtsarten, Rig, Animation, Tabelle „Wie gut?“ unter jedem Ergebnis, gemerkte Ansicht (Ansichtsart, Rig, Probe, '
        'Weg, Filter). Jobs Ursula1, Damira0, Mann1, Matt0, dazu die Prüfposen-Jobs UrsulaSpagat, DamiraSitzen, MattLiegen, '
        'MannLaufen und der Reiter „Test“ mit fremden Netzen.\n'
        '- **Netz**: Stimmen je Punkt für 138 Gelenke, Ausgabe als Daz-Winkel in den Grenzen von Genesis 9 (keine '
        'gebrochenen Finger mehr), Formkopf für die Genesis-Formregler (Fassung 3: 1.318 Regler mit den Morph-Familien), '
        '80 Formvarianten als Trainingskörper.\n'
        '- **Vorstufe vor dem Netz**: ein Netz wird zuerst gerigt (Mesh-3D „Nur Rig“, einmal je Netzdatei) und mit dem Rig '
        'in die A-Pose zurückgerechnet; ein eigenes Netz korrigiert dort die Gelenke, das Rig bringt sie zurück in die '
        'Haltung. Am Spagat: Netz direkt 280,5 mm, über die A-Pose 12,6 mm. Viertes Feld „Rig → A-Pose“ auf der Jobseite, '
        'Eingabe mit Textur, Löcher der Außenfläche sichtbar. Der Formkopf lernt auch auf der A-Pose-Wolke (Vergleich '
        'auf der Hilfeseite).\n'
        '- **Hilfe → Architektur → Mesh3DAI**: Netz Schicht für Schicht mit Grafik, Vorstufe, Form, Testnetze, Daz-Winkel, '
        'Plan, Vorgehen, Kleider; „So laufen Training und Erkennung“.\n'
        '- **Mesh to 3D**: Füße aus der Tiefe der SAM-Gelenke entlang der Kette (das Rig setzte die Füße beim Sitzen und '
        'Laufen über 10 cm daneben); Umfang „Nur Rig“ (Schritt „figur“ 31–37 s statt 361 s).\n'
        '- **Mesh-3D**: Gelenkkorrekturen (JCM) in der Animation wie im Studio, Farben je Punkt, Bestandteile über '
        'Textbegriffe (SAM 3), Haltung des Netzes, Hautgewichte für Robe, Hut, Bart, Stab; Prüfreihe der Testaufträge; '
        'Netz bearbeiten mit Bereich per Hover; Reiter „Testaufträge“.\n'
        '- **Modellverwaltung**: kein Lauf speichert ein Modell von selbst (Knopf „Als Modell speichern“), Ordner, '
        'Mehrfachauswahl, Verschieben und Löschen; Reiter „Posen“ mit Ordnerbaum.\n'
        '- **Genesis 9**: alle Regler im Bedienfeld und im Katalog (Zähne, Augen, verborgene Daz-Abschnitte), Sammelregler '
        '„Alter“ und Lebensalter, die Morph-Familien `hb:` (HumanBody), `mh:` (MakeHuman), `sx:` (SMPL-X) und `uma:` (UMA) '
        'als Genesis-Morphs, deren Skelett mitgeht.\n'
    ),
}
