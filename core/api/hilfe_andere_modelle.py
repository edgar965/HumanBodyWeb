# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Andere Modelle: hochauflösende Figuren im Vergleich.

Edgar (17.09.2026): „Mach eine Tabelle absteigend nach Qualität (Punkte,
Dreiecke)" — „mach diese Liste als HTML-Datei: Hilfe - Architektur - Andere
Modelle" — „ich brauche ganze Körper, mach getrennte Liste für nur Kopf".
Die Daten kommen aus `core.dienste.figurquellen` (Ganzkörper, Befund),
`figurkoepfe` (nur Kopf), `figurquellenlinks` (Adressen) und `figurbilder`
(Vorschaubilder aus `3DObjects/humanModels/`), nicht aus der Vorlage.

`Figurbild` liefert die Bilder: `vorschau` verkleinert (für das Raster),
`original` in voller Größe (ein Klick auf das Bild). Beide nehmen nur, was
`Figurbilder.quelle()` zulässt — ein fremder Pfad ist eine 404.
"""

from django.http import FileResponse, HttpResponseNotFound

from .hilfeseite import Hilfeseite
from ..dienste.figurbilder import Figurbilder
from ..dienste.figurkoepfe import Figurkoepfe
from ..dienste.figurquellen import Figurquellen
from ..dienste.figurquellenlinks import Figurquellenlinks


class AndereModelle(Hilfeseite):
    """Zwei Ranglisten, Karten je Kandidat mit Bildern und Links, Renderings."""

    template_name = "hilfe/andere_modelle.html"
    AKTIV = "hilfe_andere_modelle"

    @staticmethod
    def karten(zeilen):
        """Jede Zeile um ihre Adressen und Bilder ergänzt. `bildmuster` wählt
        aus einem geteilten Ordner (Eisko: Louise/FreakyHoody) die eigenen."""
        aus = []
        for e in zeilen:
            bilder = Figurbilder.dateien(e["ordner"])
            muster = (e.get("bildmuster") or "").lower()
            if muster:
                bilder = [b for b in bilder if muster in b.lower()]
            links = Figurquellenlinks.fuer(e.get("linkschluessel", e["ordner"]))
            # Zeilen- und Kartenklasse: eigene Figurarten rot, das MB-Lab-
            # Original (Ursprung des Netzes) orange — sonst keine.
            klasse = "am-eigen" if e.get("eigen") else "am-" + e["markierung"] if e.get("markierung") else ""
            aus.append(dict(e, links=links, bilder=bilder, klasse=klasse))
        return aus

    @staticmethod
    def lesehilfe(karten):
        """HumanBody- und Genesis-9-Zeile als Beispiel der Lesehilfe."""
        nach_ordner = {e["ordner"]: e for e in karten}
        return {"hb": nach_ordner["00_eigene_Renderings"], "g9": nach_ordner["11_Daz_Genesis9"]}

    def kontext(self):
        renderings = [
            (datei, Figurquellen.RENDERINGS.get(datei, datei))
            for datei in Figurbilder.dateien("00_eigene_Renderings")
        ]
        karten = self.karten(Figurquellen.rangliste())
        return {
            "stand": Figurquellen.STAND,
            "befund": Figurquellen.BEFUND,
            "rang_von": len(Figurquellen.mit_rang()),
            "karten": karten,
            "lesehilfe": self.lesehilfe(karten),
            "koepfe": self.karten(Figurkoepfe.rangliste()),
            "renderings": renderings,
            "ausgeschieden": Figurquellenlinks.AUSGESCHIEDEN,
            "bilderordner": str(Figurbilder.ORDNER),
        }


class Figurbild:
    """`GET …/vorschau/<ordner>/<datei>` und `…/bild/<ordner>/<datei>`."""

    CACHE = "public, max-age=86400"

    @staticmethod
    def vorschau(request, ordner, datei):
        pfad = Figurbilder.vorschau(ordner, datei)
        if pfad is None:
            return HttpResponseNotFound("Bild nicht bekannt: %s/%s" % (ordner, datei))
        return Figurbild._antwort(pfad, "image/jpeg")

    @staticmethod
    def original(request, ordner, datei):
        pfad = Figurbilder.quelle(ordner, datei)
        if pfad is None:
            return HttpResponseNotFound("Bild nicht bekannt: %s/%s" % (ordner, datei))
        return Figurbild._antwort(pfad, Figurbilder.typ(datei))

    @staticmethod
    def _antwort(pfad, typ):
        antwort = FileResponse(open(pfad, "rb"), content_type=typ)
        antwort["Cache-Control"] = Figurbild.CACHE
        return antwort
