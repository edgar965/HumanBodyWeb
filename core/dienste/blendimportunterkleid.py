# -*- coding: utf-8 -*-
"""Blendimportunterkleid — die Haut der Figur hinter die Kleidung legen, wo „Mesh to 3D" sie davor stehen lässt (10.10.2026).

Edgar, 10.10.2026, mit Bild (Rainy, „Rainy Hose (Genesis 9)"): „die Haut geht durch die Hose. Du hast ja die Haut nachgebaut,
wahrscheinlich Fehler in der Konstruktion der Scham?" Gemessen am Import 2026.10.10.14.29.08 (`ProjektTemp/_wegwerf/blendimport_massstab/
rainy_schritt.py`, `rainy_schritt_lesen.py`, `rainy_schritt_sicht.py`; Hose und Haut in der Ruhelage der Figur, von vorn gesehen):

* Die Hose ist am Schritt geschlossen — sie hat nur drei offene Ränder (Bund und zwei Säume). Es fehlt dort kein Stoff.
* Die Haut der Figur ist am Schritt 16 mm tiefer als die Hose (y 0,784 gegen 0,800 m) und steht an der Schambeinwölbung VOR ihr:
  von 1.917 nach vorn gerichteten Hautpunkten (|x| < 12 cm, y 0,70–1,00 m) liegen 664 vor der vordersten Hosenfläche, 295 davon mehr als
  10 mm, höchstens 62,2 mm (Mitte, y 0,88 m: Hose z +0,021, Haut z +0,071).
* Mit dem Scham-Stück (`Blendimportscham`) hat das nichts zu tun: es entfällt bei Rainy („nur 0 Originalpunkte weichen mehr als 5 mm ab") —
  der Originalkörper endet bei 0,911 m (`koerper_z` im Stand), über dem Schritt. Die Haut dort ist die Standardhaut von Genesis 9, so,
  wie „Mesh to 3D" sie liegen ließ.

Warum „Mesh to 3D" die Stelle liegen lässt, ist nicht durch einen Lauf geprüft. Im Code gilt für den Genitalbereich Gewicht 0,1 und kein
Zug des Stoffs (`Meshfigurabstand.GEWICHT[SCHRITT]`, `kleid_zieht`, `meshfigur_abstand.py`) — gewollt seit 29.09.2026, damit die Figur
die Beule von Shorts nicht nachformt. Das ist für Fotos richtig; der Import kennt die Kleidung aber genau (sie ist als Stück in der Hand)
und prüft hier selbst, was „Mesh to 3D" dort offen lässt.

WAS HIER GESCHIEHT — derselbe Weg wie `Blendimportnachformung` (EIGENER Regler neben dem Eigenmorph, Wert 1 = hinter der Kleidung, 0 = wie
die Anpassung): Die Kleider (Rolle „kleid", ohne Schuhe und Requisiten) kommen in die Ruhelage der Figur (`Blendimportlage.stueck_ruhelage`,
wie beim Bau der Stücke) und werden zu EINER Hülle. Im Kasten am Becken wird für jeden Hautpunkt von vorn gesehen (Strahl in −z) die
vorderste Kleiderfläche in seiner Spalte gesucht — das ist, was der Browser mit dem Tiefenpuffer zeigt. Liegt der Punkt davor, und die
Fläche höchstens `MAX_M` hinter ihm, geht er `LUFT_M` hinter sie. Die Verschiebung der Käfigpunkte, geglättet (`G9restmorph.glaetten`),
kommt als Zusatz auf den Käfig; vier Durchgänge mit Entspannung 0,8.

Hinter dem Hemd eines nackten Bauchs liegt die Rückseite des Hemds mehr als `MAX_M` entfernt: dort geschieht nichts.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportunterkleid']


class Blendimportunterkleid:
    #: Kasten wie bei der Nachformung: Höhe als Anteil der Körperhöhe über der Sohle (von, bis), halbe Breite in m bei 1,75 m Körperhöhe;
    #: nur die Vorderseite. Rainy: Haut vor der Hose bei y 0,70–0,99 m (0,42–0,59 der Höhe 1,677 m) und x −0,07…+0,12 m (gemessen, s. o.);
    #: oben bis 0,64 (1,07 m, unter dem Bund bei 1,106 m), damit die Verschiebung dort ausläuft statt an der Kastenkante abzubrechen.
    HOEHE = (0.40, 0.64)
    BREITE_M = 0.12
    #: So weit (m) hinter der vordersten Kleiderfläche soll die Haut liegen — die Stoffdicke, die auch `Blendimportkoerperergaenzung.DICKE_M`
    #: von den Beinen abzieht.
    LUFT_M = 0.003
    #: Liegt die vorderste Kleiderfläche weiter als das hinter dem Hautpunkt (m), ist es ein anderes Teil (Rückseite eines Hemds) und der Punkt bleibt.
    MAX_M = 0.08
    #: Wie `Blendimportnachformung`: Durchgänge, Anteil der Verschiebung je Durchgang, Glättung (Schritte, Anteil).
    DURCHGAENGE = 4
    ENTSPANNUNG = 0.8
    GLAETTEN = (3, 0.5)
    #: Ab so viel (m) vor der Kleiderfläche zählt ein Hautpunkt im Bericht als „davor".
    MELDEN_AB_M = 0.0005
    #: Der Regler heißt `eigen:<Eigenmorph>_unterkleid` — `Blendimportlauf._unterkleid` erkennt an der Endung den eigenen Regler eines früheren Laufs.
    ENDUNG = '_unterkleid'

    def __init__(self, ablage, job, inventar, rollen, figurname, melden=None):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.figurname = figurname
        self.melden = melden or (lambda anteil, text: None)

    # ------------------------------------------------------------- Bausteine

    @classmethod
    def kasten(cls, punkte, sohle, hoehe):
        """Maske der Punkte (Ruhelage, Y oben, Z nach vorn) im Kasten am Becken — nur die Vorderseite."""
        unten, oben = sohle + cls.HOEHE[0] * hoehe, sohle + cls.HOEHE[1] * hoehe
        breit = cls.BREITE_M * hoehe / 1.75
        return ((punkte[:, 1] > unten) & (punkte[:, 1] < oben) & (np.abs(punkte[:, 0]) < breit)
                & (punkte[:, 2] > float(np.median(punkte[:, 2]))))

    @classmethod
    def vorderste(cls, huelle, punkte, maske):
        """`(N,)` z der vordersten Kleiderfläche in der Spalte (x, y) jedes Punkts in `maske`, von vorn gesehen — `-inf` ohne Kleidung dort
        und außerhalb der Maske. `huelle`: `trimesh.Trimesh` aller Kleider in der Ruhelage."""
        aus = np.full(len(punkte), -np.inf)
        idx = np.flatnonzero(maske)
        if not len(idx) or huelle is None:
            return aus
        vor = float(max(punkte[idx, 2].max(), huelle.vertices[:, 2].max())) + 0.1
        herkunft = np.column_stack([punkte[idx, 0], punkte[idx, 1], np.full(len(idx), vor)])
        ort, strahl, _ = huelle.ray.intersects_location(herkunft, np.tile([0.0, 0.0, -1.0], (len(idx), 1)), multiple_hits=True)
        vorn = np.full(len(idx), -np.inf)
        if len(strahl):
            np.maximum.at(vorn, strahl, ort[:, 2])
        aus[idx] = vorn
        return aus

    @classmethod
    def verschiebung(cls, haut, huelle, maske):
        """`(N, 3)`: je Punkt in `maske`, der von vorn gesehen VOR der Kleiderfläche liegt (und höchstens `MAX_M` davor), der Weg in −z
        bis `LUFT_M` hinter sie; alles andere bleibt 0."""
        aus = np.zeros((len(haut), 3))
        vorn = cls.vorderste(huelle, haut, maske)
        ueber = haut[:, 2] - vorn                                  # > 0: die Haut steht vor der vordersten Kleiderfläche
        schieben = np.isfinite(vorn) & (ueber > 0.0) & (ueber <= cls.MAX_M)
        aus[schieben, 2] = vorn[schieben] - cls.LUFT_M - haut[schieben, 2]
        return aus

    @classmethod
    def sicht(cls, haut, huelle, maske):
        """Bericht: Punkte im Kasten, davon mit Kleidung in der Spalte, davon vor ihr (ab `MELDEN_AB_M`, höchstens `MAX_M`) mit größtem Überstand (mm)
        und `weit`: Punkte, deren vorderste Kleiderfläche mehr als `MAX_M` dahinterliegt (nackte Haut vor einem Rücken — bleibt unberührt)."""
        vorn = cls.vorderste(huelle, haut, maske)
        ueber = (haut[:, 2] - vorn)[np.isfinite(vorn)]
        davor = ueber[(ueber > cls.MELDEN_AB_M) & (ueber <= cls.MAX_M)]
        return {'punkte': int(maske.sum()), 'mit_kleidung': int(len(ueber)), 'davor': int(len(davor)),
                'davor_max_mm': round(float(davor.max()) * 1000.0, 1) if len(davor) else 0.0, 'weit': int((ueber > cls.MAX_M).sum())}

    @classmethod
    def zu_huelle(cls, teile):
        """Eine `trimesh.Trimesh` aus `[(Punkte, Dreiecke), …]` — oder None ohne Teile."""
        import trimesh

        if not teile:
            return None
        versatz = np.cumsum([0] + [len(p) for p, _ in teile[:-1]])
        return trimesh.Trimesh(np.vstack([p for p, _ in teile]), np.vstack([d + int(v) for (_, d), v in zip(teile, versatz, strict=True)]),
                               process=False)

    def huelle(self, lage):
        """Die Kleider (ohne Schuhe und Requisiten) in der Ruhelage der Figur als eine Fläche — wie `Blendimportstuecke.stueck` sie legt."""
        from .blendimportrequisit import Blendimportrequisit
        from .blendimportteile import Blendimportteile

        teile = []
        for rolle in self.rollen:
            if rolle['rolle'] != 'kleid' or rolle['name'] not in self.inventar or rolle.get('ordner') == 'shoes':
                continue
            with np.load(self.ablage.export(self.inventar[rolle['name']]['datei'])) as d:
                punkte, dreiecke = np.asarray(d['punkte']), np.asarray(d['dreiecke'], dtype=np.int64)
            if Blendimportrequisit(lage).erkennen(punkte):
                continue
            erlaubt = Blendimportteile.erlaubt(rolle.get('ordner'), '%s %s' % (rolle['name'], rolle.get('art', '')))
            teile.append((np.asarray(lage.stueck_ruhelage(punkte, dreiecke, erlaubt), dtype=np.float64), dreiecke))
        return self.zu_huelle(teile)

    # ----------------------------------------------------------------- Lauf

    def feld(self, zusatzregler=None):
        """`(Zusatzfeld (Käfigpunkte, 3) oder None, Bericht)` — die Rechnung ohne Ablage des Reglers (Probe)."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.restmorph import G9restmorph

        from .blendimportlage import Blendimportlage

        lage = Blendimportlage(self.job, zusatzregler)
        huelle = self.huelle(lage)
        if huelle is None:
            return None, {'aus': 'kein Kleid in der Ruhelage'}
        stufe = G9basisnetz.holen().netzstufe(1)
        anzahl = len(G9basisnetz.holen().punkte)
        kaefig0 = np.asarray(G9reglerableitung.lage(G9formung(lage.stellung()))[0], dtype=np.float64)
        zusatz = np.zeros_like(kaefig0)
        bericht = {}
        for durchgang in range(self.DURCHGAENGE + 1):
            haut = np.asarray(stufe.punkte(kaefig0 + zusatz), dtype=np.float64)
            maske = self.kasten(haut, float(haut[:, 1].min()), float(haut[:, 1].max() - haut[:, 1].min()))
            if not maske.any():
                return None, {'aus': 'kein Hautpunkt im Kasten'}
            if durchgang == 0:
                bericht['vorher'] = self.sicht(haut, huelle, maske)
            if durchgang == self.DURCHGAENGE:
                bericht['nachher'] = self.sicht(haut, huelle, maske)
                break
            rest = self.verschiebung(haut, huelle, maske)[:anzahl]
            if not np.linalg.norm(rest, axis=1).any():
                # Kein Käfigpunkt steht mehr vor der Kleidung (ein Rest an Zwischenpunkten der Fläche bleibt): gemessen wird die Haut, wie sie jetzt liegt.
                bericht['nachher'] = self.sicht(haut, huelle, maske)
                break
            zusatz = zusatz + self.ENTSPANNUNG * G9restmorph.glaetten(rest, (np.linalg.norm(rest, axis=1) > 0).astype(float), *self.GLAETTEN)
            self.melden(0.96, 'Haut unter die Kleidung')
        bericht['zusatz_max_mm'] = round(float(np.linalg.norm(zusatz, axis=1).max()) * 1000.0, 1)
        return (zusatz if bericht['zusatz_max_mm'] > 0.0 else None), bericht

    def formen(self, zusatzregler=None):
        """Bericht (mit `regler`: der neue Eigenmorph-Regler `{eigen:…: 1.0}`) oder `{'aus': Grund}`. `zusatzregler`: die Regler der
        Nachformung der Scham, auf deren Figur die Haut hier gelegt wird."""
        from Genesis9.eigenmorphe import G9eigenmorphe

        from .blendimportnachformung import Blendimportnachformung

        reglername = ((self.job.ergebnis or {}).get('rest') or {}).get('regler')
        if not reglername or not G9eigenmorphe.vorhanden(reglername):
            return {'aus': 'Mesh to 3D hat keinen Eigenmorph geschrieben'}
        zusatz, bericht = self.feld(zusatzregler)
        if zusatz is None or bericht['vorher']['davor'] == 0:
            return dict(bericht, **({'aus': 'keine Haut vor der Kleidung'} if 'aus' not in bericht else {}))
        nummern, deltas = Blendimportnachformung.zusammenfuehren(None, None, zusatz)
        kennung = reglername[len(G9eigenmorphe.PRAEFIX):]
        brief = {'anzeige': '%s · Haut unter Kleidung' % self.figurname, 'nachformung': bericht}
        bericht['regler'] = {G9eigenmorphe.ablegen(kennung + self.ENDUNG, nummern, deltas, brief): 1.0}
        logger.info('Blender-Import %s: Haut unter die Kleidung %s', self.ablage.kennung, bericht)
        return bericht
