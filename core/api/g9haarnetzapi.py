# -*- coding: utf-8 -*-
"""G9haarnetzapi — Haar und Bart der Haar-Engine eines gespeicherten Genesis-Modells (23.11.2026, `Modellhaarnetze`).

GET /api/character/genesis9-figur/haarnetz/<name>/netz/          das Anzeigenetz (Binärpaket wie ein Stück eines Tests, `Meshgenesisflaechennetz`, zstd über `Netzpackung`)
GET /api/character/genesis9-figur/haarnetz/<name>/bild/<datei>   sein Deckkraftbild (`m0_alpha.jpg`)
`<name>` = `<Stück>_<Stand>` (`Modellhaarnetze.NAME`); der Browser holt beides über `Meshgenesisflaechennetz.holen` (`genesis9haarnetze.js`).
"""

from django.http import Http404
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesisflaechennetz import Meshgenesisflaechennetz
from ..dienste.modellhaarnetze import Modellhaarnetze
from ..dienste.netzpackung import Netzpackung

__all__ = ['G9haarnetzapi']


class G9haarnetzapi:

    @staticmethod
    @require_GET
    def netz(request, name):
        ordner = Modellhaarnetze.ordner(name)
        antwort = Netzpackung.flaechennetz(request, str(ordner)) if ordner else None
        if antwort is None:
            raise Http404('Kein Haarnetz %s' % name)
        return antwort

    @staticmethod
    @require_GET
    def bild(request, name, datei):
        ordner = Modellhaarnetze.ordner(name)
        pfad = Meshgenesisflaechennetz.bild(str(ordner), datei) if ordner else None
        if pfad is None:
            raise Http404('Kein Bild %s im Haarnetz %s' % (datei, name))
        return Auftragsdatei.antwort(request, pfad)
