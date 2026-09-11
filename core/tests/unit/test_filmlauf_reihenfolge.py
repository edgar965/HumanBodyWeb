# -*- coding: utf-8 -*-
u"""`filmlauf.py` meldet „Fertig" erst NACH der Bilanz (11.09.2026).

Der Server liest bei „fertig" sofort `video.mp4.json`. Der Lauf schrieb
die Datei 70 ms nach der Meldung — der Stand kam ohne Messwerte an, die
Bilanzzeile im Reiter blieb leer. Ein Quelltext-Test, weil der Lauf selbst
einen OpenGL-Kontext und eine halbe Minute braucht.
"""
from django.conf import settings
from django.test import SimpleTestCase


class FilmlaufReihenfolgeTest(SimpleTestCase):

    databases = []

    def test_bilanz_vor_fertig(self):
        pfad = settings.BASE_DIR / 'TheatreJS' / 'ModelPhysik' / 'filmlauf.py'
        quelle = pfad.read_text(encoding='utf-8')
        bilanz = quelle.index('self._bilanz(film, proben, zahl)')
        fertig = quelle.index("self._melden(u'Fertig', 1.0, fertig=True)")
        self.assertLess(bilanz, fertig)
