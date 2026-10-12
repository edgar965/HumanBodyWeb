# -*- coding: utf-8 -*-
"""Mesh3dansicht — ein Netz aus bekannter Kamera als Bild rendern (11.10.2026): die Vorlage für Dinge, die ein Bild einer Person brauchen.

Der Schritt „Pose“ des Imports (`Blendimportpose`) gibt SAM 3D Body kein Foto, sondern ein Rendering des Körpers: von vorn (+Z, die Seite, die `Blendimportkoerper` aus Blenders −Y macht),
orthografisch, mit Alpha aus der Tiefenkarte. Weil die Kamera bekannt ist, liegt das Netz in der Silhouette des Bildes exakt (IoU ≈ 1) — die Abbildung der Gelenke ins Netz
(`Engine2d3dKleiderposeabbildung`) braucht dann keine Annahmen über ein Foto. Gleiche Bauart wie `Meshicon` (pyrender, python14, im Arbeitsprozess, nie im Django-Server);
das Konzept der Jobseite sieht dieselben Renderings als Vorlagen der Iterationen vor (`Docu/konzepte/2026-10-11_mesh-3d-konzept.md`).
"""

import os

import numpy as np

__all__ = ['Mesh3dansicht']


class Mesh3dansicht:
    #: Hochzählen, wenn sich das Rendering ändert (Kamera, Licht, Hintergrund): Ergebnisse, die an einer Ansicht hängen (`Posebestimmung.sam`), gelten nur für ihre Fassung.
    FASSUNG = 1
    KANTE = 1024
    #: Rand um die größere Ausdehnung des Netzes.
    RAND = 1.1
    HINTERGRUND = (0.5, 0.5, 0.5, 1.0)
    UMGEBUNG = (0.82, 0.82, 0.82)
    LICHT = 1.4
    #: Die vier Ansichten der Fotoprojektion — (Blickrichtung zur Kamera, Bild rechts, Bild oben), Wort für Wort `mesh_fototextur.ACHSEN` (`VideoToBVH/wrappers`): vorne = Kamera bei +Z, Bild rechts +X;
    #: hinten = −Z, rechts −X; „rechts“ (das Foto der rechten Seite) = Kamera bei −X, Bild rechts +Z; „links“ = Kamera bei +X, Bild rechts −Z; Y oben. Die Etiketten der Segmentierung gehören nur dann
    #: auf die richtigen Flächen, wenn Bild und Projektion diese Tabelle teilen (`Sapiensflaechen`).
    ACHSEN = {
        'vorne': ((0, 0, 1.0), (1.0, 0, 0), (0, 1.0, 0)),
        'hinten': ((0, 0, -1.0), (-1.0, 0, 0), (0, 1.0, 0)),
        'rechts': ((-1.0, 0, 0), (0, 0, 1.0), (0, 1.0, 0)),
        'links': ((1.0, 0, 0), (0, 0, -1.0), (0, 1.0, 0)),
    }

    @classmethod
    def rundum(cls, glb, ziele, kante=KANTE):
        """Rendert `glb` aus den Ansichten in `ziele` (`{rolle: Pfad}`, Rollen aus `ACHSEN`) — RGBA-PNG, quadratisch, Alpha = Netz, orthografisch, das Netz einmal geladen. Gibt `ziele` zurück.

        Quadrat je Ansicht: die größere der beiden Ausdehnungen in der Bildebene (von vorn und hinten Breite und Höhe, von der Seite Tiefe und Höhe) mit `RAND`; das Netz liegt mittig. Weil die Kamera
        bekannt ist, passt das Netz exakt in die Silhouette (`Sapiensflaechen.bildpassung` findet Maßstab und Mitte wieder)."""
        import pyrender
        import trimesh
        from PIL import Image

        geladen = trimesh.load(str(glb), process=False)
        szene_tm = geladen if isinstance(geladen, trimesh.Scene) else trimesh.Scene(geladen)
        tief, hoch = szene_tm.bounds
        mitte = (tief + hoch) / 2.0
        ausdehnung = hoch - tief
        if not np.isfinite(ausdehnung).all() or float(ausdehnung.max()) <= 0:
            raise ValueError('Netz ohne Ausdehnung: %s' % glb)
        abstand = float(np.linalg.norm(ausdehnung)) + 1.0
        szene = pyrender.Scene.from_trimesh_scene(szene_tm, bg_color=cls.HINTERGRUND, ambient_light=cls.UMGEBUNG)
        renderer = pyrender.OffscreenRenderer(kante, kante)
        try:
            for rolle, ziel in ziele.items():
                blick, rechts, oben = (np.asarray(v, dtype=np.float64) for v in cls.ACHSEN[rolle])
                spanne = max(abs(float(rechts @ ausdehnung)), abs(float(oben @ ausdehnung)))
                lage = np.eye(4)
                lage[:3, 0], lage[:3, 1], lage[:3, 2] = rechts, oben, blick          # Spalten der Kamera: rechts, oben, hinten (sie blickt entlang −z)
                lage[:3, 3] = mitte + blick * abstand
                halb = spanne * cls.RAND / 2.0
                kamera = szene.add(pyrender.OrthographicCamera(xmag=halb, ymag=halb, znear=0.05, zfar=1000.0), pose=lage)
                licht = szene.add(pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=cls.LICHT), pose=lage)
                try:
                    farbe, tiefe = renderer.render(szene)
                finally:
                    szene.remove_node(kamera)
                    szene.remove_node(licht)
                rgba = np.dstack([farbe[:, :, :3], np.where(tiefe > 0, 255, 0).astype(np.uint8)])
                Image.fromarray(rgba, 'RGBA').save(str(ziel))
        finally:
            renderer.delete()
        return ziele

    @classmethod
    def eingaben(cls, glb, kante=KANTE):
        """Was das Bild bestimmt: die Datei (Größe, Änderungszeit) und die Einstellungen des Renderings — JSON-fähig, zum Vergleichen. Das Bild selbst taugt nicht als Schlüssel: pyrender liefert von Lauf zu Lauf
        nicht bitgleiche Bilder (gemessen 12.10.2026: 0,02 % der Pixel um eine Stufe, Alpha gleich), seine Dateizeit ist jedes Mal neu."""
        s = os.stat(str(glb))
        return {'netz': [s.st_size, s.st_mtime_ns], 'ansicht': [cls.FASSUNG, kante, cls.RAND, list(cls.HINTERGRUND), list(cls.UMGEBUNG), cls.LICHT]}

    @classmethod
    def vorne(cls, glb, ziel, kante=KANTE):
        """Rendert `glb` von vorn nach `ziel` (RGBA-PNG, quadratisch, Alpha = Netz); gibt `ziel` zurück. Wirft, wenn das Netz keine Ausdehnung hat."""
        import pyrender
        import trimesh
        from PIL import Image

        geladen = trimesh.load(str(glb), process=False)
        szene_tm = geladen if isinstance(geladen, trimesh.Scene) else trimesh.Scene(geladen)
        tief, hoch = szene_tm.bounds
        mitte = (tief + hoch) / 2.0
        spanne = float(max(hoch[0] - tief[0], hoch[1] - tief[1]))
        if not np.isfinite(spanne) or spanne <= 0:
            raise ValueError('Netz ohne Ausdehnung: %s' % glb)
        szene = pyrender.Scene.from_trimesh_scene(szene_tm, bg_color=cls.HINTERGRUND, ambient_light=cls.UMGEBUNG)
        halb = spanne * cls.RAND / 2.0
        lage = np.eye(4)
        lage[:3, 3] = [mitte[0], mitte[1], hoch[2] + max(spanne, float(hoch[2] - tief[2])) + 1.0]
        szene.add(pyrender.OrthographicCamera(xmag=halb, ymag=halb, znear=0.05, zfar=1000.0), pose=lage)
        szene.add(pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=cls.LICHT), pose=lage)
        renderer = pyrender.OffscreenRenderer(kante, kante)
        try:
            farbe, tiefe = renderer.render(szene)
        finally:
            renderer.delete()
        rgba = np.dstack([farbe[:, :, :3], np.where(tiefe > 0, 255, 0).astype(np.uint8)])
        Image.fromarray(rgba, 'RGBA').save(str(ziel))
        return ziel
