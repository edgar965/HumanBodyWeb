# -*- coding: utf-8 -*-
"""Szenentexturwahl — wie /Charakter/ die Bilder der Genesis-Figuren lädt (19.10.2026).

Edgar, 19.10.2026, nach dem KTX2-Versuch auf Mesh3D-AI („würde das auch was bringen für die Charakter seite?“): „mach das“ — gemeint waren die zwei Wege, die
auf /Charakter/ taugen (die Figur füllt dort den Bildschirm, man zoomt aufs Gesicht; verkleinerte Bilder wie Weg A von Mesh3D-AI also nicht):
    voll         die Originale wie bisher (Vorgabe — nichts ändert sich, bis jemand umstellt)
    komprimiert  S3TC-Block mit Mip-Stufen (`G9texturblock`, Weg C von Mesh3D-AI)
    uastc        UASTC (KTX2, `G9texturbasis`): kodiert im Hintergrund, bis dahin der S3TC-Block
Die Seite trägt die Wahl im Kopf (`<meta name="texturweg">`, `{% szenentexturweg %}` in `scene_config.html`, `gemeinsam/texturweg.js`), gilt also ab dem nächsten
Laden. Ohne S3TC im Browser fällt sie auf `voll` zurück (`data-rueckfall`), nicht auf verkleinerte Bilder. Wert in `AppSettings.ui_prefs` unter `SCHLUESSEL`
(Einstellungen → Charakter, `SzeneEinstellungen`); Unbekanntes heißt Vorgabe.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Szenentexturwahl']


class Szenentexturwahl:
    SCHLUESSEL = 'szene_texturen'
    VORGABE = 'voll'
    WERTE = (
        ('voll', 'Volle Bilder wie bisher (Vorgabe)'),
        ('komprimiert', 'Volle Bilder, für die Grafikkarte komprimiert (S3TC)'),
        ('uastc', 'Volle Bilder, fast verlustfrei komprimiert (UASTC)'),
    )
    # Gemessen 19.10.2026 im Chrome an Damira0 auf Mesh3D-AI (Probe 41, 22 Bilder, davon 17 mit 4096 px), Ladeprobe mit 22 Einzelabrufen, je Weg drei Läufe im
    # Wechsel; Bildvergleich gegen die vollen Bilder in Pixeln der Leinwand (0–255). Auf /Charakter/ selbst gemessen: Tagebuch 2026-10-19, Abschnitt „Abend, zweiter Teil“.
    BESCHREIBUNG = {
        'voll': 'wie bisher. Alle Bilder da nach 3,8–4,2 s, die Seite steht bis 0,64 s.',
        'komprimiert': 'alle Bilder da nach 0,8–1,2 s, die Seite steht höchstens 0,09 s, ein Achtel des Grafikspeichers. Kleine Abweichungen an Kanten. '
                       'Beim ersten Öffnen rechnet der Server jedes Bild einmal (4096 px: 1,9 s).',
        'uastc': 'fast wie das Original, die Seite steht höchstens 0,08 s, ein Viertel des Grafikspeichers — aber alle Bilder erst nach 4,4–5,1 s. '
                 'Der Server packt jedes Bild einmal im Hintergrund (4096 px: rund 45 s), bis dahin kommt es wie bei S3TC.',
    }
    #: Kurzname je Weg für die Erklärung unter der Überschrift.
    KURZ = {'voll': 'Volle Bilder', 'komprimiert': 'S3TC', 'uastc': 'UASTC'}
    #: Woher die Zahlen sind (steht unter den drei Wegen auf der Einstellungsseite).
    QUELLE = 'Gemessen an Damira0 (22 Bilder) auf Mesh3D-AI; Grafikspeicher gerechnet.'

    @classmethod
    def aus(cls, prefs):
        """Der Weg aus einem `ui_prefs`-Dict; alles, was keiner der `WERTE` ist, ist die Vorgabe."""
        wert = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return wert if wert in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Wahl — ohne lesbare Einstellungen (keine Datenbank) die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — die Seite soll auch ohne Datenbank laden, mit der Vorgabe
            logger.warning('Szenentexturwahl: Einstellung nicht lesbar (%s) — %s', fehler, cls.VORGABE)
            return cls.VORGABE
