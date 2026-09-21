# -*- coding: utf-8 -*-
"""Bildmodellposierung — der Genesis-Käfig in der Pose und Kamera JEDES Fotos (T1).

Konzept `Docu/konzepte/2026-09-20_modell-aus-bildern-regler-und-textur.md`, T1: Die
Fototextur projizierte den Käfig in Ruhehaltung gegen Fotos in Pose, die starre
Rig-Registrierung blieb an Damira 15,8–46,1 px daneben. Je Hauptbild liegt aus GVHMR
das SMPL-X-Netz in der Pose und Kamera des Fotos vor (`gvhmr.kamera.netz`, OpenGL-
Sicht, fx/fy/cx/cy). Hier wird der Käfig der Reglerstellung an das SMPL-X derselben
Betas in A-Pose gebunden (`G9netzwickel`, normiert) und auf das posierte Netz
übertragen — Ergebnis: der Käfig in Metern im Kameraraum (OpenCV: x rechts, y unten,
z nach vorn), dazu die Landmarken des Modells (COCO, Füße, Hände, Gesicht) ebenso.

Dateien unter `schaetzung/gvhmr/`: `<stamm>_kaefig_kamera.npy` (N, 3) und
`<stamm>_landmarken_kamera.npz` (`coco`, `fuesse`, `hand_l`, `hand_r`, `gesicht`).
`fuer_bild(b)` gibt `{posiert, landmarken, kamera_gvhmr: {fx, fy, cx, cy, breite,
hoehe}, wickel: {…}}` oder None (kein GVHMR, Kopfbild, Bildgröße passt nicht).
"""

import logging
import os

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Bildmodellposierung']


class Bildmodellposierung:
    KAEFIG = '%s_kaefig_kamera.npy'
    LANDMARKEN = '%s_landmarken_kamera.npz'
    #: OpenGL-Sicht (GVHMR-Ablage) → OpenCV (Runner): y und z negiert.
    SPIEGEL = np.array([1.0, -1.0, -1.0])
    TOLERANZ_PX = 2

    def __init__(self, job, ablage, modell):
        """`modell` = `G9texturmodell` der Reglerstellung (Käfig in Metern, Füße auf 0)."""
        self.job = job
        self.ablage = ablage
        self.modell = modell
        self._bindung = {}

    def ordner(self):
        from .bildmodellgvhmr import Bildmodellgvhmr

        return self.ablage.schaetzung() / Bildmodellgvhmr.UNTERORDNER

    # ---------------------------------------------------------- Nachholen

    @staticmethod
    def nachholen(job, ablage, bilder, melder=None):
        """Für jedes Körperbild der Textur die Pose und Kamera des Fotos aus GVHMR — rechnen, was
        fehlt (~70 s je Bild beim ersten Mal), und den Feinabgleich am Rig nachholen, wo ein
        älterer Lauf ihn nicht hat (~10 s). Kopfbilder bleiben beim Rig (FLAME kommt später).
        Schreibt die frischen `gvhmr`-Felder in die übergebenen Einträge."""
        from .bildmodellgvhmr import Bildmodellgvhmr

        dienst = Bildmodellgvhmr(job, ablage)
        offen = []
        for b in bilder:
            if b.get('video') or b.get('kategorie') == 'kopf' or b.get('kamera_bekannt'):
                continue
            k = (b.get('gvhmr') or {}).get('kamera') or {}
            fein = k.get('feinabgleich') or {}
            # Ohne `silhouette` stammt der Abgleich von vor dem 21.09.2026 (nur Rig) — mit Maske
            # nachrechnen (GVHMR liest sein Ergebnis, ~5 s + Abgleich ~10 s).
            if not k.get('netz') or (b.get('rigs') and (not fein or 'silhouette' not in fein)):
                offen.append(b['datei'])
        for i, datei in enumerate(offen):
            if melder:
                melder(0.03, 'Pose je Foto (GVHMR) %d / %d: %s' % (i + 1, len(offen), datei))
            try:
                dienst.ausfuehren(datei, melder=None)
            except Exception as fehler:  # noqa: BLE001 — dann bleibt das Bild beim Rig
                logger.warning('Bildmodell %s: GVHMR für %s: %s', job.kennung, datei, fehler)
        if offen:
            job.refresh_from_db(fields=['bilder'])
            frisch = {b['datei']: b for b in job.bilder}
            for b in bilder:
                if b['datei'] in frisch and frisch[b['datei']].get('gvhmr'):
                    b['gvhmr'] = frisch[b['datei']]['gvhmr']
        return offen

    # ------------------------------------------------------------ Je Bild

    def fuer_bild(self, b):
        g = (b or {}).get('gvhmr') or {}
        k = g.get('kamera') or {}
        ordner = self.ordner()
        pfad = ordner / os.path.basename(k.get('netz') or '')
        if not (g.get('betas') and k.get('netz') and k.get('fx') and pfad.is_file()):
            return None
        if b.get('kategorie') == 'kopf':
            return None    # GVHMR erfindet auf einem Kopfausschnitt einen Körper (Damira 18daz3d_z5)
        # GVHMR rechnet über ein Standvideo mit GERADEN Kantenlängen (2000×2667 → 2000×2666):
        # bis 2 px Unterschied gelten die Kameradaten für das Foto.
        if b.get('breite') and b.get('hoehe') and (
                abs(int(k.get('breite') or 0) - int(b['breite'])) > self.TOLERANZ_PX
                or abs(int(k.get('hoehe') or 0) - int(b['hoehe'])) > self.TOLERANZ_PX):
            logger.warning('Bildmodell %s: GVHMR-Kamera von %s passt nicht zur Bildgröße (%s×%s gegen %s×%s)',
                           self.job.kennung, b.get('datei'), k.get('breite'), k.get('hoehe'),
                           b['breite'], b['hoehe'])
            return None
        dreiecke = np.load(ordner / os.path.basename(g.get('dreiecke') or 'smplx_dreiecke.npy'))
        dreiecke = dreiecke.astype(np.int64)
        posiert = np.load(pfad).astype(np.float64) * self.SPIEGEL
        bindung, hoehe_s = self._binden(k.get('betas') or g['betas'], dreiecke)
        kaefig = bindung['kaefig'].anwenden(posiert, dreiecke, hoehe_s)
        landmarken = {}
        for name, wickel in bindung['landmarken'].items():
            werte = wickel['wickel'].anwenden(posiert, dreiecke, hoehe_s)
            voll = np.full((wickel['anzahl'], 3), np.nan)
            voll[wickel['gueltig']] = werte
            landmarken[name] = voll
        stamm = os.path.splitext(b['datei'])[0]
        np.save(ordner / (self.KAEFIG % stamm), kaefig.astype(np.float32))
        np.savez(ordner / (self.LANDMARKEN % stamm), **landmarken)
        return {
            'posiert': str(ordner / (self.KAEFIG % stamm)),
            'landmarken': str(ordner / (self.LANDMARKEN % stamm)),
            'kamera_gvhmr': {n: float(k[n]) for n in ('fx', 'fy', 'cx', 'cy')}
            | {'breite': int(k['breite']), 'hoehe': int(k['hoehe'])},
            'wickel': bindung['kaefig'].steckbrief(),
        }

    # ------------------------------------------------------------ Bindung

    def _binden(self, betas, dreiecke):
        """Käfig und Landmarken an das SMPL-X dieser Betas in A-Pose binden (einmal je Betas)."""
        from Genesis9.netzwickel import G9netzwickel
        from Genesis9.zielnetz import G9zielnetz

        schluessel = tuple(round(float(v), 3) for v in betas)
        if schluessel in self._bindung:
            return self._bindung[schluessel]
        rest = G9zielnetz.aus(betas, None, symmetrisch=False).punkte
        rest_n, hoehe_s, _ = G9netzwickel.normiert(rest)
        kaefig_n, hoehe_g, mitte_g = G9netzwickel.normiert(self.modell.punkte)
        aus = {'kaefig': G9netzwickel.binden(rest_n, dreiecke, kaefig_n), 'landmarken': {}}
        daten = self.modell.daten()
        for feld, werte in daten.items():
            if not feld.startswith('lm_'):
                continue
            name = feld[3:]
            w = np.asarray(werte, dtype=np.float64)
            gueltig = np.isfinite(w).all(1)
            if not gueltig.any():
                continue
            aus['landmarken'][name] = {
                'anzahl': int(len(w)), 'gueltig': gueltig,
                'wickel': G9netzwickel.binden(rest_n, dreiecke, (w[gueltig] - mitte_g) / hoehe_g),
            }
        self._bindung[schluessel] = (aus, hoehe_s)
        return self._bindung[schluessel]
