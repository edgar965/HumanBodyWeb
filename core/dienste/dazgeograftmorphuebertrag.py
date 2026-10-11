# -*- coding: utf-8 -*-
"""Dazgeograftmorphuebertrag — die Regler `sch_*` des alten Scham-Stücks auf das angepasste Daz-Stück übernehmen (10.10.2026).

Edgar: „Portiere auf jeden Fall unsere Morphs … Da steckt viel Arbeit drin" und „wir haben den Anpassungsprozess mit der alten Scham tagelang durchprobiert". Die Regler der Anatomie rechnen ihre Zonen
(Hügel, Lippen, Haube, Eingang, Damm) aus der FORM des Stücks, in Anteilen seiner Länge und Breite (`G9schammorphe.koordinaten`) — auf dem Daz-Stück, das länger und breiter ist als der Ausschnitt des
Originals, lagen sie daneben (gemessen am 10.10.2026: `sch_haube_groesse` bewegte 2.015 von 4.260 Punkten). Das angepasste Daz-Stück liegt aber im selben Raum und auf derselben Fläche wie das alte
(`Dazgeograftanpassung`: Original → Modell Median 0,8 mm). Hier werden deshalb die fertigen Delta-Felder des alten Stücks übernommen:

    Zuordnung   jeder Punkt des Daz-Stücks → nächster Punkt auf der FLÄCHE des alten Stücks; sein Delta ist das über die drei Ecken des Dreiecks interpolierte (Schwerpunktkoordinaten)
                (der erste Versuch maß Punkt zu Punkt: das alte Stück hat in flachen Bereichen 3–4 mm Punktabstand, dort fielen Verformungen weg — Verschiebungsmasse nur 0,32 des alten)
    Auslauf     je weiter die Fläche des alten Stücks weg ist, desto weniger: voll bis `VOLL_M`, null ab `AUS_M` — der Kragen des Daz-Stücks um das Original herum (und damit der Rand an der Naht) bleibt in Ruhe
Danach misst `pruefen` je Regler, ob das neue Stück sich verformt wie das alte (Einzelheiten dort). Die alten Regler selbst bleiben unverändert.
"""
import json
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Dazgeograftmorphuebertrag']


class Dazgeograftmorphuebertrag:
    #: Abstand zur Fläche des alten Stücks (m): voll bis `VOLL_M`, null ab `AUS_M`. Gemessen 10.10.2026 an „cute girl" (Mittel je Reglergruppe, `pruefen`):
    #:   1,5 / 3,5 mm   Abdeckung 81 % (äußere Lippen 53 %, Damm 74 %)   Masse neu/alt gesamt 0,83, Hügel 0,88, äußere 0,47, innere 0,95, Haube 1,18, Eingang 0,84, Damm 0,88
    #:   3,0 / 7,0 mm   Abdeckung 93 % (äußere Lippen 82 %, Damm 82 %)   Masse                    0,84,       0,99,        0,56,        1,03,       1,20,         0,84,       0,70
    #:   4,0 / 10 mm    Abdeckung 96 %                                    Masse                    0,83,       1,02,        0,54,        1,05,       1,21,         0,84,       0,65
    #: Rest-Abstand zur verformten alten Fläche (p90 minus Grundabstand) in allen drei Fällen ≤ 0 mm. Gewählt 3 / 7 mm.
    VOLL_M, AUS_M = 0.003, 0.007
    #: Wert, bei dem `pruefen` die Verformung vergleicht.
    PRUEF_WERT = 2.0

    #: Punkte mit Gegenstück für den Vergleich in `pruefen` (m) — unabhängig von der Reichweite der Übernahme.
    PRUEF_NAH_M = 0.0015

    def __init__(self, alt, neu, voll_m=None, aus_m=None):
        """`alt`, `neu`: Kennungen der Stücke (`cute_girl_scham`, `cute_girl_daz_scham`); `voll_m`, `aus_m`: Reichweite der Übernahme (Vorgabe `VOLL_M`, `AUS_M`)."""
        import trimesh
        from Genesis9.kleidmorphe import G9kleidmorphe

        self.alt, self.neu = alt, neu
        self.voll_m = self.VOLL_M if voll_m is None else float(voll_m)
        self.aus_m = self.AUS_M if aus_m is None else float(aus_m)
        self.teile_alt, kaefige_alt, *_ = G9kleidmorphe.kaefige(alt)
        self.teile_neu, kaefige_neu, *_ = G9kleidmorphe.kaefige(neu)
        if len(self.teile_alt) != 1 or len(self.teile_neu) != 1:
            raise ValueError('Übernahme nur für Stücke aus einem Teil (%d / %d Teile)' % (len(self.teile_alt), len(self.teile_neu)))
        self.p_alt, self.p_neu = kaefige_alt[0], kaefige_neu[0]
        self.dreiecke_alt = self._dreiecke(self.teile_alt[0][0].polys)
        self.dreiecke_neu = self._dreiecke(self.teile_neu[0][0].polys)
        self.netz_alt = trimesh.Trimesh(self.p_alt, self.dreiecke_alt, process=False)
        stelle, self.abstand, dreieck = trimesh.proximity.closest_point(self.netz_alt, self.p_neu)
        self.ecken = self.dreiecke_alt[dreieck]
        self.bary = trimesh.triangles.points_to_barycentric(self.netz_alt.triangles[dreieck], stelle)
        x = np.clip((self.abstand - self.voll_m) / (self.aus_m - self.voll_m), 0.0, 1.0)
        self.auslauf = 1.0 - x * x * (3.0 - 2.0 * x)
        from Genesis9.schammorphe import G9schammorphe

        #: Flächennormalen (nach außen, wie die Regler sie rechnen: `G9schammorphe.normalen`) beider Stücke.
        self.n_alt = G9schammorphe.normalen(self.p_alt, self.teile_alt[0][0].polys)
        self.n_neu = G9schammorphe.normalen(self.p_neu, self.teile_neu[0][0].polys)

    # ------------------------------------------------------------ Übernahme

    def alt_deltas(self, name):
        """`(No, 3)` Deltas des alten Reglers `name` (Wert 1) in Dateireihenfolge des alten Stücks — baut ihn, falls er noch fehlt."""
        from Genesis9.kleidmorphe import G9kleidmorphe

        felder = G9kleidmorphe.deltas(self.alt, name)
        if not felder:
            raise ValueError('alter Regler %s/%s nicht lesbar' % (self.alt, name))
        d = np.zeros((len(self.p_alt), 3))
        for nummern, deltas in felder.values():
            d[np.asarray(nummern, dtype=np.int64)] = deltas
        return d

    #: Regler, deren Verschiebung der Formel nach genau entlang der Flächennormale zeigt (`G9schammorphe.deltas`: Art `normal`, `kraeuseln`): sie werden als vorzeichenbehafteter Betrag
    #: übertragen und am Ziel entlang DESSEN Normale gelegt — ein kopierter Vektor stand am Basis-Stück 33–55° schief zur Fläche (gemessen 10.10.2026, Damm 55°).
    NORMAL_ARTEN = ('normal', 'kraeuseln')

    def neu_deltas(self, alt_deltas, nach_normale=False):
        """`(Nn, 3)`: die Deltas des alten Stücks, auf die Punkte des neuen übertragen (`nach_normale`: als Betrag entlang der Normale des neuen Stücks)."""
        if nach_normale:
            betrag = np.einsum('ij,ij->i', alt_deltas, self.n_alt)
            return (np.einsum('nk,nk->n', self.bary, betrag[self.ecken]) * self.auslauf)[:, None] * self.n_neu
        return np.einsum('nk,nkj->nj', self.bary, alt_deltas[self.ecken]) * self.auslauf[:, None]

    def uebertragen(self, name):
        """Den Regler `name` auf das neue Stück übertragen und ablegen → `(deltas_neu (Nn, 3), Steckbrief)`."""
        from Genesis9.kleidmorphe import G9kleidmorphe

        zusatz = {'uebernommen_von': self.alt}
        try:
            with open(G9kleidmorphe._pfad(self.alt, name, '.json'), encoding='utf-8') as datei:
                zusatz['scham'] = json.load(datei).get('scham')
        except (OSError, ValueError) as fehler:
            logger.warning('Übernahme %s: Steckbrief des alten Reglers %s nicht lesbar (%s)', self.neu, name, fehler)
        art = (zusatz.get('scham') or {}).get('art')
        neu = self.neu_deltas(self.alt_deltas(name), art in self.NORMAL_ARTEN)
        brief = G9kleidmorphe.ablegen(self.neu, name, [f.kennung for f, _lage in self.teile_neu], [neu], zusatz)
        return neu, brief

    def alle(self, namen):
        """Alle Regler `namen` übertragen → `(uebernommen, gescheitert)` — die Namen bzw. `{name: Grund}`."""
        uebernommen, gescheitert = [], {}
        for name in namen:
            try:
                self.uebertragen(name)
                uebernommen.append(name)
            except (ValueError, OSError, KeyError, IndexError) as fehler:
                gescheitert[name] = str(fehler)[:160]
                logger.warning('Übernahme %s/%s gescheitert: %s', self.neu, name, fehler)
        return uebernommen, gescheitert

    # ------------------------------------------------------------ Prüfung

    @staticmethod
    def _dreiecke(polys):
        aus = []
        for poly in polys:
            v = [int(i) for i in poly[2:]]
            aus.append(v[:3])
            if len(v) > 3:
                aus.append([v[0], v[2], v[3]])
        return np.asarray(aus, dtype=np.int64)

    @staticmethod
    def _punktflaechen(punkte, dreiecke):
        """Fläche je Punkt (m²): ein Drittel der Fläche seiner Dreiecke — das Gewicht, mit dem ein Punkt zum Integral der Verschiebung beiträgt (die Stücke sind verschieden fein vermascht)."""
        p = np.asarray(punkte)
        a = 0.5 * np.linalg.norm(np.cross(p[dreiecke[:, 1]] - p[dreiecke[:, 0]], p[dreiecke[:, 2]] - p[dreiecke[:, 0]]), axis=1)
        aus = np.zeros(len(p))
        for ecke in range(3):
            np.add.at(aus, dreiecke[:, ecke], a / 3.0)
        return aus

    def pruefen(self, namen):
        """Je Regler, bei `PRUEF_WERT` (alle Zahlen in mm bzw. Anteilen):

        `grund_mm`    Abstand der neuen Punkte zur Fläche des alten Stücks ohne Verformung (Median, p90) — nur Punkte mit Gegenstück (Abstand ≤ `VOLL_M`)
        `rest_mm`     derselbe Abstand, wenn beide Stücke um den Wert verformt sind: gleich `grund_mm` heißt, das neue Stück verformt sich wie das alte
        `masse`       Integral der Verschiebung (Betrag × Fläche je Punkt) des neuen Stücks im Bereich des alten, geteilt durch das des alten (1 = gleich viel Bewegung)
        `abdeckung`   Anteil der Verschiebungssumme des alten Reglers, der auf Punkten sitzt, die höchstens `aus_m` von der Fläche des neuen Stücks entfernt sind (der Rest geht verloren)
        `bewegt_*`, `weg_*_mm`   Zahl der bewegten Punkte (über 0,05 mm) und größte Verschiebung, alt / neu"""
        import trimesh
        from Genesis9.kleidmorphe import G9kleidmorphe

        grund = self.abstand_flaeche_neu_zu_alt()
        netz_neu = trimesh.Trimesh(self.p_neu, self.dreiecke_neu, process=False)
        abstand_alt = trimesh.proximity.closest_point(netz_neu, self.p_alt)[1]
        flaeche_alt, flaeche_neu = self._punktflaechen(self.p_alt, self.dreiecke_alt), self._punktflaechen(self.p_neu, self.dreiecke_neu)
        im_alt = self.abstand <= self.PRUEF_NAH_M
        erreicht_neu = self.abstand <= self.aus_m
        aus = {'punkte_im_alten_stueck': int(im_alt.sum()), 'punkte_neu': int(len(self.p_neu)), 'alt_mit_gegenstueck': round(float((abstand_alt <= self.aus_m).mean()), 3)}
        for name in namen:
            try:
                d_alt = self.alt_deltas(name)
                felder = G9kleidmorphe.deltas(self.neu, name)
                d_neu = np.zeros((len(self.p_neu), 3))
                for nummern, deltas in (felder or {}).values():
                    d_neu[np.asarray(nummern, dtype=np.int64)] = deltas
            except (ValueError, OSError, KeyError) as fehler:
                aus[name] = {'fehler': str(fehler)[:120]}
                continue
            verformt = trimesh.Trimesh(self.p_alt + self.PRUEF_WERT * d_alt, self.dreiecke_alt, process=False)
            rest = trimesh.proximity.closest_point(verformt, (self.p_neu + self.PRUEF_WERT * d_neu)[im_alt])[1] * 1000.0
            weg_alt, weg_neu = np.linalg.norm(d_alt, axis=1) * 1000.0, np.linalg.norm(d_neu, axis=1) * 1000.0
            gedeckt = abstand_alt <= self.aus_m
            aus[name] = {'grund_mm': [round(float(np.median(grund[im_alt])), 2), round(float(np.percentile(grund[im_alt], 90)), 2)],
                         'rest_mm': [round(float(np.median(rest)), 2), round(float(np.percentile(rest, 90)), 2)],
                         'masse': round(float((weg_neu * flaeche_neu)[erreicht_neu].sum() / max((weg_alt * flaeche_alt)[gedeckt].sum(), 1e-12)), 2),
                         'abdeckung': round(float(weg_alt[gedeckt].sum() / max(weg_alt.sum(), 1e-12)), 3),
                         'bewegt_alt': int((weg_alt > 0.05).sum()), 'bewegt_neu': int((weg_neu > 0.05).sum()),
                         'weg_alt_mm': round(float(weg_alt.max()), 2), 'weg_neu_mm': round(float(weg_neu.max()), 2)}
        return aus

    GRUPPEN = ('gesamt', 'huegel', 'aussen', 'innen', 'haube', 'eingang', 'damm')

    @classmethod
    def zeilen(cls, pruefung):
        """Die Prüfung (`pruefen`) als Zeilen: je Reglergruppe Mittel von Masse, Abdeckung und Rest-Abstand; dazu jeder Regler, der schwach übernommen ist."""
        z = ['Übernahme der Regler (Wert %g): Gruppe — Masse neu/alt, Abdeckung, Rest-p90 minus Grund-p90 (mm)' % cls.PRUEF_WERT]
        schwach = []
        for gruppe in cls.GRUPPEN:
            je = {k: v for k, v in pruefung.items() if k.startswith('sch_' + gruppe + '_') and isinstance(v, dict) and 'masse' in v}
            if not je:
                continue
            z.append('  %-8s %4.2f  %3.0f %%  %+.2f' % (gruppe, np.mean([v['masse'] for v in je.values()]), 100 * np.mean([v['abdeckung'] for v in je.values()]),
                                                    np.mean([v['rest_mm'][1] - v['grund_mm'][1] for v in je.values()])))
            schwach += ['%s (Masse %.2f, Abdeckung %.0f %%)' % (k, v['masse'], v['abdeckung'] * 100) for k, v in je.items() if v['masse'] < 0.5 or v['abdeckung'] < 0.6]
        fehler = {k: v['fehler'] for k, v in pruefung.items() if isinstance(v, dict) and 'fehler' in v}
        if fehler:
            z.append('  nicht prüfbar: %s' % fehler)
        z.append('  schwach übernommen: %s' % (', '.join(schwach) if schwach else 'keiner'))
        return z

    def abstand_flaeche_neu_zu_alt(self):
        """Abstand (mm) jedes neuen Punkts zur Fläche des alten Stücks — der Grundabstand der beiden Flächen."""
        return self.abstand * 1000.0
