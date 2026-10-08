# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtsbilder — Vergleichsbilder (matplotlib) UND ihre Zahlen (Tabelle) fuer den Reiter
„Gesicht" (07.10.2026, Edgar: „mach solche Bilder mit vergleich Mesh zu Modell" / „unterhalb der View" /
„und solche in dem Stil wo du Mesh rot hast, 3D Modell blau" / „solche fuer senkrechte Schnitte, daneben
die Tabelle mit den Werten" — Referenzbilder aus der PARALLELEN Sitzung am Hunyuan-Kopf).

Drei Bilder, alle auf denselben zwei Flaechen wie `Engine2d3dKleiderGesichtsvergleich` (Mesh = ausgerichtetes
TRELLIS-Netz, Modell = aktuelle Genesis-9-Oberflaeche), Farbe durchgehend **Mesh rot, Modell blau**:

1. `schnittprofile(richtung='horizontal')` — waagerechte Schnitte alle 20 mm relativ zur Nasenspitze
   (Landmark 4): Hoehe fest, geplottet x' (Breite) gegen z' (Tiefe).
2. `schnittprofile(richtung='vertikal')` — senkrechte Schnitte alle 20 mm relativ zur Nasenspitze:
   Breite fest, geplottet y' (Hoehe) gegen z' (Tiefe).
   Beide: je Schnitt nur die VORDERE Haelfte (groesseres Z = weiter vorn), Titel zeigt die groesste
   Abweichung und wo sie liegt (wie die Vorlage: „waagerecht -40 mm / max |Δ| 29.5 mm bei -66").
3. `silhouetten()` — Seitenansicht (Tiefe × Hoehe) und Frontansicht (Breite × Hoehe) als Punktwolke: ALLE
   Kopf-Punkte von Mesh (rot) und Modell (blau) uebereinander, gruene Linie bei der Nasenspitzen-Hoehe.

`werte()` liefert dieselben Zahlen wie die Titel der Schnittprofile (beide Richtungen) als Liste — die
Tabelle neben den Bildern (`engine2d3dkleiderschnitttabelle.js`, djangoBase `sortable`) zeigt genau das.

Die Bild-Methoden geben PNG-Bytes zurueck (nichts wird auf die Platte geschrieben), der Endpunkt liefert
sie direkt als `image/png`.
"""
import io

import matplotlib
matplotlib.use('Agg')  # kein Display noetig — Server-Prozess (keine GUI-Backends)
import matplotlib.pyplot as plt
import numpy as np

from .engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage
from .engine2d3dkleidergesichtsvergleich import Engine2d3dKleiderGesichtsvergleich as GV

__all__ = ['Engine2d3dKleiderGesichtsbilder']

#: Je Richtung: die Ebenen-Normale, die deutsche Bezeichnung, welche Koordinate (0=x,1=y) im Schnitt
#: geplottet wird, und die Offsets in mm relativ zur Nasenspitze (Landmark 4) in GENAU dieser Koordinate.
RICHTUNGEN = {
    'horizontal': {'normal': (0.0, 1.0, 0.0), 'bezeichnung': 'waagerecht', 'achse': 0,
                   'offsets_mm': (-80, -60, -40, -20, 0, 20, 40)},
    'vertikal': {'normal': (1.0, 0.0, 0.0), 'bezeichnung': 'senkrecht', 'achse': 1,
                 'offsets_mm': (-60, -40, -20, 0, 20, 40, 60)},
}
MESH_FARBE, MODELL_FARBE = 'red', 'blue'


class Engine2d3dKleiderGesichtsbilder:

    @classmethod
    def schnittprofile(cls, job, ablage, richtung='horizontal'):
        vor = cls._vorbereiten(job, ablage)
        kurven = cls._kurven(richtung, *vor)
        n = len(kurven)
        fig, achsen = plt.subplots(1, n, figsize=(3.1 * n, 3.4))
        rb = RICHTUNGEN[richtung]
        for ax, (offset, mesh_xy, modell_xy, max_dev, bei) in zip(achsen, kurven):
            ax.plot(mesh_xy[:, 0], mesh_xy[:, 1], color=MESH_FARBE, linewidth=2, label='Mesh')
            ax.plot(modell_xy[:, 0], modell_xy[:, 1], color=MODELL_FARBE, linewidth=1.3, label='Modell')
            titel = '%s %+d mm' % (rb['bezeichnung'], offset)
            if max_dev is not None:
                titel += '\nmax |Δ| %.1f mm bei %+.0f' % (max_dev, bei)
            ax.set_title(titel, fontsize=9)
            ax.set_xlabel("%s' mm" % ('y' if richtung == 'vertikal' else 'x'), fontsize=8)
            ax.tick_params(labelsize=7)
            ax.set_aspect('equal', adjustable='datalim')
        achsen[0].legend(fontsize=8, loc='lower left')
        fig.suptitle('%s — %s-Schnitte, Mesh = %s (rot) gegen Modell (blau), Kopfhaltung zurückgedreht, relativ zur Nasenspitze'
                      % (job.name, rb['bezeichnung'], Engine2d3dKleiderGesichtslage.netzart(job, ablage)), fontsize=10)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        return cls._png(fig)

    @classmethod
    def werte(cls, job, ablage):
        """[{richtung, offset_mm, max_delta_mm, bei_mm}, …] — dieselben Zahlen wie in den Bild-Titeln."""
        vor = cls._vorbereiten(job, ablage)
        zeilen = []
        for richtung in RICHTUNGEN:
            for offset, _mesh_xy, _modell_xy, max_dev, bei in cls._kurven(richtung, *vor):
                zeilen.append({
                    'richtung': richtung,
                    'bezeichnung': RICHTUNGEN[richtung]['bezeichnung'],
                    'offset_mm': offset,
                    'max_delta_mm': round(max_dev, 1) if max_dev is not None else None,
                    'bei_mm': round(bei) if bei is not None else None,
                })
        return zeilen

    @classmethod
    def silhouetten(cls, job, ablage):
        gesicht, mesh_figur, modell_figur, kasten = cls._vorbereiten(job, ablage)
        nase_y = float(gesicht[4, 1])

        fig, (seite, front) = plt.subplots(1, 2, figsize=(11, 6.5))
        fig.patch.set_facecolor('#11141c')
        for figur, farbe, name in ((mesh_figur, MESH_FARBE, 'Mesh'), (modell_figur, MODELL_FARBE, 'Modell')):
            punkte = cls._kopf_punkte(figur, kasten)
            seite.scatter(punkte[:, 2] * 1000, punkte[:, 1] * 1000, s=0.6, c=farbe, alpha=0.5, label=name, linewidths=0)
            front.scatter(punkte[:, 0] * 1000, punkte[:, 1] * 1000, s=0.6, c=farbe, alpha=0.5, label=name, linewidths=0)
        for ax, titel, xlabel in ((seite, 'Seite (Tiefe × Höhe)', "z' mm"), (front, 'Front (Breite × Höhe)', "x' mm")):
            ax.set_facecolor('#11141c')
            ax.axhline(nase_y * 1000, color='lime', linewidth=1)
            ax.set_title('%s — rot Mesh, blau Modell, grün Nasenspitzen-Höhe' % titel, color='white', fontsize=10)
            ax.set_xlabel(xlabel, color='white', fontsize=9)
            ax.tick_params(colors='white', labelsize=8)
            ax.set_aspect('equal', adjustable='datalim')
            for spine in ax.spines.values():
                spine.set_color('#555')
        fig.tight_layout()
        return cls._png(fig, facecolor='#11141c')

    # --------------------------------------------------------------------------------------------- Helfer

    @staticmethod
    def _vorbereiten(job, ablage):
        # Landmarken und Netz in der Ruhelage des Modells (Kopfhaltung zurückgedreht; Kopfnetz, wenn der Körper es benutzt hat) — `Engine2d3dKleiderGesichtslage`.
        lage = Engine2d3dKleiderGesichtslage.berechnen(job, ablage)
        gesicht = lage['gesicht']
        modell_figur = GV._modell_figur(job)
        mesh_figur = GV._mesh_figur(lage)
        if mesh_figur is None:
            raise ValueError('Kein ausgerichtetes Netz — „netz/mesh.glb" oder „arbeit/scan_lage.npz" fehlt.')
        kasten = GV._kopfkasten(mesh_figur, gesicht)
        return gesicht, mesh_figur, modell_figur, kasten

    @classmethod
    def _kurven(cls, richtung, gesicht, mesh_figur, modell_figur, kasten):
        """[(offset_mm, mesh_xy, modell_xy, max_dev_mm, bei_mm), …] fuer alle Offsets der Richtung.

        `achse` ist die GEPLOTTETE Koordinate (0=x bei „horizontal", 1=y bei „vertikal"); die Ebene wird
        entlang der JEWEILS ANDEREN der beiden (`offset_achse = 1 - achse`) von der Nasenspitze verschoben —
        bei „horizontal" also die Hoehe (Y), bei „vertikal" die Breite (X)."""
        rb = RICHTUNGEN[richtung]
        normal = np.array(rb['normal'])
        achse = rb['achse']
        offset_achse = 1 - achse
        nase = gesicht[4]                         # Nasenspitze — gemeinsamer Nullpunkt beider Richtungen
        z_mitte = sum(kasten['z']) / 2
        quer_mitte = float(nase[achse])            # Mitte der GEPLOTTETEN Koordinate = Nasenspitze auf dieser Achse
        mitte_kasten = np.array([sum(kasten['x']) / 2, sum(kasten['y']) / 2, sum(kasten['z']) / 2])
        ergebnis = []
        for offset in rb['offsets_mm']:
            ursprung = mitte_kasten.copy()
            ursprung[offset_achse] = nase[offset_achse] - offset / 1000.0
            mesh_xy = cls._vorderes_profil(mesh_figur, normal, ursprung, kasten, achse, quer_mitte, z_mitte)
            modell_xy = cls._vorderes_profil(modell_figur, normal, ursprung, kasten, achse, quer_mitte, z_mitte)
            max_dev, bei = cls._max_abweichung(mesh_xy, modell_xy)
            ergebnis.append((offset, mesh_xy, modell_xy, max_dev, bei))
        return ergebnis

    @staticmethod
    def _vorderes_profil(figur, normal, ursprung, kasten, achse, quer_mitte, z_mitte_anzeige):
        """(quer'_mm, z'_mm) sortiert, nur die VORDERE Haelfte des Schnitts durch `figur`.

        Die vordere/hintere Trennung MUSS lokal an DIESEM Schnitt entschieden werden (Mittelpunkt von
        dessen EIGENEM Z-Bereich) — nicht am gemeinsamen `z_mitte_anzeige` (Befund 07.10.2026: sitzt das
        Modell insgesamt etwas weiter hinten als das Mesh, schnitt der GEMEINSAME Mittelwert einen Teil der
        echten Modell-Vorderseite als „hinten" weg, die Modell-Kurve wirkte dadurch kuenstlich flach — bis zu
        70 mm „Abweichung", die keine war). `z_mitte_anzeige` dient NUR der Anzeige (beide Kurven auf
        derselben Tiefen-Null, damit sie vergleichbar uebereinanderliegen), nicht der Auswahl."""
        segmente = GV._segmente(figur, normal, ursprung, kasten)
        if not segmente:
            return np.zeros((0, 2))
        punkte = np.array(segmente).reshape(-1, 3)
        z_lokal_mitte = (punkte[:, 2].min() + punkte[:, 2].max()) / 2
        vorn = punkte[punkte[:, 2] > z_lokal_mitte]
        if len(vorn) == 0:
            return np.zeros((0, 2))
        quer = vorn[:, achse]
        reihenfolge = np.argsort(quer)
        xy = np.stack([(quer[reihenfolge] - quer_mitte) * 1000, (vorn[reihenfolge, 2] - z_mitte_anzeige) * 1000], axis=1)
        return xy

    @staticmethod
    def _max_abweichung(mesh_xy, modell_xy):
        """(max |Δz'| mm, Stelle) — Modell-Kurve auf die Stellen des Mesh interpoliert, nur im gemeinsamen Bereich."""
        if len(mesh_xy) < 2 or len(modell_xy) < 2:
            return None, None
        x_lo = max(mesh_xy[:, 0].min(), modell_xy[:, 0].min())
        x_hi = min(mesh_xy[:, 0].max(), modell_xy[:, 0].max())
        innen = (mesh_xy[:, 0] >= x_lo) & (mesh_xy[:, 0] <= x_hi)
        if not innen.any():
            return None, None
        modell_bei_mesh_x = np.interp(mesh_xy[innen, 0], modell_xy[:, 0], modell_xy[:, 1])
        delta = np.abs(mesh_xy[innen, 1] - modell_bei_mesh_x)
        i = int(np.argmax(delta))
        return float(delta[i]), float(mesh_xy[innen, 0][i])

    @staticmethod
    def _kopf_punkte(figur, kasten):
        v = figur.vertices
        innen = (
            (v[:, 0] >= kasten['x'][0]) & (v[:, 0] <= kasten['x'][1])
            & (v[:, 1] >= kasten['y'][0]) & (v[:, 1] <= kasten['y'][1])
            & (v[:, 2] >= kasten['z'][0]) & (v[:, 2] <= kasten['z'][1])
        )
        return v[innen]

    @staticmethod
    def _png(fig, facecolor=None):
        puffer = io.BytesIO()
        fig.savefig(puffer, format='png', dpi=130, facecolor=facecolor or fig.get_facecolor())
        plt.close(fig)
        puffer.seek(0)
        return puffer.getvalue()
