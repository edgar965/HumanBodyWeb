# -*- coding: utf-8 -*-
u"""G9modellvorrat — die Anzeigen der Genesis-Figuren dauerhaft, über Code-Änderungen hinweg (19.10.2026).

Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen … sodass sie beim Laden schnell angezeigt werden".

WARUM DER ANTWORTVORRAT NICHT REICHTE: `G9antworten` legt jede Netzantwort ab — aber unter der Code-Fassung (Inhalts-Hash über `Genesis9/` und die
Antwortmodule). Jede Änderung dort macht ALLES ungültig; gemessen am 19.10.2026 lagen nach einem Tag Arbeit 6 Antworten (9,3 MB, alle grob) im Vorrat,
jeder Ladevorgang rechnete Körper und Stücke neu (kalt 5–14 s je Stück). Hier liegt dieselbe Antwort OHNE Fassung im Schlüssel:

    liefern: Vorrat dieser Fassung → sonst HIER (sofort ausliefern, im Hintergrund mit dem jetzigen Code neu rechnen) → sonst rechnen.

Der Inhalt ist also höchstens einen Ladevorgang alt („stale-while-revalidate"): wer nach einer Code-Änderung lädt, sieht einmal den alten Stand, der nächste den
neuen. Das gilt für alles im Code — auch für Fehlerbehebungen am Netz.

WAS HINEINKOMMT: nur Anfragen, die der Browser als ANZEIGE einer Figur markiert (`X-G9-Vorrat`, `gemeinsam/genesis9vorrat.js`: das Laden einer Figur, der
Stufenwechsel und das Vorab-Füllen nach dem Laden eines gespeicherten Modells) — Reglerzüge nicht, sonst läge jede Zwischenstellung hier. Und nur bis zur
Stufe der Einstellung (`Netzvorratwahl`, Vorgabe ultrafein). Gelesen wird ohne Markierung: eine Stellung, die einmal angezeigt wurde, kommt von hier.

Ablage `Genesis9/ablage/modellvorrat/<schema>/` wie der Antwortvorrat (Inhalt einmal je sha1, Schlüssel als Verweis), höchstens `PLATTE_MB`; was am längsten
nicht gelesen wurde, fliegt zuerst (`G9vorratputz.eigene`). Geschätzt (19.10.2026, `ProjektTemp/_wegwerf/anzeigevorrat/platz_probe.py`, nur grob gemessen,
fein/ultrafein über die Punktzahl hochgerechnet): 36 gespeicherte Modelle 3–7 GB mit float32, mit 16 Bit (`Netzkurz`) rund ein Viertel weniger.
"""
import threading
from collections import OrderedDict

from .g9antwortvorrat import G9antwortvorrat

__all__ = ['G9modellvorrat']


class G9modellvorrat(G9antwortvorrat):

    ORDNER = 'modellvorrat'
    #: Im Prozess hält schon `G9antworten` die jüngsten; hier nur wenige, damit ein zweiter Zugriff im selben Ladevorgang nicht die Platte fragt.
    IM_SPEICHER = 2
    PLATTE_MB = 20000
    #: Das Ablageformat dieses Vorrats — hochzählen, wenn eine Antwort alter Bauart der Browser nicht mehr lesen kann (dann ist der Ordner fremd).
    SCHEMA = 1

    # Eigene Ablagen: geerbt wären Speicher und Schloss die des Antwortvorrats.
    _speicher = OrderedDict()
    _schloss = threading.Lock()

    @classmethod
    def fassung(cls):
        u"""Bewusst KEINE Code-Fassung — das ist der Sinn dieses Vorrats (Kopf). Der Schlüssel der Antwort trägt `stabil` statt der Fassung."""
        return 'stabil'

    @classmethod
    def vorhanden(cls, schluessel):
        u"""Liegt der Schlüssel auf der Platte (ohne zu lesen)?"""
        return (cls.ordner() / (schluessel + cls.VERWEIS)).is_file()
