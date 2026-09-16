# -*- coding: utf-8 -*-
u"""Auftragskennung — Datum und Uhrzeit als Adresse eines Auftrags.

Edgar, 16.09.2026: „änder die Verzeichnisnamen der Process Seiten …
Das Directory soll das Datum und Uhrzeit enthalten, in der Form
http://127.0.0.1:8081/process/2026.09.16.22.00.12/result". Die Seiten eines
Auftrags (`/process/<kennung>/`, `…/result/`, `…/start/`, `…/stop/`,
`…/delete/`) laufen seither über diese Kennung; die UUID bleibt Primär-
schlüssel, Ordnername unter `media/output/` und Adresse der Datei-Endpunkte
(`/api/bvh/<uuid>/` …) — gespeicherte Studio-Projekte und Szenen halten
diese Adressen, sie dürfen sich nicht ändern.

Die Kennung ist die ORTSZEIT (`TIME_ZONE`, Europe/Berlin) der Anlage, auf die
Sekunde. Legt etwas zwei Aufträge in derselben Sekunde an (der Pipeline-
vergleich tut das, Tests auch), bekommt der zweite die NÄCHSTE FREIE Sekunde:
Die Form bleibt, die Reihenfolge stimmt, und die Abweichung ist so groß wie
die Zahl der Aufträge in dieser Sekunde.
"""
import re
from datetime import timedelta

from django.utils import timezone


class Auftragskennung:

    FORMAT = '%Y.%m.%d.%H.%M.%S'
    #: Für den URL-Konverter und die Prüfung einer Zeichenkette.
    MUSTER = r'[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}'
    LAENGE = 19

    @classmethod
    def aus(cls, zeit):
        u"""Die Kennung zu einem Zeitpunkt (bewusste Zeit → Ortszeit)."""
        if timezone.is_aware(zeit):
            zeit = timezone.localtime(zeit)
        return zeit.strftime(cls.FORMAT)

    @classmethod
    def frei(cls, zeit, belegt):
        u"""Die erste freie Kennung ab `zeit`; `belegt(kennung)` sagt, ob es
        sie schon gibt. Sekundenbruchteile spielen keine Rolle."""
        zeit = zeit.replace(microsecond=0)
        while belegt(cls.aus(zeit)):
            zeit += timedelta(seconds=1)
        return cls.aus(zeit)

    @classmethod
    def passt(cls, text):
        return bool(text) and re.fullmatch(cls.MUSTER, text) is not None

    @classmethod
    def fuer(cls, auftrag):
        u"""Die Kennung für einen Auftrag, der noch keine hat — aus seiner
        Anlagezeit, sonst aus jetzt; frei gegenüber allen anderen Aufträgen."""
        zeit = auftrag.created_at or timezone.now()
        andere = type(auftrag).objects.exclude(pk=auftrag.pk)
        return cls.frei(zeit, lambda k: andere.filter(kennung=k).exists())
