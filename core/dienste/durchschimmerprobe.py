# -*- coding: utf-8 -*-
u"""Durchschimmerprobe — die Abnahme des Fitting-Konzepts: Bilder, nicht Perzentile.

Edgar (21.09.2026): „deine Loesungen waren bisher immer nur sehr kurzfristig."
Jeder Fix galt als fertig, weil eine Kennzahl gruen war; das Bild war es nicht.
Diese Probe rechnet je Stueck und Daz-Pose den Koerper und das Stueck so, wie
der Browser sie zeigt — Stoff in Ruhe aus der Haut gehoben, dann je Pose
(a) gehaeutet wie die GPU (Gelenkfelder + Knochenmatrizen mit der Browserhaut)
und (b) an die Oberflaeche gebunden (`G9oberflaechenbindung`, Schicht 2) — und
misst zweierlei:

    innen      Stoffpunkte IM Koerper (Tiefe entlang der Normale des naechsten
               Hautpunkts < 0), Anzahl und Anteil
    pixel      Hautpixel VOR dem Stoff innerhalb der Stoffsilhouette, aus vier
               Ansichten (pyrender: Tiefe des Koerpers gegen Tiefe des Stoffs)

Dazu ein Kontaktbogen (JPG) je Stueck mit allen Posen und Ansichten. Ohne die
Hautmaske (die entsteht im Browser): die Zahl hier ist die OBERE Schranke
dessen, was der Browser zeigt. Schwelle fuer gebundene Stuecke: 0 Pixel.

LongRunner, nur auf Ansage (`manage.py durchschimmern_probe`, Test in
`core/tests/longrunner/`): je Stueck und Pose Sekunden Serverzeit.
"""
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

__all__ = ['Durchschimmerprobe']


class Durchschimmerprobe:
    u"""Stueck × Pose → Zahlen und Bilder."""

    POSEN = ('de_g9_base_05_standing', 'g9_base_pose_01_running_g9f')
    ANSICHTEN = ((0.0, 'vorn'), (np.pi, 'hinten'), (np.pi / 2, 'links'), (-np.pi / 2, 'rechts'))
    BILD_PX = 360
    #: Mindestabstand Haut vor Stoff, damit ein Pixel zaehlt (Meter) — die Tiefen
    #: beider Netze rauschen um ein halbes Texel.
    TIEFENSPIEL_M = 0.0015
    #: Weiter als das VOR dem Stoff ist keine durchschimmernde Haut, sondern ein
    #: Glied vor dem Rumpf (der Arm neben dem T-Shirt in der Seitenansicht: 5.000
    #: Pixel, gemessen 21.09.2026) — Durchschimmern ist Haut IM Stoff, Millimeter.
    DICKE_M = 0.02

    def __init__(self, regler=None, posen=None, stufen=None, ziel=None, rendern=True):
        from Genesis9.netzstufe import G9netzstufe

        from core.api.g9felder import G9felderapi
        self.regler = dict(regler or {})
        self.posen = list(posen or self.POSEN)
        self.stufen = G9netzstufe.browser() if stufen is None else int(stufen)
        self.ziel = Path(ziel) if ziel else None
        self.rendern = rendern
        self.kanaele = G9felderapi.kanaele('gelenke')
        self._koerper = {}

    # ---------------------------------------------------------------- Lauf

    def laufen(self, kennungen):
        u"""`[{kennung, teil, pose, weg, punkte, innen, anteil, pixel}]` — `weg`
        ist `gehaeutet` oder `gebunden`; dazu je Stueck ein Kontaktbogen."""
        from core.api.g9figur import G9figur
        formung_r = G9figur.formung({'regler': dict(self.regler)}, {})
        koerper_r = self.koerper(formung_r)
        aus = []
        for kennung in kennungen:
            t0 = time.time()
            teile = self.ruhe(kennung, formung_r, koerper_r)
            bilder = []
            for pose in self.posen:
                formung_p = G9figur.formung({'regler': dict(self.regler), 'pose': pose}, {})
                koerper_p = self.koerper(formung_p)
                for name, gehaeutet, gebunden, _haut in self.bewegt(kennung, teile, formung_p, koerper_p):
                    for weg, punkte in (('gehaeutet', gehaeutet), ('gebunden', gebunden)):
                        tiefe = self.tiefen(punkte, koerper_p)
                        zeile = {'kennung': kennung, 'teil': name, 'pose': pose, 'weg': weg,
                                 'punkte': int(len(tiefe)), 'innen': int((tiefe < 0).sum()),
                                 'anteil': round(100.0 * float((tiefe < 0).mean()), 2), 'pixel': None}
                        if self.rendern:
                            dreiecke = next(t.dreiecke for t in teile if t is not None and t.name == name)
                            zeile['pixel'], bild = self.pixel(koerper_p, punkte, dreiecke,
                                                              '%s %s %s' % (name, pose[:18], weg))
                            bilder.append(bild)
                        aus.append(zeile)
            if self.ziel and bilder:
                self.kontaktbogen(bilder, self.ziel / ('%s.jpg' % kennung))
            for z in aus:
                if z['kennung'] == kennung:
                    z['sekunden'] = round(time.time() - t0, 1)
        return aus

    # ------------------------------------------------------------- Koerper

    def koerper(self, formung):
        u"""(Punkte, Normalen, Dreiecke, Baum, Bindung) des Koerpers dieser Stellung, im Figurraum."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.koerpernetz import G9koerpernetz
        from Genesis9.kollision import G9kollision
        schluessel = formung.fingerabdruck()
        if schluessel in self._koerper:
            return self._koerper[schluessel]
        netz = G9koerpernetz(formung, stufen=self.stufen)
        fein, normalen, _baum = netz.koerperflaeche()
        hoch = np.array([0.0, formung.boden(), 0.0])
        fein = fein + hoch
        stufe = G9basisnetz.holen().netzstufe(self.stufen)
        # ALLES im Figurraum (Boden nicht abgezogen): die Knochenmatrizen der
        # Pose rechnen dort, und der Koerper der Pose steht dort auch.
        baum = G9kollision.baum(fein)
        from Genesis9.oberflaechenbindung import G9oberflaechenbindung
        aus = SimpleNamespace(punkte=fein, normalen=normalen, dreiecke=np.asarray(stufe.dreiecke),
                              baum=baum,
                              bindung=G9oberflaechenbindung(fein, normalen, stufe.dreiecke, baum))
        self._koerper[schluessel] = aus
        return aus

    def tiefen(self, punkte, koerper):
        from Genesis9.kollision import G9kollision
        _w, naechster = G9kollision.naechste(koerper.baum, np.asarray(punkte, dtype=np.float64))
        return np.einsum('ij,ij->i', punkte - koerper.punkte[naechster], koerper.normalen[naechster])

    # ---------------------------------------------------------------- Ruhe

    def ruhe(self, kennung, formung_r, koerper_r):
        u"""Je Teil: Browserpunkte (nach Kollision), Haut, Dreiecke, Bindung — Figurraum."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.koerpernetz import G9koerpernetz
        eintrag = G9garderobe.eintrag(kennung) or {}
        zusatz = dict(eintrag.get('vorgaben') or {})
        bilder = G9garderobe.bilder(kennung, None)
        koerper = (koerper_r.punkte, koerper_r.normalen, koerper_r.baum)
        # In der Reihenfolge der Teile, Props und Straehnen als None — die
        # Gelenkfelder (`felder.teile`) zaehlen genauso.
        aus = []
        for folger, lage in G9garderobe.teile(kennung):
            if lage is not None or getattr(folger, 'ART', None) == 'strang':
                aus.append(None)
                continue
            kaefig = folger.punkte_zu(formung_r, zusatz)
            netz = G9koerpernetz.folgernetz(folger, kaefig, bilder, self.stufen, koerper=koerper,
                                            werte=dict(formung_r.morphwerte()),
                                            bindung=koerper_r.bindung)
            haut = netz['haut']
            aus.append(SimpleNamespace(
                name=folger.name,
                punkte=np.asarray(netz['punkte'], dtype=np.float64),
                haut=haut if haut is None or hasattr(haut, 'knochen') else SimpleNamespace(**haut),
                dreiecke=np.asarray(netz['dreiecke']), bindung=netz['bindung']))
        return aus

    # ------------------------------------------------------------- Bewegt

    def bewegt(self, kennung, teile, formung_p, koerper_p):
        u"""Je Teil: (Name, gehaeutet, gebunden, Haut) in der Pose — Figurraum."""
        from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
        from Genesis9.stueckfelder import G9stueckfelder
        felder = G9stueckfelder.holen('gelenke', self.kanaele, kennung, self.stufen)
        werte = G9gelenkkorrekturen.werte(formung_p.drehung, regler=G9gelenkkorrekturen.regler(formung_p))
        matrizen = formung_p.matrizen()
        aus = []
        for teil, feld in zip(teile, felder.teile, strict=False):
            if teil is None:
                continue
            punkte = np.array(teil.punkte, copy=True)
            for kanal, (nummern, deltas) in (feld or {}).items():
                w = float(werte.get(kanal, 0.0) or 0.0)
                if abs(w) > 1e-6:
                    punkte[nummern] += w * np.asarray(deltas, dtype=np.float64)
            gehaeutet = matrizen.anwenden(punkte, teil.haut)
            gebunden = self.binden(gehaeutet, teil.bindung, koerper_p)
            aus.append((teil.name, gehaeutet, gebunden, teil.haut))
        return aus

    @staticmethod
    def binden(gehaeutet, bindung, koerper):
        u"""Die Formel des Shaders: q = u·A + v·B + w·C + d·n, gemischt mit `mischung`."""
        if bindung is None:
            return gehaeutet
        ecken = np.asarray(bindung['dreieck']).astype(np.int64)
        bary = np.asarray(bindung['bary'], dtype=np.float64)
        d = np.asarray(bindung['abstand'], dtype=np.float64)
        m = np.asarray(bindung['mischung'], dtype=np.float64)
        dabei = (ecken[:, 0] >= 0) & (m > 0)
        aus = np.array(gehaeutet, copy=True)
        e = ecken[dabei]
        q = np.einsum('kc,kcj->kj', bary[dabei], koerper.punkte[e])
        n = np.einsum('kc,kcj->kj', bary[dabei], koerper.normalen[e])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        ziel = q + d[dabei, None] * n
        aus[dabei] = aus[dabei] + (ziel - aus[dabei]) * m[dabei, None]
        return aus

    # --------------------------------------------------------------- Bild

    def pixel(self, koerper, stoff, dreiecke, titel):
        u"""Hautpixel vor dem Stoff in der Stoffsilhouette (Summe der vier
        Ansichten) und ein Bildstreifen (Farbe, Treffer rot)."""
        import pyrender
        import trimesh
        from PIL import Image, ImageDraw
        renderer = self._renderer()
        kn = trimesh.Trimesh(koerper.punkte, koerper.dreiecke, process=False)
        sn = trimesh.Trimesh(stoff, dreiecke, process=False)
        mitte = koerper.punkte.mean(axis=0)
        hoehe = float(koerper.punkte[:, 1].max() - koerper.punkte[:, 1].min())
        streifen = []
        summe = 0
        for winkel, name in self.ANSICHTEN:
            farbe_k, tiefe_k = self._rendern(renderer, pyrender, kn, (0.85, 0.65, 0.55), mitte, hoehe, winkel)
            farbe_s, tiefe_s = self._rendern(renderer, pyrender, sn, (0.25, 0.30, 0.55), mitte, hoehe, winkel)
            treffer = ((tiefe_s > 0) & (tiefe_k > 0) & (tiefe_k < tiefe_s - self.TIEFENSPIEL_M)
                       & (tiefe_k > tiefe_s - self.DICKE_M))
            summe += int(treffer.sum())
            bild = np.where((tiefe_k > 0)[..., None], farbe_k, 0)
            stoff_vorn = (tiefe_s > 0) & ((tiefe_k <= 0) | (tiefe_s <= tiefe_k + self.TIEFENSPIEL_M))
            bild = np.where(stoff_vorn[..., None], farbe_s, bild)
            bild[treffer] = (255, 0, 0)
            img = Image.fromarray(bild.astype(np.uint8))
            ImageDraw.Draw(img).text((4, 4), '%s %s: %d' % (titel, name, int(treffer.sum())),
                                     fill=(255, 255, 0))
            streifen.append(img)
        renderer.delete()
        breite = sum(s.width for s in streifen)
        zeile = Image.new('RGB', (breite, streifen[0].height), 'black')
        x = 0
        for s in streifen:
            zeile.paste(s, (x, 0))
            x += s.width
        return summe, zeile

    def _renderer(self):
        import pyrender
        return pyrender.OffscreenRenderer(self.BILD_PX, self.BILD_PX * 2)

    def _rendern(self, renderer, pyrender, netz, farbe, mitte, hoehe, winkel):
        material = pyrender.MetallicRoughnessMaterial(baseColorFactor=(*farbe, 1.0), metallicFactor=0.0,
                                                     roughnessFactor=0.8)
        szene = pyrender.Scene(bg_color=(0, 0, 0, 1.0), ambient_light=(0.4, 0.4, 0.4))
        szene.add(pyrender.Mesh.from_trimesh(netz, material=material, smooth=False))
        kamera = pyrender.PerspectiveCamera(yfov=np.radians(40), aspectRatio=0.5)
        abstand = hoehe * 1.5
        lage = np.eye(4)
        c, s = np.cos(winkel), np.sin(winkel)
        lage[:3, :3] = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        lage[:3, 3] = mitte + abstand * np.array([s, 0, c])
        szene.add(kamera, pose=lage)
        szene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=2.5), pose=lage)
        farbe_bild, tiefe = renderer.render(szene)
        return farbe_bild[..., :3], tiefe

    @staticmethod
    def kontaktbogen(bilder, pfad):
        from PIL import Image
        pfad.parent.mkdir(parents=True, exist_ok=True)
        breite = max(b.width for b in bilder)
        hoehe = sum(b.height for b in bilder)
        bogen = Image.new('RGB', (breite, hoehe), 'black')
        y = 0
        for b in bilder:
            bogen.paste(b, (0, y))
            y += b.height
        bogen.save(pfad, quality=85)
        return pfad
