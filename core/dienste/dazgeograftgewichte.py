# -*- coding: utf-8 -*-
"""Dazgeograftgewichte — die Hautgewichte eines Daz-Geograft-Stücks aus Dazs eigener Hautbindung (28.10.2026).

Edgar, 28.10.2026 (Mesh3D-AI, Test edgar, Bild): „fixe auch das Geschlechtsteil, das ist entweder nicht da oder monströs in der 2. Zeile“. Gemessen: In der Ruhelage
ist „Daz Anatomie Mann“ ganz. Gehäutet in der Haltung des Tests (Oberschenkel 10° und 17,6° gegen die Ruhe) liegen die Lagen, die die Knochen eines Punkts ihm geben,
bis 83 mm auseinander (p90 48 mm, 30 % der Punkte über 10 mm), das Stück zerknüllt (`ProjektTemp/_wegwerf/regler_ki/anatomie_pruefen.py`, im Tab `__mesh3daitest`).
Ursache: `Blendimportschamgewichte` gibt jedem Punkt die Gewichte der Haut, die ihn verdeckt. Penis und Hoden hängen zwischen den Oberschenkeln, ihre Verdecker sind deren
Innenseiten: 2.971 bzw. 2.975 von 6.028 Punkten trugen `l_/r_thightwist1` (Summe 791 und 785, zusammen 26 %). Dazs Geograft (`Genesis9MaleGenitalia.dsf`, `SkinBinding`)
gibt den Oberschenkeln 0,9 % (Summe 13 von 1.516, `geograft_gewichte.py`), alles andere `pelvis` und eigenen Knochen darunter (`genbase`, `gen1`–`gen6`, `testes`,
`l_/r_teste`). Beim weiblichen Stück lag die Verdecker-Rechnung nahe an Daz (Stück 1,2 %, Daz 1,1 % auf den Oberschenkeln).

HIER — nur, was Daz tut: die Gewichte der `SkinBinding` je Käfigpunkt. Eigene Knochen, die die Figur nicht hat, fallen auf ihren ersten Vorfahren im Skelett der Figur
(wie `G9haut.umleitung`; beim Geograft alle auf `pelvis`). Neigung und Erektion rechnen ohnehin die Regler (`Dazgeograft`, Docstring). Über die Unterteilung
(`G9netzstufe.matrix`, linear wie die Punkte) kommen sie auf die Stufe des Stücks, je Stückpunkt aus den `NACHBARN` nächsten Punkten des geposteten Geografts, nach
Kehrwert des Abstands. Zuschnitt, Randseite und Naht verschieben Punkte, darum über die Lage, nicht die Nummer. Den Rand legt danach
`Blendimportschamgewichte.an_ring` auf die Haut (Daz: Randpunkte SIND Punkte des Körpers).
"""
import numpy as np

__all__ = ['Dazgeograftgewichte']


class Dazgeograftgewichte:
    NACHBARN = 4

    def __init__(self, quelle, knochen):
        """`quelle`: `Dazgeograftquelle`; `knochen`: die Namen der Gewichtsspalten (Skelett der Figur, `Blendimportschamgewichte.knochen`)."""
        self.quelle = quelle
        self.knochen = list(knochen)
        self.bericht = {}

    def kaefig(self):
        """`(K, len(knochen))`: die Gewichte der `SkinBinding` je Käfigpunkt, eigene Knochen auf ihrem ersten Vorfahren in `knochen`."""
        from Genesis9.dson import G9dson

        q = self.quelle
        doc = G9dson.lesen(q.ordner / q.DATEI[q.geschlecht])
        # id → (Name, Eltern-id); die Gelenke zeigen auf die id (`#lThighTwist`), die Figur kennt den Namen (`l_thightwist1`)
        knoten = {n['id']: (n.get('name') or n['id'], str(n.get('parent') or '').lstrip('#') or None) for n in doc.bibliothek('node_library')}
        spalte = {name: i for i, name in enumerate(self.knochen)}
        w = np.zeros((len(q.punkte), len(self.knochen)))
        umgelegt = {}
        haut = next(m for m in doc.modifikatoren() if m.get('id') == 'SkinBinding')['skin']
        for gelenk in haut['joints']:
            werte = np.asarray((gelenk.get('node_weights') or {}).get('values') or [], dtype=np.float64).reshape(-1, 2)
            if not len(werte):
                continue
            k = str(gelenk.get('node', '')).lstrip('#')
            while k is not None and knoten.get(k, (k, None))[0] not in spalte:
                k = knoten.get(k, (None, None))[1]
            if k is None:
                raise ValueError('Gelenk %s des Geografts hat keinen Vorfahren im Skelett der Figur' % gelenk.get('node'))
            ziel = knoten.get(k, (k, None))[0]
            if ziel != gelenk.get('id'):
                umgelegt[str(gelenk.get('id'))] = ziel
            np.add.at(w[:, spalte[ziel]], werte[:, 0].astype(np.int64), werte[:, 1])
        summe = w.sum(axis=1)
        if (summe <= 0).any():
            raise ValueError('%d Käfigpunkte des Geografts ohne Gewicht' % int((summe <= 0).sum()))
        self.bericht['umgelegt'] = umgelegt
        self.bericht['oberschenkel_anteil'] = round(float(w[:, [spalte[n] for n in spalte if 'thigh' in n]].sum() / summe.sum()), 4)
        return w / summe[:, None]

    def dicht(self, p, stufe, lage):
        """`(N, len(knochen))` für die Stückpunkte `p` (m, Ruhelage): Käfiggewichte über `stufe.matrix` auf die Stufe, je Stückpunkt aus den nächsten Punkten der Stufe
        in der Lage `lage` (`(P, 3)`, `Dazgeograft.stufe_punkte`: das gepostete Geograft, dieselbe Reihenfolge wie die Matrix)."""
        from scipy.spatial import cKDTree

        p = np.asarray(p, dtype=np.float64)
        w_kaefig = self.kaefig()
        w_stufe = np.asarray(stufe.matrix(len(w_kaefig)) @ w_kaefig, dtype=np.float64)
        abstand, nachbar = cKDTree(np.asarray(lage, dtype=np.float64)).query(p, k=self.NACHBARN)
        g = 1.0 / np.maximum(abstand, 1e-6)
        aus = (g[:, :, None] * w_stufe[nachbar]).sum(axis=1) / g.sum(axis=1)[:, None]
        aus /= aus.sum(axis=1, keepdims=True)
        self.bericht.update(punkte=int(len(p)), abstand_mm={'median': round(float(np.median(abstand[:, 0])) * 1000.0, 3), 'max': round(float(abstand[:, 0].max()) * 1000.0, 3)})
        return aus
