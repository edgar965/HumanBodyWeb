# -*- coding: utf-8 -*-
"""Bvhbibliothek — Suche und Seitenaufteilung der BVH-Dateiliste.

PERFORMANCE 16.08.2026: `/library/` war mit 2.082 ms der zweitlangsamste
Endpunkt der Anwendung. Die Ursache lag nicht in der Datenbank — eine einzige
Abfrage, 5 ms — sondern in der Vorlage: sie rendert JEDE der 7.110 Zeilen als
Karte mit zwei Formularen samt CSRF-Feld. Ergebnis: **10,5 MB HTML**. Danach
muss der Browser 7.110 Karten aufbauen, was die eigentliche Wartezeit erklaert;
die 2 Sekunden Serverzeit sind nur der Anfang.

Eine Liste mit 7.110 Eintraegen ist ohne Suche ohnehin nicht benutzbar, deshalb
loest eine Seitenaufteilung zwei Probleme auf einmal. Gefiltert wird in der
Datenbank, nicht in Python — bei 7.110 Zeilen ist der Unterschied noch klein,
aber die Liste waechst mit jedem Scan.
"""

from django.core.paginator import Paginator

from ..models import BVHFile


class Bvhbibliothek:
    """Gefilterte, seitenweise Sicht auf die BVH-Dateien."""

    #: Karten je Seite. 60 statt 7.110 druecken das HTML von 10,5 MB auf ~90 KB.
    JE_SEITE = 60

    def __init__(self, suche='', quelle='', seite=1):
        self.suche = (suche or '').strip()
        self.quelle = (quelle or '').strip()
        self.seite = seite

    @classmethod
    def aus_anfrage(cls, request):
        return cls(suche=request.GET.get('q', ''),
                   quelle=request.GET.get('source', ''),
                   seite=request.GET.get('page', 1))

    def _menge(self):
        menge = BVHFile.objects.all()
        if self.suche:
            menge = menge.filter(name__icontains=self.suche)
        if self.quelle:
            menge = menge.filter(source=self.quelle)
        # Feste Reihenfolge: ohne order_by warnt der Paginator, und die
        # Seitengrenzen waeren zwischen zwei Aufrufen nicht stabil.
        return menge.order_by('name', 'pk')

    def quellen(self):
        """Vorhandene Quellwerte fuer das Auswahlfeld.

        `order_by()` OHNE Argument ist hier zwingend und kein Schoenheitsfehler:
        Hat das Modell eine Standardsortierung (`Meta.ordering`), haengt Django
        deren Felder an die Auswahl an — und dann wirkt `distinct()` auf
        (source, name, …) statt auf source allein. Beim ersten Bauen lieferte
        das Feld 7.110 Einträge, einen je Datei, alle mit demselben Wert.
        """
        return sorted(BVHFile.objects.exclude(source='').order_by()
                      .values_list('source', flat=True).distinct())

    def seiteninhalt(self):
        aufteiler = Paginator(self._menge(), self.JE_SEITE)
        return aufteiler.get_page(self.seite)

    def zusatzfrage(self):
        """Query-Anteil fuer die Seitenlinks, damit Filter erhalten bleiben."""
        teile = []
        if self.suche:
            teile.append('q=%s' % self.suche)
        if self.quelle:
            teile.append('source=%s' % self.quelle)
        return ('&' + '&'.join(teile)) if teile else ''

    def zusammenhang(self):
        inhalt = self.seiteninhalt()
        return {
            'files': inhalt,
            'seite': inhalt,
            'suche': self.suche,
            'quelle': self.quelle,
            'quellen': self.quellen(),
            'zusatzfrage': self.zusatzfrage(),
            'gesamt': inhalt.paginator.count,
        }
