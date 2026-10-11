# -*- coding: utf-8 -*-
"""Dazgeograftverfeinerung — das angepasste Daz-Netz beidseitig an die Original-Scham heranziehen (10.10.2026).

Edgar: „die unterscheidet sich auch noch sehr vom Blender-Modell". Gemessen nach dem ersten Schritt (`Dazgeograftanpassung.anpassen`, Strahlen längs der Haut): das Daz-Netz liegt zu 97 %
auf dem Original (Median 0,3 mm), aber umgekehrt liegt die Hälfte der Original-Punkte mehr als 1,7 mm vom Daz-Netz weg, ein Prozent bis 17 mm — die tiefen inneren Teile (innere
Lippen, Spalt) erreicht ein Strahl von vorn nicht. Hier ziehen deshalb auch die Punkte des Originals: je Durchgang

    vorwärts    jeder Punkt des Netzes → nächster Probenpunkt auf dem Original (in `reichweite`, Normalen höchstens `NORMALE_GRAD` auseinander)
    rückwärts   jeder Probenpunkt des Originals → nächster Punkt des Netzes (in `reichweite`, Normalen ebenso); die Mitte seiner Proben ist dessen Ziel, Gewicht nach Anzahl
gelöst wird wie dort `(W + a·L) D = W (Ziel − Anfang)` für die ganze Verschiebung; Steifigkeit `a` und Reichweite sinken von Durchgang zu Durchgang, der Ring bleibt fest.
Der erste Versuch (a bis 0,2, keine Normalenprüfung) knitterte das Netz: 558 von 8.320 Dreiecken klappten um. Jetzt prüft jeder Durchgang das Umklappen und halbiert den Schritt,
bis es nicht mehr Dreiecke sind als vorher.
"""
import numpy as np

__all__ = ['Dazgeograftverfeinerung']


class Dazgeograftverfeinerung:
    #: `(Steifigkeit, Reichweite in m)` je Durchgang.
    PLAN = ((3.0, 0.012), (2.0, 0.009), (1.4, 0.007), (1.0, 0.005))
    #: Zahl der Proben auf dem Original, Gewicht der Randpunkte, Gewicht der Rückwärtsziele je Probe (höchstens 3 zählen), größte Normalenabweichung (Grad).
    PROBEN, RAND_GEWICHT, RUECK_GEWICHT, NORMALE_GRAD = 30000, 100.0, 0.5, 60.0
    #: Ein Durchgang wird halbiert, solange er mehr als so viele Dreiecke mehr umklappt als der Stand davor. Gemessen 11.10.2026 am neu gebauten Ziel von „cute girl" (Sockel ≈ 740 umgeklappte
    #: Dreiecke gegen das Verlegte), Form Original → Modell Median / p90 | Lippen seitlich Median | Knick über die Naht Median / p90 | Falten über 90°:
    #:   5 (vorher)  0,89 / 3,08 mm | 3,09 mm | 11,0° / 34,8° | 2,3 %     die Durchgänge 3 und 4 liefen nur noch mit Schritt 1/16 — schon 2 mm Änderung am Ziel kippten das Ergebnis
    #:   20          0,81 / 2,86    | 2,69    | 10,9° / 36,5° | 2,2 %
    #:   50 … 200    0,64 / 2,19    | 1,67    | 11,3° / 38,5° | 2,6 %     alle Durchgänge mit Schritt 1; 50, 100 und 200 sind gleich
    UMKLAPP_TOLERANZ = 100

    @classmethod
    def verfeinern(cls, anfang, q, dreiecke, rand, laplace, ziel_netz, aussen, plan=None, band=None, band_gewicht=0.0, toleranz=None):
        """`(neue Punkte, bericht)`. `anfang`: die Punkte vor jeder Anpassung (Bezug der Verschiebung), `q`: der Stand nach dem ersten Schritt, `rand`: bool je Punkt (Ring),
        `laplace`: der Graph-Laplace des Netzes, `aussen`: `(P, 3)` Richtung nach außen je Punkt (Hautnormale) — legt die Seite der Normalen fest. `toleranz`: wie viele Dreiecke ein Durchgang
        mehr umklappen darf als der Stand davor (Vorgabe `UMKLAPP_TOLERANZ`, gilt für ein Netz von ≈ 8.300 Dreiecken — bei feinerem wächst sie mit der Zahl der Dreiecke)."""
        import scipy.sparse as sp
        import scipy.sparse.linalg as spl
        import trimesh
        from scipy.spatial import cKDTree

        proben, flaeche = trimesh.sample.sample_surface(ziel_netz, cls.PROBEN, seed=7)
        proben_baum = cKDTree(proben)
        n_proben = np.asarray(ziel_netz.face_normals)[flaeche]
        n = len(anfang)
        schwelle = np.cos(np.radians(cls.NORMALE_GRAD))
        n_netz = cls._normalen(q, dreiecke, aussen)
        # Das Original hat keine verbindliche Seite: die, auf der die Normalen mehrheitlich zu denen des Netzes zeigen, ist außen.
        _d, i0 = proben_baum.query(q)
        n_proben = n_proben * (1.0 if np.einsum('ij,ij->i', n_proben[i0], n_netz).mean() >= 0 else -1.0)
        berichte, umgeklappt_vorher = [], cls._umgeklappt(q, dreiecke, anfang)
        toleranz = cls.UMKLAPP_TOLERANZ if toleranz is None else toleranz
        for steifigkeit, reichweite in (plan or cls.PLAN):
            n_netz = cls._normalen(q, dreiecke, aussen)
            d_vor, i_vor = proben_baum.query(q)
            vor = (d_vor < reichweite) & (np.einsum('ij,ij->i', n_proben[i_vor], n_netz) > schwelle)
            netz_baum = cKDTree(q)
            d_rueck, j_rueck = netz_baum.query(proben)
            rueck = (d_rueck < reichweite) & (np.einsum('ij,ij->i', n_proben, n_netz[j_rueck]) > schwelle)
            summe, anzahl = np.zeros((n, 3)), np.zeros(n)
            np.add.at(summe, j_rueck[rueck], proben[rueck])
            np.add.at(anzahl, j_rueck[rueck], 1.0)
            w_vor, w_rueck = vor.astype(np.float64), cls.RUECK_GEWICHT * np.minimum(anzahl, 3.0)
            w = w_vor + w_rueck
            mitte = summe / np.maximum(anzahl, 1.0)[:, None]
            ziel = np.where(w[:, None] > 0, (w_vor[:, None] * proben[i_vor] + w_rueck[:, None] * mitte) / np.maximum(w, 1e-12)[:, None], q)
            w[rand], ziel[rand] = cls.RAND_GEWICHT, anfang[rand]
            if band is not None and band.any() and band_gewicht > 0:         # randnahe Punkte bleiben mit `band_gewicht` bei ihrer verlegten Lage
                alt = w[band].copy()
                w[band] = alt + band_gewicht
                ziel[band] = (alt[:, None] * ziel[band] + band_gewicht * anfang[band]) / w[band][:, None]
            lhs = (sp.diags(w) + steifigkeit * laplace + 1e-9 * sp.identity(n)).tocsc()
            neu = anfang + spl.splu(lhs).solve(w[:, None] * (ziel - anfang))
            schritt = 1.0
            while schritt > 0.1 and cls._umgeklappt(q + schritt * (neu - q), dreiecke, anfang) > max(umgeklappt_vorher, 0) + toleranz:
                schritt *= 0.5
            q = q + schritt * (neu - q)
            umgeklappt_vorher = cls._umgeklappt(q, dreiecke, anfang)
            berichte.append({'a': steifigkeit, 'reichweite_mm': round(reichweite * 1000, 1), 'vorwaerts': int(vor.sum()), 'rueckwaerts': int(rueck.sum()),
                             'schritt': schritt, 'umgeklappt': umgeklappt_vorher})
        d_netz = cKDTree(q).query(proben)[0] * 1000
        d_orig = proben_baum.query(q)[0] * 1000
        return q, {'durchgaenge': berichte, 'umgeklappt': umgeklappt_vorher,
                   'original_zu_netz_mm': [round(float(x), 2) for x in np.percentile(d_netz, [50, 90, 99])],
                   'netz_zu_original_mm': [round(float(x), 2) for x in np.percentile(d_orig, [50, 90, 99])]}

    @staticmethod
    def _normalen(punkte, dreiecke, aussen):
        """Glatte Punktnormalen des Netzes, zur Seite von `aussen` gedreht."""
        import trimesh

        n = np.asarray(trimesh.Trimesh(punkte, dreiecke, process=False).vertex_normals)
        return n * (1.0 if np.einsum('ij,ij->i', n, aussen).sum() >= 0 else -1.0)

    @staticmethod
    def _umgeklappt(punkte, dreiecke, bezug):
        """Zahl der Dreiecke, deren Normale gegen die im `bezug` (Ausgangsnetz) zeigt."""
        import trimesh

        jetzt = trimesh.Trimesh(punkte, dreiecke, process=False).face_normals
        vorher = trimesh.Trimesh(bezug, dreiecke, process=False).face_normals
        return int((np.einsum('ij,ij->i', jetzt, vorher) < 0).sum())
