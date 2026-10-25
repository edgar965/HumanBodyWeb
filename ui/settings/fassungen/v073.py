# -*- coding: utf-8 -*-
"""Fassung 0.73 (25.10.2026) — Mesh3D-AI rechnet per Knopf (Kette im Projekt, Kostüm-Prüfung, Kopf-, Lage- und Körper-Schritt, Haut-KI im Bildraum mit einstellbarer Entlichtung); 2d-3d-AI aus Fotos."""

FASSUNG = {
    'version': '0.73',
    'date': '2026-10-25',
    'title': 'Mesh3D-AI rechnet per Knopf: Kleider und Haar aus der KI, Kostüm-Prüfung, Kopf-, Lage- und Körper-Schritt, '
    'Haut-KI im Bildraum mit einstellbarer Entlichtung; 2d-3d-AI: Genesis-Modell aus Fotos',
    'author': 'edgar965',
    'body_md': (
        '- **Mesh3D-AI – Rechnen per Knopf**: Netz hochladen, „Rechnen“, Fortschritt sehen; Warteschlange, Papierkorb, '
        'KI-Fassungen in einer Datei. Der Rechencode liegt im Projekt (`mesh3dai/`) und läuft ganz in python14, '
        'mit Skriptdienst, MIA-Nachbau (bitgleich zum Original) und MediaPipe, Sapiens2 und SAM 3 auf der Grafikkarte.\n'
        '- **Mesh3D-AI – Kleider und Haar aus der KI**: Zerlegungskopf, Schichtkopf und der Kostüm-Weg (Stücke aus dem '
        'Netz erkennen und ausschneiden, auf die KI-Figur legen).\n'
        '- **Mesh3D-AI – Kostüm-Prüfung** mit Testfällen und Prioritäten: Haltung, Flecken und Zeichnung der Haut, Naht, '
        'Gesicht und Kopfform wie der Eingang, Durchsicht, Glieder und Knochenlängen, Blickrichtung, Haut durch Stück '
        'im Tanz, Hautton und Entlichtung.\n'
        '- **Mesh3D-AI – neue Schritte**: „kopf“ (Kopfregler an das Netz), „lage“ (Gelenke in die Bilderkennung), '
        '„koerper“ (Körper in die Außenmaße des Netzes, mit der Lage des Gesichts).\n'
        '- **Haut-KI im Bildraum**: Haut wechselt im Training, kein Saum am Inselrand, Ton aus dem Eingang (Versuch); '
        'Einstellungen → 2d-3d-AI → „Entlichtung der Haut (%)“, Vorgabe 100 %.\n'
        '- **2d-3d-AI**: Genesis-Modell aus Fotos — Liste, Jobseite, Hilfe → Architektur, Einstellungen; gemeinsamer '
        'Code mit Mesh3D-AI in `KoerperKI_alle/`.\n'
        '- **GarmentCode und Genesis 9**: Drapierung schneller, Schnitt aus der Fläche, Ärmelwinkel; Genesis 9 auf der '
        'Grafikkarte (Morphsumme, Oberflächenbindung).\n'
    ),
}
