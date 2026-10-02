# -*- coding: utf-8 -*-
"""Genesishaarrender — Figur mit Frisur als freigestelltes Bild, je Blickwinkel (30.09.2026).

Was die Iterationen zum Vergleichen brauchen (`Iterationsbild`, `Iterationsnote`): die Figur vor
NICHTS — ein PNG mit Alpha, in dem nur die Figur steht. Der Umriss ist die halbe Note, also darf kein
Hintergrund hineinzählen; das Alpha kommt aus der Tiefenkarte (wo pyrender nichts getroffen hat, ist
Tiefe 0).

**Orthografisch, nicht perspektivisch:** Die Note vergleicht Umrisse, nachdem `Iterationsbild` beide
Bilder an der Figur ausgerichtet hat (Höhe und Schwerpunkt des Rumpfbands). Eine perspektivische Kamera
verschiebt Kopf und Füße je nach Abstand gegeneinander — die Ausrichtung könnte das nicht mehr
herausrechnen.

Der Winkel zählt in Grad ab vorn, positiv zur LINKEN Seite der Figur (der Vertrag in
`Genesisengine2d3dkleider`, dieselbe Drehrichtung wie `Durchschimmerprobe.ANSICHTEN`).

Läuft im Arbeitsprozess (`engine2d3dkleider_fahren`, python14), nie im Django-Server — pyrender belegt die
Grafikkarte (`Haar/haarbild.py` hält es ebenso).

**Seit 01.10.2026 rendert Mitsuba 3 auf der Grafikkarte** (`Mitsubaszene`: Pfadverfolgung wie Cycles, Normalkarten,
Strähnen als Kurven); pyrender ist wählbar (Einstellungen → 2D3D Kleider, `Renderwahl`, Vorgabe Mitsuba) und der
Rückfall, wenn Mitsuba oder CUDA fehlt (Warnung im Log, `motor` sagt, wer gerendert hat). Dieselbe Kamera, dieselben
Dateien. `kennung=True` (Teilmasken) liefert die Kennfarben unbeleuchtet und ohne Mischkante.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Genesishaarrender']


class Genesishaarrender:
    """`bild(punkte, dreiecke, farbe, winkel, pfad)` → Pfad des freigestellten PNG."""

    #: Bildgröße (Breite × Höhe) — hochkant wie eine stehende Figur.
    BREITE, HOEHE = 512, 768
    #: Rand um die Figur, als Anteil ihrer Höhe.
    RAND = 0.06
    UMGEBUNG = 0.55
    LICHT = 2.2
    #: Die Haut, wenn der Körper keine eigene Farbe trägt (die Note vergleicht Farbflächen).
    HAUT = (0.82, 0.68, 0.60)

    #: 'mitsuba' (GPU-Pfadverfolgung) oder 'pyrender'; None = die Einstellung (`Renderwahl`, Einstellungen →
    #: 2D3D Kleider, Vorgabe Mitsuba).
    MOTOR = None

    def __init__(self, koerper=None, motor=None):
        """`koerper`: Pfad einer GLB (die Grundfigur mit Rig) oder `(punkte, dreiecke)` — sie steht in
        jedem Bild mit, sonst verglichen wir eine Frisur ohne Kopf. `motor` schlägt die Einstellung."""
        from .renderwahl import Renderwahl
        self.MOTOR = motor or type(self).MOTOR or Renderwahl.gewaehlt()
        self._koerper = self._laden(koerper)
        self._renderer = None
        self._szenen = {}
        #: Wer das letzte Bild gerendert hat ('mitsuba' | 'pyrender').
        self.motor = None

    # -------------------------------------------------------------- Netze

    @staticmethod
    def _laden(koerper):
        if koerper is None:
            return None
        if isinstance(koerper, tuple):
            return (np.asarray(koerper[0], dtype=np.float64), np.asarray(koerper[1], dtype=np.int64))
        import trimesh
        netz = trimesh.load(str(koerper), force='mesh', process=False)
        return (np.asarray(netz.vertices, dtype=np.float64), np.asarray(netz.faces, dtype=np.int64))

    def renderer(self):
        if self._renderer is None:
            import pyrender
            self._renderer = pyrender.OffscreenRenderer(self.BREITE, self.HOEHE)
        return self._renderer

    def schliessen(self):
        self._szenen.clear()
        self._pyrender_zu()

    def _pyrender_zu(self):
        if self._renderer is not None:
            try:
                self._renderer.delete()
            except Exception:  # noqa: BLE001 — beim Aufräumen zählt nur, dass es weitergeht
                logger.debug('Haarrender: Renderer ließ sich nicht schließen', exc_info=True)
            self._renderer = None

    def _groesse(self, groesse):
        if groesse and tuple(groesse) != (self.BREITE, self.HOEHE):
            self._pyrender_zu()
            self.BREITE, self.HOEHE = int(groesse[0]), int(groesse[1])

    # --------------------------------------------------------- Mitsuba

    @staticmethod
    def _schluessel(teile, kennung):
        """Ein Teilesatz ist dieselbe Szene, solange Punkte, Dreiecke, Farben und Bilder dieselben sind — die Felder
        hält der Vorrat selbst fest (sonst könnte eine neue Liste die `id` einer freigegebenen bekommen)."""
        def extra(e):
            if not e:
                return None
            gruppen = tuple((int(g['ab']), int(g['anzahl']), str(g.get('albedo')), str(g.get('normalen')),
                             str(g.get('alpha')),
                             tuple(np.round(np.asarray(g.get('faktor', (1, 1, 1)), dtype=np.float64), 4)))
                            for g in e.get('gruppen') or [])
            return (id(e.get('uv')), gruppen, id(e.get('kurven')))
        return (bool(kennung),) + tuple((id(t[0]), id(t[1]), tuple(np.round(t[2], 4)), extra(t[3])) for t in teile)

    def _mitsuba(self, teile, mitte, halb, winkel, kennung):
        """(H, B, 4) aus Mitsuba — oder None (dann rendert pyrender)."""
        if self.MOTOR != 'mitsuba':
            return None
        from .mitsubaszene import Mitsubaszene
        if Mitsubaszene.mitsuba() is None:
            return None
        schluessel = self._schluessel(teile, kennung)
        eintrag = self._szenen.get(schluessel)
        # Dieselben Dreiecke, Farben und Bilder mit neuen Punkten (Film: je Bild gehäutet): nur die Lage tauschen.
        bau = tuple(s[1:] for s in schluessel[1:])
        mit_kurven = any(t[3] and t[3].get('kurven') is not None for t in teile)
        gleich = next((e for s, e in self._szenen.items()
                       if s[0] == schluessel[0] and tuple(x[1:] for x in s[1:]) == bau and not mit_kurven), None)
        if eintrag is None and gleich is not None:
            gleich[0].punkte_setzen(teile)
            self._szenen = {schluessel: (gleich[0], teile)}
            eintrag = self._szenen[schluessel]
        if eintrag is None:
            self._szenen.clear()
            eintrag = (Mitsubaszene(teile, kennung=kennung), teile)
            self._szenen[schluessel] = eintrag
        self.motor = 'mitsuba'
        return eintrag[0].rendern(mitte, halb, winkel, (self.BREITE, self.HOEHE), saat=getattr(self, 'saat', 0))

    # ------------------------------------------------------------- Bilder

    @staticmethod
    def _hex(farbe):
        roh = str(farbe or '').lstrip('#')
        if len(roh) != 6:
            return (0.28, 0.20, 0.15)
        return tuple(int(roh[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def _flach(self, pyrender, szene, punkte, dreiecke, farbe):
        import trimesh
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64),
                               faces=np.asarray(dreiecke, dtype=np.int64), process=False)
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=(*farbe, 1.0), metallicFactor=0.0, roughnessFactor=0.75, doubleSided=True)
        szene.add(pyrender.Mesh.from_trimesh(netz, material=material, smooth=False))

    def _textur(self, pyrender, szene, punkte, dreiecke, farbe, textur):
        """Je Materialgruppe mit Bild ein Netz mit UV und Albedo (`Kleidermodellbau._textur`: ab, anzahl, albedo,
        faktor); Dreiecke ohne Bild flach. pyrender legt Zeile 0 des Bildes auf v = 1 — wie Daz' UV (OBJ)."""
        import trimesh
        from PIL import Image
        uv = np.asarray(textur['uv'], dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64)
        belegt = np.zeros(len(dreiecke), dtype=bool)
        for g in textur['gruppen']:
            if g.get('albedo') is None:
                continue
            wahl = dreiecke[g['ab']:g['ab'] + g['anzahl']]
            if not len(wahl):
                continue
            belegt[g['ab']:g['ab'] + g['anzahl']] = True
            nummern, neu = np.unique(wahl.ravel(), return_inverse=True)
            netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64)[nummern], faces=neu.reshape(-1, 3),
                                   process=False)
            with Image.open(g['albedo']) as roh:
                bild = np.asarray(roh.convert('RGB'))
            netz.visual = trimesh.visual.TextureVisuals(uv=uv[nummern])
            # Die Normalkarte (Daz, Falten aus der Simulation) wie unter Mitsuba — pyrender rechnet die Tangenten im
            # Shader (Probe 01.10.2026: flach 30, zum Licht gekippt 35, weg 2); DirectX-Karten mit gespiegeltem Grün.
            karte = None
            if g.get('normalen') is not None:
                with Image.open(g['normalen']) as roh:
                    karte = np.asarray(roh.convert('RGB')).copy()
                if int(g.get('normalenachse') or 1) < 0:
                    karte[..., 1] = 255 - karte[..., 1]
            material = pyrender.MetallicRoughnessMaterial(
                baseColorFactor=(*[float(c) for c in g['faktor'][:3]], 1.0), metallicFactor=0.0, roughnessFactor=0.85,
                doubleSided=True, baseColorTexture=pyrender.Texture(source=bild, source_channels='RGB'),
                normalTexture=pyrender.Texture(source=karte, source_channels='RGB') if karte is not None else None)
            szene.add(pyrender.Mesh.from_trimesh(netz, material=material, smooth=False))
        if not belegt.all():
            self._flach(pyrender, szene, punkte, dreiecke[~belegt], farbe)

    def _szene(self, pyrender, teile, mitte, hoehe, winkel):
        szene = pyrender.Scene(bg_color=(0, 0, 0, 0), ambient_light=(self.UMGEBUNG,) * 3)
        for punkte, dreiecke, farbe, textur in teile:
            if punkte is None or dreiecke is None or not len(dreiecke):
                continue
            if textur and textur.get('uv') is not None and any(g.get('albedo') for g in textur.get('gruppen') or []):
                self._textur(pyrender, szene, punkte, dreiecke, farbe, textur)
            else:
                self._flach(pyrender, szene, punkte, dreiecke, farbe)
        # Orthografisch: die halbe Bildhöhe in Metern ist `ymag`; die Breite folgt dem Seitenverhältnis.
        halb = 0.5 * hoehe * (1.0 + 2.0 * self.RAND)
        kamera = pyrender.OrthographicCamera(xmag=halb * self.BREITE / self.HOEHE, ymag=halb)
        bogen = np.radians(float(winkel))
        c, s = np.cos(bogen), np.sin(bogen)
        lage = np.eye(4)
        lage[:3, :3] = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
        lage[:3, 3] = mitte + max(2.0 * hoehe, 2.0) * np.array([s, 0.0, c])
        szene.add(kamera, pose=lage)
        szene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=self.LICHT), pose=lage)
        return szene

    def bild(self, punkte, dreiecke, farbe, winkel, pfad):
        """Figur + Frisur aus `winkel` Grad, freigestellt nach `pfad` (PNG mit Alpha)."""
        teile = []
        if self._koerper is not None:
            teile.append((self._koerper[0], self._koerper[1], self.HAUT))
        if punkte is not None and dreiecke is not None:
            teile.append((punkte, dreiecke, self._hex(farbe)))
        return self.bild_teile(teile, winkel, pfad)

    KOPF_HOEHE = 0.34
    KOPF_UNTER_SCHEITEL = 0.13

    def bild_kopf(self, teile, winkel, pfad, groesse=(512, 512), saat=0, kennung=False):
        """Nur der Kopf: Kamera auf `KOPF_UNTER_SCHEITEL` unter dem höchsten Punkt, Bildhöhe `KOPF_HOEHE` m — für die
        Gesichtslandmarken (`Gesichtsmasse`, 01.10.2026); auf dem Figurrender wäre das Gesicht 30 Pixel groß. `saat`:
        Mitsubas Zufallsfolge (`Gesichtsmasse` mittelt über mehrere); `kennung` wie bei `bild_teile` (`Haarabgleich`)."""
        self.saat = int(saat)
        from PIL import Image
        teile = self._teile(teile)
        if not teile:
            raise ValueError('Nichts zu rendern')
        self._groesse(groesse)
        scheitel = max(float(np.asarray(t[0])[:, 1].max()) for t in teile)
        mitte = np.array([0.0, scheitel - self.KOPF_UNTER_SCHEITEL, 0.0])
        rgba = self._rgba(teile, mitte, self.KOPF_HOEHE / (1.0 + 2.0 * self.RAND), winkel, kennung)
        self.saat = 0
        rgb = rgba[..., :3].copy()
        rgb[rgba[..., 3] == 0] = 255              # weißer Grund: der Detektor sieht Fotos, keine Alphakanäle
        pfad.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgb, mode='RGB').save(pfad)
        return pfad

    @staticmethod
    def extra(teil, kurven=True):
        """Das Paket eines gebauten Teils (`Kleidermodellbau`) für `bild_teile`: UV + Gruppen mit Bildern, Strähnen als
        `kurven` (Mitsuba) — None ohne beides (dann flach in der Farbe des Teils). `kurven=False` für den Film: die
        Kurven liegen in der Ruhelage, die gehäuteten Punkte des Teils tanzen."""
        aus = {}
        if teil.get('uv') is not None and teil.get('textur'):
            aus.update(uv=teil['uv'], gruppen=teil['textur'])
        if kurven and teil.get('kurven') is not None:
            aus['kurven'] = teil['kurven']
        return aus or None

    @staticmethod
    def _teile(teile):
        return [(t[0], t[1], tuple(float(c) for c in np.asarray(t[2])[:3]), t[3] if len(t) > 3 else None)
                for t in teile if t[0] is not None]

    def _rgba(self, teile, mitte, hoehe, winkel, kennung):
        """(H, B, 4) uint8 — Mitsuba, sonst pyrender (Alpha aus der Tiefe)."""
        feld = self._mitsuba(teile, mitte, 0.5 * hoehe * (1.0 + 2.0 * self.RAND), winkel, kennung)
        if feld is not None:
            return np.clip(np.round(feld * 255.0), 0, 255).astype(np.uint8)
        import pyrender
        self.motor = 'pyrender'
        farbbild, tiefe = self.renderer().render(self._szene(pyrender, teile, mitte, hoehe, winkel))
        alpha = (np.asarray(tiefe) > 0).astype(np.uint8) * 255
        return np.dstack([np.asarray(farbbild)[..., :3], alpha])

    def bild_teile(self, teile, winkel, pfad, groesse=None, kennung=False):
        """Beliebig viele Teile `[(punkte, dreiecke, farbe rgb 0…1[, textur])]` — „2D3D Kleider" (Körper, Kleider,
        Haar) aus `winkel` Grad, freigestellt nach `pfad`. `textur` (30.09.2026): `{'uv': (N, 2), 'gruppen': [{ab,
        anzahl, albedo, normalen, faktor}], 'kurven': …}` — dann trägt das Teil seine Albedo je Materialgruppe (Foto,
        Decal, Daz-Bild) statt der flachen Farbe, unter Mitsuba auch die Normalkarte, und Stranghaar mit `kurven` wird
        als Strähnen gerendert. `groesse` (Breite, Höhe) statt BREITE × HOEHE: ein kleines Bild für die Iterationen, die
        Note rechnet ohnehin auf 128 × 192. `kennung`: Kennfarben für die Teilmasken (unbeleuchtet, ohne Mischkante)."""
        from PIL import Image

        teile = self._teile(teile)
        if not teile:
            raise ValueError('Nichts zu rendern — weder Körper noch Frisur')
        self._groesse(groesse)
        alle = np.vstack([t[0] for t in teile])
        mitte = np.array([0.0, 0.5 * (alle[:, 1].min() + alle[:, 1].max()), 0.0])
        hoehe = float(alle[:, 1].max() - alle[:, 1].min()) or 1.0
        rgba = self._rgba(teile, mitte, hoehe, winkel, kennung)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgba, mode='RGBA').save(pfad)
        return pfad
