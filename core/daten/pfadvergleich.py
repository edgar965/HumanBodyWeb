# -*- coding: utf-8 -*-
"""Pfadvergleich — liegt dieser Pfad unter dieser Wurzel?

DIE EINE FRAGE, SIEBEN ANTWORTEN
================================
Sieben Stellen im Projekt beantworteten sie mit einem ZEICHENVERGLEICH:

    if not ziel.startswith(os.path.normpath(wurzel)):

Das ist falsch, und zwar seit dem 12.08.2026 bekannt: `…/media_evil/x.bvh`
beginnt mit `…/media`, also besteht es die Pruefung. Dasselbe gilt fuer
`animations_evil` neben `animations` und `poseData_evil` neben `poseData`. Der
Fehler ist im Projekt VIERMAL einzeln gefunden und viermal einzeln repariert
worden — das Werkzeug `pfadpraefix` findet ihn jetzt von selbst.

`Path.is_relative_to` vergleicht Pfad-TEILE statt Zeichen und kennt diesen Fall
nicht.

WARUM `resolve()` UND NICHT NUR `normpath`
==========================================
`resolve()` loest `..`, Verknuepfungen und die Gross-/Kleinschreibung des
Laufwerksbuchstaben auf. Unter Windows sind `A:\\Media` und `a:\\media` dasselbe
Verzeichnis — ein Vergleich ohne Auflösung sagt „nein" (im Projekt am
18.08.2026 als eigener Test festgenagelt, `test_safe_paths`).

WANN STATTDESSEN `SafePath`
===========================
`core/safe_paths.SafePath` beantwortet dieselbe Frage fuer Pfade, die ein
Nutzer FREI angeben darf (Studio-Projekte, Videoausgabe): Es kennt zusaetzlich
Windows-Geraetenamen (`NUL`, `COM1`), UNC-Pfade und NTFS-Datenstroeme und wirft
`PfadAbgelehnt` mit Begruendung. Diese Klasse hier ist der engere Fall: ein
selbst gebauter Pfad, eine Wurzel, ja oder nein.
"""

from pathlib import Path


class Pfadvergleich:
    """Ja/Nein auf Pfadteilen — nie auf Zeichen."""

    @staticmethod
    def liegt_unter(pfad, wurzel):
        """Liegt `pfad` in `wurzel` (oder IST die Wurzel)?

        `False` auch dann, wenn einer der beiden nicht aufloesbar ist — ein
        Zweifelsfall wird abgelehnt, nicht durchgelassen.
        """
        try:
            ziel = Path(pfad).resolve()
            basis = Path(wurzel).resolve()
        except (OSError, ValueError, TypeError):
            # stumm gewollt: Diese Methode ist ein WAECHTER und wird in
            # Schleifen ueber viele Pfade gerufen. Was hier scheitert, ist
            # kein Pfad — und „False" ist die vollstaendige Antwort darauf.
            # Wer den Grund braucht, protokolliert an der Aufrufstelle, die
            # den Zusammenhang kennt.
            return False
        return ziel == basis or ziel.is_relative_to(basis)
