# -*- coding: utf-8 -*-
"""Meshfigurregler — welche Genesis-Regler „Mesh to 3D" stellt, in welcher Reihenfolge.

Edgar (27.09.2026): „vielleicht erst mal die Regler evaluieren, welche als erste kommen
(Größe, Gewicht usw.), dann die Feinregler? also eine Prio-Liste der Regler?" — und: „besonderes
Augenmerk auf das Gesicht, hier eine separate Kette". Der Reglersatz ist `charaktere` aus
`G9reglerableitung` (installierte Charaktere, Body Shapes, 200 Plus), in zwei Teilen:

KÖRPER (`teil='koerper'`, 158 Regler, gemessen 27.09.2026)
    1  Größe und Proportionen: alle `Proportion…` (Height, Beine, Arme, Rumpf, Hals, Schultern,
       Brustkorb, Hände, Füße) und `BodyMass` — was die Figur im Großen bestimmt
    2  Körpertyp und Charaktere: Bereich `figur` (Amala, Damira, Ursula …) und `koerper`
       (Charakterkörper, Heavy, Pear, Muscular, Fitness, Tone …)
    3  Körperbereiche: Brust, Taille, Hüfte, Rücken, Arme, Beine, Hals, Hände, Füße
KOPF (`teil='kopf'`, 296 Regler — die Gesichtskette)
    11 Kopfgröße, Schädel, Gesichtsproportionen, Charakterköpfe (NW Damira Head, DF-200 …)
    12 Gesichtszüge: Nase, Mund, Lippen, Augen, Brauen, Wangen, Kinn, Kiefer
    13 Ohren und alles Übrige
    0  gar nicht: `ProportionSmaller/Larger` (verkleinern die ganze Figur mit Kinderproportionen —
       doppelt zu Height), die Grundfigur selbst (steht schon auf 1, Ableitung 0), Mundhöhle,
       „Ears Gone", `HipGenitalBulge` (die Anpassung stellte ihn auf 100 %, um die Beule der Shorts
       nachzuformen — bei Edgar ein Klumpen; jetzt fest, siehe `festwerte`)

Die Ableitung kommt aus der Ablage (`G9reglerableitung.holen`, an der Grundfigur — dieselbe
Datei wie im Reiter „3D"); python10 liest `punkte`/`gelenke` direkt daraus (`ablagepfad`). Hier
entstehen nur die Begleitdaten je Runde: aktueller Wert, Grundwert, Stufe, Grenzen als Δ.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurregler']


class Meshfigurregler:
    SATZ = 'charaktere'
    SATZ_REGIONEN = 'regionen'
    GRUNDFIGUREN = {
        'feminine': {'BaseFeminine_figure_ctrl_Character': 1.0},
        'masculine': {'BaseMasculine_figure_ctrl_Character': 1.0},
        'neutral': {},
    }
    AUS = (
        'ProportionSmaller',
        'ProportionLarger',
        'BaseFeminine_figure_ctrl',
        'BaseFeminine_body_bs',
        'Mouth Cavity',
        'Ears Gone',
        'HipGenitalBulge',
    )
    #: Mimik, keine Form: Sie öffnen den Mund. Am verwaschenen Mund des TRELLIS-Netzes stellte die Anpassung
    #: `Lip Upper Gap` 0,74, `Lip Part` 0,30, `Mouth Opening M/V Shape` −1 — Mund offen, Unterlippe zurück
    #: (Testauftrag 2026.10.01.12.38.09, Befund Edgar „Unterlippe kaputt"; auf den Fotos ist der Mund zu). Gesperrt
    #: in der Anpassung (`stufe` 0) UND beim Lesen einer gespeicherten Stellung (`ohne_mimik`, von
    #: `Engine2d3dKleiderauftrag.stellung` gerufen) — so wirkt die Sperre auf alte Aufträge in Sekunden, ohne die 872 s des
    #: Körperschritts (Befund Edgar: „eine Mundanpassung muss 2–3 s dauern").
    MIMIK = ('Lip Part', 'Lip Upper Gap', 'Lip Lower Gap', 'Mouth Opening')

    @classmethod
    def ohne_mimik(cls, stellung):
        return {k: v for k, v in (stellung or {}).items() if not any(m in k for m in cls.MIMIK)}
    #: Nur auf der männlichen Grundfigur gesperrt: die Brust-Morphs der Frauenfigur. Unter dem Shirt füllten sie die
    #: Rumpftiefe (Testauftrag 2026.10.01.12.38.09: `BreastsDiameter`, `BreastsFullnessUpper` auf 1) — der Brustkorb
    #: eines Mannes kommt aus `Pectorals*`, `MassUpperTorso` und den Körpertypen.
    MAENNLICH = 'BaseMasculine_figure_ctrl_Character'
    AUS_MAENNLICH = ('body_bs_Breast',)
    #: Der Genitalbereich der Genesis-9-Grundfigur ist EIN Regler (`Hip Genital Bulge`, 0–1: bis 2,9 cm nach vorn,
    #: 170 Punkte); ein Anatomie-Paket ist nicht installiert (nur sein UV-Satz). Für die männliche Grundfigur steht
    #: er fest auf `genitalform` % der Optionen, sonst auf 0.
    GENITAL_REGLER = 'body_bs_HipGenitalBulge'
    GENITAL_VORGABE = 30
    KOPF_GROSS = ('ProportionHeadSize', 'Cranium', 'Face ', 'ForeHead', 'Jaw Height', 'Head Shape')
    KOPF_ZUEGE = (
        'Nose',
        'Mouth',
        'Lip',
        'Eyes',
        'Eye ',
        'Brow',
        'Cheek',
        'Chin',
        'Jaw',
        'Temple',
        'Philtrum',
        'Nostril',
        'Smile',
    )
    #: Kleinere Werte werden 0 (wie `G9formanpassung.NULL_UNTER`).
    NULL_UNTER = 0.005

    def __init__(self, grund, gesperrt=None, satz=None, spielraum=1.0):
        #: Der Reglersatz der Ableitung: `charaktere` oder `regionen` (dazu die Regionen-Regler, `G9koerperregionen`, Option `koerper.regionen`).
        self.satz = satz or self.SATZ
        #: Faktor auf Dazʼ Grenze für die Körperregler mit Spielraum (`G9reglergrenzen`, Option `koerper.spielraum`): 1 = wie Daz, höchstens `SPIELRAUM`.
        self.spielraum = max(1.0, float(spielraum or 1.0))
        self._grenzen_gemerkt = {}
        #: Die Grundfigur (`GRUNDFIGUREN[...]`) — Ort der Ableitung und Ziel der Dämpfung.
        self.grund = dict(grund or {})
        #: Marken gesperrter Regler (`sperrmarken`): Testfall „blind" — die Charakterregler der
        #: Referenzfigur darf die Anpassung nicht benutzen, sonst misst der Test nur, ob sie sie findet.
        self.gesperrt = list(gesperrt or [])

    @classmethod
    def festwerte(cls, optionen):
        """`{regler: wert}`, die ab der ersten Runde in der Stellung stehen und die Kette nicht ändert (Stufe 0)."""
        if (optionen or {}).get('basis') != 'masculine':
            return {}
        prozent = float((optionen or {}).get('genitalform', cls.GENITAL_VORGABE))
        wert = round(min(max(prozent / 100.0, 0.0), 1.0), 4)
        return {cls.GENITAL_REGLER: wert} if wert >= cls.NULL_UNTER else {}

    @staticmethod
    def marke(name):
        return ''.join(c for c in str(name).split('-0x')[0].lower() if c.isalnum())

    @classmethod
    def sperrmarken(cls, regler):
        """Aus den Reglern eines Katalogeintrags (`NWDamira_figure_ctrl_Character-0x…`) die Marken
        seiner Charakterregler (`nwdamira` trifft `NW Damira Body`, `NW Damira Head`, `… Abs I`)."""
        aus = []
        for name in regler:
            if '_figure_ctrl_Character' in name:
                aus.append(cls.marke(name.split('_figure_ctrl_Character')[0]))
        return [m for m in aus if len(m) >= 3]

    def stufe_fuer(self, name, bereich, teil):
        if any(m in self.marke(name) for m in self.gesperrt):
            return 0
        if self.MAENNLICH in self.grund and any(a in name for a in self.AUS_MAENNLICH):
            return 0
        return self.stufe(name, bereich, teil)

    # --------------------------------------------------------------- Stufen

    @classmethod
    def stufe(cls, name, bereich, teil):
        if any(a in name for a in cls.AUS + cls.MIMIK):
            return 0
        if teil == 'kopf':
            # Charakterköpfe: `<X>_head_bs_Head`, `MB_Olesia_Head_bs_head-0x…`, `NW Damira Head-0x…`,
            # `DF-200KumikoHead` — der Name (ohne Daz' `-0x…`-Anhang) endet auf „head".
            if name.split('-0x')[0].lower().endswith('head'):
                return 11
            if any(k in name for k in cls.KOPF_GROSS):
                return 11
            if any(k in name for k in cls.KOPF_ZUEGE):
                return 12
            return 13
        if 'Proportion' in name or name.startswith('body_bs_BodyMass'):
            return 1
        if bereich in ('figur', 'koerper') and 'Abs ' not in name:
            return 2
        return 3

    # ---------------------------------------------------------------- Daten

    def ableitung(self, teil):
        from Genesis9.reglerableitung import G9reglerableitung

        return G9reglerableitung.holen(self.satz, self.grund, teil=teil)

    def grenzen(self, teil):
        """(K, 2) Grenzen der Variablen von `teil`: Dazʼ Grenzen, bei Reglern mit Spielraum (`weit_max` im Plan) × `spielraum`."""
        a = self.ableitung(teil)
        if self.spielraum <= 1.0:
            return a.grenzen
        if teil not in self._grenzen_gemerkt:
            from Genesis9.reglerableitung import G9reglerableitung
            from Genesis9.reglergrenzen import G9reglergrenzen

            faktor = min(self.spielraum, G9reglergrenzen.SPIELRAUM)
            plan = {r['name']: r for r in G9reglerableitung.regler(self.satz, teil=teil)}
            g = np.array(a.grenzen, dtype=np.float64)
            for i, v in enumerate(a.namen):
                r = plan.get(a.paare[v][0])
                # Nur die Körperbereiche (Stufe 3: Hals, Arme, Beine, Gesäß …) — Körpertypen und Charaktere auf 200 % wären ein anderer Körper, und das Tor soll genau das melden.
                if r is not None and 'weit_max' in r and self.stufe_fuer(v, r.get('bereich'), teil) == 3:
                    g[i] *= faktor
            self._grenzen_gemerkt[teil] = g
        return self._grenzen_gemerkt[teil]

    def daten(self, teil, stellung):
        """Begleitdaten der Ableitung von `teil` für die Stellung dieser Runde."""
        from Genesis9.reglerableitung import G9reglerableitung

        a = self.ableitung(teil)
        g = self.grenzen(teil)
        bereich = {r['name']: r.get('bereich') for r in G9reglerableitung.regler(self.satz, teil=teil)}
        jetzt = np.array([float(stellung.get(a.paare[v][0], 0.0)) for v in a.namen])
        grund = np.array([float(self.grund.get(a.paare[v][0], 0.0)) for v in a.namen])
        stufen = np.array([self.stufe_fuer(v, bereich.get(a.paare[v][0]), teil) for v in a.namen], np.int64)
        return {
            'quelle': np.array(str(G9reglerableitung.ablagepfad(self.satz, self.grund, teil))),
            'namen': np.array(a.namen),
            'jetzt': jetzt.astype(np.float32),
            'grund': grund.astype(np.float32),
            'stufe': stufen,
            'unten': (g[:, 0] - jetzt).astype(np.float32),
            'oben': (g[:, 1] - jetzt).astype(np.float32),
        }

    def speichern(self, pfad, teil, stellung):
        daten = self.daten(teil, stellung)
        np.savez(pfad, **daten)
        return {int(s): int((daten['stufe'] == s).sum()) for s in np.unique(daten['stufe'])}

    # ------------------------------------------------------------ Ergebnis

    def stellung(self, teil, werte, alt):
        """Die neue Reglerstellung: `alt` plus die Werte der Variablen von `teil` (Paare auf
        beide Seiten), auf die Grenzen geklemmt, Kleinstwerte auf 0."""
        a = self.ableitung(teil)
        g = self.grenzen(teil)
        aus = dict(alt)
        for i, v in enumerate(a.namen):
            if v not in werte:
                continue
            wert = float(np.clip(werte[v], g[i, 0], g[i, 1]))
            for r in a.paare[v]:
                if abs(wert) < self.NULL_UNTER:
                    aus.pop(r, None)
                else:
                    aus[r] = round(wert, 5)
        return aus

    def geaendert(self, stellung, schwelle=0.01):
        """`[[regler, wert], …]` — was von der Grundfigur abweicht, nach Betrag absteigend."""
        aus = [
            [k, round(float(v), 4)]
            for k, v in stellung.items()
            if abs(float(v) - float(self.grund.get(k, 0.0))) > schwelle
        ]
        return sorted(aus, key=lambda kv: -abs(kv[1]))
