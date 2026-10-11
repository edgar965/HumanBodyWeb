# -*- coding: utf-8 -*-
"""Meshfigurschammessung — die Scham-Messung von „Mesh to 3D": trifft die Genesis-Figur die Scham des Netzes? (11.10.2026)

Edgar (11.10.2026): „Ich hatte schon extra beauftragt, dass die Messung bei jedem Import ausgeführt wird. Und auch bei jedem Mesh-to-3D Auftrag." Bis dahin lief `Schammessung` nur beim Bau eines
Scham-STÜCKS (`Dazgeograft.bauen`, `Blendimportstuecke.scham_stueck`) — nicht, wenn die Figur die Scham selbst trägt (kein Stück: Rainy, seori, Rosemary …), und nie in „Mesh to 3D".
Diese Klasse schließt die Lücke: `Meshfigurvorschau.ausfuehren` ruft `sicher` bei JEDEM Auftrag (auch dem Schritt „figur" des Blender-Imports und „2D3D Kleider"), ohne Schalter; das Ergebnis
steht in `job.ergebnis['schammessung']` und als `ergebnis/schammessung.json`. Ein Fehler der Messung beendet den Lauf nie, steht aber im Ergebnis und im Log.

Gemessen wird im Beckenkasten (`Blendimportnachformung.REGIONEN['scham']`: Höhe 44–55,5 % der Körperhöhe, ±7 cm, nur die Vorderseite) an der ECHTEN Endfigur in der Haltung des Netzes
(`arbeit/posiert.npy`, Stufe 1 = 4 mm) gegen das Netz in der Lage der Erkennung (`arbeit/scan_lage.npz`), alles in mm:

    netz_zu_figur   jeder Netzpunkt im Kasten → nächster Punkt auf der Fläche der Figur: so weit müsste die Figur verschoben werden, um das Netz zu treffen
    figur_zu_netz   jeder Figurpunkt im Kasten → nächster Punkt auf der Fläche des Netzes: wo steht die Figur dort, wo das Netz nichts hat?
    je Drittel      beides getrennt nach oberem, mittlerem und unterem Drittel des Kastens (Hügel, Lippen, Damm)

Die Schwellen sind die von `Schammessung` (`FORM_MEDIAN_MM`, `FORM_P90_MM`, Setzungen). Ein Netz mit Hose oder Slip im Becken wird daran ebenso gemessen — der Wert sagt dann „Stoff", nicht „Figur falsch".
Gemessen wird die Figur VOR der Nachformung (`Blendimportnachformung`) und vor einem Scham-Stück des Imports: das ist der Stand, den „Mesh to 3D" liefert.
"""

import json
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurschammessung']


class Meshfigurschammessung:
    #: Höchstens so viele Proben je Richtung (fester Samen); mehr Punkte im Kasten werden ausgedünnt.
    PROBEN = 6000
    #: Die Flächen werden auf den Kasten plus so viel (m) zugeschnitten, bevor der nächste Punkt gesucht wird (große Netze: 500.000 Dreiecke).
    UMKREIS_M = 0.03
    #: Weniger Punkte als das in einer der beiden Flächen: keine Aussage (anderes Körperteil im Kasten, Figur sitzt, Netz ohne Becken).
    MINDEST_PUNKTE = 40
    DATEI = 'schammessung.json'

    def __init__(self, lauf):
        self.lauf = lauf
        self.ablage = lauf.ablage
        self.job = lauf.job

    # ------------------------------------------------------------------ Aufruf

    @classmethod
    def sicher(cls, lauf):
        """Messen, ohne dass ein Fehler den Lauf beendet → Bericht (bei Fehler `{'fehler': Text}`); legt `ergebnis/schammessung.json` ab."""
        try:
            messung = cls(lauf)
            bericht = messung.messen()
            for zeile in cls.zeilen(bericht):
                logger.info('Mesh to 3D %s: Schammessung: %s', lauf.job.kennung, zeile)
            lauf.ablage.ergebnis(cls.DATEI).write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
            return bericht
        except Exception as fehler:  # noqa: BLE001 — die Messung darf den Lauf nie beenden; Grund steht im Log und im Ergebnis
            logger.exception('Mesh to 3D %s: Schammessung gescheitert', lauf.job.kennung)
            return {'fehler': '%s: %s' % (type(fehler).__name__, str(fehler)[:300])}

    def messen(self):
        """Figur und Netz aus der Ablage des Auftrags laden und im Beckenkasten messen."""
        import trimesh
        from Genesis9.basisnetz import G9basisnetz

        posiert = np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64)
        stufe = G9basisnetz.holen().netzstufe(1)
        figur_punkte = np.asarray(stufe.punkte(posiert), dtype=np.float64)
        figur_dreiecke = np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3)
        netz_pfad = self.ablage.netzdatei()
        if netz_pfad is None:
            return {'hinweis': 'kein Netz im Eingang'}
        with np.load(self.ablage.arbeit('scan_lage.npz')) as d:
            matrix = np.asarray(d['matrix'], dtype=np.float64)
        netz = trimesh.load(str(netz_pfad), force='mesh', process=False)
        netz.apply_transform(matrix)
        bericht = self.flaechen(figur_punkte, figur_dreiecke, np.asarray(netz.vertices, dtype=np.float64), np.asarray(netz.faces, dtype=np.int64))
        bericht['netz'] = {'datei': netz_pfad.name, 'punkte': int(len(netz.vertices)), 'dreiecke': int(len(netz.faces))}
        return bericht

    # ------------------------------------------------------------------ Rechnung

    @classmethod
    def flaechen(cls, figur_punkte, figur_dreiecke, netz_punkte, netz_dreiecke):
        """Die Messung an zwei Flächen (Meter, Y oben, Z nach vorn; die Füße der Figur stehen auf ihrem tiefsten Punkt) — unabhängig von Dateien und Django."""
        import trimesh

        from .blendimportnachformung import Blendimportnachformung

        sohle = float(figur_punkte[:, 1].min())
        hoehe = float(figur_punkte[:, 1].max()) - sohle
        im_kasten_figur = Blendimportnachformung.kasten(figur_punkte, 'scham', sohle, hoehe)
        im_kasten_netz = Blendimportnachformung.kasten(netz_punkte, 'scham', sohle, hoehe)
        aus = {'kasten': {'figur_punkte': int(im_kasten_figur.sum()), 'netz_punkte': int(im_kasten_netz.sum()), 'hoehe_figur_m': round(hoehe, 3),
                          'hoehe_anteil': list(Blendimportnachformung.REGIONEN['scham']['hoehe'])}}
        if min(aus['kasten']['figur_punkte'], aus['kasten']['netz_punkte']) < cls.MINDEST_PUNKTE:
            aus['hinweis'] = 'zu wenige Punkte im Beckenkasten (Figur %d, Netz %d, nötig %d): keine Aussage' % (
                aus['kasten']['figur_punkte'], aus['kasten']['netz_punkte'], cls.MINDEST_PUNKTE)
            aus['abweichungen'] = []
            return aus
        proben_f = cls._ausduennen(figur_punkte[im_kasten_figur])
        proben_n = cls._ausduennen(netz_punkte[im_kasten_netz])
        flaeche_f = cls._zuschneiden(figur_punkte, figur_dreiecke, proben_f)
        flaeche_n = cls._zuschneiden(netz_punkte, netz_dreiecke, proben_n)
        d_nf = trimesh.proximity.closest_point(flaeche_f, proben_n)[1] * 1000.0
        d_fn = trimesh.proximity.closest_point(flaeche_n, proben_f)[1] * 1000.0
        aus['netz_zu_figur'] = cls._statistik(d_nf, proben_n[:, 1])
        aus['figur_zu_netz'] = cls._statistik(d_fn, proben_f[:, 1])
        aus['abweichungen'] = cls.abweichungen(aus)
        return aus

    @classmethod
    def _ausduennen(cls, punkte):
        if len(punkte) <= cls.PROBEN:
            return punkte
        return punkte[np.sort(np.random.default_rng(7).choice(len(punkte), cls.PROBEN, replace=False))]

    @classmethod
    def _zuschneiden(cls, punkte, dreiecke, proben):
        """Die Dreiecke, deren Mitte im Kasten der Proben plus `UMKREIS_M` liegt."""
        import trimesh

        lo, hi = proben.min(axis=0) - cls.UMKREIS_M, proben.max(axis=0) + cls.UMKREIS_M
        mitte = punkte[dreiecke].mean(axis=1)
        netz = trimesh.Trimesh(punkte, dreiecke[((mitte >= lo) & (mitte <= hi)).all(axis=1)], process=False)
        netz.remove_unreferenced_vertices()
        return netz

    @staticmethod
    def _statistik(d, hoehe):
        """`{n, median, p90, max, innerhalb_1mm, innerhalb_2mm, drittel: [unten, mitte, oben]}` der Abstände `d` (mm); die Drittel nach der Höhe `hoehe` (m) der Punkte."""
        def zeile(x):
            return {'n': int(len(x)), 'median': round(float(np.median(x)), 2), 'p90': round(float(np.percentile(x, 90)), 2), 'max': round(float(x.max()), 1)} if len(x) else {'n': 0}

        grenzen = np.percentile(hoehe, [100 / 3, 200 / 3])
        drittel = [zeile(d[hoehe <= grenzen[0]]), zeile(d[(hoehe > grenzen[0]) & (hoehe <= grenzen[1])]), zeile(d[hoehe > grenzen[1]])]
        return {**zeile(d), 'innerhalb_1mm': round(float((d < 1.0).mean()), 3), 'innerhalb_2mm': round(float((d < 2.0).mean()), 3), 'drittel': drittel}

    # ------------------------------------------------------------------ Urteil

    @classmethod
    def abweichungen(cls, bericht):
        """Texte zu allem, was über den Schwellen von `Schammessung` liegt (leer = alles innerhalb)."""
        from .schammessung import Schammessung

        a = []
        for schluessel, titel in (('netz_zu_figur', 'Netz → Figur'), ('figur_zu_netz', 'Figur → Netz')):
            m = bericht.get(schluessel)
            if m and (m['median'] > Schammessung.FORM_MEDIAN_MM or m['p90'] > Schammessung.FORM_P90_MM):
                a.append('Scham, %s: Median %.2f / p90 %.2f mm (Schwelle %.1f / %.1f) — die Figur trifft die Scham des Netzes dort nicht' % (
                    titel, m['median'], m['p90'], Schammessung.FORM_MEDIAN_MM, Schammessung.FORM_P90_MM))
        return a

    @staticmethod
    def zeilen(b):
        """Der Bericht als lesbare Zeilen (Log, Seite)."""
        if b.get('fehler'):
            return ['Messung gescheitert: %s' % b['fehler']]
        k = b.get('kasten') or {}
        z = ['Beckenkasten: %s Figurpunkte, %s Netzpunkte' % (k.get('figur_punkte'), k.get('netz_punkte'))]
        if b.get('hinweis'):
            return z + [b['hinweis']]
        for schluessel, titel in (('netz_zu_figur', 'Netz → Figur'), ('figur_zu_netz', 'Figur → Netz')):
            m = b[schluessel]
            z.append('%s: Median %.2f, p90 %.2f, max %.1f mm; innerhalb 1 mm %.0f %%, 2 mm %.0f %%; Drittel (unten/mitte/oben) Median %s' % (
                titel, m['median'], m['p90'], m['max'], 100 * m['innerhalb_1mm'], 100 * m['innerhalb_2mm'],
                ' / '.join('%.2f' % t['median'] if t['n'] else '–' for t in m['drittel'])))
        return z + (['ABWEICHUNG: ' + t for t in b['abweichungen']] if b.get('abweichungen') else ['keine Abweichung über den Schwellen'])
