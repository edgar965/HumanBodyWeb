# -*- coding: utf-8 -*-
u"""G9texturfassung — ein Bild der Daz-Bibliothek so, wie die Seite es bestellt: unverändert, verkleinert (`?kante=1024`) oder als GPU-Block (`?format=bc`), 19.10.2026.

Edgar (19.10.2026, nach der Untersuchung „ein Bildersatz kostet 1,7–2,8 s, weil 15 von 22 Bildern 4096² sind“): „mach alle 3, per Option einstellbar, default: A“ —
Einstellungen → Mesh3D-AI (`Mesh3daitexturwahl`). Die Seite hängt ihre Wahl an die Adresse jedes Bildes (`gemeinsam/texturweg.js`); dieselbe Adresse beantworten der
Einzelabruf (`G9garderobeapi.textur`) und das Bündel (`G9texturbuendelapi`). Ohne Zusatz kommt das Original wie bisher.

    kante=512|1024|2048   `G9texturkopie` (Weg A)
    format=bc             `G9texturblock` (Weg C); geht vor `kante`
    format=uastc          `G9texturbasis` (UASTC, /Charakter/, `Szenentexturwahl`); `&raum=lin` für Bilder ohne Farbe (Normalen, Rauheit …) — bis die
                          Fassung kodiert ist, kommt der Block von Weg C
Weg B (volle Bilder, eines nach dem anderen hochladen) braucht vom Server nichts.
"""
from django.http import HttpResponseNotFound

from Genesis9.material import G9material

from .auftragsdatei import Auftragsdatei
from .g9texturbasis import G9texturbasis
from .g9texturblock import G9texturblock
from .g9texturkopie import G9texturkopie

__all__ = ['G9texturfassung']


class G9texturfassung:
    u"""Wahl aus der Anfrage, Datei dazu, Antwort."""

    KANTEN = (512, 1024, 2048)

    @classmethod
    def wahl(cls, abfrage):
        u"""`(kante, form)` aus den Parametern der Anfrage: `kante` eine von `KANTEN` oder 0, `form` 'bc', 'uastc', 'uastc-lin' oder ''."""
        if (abfrage.get('format') or '') == 'bc':
            return 0, 'bc'
        if (abfrage.get('format') or '') == 'uastc':
            return 0, 'uastc-lin' if abfrage.get('raum') == 'lin' else 'uastc'
        try:
            kante = int(abfrage.get('kante') or 0)
        except ValueError:
            kante = 0
        return (kante if kante in cls.KANTEN else 0), ''

    @staticmethod
    def marke(kante, form):
        u"""Teil des ETags im Bündel: Wahl und Fassung des Rechenwegs (das Original geht dort mit Größe und Zeit ein)."""
        return 'k%d|f%s|%d|%d|%d' % (kante, form, G9texturkopie.FASSUNG, G9texturblock.FASSUNG, G9texturbasis.FASSUNG)

    @staticmethod
    def stand(pfad, kante=0, form=''):
        u"""Was sich an der Antwort für `pfad` ändert, ohne dass sich das Original ändert: bei UASTC, ob die Fassung schon liegt (sonst kommt der Block) —
        Teil des ETags im Bündel, sonst bekäme der Browser den Block für immer als 304. Sonst ''."""
        if not form.startswith('uastc'):
            return ''
        original = G9material.datei(pfad)
        return 'u1' if original is not None and G9texturbasis.liegt(original, str(pfad), form == 'uastc-lin') else 'u0'

    @staticmethod
    def datei(pfad, kante=0, form=''):
        u"""`(Pfad, Art)` dessen, was ausgeliefert wird — `(None, None)`, wenn es das Bild nicht gibt oder keine Fassung entsteht."""
        original, art = G9material.datei(pfad), G9material.bildart(pfad)
        if original is None or not art:
            return None, None
        if form == 'bc':
            return G9texturblock.fuer(original, str(pfad))
        if form.startswith('uastc'):
            return G9texturbasis.fuer(original, str(pfad), form == 'uastc-lin')
        if kante:
            return G9texturkopie.fuer(original, str(pfad), art, kante)
        return original, art

    @classmethod
    def antwort(cls, request, pfad):
        u"""Der Einzelabruf: Datei mit ETag (`Auftragsdatei`, unverändert → 304) oder 404."""
        datei, art = cls.datei(pfad, *cls.wahl(request.GET))
        if datei is None:
            return HttpResponseNotFound('Texture not found')
        return Auftragsdatei.antwort(request, datei, art=art)
