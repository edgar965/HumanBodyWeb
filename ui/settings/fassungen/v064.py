# -*- coding: utf-8 -*-
"""Fassung 0.64 (24.09.2026) — Oberflächenbindung repariert, Texturbündel, Webserver-Vergleich, BVH-Studio-Videoexport in Paketen mit Ton."""

FASSUNG = {
    'version': '0.64',
    'date': '2026-09-24',
    'title': 'Genesis 9: Oberflächenbindung drückt nur noch hinaus (Schuhform bleibt), '
    'Texturbündel; Hilfe → Architektur → Webserver; BVH Studio: Videoexport in Paketen '
    'mit Ton',
    'author': 'edgar965',
    'body_md': (
        'HumanBodyWeb ab `e8868f7` (Version 0.63), HumanBodyBlender ohne Inhaltsänderung, '
        'VideoToBVH unverändert.\n'
        '\n'
        '- **Genesis 9, Oberflächenbindung repariert**: Die Schicht-2-Bindung („dehnbar", '
        'Kleidung ohne Durchschimmern) setzte bisher jeden gebundenen Stoffpunkt starr auf '
        'die projizierte Körperfläche — ein Schuh über dem Fuß verlor dadurch seine eigene '
        'Form, die Sohle riss (Fund 24.09.: G9-Base-Shirt zeigte Haut durch den Stoff). Jetzt '
        'bleibt der Stoff beim normalen Skinning und wird nur dort nach außen gedrückt, wo er '
        'TIEFER liegt als im Ruhezustand — nie mehr hineingezogen; zwei Grenzen (Tiefe, '
        'seitlicher Versatz zum Dreieck) fangen Punkte ab, die durch ein dünnes Körperteil '
        'gefahren sind. Dazu eine Normalenglättung im Fragment-Shader an Gelenken (Achsel, '
        'Ellbogen, Leiste), wo eine gehäutete Punktnormale stark von der Flächennormale '
        'abweicht. Beide Effekte jetzt abschaltbar über die neue Seite Einstellungen → '
        'Kleider (Standard: an).\n'
        '- **Genesis 9, Texturbündel**: Alle Bilder eines Netzes (Körper + Kleidung + Haar) '
        'kommen jetzt in EINER binären Antwort statt einzeln — Daphne kann kein HTTP/2, Chrome '
        'hält je Herkunft nur sechs Verbindungen offen, rund vierzig Einzelbilder liefen bisher '
        'in sieben Wellen. Rohe Bytes statt Base64 (kein `JSON.parse` über zig Megabyte); was '
        'über der Bündel-Obergrenze liegt (einzelne 8K-Kacheln, 97 MB), bleibt außen und kommt '
        'wie bisher einzeln.\n'
        '- **Hilfe → Architektur → Webserver**: Vergleichstabelle der ASGI-Server-Alternativen '
        'zu Daphne (Uvicorn, Hypercorn, Granian, Gunicorn+Uvicorn-Worker), sortierbar nach '
        'djangoBase-Muster — Sterne und Tage seit dem letzten Push gemessen (GitHub-/PyPI-API, '
        '23.09.2026), nicht geschätzt. Richtiggestellt: Daphne kann HTTP/2, aber nur mit TLS '
        'und den Twisted-Extras `h2`/`priority` (hier noch nicht installiert).\n'
        '- **BVH Studio, Videoexport**: Bilder eines Server-Exports kommen jetzt in kleinen '
        'Paketen statt einer einzigen Anfrage mit allen Bildern — Django prüft die '
        '500-MB-Grenze am GESAMTEN Request, ein langer Export lief in „Too many open files" '
        '(Windows-Limit, seit Python 3.13 nicht mehr per `msvcrt.setmaxstdio` hochsetzbar). '
        'Dazu werden die Tonspuren des Studios jetzt tatsächlich in den Export eingemischt '
        '(vorher exportierte die Bildfolge stumm, obwohl Audio-Clips im Projekt lagen).\n'
        '- Kleinere BVH-Studio-Arbeit: eigene Spur-Anzeige für fehlende Clips, Modellspur, '
        'Lichtschlüssel-Regler, Vorladen und Bibliotheksbaum-Menüs überarbeitet.'
    ),
}
