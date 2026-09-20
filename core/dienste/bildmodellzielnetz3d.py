# -*- coding: utf-8 -*-
"""Bildmodellzielnetz3d — das Zielnetz für das 3D-Popup, je Reglerzug neu geformt.

Edgar (20.09.2026): „brauche ich eine Möglichkeit, das 3D Modell interaktiv
anzupassen wenn ich die Pfeile ändere. also sowas wie die Morph slider bei
Genesis … ein neues Popup, mit dem ich das Genesis Modell sehe, das ich mit
diesen Pfeilen als Morph Slider modellieren kann? Dann sehe ich nämlich gleich
die ‚Donauwellen' oder andere Fehler."

Gemessen an Ursula (25.182 Punkte): der Umriss der Fotos braucht 4,2 s, die
Proportionsformung 64 ms. Darum liegt das Ziel NACH dem Umriss einmal in der
Ablage (`ziel_umriss.npz`, mit `stand` aus der Zeit von `ziel.npz`, der Option
und den Bildern — ändert sich eines, wird neu gerechnet), und jeder Zug im
Popup formt nur noch die Proportionen darauf (`G9proportionsformung`, wie im
Lauf: `Bildmodellzielproportionen.ziele_m(ohne_foto=True)` — Eingaben, keine
Fotomaße, weil der Umriss schon Zeile für Zeile geformt hat). Ungepaarte
Punkte (Mundhöhle, Augenhöhle) nehmen die Lage des Modells, wie im Bild
(`Bildmodellproportionen`), sonst stünde ein Klotz im Mund. Nichts wird
abgelegt außer dieser Grundlage — `ziel_prop.npz` schreibt erst „Übernehmen".

POST `api/bildmodell/<id>/zielnetz3d/` mit `{proportionen: {schluessel: cm},
netz: true}` → `{ok, punkte (base64 float32, N×3, Meter, Y oben), anzahl,
hoehe_cm, bericht: {schluessel: {vorher, ziel, nachher}} in cm, dauer_ms;
mit `netz` dazu `dreiecke` (base64 uint32) und `gewicht` (base64 float32)}`.
"""

import base64
import hashlib
import json
import logging
import time

import numpy as np

from .bildmodellanpassung import Bildmodellanpassung
from .bildmodelloptionen import Bildmodelloptionen
from .bildmodellumriss import Bildmodellumriss
from .bildmodellzielproportionen import Bildmodellzielproportionen

logger = logging.getLogger('core')

__all__ = ['Bildmodellzielnetz3d']


class Bildmodellzielnetz3d:
    DATEI = 'ziel_umriss.npz'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage
        self.optionen = Bildmodelloptionen.pruefen(job.optionen)
        self.anpassung = Bildmodellanpassung(job, ablage, self.optionen)

    # ---------------------------------------------------------- Grundlage

    def stand(self):
        """Wovon die Grundlage abhängt: Zielnetz, Option `umriss`, die Bilder (Profile, Rigs)."""
        ziel = self.ablage.ergebnis() / Bildmodellanpassung.ZIEL
        if not ziel.is_file():
            raise RuntimeError('Zielnetz fehlt — Schritt „ziel" zuerst')
        bilder = hashlib.md5(json.dumps(self.job.bilder, sort_keys=True, default=str).encode()).hexdigest()
        return '%d|%s|%s' % (ziel.stat().st_mtime_ns, Bildmodellumriss.an(self.optionen, self.job), bilder)

    def grundlage(self):
        """`(punkte, gewicht, gelenke)` nach dem Umriss — aus der Ablage, sonst gerechnet und abgelegt."""
        stand = self.stand()
        pfad = self.ablage.ergebnis() / self.DATEI
        if pfad.is_file():
            with np.load(pfad) as d:
                if str(d['stand']) == stand:
                    gelenke = {str(n): d['gelenke'][i] for i, n in enumerate(d['gelenknamen'])}
                    return d['punkte'].astype(float), d['gewicht'].astype(float), gelenke
        t = time.perf_counter()
        punkte, gewicht, gelenke = self.anpassung._ziel_laden(roh=True)
        punkte, gelenke, _ = Bildmodellumriss(self.job, self.optionen).formen(punkte, gelenke)
        punkte = self._ungepaarte_fuellen(np.asarray(punkte, float), gewicht)
        np.savez_compressed(
            pfad, stand=stand, punkte=punkte.astype(np.float32), gewicht=np.asarray(gewicht, np.float32),
            gelenknamen=np.array(list(gelenke)), gelenke=np.array([gelenke[k] for k in gelenke], np.float32),
        )
        logger.info('Bildmodell %s: Grundlage fürs 3D-Popup abgelegt (%.1f s)', self.job.kennung,
                    time.perf_counter() - t)
        return punkte, np.asarray(gewicht, float), gelenke

    def _ungepaarte_fuellen(self, punkte, gewicht):
        """Punkte ohne Paarung (Gewicht 0) aus dem Modell des Ergebnisses — wenn es eines gibt."""
        stellung = self.anpassung.stellung()
        ok = np.asarray(gewicht) > 0
        if ok.all() or not stellung:
            return punkte
        from .bildmodellproportionen import Bildmodellproportionen

        modell, _ = Bildmodellproportionen(self.job, self.ablage, stellung, None).modell()
        if len(modell) != len(punkte):
            return punkte
        return np.where(ok[:, None], punkte, modell)

    # ------------------------------------------------------------- Formen

    def formen(self, proportionen):
        """`(punkte, bericht)` — die Grundlage mit den Werten des Popups geformt, Bericht in cm."""
        punkte, gewicht, gelenke = self.grundlage()
        optionen = dict(self.optionen)
        optionen['proportionen'] = Bildmodelloptionen.proportionen_pruefen(proportionen)
        ziele, _ = Bildmodellzielproportionen(self.job, self.ablage, optionen).ziele_m(ohne_foto=True)
        if not ziele:
            return punkte, {}
        from Genesis9.proportionsformung import G9proportionsformung

        p, _, bericht = G9proportionsformung().formen(punkte, gelenke, ziele, gewicht > 0)
        aus = {k: {n: (round(b[n] * 100, 1) if b.get(n) is not None else None)
                   for n in ('vorher', 'ziel', 'nachher')}
               for k, b in bericht.items()}
        return np.asarray(p, float), aus

    def antwort(self, proportionen, mit_netz=False):
        """Die Antwort des Endpunkts — Punkte als base64, mit `mit_netz` auch Dreiecke und Gewicht."""
        t = time.perf_counter()
        punkte, bericht = self.formen(proportionen)
        aus = {
            'ok': True,
            'punkte': self._b64(punkte, np.float32),
            'anzahl': int(len(punkte)),
            'hoehe_cm': round(float(punkte[:, 1].max() - punkte[:, 1].min()) * 100, 1),
            'bericht': bericht,
        }
        if mit_netz:
            from Genesis9.basisnetz import G9basisnetz

            q = G9basisnetz.holen().vierecke
            aus['dreiecke'] = self._b64(np.concatenate([q[:, [0, 1, 2]], q[:, [0, 2, 3]]]), np.uint32)
            aus['gewicht'] = self._b64(self.grundlage()[1], np.float32)
        aus['dauer_ms'] = round((time.perf_counter() - t) * 1000)
        return aus

    @staticmethod
    def _b64(feld, art):
        return base64.b64encode(np.ascontiguousarray(feld, dtype=art).tobytes()).decode('ascii')
