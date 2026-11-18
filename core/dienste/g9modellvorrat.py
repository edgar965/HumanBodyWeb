# -*- coding: utf-8 -*-
u"""G9modellvorrat — die Anzeigen der Genesis-Figuren dauerhaft, über Code-Änderungen hinweg (19.10.2026).

Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen … sodass sie beim Laden schnell angezeigt werden".

WARUM DER ANTWORTVORRAT NICHT REICHTE: `G9antworten` legt jede Netzantwort ab — aber unter der Code-Fassung (Inhalts-Hash über `Genesis9/` und die
Antwortmodule). Jede Änderung dort macht ALLES ungültig; gemessen am 19.10.2026 lagen nach einem Tag Arbeit 6 Antworten (9,3 MB, alle grob) im Vorrat,
jeder Ladevorgang rechnete Körper und Stücke neu (kalt 5–14 s je Stück). Hier liegt dieselbe Antwort OHNE Fassung im Schlüssel:

    liefern: Vorrat dieser Fassung → sonst HIER, wenn mit dem jetzigen Code gerechnet → sonst rechnen.

JEDER EINTRAG TRÄGT SEINE CODE-FASSUNG (17.11.2026, Edgar: „fixe das: Nach einer Code-Änderung zeigen sie beim ersten Laden noch den alten Stand"): im Verweis
hinter dem sha1 (`G9antwortvorrat._von_platte`); Verweise von davor tragen keine und gelten als alt. Ein Eintrag älteren Codes geht nur noch hinaus
* als VORSCHAU: der Käfig des ersten Zugs, den die gewählte Stufe gleich ersetzt (Kopf `X-G9-Vorrat-Vorschau`, `gemeinsam/genesis9vorrat.js`) — mit
  `X-G9-Vorrat-Alt`, damit der Browser ihn nicht im RAM hält (`Genesis9antwortspeicher.ablegen`),
* beim Vorab-Füllen (es geht nichts hinaus);
dann rechnet `G9vorratnachlauf` ihn im Hintergrund neu. Sonst wird neu gerechnet und der Eintrag ersetzt: die gewählte Stufe kommt immer aus dem jetzigen
Code und wird nach einer Code-Änderung beim ersten Laden neu gerechnet. Bis 17.11.2026 ging jeder alte Eintrag sofort hinaus („stale-while-revalidate"): wer
nach einer Code-Änderung lud, sah einmal den alten Stand.

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
    def lesen(cls, schluessel):
        u"""(Bytes, Code-Fassung beim Ablegen) — oder None. Ein Verweis von vor dem 17.11.2026 trägt keine Fassung: ''."""
        with cls._schloss:
            eintrag = cls._speicher.get(schluessel)
            if eintrag is not None:
                cls._speicher.move_to_end(schluessel)
                return eintrag
        eintrag = cls._von_platte(schluessel)
        if eintrag is not None:
            cls._im_speicher(schluessel, eintrag)
        return eintrag

    @classmethod
    def holen(cls, schluessel):
        eintrag = cls.lesen(schluessel)
        return None if eintrag is None else eintrag[0]

    @classmethod
    def merken(cls, schluessel, daten, fassung=''):
        u"""Bytes ablegen, mit der Code-Fassung, die sie gerechnet hat (`G9antworten.fassung`)."""
        cls._im_speicher(schluessel, (daten, fassung))
        threading.Thread(target=cls._schreiben, args=(schluessel, daten, fassung), daemon=True, name='g9-modellvorrat').start()

    @classmethod
    def fassung_von(cls, schluessel):
        u"""Die Code-Fassung des Eintrags ('' ohne) — None, wenn keiner liegt. Liest nur den Verweis, nicht den Inhalt."""
        with cls._schloss:
            eintrag = cls._speicher.get(schluessel)
        if eintrag is not None:
            return eintrag[1]
        try:
            teile = (cls.ordner() / (schluessel + cls.VERWEIS)).read_text(encoding='ascii').split()
        except OSError:
            return None
        return ' '.join(teile[1:]) if teile else None
