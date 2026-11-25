# -*- coding: utf-8 -*-
"""Meshicon — die Tabellenvorschau des ERGEBNISNETZES rendern (27.09.2026).

Edgar: „in der Spalte Mesh ein Screenshot des Ergebnis Mesh". Bis dahin zeigte die
Spalte das freigestellte Vorderfoto (`mesh_export._icon`) — bei jedem Formmodell
dasselbe Bild, also kein Hinweis darauf, was der Lauf wirklich gebaut hat
(`mesh-laeufe.md`: „Das Tabellen-Icon taugt NICHT als Beleg für die Netzqualität").

Gerendert wird hier, im python14-Arbeitsprozess (`manage.py mesh_fahren`), nicht im
Runner: `python10_mesh` hat kein pyrender, python14 schon (dieselbe Bibliothek nutzt
„Mesh to 3D" über `Meshfiguransichten`). Der Arbeitsprozess ist abgelöst — der
GL-Kontext entsteht also nicht im Django-Server.

Ansicht wie im Betrachter: von vorn (+Z, die Seite, die beide Formmodelle aus dem Foto
bauen), orthografisch (ein Icon braucht keine Perspektive) und überwiegend ambient
beleuchtet, damit Dellen und Flecken sichtbar bleiben statt im Schlagschatten zu
verschwinden. Ein schwaches Licht aus der Kamera gibt gerade genug Plastik, um die Form
zu erkennen.

Scheitert das Rendern, gibt es kein Icon — die Tabelle zeigt dann ihren Platzhalter.
Ein fehlendes Vorschaubild darf einen fertigen Lauf nie nachträglich rot machen.
"""

import logging
import os

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from KoerperKI_alle.trimeshnormalen import Trimeshnormalen

__all__ = ['Meshicon']

logger = logging.getLogger('core')


class Meshicon:
    KANTE = 256
    DATEI = 'icon.png'
    VORLAGE = 'vorlage.png'
    #: Rand um die Figur, als Anteil ihrer größeren Ausdehnung.
    RAND = 1.06
    HINTERGRUND = (0.094, 0.094, 0.125, 1.0)
    UMGEBUNG = (0.82, 0.82, 0.82)
    LICHT = 1.4

    @classmethod
    def schreiben(cls, glb_pfad, ziel_ordner, datei=DATEI, matrix=None):
        """Rendert `glb_pfad` nach `<ziel_ordner>/<datei>`; gibt den Dateinamen oder ''.

        `matrix` (4×4): das Netz vorher so legen — „Mesh to 3D" gibt die Lage aus der Erkennung
        mit (`arbeit/scan_lage.npz`), dort ist +Z sicher vorn, auch bei einem Netz aus Blender."""
        try:
            return cls._rendern(str(glb_pfad), str(ziel_ordner), datei, matrix)
        except Exception as fehler:  # noqa: BLE001 -- siehe Modulkopf: nie den Lauf scheitern lassen
            logger.warning('Mesh-Icon konnte nicht gerendert werden (%s): %s', glb_pfad, fehler)
            return ''

    @classmethod
    def aus_scan(cls, netz_pfad, ziel_ordner, datei=DATEI, matrix=None):
        """Wie `schreiben`, gerendert auf der Karte aus dem hergerichteten Netz (`Meshfigurscan`, im selben Prozess aus dem Speicher) statt mit pyrender."""
        try:
            from KoerperKI_alle.perspektivbild import Perspektivbild
            from PIL import Image

            from ..daten.meshto3dpfad import Meshto3dpfad

            with Meshto3dpfad():
                from meshfigur_scan import Meshfigurscan
                scan = Meshfigurscan.laden(netz_pfad)
            if matrix is not None:
                scan.anwenden(matrix)
            tief, hoch = scan.punkte.amin(0), scan.punkte.amax(0)
            mitte, spanne = (tief + hoch) / 2.0, float((hoch - tief).max())
            lage = torch.eye(4, dtype=torch.float64, device=scan.punkte.device)
            lage[:3, 3] = torch.stack([mitte[0], mitte[1], hoch[2] + spanne])
            bild = Perspektivbild(scan.punkte, scan.punktnormalen(), scan.flaechen, scan.uv_ecken, scan.textur, scan.punktfarben)
            farbe, _tiefe = bild.rendern(lage, None, cls.KANTE, cls.KANTE, cls.HINTERGRUND, cls.UMGEBUNG, cls.LICHT, halb=spanne * cls.RAND / 2.0)
            Image.fromarray(Torchfeld.roh(farbe)).save(os.path.join(str(ziel_ordner), datei))
            return datei
        except Exception as fehler:  # noqa: BLE001 -- siehe Modulkopf: nie den Lauf scheitern lassen
            logger.warning('Mesh-Icon konnte nicht gerendert werden (%s): %s', netz_pfad, fehler)
            return ''

    @classmethod
    def vorlage_schreiben(cls, foto_pfad, ziel_ordner):
        """Verkleinert das erste Vorlagenfoto nach `<ziel_ordner>/vorlage.png` (Dateiname oder '').

        Die Tabelle darf nicht die Originalfotos einbinden: Die Damira-Bilder sind mehrere MB
        groß, bei 16 Zeilen wären das zweistellige Megabyte nur für Daumennagel-Spalten.
        """
        try:
            from PIL import Image

            bild = Image.open(str(foto_pfad))
            bild.draft('RGB', (cls.KANTE * 2, cls.KANTE * 2))  # JPEG schon beim Dekodieren kleiner
            bild = bild.convert('RGB')
            bild.thumbnail((cls.KANTE, cls.KANTE), Image.LANCZOS)
            pfad = os.path.join(str(ziel_ordner), cls.VORLAGE)
            bild.save(pfad)
            return cls.VORLAGE
        except Exception as fehler:  # noqa: BLE001 -- siehe Modulkopf
            logger.warning('Mesh-Vorlagenbild fehlgeschlagen (%s): %s', foto_pfad, fehler)
            return ''

    @classmethod
    def _rendern(cls, glb_pfad, ziel_ordner, datei=DATEI, matrix=None):
        # Späte Importe: pyrender legt beim Import schon OpenGL-Bindungen an, und dieser
        # Dienst wird auch von Modulen importiert, die nur die Pfade brauchen.
        import pyrender
        import trimesh
        from PIL import Image

        geladen = trimesh.load(glb_pfad, process=False)
        szene_tm = geladen if isinstance(geladen, trimesh.Scene) else trimesh.Scene(geladen)
        if matrix is not None:
            szene_tm.apply_transform(Torchfeld.feld(matrix, dtype=torch.float64))
        tief, hoch = szene_tm.bounds
        mitte = (tief + hoch) / 2.0
        spanne = float(Torchfeld.amax(hoch - tief))
        if not Torchfeld.isfinite(spanne) or spanne <= 0:
            raise ValueError('Netz ohne Ausdehnung')

        Trimeshnormalen.setzen(szene_tm)
        szene = pyrender.Scene.from_trimesh_scene(
            szene_tm, bg_color=cls.HINTERGRUND, ambient_light=cls.UMGEBUNG)
        # Orthografisch von vorn: beide Formmodelle legen die im Foto sichtbare Seite
        # nach +Z (dieselbe Konvention wie `mesh_fototextur.ACHSEN`).
        halb = spanne * cls.RAND / 2.0
        kamera = pyrender.OrthographicCamera(xmag=halb, ymag=halb)
        lage = torch.eye(4, dtype=torch.float64, device='cuda')
        lage[:3, 3] = Torchfeld.feld([mitte[0], mitte[1], hoch[2] + spanne])
        szene.add(kamera, pose=lage)
        szene.add(pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=cls.LICHT), pose=lage)

        renderer = pyrender.OffscreenRenderer(cls.KANTE, cls.KANTE)
        try:
            farbe, _tiefe = renderer.render(szene)
        finally:
            renderer.delete()
        pfad = os.path.join(ziel_ordner, datei)
        Image.fromarray(farbe).save(pfad)
        return datei
