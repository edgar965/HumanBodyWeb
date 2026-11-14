# -*- coding: utf-8 -*-
"""Exportleistekollision — das Wegschieben der Stücke aus fremden Gliedern (`KoerperKI_alle.Koerperkollision`, im Browser `Meshgenesiskollision`) als Morph-Ziele in die animierte GLB der
Exportleiste (31.10.2026 nachts, Edgar: „mach das alles: … Das neue Wegschieben der Kleider beim Bewegen wirkt nur in der Anzeige, nicht im GLB-Export“).

Im Browser schiebt ein Vertex-Shader je Bild (Kapseln aus `kleider_<g>/k/kapseln.json`); eine GLB kann keinen Shader tragen. Hier wird dieselbe Regel für jedes `SCHRITT`-te Bild der
eingebauten Bewegung gerechnet und als Morph-Ziel des Stücks abgelegt (nur die geschobenen Punkte, dünn besetzter Accessor, glTF 2.0 3.6.2.4); eine Gewichtsspur blendet je Bild
genau dieses Ziel ein, dazwischen linear. Blender liest das als Formschlüssel mit Spur, three.js als Morph-Ziele.

Rechnung je Bild f (glTF-Häutung, glTF 2.0 3.7.3): Gelenkmatrix J_k = Welt(Gelenk k, f) · IBM_k; Punkt im Bild q = Σ w_k J_k v. Die Kapseln stehen in der Ruhe der Kinematik und werden
starr auf die Bindelage der GLB gelegt (Zentren der Kinematik ↔ inv(IBM), Kabsch); geschoben wird mit `Koerperkollision.schieben` (Besitzer Mesh-Genesis, seit 01.11.2026 gemeinsamer
Baustein — keine eigene Fassung der Formel hier), J_k als `bild.dreh`/`bild.lage`. Der Versatz im Bild geht mit der nächsten Drehung zur Mischung Σ w_k J_k in die Bindelage (Morph
wirkt vor der Häutung) — nicht mit ihrer Inversen: an der Achsel ist die Mischung fast singulär (`KoerperKI_Fotos.Zeile1versatz`: dort 440 mm mit `solve`). `SCHRITT` ist eine Setzung.
Seit 01.11.2026 auf der Karte, im Prozess des Aufrufers unter der Gpusperre (Edgar: „alles auf GPU und RAM, in einem Prozess“): Häutung `Kostuemgpu.haeuten`, Schieben über den CUDA-Graphen
von `Koerperkollision`, Polarzerlegung; zur CPU gehen nur die Versätze der geschobenen Punkte für die GLB.

    bericht = Exportleistekollision(modell).einbauen(kapseln, kinematik)     # modell: G9glbanimation NACH einbauen(bewegung)
"""
import ctypes
import os
import sys
from contextlib import contextmanager
from types import SimpleNamespace

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from django.conf import settings
from KoerperKI_alle.drehung import Drehung as Rotation

from .exportleisterendermodell import Exportleisterendermodell

__all__ = ['Exportleistekollision']


class Exportleistekollision:
    SCHRITT = 3
    PRAEFIX = 'ki_'
    #: Angabe an die Gpusperre (GB, Setzung): die Häutung hält je Knotenplatz (N, 3, 3) float64, am Haar von Venus (377.752 Punkte) 27 MB
    GPU_BEDARF_GB = 4
    #: so lange wartet ein Export auf die Karte, dann RuntimeError (der Aufruf kommt aus einer Anfrage der Seite, nicht aus einer Kette)
    SPERRE_WARTEN_S = 900

    def __init__(self, modell):
        self.m = modell
        self.j = modell.j

    def _feld(self, i):
        return Torchfeld.feld(Exportleisterendermodell._feld(self.m, i), dtype=torch.float64)

    def _welt(self, belegt):
        """Weltmatrix je Knoten; `belegt` {(knoten, pfad): Wert} ersetzt TRS-Werte (ein Bild der Animation)."""
        knoten = self.j['nodes']
        eltern = {c: i for i, k in enumerate(knoten) for c in k.get('children', [])}
        welt = [None] * len(knoten)

        def rechnen(i):
            if welt[i] is not None:
                return welt[i]
            k = knoten[i]
            if 'matrix' in k and not any((i, p) in belegt for p in ('translation', 'rotation', 'scale')):
                lokal = Torchfeld.feld(k['matrix'], dtype=torch.float64).reshape(4, 4).T
            else:
                t, r, s = (belegt.get((i, p), k.get(p, v)) for p, v in (('translation', (0, 0, 0)), ('rotation', (0, 0, 0, 1)), ('scale', (1, 1, 1))))
                lokal = torch.eye(4, dtype=torch.float64, device='cuda')
                lokal[:3, :3] = Rotation.from_quat(Torchfeld.feld(r, dtype=torch.float64)).as_matrix() * Torchfeld.feld(s, dtype=torch.float64)
                lokal[:3, 3] = t
            welt[i] = (rechnen(eltern[i]) @ lokal) if i in eltern else lokal
            return welt[i]
        for i in range(len(knoten)):
            rechnen(i)
        return welt

    def _kapseln(self, kapseln, kinematik, namen, ibm):
        """Kapseln in der Bindelage der GLB, `nummer` = Platz im Skin (Format von `Koerperkollision`); Rest der Ausrichtung in mm; Haltung der KI im selben Rahmen (Koerperkollision Fassung 3) oder None."""
        bind = {n: Torchfeld.linalg_inv(m)[:3, 3] for n, m in zip(namen, ibm, strict=True)}
        paare = [(Torchfeld.feld(k['zentrum'], dtype=torch.float64), bind[k['name']]) for k in kinematik if k.get('name') in bind and k.get('zentrum') is not None]
        if len(paare) < 3:
            return [], None, None
        from KoerperKI_alle.kabsch import Kabsch
        a, b = Torchfeld.feld([p[0] for p in paare], copy=True), Torchfeld.feld([p[1] for p in paare], copy=True)
        _s, r, t = Kabsch.lage(a, b)
        rest_mm = float(Torchfeld.median(Torchfeld.linalg_norm(a @ r.T + t - b, dim=1))) * 1000
        platz = {n: i for i, n in enumerate(namen)}
        aus = [{'knochen': k['knochen'], 'nummer': platz[k['knochen']], 'a': (r @ Torchfeld.feld(k['a']) + t).tolist(), 'b': (r @ Torchfeld.feld(k['b']) + t).tolist(),
                'ra': float(k['ra']), 'rb': float(k['rb'])} for k in (kapseln.get('kapseln') or []) if k.get('knochen') in platz]
        return aus, rest_mm, self._haltung(kapseln.get('haltung'), kinematik, platz, r, t)

    @staticmethod
    def _haltung(haltung, kinematik, platz, r, t):
        """Haltung der KI (x' = D x + v in der Kinematik) je Platz im Skin, in der Bindelage x_b = r x + t: D_b = r D rᵀ, v_b = r v + t − D_b t; Gelenke ohne Kinematik bleiben, wie sie sind."""
        if not haltung:
            return None
        n = len(platz)
        dreh, versch = torch.tile(torch.eye(3, dtype=torch.float64, device='cuda'), (n, 1, 1)), torch.zeros((n, 3), dtype=torch.float64, device='cuda')
        for j, k in enumerate(kinematik):
            i = platz.get(k.get('name'))
            if i is None or j >= len(haltung['dreh']):
                continue
            dreh[i] = r @ Torchfeld.feld(haltung['dreh'][j], dtype=torch.float64) @ r.T
            versch[i] = r @ Torchfeld.feld(haltung['versch'][j], dtype=torch.float64) + t - dreh[i] @ t
        return {'dreh': dreh.tolist(), 'versch': versch.tolist()}

    def _ablegen(self, feld):
        feld = Torchfeld.feld(feld)
        while len(self.m.bin) % 4:
            self.m.bin.append(0)
        start = len(self.m.bin)
        self.m.bin += Torchfeld.als_bytes(feld)
        self.j.setdefault('bufferViews', []).append({'buffer': 0, 'byteOffset': start, 'byteLength': feld.nbytes})
        return len(self.j['bufferViews']) - 1

    def _ziel(self, versatz):
        """Ein dünn besetztes POSITION-Ziel (Accessor-Index); ohne geschobenen Punkt ein Eintrag 0 (glTF verlangt count ≥ 1). `byteOffset` steht ausdrücklich da, obwohl glTF 0 als Vorgabe kennt:
        F3D 3.5 verwirft die ganze Datei ohne ihn („Invalid accessor.sparse.indices.byteOffset value“, gemessen 04.11.2026 an Session3dTools_DanceKurz.glb, `_wegwerf/session3dtools/glb_byteoffset.py`)."""
        idx = Torchfeld.astype(torch.nonzero(Torchfeld.linalg_norm(versatz, dim=1) > 1e-6, as_tuple=True)[0], torch.uint32)
        if not len(idx):
            idx = torch.zeros(1, dtype=torch.uint32, device='cuda')
        self.j['accessors'].append({'componentType': 5126, 'count': len(versatz), 'type': 'VEC3',
                                    'min': Torchfeld.astype(Torchfeld.minimum(versatz.amin(0), 0), torch.float64).tolist(), 'max': Torchfeld.astype(Torchfeld.maximum(versatz.amax(0), 0), torch.float64).tolist(),
                                    'sparse': {'count': int(len(idx)), 'indices': {'bufferView': self._ablegen(idx), 'byteOffset': 0, 'componentType': 5125},
                                               'values': {'bufferView': self._ablegen(Torchfeld.astype(versatz[idx], torch.float32)), 'byteOffset': 0}}})
        return len(self.j['accessors']) - 1

    @contextmanager
    def _karte(self):
        """Die Karte über die Gpusperre (höchstens `SPERRE_WARTEN_S`); danach ist der Zwischenspeicher der Karte frei und die Priorität des Prozesses wie vorher —
        `Gpusperre` senkt sie auf BelowNormal, im Serverprozess bliebe das sonst bis zum Neustart."""
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError('Kollision im Export: keine CUDA-Karte')
        mesh = str(settings.TOOLS_ROOT / 'meshgenesis')
        if mesh not in sys.path:
            sys.path.insert(0, mesh)
        from meshgenesis_gpusperre import Gpusperre
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.GetPriorityClass.argtypes = [ctypes.c_void_p]
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        vorher = k.GetPriorityClass(k.GetCurrentProcess())
        sperre = Gpusperre('exportleiste_kollision_%d' % os.getpid(), bedarf=self.GPU_BEDARF_GB)
        sperre.WARTEN_S = self.SPERRE_WARTEN_S
        try:
            with sperre:
                try:
                    yield
                finally:
                    torch.cuda.empty_cache()
        except SystemExit as e:                                                  # Gpusperre ohne Platz nach WARTEN_S
            raise RuntimeError('Kollision im Export: %s' % e) from None
        finally:
            if vorher:
                k.SetPriorityClass(k.GetCurrentProcess(), vorher)

    def einbauen(self, kapseln, kinematik):
        anim = (self.j.get('animations') or [None])[-1]
        if not anim or not anim.get('channels') or not (kapseln or {}).get('kapseln'):
            return {'stuecke': 0, 'grund': 'keine Bewegung oder keine Kapseln'}
        with self._karte():
            return self._einbauen(anim, kapseln, kinematik)

    def _einbauen(self, anim, kapseln, kinematik):
        from KoerperKI_alle.koerperkollision import Koerperkollision
        zeiten = self._feld(anim['samplers'][anim['channels'][0]['sampler']]['input'])[:, 0]
        spuren = [(c['target']['node'], c['target']['path'], self._feld(anim['samplers'][c['sampler']]['output'])) for c in anim['channels']
                  if c['target']['path'] in ('translation', 'rotation', 'scale')]
        bilder = sorted(set(range(0, len(zeiten), self.SCHRITT)) | {len(zeiten) - 1})
        welten = [self._welt({(n, p): w[f] for n, p, w in spuren}) for f in bilder]
        bericht = {'bilder': len(bilder), 'schritt': self.SCHRITT, 'stuecke': []}
        for ni, k in enumerate(self.j['nodes']):
            if 'mesh' not in k or 'skin' not in k or not str(k.get('name', '')).startswith(self.PRAEFIX):
                continue
            skin = self.j['skins'][k['skin']]
            namen = [self.j['nodes'][g].get('name', '') for g in skin['joints']]
            ibm = self._feld(skin['inverseBindMatrices']).reshape(-1, 4, 4).permute(0, 2, 1)
            kap, rest_mm, haltung = self._kapseln(kapseln, kinematik, namen, ibm)
            if not kap:
                continue
            gelenke = [Torchfeld.einsum('gij,gjk->gik', Torchfeld.feld([w[g] for g in skin['joints']], copy=True), ibm)[:, :3, :] for w in welten]
            stueck = {'name': k['name'], 'rahmen_mm': round(rest_mm, 2), 'kapseln': len(kap), 'geschoben_max': 0, 'versatz_max_mm': 0.0}
            mesh = self.j['meshes'][k['mesh']]
            for prim in mesh['primitives']:
                prim['targets'] = [{'POSITION': self._ziel(v)} for v in self._versaetze(prim, gelenke, Koerperkollision({'kapseln': kap, 'haltung': haltung}), stueck)]
            mesh['weights'] = [0.0] * len(bilder)
            mesh.setdefault('extras', {})['targetNames'] = ['kollision_%04d' % f for f in bilder]
            t = self.m._anhaengen(zeiten[bilder], 'SCALAR', minmax=True)
            anim['samplers'].append({'input': t, 'output': self.m._anhaengen(torch.eye(len(bilder), dtype=torch.float64, device='cuda').reshape(-1), 'SCALAR'), 'interpolation': 'LINEAR'})
            anim['channels'].append({'sampler': len(anim['samplers']) - 1, 'target': {'node': ni, 'path': 'weights'}})
            bericht['stuecke'].append(stueck)
        return bericht

    @staticmethod
    def _drehung(m, runden=10):
        """Nächste Drehung zu je einer 3×3-Matrix (W, 3, 3) — der orthogonale Faktor der Polarzerlegung, = U Vᵀ der SVD — per Newton-Iteration X ← (γ X + X⁻ᵀ / γ) / 2 mit
        γ = |det X|^(−1/3) (Higham 1986, „Computing the polar decomposition“); X⁻ᵀ = Kofaktoren / det, nur elementweise Rechnung. An 27.223 Mischungen (Haar von Venus, ein Bild,
        float64): `torch.linalg.svd` 121 ms, hier 24 ms, Unterschied zu U Vᵀ höchstens 2,2e-15 (`_wegwerf/exportleiste/schieben_typ_probe.py`)."""
        import torch
        x = m
        for _ in range(runden):
            c0, c1, c2 = x[:, :, 0], x[:, :, 1], x[:, :, 2]
            kof = torch.stack([torch.cross(c1, c2, dim=1), torch.cross(c2, c0, dim=1), torch.cross(c0, c1, dim=1)], dim=2)      # det · X⁻ᵀ
            det = (c0 * kof[:, :, 0]).sum(1)
            det = torch.where(det.abs() < 1e-30, torch.full_like(det, 1e-30), det)[:, None, None]
            g = det.abs() ** (-1.0 / 3.0)
            x = 0.5 * (g * x + kof / (det * g))
        return x

    def _versaetze(self, prim, gelenke, kollision, stueck):
        """Je Bild der Versatz der Punkte dieser Primitive in der Bindelage (N, 3), gerechnet auf der Karte. `v`, `gl`, `gw` sind über alle Bilder dieselben Tensoren: `schieben` nimmt
        das Stück beim ersten Bild als CUDA-Graphen auf und erkennt es an diesen Objekten wieder. `ruhe` = Bindelage, derselbe Rahmen wie die Kapseln (`_kapseln`): geschoben wird
        nur, was tiefer in einer Kapsel liegt als in der Haltung der KI (Fassung 3, ohne `haltung` als in der Ruhe). Bis 01.11.2026 auf der CPU, gemessen 2,6 s je Bild am Haar von Venus (377.752 Punkte).
        Geschoben wird in float32 wie im Shader der Seite (WebGL): am Haar von Venus 18 ms je Bild gegen 170 ms in float64, Schub höchstens 0,0002 mm anders, gleich viele Punkte geschoben
        (`_wegwerf/exportleiste/schieben_typ_probe.py`, 01.11.2026, Karte dabei zu 55–63 % von einem anderen Lauf belegt). Gehäutet wird in float64 (`Kostuemgpu.haeuten`)."""
        import torch
        from meshgenesis_kostuemgpu import Kostuemgpu
        kg = Kostuemgpu.an()
        v = kg.feld(self._feld(prim['attributes']['POSITION']), torch.float64)
        gl = kg.feld(self._feld(prim['attributes']['JOINTS_0']), torch.int64)
        gw = kg.feld(self._feld(prim['attributes']['WEIGHTS_0']), torch.float64)
        gw = gw / gw.sum(1, keepdim=True).clamp_min(1e-9)
        v32, gw32 = v.float(), gw.float()
        for jm in gelenke:
            bild = SimpleNamespace(dreh=jm[:, :, :3], lage=jm[:, :, 3], zentren=torch.zeros((len(jm), 3), dtype=torch.float64, device='cuda'))
            q0 = kg.haeuten(bild, v, gl, gw).float()
            d = kollision.schieben(q0, gl, gw32, bild, ruhe=v32) - q0
            weg = torch.nonzero(d.norm(dim=1) > 1e-7)[:, 0]
            versatz = torch.zeros((len(v), 3), dtype=torch.float32, device='cuda')
            if len(weg):
                mischung = (gw32[weg, :, None, None] * kg.feld(jm[:, :, :3], torch.float32)[gl[weg]]).sum(1)    # Σ w_k D_k je geschobenem Punkt (W, 3, 3)
                versatz[weg.cpu().numpy()] = torch.einsum('nji,nj->ni', self._drehung(mischung), d[weg]).cpu().numpy()
                stueck['geschoben_max'] = max(stueck['geschoben_max'], int(len(weg)))
                stueck['versatz_max_mm'] = round(max(stueck['versatz_max_mm'], float(d[weg].norm(dim=1).max()) * 1000), 1)
            yield versatz
