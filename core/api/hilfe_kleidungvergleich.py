# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> Vergleich: MakeHuman, Genesis 9, GarmentCode und UMA Schritt fuer Schritt.

Edgar (25.09.2026): „mache dazu eine neue Seite: Hilfe - Kleidung - Vergleich
darin eine Tabelle mit den 4 Kleider und Fitting bibltiothken", dann „tabelle
nach djangoBase format und verständlicher". Die Daten kommen aus
`kleidung.schrittvergleich.Kleidungsschritte`; hier entsteht daraus die
Struktur fuer `djangobase/_tabelle.html` (Zellgitter, ziehbare Breiten,
Abschnittszeilen mit `gruppe`).

Sortieren ist fuer alle Spalten aus (`sortAus`): die Zeilen sind eine
Abfolge von Schritten — alphabetisch sortiert stuende „Dauer" vor „Figur".
Code-Namen stehen in der Datenklasse in Backticks; hier werden sie maskiert
und zu `<code>`.
"""

import re

from django.utils.html import escape
from kleidung.ablaufvergleich import Kleidungsablauf
from kleidung.empfehlung import Kleidungsempfehlung
from kleidung.schrittvergleich import Kleidungsschritte

from .hilfeseite import Hilfeseite

_CODE = re.compile(r'`([^`]+)`')
_FETT = re.compile(r'\*\*([^*]+)\*\*')


class KleidungVergleich(Hilfeseite):
    """Die vier Bibliotheken in Spalten, die Schritte in Zeilen."""

    template_name = 'hilfe/kleidung_vergleich.html'
    AKTIV = 'hilfe_kleidung_vergleich'

    @staticmethod
    def _html(text):
        u"""Escapen, dann `` `code` `` -> `<code>` und `**fett**` -> `<strong>`."""
        roh = escape(text)
        roh = _CODE.sub(r'<code>\1</code>', roh)
        return _FETT.sub(r'<strong>\1</strong>', roh)

    @classmethod
    def _zelle(cls, z):
        kurz = '<strong>%s</strong>' % cls._html(z['kurz']) if z['kurz'] else ''
        genau = '<div class="schritt-genau">%s</div>' % cls._html(z['genau']) if z['genau'] else ''
        return {'html': kurz + genau}

    @classmethod
    def tabelle(cls, daten=Kleidungsschritte, key='hilfe-kleidung-vergleich'):
        u"""`daten`: `Kleidungsschritte` (was geschieht) oder `Kleidungsablauf` (wo im Code)."""
        spalten = daten.spalten()
        kopf = [{'label': 'Schritt', 'key': 'schritt', 'sortAus': True},
                {'label': 'Was heißt das?', 'key': 'erklaerung', 'sortAus': True}]
        kopf += [{'label': s['name'], 'key': s['kuerzel'], 'sortAus': True, 'titel': s['prinzip']}
                 for s in spalten]
        zeilen = []
        for gruppe in daten.gruppen():
            zeilen.append({'gruppe': True, 'klasse': 'schritte-gruppe',
                           'zellen': [{'html': escape(gruppe['name']), 'colspan': len(kopf)}]})
            for zeile in gruppe['zeilen']:
                zeilen.append({'zellen': [{'html': '<strong>%s</strong>' % escape(zeile['schritt'])},
                                          {'html': escape(zeile['erklaerung']), 'klasse': 'schritt-erklaerung'}]
                               + [cls._zelle(z) for z in zeile['zellen']]})
        # Dictionary gewollt: geht unveraendert in `djangobase/_tabelle.html`.
        return {'key': key, 'spalten': kopf, 'zeilen': zeilen, 'klasse': 'kleidung-schritte'}

    def kontext(self):
        empfehlung = [{'titel': a['titel'],
                       'absaetze': [self._html(p) for p in a['absaetze']]}
                      for a in Kleidungsempfehlung.abschnitte()]
        return {'spalten': Kleidungsschritte.spalten(), 'tabelle': self.tabelle(),
                'ablauf': self.tabelle(Kleidungsablauf, 'hilfe-kleidung-ablauf'),
                'empfehlung': empfehlung, 'eigenstueck_kategorien': self.EIGENSTUECK_KATEGORIEN}

    #: Kategorien des Formulars „Eigenes Stück" — die Schlüssel sind die von
    #: `G9mbkategorien.ORDNER`, der Endpunkt nimmt nur diese.
    EIGENSTUECK_KATEGORIEN = (('tops', 'Oberteil'), ('dresses', 'Kleid'), ('pants', 'Hose'),
                              ('skirts', 'Rock'), ('shoes', 'Schuhe'), ('underwear', 'Unterwäsche'),
                              ('accessories', 'Zubehör'))
