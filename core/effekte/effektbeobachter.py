# -*- coding: utf-8 -*-
u"""Effektbeobachter — der Logbeobachter, der nur die Effekte-Zeilen liest.

Blender schreibt beim Start seitenweise Fremdes ins Protokoll (MB-Lab,
Addon-Updater, ein Traceback eines fremden Addons). Der Logbeobachter
nimmt die LETZTE Zeile des Nachschubs — und zeigte auf der Seite
`ValueError: expected Panel, HUMANBODY_PT_main …` als Fortschritt
(12.09.2026). Hier zaehlen nur Zeilen mit dem Praefix `Effekte:`; der
Praefix selbst faellt in der Anzeige weg.
"""
from ..pipelines.logbeobachter import Logbeobachter

__all__ = ['Effektbeobachter']


class Effektbeobachter(Logbeobachter):

    PRAEFIX = 'Effekte: '

    def auswerten(self, text, jetzt=None):
        zeilen = [z.strip()[len(self.PRAEFIX):] for z in text.splitlines()
                  if z.strip().startswith(self.PRAEFIX)]
        if not zeilen:
            return False
        return super().auswerten('\n'.join(zeilen), jetzt)
