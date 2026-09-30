# -*- coding: utf-8 -*-
u"""G9haarmischbau — die Antwort von „Haar – Generisch": mehrere Frisuren, ausgedünnt, in einer.

Edgar, 30.09.2026: „dann ist das generische Haar aber nutzlos! Überlege dir eine Lösung wie
ich die mischen kann!" und „wenn ich einen anteil eines neuen haares hinzumische, soll der
anteil der anderen proportional sinken, so dass die Summe aller Anteile immer 100% ist".

WAS HIER GESCHIEHT
==================
`G9haargenerisch.mischung` liefert die Aufteilung (`[(kennung, anteil, regler)]`, Summe 1,
Hauptsorte zuerst). Jede Sorte wird wie ein gewöhnliches Stück gebaut
(`G9garderobeapi._kleid` — dieselbe Kette mit Formung, Lagen, Kollision), aber jedes ihrer
Teile vor der Kodierung auf ihren Anteil ausgedünnt (`G9haarmischung.ausduennen`). Die Teile
aller Sorten stehen dann hintereinander in EINER Antwort. Der Browser hängt sie unter
`haar_generisch/0…n` ein — die Farbe des Eintrags (`Umfaerbung`) färbt so alle zugleich.

Auf einer HumanBody-Figur ist `kleid` deren Bauweg (`G9kleidhumanbody.antwort`, derselbe
Eingriff je Teil); Edgar, 30.09.2026: „auf einer HumanBody soll das haar genau so gemischt
werden". Der Browser hängt die Teile dort unter `daz_haar_generisch/0…n` ein.
Dieselbe Saat je Sorte und Teil heißt: dieselben Strähnen auf beiden Figurarten.

DIE KAPPE
=========
Ein eigenes Kappen-Teil (`art == 'kappe'`, Pixie: 1.084 von 1.085 Punkten in EINER Insel)
kommt nur von der Hauptsorte und dort ganz. Eine Beimischung bringt keine mit: zwei Kappen
übereinander flimmern, und eine ausgedünnte Kappe gibt es nicht (sie ist ein Stück). Bei
Flächenhaar ohne eigenes Kappen-Teil behält die Hauptsorte ihre größte Insel
(`groesste_behalten`).

WAS DIE BEIMISCHUNG NICHT HAT
=============================
- Keinen Stoffschwung: dForce rechnet auf den Käfigpunkten des GANZEN Netzes; die gibt es
  nach dem Zuschnitt nicht mehr (`G9haarmischung._zuschneiden` nimmt `stoff` heraus).
- Keine Kollision gegen die anderen Sorten: Jede Sorte liegt gegen Körper und getragene
  Stücke, nicht gegen ihre Mitsorten. Das ist gewollt — ihre Strähnen sollen sich ja
  durchdringen, das IST die Mischung.

WAS ES KOSTET
=============
Jede Sorte ist ein eigener Bau (warm 0,7–1,5 s auf der Käfigstufe, kalt bis 20 s — gemessen
30.09.2026). Der Antwortvorrat merkt die GANZE Mischung unter ihrem Rumpf; ein zweiter Zug
an denselben Anteilen kommt aus dem Vorrat. `HOECHSTENS` in `G9haargenerisch` begrenzt die
Zahl der Sorten.
"""
import logging

from django.http import HttpResponse, JsonResponse
from Genesis9.garderobe import G9garderobe
from Genesis9.haargenerisch import G9haargenerisch
from Genesis9.haarmischung import G9haarmischung

__all__ = ['G9haarmischbau']

logger = logging.getLogger('core')


class G9haarmischbau:
    u"""Baut die gemischte Frisur aus der Aufteilung im Rumpf."""

    #: Der „Eintrag" für den Schlüssel des Antwortvorrats. Welche Sorten gemischt werden,
    #: steht im Rumpf (`regler_stueck`); die Bauart selbst trägt ihre Fassung hier —
    #: ändert sich die Mischregel, gilt keine alte Antwort mehr
    #: (`~/.claude/rules/artefakte-benennen.md`).
    KENNZEICHEN = {'mischung': 'dichte', 'fassung': 1}

    @classmethod
    def antwort(cls, rumpf, kleid):
        u"""Das Antwort-Dict der Mischung — oder eine Fehlerantwort.

        `kleid` ist `G9garderobeapi._kleid` oder auf einer HumanBody-Figur
        `G9kleidhumanbody.antwort` (hereingereicht, damit dieser Dienst die API nicht
        importiert — sie importiert ihn)."""
        folge = G9haargenerisch.mischung(rumpf.get('regler_stueck'))
        if not folge:
            return JsonResponse({'fehler': 'Keine Frisur in der Garderobe'}, status=404)
        teile, innen, aussen = [], [], []
        boden = stufen = figurart = None
        for rang, (kennung, anteil, regler) in enumerate(folge):
            haupt = rang == 0
            eintrag = G9garderobe.eintrag(kennung) or {}
            aus = kleid(kennung, eintrag, dict(rumpf, regler_stueck=regler),
                        vor_antwort=cls._ausduenner(kennung, anteil, haupt, G9haarmischung.ort_aus(regler)))
            if isinstance(aus, HttpResponse):
                if haupt:
                    return aus
                # Eine Beimischung, die nicht baut, kostet nicht die ganze Frisur.
                logger.warning('Haar – Generisch: Beimischung %s nicht gebaut (%s)',
                               kennung, getattr(aus, 'status_code', '?'))
                continue
            for teil in aus.get('teile') or []:
                teil['sorte'] = kennung
                teil['anteil_sorte'] = round(float(anteil), 4)
                teile.append(teil)
            boden = aus.get('boden') if boden is None else max(boden, aus.get('boden') or boden)
            stufen = aus.get('stufen') if stufen is None else stufen
            figurart = figurart or aus.get('figurart')
            cls._dazu(innen, aus.get('innen'))
            cls._dazu(aussen, aus.get('aussen'))
        antwort = {'kennung': G9haargenerisch.KENNUNG, 'teile': teile, 'boden': boden,
                   'stufen': stufen, 'innen': innen, 'aussen': aussen, 'art': G9haargenerisch.ART,
                   'mischung': [{'sorte': k, 'anteil': round(float(a), 4)} for k, a, _ in folge]}
        if figurart:
            antwort['figurart'] = figurart      # HumanBody: wie `G9kleidhumanbody.antwort`
        return antwort

    @staticmethod
    def _dazu(liste, neue):
        for eintrag in neue or []:
            if eintrag not in liste:
                liste.append(eintrag)

    @staticmethod
    def _ausduenner(kennung, anteil, haupt, ort=None):
        u"""Der Eingriff je Teil für `_kleid` — `(nummer, netz) -> netz | None`. `ort` (30.09.2026, nachts): die
        Strähnen dieser Sorte nur in einem Sektor/Band (`G9haarmischung.eignung`); die Kappe bleibt ganz."""
        def eingreifen(nummer, netz):
            if netz.get('art') == 'kappe':
                return netz if haupt else None
            return G9haarmischung.ausduennen(netz, anteil, '%s/%d' % (kennung, nummer),
                                             groesste_behalten=haupt and not ort, ort=ort)
        return eingreifen
