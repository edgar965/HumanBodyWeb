# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtsvergleich — Mesh-gegen-Modell-Linien UND -Schnitte fuer den Reiter „Gesicht" (07.10.2026).

Edgar: „ich sehe keine verbesserung ... mach mir einen zweiten Tab bei der Modell View ... zeichne
alle Linien ein die du gemessen hast, mit Bezeichnung von 1 bis x, und eine Tabelle Nummer, Mesh (cm),
Modell (cm)". Spaeter: „ich sagte, mach schnitte alle paar cm horizontal, vertikal und diagonal, mach
die alle und zeige sie auf dem Tab".

Zwei Vergleiche, beide auf denselben zwei Flaechen (Mesh = ausgerichtetes TRELLIS-Netz, Modell =
aktuelle Genesis-9-Oberflaeche):

1. `LINIEN` — zwoelf benannte Gesichtsstrecken (MediaPipe-Face-Mesh-Indexpaare aus den 478 Landmarken in
   `landmarken.npz`): Mesh-Punkt = der Landmark direkt (echter Punkt auf der TRELLIS-Oberflaeche), Modell-
   Punkt = naechster Punkt auf der AKTUELLEN Genesis-9-Oberflaeche zu GENAU DIESEM Landmark
   (`trimesh.nearest.on_surface`, dieselbe Methode wie `direktpruefung_landmarken.py` und
   `mund_messen_exakt.py`, Sitzung 07.10.2026) — das Modell hat keine MediaPipe-Topologie, die naechste
   Flaeche ist der einzige ehrliche Vergleichspunkt. Beide Strecken sind echte Punkt-zu-Punkt-Distanzen,
   „Mesh (cm)" und „Modell (cm)" also direkt vergleichbar.

2. `_schnitte()` — Ebenen-Schnitte (horizontal/vertikal/diagonal, alle `SCHRITT` Meter) durch BEIDE
   Flaechen (`trimesh.intersections.mesh_plane`), auf eine Kopf-Box beschraenkt (aus den Landmarken plus
   Rand). Zeigt die Kontur-Abweichung flaechendeckend, nicht nur an den zwoelf benannten Punkten.
"""
import json
import os

import numpy as np
import trimesh

from Genesis9.basisnetz import G9basisnetz
from Genesis9.formung import G9formung

from .engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage

__all__ = ['Engine2d3dKleiderGesichtsvergleich']


class Engine2d3dKleiderGesichtsvergleich:
    #: (Nummer, Bezeichnung, MediaPipe-Face-Mesh-Index A, Index B) — Indizes der 478 Landmarken aus `landmarken.npz`.
    LINIEN = [
        (1, 'Augenabstand innen', 133, 362),
        (2, 'Augenabstand außen', 33, 263),
        (3, 'Augenbreite links', 33, 133),
        (4, 'Augenbreite rechts', 362, 263),
        (5, 'Nasenbreite', 129, 358),
        (6, 'Nasenlänge', 168, 4),
        (7, 'Mundbreite', 61, 291),
        (8, 'Mundöffnung', 13, 14),
        (9, 'Gesichtsbreite (Jochbein)', 234, 454),
        (10, 'Gesichtsbreite (Schläfen)', 127, 356),
        (11, 'Kieferbreite', 58, 288),
        (12, 'Gesichtshöhe', 10, 152),
        # Mund, Nase, Augen genauer (Edgar, 07.10.2026: „mundproportionen und nasenproportionen stimmen nicht", „augenform auch nicht")
        (13, 'Oberlippe (außen–innen)', 0, 13),
        (14, 'Unterlippe (innen–außen)', 14, 17),
        (15, 'Nase–Oberlippe', 2, 0),
        (16, 'Nasenflügel innen', 98, 327),
        (17, 'Augenöffnung rechts', 159, 145),
        (18, 'Augenöffnung links', 386, 374),
        (19, 'Kinn–Unterlippe', 152, 17),
        (20, 'Brauenabstand innen', 55, 285),
    ]

    #: Abstand der Schnitt-Ebenen — „alle paar cm" (Edgar, 07.10.2026).
    SCHRITT = 0.025
    #: Rand um die Kopf-Box, in dem ein Schnitt-Segment noch gilt (filtert Arme/Schultern/Rauschen weg).
    RAND = 0.03

    @classmethod
    def berechnen(cls, job, ablage):
        """{linien, schnitte, mesh_datei, modell_datei} — oder ValueError-Text, wenn etwas fehlt."""
        if not job.stellung():
            raise ValueError('Noch keine Stellung — erst nach dem Schritt „Körper“.')
        # Landmarken und Netz in der Ruhelage des Modells (Kopfhaltung zurückgedreht, Kopfnetz statt Körpernetz, wenn der Körper es benutzt hat) — `Engine2d3dKleiderGesichtslage`.
        lage = Engine2d3dKleiderGesichtslage.berechnen(job, ablage)
        # Die Netz-Landmarken auf die Netzfläche gelegt (wie die Anpassung es tut): sie schweben 1,3–2,5 mm darüber, und die Abweichung zum Modell zeigte sonst vor allem das.
        lage['gesicht'] = gesicht = Engine2d3dKleiderGesichtslage.auf_flaeche(lage)  # (478, 3) Meter, Ruhelage des Modells

        modell_figur = cls._modell_figur(job)
        gebraucht = sorted({i for _, _, a, b in cls.LINIEN for i in (a, b)})
        if lage['modell_gesicht'] is not None:
            # Die EIGENEN Landmarken der Figur (Dreieck + Anteile aus `genesis_ende.npz`) — Landmarke gegen Landmarke. Der nächste Flächenpunkt (unten) lag beim Mund und an den Lidern auf einer
            # anderen Stelle desselben Merkmals und täuschte Unterschiede vor oder verdeckte sie (07.10.2026).
            modell_punkte = lage['modell_gesicht']
            modell_quelle = 'eigene Landmarken der Figur'
        else:
            nah, _, _ = modell_figur.nearest.on_surface(gesicht[gebraucht])
            modell_punkte = np.zeros_like(gesicht)
            modell_punkte[gebraucht] = nah
            modell_quelle = 'nächster Flächenpunkt'

        linien = []
        for nr, name, a, b in cls.LINIEN:
            mesh_a, mesh_b = gesicht[a], gesicht[b]
            mod_a, mod_b = modell_punkte[a], modell_punkte[b]
            linien.append({
                'nummer': nr,
                'bezeichnung': name,
                'mesh_a': mesh_a.tolist(), 'mesh_b': mesh_b.tolist(),
                'modell_a': mod_a.tolist(), 'modell_b': mod_b.tolist(),
                'mesh_cm': round(float(np.linalg.norm(mesh_a - mesh_b) * 100), 2),
                'modell_cm': round(float(np.linalg.norm(mod_a - mod_b) * 100), 2),
            })

        mesh_figur = cls._mesh_figur(lage)
        schnitte = cls._schnitte(mesh_figur, modell_figur, gesicht) if mesh_figur is not None else []

        return {
            'linien': linien,
            'schnitte': schnitte,
            'mesh_datei': cls._mesh_adresse(job, lage),
            'modell_datei': cls._modell_adresse(job, ablage),
            'haltung': lage['haltung'],
            'modell_quelle': modell_quelle,
            'abweichung': Engine2d3dKleiderGesichtslage.abweichung(lage),
        }

    @staticmethod
    def _modell_figur(job):
        """Die AKTUELLE Genesis-9-Oberflaeche als Dreiecksnetz (Vierecke des Basisnetzes gesplittet)."""
        formung = G9formung.aus_abfrage(job.stellung())
        p = formung.punkte().copy()
        p[:, 1] -= formung.boden()
        quads = G9basisnetz.holen().vierecke
        tris = np.concatenate([quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]])
        return trimesh.Trimesh(vertices=p, faces=tris, process=False)

    @staticmethod
    def _mesh_figur(lage):
        """Das Netz (Kopfnetz oder Körpernetz, `Engine2d3dKleiderGesichtslage`) in der Ruhelage des Modells: `scan_lage.npz` (wie `direktmorph_rechnen.py`), danach die Kopfhaltung zurückgedreht.
        None, wenn Netz oder Lage-Datei fehlen (dann gibt's nur die Linien, keine Schnitte)."""
        if lage['netz_pfad'] is None:
            return None
        mesh = trimesh.load(str(lage['netz_pfad']), force='mesh')
        matrix = lage['netz_matrix']
        v = np.asarray(mesh.vertices, dtype=float)
        v = (matrix[:3, :3] @ v.T).T + matrix[:3, 3]
        return trimesh.Trimesh(vertices=v, faces=mesh.faces, process=False)

    # --------------------------------------------------------------------------------------------- Schnitte

    @classmethod
    def _schnitte(cls, mesh_figur, modell_figur, gesicht):
        """[{kategorie, nummer, mesh: [[[x,y,z],[x,y,z]], …], modell: [...]}, …] — je Ebene die Schnitt-Segmente
        BEIDER Flaechen, auf die Kopf-Box beschraenkt."""
        kasten = cls._kopfkasten(mesh_figur, gesicht)
        ebenen = []
        ebenen += cls._ebenen('horizontal', np.array([0.0, 1.0, 0.0]), kasten)
        ebenen += cls._ebenen('vertikal', np.array([1.0, 0.0, 0.0]), kasten)
        diagonal = np.array([1.0, 1.0, 0.0])
        diagonal /= np.linalg.norm(diagonal)
        ebenen += cls._ebenen('diagonal', diagonal, kasten)
        ergebnis = []
        for kategorie, nummer, normal, ursprung in ebenen:
            mesh_segmente = cls._segmente(mesh_figur, normal, ursprung, kasten)
            modell_segmente = cls._segmente(modell_figur, normal, ursprung, kasten)
            if not mesh_segmente and not modell_segmente:
                continue
            ergebnis.append({'kategorie': kategorie, 'nummer': nummer, 'mesh': mesh_segmente, 'modell': modell_segmente})
        return ergebnis

    @classmethod
    def _kopfkasten(cls, mesh_figur, gesicht):
        """Kopf-Box aus den Landmarken (Hoehe) + den Mesh-Punkten IN dieser Hoehe (Breite/Tiefe) — Rand
        grosszuegig, damit Ohren/Haaransatz/Hinterkopf noch mitkommen (die Landmarken sind nur das Gesicht).

        NUR aus den Landmarken + festen Raendern — NICHT aus den Mesh-Punkten im Hoehenband (Befund
        07.10.2026, `Engine2d3dKleiderGesichtsbilder`: bei schraegem Hals/hochgezogenen Schultern reichte
        das Hoehenband bis in die Schultern, die Box wurde doppelt so breit wie der Kopf — die
        Schnittprofile zeigten dann die Schulterbreite statt der Kopfbreite).

        `nanmin`/`nanmax` statt `min`/`max`: eine einzelne nicht erkannte Landmarke (NaN) kippt sonst den
        ganzen Kasten auf NaN und `_segmente` findet nirgends mehr „innen“ (Befund 08.10.2026, Edgar 9
        TRELLIS-Kopf: Landmarke 332 NaN, 0 Schnitte trotz vorhandenem Netz)."""
        x_min, x_max = float(np.nanmin(gesicht[:, 0])) - 0.08, float(np.nanmax(gesicht[:, 0])) + 0.08
        y_min, y_max = float(np.nanmin(gesicht[:, 1])) - 0.05, float(np.nanmax(gesicht[:, 1])) + 0.13
        z_min, z_max = float(np.nanmin(gesicht[:, 2])) - 0.10, float(np.nanmax(gesicht[:, 2])) + 0.03
        return {'x': (x_min, x_max), 'y': (y_min, y_max), 'z': (z_min, z_max)}

    @classmethod
    def _ebenen(cls, kategorie, normal, kasten):
        """Ebenen mit `normal`, von einem Rand der Kopf-Box zum anderen (entlang `normal`) in `SCHRITT`-
        Abstaenden — `ursprung` liegt sonst im Kopf-Mittelpunkt (die Box-Mitte in den anderen zwei Achsen)."""
        mitte = np.array([sum(kasten['x']) / 2, sum(kasten['y']) / 2, sum(kasten['z']) / 2])
        ecken = np.array([[x, y, z] for x in kasten['x'] for y in kasten['y'] for z in kasten['z']])
        t_werte = ecken @ normal
        t_mitte = float(mitte @ normal)
        ebenen, t, nummer = [], float(t_werte.min()), 1
        while t <= float(t_werte.max()) + 1e-9:
            ursprung = mitte + (t - t_mitte) * normal
            ebenen.append((kategorie, nummer, normal, ursprung))
            t += cls.SCHRITT
            nummer += 1
        return ebenen

    @classmethod
    def _segmente(cls, figur, normal, ursprung, kasten):
        """Schnitt-Segmente von `figur` mit der Ebene (`normal`, `ursprung`), auf die Kopf-Box (+ `RAND`) beschraenkt —
        sonst naehme ein horizontaler Schnitt auch Arme/Schultern mit, ein vertikaler den ganzen Rumpf."""
        try:
            segmente = trimesh.intersections.mesh_plane(figur, normal, ursprung)
        except Exception:
            return []
        if len(segmente) == 0:
            return []
        mitte = segmente.mean(axis=1)
        r = cls.RAND
        innen = (
            (mitte[:, 0] >= kasten['x'][0] - r) & (mitte[:, 0] <= kasten['x'][1] + r)
            & (mitte[:, 1] >= kasten['y'][0] - r) & (mitte[:, 1] <= kasten['y'][1] + r)
            & (mitte[:, 2] >= kasten['z'][0] - r) & (mitte[:, 2] <= kasten['z'][1] + r)
        )
        return segmente[innen].tolist()

    # ----------------------------------------------------------------------------------------- Datei-Adressen

    @staticmethod
    def _mesh_adresse(job, lage):
        """Das Netz des Reiters (Kopfnetz `kopf/mesh.glb` oder Körpernetz `netz/mesh.glb`) — Version = Datei-Mtime (kein eigener Fassungsname, nur Browser-Cache).

        Die GLB liegt im ROHEN Raum des Netzes, die Landmarken (und damit Linien UND Schnitte) in der Ruhelage des Modells. Ohne `ausrichtung` (4×4, zeilenweise:
        `scan_lage.npz`, beim Kopfnetz davor `kopf_lage.matrix_roh`, danach die Kopfhaltung zurückgedreht) stünde das Netz abseits — der Browser wendet sie an."""
        if lage['netz_pfad'] is None:
            return None
        v = os.stat(str(lage['netz_pfad'])).st_mtime_ns
        return {
            'url': '/api/engine2d3dkleider/%s/datei/%s/%s?v=%s' % (job.id, lage['netz_ordner'], lage['netz_name'], v),
            'ordner': lage['netz_ordner'], 'name': lage['netz_name'], 'ausrichtung': lage['netz_matrix'].tolist(), 'art': lage['netz_art'],
        }

    @staticmethod
    def _modell_adresse(job, ablage):
        """Der aktuelle Stand (`ergebnis/stand_<fassung>.glb`), aus `stand.json` — dieselbe Quelle wie die Hauptbühne."""
        pfad = ablage.ergebnis('stand.json')
        if not pfad.is_file():
            return None
        bericht = json.loads(pfad.read_text(encoding='utf-8'))
        name = bericht.get('datei')
        if not name or not ablage.ergebnis(name).is_file():
            return None
        return {
            'url': '/api/engine2d3dkleider/%s/datei/ergebnis/%s?v=%s' % (job.id, name, bericht.get('fassung') or ''),
            'ordner': 'ergebnis', 'name': name,
        }
