# -*- coding: utf-8 -*-
"""Meshfigurkleidungsruhelage — das Kleidungsobjekt von „Mesh to 3D" aus der Haltung des Netzes in die Ruhelage der Figur, mit Körperteilen (12.10.2026).

Bis 12.10.2026 rechnete `Meshfigurkleidung.objekt` jeden Stoffpunkt über die 40 nächsten Käfigpunkte zurück, gleich welchen Körperteils. Am Auftrag „Edgar" (`2026.10.12.12.18.38`) hängt die linke Hand 6 cm neben dem Saum der
Unterhose; die Hand hat 3.000 dichte Käfigpunkte, 25 % der 40 Nachbarn der Saumpunkte, und drehte 627 Punkte (7 cm Saum) mit dem Arm nach außen: eine Fahne bis 131 mm vom Körper (Kantenverzerrung bis 37,4×). Dasselbe war beim
Blender-Import die Hand auf der Hüfte (`Blendimportlage`, `Kleidungsentposen.ruhelage(teile=)`); hier derselbe Weg: jeder Punkt sucht sein Teil (nächster Käfigpunkt mit passender Normale), kleine Inseln und freier Stoff übernehmen
das Teil ihrer Nachbarn auf dem Stoff, danach rechnet `ruhelage` nur mit den Käfigpunkten dieses und der angrenzenden Teile, und `entzerren` hält frei hängenden Stoff bei den Kantenlängen des Originals.

Die Konstanten sind die von `Blendimportlage` (an drei Modellen abgestimmt, `blendimport-kleidung.md`) — es gibt keine zweite Fassung.
Gemessen am Auftrag „Edgar" (`ProjektTemp/_wegwerf/mesh3d/hose_entposen_ursache.py`): Abstand zum Käfig max 131 → 53 mm, Punkte über 60 mm 627 → 0, Kanten außerhalb 0,75–1,33 5,25 → 1,66 %, größte Streckung 37,4× → 2,2×; `entzerren` allein kostet 29 s.
"""

import numpy as np

__all__ = ['Meshfigurkleidungsruhelage']


class Meshfigurkleidungsruhelage:
    def __init__(self, kaefig_ruhe, kaefig_posiert, teil=None, kaefig_normalen=None):
        """`kaefig_ruhe`, `kaefig_posiert` (N, 3) Meter — derselbe Käfig in Ruhe und in der Haltung des Netzes; `teil` (N,) Körperteil je Käfigpunkt (`genesis_ende.npz`, `teil`). Ohne `teil` rechnet es wie vor dem 12.10.2026.
        `kaefig_normalen` (N, 3): Punktnormalen des posierten Käfigs; ohne sie rechnet `G9basisnetz` sie (nur für den echten Käfig von 25.182 Punkten)."""
        from Genesis9.koerperteile import G9koerperteile
        from Kleidung.kleidungsentposen import Kleidungsentposen

        self.posiert = np.asarray(kaefig_posiert, dtype=np.float64)
        self.teil = None if teil is None else np.asarray(teil)
        self._kaefig_normalen = None if kaefig_normalen is None else np.asarray(kaefig_normalen, dtype=np.float64)
        self.entposen = Kleidungsentposen(
            kaefig_ruhe, self.posiert, self.teil, G9koerperteile.nachbarn() if self.teil is not None else None
        )
        #: Befund des letzten `punkte`: `{mit_teilen, teile, h_mm, kante_mm, abstand_median_mm, abstand_max_mm}`.
        self.befund = {}

    @property
    def h(self):
        """Punktabstand des posierten Käfigs (m): Median des Abstands zum nächsten Nachbarn (wie `Blendimportlage.h`)."""
        from scipy.spatial import cKDTree

        return float(np.median(cKDTree(self.posiert).query(self.posiert, k=2)[0][:, 1]))

    def kaefig_normalen(self):
        if self._kaefig_normalen is None:
            from Genesis9.basisnetz import G9basisnetz

            self._kaefig_normalen = G9basisnetz.holen().normalen(self.posiert)
        return self._kaefig_normalen

    def punkte(self, netz, dreiecke):
        """(M, 3) — die Punkte des Kleidungsnetzes (Lage des Netzes, Meter) in der Ruhelage der Figur."""
        netz = np.asarray(netz, dtype=np.float64)
        if self.teil is None:
            ruhe = self.entposen.ruhelage(netz)
            self.befund = {'mit_teilen': False}
            return ruhe
        from .blendimportlage import Blendimportlage as L

        d = np.asarray(dreiecke, dtype=np.int64)
        h = self.h
        kante = float(np.median(np.linalg.norm(netz[d[:, 0]] - netz[d[:, 1]], axis=1)))
        normalen = L.netz_normalen(netz, d)
        kaefig = self.kaefig_normalen()
        _, nah = self.entposen.baum.query(netz)
        if float(np.einsum('ij,ij->i', normalen, kaefig[nah]).mean()) < 0.0:      # Umlauf des Netzes gegen den des Käfigs
            normalen = -normalen
        teile, abstand = self.entposen.teile_von(netz, None, normalen, kaefig, abstand=True)
        je_punkt = 0.87 * max(kante, 1e-6) ** 2
        flaeche = min(max(L.INSEL_E2 * je_punkt, L.INSEL_FLAECHE_H2[0] * h * h), L.INSEL_FLAECHE_H2[1] * h * h)
        teile = self.entposen.teile_inseln(teile, d, max(3, int(round(flaeche / je_punkt))), abstand=abstand, ab=L.INSEL_AB_H * h)
        haft = np.exp(-(abstand / (L.HAFT_H * h)) ** 2)
        teile = self.entposen.teile_glaetten(teile, d, haft, runden=L.GLAETTEN_STOFF)
        ruhe = self.entposen.ruhelage(netz, teile)
        ruhe = self.entposen.entzerren(ruhe, netz, d, abstand, min(L.KOPPELN_H * h, L.KOPPELN_E * kante), L.ANKER, L.ANKER_H * h)
        self.befund = {'mit_teilen': True, 'teile': int(len(np.unique(teile))), 'h_mm': round(h * 1000, 2), 'kante_mm': round(kante * 1000, 2),
                       **self._abstand(ruhe)}
        return ruhe

    def _abstand(self, ruhe):
        """Abstand der Punkte in Ruhe zum Käfig in Ruhe (Median, größter) — eine Fahne zeigt sich im größten."""
        from scipy.spatial import cKDTree

        d, _ = cKDTree(self.entposen.ruhe).query(ruhe, workers=-1)
        return {'abstand_median_mm': round(float(np.median(d)) * 1000, 1), 'abstand_max_mm': round(float(d.max()) * 1000, 1)}
