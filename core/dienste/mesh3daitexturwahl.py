# -*- coding: utf-8 -*-
"""Mesh3daitexturwahl — wie die Jobseite von Mesh3D-AI die Bilder der Genesis-Figuren lädt (19.10.2026).

Edgar, nach der Untersuchung „ein Bildersatz kostet 1,7–2,8 s, weil 15 von 22 Bildern 4096² sind“: „mach alle 3, per Option einstellbar, default: A“. Drei Wege:
    klein        A — der Server verkleinert jedes Bild auf höchstens `KANTE` px (`G9texturkopie`), Vorgabe
    verteilt     B — volle Bilder, aber jedes in einem eigenen Schritt auf die Grafikkarte (`gemeinsam/texturweg.js`, `renderer.initTexture`)
    komprimiert  C — volle Bilder als S3TC-Block mit Mip-Stufen (`G9texturblock`); Rechnungen im Browser lesen eine 1024er Vorschau
Die Jobseite trägt die Wahl im Kopf (`<meta name="texturweg">`, `Mesh3daiendpunkte.seite`), gilt also ab dem nächsten Laden der Seite. Andere Seiten (Charakter) laden wie bisher.
Der Wert liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Formular als JSON an `/api/ui-prefs/`, wie `Mesh3daiaposewahl`). Unbekanntes oder Unlesbares heißt Vorgabe.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daitexturwahl']


class Mesh3daitexturwahl:
    SCHLUESSEL = 'mesh3dai_texturen'
    #: Längste Kante bei Weg A — Setzung nach der Messung vom 19.10.2026 (1024 im Feld nicht vom Original zu unterscheiden, 2048 noch 0,55–0,70 s je Satz).
    KANTE = 1024
    WERTE = (
        ('klein', 'Kleinere Bilder (höchstens 1024 px) — am schnellsten'),
        ('verteilt', 'Volle Bilder, eines nach dem anderen hochladen'),
        ('komprimiert', 'Volle Bilder, für die Grafikkarte komprimiert'),
    )
    # Gemessen 19.10.2026 im Chrome an Damira0 (Probe 41, 22 Bilder, davon 17 mit 4096 px), je Weg mehrere Neuladen im Wechsel; vorher (alles voll, sofort hochgeladen):
    # alle Bilder da nach 4,6–5,4 s, eine Aufgabe hielt die Seite 2,1–2,3 s an. Bildvergleich gegen die vollen Bilder: Pixel der Leinwand, 0–255.
    BESCHREIBUNG = {
        'klein': 'Der Server verkleinert jedes Bild der Figur einmal auf höchstens 1024 Pixel und legt es ab. Gemessen an Damira0: alle Bilder da nach 0,5–0,7 s statt 4,6–5,4 s, '
                 'die Seite steht höchstens 0,16–0,30 s statt 2,1–2,3 s. Im Bild kaum ein Unterschied (ganzer Körper im Mittel 0,02, Gesicht von nah 0,05 von 255). '
                 'Beim allerersten Öffnen rechnet der Server die kleinen Bilder einmal (ein Bildersatz kam dann nach 1,0–1,6 s).',
        'verteilt': 'Die Bilder kommen in voller Größe, jedes geht in einem eigenen Schritt auf die Grafikkarte. Gemessen an Damira0: alle Bilder da nach 5,3–5,9 s (so lange wie '
                    'bisher), aber die Seite steht höchstens 0,28–0,34 s am Stück statt 2,1–2,3 s — dazwischen bleibt sie bedienbar.',
        'komprimiert': 'Die Bilder kommen in voller Größe, aber schon für die Grafikkarte gepackt (S3TC: BC1, mit Durchsichtigkeit BC3) mit fertigen Verkleinerungsstufen. '
                       'Gemessen an Damira0: alle Bilder da nach 3,2–5,3 s, die Seite steht höchstens 0,19–0,30 s. Beim ersten Öffnen rechnet der Server jedes Bild '
                       '(4096 px: 1,9 s, danach 0,2 s aus der Ablage) — die erste Ansicht dauerte 17 s. Ein 4096er-Bild wiegt 11,3 MB statt 2,7 MB. Im Bild: ganzer Körper '
                       'im Mittel 0,16, Gesicht von nah 0,30 von 255, an Kanten bis 33. Rechnungen im Browser (Hautton, Karten der Scham, Umfärbung) lesen eine 1024er Vorschau.',
    }
    VORGABE = 'klein'

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
            logger.warning('Mesh3daitexturwahl: Einstellung nicht lesbar (%s) — Weg %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, wert)
