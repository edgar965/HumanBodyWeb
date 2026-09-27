# -*- coding: utf-8 -*-
"""Fassung 0.65 (27.09.2026) — Modellexport: Bildrate einstellbar, Schuh-Occlusion repariert, Fleckenprüfung ohne Kanten-Fehlalarm."""

FASSUNG = {
    'version': '0.65',
    'date': '2026-09-27',
    'title': 'Modellexport: Export Blender/.blend, GLB, OBJ mit einstellbarer Bildrate; '
    'Genesis 9: Schuh-Occlusion repariert, Fleckenprüfung ohne Kanten-Fehlalarm',
    'author': 'edgar965',
    'body_md': (
        '- **Modellexport, Bildrate einstellbar (fps-Feld im Export-Dialog, Standard 30)**: '
        'Die Animation wurde bisher mit ihrer Quellrate exportiert (DanceKurz: rund 60 '
        'Bilder/s) — Blenders `.blend`-Import rechnet Keyframe-Zeiten aber über die Szenen-FPS '
        '(Werkseinstellung 24) in Framenummern um; mehrere Quell-Zeiten fielen auf dieselbe '
        'Framenummer, aus 1004 Bildern wurden 401 (Fund: „als ob viele Frames fehlen"). Ein '
        'erster Zwischenschritt setzte die Szenen-FPS pauschal auf 240 — dadurch wurde die '
        'Wiedergabe bei der schweren Figur (792.828 Körperdreiecke) sichtbar LANGSAMER, weil '
        'jedes real gerenderte Bild die Animation nur noch um 1/240 s vorrückte. Jetzt tastet '
        'der Browser den Clip vor dem Export selbst auf die gewählte Rate ab '
        '(`clipabtastung.js`), Blenders Szenen-FPS wird auf dieselbe Rate gesetzt und die '
        'Wiedergabe läuft mit Frame-Dropping (Echtzeit-Tempo, notfalls ausgelassene Bilder, '
        'statt Zeitlupe). Gilt für GLB, `.blend`, DAE.\n'
        '- **Genesis 9, Schuh-Occlusion repariert** (Fund: Damira1/Flats, Haut sichtbar durch '
        'den Schuh, in Export UND Live-Szene): Die Hautverdeckung prüft je Körperpunkt einen '
        'Strahl entlang der Körpernormale gegen die Kleidung — ein steifer Schuh krümmt sich '
        'an Zehenkappe und Rist anders als der Fuß darunter, der Strahl verfehlte die '
        'Schuhwand trotz weniger Millimeter Abstand. Zusätzlicher richtungsloser Abstandstest '
        'als Fallback; dazu behält ein als starr erkanntes Stück (der Schuh) nicht mehr den '
        'Randstreifen, den die Maske für eine lockere, sich hebende Stoffkante (Bund, Ärmel) '
        'bewusst freilässt.\n'
        '- **Exportfleckenprüfung ohne Kanten-Fehlalarm**: Das Prüfwerkzeug für „fremde Farbe '
        'im Umriss eines einfarbigen Teils" maß am Schuh nach dem obigen Fix weiterhin 6 % — '
        'die markierten Punkte lagen aber alle auf einer dünnen Linie exakt am Silhouettenrand '
        '(Antialiasing-Unterschied zwischen zwei separat gerenderten Bildern), nicht in der '
        'Fläche. Bei einer kleinen Silhouette (Schuh, in der Kamera auf die ganze Figur '
        'gerahmt) macht das allein mehrere Prozent aus. Die Silhouette wird jetzt vor der '
        'Auswertung um 3 Pixel eingezogen; ein echter, flächiger Fund bleibt davon '
        'unberührt (Gegenprobe mit dem ursprünglichen Fund nachgestellt).'
    ),
}
