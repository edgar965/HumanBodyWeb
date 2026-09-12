# -*- coding: utf-8 -*-
u"""Effektfilmlauf — `Filmlauf` fuer die Effekte-Pipeline.

Drei Unterschiede zum Videoweg der Szene, alle als Ueberschreibung:
Meldung zusaetzlich ins Protokoll (`Effekte: …`-Zeilen fuer den
`Effektbeobachter`), Bildgroesse aus dem Auftrag, H.264 ueber ffmpeg statt
`mp4v` aus OpenCV (Chrome spielt MPEG-4 Teil 2 nicht ab).

`filmlauf` importiert seine Nachbarn flach (`from hbfilm import Hbfilm`);
wer dieses Modul laedt, muss `TheatreJS/ModelPhysik` vorher in `sys.path`
haben — `figurfilm.py` tut das im Modulkopf.
"""
import json
import os
import shutil
import time

from filmlauf import Filmlauf

__all__ = ['Effektfilmlauf']


class Effektfilmlauf(Filmlauf):

    def __init__(self, auftrag_pfad, film):
        # VOR `super()`: der Vater meldet schon im Konstruktor („Start").
        self.film = film
        super().__init__(auftrag_pfad)

    def _melden(self, phase, anteil, fehler=None, fertig=False):
        super()._melden(phase, anteil, fehler=fehler, fertig=fertig)
        self.film.melden(phase, anteil)
        if fehler:
            print(fehler, flush=True)

    def stand(self):
        with open(self.fortschritt, encoding='utf-8') as datei:
            return json.load(datei)

    def _video(self, hb, fps):
        u"""Erst der Stoff (Newton), dann Bilder als PNG neben die Ausgabe,
        dann ffmpeg (H.264)."""
        from core.dienste.videokodierer import Videokodierer
        import cv2
        self._stoff(hb)
        bilder = os.path.join(self.film.ablage, 'bilder')
        os.makedirs(bilder, exist_ok=True)
        start = time.time()
        zahl = 0
        for nummer, bild in enumerate(hb.bilder_rendern(
                self.auftrag['breite'], self.auftrag['hoehe'])):
            # `cv2.imencode` + `open`: `cv2.imwrite` schreibt bei einem
            # Umlaut im Pfad nichts und wirft nicht (physik.md).
            ok, roh = cv2.imencode('.png', cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
            if not ok:
                raise ValueError(u'Bild %d nicht kodierbar' % nummer)
            with open(os.path.join(bilder, '%06d.png' % nummer), 'wb') as datei:
                datei.write(roh.tobytes())
            zahl += 1
        self.film.zeiten['rendern'] = round(time.time() - start, 1)
        start = time.time()
        Videokodierer.ausfuehren(Videokodierer.aus_bildfolge(
            bilder, self.auftrag['ziel'], fps=int(fps), crf=20))
        self.film.zeiten['kodieren'] = round(time.time() - start, 1)
        shutil.rmtree(bilder, ignore_errors=True)
        return self.auftrag['ziel'], zahl

    def _stoff(self, hb):
        u"""Die GarmentCode-Stuecke durch Newton — wenn `stoff` an ist."""
        if not self.film.p.stoff:
            return
        from django.conf import settings
        from effekte.figur.stoffauftrag import Stoffauftrag
        start = time.time()
        auftrag = Stoffauftrag(hb, self.film.ablage, self.film.p, self.film.melden,
                               self.film.stuecke)
        self.film.stoffbericht = auftrag.rechnen(
            str(settings.EFFEKTE_NEWTON_PYTHON), str(settings.EFFEKTE_NEWTON_SKRIPT),
            str(settings.EFFEKTE_WARP_CACHE))
        self.film.zeiten['stoff'] = round(time.time() - start, 1)
