# -*- coding: utf-8 -*-
"""Gesichtsformziel — die Zielkurven von „Kopf-Eigen" aus dem Kopfnetz eines „Mesh to 3D"-Auftrags.

Das Netz (Kopfnetz, sonst Körpernetz) in der Lage des Körpers (`scan_lage.npz`, `kopf_lage.npz`),
dazu seine 478 Gesichtspunkte (`landmarken.npz`, `gesicht`) — beides über die Registrierung der Anpassung
(`lage`: Kopf der Figur in Ruhe gegen posiert) in die Ruhelage der Figur gelegt und im Rahmen der FIGUR
gemessen: Tiefenprofile (`G9gesichtsschnitte`) und Konturpunkte von vorn.

KEINE VORGABE, wo das Netz nicht das Gesicht zeigt:
  * Haar — die Farbe am Schnittpunkt ist keine Haut: nicht rot vor blau und gesättigt
    (`Meshfigurkopfabgleich.ist_haut`, dieselbe Regel wie der Farbangleich) oder deutlich dunkler bzw.
    heller als der Hautton um die Nase (`HELL`). Am Damira-Kopfnetz liegen Strähnen vor Stirn und
    Schläfen — die Figur sollte dort nicht in die Frisur wachsen.
  * Augen — Hunyuan legt eine Mulde mit Malerei an (`AUGE_RAND` um die Lidkontur).
  * Mundspalt — innere Lippenkontur.
Die Konturpunkte (Lage und Größe von vorn) gelten alle: die Malerei zeigt Lider, Lippen und Brauen dort,
wo sie sein sollen.
"""

import json
import logging

import math
import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

logger = logging.getLogger('core')

__all__ = ['Gesichtsformziel']


class Gesichtsformziel:
    AUGE_RAND = 0.003
    HELL = (0.55, 1.7)
    #: Hautton aus den Proben um die Nase: |u| und Lage in diesem Fenster (Meter), Augen ausgenommen.
    TONFENSTER = 0.035
    _vorrat = {}

    def __init__(self, job):
        self.job = job
        self.ablage = self._ablage_fuer(job)

    @staticmethod
    def _ablage_fuer(job):
        """Die Ablage nach dem Auftragstyp — nicht immer „Mesh to 3D": BlenderModel (29.09.2026) und
        „2D3D Kleider" (`Engine2d3dKleiderauftrag`, Option `koerper.quelle = rechnen`, 30.09.2026) nutzen dieselben
        Figur-Schritte (`Meshfigurkette`, `Meshfigurhaar`, …) auf EIGENEN Ordnern. Fest auf `Meshfigurablage`
        verdrahtet, fiel das erst beim ersten echten End-zu-End-Lauf auf: `FileNotFoundError …
        meshfigurauftraege\\<kennung>\\…` für einen Auftrag, der gar keinen solchen Ordner hat (Edgar,
        29.09.2026, und erneut 30.09.2026 mit dem ersten Lauf von „koerper.quelle = rechnen")."""
        from ..daten.meshfigurablage import Meshfigurablage
        from ..models import Blendermodellauftrag, Engine2d3dKleiderauftrag

        if isinstance(job, Blendermodellauftrag):
            from ..daten.blendermodellablage import Blendermodellablage

            return Blendermodellablage(job.kennung)
        if isinstance(job, Engine2d3dKleiderauftrag):
            from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage

            return Engine2d3dKleiderablage(job.kennung)
        return Meshfigurablage(job.kennung)

    def laden(self):
        """`(scan, gesicht)` — das Netz in der Lage des Körpers und seine Gesichtspunkte (478, 3)."""
        from ..daten.meshto3dpfad import Meshto3dpfad

        arbeit = self.ablage.arbeit()
        with open(arbeit / 'auftrag.json', encoding='utf-8') as f:
            auftrag = json.load(f)
        with Npztorch.lesen(arbeit / 'scan_lage.npz') as d:
            matrix = d['matrix']
        with Meshto3dpfad():
            from meshfigur_scan import Meshfigurscan

            if auftrag.get('kopfnetz') and Npztorch.da(arbeit / 'kopf_lage.npz'):
                with Npztorch.lesen(arbeit / 'kopf_lage.npz') as d:
                    matrix = matrix @ d['matrix_roh']
                scan = Meshfigurscan.laden(auftrag['kopfnetz'])
            else:
                scan = Meshfigurscan.laden(auftrag['netz'])
        scan.anwenden(matrix)
        with Npztorch.lesen(arbeit / 'landmarken.npz') as d:
            gesicht = Torchfeld.feld(d['gesicht'], dtype=torch.float64)
        return scan, gesicht

    def lage(self):
        """`(R, t)` — Ruhelage der Figur → Weltlage des Netzes (Kopf starr, Kabsch).

        Aus der Anpassung selbst: `genesis_ende.npz` (Käfig in Ruhe) gegen `posiert.npy` (derselbe Käfig in
        der Haltung des Netzes), nur Kopfpunkte. NICHT über die Landmarkenrahmen beider Netze: die lagen bei
        Damira 3,4° gegeneinander (Augenwinkel 33 im Kopfnetz 4,3 mm tiefer, in der Augenmulde; Stirnpunkt 10
        8,9 mm höher, am Haaransatz) — der Morph verdrehte das Gesicht gegen den Schädel."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile

        with Npztorch.lesen(self.ablage.arbeit('genesis_ende.npz')) as d:
            ruhe = Torchfeld.feld(d['punkte'], dtype=torch.float64)
        welt = Torchfeld.astype(Npztorch.lesen(self.ablage.arbeit('posiert.npy')), torch.float64)
        kopf = G9koerperteile.genesis_punkte(G9haut.holen()) == 0
        a, b = ruhe[kopf], welt[kopf]
        ma, mb = a.mean(0), b.mean(0)
        u, _, vt = Torchfeld.linalg_svd(Torchfeld.feld((a - ma).T @ (b - mb)))
        r = (u @ Torchfeld.diag(Torchfeld.feld([1.0, 1.0, Torchfeld.sign(Torchfeld.linalg_det(u @ vt))])) @ vt).T
        return r, mb - r @ ma

    def vorhanden(self):
        namen = ('landmarken.npz', 'scan_lage.npz', 'genesis_ende.npz', 'posiert.npy')
        return all(Npztorch.da(self.ablage.arbeit(n)) for n in namen)

    def ziel(self, lagen, rahmen):
        """`{'schnitte': [...] (Meter, NaN = keine Vorgabe), 'punkte': {nr: (x', y')}}` im Rahmen `rahmen` der
        Figur (Ruhelage) — das Netz wird mit `lage` dorthin gelegt."""
        stand = [Npztorch.stat(self.ablage.arbeit(n)).st_mtime_ns for n in ('landmarken.npz', 'posiert.npy')]
        schluessel = (self.job.kennung, repr(sorted((k, tuple(Torchfeld.liste(v))) for k, v in lagen.items())),
                      tuple(Torchfeld.round(rahmen.ursprung, 5).tolist()), tuple(stand))
        if schluessel in self._vorrat:
            return self._vorrat[schluessel]
        from Genesis9.gesichtsrahmen import G9gesichtsrahmen
        from Genesis9.gesichtsschnitte import G9gesichtsschnitte

        scan, gesicht = self.laden()
        r, t = self.lage()
        scan.punkte = (Torchfeld.feld(scan.punkte, dtype=torch.float64) - t) @ r
        gesicht = (gesicht - t) @ r
        profile = G9gesichtsschnitte(rahmen).profile(scan.punkte, scan.flaechen[scan.gueltig], lagen)
        # `profile` rechnete auf den gültigen Flächen — die Flächennummern zurück auf das ganze Netz.
        gueltig = torch.flatten(scan.gueltig).nonzero()[:, 0]
        for p in profile:
            p['flaeche'] = torch.where(p['flaeche'] >= 0, gueltig[Torchfeld.maximum(p['flaeche'], 0)], -1)
        self._ohne_vorgabe(scan, rahmen, profile, gesicht)
        punkte = {j: rahmen.hinein(gesicht[j])[:2] for k in G9gesichtsrahmen.KONTUREN
                  for j in G9gesichtsrahmen.KONTUREN[k] if Torchfeld.isfinite(gesicht[j]).all()}
        aus = {'schnitte': profile, 'punkte': punkte}
        if len(self._vorrat) > 4:
            self._vorrat.clear()
        self._vorrat[schluessel] = aus
        return aus

    # ------------------------------------------------------------ Ausnahmen

    def _ohne_vorgabe(self, scan, rahmen, profile, gesicht):
        """Haar, Augenmulden und Mundspalt auf NaN — in `profile` (Meter) selbst. Augen und Mund nach den
        Landmarken des NETZES (`gesicht`, in der Ruhelage der Figur), nicht nach denen der Figur."""
        from Genesis9.gesichtsrahmen import G9gesichtsrahmen

        def kontur(name):
            return rahmen.hinein(gesicht[list(G9gesichtsrahmen.KONTUREN[name])])[:, :2]

        farben = {id(p): self._farben(scan, p) for p in profile}
        ton = self._hautton(rahmen, profile, farben)
        augen = [kontur(k) for k in ('auge_rechts', 'auge_links')]
        mund = kontur('mund')
        for p in profile:
            achse = 1 if p['art'] == 'waagerecht' else 0
            xy = torch.zeros((len(p['u']), 2), dtype=torch.float64, device='cuda')
            xy[:, achse], xy[:, 1 - achse] = p['lage'], p['u']
            weg = ~self._haut(farben[id(p)], ton)
            for kontur in augen:
                if Torchfeld.isfinite(kontur).all():
                    abstand = Torchfeld.amin(Torchfeld.linalg_norm(xy[:, None, :] - kontur[None, :, :], dim=2), dim=1)
                    nah = abstand < self.AUGE_RAND
                    weg |= G9gesichtsrahmen.innen(kontur, xy) | nah
            if Torchfeld.isfinite(mund).all():
                weg |= G9gesichtsrahmen.innen(mund, xy)
            p['z'] = torch.where(weg, math.nan, p['z'])

    @staticmethod
    def _farben(scan, p):
        """(n, 3) Farbe des Netzes an den Schnittpunkten (NaN ohne Treffer)."""
        import trimesh

        aus = Torchfeld.full((len(p['u']), 3), math.nan)
        ok = p['flaeche'] >= 0
        if ok.any():
            ecken = scan.punkte[scan.flaechen[p['flaeche'][ok]]]
            bary = Torchfeld.clip(trimesh.triangles.points_to_barycentric(ecken, p['punkt'][ok]), 0, 1)
            bary /= Torchfeld.maximum(bary.sum(axis=1, keepdims=True), 1e-9)
            aus[ok] = scan.farben(p['flaeche'][ok], bary)
        return aus

    def _hautton(self, rahmen, profile, farben):
        """Median-Helligkeit (Y) der Haut um die Nase — Bezug für „zu dunkel/zu hell"."""
        werte = []
        for p in profile:
            nah = (Torchfeld.abs(p['u']) < self.TONFENSTER) & (Torchfeld.abs(p['lage']) < self.TONFENSTER)
            f = farben[id(p)][nah]
            f = f[Torchfeld.isfinite(f).all(axis=1)]
            if len(f):
                werte.append(f[self._ist_haut(f)])
        alle = Torchfeld.cat(werte) if werte else torch.zeros((0, 3), dtype=torch.float64, device='cuda')
        return float(Torchfeld.median(self._hell(alle))) if len(alle) else None

    def _haut(self, farben, ton):
        ok = Torchfeld.isfinite(farben).all(axis=1)
        aus = torch.zeros(len(farben), dtype=torch.bool, device='cuda')
        f = farben[ok]
        haut = self._ist_haut(f)
        if ton:
            y = self._hell(f) / ton
            haut &= (y > self.HELL[0]) & (y < self.HELL[1])
        aus[ok] = haut
        return aus

    @staticmethod
    def _hell(f):
        f = Torchfeld.feld(f, dtype=torch.float64)
        return 0.299 * f[:, 0] + 0.587 * f[:, 1] + 0.114 * f[:, 2]

    @staticmethod
    def _ist_haut(f):
        from ..daten.meshto3dpfad import Meshto3dpfad

        with Meshto3dpfad():
            from meshfigur_kopfabgleich import Meshfigurkopfabgleich

            return Meshfigurkopfabgleich.ist_haut(f)
