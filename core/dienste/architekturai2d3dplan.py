# -*- coding: utf-8 -*-
"""Architekturai2d3dplan — Entscheidungen, Reihenfolge, Vorgabe „alles im Speicher und auf der GPU“ und offene Fragen von 2d-3d-AI (24.10.2026), für Hilfe → Architektur → 2d-3d-AI.

Die Entscheidungen sind Edgars Antworten vom 24.10.2026 auf die fünf Fragen des Plans; die Reihenfolge folgt seinen Projektregeln („erst EIN Modell“, „erst die Prüfung, dann der Fix“).
"""

__all__ = ['Architekturai2d3dplan']


class Architekturai2d3dplan:
    ENTSCHEIDUNGEN = (
        ('Eingabe', 'Exporte der Charakter-Seite (mit Wahrheit) UND echte Fotos (Randy, Ed 2026, Zauberer).'),
        ('Weg', 'B (Fotos direkt → KI → Genesis) ist das Ziel; A (Fotos → Hunyuan/Tripo → Mesh3D-AI → Genesis) bleibt die Messlatte.'),
        ('Anpassen beim Rechnen', 'erlaubt: nach der KI wird die Figur noch an die EINGABEFOTOS angepasst — nie an einer Wahrheit.'),
        ('Kleider', 'zuerst Katalogstück + Farbe; „genau so aussehen“ gilt für den Körper.'),
        ('Oberfläche', 'Jobseite mit Fotos · Netz · Genesis-Modell · Ergebnis, Ansichtsarten und Kleider wie bei Mesh3D-AI; Zeilen Gesicht, Hände, Kleider später.'),
        ('Speicher', '„alles, aber wirklich alles in der Pipeline soll im RAM und auf GPU laufen“ — keine Zwischendateien, ein Prozess; auf die Platte nur das Ergebnis.'),
    )
    #: (Nr, Schritt, Inhalt, Stand)
    SCHRITTE = (
        (1, 'Prüfung', 'Vergleich Rendering ↔ Foto aus allen Perspektiven, Gegenprobe mit der Wahrheit', 'gebaut 24.10.2026 (Jobseite, im Browser), Gegenprobe 97,9 % / 98,5 %'),
        (2, 'Messlatte A', 'heutiges Ergebnis von Mesh3D-AI (Tripo-Netz → KI) an den sechs Exporten messen', 'OlesiaWalk gemessen (86,8 %), die übrigen fünf zeigt die Seite, nicht festgehalten'),
        (3, 'Prüfung auf der GPU', 'dieselbe Messung in torch + nvdiffrast im selben Prozess wie das Training (die Browser-Messung bleibt die Anzeige)', 'nicht gebaut'),
        (4, 'Genesis auf der GPU', 'Formregler → Punkte (Wirkung linear), Winkel → Skelett → Häutung, Kleider anziehen — differenzierbar, in python10', 'Bausteine da, als Ganzes nicht geprüft'),
        (5, 'Datengenerator im Speicher', 'Figuren × Kleider × Posen zufällig, vier Renderings je Probe direkt in den Trainingsstapel (keine Bilddateien)', 'nicht gebaut'),
        (6, 'Ein Modell', 'Training und Anpassung zuerst an EINEM Job (OlesiaWalk), zeigen, dann erst die übrigen', 'nicht gebaut'),
        (7, 'Echte Fotos', 'Maske (Sapiens2), Kamerakopf, Licht; Randy, Ed 2026, Zauberer', 'nicht gebaut'),
    )
    #: Was im Speicher und auf der GPU läuft — und was dafür fehlt.
    GPU = (
        ('Fotos', 'einmal von der Platte gelesen, dann als Tensor auf der Karte (Exporte 4 × 512 × 384, echte Fotos bis 8)'),
        ('Rückgrat', 'Sapiens2-0.4B in python10, gemessen 09.10.2026: 0,23–0,33 s je kleinem Foto, Spitze 2,73 GB'),
        ('Trainingsdaten', 'vom Generator auf der Karte gerendert und sofort verbraucht — nicht als JPG/NPZ abgelegt (bei Mesh3D-AI lagen Bilder, Netze und Wolken als Dateien)'),
        ('Genesis 9', 'Formwirkung, Vorwärtskinematik, Häutung in torch; heute gibt es dafür Bausteine (`G9rechenkarte`, Formwirkung `formregler_wirkung_v6.npz`, Winkelanpassung als CUDA-Graph)'),
        ('Rendern und Vergleichen', 'nvdiffrast 0.4.0 im selben Prozess; der Verlust geht zurück durch Rendering, Genesis und Netz'),
        ('Hunyuan / Tripo', 'NICHT in diesem Prozess: Hunyuan3D-2mv läuft in einer eigenen Umgebung, Tripo ist ein Dienst — darum bleibt Weg A Messlatte und gehört nicht in die Schleife'),
    )
    OFFEN = (
        'Breite der Merkmale von Sapiens2-0.4B — für die Rechnung auf 1.024 gesetzt, nicht nachgelesen.',
        'Ob eine differenzierbare Genesis-Figur mit allen Kleidern in den Grafikspeicher passt (Batch, vier Ansichten) — nicht gemessen.',
        'Licht: die Jobseite rendert mit dem Licht der Felder, nicht mit dem der Charakter-Szene — der Farbabstand ist deshalb auch bei der Wahrheit 37–61 / 255 und taugt noch nicht als Maß.',
        'Netzstufe: die Seite zeigt die Figur grob (schnelle Anzeige wie Mesh3D-AI), die Exporte sind fein — ein Teil der fehlenden 2 % der Gegenprobe; nicht getrennt gemessen.',
        'Die Umriss-Deckung passt die Größe mit ein (Kamera auf die Hülle der gezeigten Figur) — ein Fehler in der Körpergröße fällt hier nicht auf; dafür braucht es den Vergleich mit fester Kamera.',
        'Echte Fotos: Winkel nach Augenschein in den job.json (Zauberer: fünf von acht unbekannt), Kamera und Licht unbekannt.',
    )
