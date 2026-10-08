# -*- coding: utf-8 -*-
"""Fassung 0.68 (09.10.2026) — Blender-Import (.blend → Genesis-Modell), Formregler über Dazʼ Grenze, Mesh to 3D und 2D3D Kleider."""

FASSUNG = {
    'version': '0.68',
    'date': '2026-10-09',
    'title': 'Blender-Import: .blend → Genesis-9-Modell mit Kleidern, Haar, Augen und gebackener Haut (auch ohne Skelett); '
    'Formregler bis ×2; Mesh to 3D und 2D3D Kleider: Kopf, Gesicht, Haltung, Herrenhaar; ruhigere Bedienung der Szene',
    'author': 'edgar965',
    'body_md': (
        '- **Blender-Import** (Datei → Modell importieren …): Eine .blend wird zum Genesis-9-Modell. Der Körper '
        'läuft über „Mesh to 3D"; Kleider und Haar kommen als eigene Stücke in die Garderobe, die Originalaugen '
        'als eigenes Objekt (die Genesis-Augen weichen), die Originalhaut wird auf die Genesis-Kacheln gebacken '
        '(bis 8192 px, Normalen gesäubert). Die Haltung bringt das Rig (Auto-Rig Pro) in die Genesis-Haltung. '
        'Fortschritt oben neben dem Titel, Einstellungen werden gemerkt, ein zweiter Import startet nicht neben '
        'einem laufenden. Neuer Regler für die Scham.\n'
        '- **Blender-Import ohne Skelett**: Auch eine .blend ganz ohne Armatur (Character-Creator-Export, '
        '„Beautiful Asian girl": 15 Netze, 3,26 m hoch, freie Pose) wird eingelesen. Die Rollen (Körper, Augen, '
        'Zähne, Haar, Kleider) ergeben sich aus Maßen, Material und Namen; zu große oder zu kleine Modelle '
        'werden auf 1,75 m gebracht, weil „Mesh to 3D" Längen über 3 als Zentimeter liest. Das Umposen entfällt, '
        'die Haltung schätzt „Mesh to 3D". Zwei Stücke derselben Art (zwei Socken) überschreiben sich nicht mehr.\n'
        '- **Genesis-Formregler über Dazʼ Grenze**: Regler mit Formdeltas gelten bis ×2 statt nur bis ±1, aber nur '
        'ausdrücklich gestellte Werte (Formeln bleiben bei Daz). Der Schieber zeigt Werte über 100 %; für die '
        'Anpassung gibt es die Option „Spielraum" (aus, 150, 200).\n'
        '- **Mesh to 3D / 2D3D Kleider**: Kopf-Schritt mit Naht am Hals und Streckung des Kopfnetzes; Reiter '
        '„Gesicht" (Kopfhaltung zurückgedreht, Landmarkmorphe für Lippen, Nase, Augen, Brauen); Haltung je Foto '
        'und Fotoabgleich der Fotohaut; Haarfarbwahl; Entlichten der Netzfarbe; ETCH-X als Entkleider; '
        'Hunyuan3D-2.1 als Maler; Körper-Tor zählt Hände und Randzonen nicht mehr als „am Anschlag"; Regionen-'
        'Regler (Vorgabe aus).\n'
        '- **2D3D Kleider, Iterationen**: Iteration 0, Herrenhaar als eigenes Kurzhaar mit Länge unten und oben, '
        'Licht aus der Fotofarbe, Rumpftiefe und Gesichtsprofil gegen die Seitenfotos; ein Neulauf legt die '
        'Runden beiseite, statt sie mit dem Stand eines anderen Netzes zu vergleichen.\n'
        '- **Szene, Bedienung**: Beim Drehen, Verschieben und Greifen läuft kein Treffertest mehr (das Ruckeln '
        'war ein Test gegen alle Netze je Bild); ein Klick auf ein Stück trifft auch in Tanzhaltung das gehäutete '
        'Netz. Das Figurvideo lässt sich abbrechen, zeigt bei pausierter Aktion wieder Bewegung, und ein ganzer '
        'Pfad im Feld „Ablage" wird in Ordner und Datei geteilt. Reißt die Verbindung beim Anziehen eines Stücks '
        'ab (Serverneustart), wird der Abruf wiederholt, statt ein Häkchen ohne Stück stehen zu lassen.\n'
        '- **Hilfe**: Architektur → 2D3D und → Genesis nachgezogen (Standard und Ausnahme beim Drapieren, '
        'Technische Details, Blender-Import).\n'
    ),
}
