# -*- coding: utf-8 -*-
"""Blendimportnachformung — die Scham der Genesis-Figur an das Original angleichen (08.10.2026).

Edgar zu „cute girl": „die scham ist völlig anders als in Blender, überprüfe, Textur und form kaputt — vor allem in der hohen
Auflösung". Gemessen am Import 2026.10.08.19.31.50 (Mittelschnitt, `scham_schnitt.py`): Die Figur steht im unteren Teil des
Venushügels bis 22 mm VOR dem Original (z 0,86 m), bei 0,88 m noch 9 mm; darüber stimmen beide auf 1–2 mm. „Mesh to 3D" lässt
diese Stelle liegen (warum, ist nicht geprüft — Vermutung: die Zuordnung der Anpassung weist so große Abstände als Ausreißer
ab, und der Eigenmorph ist das GLÄTTETE Restfeld, `G9restmorph`). Der Bake trifft dort dann das Original bis 20 mm hinter der
Fläche: gesprenkelte Normalen und Farbränder, im 8K-Bild deutlich (Kachel 1002, Ausschnitt gesehen 08.10.2026).

WAS HIER GESCHIEHT: Je Durchgang wird die Fläche der Figur (Stufe 1, aus Reglern + Eigenmorph) im Beckenkasten gegen die Fläche
des Originals (Ruhelage) gemessen; jeder Punkt wird ein Stück zum nächsten Punkt des Originals gezogen. Die ersten N Punkte
der Stufe 1 sind die N Käfigpunkte — ihre Verschiebung, geglättet (`G9restmorph.glaetten`), kommt als Zusatz auf den
Käfig. Vier Durchgänge mit Entspannung 0,8 (ein Käfigpunkt bewegt die Fläche nur zum Teil). Am Ende steht das Zusatzfeld als
EIGENER Regler neben dem Eigenmorph der Anpassung (Edgar: „baue dir neue Regler, falls Genesis die nicht hat!"):
`eigen:<Eigenmorph>_<region>`, Wert 1 = die Form des Originals, 0 = die Form der Anpassung, bis 2 übertrieben — im Bedienfeld
„Modell-Eigen" als Schieber „<Figur> · Eigenform · scham" (`Blendimportmodell.eigenform_markieren`). Reglerstellung, Bake, Stücke
und Modell bekommen ihn über `zusatzregler` (Bericht `regler`, Stand `ergebnis.nachformung`).

GEMESSEN (Probe `nachformung_probe.py`, 4 Durchgänge): Abstand der Flächenpunkte im Kasten zum Original Median 2,28 → 0,14 mm,
p90 12,5 → 1,1 mm (max 21 → 11 mm: die kleinen Schamlippen sind feiner als die Fläche); der 30-mm-Rand ringsum wurde nicht
schlechter (p90 3,6 → 1,3 mm); der Käfig wandert dafür bis 23 mm. Was bleibt: Die Figur hat dort keine Form für die inneren
Schamlippen — das Bild des Originals sitzt dann als Farbe auf einer weichen Mulde.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportnachformung']


class Blendimportnachformung:
    DURCHGAENGE = 4
    #: Anteil der gemessenen Verschiebung, der je Durchgang auf den Käfig geht (ein Käfigpunkt bewegt die Fläche nur zum Teil).
    ENTSPANNUNG = 0.8
    #: Weiter als das vom Original entfernte Flächenpunkte (m) sind keine Zuordnung, sondern ein anderes Körperteil.
    AUSREISSER_M = 0.04
    GLAETTEN = (3, 0.5)
    #: Kästen: Höhe als Anteil der Körperhöhe über der Sohle (von, bis), halbe Breite in m bei 1,75 m Körperhöhe; nur die Vorderseite.
    REGIONEN = {'scham': {'hoehe': (0.44, 0.555), 'breite_m': 0.07}}
    #: Kleinere Zusatzverschiebungen (m) bleiben weg (wie `G9restmorph.MINDESTENS`).
    MINDESTENS = 1e-4

    def __init__(self, ablage, job, inventar, rollen, figurname, melden=None):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.figurname = figurname
        self.melden = melden or (lambda anteil, text: None)

    @staticmethod
    def zusatzregler(stand):
        """`{eigen:…: 1.0}` der Nachformung aus dem Stand eines Imports (`stand.json`) — leer ohne sie."""
        return dict(((stand or {}).get('ergebnis') or {}).get('nachformung', {}).get('regler') or {})

    # ------------------------------------------------------------- Bausteine

    @classmethod
    def kasten(cls, punkte, region, sohle, hoehe):
        """Maske der Punkte (Ruhelage, Y oben, Z nach vorn) im Kasten `region` — nur die Vorderseite."""
        r = cls.REGIONEN[region]
        unten, oben = sohle + r['hoehe'][0] * hoehe, sohle + r['hoehe'][1] * hoehe
        breit = r['breite_m'] * hoehe / 1.75
        return ((punkte[:, 1] > unten) & (punkte[:, 1] < oben) & (np.abs(punkte[:, 0]) < breit)
                & (punkte[:, 2] > float(np.median(punkte[:, 2]))))

    @classmethod
    def verschiebung(cls, flaeche, original, maske):
        """`(N, 3)`: je Punkt in `maske` der Vektor zum nächsten Punkt auf der Fläche des Originals (trimesh); Ausreißer und
        alles außerhalb der Maske bleiben 0."""
        import trimesh

        aus = np.zeros((len(flaeche), 3))
        if not maske.any():
            return aus
        nah, _abstand, _dreieck = trimesh.proximity.closest_point(original, flaeche[maske])
        aus[np.flatnonzero(maske)] = nah - flaeche[maske]
        aus[np.linalg.norm(aus, axis=1) > cls.AUSREISSER_M] = 0.0
        return aus

    @classmethod
    def zusammenfuehren(cls, nummern, deltas, zusatz):
        """`(nummern, deltas)` des bisherigen Eigenmorphs plus das Zusatzfeld `zusatz` (N, 3) — dicht addiert, kleine Reste weg."""
        dicht = np.zeros((len(zusatz), 3))
        if nummern is not None and len(nummern):
            dicht[np.asarray(nummern, dtype=np.int64)] = np.asarray(deltas, dtype=np.float64)
        dicht += zusatz
        neu = np.flatnonzero(np.linalg.norm(dicht, axis=1) > cls.MINDESTENS)
        return neu.astype(np.int32), dicht[neu].astype(np.float32)

    # ----------------------------------------------------------------- Lauf

    def original(self, lage):
        """Fläche des Originalkörpers in der Ruhelage der Figur (Y oben) als `trimesh.Trimesh`."""
        import trimesh

        name = next(r['name'] for r in self.rollen if r['rolle'] == 'koerper')
        with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
            punkte, dreiecke = d['punkte'], d['dreiecke']
        return trimesh.Trimesh(lage.ruhelage(punkte), dreiecke, process=False)

    def abstaende(self, flaeche, original, maske):
        """`{median_mm, p90_mm, max_mm}` der Flächenpunkte in `maske` zum Original."""
        import trimesh

        d = trimesh.proximity.closest_point(original, flaeche[maske])[1] * 1000.0
        return {'median_mm': round(float(np.median(d)), 2), 'p90_mm': round(float(np.percentile(d, 90)), 2),
                'max_mm': round(float(d.max()), 1)}

    def formen(self):
        """Den Eigenmorph der Anpassung nachformen; gibt den Bericht (Abstände vorher/nachher) oder `{'aus': Grund}`."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.restmorph import G9restmorph

        from .blendimportlage import Blendimportlage

        reglername = ((self.job.ergebnis or {}).get('rest') or {}).get('regler')
        if not reglername or not G9eigenmorphe.vorhanden(reglername):
            return {'aus': 'Mesh to 3D hat keinen Eigenmorph geschrieben'}
        lage = Blendimportlage(self.job)
        original = self.original(lage)
        stufe = G9basisnetz.holen().netzstufe(1)
        anzahl = len(G9basisnetz.holen().punkte)
        kaefig0 = np.asarray(G9reglerableitung.lage(G9formung(self.job.stellung()))[0], dtype=np.float64)
        sohle = float(original.vertices[:, 1].min())
        hoehe = float(original.vertices[:, 1].max()) - sohle
        felder, bericht = {}, {}
        for region in self.REGIONEN:
            zusatz = np.zeros_like(kaefig0)
            for durchgang in range(self.DURCHGAENGE + 1):
                flaeche = np.asarray(stufe.punkte(kaefig0 + zusatz), dtype=np.float64)
                maske = self.kasten(flaeche, region, sohle, hoehe)
                if not maske.any():
                    bericht[region] = {'aus': 'kein Flächenpunkt im Kasten'}
                    break
                if durchgang == 0:
                    bericht[region] = {'vorher': self.abstaende(flaeche, original, maske), 'punkte': int(maske.sum())}
                if durchgang == self.DURCHGAENGE:
                    bericht[region]['nachher'] = self.abstaende(flaeche, original, maske)
                    break
                rest = self.verschiebung(flaeche, original, maske)[:anzahl]
                feld = G9restmorph.glaetten(rest, (np.linalg.norm(rest, axis=1) > 0).astype(float), *self.GLAETTEN)
                zusatz = zusatz + self.ENTSPANNUNG * feld
            felder[region] = zusatz
            bericht[region]['zusatz_max_mm'] = round(float(np.linalg.norm(zusatz, axis=1).max()) * 1000.0, 1)
            self.melden(0.95, 'Nachformung %s' % region)
        kennung = reglername[len(G9eigenmorphe.PRAEFIX):]
        regler = {}
        for region, zusatz in felder.items():
            if 'aus' in bericht[region]:
                continue
            nummern, deltas = self.zusammenfuehren(None, None, zusatz)
            brief = {'anzeige': '%s · Eigenform · %s' % (self.figurname, region), 'nachformung': bericht[region]}
            regler[G9eigenmorphe.ablegen('%s_%s' % (kennung, region), nummern, deltas, brief)] = 1.0
        bericht['regler'] = regler
        logger.info('Blender-Import %s: Nachformung %s', self.ablage.kennung, bericht)
        return bericht
