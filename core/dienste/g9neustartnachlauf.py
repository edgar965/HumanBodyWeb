# -*- coding: utf-8 -*-
u"""G9neustartnachlauf — die zuletzt angezeigten Netze nach einem Neustart im Hintergrund neu rechnen.

BEFUND (Edgar, 18.11.2026: „laden vom modell … dauert viel zu lange … das muss in 2 s gehen!"): Jede
Code-Änderung startet den Server neu und ändert die Fassung des Antwortvorrats (`G9antworten.fassung`, ein
Inhalts-Hash der Quellen). Die nächste Seite fand danach keine fertige Antwort — `django.log` 18.11.2026 nach
den Neustarts 10:48:35, 10:53:27 und 10:57:44: Anatomie fein 7,58 / 7,28 s, Figur fein 1,98 / 2,18 s;
dieselben Anfragen aus dem Vorrat 0,17 / 0,09 s (10:49:52). Den Käfig zeigte der Browser als Vorschau aus
altem Code (`G9vorratanfrage`), die gewählte Stufe rechnete neu, während die Seite wartete.

Deshalb merkt sich `merken` je Adresse (Methode, Pfad, Abfrage, die Köpfe aus `KOEPFE`, Stufen-Keks) die
jüngste ausgelieferte ANZEIGE (Kopf `X-G9-Vorrat`, den der Browser beim Laden einer Figur setzt —
`gemeinsam/genesis9vorrat.js`; kein Reglerzug, keine Skriptprobe) samt Rumpf in
`Genesis9/ablage/zuletzt_angezeigt.json`. `nachrechnen`, ein
Schritt von `G9aufwaermen`, schickt nach dem Start die der zuletzt offenen Seite (`FENSTER_S`) durch dieselbe
Ansicht: Die Antworten liegen dann im Vorrat der neuen Fassung. Fragt der Browser, während eine noch rechnet,
wartet er auf dieselbe Rechnung (`G9antworten.rechnen`, `_laufend`). Nur im Serverprozess
(`G9aufwaermen.angebracht`): Tests und Skripte schreiben die Datei nicht.
"""
import json
import logging
import os
import threading
import time
from collections import OrderedDict
from urllib.parse import parse_qs

__all__ = ['G9neustartnachlauf']

logger = logging.getLogger('core')


class G9neustartnachlauf:
    u"""Die zuletzt ausgelieferten Netzanfragen merken und nach dem Start erneut schicken."""

    DATEI = 'zuletzt_angezeigt.json'
    #: So viele Adressen bleiben (eine Figur mit zwei Stücken sind sechs: je Käfig und gewählte Stufe).
    ANZAHL = 16
    #: Nachgerechnet wird, was höchstens so lange vor der jüngsten Anfrage kam — die zuletzt offene Seite.
    FENSTER_S = 600.0
    #: Ein größerer Rumpf wird nicht gemerkt.
    HOECHSTENS_BYTES = 2 * 1024 * 1024
    #: Köpfe, die über die Antwort entscheiden: das Format (`Netzausgabe.will_binaer`) und das Ablegen
    #: (`G9vorratanfrage.KOPF`). Die Vorschau nicht — nachgerechnet wird mit dem jetzigen Code.
    KOEPFE = ('Accept', 'X-G9-Vorrat')

    _schloss = threading.Lock()
    _liste = None
    _an = None

    @classmethod
    def an(cls):
        if cls._an is None:
            from .g9aufwaermen import G9aufwaermen
            cls._an = G9aufwaermen.angebracht()
        return cls._an

    @classmethod
    def datei(cls):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / cls.DATEI

    # ---------------------------------------------------------------- merken

    @classmethod
    def merken(cls, request):
        u"""Die eben ausgelieferte Anfrage als jüngste ihrer Adresse merken."""
        if request is None or not cls.an():
            return
        from .netzstufenwahl import Netzstufenwahl
        try:
            rumpf = request.body if request.method == 'POST' else b''
        except Exception:  # noqa: BLE001 — der Rumpf war schon als Strom gelesen: dann nicht merken
            return
        if len(rumpf) > cls.HOECHSTENS_BYTES:
            return
        eintrag = {'methode': request.method, 'pfad': request.path,
                   'abfrage': request.META.get('QUERY_STRING', ''),
                   'koepfe': {k: request.headers[k] for k in cls.KOEPFE if request.headers.get(k)},
                   'keks': request.COOKIES.get(Netzstufenwahl.KEKS, ''),
                   'rumpf': rumpf.decode('utf-8', 'replace'), 'zeit': time.time()}
        adresse = json.dumps([eintrag[k] for k in ('methode', 'pfad', 'abfrage', 'koepfe', 'keks')],
                             sort_keys=True)
        with cls._schloss:
            liste = cls._laden()
            liste.pop(adresse, None)
            liste[adresse] = eintrag
            while len(liste) > cls.ANZAHL:
                liste.popitem(last=False)
            cls._schreiben(liste)

    @classmethod
    def _laden(cls):
        if cls._liste is None:
            cls._liste = OrderedDict()
            try:
                for adresse, eintrag in json.loads(cls.datei().read_text(encoding='utf-8')):
                    cls._liste[adresse] = eintrag
            except FileNotFoundError:
                pass
            except (OSError, ValueError, TypeError) as fehler:
                logger.warning('Genesis 9: %s nicht lesbar (%s) — beginnt leer', cls.DATEI, fehler)
        return cls._liste

    @classmethod
    def _schreiben(cls, liste):
        ziel = cls.datei()
        neu = ziel.with_name(ziel.name + '.neu')
        try:
            neu.write_text(json.dumps(list(liste.items())), encoding='utf-8')
            os.replace(neu, ziel)
        except OSError as fehler:
            logger.warning('Genesis 9: %s nicht schreibbar: %s', cls.DATEI, fehler)

    # ----------------------------------------------------------- nachrechnen

    @classmethod
    def auswahl(cls):
        u"""Die Anfragen der zuletzt offenen Seite; die gewählte Stufe vor dem Käfig — den zeigt der Browser
        bis dahin als Vorschau aus altem Code (`G9vorratanfrage`)."""
        with cls._schloss:
            eintraege = list(cls._laden().values())
        if not eintraege:
            return []
        juengste = max(e.get('zeit', 0.0) for e in eintraege)
        aus = [e for e in eintraege if juengste - e.get('zeit', 0.0) <= cls.FENSTER_S]
        return sorted(aus, key=lambda e: parse_qs(e.get('abfrage', '')).get('stufen') == ['0'])

    @classmethod
    def nachrechnen(cls):
        u"""Jede Anfrage der Auswahl einmal durch ihre Ansicht; ein Fehler steht im Log und hält die übrigen
        nicht an."""
        auswahl = cls.auswahl()
        for eintrag in auswahl:
            beginn = time.time()
            ziel = '%s?%s' % (eintrag['pfad'], eintrag['abfrage'])
            try:
                status = cls._schicken(eintrag)
            except Exception as fehler:  # noqa: BLE001 — nur Vorrat, die Seite rechnet sonst selbst
                logger.warning('Genesis 9: %s nach dem Neustart nicht nachgerechnet: %s', ziel, fehler)
                continue
            logger.info('Genesis 9: %s nach dem Neustart nachgerechnet (%d, %.1f s)', ziel, status,
                        time.time() - beginn)
        return len(auswahl)

    @classmethod
    def _schicken(cls, eintrag):
        u"""Die gemerkte Anfrage durch ihre Ansicht, mit der Stufe aus Abfrage und Keks (`Netzstufenwahl`) —
        ohne die übrigen Middlewares: Die Netzansichten lesen weder Nutzer noch Sitzung."""
        from asgiref.sync import async_to_sync, iscoroutinefunction
        from django.test import RequestFactory
        from django.urls import resolve

        from .netzstufenwahl import Netzstufenwahl
        adresse = eintrag['pfad'] + ('?' + eintrag['abfrage'] if eintrag['abfrage'] else '')
        extra = {'HTTP_' + k.upper().replace('-', '_'): v for k, v in eintrag['koepfe'].items()}
        extra['HTTP_HOST'] = '127.0.0.1'
        if eintrag['keks']:
            extra['HTTP_COOKIE'] = '%s=%s' % (Netzstufenwahl.KEKS, eintrag['keks'])
        fabrik = RequestFactory()
        if eintrag['methode'] == 'POST':
            anfrage = fabrik.post(adresse, data=eintrag['rumpf'].encode('utf-8'),
                                  content_type='application/json', **extra)
        else:
            anfrage = fabrik.get(adresse, **extra)
        treffer = resolve(eintrag['pfad'])
        ansicht = async_to_sync(treffer.func) if iscoroutinefunction(treffer.func) else treffer.func
        antwort = Netzstufenwahl(lambda r: ansicht(r, *treffer.args, **treffer.kwargs))(anfrage)
        return antwort.status_code
