# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtslage — Netz und Landmarken des Reiters „Gesicht" in die Lage des MODELLS bringen (07.10.2026).

Edgar: „beim Gesicht sind noch Abweichungen, siehe die Überlagerung blau / rot, kriegst du das noch besser hin?" Gemessen an `Edgar 10 - Hunyan Kopf` (`…17.45.25`): zwei Fehler des
VERGLEICHS, nicht der Figur.

1. **Haltung.** Das Modell des Reiters steht in der Ruhehaltung (`G9formung(stellung)`), das Netz und seine Landmarken stehen in der Haltung der Person — die Anpassung dreht Hals und Kopf
   mit. Am Kopf ist die Abbildung Ruhe → Haltung starr: Kabsch (ohne Maßstab) über die Käfigpunkte im Umkreis von 10 cm um die Landmarken, Ruhe-Käfig gegen `arbeit/posiert.npy` (gleiche
   Punktreihenfolge). Am Edgar-Kopf: 10,0° Drehung, 248 mm Verschiebung, Rest RMS 0,10 mm über 3.210 Punkte (bei 14 cm Radius 0,52 mm, bei 18 cm 2,17 mm — dort hängen Schultern dran, die
   sich anders bewegen). Netz und Landmarken werden mit der Umkehrung in die Ruhelage zurückgedreht; das Modell bleibt, wie es die 3D-Ansicht zeigt.
2. **Welches Netz.** „Mesh" war immer das Körpernetz (`netz/mesh.glb`). Hat der Schritt „Körper" ein Kopfnetz benutzt (`ergebnis.erkennung.kopf.abgleich`), ist das Ziel des Gesichts das
   Kopfnetz (`kopf/mesh.glb`, über `kopf_lage.matrix_roh` in den Rohrahmen des Körpers, dann wie das Körpernetz über `scan_lage`).

Gemessen (25.900 Kopfnetzpunkte im Gesicht, Abstand zur Modelloberfläche): Ruhehaltung Median 6,01 mm (p90 12,39), Haltung (`posiert.npy`) Median 0,37 mm (p90 0,98, p99 1,74); gegen das
Körpernetz 5,92 → 2,13 mm (952 Punkte). Die großen Abweichungen im Reiter waren also zum größten Teil die 10° Kopfhaltung.

Ohne `arbeit/posiert.npy` (Lauf vor der Vorschau) oder bei abweichender Punktzahl bleibt es bei der alten Lage; `haltung` nennt den Grund.
"""

import numpy as np
import trimesh

__all__ = ['Engine2d3dKleiderGesichtslage']


class Engine2d3dKleiderGesichtslage:
    #: Käfigpunkte im Umkreis der Landmarkenmitte, aus denen die Kopfhaltung gerechnet wird (Meter).
    RADIUS = 0.10
    MINDESTPUNKTE = 200

    @classmethod
    def berechnen(cls, job, ablage, stellung=None):
        """`{gesicht, ruhe, modell_gesicht, netz_pfad, netz_ordner, netz_name, netz_art, netz_matrix, haltung}` — `gesicht` (478, 3) und `netz_matrix` (4×4, Rohnetz → Ruhelage des Modells) bereits
        zurückgedreht. `netz_pfad` ist None, wenn Netz oder `scan_lage.npz` fehlen. ValueError, wenn die Landmarken fehlen. `stellung`: statt `job.stellung()` diese Reglerstellung für das Modell
        (der Schritt „rest" rechnet auf der Stellung OHNE den Rest-Morph, den er gerade erst bauen will)."""
        landmarken_pfad = ablage.arbeit('landmarken.npz')
        if not landmarken_pfad.is_file():
            raise ValueError('Keine landmarken.npz — die Gesichtserkennung ist für diesen Auftrag noch nicht gelaufen.')
        with np.load(landmarken_pfad) as d:
            gesicht = np.asarray(d['gesicht'], dtype=float)
        pfad, ordner, art, roh = cls._netz(job, ablage)
        lage_pfad = ablage.arbeit('scan_lage.npz')
        if pfad is None or not lage_pfad.is_file():
            pfad, scan = None, np.eye(4)
        else:
            with np.load(lage_pfad) as d:
                scan = np.asarray(d['matrix'], dtype=float)
        ruhe = cls._ruhe(stellung if stellung is not None else job.stellung())
        zurueck, haltung = cls._haltung(ablage, gesicht, ruhe)
        return {
            'gesicht': cls._anwenden(gesicht, zurueck),
            'ruhe': ruhe,
            'modell_gesicht': cls._modell_gesicht(ablage, ruhe),
            'netz_pfad': pfad, 'netz_ordner': ordner, 'netz_name': 'mesh.glb', 'netz_art': art,
            'netz_matrix': zurueck @ scan @ roh,
            'haltung': haltung,
        }

    #: Landmarkengruppen (MediaPipe-Indizes) für die Abweichung Netz ↔ Modell.
    GRUPPEN = {
        'Lippen': [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 185, 40, 39, 37, 0, 267, 269, 270, 409, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 191, 80, 81, 82, 13, 312, 311, 310, 415],
        'Nase': [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 129, 358, 49, 279, 48, 278, 64, 294, 219, 439, 102, 331, 115, 344, 220, 440],
        'Augen': [263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398, 33, 7, 163, 144, 145, 153, 154, 155, 133, 246, 161, 160, 159, 158, 157, 173],
        'Brauen': [276, 283, 282, 295, 285, 300, 293, 334, 296, 336, 46, 53, 52, 65, 55, 70, 63, 105, 66, 107],
        'Gesichtsoval': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
    }

    @classmethod
    def abweichung(cls, lage):
        """`{'alle': {median_mm, p90_mm}, 'gruppen': {name: {median_mm, p90_mm}}}` — Abstand Netz-Landmarke ↔ Modell-Landmarke (je 478), oder None ohne Modell-Landmarken."""
        if lage['modell_gesicht'] is None:
            return None
        fehler = np.linalg.norm(lage['modell_gesicht'] - lage['gesicht'], axis=1) * 1000.0
        gueltig = np.isfinite(fehler)

        def zahlen(indizes):
            e = fehler[[i for i in indizes if gueltig[i]]]
            return {'median_mm': round(float(np.median(e)), 2), 'p90_mm': round(float(np.percentile(e, 90)), 2)} if len(e) else None

        return {'alle': zahlen(range(len(fehler))), 'gruppen': {name: zahlen(ix) for name, ix in cls.GRUPPEN.items()}}

    @staticmethod
    def _ruhe(stellung):
        """Der Käfig der Figur in der Ruhehaltung (25.182 Punkte, wie `Meshfigurvorschau`) — mit den Eigenmorphen der `stellung` (`job.stellung()` trägt sie)."""
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        return np.asarray(G9reglerableitung.lage(G9formung(stellung))[0], dtype=float)

    @staticmethod
    def _modell_gesicht(ablage, ruhe):
        """(478, 3) die EIGENEN Gesichtspunkte der Figur in der Ruhehaltung: Dreieck + Anteile je Landmarke aus `genesis_ende.npz` (`lm_flaeche_*`, vom Detektor kalibriert, `G9netzlandmarken`) —
        das Modell hat also doch eine Landmarken-Topologie; die Abweichung zum Netz ist Landmarke gegen Landmarke, nicht gegen die nächste Fläche. None ohne `genesis_ende.npz`; NaN, wo die Tabelle keinen Punkt kennt."""
        pfad = ablage.arbeit('genesis_ende.npz')
        if not pfad.is_file():
            return None
        with np.load(pfad) as d:
            if len(d['punkte']) != len(ruhe):
                return None
            quelle, nummer, dreieck = d['lm_flaeche_quelle'], d['lm_flaeche_nummer'], d['lm_flaeche_dreieck']
            bary, tri = d['lm_flaeche_bary'].astype(float), d['dreiecke']
        aus = np.full((478, 3), np.nan)
        for i in np.flatnonzero(quelle == 1):
            aus[nummer[i]] = bary[i] @ ruhe[tri[dreieck[i]]]
        return aus

    #: So weit darf eine Netz-Landmarke neben der Netzfläche liegen und wird auf deren nächsten Punkt gelegt (wie `Meshfigurlandmarkenflaeche` in der Anpassung, dort bis 30 mm).
    FLAECHE_MAX = 0.008

    @classmethod
    def auf_flaeche(cls, lage):
        """Die Netz-Landmarken (`lage['gesicht']`), wo sie bis `FLAECHE_MAX` neben der Netzfläche liegen, auf deren nächsten Punkt gelegt; der Rest bleibt, wie er ist. Die Landmarken schweben im Mittel
        1,3 (Lippen) bis 2,5 mm (Augen) über der Fläche — gemessen an `Edgar 10`; gegen sie zu messen oder zu morphen höbe die Figur von der Fläche ab. Ohne Netz: unverändert."""
        if lage['netz_pfad'] is None:
            return np.array(lage['gesicht'], dtype=float, copy=True)
        geladen = trimesh.load(str(lage['netz_pfad']), force='mesh')
        matrix = lage['netz_matrix']
        netz = trimesh.Trimesh(np.asarray(geladen.vertices, dtype=float) @ matrix[:3, :3].T + matrix[:3, 3], geladen.faces, process=False)
        aus = np.array(lage['gesicht'], dtype=float, copy=True)
        gueltig = np.flatnonzero(np.isfinite(aus).all(axis=1))
        nah, abstand, _ = netz.nearest.on_surface(aus[gueltig])
        nah_genug = abstand <= cls.FLAECHE_MAX
        aus[gueltig[nah_genug]] = nah[nah_genug]
        return aus

    @classmethod
    def netzart(cls, job, ablage):
        """„Kopfnetz" oder „Körpernetz" — welches Netz der Reiter als „Mesh" zeigt (ohne die Haltung zu rechnen)."""
        return cls._netz(job, ablage)[2]

    @staticmethod
    def _netz(job, ablage):
        """`(Pfad, Ordner, Art, Matrix Netz → Rohrahmen des Körpers)` — das Kopfnetz, wenn der Körper es benutzt hat, sonst das Körpernetz."""
        kopf = ((job.ergebnis or {}).get('erkennung') or {}).get('kopf') or {}
        kopfdatei, lage = ablage.kopf('mesh.glb'), ablage.arbeit('kopf_lage.npz')
        if kopf.get('abgleich') and kopfdatei.is_file() and lage.is_file():
            with np.load(lage) as d:
                return kopfdatei, ablage.KOPF, 'Kopfnetz', np.asarray(d['matrix_roh'], dtype=float)
        netz = ablage.netz('mesh.glb')
        return (netz if netz.is_file() else None), ablage.NETZ, 'Körpernetz', np.eye(4)

    @classmethod
    def _haltung(cls, ablage, gesicht, ruhe):
        """`(4×4 Haltung → Ruhe, Befund)`. Ohne Fehlerfall die Einheitsmatrix und `{'aus': Grund}`."""
        pfad = ablage.arbeit('posiert.npy')
        if not pfad.is_file():
            return np.eye(4), {'aus': 'arbeit/posiert.npy fehlt'}
        posiert = np.load(pfad).astype(float)
        if ruhe.shape != posiert.shape:
            return np.eye(4), {'aus': 'posiert.npy hat %d Punkte, der Käfig %d' % (len(posiert), len(ruhe))}
        # `np.mean` propagiert ein einzelnes NaN (eine nicht erkannte Landmarke) auf den gesamten Mittelpunkt — dann
        # findet die Kaefigpunkt-Suche darunter ueberall „zu weit weg“ und die Haltungskorrektur faellt ganz aus
        # (Befund 08.10.2026, Edgar 9 TRELLIS-Kopf: Landmarke 332 NaN, 0 Kaefigpunkte, Abweichung dadurch auf 37 mm
        # Median statt der ueblichen < 1 mm — kein Form-Fehler, nur Ruhehaltung gegen Pose verglichen).
        gueltig = np.isfinite(gesicht).all(axis=1)
        if not gueltig.any():
            return np.eye(4), {'aus': 'keine gültige Landmarke für den Kopf-Mittelpunkt'}
        kopf = np.linalg.norm(posiert - gesicht[gueltig].mean(axis=0), axis=1) < cls.RADIUS
        if kopf.sum() < cls.MINDESTPUNKTE:
            return np.eye(4), {'aus': 'nur %d Käfigpunkte am Kopf' % int(kopf.sum())}
        drehung, versatz = cls._kabsch(ruhe[kopf], posiert[kopf])
        rest = np.linalg.norm(ruhe[kopf] @ drehung.T + versatz - posiert[kopf], axis=1)
        vor = np.eye(4)
        vor[:3, :3], vor[:3, 3] = drehung, versatz
        winkel = np.degrees(np.arccos(np.clip((np.trace(drehung) - 1.0) / 2.0, -1.0, 1.0)))
        befund = {
            'punkte': int(kopf.sum()), 'drehung_grad': round(float(winkel), 1), 'verschiebung_mm': round(float(np.linalg.norm(versatz)) * 1000, 1),
            'rest_rms_mm': round(float(np.sqrt((rest ** 2).mean())) * 1000, 2),
        }
        return np.linalg.inv(vor), befund

    @staticmethod
    def _kabsch(a, b):
        """Starre Abbildung `a → b`: `(Drehung, Versatz)` mit `b ≈ a @ Drehung.T + Versatz`."""
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        vorzeichen = np.sign(np.linalg.det(vt.T @ u.T))
        drehung = vt.T @ np.diag([1.0, 1.0, vorzeichen]) @ u.T
        return drehung, mb - drehung @ ma

    @staticmethod
    def _anwenden(punkte, matrix):
        return np.asarray(punkte, dtype=float) @ matrix[:3, :3].T + matrix[:3, 3]
