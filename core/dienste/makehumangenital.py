# -*- coding: utf-8 -*-
"""Makehumangenital — MakeHumans Genitalien als Stück „MakeHuman Penis" der Garderobe (18.10.2026).

Edgar, 18.10.2026: „mach eine extra Abteilung bei Genesis Morphs für die Genitalien … und von MakeHuman gibt es noch welche". MakeHuman hat genau
eine Genitalform, den Helfer `helper-genital` des Grundnetzes hm08, und drei Ziele darauf (Länge, Umfang, Hoden; `Makehumangenitalquelle`). Als
Körpermorph ließen sich die Ziele nicht bauen — sie erreichen keinen Käfigpunkt von Genesis (`G9mhmorphe`). Hier werden sie, was sie in MakeHuman
sind: die Form eines eigenen Netzes.

    Lage      STARR (`lage`): Drehung, einheitlicher Maßstab und Verschiebung, angepasst (Umeyama) an die Haut rings um den Ansatz — hm08 gegen den
              Klon (`G9mhklon.punkte`, hm08 in der Gestalt von Genesis 9). Die erste Fassung nahm die Helferpunkte des Klons selbst: jeder bekommt den
              Weg SEINES nächsten Hautpunkts, und die liegen an Schritt und Innenschenkeln verschieden — Edgar, 18.10.2026: „dieses neue genital aus
              dem bild ist total kaputt" (Hodensack und Ansatz zu Lappen gezerrt; in hm08 selbst ist die Form heil, `_wegwerf/mh_genital_helfer.png`)
    Netz      Catmull-Clark auf `STUFE` (`G9netzstufe`, wie Dazs Geograft) — der Helfer hat nur 182 Vierecke; UV-Nähte verschweißt wie `Dazgeograft.nahtfrei`
    Schreiben `G9eigenstueck.schreiben` ohne Heben (der Ansatz liegt am Körper), alle Punkte am Becken; `.ersetzt.json` mit `anatomie: penis`, Hauttiefe
              und `hoehe_mm` wie beim Daz-Geograft — so bekommt das Stück auch die eigenen Regler des Penis (`G9penis`, `pen_*`) und folgt der Haut
              (`anatomiehaut.js`: ohne eigene Karte backt es die Karten des Körpers)
    Regler    je Ziel und Seite ein eigener Morph 0 … 1 (`G9kleidmorphe.ablegen`, Gruppe „Penis · MakeHuman"): Verschiebung × 0,1 (dm → m), mit
              derselben Drehung und demselben Maßstab wie die Lage, durch dieselbe Unterteilung (sie ist linear)

Kein Loch in der Haut: der Helfer ist an seinem Ansatz offen (34 Kanten) und hat keinen Ring auf Genesis' Haut; die Haut dahinter blendet die Hauttiefe
aus wie bei jedem Anatomie-Stück. Wie es im Bild aussieht, ist mit dem Bau nicht geprüft — das sagt erst der Browser.
"""
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Makehumangenital']


class Makehumangenital:
    NAME = 'MakeHuman Penis'
    ANATOMIE = 'penis'
    KATEGORIE = ('Follower/Accessory', '/Default/Accessories')
    MATERIAL = 'Genitalia MakeHuman'
    REGLERGRUPPE = 'Penis · MakeHuman'
    PRAEFIX = 'mh_penis_'
    #: Ohne eigene Textur die Mittelfarbe der männlichen Basishaut, wie „Daz Anatomie Mann" ohne Variante (`Dazgeograft.FARBEN`).
    FARBE = (159 / 255.0, 120 / 255.0, 102 / 255.0)
    #: Stufe 2: 182 · 16 = 2.912 Vierecke, Punktabstand wie Dazs Geograft auf Stufe 1 (~4 mm).
    STUFE = 2
    KNOCHEN = 'pelvis'
    LAGE_M = 1e-7
    #: Ein Punkt des geschriebenen Stücks muss so nah (m) an einem gerechneten liegen, sonst stimmt die Zuordnung der Regler nicht.
    MAX_ABSTAND_M = 0.001
    #: Hautpunkte von hm08 so nah (m) am offenen Ansatz des Helfers tragen die starre Anpassung.
    ANKER_M = 0.05
    #: So tief hinter dem Stück wird die Haut ausgeblendet (mm). NICHT die 30 mm des Daz-Geografts: der Hodensack hängt dichter an den Innenschenkeln —
    #: gesehen im Chrome 18.10.2026 (Ursula1, und Edgars Bild): Löcher in der Schenkelhaut neben dem Hodensack.
    HAUT_TIEFE_MM = 3.0

    def lage(self, quelle):
        """`(kaefig, s, R, bericht)`: der Helfer starr auf Genesis — `s·R·p + t` aus den Hautpunkten um den Ansatz (hm08 → Klon, Umeyama ohne Spiegelung)."""
        from Genesis9.mhklon import G9mhklon
        from MakeHuman.basisnetz import Mhbasisnetz
        from scipy.spatial import cKDTree

        mh = Mhbasisnetz.holen()
        alle = np.arange(len(mh.punkte))
        vorlage = np.asarray(mh.punkte_am_boden(alle), dtype=np.float64)
        klon = np.asarray(G9mhklon.holen().punkte(), dtype=np.float64)
        koerper = mh._punktnummern(('koerper',))
        kanten = {}
        for viereck in quelle.vierecke:
            for a, b in zip(viereck, np.roll(viereck, -1), strict=True):
                kanten[tuple(sorted((int(a), int(b))))] = kanten.get(tuple(sorted((int(a), int(b)))), 0) + 1
        ansatz = quelle.nummern[sorted({p for k, n in kanten.items() if n == 1 for p in k})]
        abstand, _n = cKDTree(vorlage[ansatz]).query(vorlage[koerper])
        anker = koerper[abstand < self.ANKER_M]
        a, b = vorlage[anker], klon[anker]
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, sigma, vt = np.linalg.svd((b - mb).T @ (a - ma) / len(a))
        d = np.diag([1.0, 1.0, np.sign(np.linalg.det(u @ vt))])
        drehung = u @ d @ vt
        s = float(np.trace(np.diag(sigma) @ d) / ((a - ma) ** 2).sum(axis=1).mean())
        kaefig = s * (vorlage[quelle.nummern] - ma) @ drehung.T + mb
        rest = np.linalg.norm(s * (a - ma) @ drehung.T + mb - b, axis=1) * 1000.0
        winkel = float(np.degrees(np.arccos(np.clip((np.trace(drehung) - 1.0) / 2.0, -1.0, 1.0))))
        return kaefig, s, drehung, {'anker': int(len(anker)), 'massstab': round(s, 4), 'drehung_grad': round(winkel, 2),
                                    'anker_rest_mm': [round(float(np.median(rest)), 1), round(float(rest.max()), 1)]}

    def bauen(self):
        """Das Stück schreiben, seine sechs MakeHuman-Regler und die Regler des Penis bauen → Bilanz von `G9eigenstueck.schreiben` mit `bericht`."""
        from Genesis9.netzstufe import G9netzstufe

        from .makehumangenitalquelle import Makehumangenitalquelle

        quelle = Makehumangenitalquelle()
        kaefig, massstab, drehung, lage = self.lage(quelle)
        polys, uvs, ueber = quelle.kaefig_daz()
        stufe = G9netzstufe('mh_genital', polys, [self.MATERIAL], uvs, ueber, None, self.STUFE)
        roh = np.asarray(stufe.punkte(kaefig), dtype=np.float64)
        dreiecke = np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3)
        uv_ecken = np.asarray(stufe.uv, dtype=np.float64)[dreiecke]
        erste, rep = self.nahtfrei(roh)
        punkte, dreiecke = roh[erste], rep[dreiecke]
        aussen = self.aussen(punkte, dreiecke)
        if aussen < 0.5:                                   # die Vierecke zeigen nach innen: umdrehen (das Stück zeichnet nur die Vorderseite)
            dreiecke, uv_ecken = dreiecke[:, [0, 2, 1]], uv_ecken[:, [0, 2, 1]]
        bilanz = self.schreiben(punkte, dreiecke, uv_ecken)
        bericht = {'helfer_punkte': int(len(quelle.nummern)), 'helfer_vierecke': int(len(quelle.vierecke)), 'stufe': self.STUFE, 'lage': lage,
                   'aussen_anteil': round(max(aussen, 1.0 - aussen), 3), 'hoehe_mm': [round(float(np.ptp(punkte[:, 1])) * 1000.0, 1)]}
        bericht['regler'] = self.regler(quelle, stufe, kaefig, erste, massstab * quelle.massstab * drehung, bilanz['stueck'])
        bericht['regler_gebaut'], bericht['regler_gescheitert'] = self._penis(bilanz['stueck'])
        bilanz['bericht'] = bericht
        logger.info('MakeHuman Penis: %s', bericht)
        return bilanz

    def nahtfrei(self, roh):
        """Wie `Dazgeograft.nahtfrei`: `(erste, rep)` — die Punkte nach dem Verschweißen der UV-Nähte und auf welchen jeder Rohpunkt fällt."""
        schluessel = np.round(roh / self.LAGE_M).astype(np.int64)
        _, erste, rep = np.unique(schluessel, axis=0, return_index=True, return_inverse=True)
        return erste, rep.ravel()

    @staticmethod
    def aussen(punkte, dreiecke):
        """Anteil der Dreiecke, deren Normale von der Mitte des Stücks weg zeigt."""
        a, b, c = (punkte[dreiecke[:, i]] for i in range(3))
        normale = np.cross(b - a, c - a)
        return float(((normale * ((a + b + c) / 3.0 - punkte.mean(axis=0))).sum(axis=1) > 0).mean())

    def schreiben(self, punkte, dreiecke, uv_ecken):
        """OBJ → Stück wie `Dazgeograft.schreiben`, aber ohne Loch und Naht: Becken als Knochen, `anatomie: penis`."""
        import trimesh
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.objleser import G9objleser
        from Genesis9.stueckersatz import G9stueckersatz

        from .blendimportbilder import Blendimportbilder
        from .blendimportschamhoehe import Blendimportschamhoehe
        from .dazgeografthaut import Dazgeografthaut

        kennung, anzeige = G9eigenstueck.kennung_und_name(self.NAME)
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        material = {'name': self.MATERIAL, 'farbe': self.FARBE, 'bild': None, 'shininess': 0.4, 'opacity': None}
        netz = G9objleser.lesen(str(Blendimportbilder.obj(ordner, punkte, dreiecke, uv_ecken, material)))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, self.KATEGORIE, material, heben=False, wicklung=False, knochen=self.KNOCHEN)
        figur = Dazgeografthaut.grundfigur()
        hoehe = np.round(Blendimportschamhoehe.ueber_figur(roh, trimesh.Trimesh(figur['punkte'], figur['dreiecke'], process=False)), 1).tolist()
        G9stueckersatz.schreiben(bilanz['duf'], [], haut_tiefe_mm=self.HAUT_TIEFE_MM, anatomie=self.ANATOMIE, eigene_gewichte=True, hoehe_mm=hoehe)
        return bilanz

    def regler(self, quelle, stufe, kaefig, erste, faktor, stueck):
        """Je Ziel und Seite einen Morph des Stücks ablegen → `{name: weg_max_mm}`. `faktor` (3 × 3): MakeHumans Verschiebung → Meter auf Genesis (s·0,1·R)."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.kleidmorphe import G9kleidmorphe
        from scipy.spatial import cKDTree

        G9garderobe.vergessen()
        teile, kaefige, _y0, _y1, _mitte, _eintrag = G9kleidmorphe.kaefige(stueck)
        if len(teile) != 1:
            raise ValueError('%s hat %d Teile — erwartet EINS' % (stueck, len(teile)))
        grund = np.asarray(stufe.punkte(kaefig), dtype=np.float64)[erste]
        abstand, nummer = cKDTree(grund).query(kaefige[0])
        if float(abstand.max()) > self.MAX_ABSTAND_M:
            raise ValueError('Ein Punkt des Stücks liegt %.2f mm neben dem gerechneten Netz (Grenze %.1f mm)' % (abstand.max() * 1e3, self.MAX_ABSTAND_M * 1e3))
        aus = {}
        for endung, ziel, anzeige in quelle.ZIELE:
            delta = np.asarray(stufe.punkte(kaefig + quelle.ziel(ziel) @ faktor.T), dtype=np.float64)[erste] - grund
            regler = {'anzeige': '%s (MakeHuman)' % anzeige, 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'gruppe': self.REGLERGRUPPE}
            brief = G9kleidmorphe.ablegen(stueck, self.PRAEFIX + endung, [f.kennung for f, _lage in teile], [delta[nummer]],
                                          {'regler': regler, 'makehuman_ziel': ziel, 'faktor': np.round(faktor, 6).tolist()})
            aus[self.PRAEFIX + endung] = brief['weg_max_mm']
        return aus

    @staticmethod
    def _penis(stueck):
        """Die eigenen Regler des Penis (`pen_*`) einmal bauen, wie beim Daz-Geograft → `(Zahl gebaut, {Name: Grund} gescheitert)`."""
        from Genesis9.anatomien import G9anatomien

        from .dazgeograftmorphe import Dazgeograftmorphe

        gebaut, gescheitert = Dazgeograftmorphe.katalog_bauen(stueck, G9anatomien.fuer('penis'))
        return len(gebaut), gescheitert
