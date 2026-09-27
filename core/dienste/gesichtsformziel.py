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

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Gesichtsformziel']


class Gesichtsformziel:
    AUGE_RAND = 0.003
    HELL = (0.55, 1.7)
    #: Hautton aus den Proben um die Nase: |u| und Lage in diesem Fenster (Meter), Augen ausgenommen.
    TONFENSTER = 0.035
    _vorrat = {}

    def __init__(self, job):
        from ..daten.meshfigurablage import Meshfigurablage

        self.job = job
        self.ablage = Meshfigurablage(job.kennung)

    def laden(self):
        """`(scan, gesicht)` — das Netz in der Lage des Körpers und seine Gesichtspunkte (478, 3)."""
        from ..daten.wrapperpfad import Wrapperpfad

        arbeit = self.ablage.arbeit()
        with open(arbeit / 'auftrag.json', encoding='utf-8') as f:
            auftrag = json.load(f)
        with np.load(arbeit / 'scan_lage.npz') as d:
            matrix = d['matrix']
        with Wrapperpfad():
            from meshfigur_scan import Meshfigurscan

            if auftrag.get('kopfnetz') and (arbeit / 'kopf_lage.npz').is_file():
                with np.load(arbeit / 'kopf_lage.npz') as d:
                    matrix = matrix @ d['matrix_roh']
                scan = Meshfigurscan.laden(auftrag['kopfnetz'])
            else:
                scan = Meshfigurscan.laden(auftrag['netz'])
        scan.anwenden(matrix)
        with np.load(arbeit / 'landmarken.npz') as d:
            gesicht = np.asarray(d['gesicht'], dtype=np.float64)
        return scan, gesicht

    def lage(self):
        """`(R, t)` — Ruhelage der Figur → Weltlage des Netzes (Kopf starr, Kabsch).

        Aus der Anpassung selbst: `genesis_ende.npz` (Käfig in Ruhe) gegen `posiert.npy` (derselbe Käfig in
        der Haltung des Netzes), nur Kopfpunkte. NICHT über die Landmarkenrahmen beider Netze: die lagen bei
        Damira 3,4° gegeneinander (Augenwinkel 33 im Kopfnetz 4,3 mm tiefer, in der Augenmulde; Stirnpunkt 10
        8,9 mm höher, am Haaransatz) — der Morph verdrehte das Gesicht gegen den Schädel."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile

        with np.load(self.ablage.arbeit('genesis_ende.npz')) as d:
            ruhe = np.asarray(d['punkte'], dtype=np.float64)
        welt = np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64)
        kopf = G9koerperteile.genesis_punkte(G9haut.holen()) == 0
        a, b = ruhe[kopf], welt[kopf]
        ma, mb = a.mean(0), b.mean(0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        r = (u @ np.diag([1.0, 1.0, np.sign(np.linalg.det(u @ vt))]) @ vt).T
        return r, mb - r @ ma

    def vorhanden(self):
        namen = ('landmarken.npz', 'scan_lage.npz', 'genesis_ende.npz', 'posiert.npy')
        return all(self.ablage.arbeit(n).is_file() for n in namen)

    def ziel(self, lagen, rahmen):
        """`{'schnitte': [...] (Meter, NaN = keine Vorgabe), 'punkte': {nr: (x', y')}}` im Rahmen `rahmen` der
        Figur (Ruhelage) — das Netz wird mit `lage` dorthin gelegt."""
        stand = [self.ablage.arbeit(n).stat().st_mtime_ns for n in ('landmarken.npz', 'posiert.npy')]
        schluessel = (self.job.kennung, repr(sorted((k, tuple(v)) for k, v in lagen.items())),
                      tuple(np.round(rahmen.ursprung, 5)), tuple(stand))
        if schluessel in self._vorrat:
            return self._vorrat[schluessel]
        from Genesis9.gesichtsrahmen import G9gesichtsrahmen
        from Genesis9.gesichtsschnitte import G9gesichtsschnitte

        scan, gesicht = self.laden()
        r, t = self.lage()
        scan.punkte = (np.asarray(scan.punkte, dtype=np.float64) - t) @ r
        gesicht = (gesicht - t) @ r
        profile = G9gesichtsschnitte(rahmen).profile(scan.punkte, scan.flaechen[scan.gueltig], lagen)
        # `profile` rechnete auf den gültigen Flächen — die Flächennummern zurück auf das ganze Netz.
        gueltig = np.flatnonzero(scan.gueltig)
        for p in profile:
            p['flaeche'] = np.where(p['flaeche'] >= 0, gueltig[np.maximum(p['flaeche'], 0)], -1)
        self._ohne_vorgabe(scan, rahmen, profile, gesicht)
        punkte = {j: rahmen.hinein(gesicht[j])[:2] for k in G9gesichtsrahmen.KONTUREN
                  for j in G9gesichtsrahmen.KONTUREN[k] if np.isfinite(gesicht[j]).all()}
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
            xy = np.zeros((len(p['u']), 2))
            xy[:, achse], xy[:, 1 - achse] = p['lage'], p['u']
            weg = ~self._haut(farben[id(p)], ton)
            for kontur in augen:
                if np.isfinite(kontur).all():
                    abstand = np.linalg.norm(xy[:, None, :] - kontur[None, :, :], axis=2).min(axis=1)
                    nah = abstand < self.AUGE_RAND
                    weg |= G9gesichtsrahmen.innen(kontur, xy) | nah
            if np.isfinite(mund).all():
                weg |= G9gesichtsrahmen.innen(mund, xy)
            p['z'] = np.where(weg, np.nan, p['z'])

    @staticmethod
    def _farben(scan, p):
        """(n, 3) Farbe des Netzes an den Schnittpunkten (NaN ohne Treffer)."""
        import trimesh

        aus = np.full((len(p['u']), 3), np.nan)
        ok = p['flaeche'] >= 0
        if ok.any():
            ecken = scan.punkte[scan.flaechen[p['flaeche'][ok]]]
            bary = np.clip(trimesh.triangles.points_to_barycentric(ecken, p['punkt'][ok]), 0, 1)
            bary /= np.maximum(bary.sum(axis=1, keepdims=True), 1e-9)
            aus[ok] = scan.farben(p['flaeche'][ok], bary)
        return aus

    def _hautton(self, rahmen, profile, farben):
        """Median-Helligkeit (Y) der Haut um die Nase — Bezug für „zu dunkel/zu hell"."""
        werte = []
        for p in profile:
            nah = (np.abs(p['u']) < self.TONFENSTER) & (abs(p['lage']) < self.TONFENSTER)
            f = farben[id(p)][nah]
            f = f[np.isfinite(f).all(axis=1)]
            if len(f):
                werte.append(f[self._ist_haut(f)])
        alle = np.concatenate(werte) if werte else np.zeros((0, 3))
        return float(np.median(self._hell(alle))) if len(alle) else None

    def _haut(self, farben, ton):
        ok = np.isfinite(farben).all(axis=1)
        aus = np.zeros(len(farben), dtype=bool)
        f = farben[ok]
        haut = self._ist_haut(f)
        if ton:
            y = self._hell(f) / ton
            haut &= (y > self.HELL[0]) & (y < self.HELL[1])
        aus[ok] = haut
        return aus

    @staticmethod
    def _hell(f):
        f = np.asarray(f, dtype=np.float64)
        return 0.299 * f[:, 0] + 0.587 * f[:, 1] + 0.114 * f[:, 2]

    @staticmethod
    def _ist_haut(f):
        from ..daten.wrapperpfad import Wrapperpfad

        with Wrapperpfad():
            from meshfigur_kopfabgleich import Meshfigurkopfabgleich

            return Meshfigurkopfabgleich.ist_haut(f)
