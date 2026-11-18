# -*- coding: utf-8 -*-
u"""G8hautaufgenesis — die Hautbilder eines Genesis-8-Charakters auf die UDIM-Kacheln von Genesis 9 umbacken (16.11.2026).

Edgar, 16.11.2026: „ja, mach G8 → G9 mit Margie“. Die Form kommt über den Klon (`G8charakteraufgenesis`); die Haut liegt auf den UVs von
Genesis 8 (je Gruppe ein Bild: Face, Torso, Arms, Legs …), Genesis 9 erwartet je Gruppe eine Kachel seines UV-Satzes `Base Multi UDIM`
(Head 1001, Body 1002, Legs 1003, Arms 1004, Nägel 1005). Einen G8-UV-Satz für Genesis 9 hat die Bibliothek nicht (gelesen 16.11.2026:
`Base Multi UDIM`, `Base Single UDIM`, `Genital Map Bake`).

JE TEXEL der G9-Kachel (`G9texturabtastung`: Dreieck und Anteile) die Lage auf Genesis 9 in G8-Gestalt (`G9autofit.punkte`), dort das nächste
Hautdreieck von Genesis 8 in G9-Stellung (`G1klonuebertragung.naechste`), dessen UV im UV-Satz der Figur (`Base Female`/`Base Male`, mit den
Nahtüberschreibungen `polygon_vertex_indices`) und das Bild der G8-Gruppe dieses Dreiecks (aus dem Preset, `G9material.bilder_aus`), bilinear.
Je Texel und nicht je Käfigpunkt: über eine UV-Naht von Genesis 8 hinweg zu mitteln gäbe Streifen.

Gebacken werden Albedo (mit der Farbe der Gruppe, Daz: Farbe × Bild, im linearen Raum) und Rauheit. Normalenkarten nicht: ihre Tangentenrahmen
hängen am UV-Satz — Genesis 9 behält seine Detailnormalen. Die Kacheln liegen in der eigenen Bibliothek (`G9pfade.eigene()`,
`Runtime/Textures/EIGEN/G8/<Kennung>/`), der Textur-Endpunkt findet sie dort (`G9pfade.finden`).
"""
import copy
import logging
import re
import time

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from Genesis9.dson import G9dson
from Genesis9.hautpresets import G9hautpresets
from Genesis9.material import G9material
from Genesis9.pfade import G9pfade
from Genesis9.texturabtastung import G9texturabtastung

logger = logging.getLogger('core')

__all__ = ['G8hautaufgenesis']


class G8hautaufgenesis:
    u"""Ein Charakter: G8-Hautbilder -> G9-Kacheln und die `bilder` für den Katalog."""

    SEITE = 4096
    BLOCK = 1 << 20
    RAND_PX = 12
    ORDNER = ('Runtime', 'Textures', 'EIGEN', 'G8')
    VORLAGE = {u'weiblich': 'G9 Feminine Skin 01 MAT', u'männlich': 'G9 Masculine Skin 01 MAT'}
    _KACHEL = re.compile(r'_(10\d\d)\.[a-z]+$', re.I)
    #: Ein Texel weiter als das (m) von der Haut von Genesis 8 (Mundwinkel innen, Nagelbett) bekommt die Farbe des Nachbarn (`RAND_PX`-Füllung).
    WEIT_M = 0.02

    def __init__(self, uebertragung, preset, kennung, geschlecht=u'weiblich'):
        self.u = uebertragung
        self.preset = preset
        self.kennung = kennung
        self.geschlecht = geschlecht

    # ------------------------------------------------------------ Quellen

    def uv(self):
        u"""`(uvs (U, 2), dreieck_uv (T, 3), dreieck_gruppe (T,), gruppennamen)` in der Reihenfolge von `u.dreiecke` (`dreiecke_der_haut`)."""
        geo = self.u.doc.geometrie()
        pfad, _kennung = G9pfade.aufloesen(geo.get('default_uv_set') or '')
        satz = G9dson.roh(pfad)['uv_set_library'][0]
        uvs = Torchfeld.feld(satz['uvs']['values'], dtype=torch.float64)
        ueber = {(int(p), int(v)): int(i) for p, v, i in satz.get('polygon_vertex_indices') or []}
        gruppen = geo['polygon_material_groups']['values']
        haut = {i for i, name in enumerate(gruppen) if any(t in name for t in self.u.HAUT)}
        dreieck_uv, dreieck_gruppe = [], []
        for nr, p in enumerate(geo['polylist']['values']):
            if p[1] not in haut:
                continue
            ecken = [ueber.get((nr, v), v) for v in p[2:]]
            for i in range(1, len(ecken) - 1):
                dreieck_uv.append((ecken[0], ecken[i], ecken[i + 1]))
                dreieck_gruppe.append(p[1])
        if len(dreieck_uv) != len(self.u.dreiecke):
            raise ValueError('G8-Haut %s: %d UV-Dreiecke, Haut %d' % (self.kennung, len(dreieck_uv), len(self.u.dreiecke)))
        return uvs, Torchfeld.feld(dreieck_uv, dtype=torch.int64), Torchfeld.feld(dreieck_gruppe, dtype=torch.int64), gruppen

    @staticmethod
    def bild(rel, kanaele):
        u"""Ein Bild der Bibliothek als (H, W, kanaele) uint8 auf der Karte — oder None."""
        from PIL import Image
        pfad = G9material.datei(rel) if rel else None
        if pfad is None:
            return None
        with Image.open(pfad) as im:
            im = im.convert('RGB' if kanaele == 3 else 'L')
            t = torch.frombuffer(bytearray(im.tobytes()), dtype=torch.uint8).reshape(im.height, im.width, kanaele)
        return t.to('cuda')

    @staticmethod
    def abtasten(bild, u, v):
        u"""Bilinear: (n, C) float 0..1 an den UVs (u, v ∈ [0, 1), v nach oben wie bei Daz)."""
        h, w = bild.shape[0], bild.shape[1]
        x = u * w - 0.5
        y = (1.0 - v) * h - 0.5
        x0, y0 = torch.floor(x), torch.floor(y)
        fx, fy = (x - x0)[:, None].to(torch.float32), (y - y0)[:, None].to(torch.float32)     # float32 wie das Ziel (Wächter: `zuweisung_typ`)
        x0 = x0.long().clamp(0, w - 1)
        y0 = y0.long().clamp(0, h - 1)
        x1, y1 = (x0 + 1).clamp(0, w - 1), (y0 + 1).clamp(0, h - 1)

        def px(yy, xx):
            return bild[yy, xx].to(torch.float32) / 255.0
        return (px(y0, x0) * (1 - fx) * (1 - fy) + px(y0, x1) * fx * (1 - fy) + px(y1, x0) * (1 - fx) * fy + px(y1, x1) * fx * fy)

    @staticmethod
    def linear(c):
        return torch.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def srgb(c):
        c = c.clamp(0.0, 1.0)
        return torch.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1.0 / 2.4) - 0.055)

    # ------------------------------------------------------------ Backen

    def backen(self):
        u"""Alle Kacheln backen und ablegen; gibt `bilder` (wie `G9hautpresets.haut`) mit den neuen Albedo-/Rauheitsbildern zurück."""
        start = time.perf_counter()
        uvs, dreieck_uv, dreieck_gruppe, gruppennamen = self.uv()
        quelle = G9material.bilder_aus(self.preset)
        tab = G9texturabtastung.holen(self.SEITE)
        klon = Torchfeld.feld(self.u.autofit.punkte, dtype=torch.float64)
        vorlage = copy.deepcopy(G9hautpresets.haut(self.VORLAGE.get(self.geschlecht, self.VORLAGE[u'weiblich'])))
        ziel_kacheln = {}
        for gruppe, b in vorlage.items():
            treffer = self._KACHEL.search(str(b.get('albedo') or ''))
            if treffer:
                ziel_kacheln.setdefault(int(treffer.group(1)), []).append(gruppe)
        bilder = {}                                                         # (rel, kanäle) -> Bild auf der Karte
        aus = {}
        for kachel in tab.kacheln:
            if kachel not in ziel_kacheln:
                continue
            gebacken = self._kachel(tab, kachel, klon, uvs, dreieck_uv, dreieck_gruppe, gruppennamen, quelle, bilder)
            if gebacken is not None:                                        # ohne ein gemaltes Texel bleibt Genesis' eigene Kachel
                aus[kachel] = gebacken
        for b in vorlage.values():
            treffer = self._KACHEL.search(str(b.get('albedo') or ''))
            if treffer and int(treffer.group(1)) in aus:
                rel = aus[int(treffer.group(1))]
                b['albedo'] = rel['albedo']
                b['farbe'] = [1.0, 1.0, 1.0]
                if rel.get('rauheit'):
                    b['rauheit'] = rel['rauheit']
        logger.info('G8-Haut %s: %d Kacheln (%d px) in %.1f s', self.kennung, len(aus), self.SEITE, time.perf_counter() - start)
        return vorlage

    def _kachel(self, tab, kachel, klon, uvs, dreieck_uv, dreieck_gruppe, gruppennamen, quelle, bilder):
        u"""Eine Kachel: `{albedo: rel, rauheit: rel|None}`."""
        drin, ecken, anteile = tab.stellen(kachel)
        n = len(ecken)
        farbe = torch.zeros((n, 3), dtype=torch.float32, device='cuda')
        rau = torch.zeros((n, 1), dtype=torch.float32, device='cuda')
        hat_rau = torch.zeros(n, dtype=torch.bool, device='cuda')
        gueltig = torch.zeros(n, dtype=torch.bool, device='cuda')
        for a in range(0, n, self.BLOCK):
            e, w = ecken[a:a + self.BLOCK], anteile[a:a + self.BLOCK]
            lage = Torchfeld.einsum('nk,nkc->nc', w, klon[e])
            dreieck, gewichte, abstand = self.u.naechste(lage)
            uv = Torchfeld.einsum('nk,nkc->nc', gewichte, uvs[dreieck_uv[dreieck]])
            uu, vv = uv[:, 0] - torch.floor(uv[:, 0]), uv[:, 1] - torch.floor(uv[:, 1])
            g = dreieck_gruppe[dreieck]
            nah = abstand <= self.WEIT_M
            for gnr in torch.unique(g).tolist():
                name = gruppennamen[gnr]
                b = quelle.get(name) or {}
                wahl = (g == gnr) & nah
                if not bool(wahl.any()):
                    continue
                idx = torch.nonzero(wahl, as_tuple=True)[0]
                for art, kanaele in (('albedo', 3), ('rauheit', 1)):
                    rel = b.get(art)
                    if not rel:
                        continue
                    if (rel, kanaele) not in bilder:
                        bilder[(rel, kanaele)] = self.bild(rel, kanaele)
                    bild = bilder[(rel, kanaele)]
                    if bild is None:
                        continue
                    wert = self.abtasten(bild, uu[idx], vv[idx])
                    if art == 'albedo':
                        f = torch.tensor(b.get('farbe') or [1.0, 1.0, 1.0], dtype=torch.float32, device='cuda')
                        farbe[a + idx] = self.srgb(self.linear(wert) * self.linear(f))
                        gueltig[a + idx] = True
                    else:
                        rau[a + idx] = wert
                        hat_rau[a + idx] = True
        if not bool(gueltig.any()):
            logger.warning('G8-Haut %s: Kachel %d ohne Bild aus %s — bleibt Genesis 9', self.kennung, kachel, self.preset)
            return None
        return {'albedo': self._ablegen(kachel, 'D', farbe, gueltig, drin),
                'rauheit': self._ablegen(kachel, 'R', rau, hat_rau, drin) if bool(hat_rau.any()) else None}

    def _ablegen(self, kachel, art, werte, gueltig, drin):
        u"""Die Werte der Inseltexel als Kachelbild ablegen, Rand `RAND_PX` nach außen gezogen; gibt den Pfad relativ zur Bibliothek zurück."""
        from KoerperKI_alle.kartenbild import Kartenbild as ndimage
        from PIL import Image
        s = self.SEITE
        k = werte.shape[1]
        bild = torch.zeros((s, s, k), dtype=torch.float32, device='cuda')
        gemalt = torch.zeros((s, s), dtype=torch.bool, device='cuda')
        pos = torch.nonzero(drin, as_tuple=False)
        bild[pos[:, 0], pos[:, 1]] = werte
        gemalt[pos[:, 0], pos[:, 1]] = gueltig
        abstand, (iy, ix) = ndimage.distance_transform_edt(~gemalt, return_indices=True)
        nah = (~gemalt) & (abstand <= self.RAND_PX)
        bild[nah] = bild[iy[nah], ix[nah]]
        if bool(gemalt.any()):
            bild[(~gemalt) & ~nah] = bild[gemalt].mean(0)
        roh = Torchfeld.astype(bild.clamp(0.0, 1.0) * 255.0 + 0.5, torch.uint8)
        name = '%s_%s_%d.jpg' % (self.kennung, art, kachel)
        rel = '/'.join(self.ORDNER + (self.kennung, name))
        ziel = G9pfade.eigene().joinpath(*self.ORDNER, self.kennung, name)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        # wie `G9texturbacken`: über `Torchfeld.roh` an PIL
        Image.fromarray(Torchfeld.roh(roh if k == 3 else roh[:, :, 0]), 'RGB' if k == 3 else 'L').save(ziel, quality=92)
        return rel
