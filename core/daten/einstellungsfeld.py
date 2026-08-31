# -*- coding: utf-8 -*-
u"""Einstellungsfeld — was eine Einstellungszeile über ihr Feld weiß.

WARUM (30.08.2026, Befund `jsbefunde`/lange Zeilen)
====================================================================
Titel, Erklärung und Grenzen einer Einstellung standen an DREI Stellen,
und sie liefen auseinander:

1. Im Model als `help_text` — auf Englisch:
   `help_text="IK gradient descent iterations per frame (1–100)"`
2. In der Vorlage als Include-Parameter — auf Deutsch:
   `beschriftung="IK Gradient-Descent Iterationen pro Frame. Mehr =
    genauer aber langsamer."`
3. Nochmal in der Vorlage als `min="1" max="100"` — dieselben Grenzen,
   die im `help_text` schon als Text stehen.

Sichtbar wurde es an zwei Feldern, die auf ZWEI Seiten stehen
(`mp_min_detection_confidence`, `mp_min_tracking_confidence`): dieselbe
Einstellung, zwei verschiedene Titel und zwei verschiedene Erklärungen —
je nachdem, welche Seite man aufruft. Und `progress_update_interval`
erklärte sich als einziges auf Englisch, mitten unter deutschen Zeilen.

Die Zeilen waren dadurch 215 bis 310 Zeichen lang und NICHT umbrechbar:
Djangos Lexer kennt kein DOTALL, ein Tag über zwei Zeilen wird still zu
Text (siehe `_schieberegler.html`). Mit dem Register bleibt in der Vorlage
`{% zahl "v4_hcd_iterations" %}` übrig.

DIE GRENZEN GEHÖREN HIERHER, nicht in die Vorlage: Sie sind eine
Eigenschaft des Feldes, nicht seiner Darstellung. Wer `max` nur in der
Vorlage ändert, hat eine Einstellung, die auf der einen Seite bis 100 und
auf der anderen bis 200 geht — genau das war der Zustand.
"""


class Einstellungsfeld:
    u"""Titel, Erklärung und Grenzen EINER Einstellung.

    Mehr als drei Felder — deshalb eine Klasse und kein Wörterbuch
    (Projektregel). Die Werte sind unveränderlich: Das Register wird beim
    Laden des Moduls gebaut und danach nur gelesen.
    """

    __slots__ = ('titel', 'text', 'min', 'max', 'schritt', 'zusatz')

    def __init__(self, titel, text, min=None, max=None, schritt=None,
                 zusatz=None):
        u"""
        @param titel    fette Überschrift links; leer = keine
        @param text     erklärender Satz darunter, deutsch
        @param min      untere Grenze (Zahlenfeld)
        @param max      obere Grenze (Zahlenfeld)
        @param schritt  `step` des Zahlenfelds; ohne Angabe 1
        @param zusatz   Aufschrift neben dem Ankreuzfeld
        """
        self.titel = titel
        self.text = text
        self.min = min
        self.max = max
        self.schritt = schritt
        self.zusatz = zusatz

    @property
    def hilfetext(self):
        u"""Was als `help_text` ans Model-Feld geht — Text plus Grenzen.

        So steht die Erklärung EINMAL da und erscheint im Admin genauso wie
        auf der Einstellungsseite. Die Grenzen kommen aus `min`/`max`, statt
        ein zweites Mal in den Text geschrieben zu werden.
        """
        if self.min is None and self.max is None:
            return self.text
        return u'%s (%s–%s)' % (self.text,
                                u'…' if self.min is None else self.min,
                                u'…' if self.max is None else self.max)

    def als_kontext(self, kennung, wert):
        u"""Was die Vorlage braucht — für `{% zahl %}` und `{% kaestchen %}`."""
        return {
            'feld': kennung,
            'titel': self.titel,
            'beschriftung': self.text,
            'wert': wert,
            'an': wert,
            'min': self.min,
            'max': self.max,
            'schritt': self.schritt or 1,
            'text': self.zusatz or u'Aktiviert',
        }
