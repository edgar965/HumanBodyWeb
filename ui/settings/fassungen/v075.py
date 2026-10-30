# -*- coding: utf-8 -*-
"""Fassung 0.75 (30.10.2026) — Mesh3D-AI: Zeile 1 mit den Klassen der Kostüm-Erkennung (koenigin1 sieht aus wie der Eingang), Zeile 2 auf Zeile 1, Studio verlässt sich schneller."""

FASSUNG = {
    'version': '0.75',
    'date': '2026-10-30',
    'title': 'Mesh3D-AI: Zeile 1 mit den Klassen der Kostüm-Erkennung – koenigin1 sieht aus wie der Eingang; Zeile 2 baut auf Zeile 1 auf; '
    'Studio und Garderobe schneller',
    'author': 'edgar965',
    'body_md': (
        '- **Mesh3D-AI – Zeile 1 Fassung 7**: Haut, Haar und Kleidung des Ziels kommen aus der Kostüm-Erkennung statt aus der '
        'Zerlegungs-KI (bei koenigin1 nannte sie 79 % Haut statt 3 %). koenigin1 neu gerechnet: Prio 1 der Kostüm-Prüfung '
        '190 von 284 → 68 von 343, Umriss 4 → 0 von 4 rot, stärkste Gelenkdrehung 107° → 58°.\n'
        '- **Mesh3D-AI – neue Prüfung „Klassen des Ziels wie die Kostüm-Erkennung“** in Zeile 1; an allen sechs Kostüm-Tests '
        'gegengeprüft (alte Klassen alle rot, neue alle grün).\n'
        '- **Mesh3D-AI – Weg „rig“**: die Ruhegelenke werden in den Rahmen der Datei zurückgerechnet (mann_gold 1,844 m statt '
        '0,904 m); eine Kopfbedeckung gilt nie als anliegend.\n'
        '- **Mesh3D-AI – Zeile 2 baut auf Zeile 1 auf** (Fassung 6 an edgar: Prio 1 0 von 340), Rechenschlange mit Sperre, '
        'Kostüm-Prüfung Fassung 30, Hautmaske Fassung 3.\n'
        '- **Mesh3D-AI – Jobseite**: der Schalter „Kleider“ blendet auch das Haar aus; die Liste /mesh-3D-AI/ liest nur '
        'geänderte Ergebnisdateien neu (1,44 → 0,48 s).\n'
        '- **Studio**: lesende Abrufe enden beim Verlassen der Seite (`Seitenabbruch`), die nächste Seite wartet nicht mehr '
        'auf Retarget und Texturen; die Garderobe sucht ihre Stücke über einen sortierten Index.\n'
    ),
}
