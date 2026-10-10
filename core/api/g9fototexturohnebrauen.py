# -*- coding: utf-8 -*-
"""Die Kopfkachel eines gespeicherten Genesis-Modells OHNE die aufgemalten Brauen des Originals (10.10.2026).

    GET /api/character/genesis9-figur/fototextur-ohne-brauen/<Modell>/<Datei>/

Edgar, Asian: „ändern funktioniert nicht" — das Brauennetz des gewählten Stils lag auf der Braue, die in der Kachel des Imports
aufgemalt ist (`core/dienste/fotohautbrauen.py`). Der Browser holt diese Fassung der Kachel, sobald ein Brauenstil gewählt ist
(`Genesis9fototextur.gruppen`). Die Datei des Modells bleibt unberührt; die Retusche liegt unter `media/hauttexturen/ohne_brauen/`.

ASYNCHRON, mit der Rechnung in einem eigenen Faden: Alle synchronen Ansichten teilen sich in Daphne EINEN Faden (`studio.md`,
`thread_sensitive`); die erste Retusche einer 8192-px-Kachel (Dekodieren, Rechnen, Speichern) hätte jede andere Anfrage so lange
aufgehalten. Der Browser wartet auf diese eine Kachel, alles andere läuft weiter.
"""

import asyncio
import threading

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from ..dienste.fotohautbrauen import Fotohautbrauen
from ..dienste.modelltexturen import Modelltexturen

__all__ = ['G9fototexturohnebrauen']

#: Zwei Anfragen derselben Kachel (Szene und Studio zugleich) rechnen nicht doppelt.
_SCHLOSS = threading.Lock()


class G9fototexturohnebrauen:
    @staticmethod
    def _holen(modell, datei, hoch):
        """`(Bytes, Medientyp)` — im Faden: Pfad, verkleinerte Fassung (wie `G9fototextur`), Retusche, Lesen."""
        pfad = Modelltexturen.datei(modell, datei)
        if pfad is None or not pfad.is_file():
            return None
        if not hoch:
            klein = Modelltexturen.klein(pfad)
            if klein.is_file():
                pfad = klein
        with _SCHLOSS:
            pfad = Fotohautbrauen.datei(pfad)
        return pfad.read_bytes(), Modelltexturen.art(pfad)

    @staticmethod
    @require_GET
    async def datei(request, modell, datei):
        ergebnis = await asyncio.to_thread(G9fototexturohnebrauen._holen, modell, datei, request.GET.get('hoch') == '1')
        if ergebnis is None:
            raise Http404('Keine Textur %s/%s' % (modell, datei))
        inhalt, art = ergebnis
        antwort = HttpResponse(inhalt, content_type=art)
        # Die Retusche kann sich mit ihrer Fassung ändern, die Adresse nicht: der Browser fragt jedes Mal nach.
        antwort['Cache-Control'] = 'no-cache'
        return antwort
