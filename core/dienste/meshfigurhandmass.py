# -*- coding: utf-8 -*-
"""Meshfigurhandmass — die Hände der Figur so groß wie die Hände im Netz (14.10.2026, Edgar1: „Hände … sind etwas kleiner als das Mesh“).

Befund (gemessen an Edgar3, `ProjektTemp/_wegwerf/mesh3d/hand_groesse_messen.py`): die Figurhand ist 18,3 cm lang, die Hand im Netz (Flächen, die Sapiens als Hand sieht) 19,7 (rechts) und 20,4 cm (links) — 8 bis 10 % kürzer. Ursache: die Anpassung gewichtet
die Hand mit 0,1 (`Meshfigurabstand.GEWICHT`), und Genesis' `Proportion Height` verkleinert Hände und Füße gegen den Körper (−10 % bei +100 %, `genesis9.md`); das Netz wird auf 2,0 m gesetzt (`Blendimportnetz.SOLL_M`), die Figur wächst mit.
Die Größe der Hand gehört nicht in die Anpassung (Fäuste und verklebte Finger formten dort die Figur), sondern ist EIN Regler: `body_ctrl_ProportionHandSize` skaliert Hand und Finger gleichmäßig um das Handgelenk (±0,5 → ×1,23 / ×0,76, `handregler_eichen.py`; `MassHands` und `FingersWidth` ändern die Länge nicht).

Hier: Länge der Hand im Netz (Ausdehnung der Handpunkte entlang ihrer Hauptachse, 2. bis 98. Perzentil — wie bei der Figur, die Pose ändert sie nicht) gegen die der Figur; der Regler wird so gesetzt, dass beide gleich lang sind. Nur wenn ALLE Hände im Netz plausibel offen
sind (Verhältnis in `PLAUSIBEL`; eine Faust ist kürzer, Sapiens' Etikett fließt auf Handschuh und Ärmel) und einig (`UNEINIG`); sonst bleibt die Figurhand, wie sie ist. Der Mittelwert beider Hände gilt (die Figur ist symmetrisch).
Gemessen an den Testaufträgen (14.10.2026, `handmass_probe.py`): Edgar 1,080 / 1,119 → ×1,099 (Hand 18,3 → 20,1 cm); Ballerina 1,258 / 1,148 und Polstertänzer 1,418 / 1,149 → unverändert (eine Hand im Etikettenüberlauf).
Läuft am Ende der Körperkette (`Meshfigurkette.koerper`), damit Gesicht, Rest, Textur und alles danach dieselbe Hand sehen. Wirft nie — ein Zusatz; `ergebnis.handmass` nennt Maße und Grund.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurhandmass']


class Meshfigurhandmass:
    REGLER = 'body_ctrl_ProportionHandSize'
    #: Verhältnis Länge der Netzhand ÷ Länge der Figurhand, das als „offene Hand“ gilt. Edgar: 1,07 und 1,11. Darunter liegt die Faust (Netzhand deutlich kürzer), darüber ein Sapiens-Etikett, das auf den Arm fließt.
    PLAUSIBEL = (0.92, 1.20)
    #: Der Regler bleibt in diesem Rahmen (±0,5 sind ×1,23 / ×0,76).
    GRENZE = 0.5
    #: Zwei Hände im Netz gelten als einig, wenn ihre Verhältnisse höchstens diesen Anteil ihres Mittels auseinanderliegen (Edgar 1,080 und 1,119: 3,6 %).
    UNEINIG = 0.08
    #: Eine Hand im Netz zählt ab dieser Fläche (cm²) — kleinere Inseln sind Etikettenreste — und Flächen, deren Mitten höchstens so weit (m) auseinanderliegen, gehören zur selben Hand.
    MIN_CM2 = 40.0
    NAEHE_M = 0.02

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    @classmethod
    def sicher(cls, lauf, stellung):
        """Rechnen und `stellung` ändern; wirft nie. Gibt den Bericht zurück (auch unter `ergebnis.handmass`)."""
        try:
            bericht = cls(lauf).anwenden(stellung)
        except Exception as fehler:  # noqa: BLE001 — die Figur behält ihre Hände, der Grund steht im Ergebnis und im Log
            logger.exception('Mesh to 3D %s: Handmaß gescheitert', lauf.job.kennung)
            bericht = {'fehler': str(fehler)[:300]}
        lauf.job.ergebnis['handmass'] = bericht
        return bericht

    # ---------------------------------------------------------------- Messen

    @staticmethod
    def laenge(punkte):
        """Ausdehnung (m) von `punkte` entlang ihrer Hauptachse, 2. bis 98. Perzentil (robust gegen einzelne Fäden)."""
        p = np.asarray(punkte, dtype=np.float64)
        m = p.mean(axis=0)
        _, _, vt = np.linalg.svd(p - m, full_matrices=False)
        q = (p - m) @ vt[0]
        return float(np.percentile(q, 98) - np.percentile(q, 2))

    def haende_im_netz(self):
        """`[Punkte (n, 3), …]` der höchstens zwei größten zusammenhängenden Handstücke im Netz (Flächen, die Sapiens als Hand sieht); leer ohne Etiketten."""
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        from scipy.spatial import cKDTree

        from .meshfigurhalter import Meshfigurhalter
        from .meshfigurkleidung import Meshfigurkleidung

        pfad = self.ablage.arbeit('sapiens_flaechen.npz')
        if not pfad.is_file():
            return []
        scan, _ = Meshfigurkleidung(self.lauf).koerpernetz()
        with np.load(pfad) as d:
            klassen = np.asarray(d['klassen'])
        if len(klassen) != len(scan.flaechen):
            return []
        ids = np.flatnonzero((klassen.max(axis=1) >= Meshfigurhalter.MIN_STIMMEN) & np.isin(klassen.argmax(axis=1), Meshfigurhalter.HAND_KLASSEN))
        if len(ids) < 100:
            return []
        flaechen = np.asarray(scan.flaechen)[ids]
        # Gruppen nach NÄHE der Flächenmitten, nicht über Kanten: Sapiens' Handfläche zerfällt im Netz in 553 Stücke (Edgar3, größtes 73 cm²); mit 2 cm Abstand bleiben genau zwei übrig (19,7 und 20,4 cm lang, je ~230 cm²).
        mitten = np.asarray(scan.punkte)[flaechen].mean(axis=1)
        paare = cKDTree(mitten).query_pairs(self.NAEHE_M, output_type='ndarray')
        n, teil = connected_components(coo_matrix((np.ones(len(paare)), (paare[:, 0], paare[:, 1])), shape=(len(ids), len(ids))), directed=False)
        cm2 = np.bincount(teil, weights=scan.flaecheninhalte()[ids], minlength=n) * 1e4
        stuecke = [k for k in np.argsort(cm2)[::-1][:2] if cm2[k] >= self.MIN_CM2]
        return [np.asarray(scan.punkte)[np.unique(flaechen[teil == k].reshape(-1))] for k in stuecke]

    @staticmethod
    def figurhand(stellung):
        """`(Länge (m) der Käfighand, Punkte)` für jede Hand der Figur dieser Stellung (Ruhelage); die Pose ändert die Länge nicht."""
        from Genesis9.formung import G9formung
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.reglerableitung import G9reglerableitung

        punkte, _, _ = G9reglerableitung.lage(G9formung(stellung))
        teil = G9koerperteile.genesis_punkte(G9haut.holen())
        return [np.asarray(punkte)[teil == G9koerperteile.NUMMER[s + '_hand']] for s in ('l', 'r')]

    # ---------------------------------------------------------------- Anwenden

    def anwenden(self, stellung):
        """Setzt `body_ctrl_ProportionHandSize` in `stellung` (an Ort und Stelle) und gibt den Bericht zurück."""
        if (self.job.optionen or {}).get('handmass') == 'aus':
            return {'aus': True}
        im_netz = self.haende_im_netz()
        if not im_netz:
            return {'hinweis': 'Keine Hand im Netz erkannt (Sapiens-Etiketten fehlen oder zu klein)'}
        netz = [self.laenge(p) for p in im_netz]
        figur = [self.laenge(p) for p in self.figurhand(stellung)]
        mittel_figur = float(np.mean(figur))
        verhaeltnisse = [laenge_netz / mittel_figur for laenge_netz in netz]
        bericht = {'netz_cm': [round(x * 100, 1) for x in netz], 'figur_cm': [round(x * 100, 1) for x in figur],
                   'verhaeltnis': [round(v, 3) for v in verhaeltnisse], 'regler_vorher': round(float(stellung.get(self.REGLER, 0.0)), 4)}
        # ALLE gemessenen Hände müssen plausibel und einig sein: eine Hand im Handschuh oder Ärmel (Sapiens' Etikett fließt auf den Stoff: Ballerina 1,26 gegen 1,15, Polstertänzer 1,42 gegen 1,15) macht die Messung der anderen unsicher.
        if not all(self.PLAUSIBEL[0] <= v <= self.PLAUSIBEL[1] for v in verhaeltnisse):
            bericht['hinweis'] = 'Eine Hand im Netz ist keine offene Hand (Verhältnis %s außerhalb %s): die Figur behält ihre Hand' % (bericht['verhaeltnis'], self.PLAUSIBEL)
            return bericht
        if len(verhaeltnisse) > 1 and (max(verhaeltnisse) - min(verhaeltnisse)) > self.UNEINIG * float(np.mean(verhaeltnisse)):
            bericht['hinweis'] = 'Die Hände im Netz sind verschieden lang (Verhältnis %s, mehr als %.0f %% auseinander): die Figur behält ihre Hand' % (bericht['verhaeltnis'], 100 * self.UNEINIG)
            return bericht
        ziel = float(np.mean(verhaeltnisse))
        # Länge ist linear im Regler: zwei Stützstellen statt einer Annahme über die Steigung.
        alt = float(stellung.get(self.REGLER, 0.0))
        schritt = 0.25
        l0 = float(np.mean([self.laenge(p) for p in self.figurhand(stellung)]))
        l1 = float(np.mean([self.laenge(p) for p in self.figurhand({**stellung, self.REGLER: alt + schritt})]))
        steigung = (l1 - l0) / schritt
        neu = float(np.clip(alt + (ziel * l0 - l0) / steigung, -self.GRENZE, self.GRENZE))
        stellung[self.REGLER] = neu
        lange_danach = float(np.mean([self.laenge(p) for p in self.figurhand(stellung)]))
        bericht.update(regler_nachher=round(neu, 4), faktor=round(ziel, 3), figur_nachher_cm=round(lange_danach * 100, 1))
        logger.info('Mesh to 3D %s: Handmaß — Hand im Netz %s cm, Figur %s → %.1f cm (Regler %.3f → %.3f)', self.job.kennung, bericht['netz_cm'], bericht['figur_cm'], lange_danach * 100, alt, neu)
        return bericht
