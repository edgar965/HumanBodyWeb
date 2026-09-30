# -*- coding: utf-8 -*-
u"""G9kleidmischbau — die Antwort von „Kleidung – Generisch" bei einer Mischung: mehrere Stücke, in der Überdeckung EINE
Fläche.

Edgar, 30.09.2026: „die neuen Kleider sollen mischbar sein, wie das neue Haar" und „Gemischt wird nur an Hautstellen,
an denen beide Stücke vorhanden sind … In der Mischzone steht nur eine Fläche, und zwar die Mischung aus beiden Teilen
in dem angegebenen Verhältnis". Muster: `G9haarmischbau` — jedes Stück wird wie ein gewöhnliches gebaut
(`G9garderobeapi._kleid`, dieselbe Kette mit Formung, Lagen, Kollision), die Teile aller Stücke stehen danach in EINER
Antwort. Was hier anders ist: Die Stücke werden nicht ausgedünnt, sondern über die Haut gemischt (`G9kleidmischung`).

WAS HIER GESCHIEHT
==================
1. Jedes Stück mit Anteil wird gebaut; `vor_antwort` von `_kleid` hält dabei das ROHE Netz jedes Teils fest (noch vor
   der Kodierung: Punkte, Bindung, UV) — gemischt wird nicht an fertigen Bytes.
2. Die Teile, die an der Haut hängen (mit Bindung, keine Strähnen, keine Kappe), gehen als Höhenfelder in
   `G9kleidmischung`. Requisiten, Knöpfe an eigenen Knochen und Ähnliches bleiben, wie sie sind.
3. Das Ergebnis (gemischte Punkte, zugeschnitten auf die Punkte, die die Zone nicht anderen überlässt) wird neu kodiert
   und ersetzt das Teil in der Antwort.

Die Stücke sehen einander nicht als getragen: Sie liegen ja ineinander, das ist die Mischung. Ihr eigener Platz wird aus
`getragen` genommen — sonst hebt die Lagenrechnung (`G9lagen`) das eine Stück über das andere und mischt nichts mehr.

AUF EINER HUMANBODY-FIGUR
=========================
Derselbe Weg, nur mit dem Bauweg der Figur (`G9kleidhumanbody.antwort`, gleiche Form wie `_kleid`) und ihrer Haut als
Körper (`G9kleidhumanbody.bindungsflaeche`). Ein HumanBody-Netz trägt keine Bindung — die Hautstelle jedes Punkts
kommt dann ganz aus dieser Haut (`G9kleidmischflaeche.aus_netz`). Die Antwort trägt `figurart` und `absatz` wie die
eines einzelnen Stücks.

STOFFSCHWUNG (dForce)
=====================
Der Stoffschwung rechnet im Browser auf dem KÄFIG des ursprünglichen Stücks und kennt das Stück unter seiner eigenen
Kennung und Teilnummer (Bauplan `garderobe/<stück>/stoff/<n>/`). Deshalb trägt `teil['stoff']` hier zusätzlich
`stueck` und `nummer` — auch bei Teilen, die nicht gemischt werden — und bei einem gemischten Teil `misch`
(`G9kleidmischflaeche.stoff_misch`: welcher Punkt des ursprünglichen Netzes jeder bleibende Punkt war und um wie viel
er verschoben ist). Der Browser schwingt das ursprüngliche Netz und überträgt es darauf (`stoffmischung.js`).

WAS DIE MISCHUNG NICHT HAT
==========================
- Keine Textur-Mischung im Netz: Jeder Punkt behält seine UV und sein Material. Damit die Bilder trotzdem mischbar sind
  (Regler „Textur", Edgar 30.09.2026: „gesondert mit Regler … für die gesamte Bekleidung"), trägt jedes Teil je
  Gegenstück die Farbe dieses Stücks an der Stelle des Punkts und wie stark die Zone dort gilt (`fremd`,
  `G9kleidfarbe`). Der Browser mischt sie im Shader (`kleidfarbmischung.js`) — ein Reglerzug kostet den Server nichts.

WAS ES KOSTET
=============
Jedes Stück ein eigener Bau (wie bei Haaren), dazu die Mischung: eine Zuordnung zur Haut und je Paar eine Abfrage der
nächsten Nachbarn. Der Antwortvorrat merkt die GANZE Mischung unter ihrem Rumpf.
"""
import logging

import numpy as np
from django.http import HttpResponse
from Genesis9.garderobe import G9garderobe
from Genesis9.kleidfarbe import G9kleidfarbe
from Genesis9.kleidgenerisch import G9kleidgenerisch
from Genesis9.kleidmischflaeche import G9kleidmischflaeche
from Genesis9.kleidmischung import G9kleidmischung

from ..api.g9netzantwort import G9netzantwort
from ..daten.netzantwort import Netzantwort

__all__ = ['G9kleidmischbau']

logger = logging.getLogger('core')


class G9kleidmischbau:
    u"""Baut die gemischten Stücke aus der Aufteilung im Rumpf."""

    #: Der „Eintrag" für den Schlüssel des Antwortvorrats — die Bauart trägt ihre Fassung hier: ändert sich die
    #: Mischregel, gilt keine alte Antwort mehr (`~/.claude/rules/artefakte-benennen.md`).
    KENNZEICHEN = {'mischung': 'ueberdeckung', 'fassung': 3}
    #: Diese Felder des fertig kodierten Teils bleiben, wenn seine Geometrie neu kodiert wird.
    BLEIBT = ('name', 'stufen', 'knochen', 'zweiseitig')

    @classmethod
    def antwort(cls, rumpf, kleid, kennung, folge, uebergang, koerper, humanbody=False):
        u"""Das Antwort-Dict der Mischung — oder eine Fehlerantwort.

        `folge`: `[(stück, anteil, regler_stueck)]`, das stärkste zuerst (`G9kleidgenerisch.mischung`);
        `uebergang`: Breite des weichen Rands, Meter; `kleid`: `G9garderobeapi._kleid` oder auf einer HumanBody-Figur
        `G9kleidhumanbody.antwort` (hereingereicht, damit dieser Dienst die API nicht importiert — sie importiert
        ihn); `koerper`: liefert die `G9oberflaechenbindung` des Körpers; `humanbody`: die Netze tragen keine
        Bindung."""
        getragen, rang = cls._ohne_eigenes(rumpf, kennung)
        bauten = []
        for nummer, (stueck, anteil, regler) in enumerate(folge):
            erfasst = []
            aus = kleid(stueck, G9garderobe.eintrag(stueck) or {},
                        dict(rumpf, regler_stueck=regler, getragen=getragen, rang=rang),
                        vor_antwort=cls._sammler(erfasst))
            if isinstance(aus, HttpResponse):
                if nummer == 0:
                    return aus
                # Ein Stück, das nicht baut, kostet nicht die ganze Mischung.
                logger.warning('Kleidung – Generisch: %s nicht gebaut (%s)', stueck, getattr(aus, 'status_code', '?'))
                continue
            bauten.append((stueck, anteil, aus, erfasst))
        if len(bauten) > 1:
            cls._mischen(bauten, uebergang, koerper(), humanbody)
        return cls._zusammen(kennung, bauten)

    @staticmethod
    def _ohne_eigenes(rumpf, kennung):
        u"""`(getragen ohne den eigenen Eintrag und aufgelöst, rang)`. Ohne den eigenen Eintrag darin bleibt die
        Liste."""
        roh = rumpf.get('getragen')
        if not isinstance(roh, list):
            return roh, rumpf.get('rang')
        try:
            rang = int(rumpf.get('rang', len(roh)))
        except (TypeError, ValueError):
            rang = len(roh)
        if 0 <= rang < len(roh) and isinstance(roh[rang], dict) and roh[rang].get('kennung') == kennung:
            roh = roh[:rang] + roh[rang + 1:]
        return G9kleidgenerisch.getragene_aufloesen(roh), rang

    @staticmethod
    def _sammler(erfasst):
        u"""Der Eingriff je Teil für `_kleid`: das rohe Netz merken, unverändert weiter (`(nummer, netz) -> netz`)."""
        def sammeln(_nummer, netz):
            erfasst.append(netz)
            return netz
        return sammeln

    @staticmethod
    def _mischbar(netz, humanbody=False):
        u"""Nur ein Teil an der Haut — mit Bindung (HumanBody: ohne, dort trägt keines eine) und UV, weder Strang noch
        Kappe — lässt sich mischen."""
        return ((humanbody or netz.get('bindung') is not None)
                and netz.get('uv') is not None and not netz.get('art'))

    @classmethod
    def _mischen(cls, bauten, uebergang, koerper, humanbody=False):
        u"""Mischt die Teile der Bauten und ersetzt sie in `aus['teile']` (ein weggefallenes Teil wird `None`)."""
        flaechen = [G9kleidmischflaeche.aus_netz(stueck, nummer, netz, koerper)
                    for stueck, _anteil, _aus, erfasst in bauten
                    for nummer, netz in enumerate(erfasst) if cls._mischbar(netz, humanbody)]
        if len({f.stueck for f in flaechen}) < 2:
            return
        anteile = {stueck: anteil for stueck, anteil, _aus, _erfasst in bauten}
        reihenfolge = [b[0] for b in bauten]
        ergebnis = G9kleidmischung.mischen(flaechen, anteile, reihenfolge, uebergang)
        je_stueck = {stueck: (aus, erfasst) for stueck, _anteil, aus, erfasst in bauten}
        farben = cls._farben(flaechen, je_stueck)
        for f, (punkte, behalten, fremd) in zip(flaechen, ergebnis, strict=True):
            aus, erfasst = je_stueck[f.stueck]
            neu = f.neues_netz(erfasst[f.nummer], punkte, behalten, koerper)
            alt = aus['teile'][f.nummer]
            if neu is None:
                aus['teile'][f.nummer] = None
                continue
            teil = G9netzantwort.aus(neu)
            teil.update({feld: alt.get(feld) for feld in cls.BLEIBT})
            if alt.get('stoff'):
                quelle, versatz = f.stoff_misch(punkte, behalten)
                teil['stoff'] = dict(alt['stoff'], misch={
                    'quelle': Netzantwort.feld(quelle, 'quelle', typ=np.uint32),
                    'versatz': Netzantwort.feld(versatz, 'versatz', typ=np.float32)})
            eintraege = cls._fremd(fremd, farben, behalten, reihenfolge)
            if eintraege:
                teil['fremd'] = eintraege
            aus['teile'][f.nummer] = teil

    @staticmethod
    def _farben(flaechen, je_stueck):
        u"""`{stück: (M, 3)}`: die Farbe jedes Punkts aller mischbaren Teile eines Stücks, hintereinander in der
        Reihenfolge
        von `flaechen` — so, wie `G9kleidmischung` die Nummern der Gegenstücke zählt."""
        je = {}
        for f in flaechen:
            je.setdefault(f.stueck, []).append(G9kleidfarbe.farben(je_stueck[f.stueck][1][f.nummer]))
        return {stueck: np.vstack(liste) for stueck, liste in je.items()}

    @staticmethod
    def _fremd(fremd, farben, behalten, reihenfolge):
        u"""Je Gegenstück die Farbe an der Stelle jedes bleibenden Punkts (`farbe`, 3 Bytes) und wie stark die Zone dort
        gilt (`deckung`, 1 Byte) als Netzfelder (Binärpaket oder base64, `Netzfeld`) — der Shader mischt daraus die
        Textur (`kleidfarbmischung.js`). `rang` = Platz des Gegenstücks in der Mischung (0 = stärkstes): danach richten
        sich die Textur-Regler."""
        eintraege = []
        for stueck, nummer, gewicht, deckung in fremd:
            farbe = np.einsum('nk,nkj->nj', gewicht[behalten], farben[stueck][nummer[behalten]])
            byte = np.clip(farbe * 255.0 + 0.5, 0, 255).astype(np.uint8)
            deck = np.clip(deckung[behalten] * 255.0 + 0.5, 0, 255).astype(np.uint8)
            eintraege.append({'rang': reihenfolge.index(stueck), 'sorte': stueck,
                              'farbe': Netzantwort.feld(byte, 'farbe', typ=np.uint8),
                              'deckung': Netzantwort.feld(deck, 'deckung', typ=np.uint8)})
        return eintraege

    @staticmethod
    def _zusammen(kennung, bauten):
        u"""Die Teile aller Stücke hintereinander in EINER Antwort; der Browser hängt sie unter dem Eintrag ein."""
        teile, innen, aussen = [], [], []
        boden = stufen = figurart = absatz = None
        for rang, (stueck, anteil, aus, _erfasst) in enumerate(bauten):
            for nummer, teil in enumerate(aus.get('teile') or []):
                if teil is None:
                    continue
                teil['sorte'] = stueck
                teil['anteil_sorte'] = round(float(anteil), 4)
                teil['rang'] = rang
                if teil.get('stoff') is not None:
                    # Der Stoffschwung kennt das Teil unter SEINER Kennung und Nummer (Bauplan), nicht unter
                    # der des Sammeleintrags.
                    teil['stoff'] = dict(teil['stoff'], stueck=stueck, nummer=nummer)
                teile.append(teil)
            boden = aus.get('boden') if boden is None else max(boden, aus.get('boden') or boden)
            stufen = aus.get('stufen') if stufen is None else stufen
            figurart = figurart or aus.get('figurart')
            absatz = absatz or aus.get('absatz')
            for liste, neue in ((innen, aus.get('innen')), (aussen, aus.get('aussen'))):
                liste.extend(e for e in neue or [] if e not in liste)
        antwort = {'kennung': kennung, 'teile': teile, 'boden': boden, 'stufen': stufen,
                   'innen': innen, 'aussen': aussen, 'art': G9kleidgenerisch.ART,
                   'mischung': [{'stueck': s, 'anteil': round(float(a), 4)} for s, a, _aus, _e in bauten]}
        if figurart:
            antwort['figurart'] = figurart       # HumanBody: wie `G9kleidhumanbody.antwort`
            antwort['absatz'] = absatz
        return antwort
