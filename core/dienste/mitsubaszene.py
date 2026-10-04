# -*- coding: utf-8 -*-
"""Mitsubaszene — die Teile eines Modells als Mitsuba-3-Szene, gerendert auf der GRAFIKKARTE (01.10.2026).

Edgar: „Cycles oder so was soll auf GPU laufen, auf CPU ist das nichts" — „dann schau nach einem Ersatz für pyrender,
das alles kann, inkl. Cycles". Mitsuba 3 (EPFL, `pip install mitsuba`, Variante `cuda_ad_rgb`) ist ein Pfadverfolger wie
Cycles, rechnet mit OptiX auf der Karte und bringt, was pyrender fehlte: Normalkarten (gebackene Falten, Daz-Normalen),
echte Strähnen als Kurven (Radius je Punkt aus dem Profil), weiche Schatten, Verdeckung, Kantenglättung — und es ist
differenzierbar (Fotos ↔ Textur/Form ließen sich später direkt optimieren). Gemessen an der Grundfigur mit Pixie-
Stranghaar (236.136 Punkte als Kurven) und einer Normalkarte: Szene 0,3 s, erstes Bild 0,6 s (Kernel), danach
1024 × 1536 mit 64 Abtastungen 0,04 s; Kopf 512² mit Kurven 1,1 s (neu) / 0,11 s (zweite Ansicht). Gegen pyrender
(Grundfigur + Viereck, 0/30/90/180°): IoU der Umrisse 0,984–0,988, Schwerpunkt ≤ 0,3 Pixel daneben, UV-Richtung gleich.

**Die Kamera ist die von `Genesishaarrender`** — orthografisch, Mitte, halbe Bildhöhe `halb` in Metern, Drehung um die
senkrechte Achse (0 = von vorn, positiv zur linken Seite der Figur). `Fotoprojektion` und `Sichtkoerper` rechnen diese
Abbildung nach (`sx = B/2 + (c·x − s·z)·ppm`); Mitsubas Orthografie bildet [−1, 1] × [−1/a, 1/a] (a = B/H) auf das Bild
ab, also skaliert `to_world` gleichmäßig mit `halb · a`. Abgetastet wird über die Fläche des Pixels wie bei pyrender.

Zwei Arten: das **Bild** (Pfadverfolgung, `SPP` Abtastungen, sRGB, Alpha = Deckung) und die **Kennung** (Teilmasken:
die Albedo als Ausgabe mit EINER Abtastung je Pixel — jeder Pixel trägt genau die Kennfarbe eines Teils, ohne Licht,
ohne Mischkante). Die Szene wird einmal je Teilesatz gebaut; jede Ansicht ist nur ein neuer Sensor.

Dr.Jit legt seinen Kernel- und OptiX-Cache unter `settings.MITSUBA_CACHE` (`DRJIT_CACHE_DIR`, gesetzt VOR dem Import) —
ohne das landet er unter %TEMP%\\drjit auf C:.
"""

import logging
import os

import numpy as np

from .mitsubamaterial import Mitsubamaterial

logger = logging.getLogger('core')

__all__ = ['Mitsubaszene']


class Mitsubaszene:
    VARIANTE = 'cuda_ad_rgb'
    #: Abtastungen je Pixel: ein Quadrat (12², sonst rundet `multijitter` mit Warnung auf, 128 → 132). Gemessen 03.10.2026 mit
    #: `_wegwerf/randy/haut_spp_probe.py` (CPU, scalar_rgb, teilverdeckte Hautkugel unter Himmel 0,8 + Richtlicht 1,4): Rauschen
    #: independent/64 = 5,25 % des Mittels, multijitter/64 = 2,49 %, multijitter/144 = 1,73 % — die Körnung der Haut im Runden-
    #: bild (Randy, Runde 42) ist dieses Abtastrauschen, nicht die Hauttextur (HF der Kacheln 0,5–0,9 Stufen).
    SPP = 144
    #: Strahldichte des gleichmäßigen Himmels (linear) und das Richtlicht von oben vorn — fest in der Welt, für alle
    #: Ansichten gleich (pyrender hatte ein Kopflicht je Ansicht; eine Tönung soll in jeder Ansicht dieselbe sein).
    HIMMEL = 0.8
    LICHT = 1.4
    RICHTUNG = (-0.25, -0.8, -0.55)
    MAX_TIEFE = 6
    _mi = None
    _fehler = None

    # ------------------------------------------------------------ Laden

    @classmethod
    def mitsuba(cls):
        """Das Mitsuba-Modul (Variante gesetzt) oder None — dann sagt `fehler`, warum (kein Paket, keine CUDA)."""
        if cls._mi is None and cls._fehler is None:
            try:
                from django.conf import settings
                ordner = getattr(settings, 'MITSUBA_CACHE', None)
                if ordner is not None:
                    os.makedirs(ordner, exist_ok=True)
                    os.environ.setdefault('DRJIT_CACHE_DIR', str(ordner))
                import mitsuba as mi
                mi.set_variant(cls.VARIANTE)
                cls._mi = mi
            except Exception as fehler:  # noqa: BLE001 — ohne Mitsuba rendert pyrender weiter, gemeldet im Log
                cls._fehler = '%s: %s' % (type(fehler).__name__, fehler)
                logger.warning('Mitsuba nicht verfügbar (%s) — Renderer bleibt pyrender', cls._fehler)
        return cls._mi

    # ------------------------------------------------------------- Bau

    def __init__(self, teile, kennung=False, kante=1024):
        """`teile`: `[(punkte, dreiecke, farbe sRGB 0…1, extra)]`; `extra` None oder ein Wörterbuch mit `uv` + `gruppen`
        (`[{ab, anzahl, albedo, normalen, normalenachse, faktor}]` in Dreiecken) und/oder `kurven` (`punkte`,
        `laengen`, `reihe`, `radius` je Punkt in m). `kennung`: Kennfarbenbild für die Teilmasken."""
        mi = self.mitsuba()
        if mi is None:
            raise RuntimeError('Mitsuba nicht verfügbar: %s' % self._fehler)
        self.mi = mi
        self.kennung = bool(kennung)
        self.kante = int(kante)
        #: `[(form, teil, nummern, dreiecke, gruppe)]` je Netz — für `punkte_setzen` (Film: dieselben Netze, neue Lage
        #: je Bild; `gruppe` = Nahtkopien aus der Ruhelage).
        self._netzliste = []
        formen = {}
        for i, (punkte, dreiecke, farbe, extra) in enumerate(teile):
            extra = extra or {}
            if extra.get('kurven') is not None and not self.kennung:
                formen['t%d_kurven' % i] = self._kurven(extra['kurven'], Mitsubamaterial.haar(farbe))
                continue
            self._netze(formen, 't%d' % i, punkte, dreiecke, farbe, extra)
        szene = {'type': 'scene', 'integrator': self._integrator()}
        if not self.kennung:
            szene['himmel'] = {'type': 'constant', 'radiance': {'type': 'rgb', 'value': self.HIMMEL}}
            szene['licht'] = {'type': 'directional', 'direction': list(self.RICHTUNG),
                              'irradiance': {'type': 'rgb', 'value': self.LICHT}}
        szene.update(formen)
        self.szene = mi.load_dict(szene)

    def _integrator(self):
        pfad = {'type': 'path', 'max_depth': 1 if self.kennung else self.MAX_TIEFE, 'hide_emitters': True}
        return {'type': 'aov', 'aovs': 'alb:albedo', 'integrator': pfad} if self.kennung else pfad

    def _netze(self, formen, name, punkte, dreiecke, farbe, extra):
        dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        if not len(dreiecke):
            return
        # Nahtkopien EINMAL je Teil suchen (je Teilnetz und doppelt kostete es 6,3 s je Runde, 01.10.2026).
        lage = Mitsubamaterial.gruppen(punkte)
        if self.kennung:
            formen[name] = self._netz(name, punkte, dreiecke, Mitsubamaterial.kennung(farbe), lage=lage)
            return
        uv = extra.get('uv')
        gruppen = [g for g in (extra.get('gruppen') or []) if g.get('albedo') is not None or g.get('opazitaet') is not None] if uv is not None else []
        belegt = np.zeros(len(dreiecke), dtype=bool)
        for k, g in enumerate(gruppen):
            ab, anzahl = int(g['ab']), int(g['anzahl'])
            wahl = dreiecke[ab:ab + anzahl]
            if not len(wahl):
                continue
            try:
                bsdf = (Mitsubamaterial.textur(g['albedo'], g.get('faktor', (1.0, 1.0, 1.0)), g.get('normalen'),
                                               self.kante, int(g.get('normalenachse') or 1), g.get('metall'), g.get('rauheit'))
                        if g.get('albedo') is not None else Mitsubamaterial.flach(g.get('faktor', farbe)))
                if g.get('alpha') is not None:                   # Haarkarten: Strähnen statt geschlossener Flächen
                    bsdf = Mitsubamaterial.maske(bsdf, g['alpha'], self.kante)
                if g.get('opazitaet') is not None and float(g['opazitaet']) < 0.999:      # Regler „Transparenz“ (`G9kleidtransparenz`)
                    bsdf = Mitsubamaterial.durchsicht(bsdf, g['opazitaet'])
            except (OSError, ValueError) as fehler:
                logger.warning('Mitsuba: Bild %s nicht lesbar (%s) — Gruppe flach', g.get('albedo'), fehler)
                continue
            belegt[ab:ab + anzahl] = True
            formen['%s_g%d' % (name, k)] = self._netz('%s_g%d' % (name, k), punkte, wahl, bsdf, uv, lage)
        if not belegt.all():
            formen[name] = self._netz(name, punkte, dreiecke[~belegt], Mitsubamaterial.flach(farbe), lage=lage)

    def punkte_setzen(self, teile):
        """Dieselben Netze, neue Punkte (Film: je Bild gehäutet) — Lage und Normalen tauschen statt neu bauen. Kurven
        bleiben, wo sie sind (der Film rendert Stranghaar als Band)."""
        werte = self.mi.traverse(self.szene)
        for form, teil, nummern, dreiecke, gruppe in self._netzliste:
            p = np.asarray(teile[teil][0], dtype=np.float64)[nummern]
            werte['%s.vertex_positions' % form] = self.mi.Float(np.ascontiguousarray(p, dtype=np.float32).ravel())
            werte['%s.vertex_normals' % form] = self.mi.Float(Mitsubamaterial.normalen(p, dreiecke, gruppe).ravel())
        werte.update()

    def _netz(self, name, punkte, dreiecke, bsdf, uv=None, lage=None):
        """Ein Mitsuba-Netz aus den Punkten, die die Dreiecke brauchen, gemerkt für `punkte_setzen` (`lage`: Nahtkopien
        des ganzen Teils, `Mitsubamaterial.gruppen`). UV von Daz (v nach oben, OBJ) → Mitsuba (v nach unten: Zeile 0 des
        Bildes bei v = 0)."""
        mi = self.mi
        nummern, neu = np.unique(np.asarray(dreiecke, dtype=np.int64).ravel(), return_inverse=True)
        p = np.asarray(punkte, dtype=np.float64)[nummern]
        d = neu.reshape(-1, 3)
        gruppe = (Mitsubamaterial.gruppen(punkte) if lage is None else lage)[nummern]
        self._netzliste.append((name, int(name[1:].split('_')[0]), nummern, d, gruppe))
        eigen = mi.Properties()
        eigen['bsdf'] = mi.load_dict(self._tensoren(bsdf))
        netz = mi.Mesh(name, vertex_count=len(p), face_count=len(d), has_vertex_normals=True,
                       has_vertex_texcoords=uv is not None, props=eigen)
        werte = mi.traverse(netz)
        werte['vertex_positions'] = mi.Float(np.ascontiguousarray(p, dtype=np.float32).ravel())
        werte['faces'] = mi.UInt32(np.ascontiguousarray(d, dtype=np.uint32).ravel())
        werte['vertex_normals'] = mi.Float(Mitsubamaterial.normalen(p, d, gruppe).ravel())
        if uv is not None:
            t = np.asarray(uv, dtype=np.float64)[nummern].copy()
            t[:, 1] = 1.0 - t[:, 1]
            werte['vertex_texcoords'] = mi.Float(np.ascontiguousarray(t, dtype=np.float32).ravel())
        werte.update()
        return netz

    def _tensoren(self, wert):
        """Bildfelder (`data`, NumPy) als Dr.Jit-Tensor — `load_dict` nimmt kein ndarray."""
        if isinstance(wert, dict):
            return {k: (self.mi.TensorXf(v) if k == 'data' and isinstance(v, np.ndarray) else self._tensoren(v))
                    for k, v in wert.items()}
        return wert

    def _kurven(self, kurven, bsdf):
        """Strähnen als `linearcurve`: Kontrollpunkte (x, y, z, r) und Segmentanfänge direkt aus den Feldern — Mitsuba
        liest Kurven nur aus einer Datei, also eine Strähne als Platzhalter laden und die Felder ersetzen."""
        mi = self.mi
        reihe = np.asarray(kurven['reihe'], dtype=np.int64)
        laengen = np.asarray(kurven['laengen'], dtype=np.int64)
        p = np.asarray(kurven['punkte'], dtype=np.float32)[reihe]
        r = np.asarray(kurven['radius'], dtype=np.float32)[reihe]
        start = np.concatenate([[0], np.cumsum(laengen)[:-1]])
        segment = np.concatenate([np.arange(s, s + n - 1) for s, n in zip(start, laengen, strict=True) if n >= 2])
        form = mi.load_dict({'type': 'linearcurve', 'filename': self._platzhalter(), 'bsdf': bsdf})
        werte = mi.traverse(form)
        werte['control_points'] = mi.Float(np.ascontiguousarray(np.column_stack([p, r]), dtype=np.float32).ravel())
        werte['segment_indices'] = mi.UInt32(segment.astype(np.uint32))
        werte.update()
        return form

    @staticmethod
    def _platzhalter():
        from django.conf import settings
        pfad = os.path.join(str(settings.MITSUBA_CACHE), 'kurve_platzhalter.txt')
        if not os.path.isfile(pfad):
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
            with open(pfad, 'w', encoding='ascii') as fh:
                fh.write('0 0 0 0.001\n0 0.01 0 0.001\n')
        return pfad

    # ----------------------------------------------------------- Kamera

    def sensor(self, mitte, halb, winkel, groesse, spp):
        b, h = int(groesse[0]), int(groesse[1])
        s = float(halb) * b / h
        bogen = np.radians(float(winkel))
        mitte = np.asarray(mitte, dtype=np.float64)
        lage = mitte + max(4.0 * float(halb), 2.0) * np.array([np.sin(bogen), 0.0, np.cos(bogen)])
        T = self.mi.ScalarTransform4f
        return self.mi.load_dict({
            'type': 'orthographic', 'near_clip': 1e-3, 'far_clip': 1e3,
            'to_world': T().look_at(origin=lage.tolist(), target=mitte.tolist(), up=[0.0, 1.0, 0.0]).scale([s, s, 1.0]),
            # Bild: geschichteter Abtaster (halbes Rauschen bei gleicher Zahl); Kennbild (1 Abtastung): unverändert unabhängig.
            'sampler': {'type': 'multijitter' if int(spp) > 1 else 'independent', 'sample_count': int(spp)},
            'film': {'type': 'hdrfilm', 'width': b, 'height': h, 'pixel_format': 'rgba',
                     'rfilter': {'type': 'box'}}})

    # ------------------------------------------------------------- Bild

    def rendern(self, mitte, halb, winkel, groesse, spp=None, saat=0):
        """(H, B, 4) float 0…1: sRGB mit geradem Alpha — beim Kennbild die Kennfarben selbst."""
        import drjit as dr
        spp = 1 if self.kennung else int(spp or self.SPP)
        roh = self.mi.render(self.szene, sensor=self.sensor(mitte, halb, winkel, groesse, spp), spp=spp, seed=int(saat))
        dr.sync_thread()
        feld = np.array(roh, dtype=np.float32)
        alpha = np.clip(feld[..., 3], 0.0, 1.0)
        if self.kennung:
            rgb = np.clip(feld[..., 4:7], 0.0, 1.0)
            alpha = (alpha > 0.5).astype(np.float32)
        else:
            rgb = Mitsubamaterial.srgb(feld[..., :3] / np.maximum(alpha, 1e-6)[..., None])
        return np.dstack([rgb * (alpha[..., None] > 0), alpha]).astype(np.float32)
