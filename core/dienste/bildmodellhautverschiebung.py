# -*- coding: utf-8 -*-
"""Bildmodellhautverschiebung — Alter, Tonus und Masse als Verschiebungskacheln des Genesis-9-Modells.

WARUM (Edgar, 21.09.2026: „wenn ich Gewicht, Alter, Tonus usw. angebe, wird das im
Modell berücksichtigt?" — „mach auch die Änderungen Alter/tonus/masse bei Textur"):
Die Daz Starter Essentials haben keinen Regler für Alter oder Tonus; im
Bildmodell standen die Werte nur am Auftrag. MB-Lab (HumanBody) rechnet aus den
dreien seine Displacement-Textur (`Verschiebungstextur`, `Hautverschiebung`:
Poren + Alter·Falten + Tonus·Muskeln + Masse·Fett, 2048², ±5 mm entlang der
Normale) — aber im UV-Raum des HumanBody-Netzes. Hier wird sie in die UDIM-
Kacheln von Genesis 9 umgesetzt (`Hbdreiecksuche` findet den Oberflächenpunkt):

    Texel der Kachel (`G9texturabtastung`: Dreieck + Anteile) → Lage auf dem Käfig
    → HumanBody-Lage (Paarung `G9aufhumanbody`, `skaliert` je Browserpunkt, je
    Körperteil) → nächster Punkt auf den HumanBody-Dreiecken dieses Teils
    (Kandidaten nach Schwerpunkt, dann exakt) → baryzentrisch die UV der Dreiecks-
    ECKEN (`uv_loops`, an Nähten je Insel richtig) → bilinear aus der MB-Lab-Textur.
    Außerhalb der Inseln 0,5 (keine Verschiebung), Inselrand um `RAND_PX` nach
    außen gezogen wie bei den Farbkacheln. Erster Ansatz über die drei nächsten
    PUNKTE gab Zellen (Voronoi-Flecken, 34 % Rückfall) — verworfen.

Die Reglerwerte kommen wie in HumanBody zustande (`templates/_koerpermasse.html`,
`viewer/metawerte.js`: Regler 18–100 Jahre, 45–200 kg, 0–100 % Tonus → −1..+1 um
die Mitte); negative Faktoren zählen in MB-Lab nicht (dünn = kein Fett). Der
Browser hängt die Kachel als `displacementMap` ein (`texturauflage.js`, Stärke
0,01 m, Bias −0,005 wie `hauttextur.js`). Die Grundfigur ist die weibliche Paarung
wie bei den HB-Morphs (`Hbmorpheaufgenesis.GESCHLECHT`).
"""
import logging
import os
import time

import numpy as np

from .hbdreiecksuche import Hbdreiecksuche

logger = logging.getLogger('core')

__all__ = ['Bildmodellhautverschiebung']


class Bildmodellhautverschiebung:
    """Je UDIM-Kachel ein 8-Bit-Graustufen-PNG `verschiebung_<kachel>.png`."""

    GESCHLECHT = 'female'
    PRAEFIX = 'verschiebung'
    #: Kachelseite: die MB-Lab-Quelle hat 2048² für den GANZEN Körper (Kopf ~512²) — 1024² je
    #: UDIM-Kachel verliert nichts und rechnet viermal schneller (2048²: 35 s je Kachel).
    SEITE = 1024
    RAND_PX = 6
    MITTE = 0.5
    #: Reglerbereiche von HumanBody: (Feld, min, max) → Kernwert (wert − mitte) / halbe Spanne.
    SPANNEN = {'age': ('alter', 18.0, 100.0), 'mass': ('gewicht_kg', 45.0, 200.0),
               'tone': ('tonus', 0.0, 100.0)}

    def __init__(self, person, seite=None):
        self.person = person if isinstance(person, dict) else {}
        self.seite = seite
        self._netz = None

    # ------------------------------------------------------------ Werte

    @classmethod
    def metawerte(cls, person):
        """`{age, tone, mass}` in −1..1 aus `person` — fehlende Angaben sind 0 (Mitte)."""
        person = person if isinstance(person, dict) else {}
        aus = {}
        for name, (feld, klein, gross) in cls.SPANNEN.items():
            wert = person.get(feld)
            if wert is None or wert == '':
                aus[name] = 0.0
                continue
            mitte, halb = (klein + gross) / 2.0, (gross - klein) / 2.0
            aus[name] = round(float(min(max((float(wert) - mitte) / halb, -1.0), 1.0)), 2)
        return aus

    @classmethod
    def gleich(cls, person, bericht):
        """Stimmen die Werte eines früheren Backens (`verschiebung_werte`) mit `person` überein?"""
        if not isinstance(bericht, dict):
            return False
        neu = cls.metawerte(person)
        return all(abs(float(bericht.get(k, 99)) - v) < 1e-6 for k, v in neu.items())

    # ------------------------------------------------------- Vorbereiten

    def _vorbereiten(self):
        """HumanBody-Dreiecke mit UV-Ecken, Käfig in HumanBody-Lage, Suche je Körperteil."""
        if self._netz is not None:
            return self._netz
        from GarmentCode.webbruecke import charakterdaten
        from Genesis9.basisnetz import G9basisnetz

        from .g9aufhumanbody import G9aufhumanbody
        from .hbtraeger import Hbtraeger

        netz = charakterdaten().netzdaten(self.GESCHLECHT)
        if getattr(netz, 'uv_loops', None) is None or netz.faces is None:
            raise ValueError('HumanBody-Netz ohne UV-Ecken (uv_loops.npy) — keine Verschiebungskacheln')
        flaechen = np.asarray(netz.faces, dtype=np.int64)                  # (F, 4)
        uv_ecken = np.asarray(netz.uv_loops, dtype=np.float64)             # (F, 4, 2)
        hb = Hbtraeger.laden(self.GESCHLECHT, None, {}, {})
        paar = G9aufhumanbody.paarung_holen(self.GESCHLECHT, None)
        basis = G9basisnetz.holen()
        ursprung = np.asarray(basis.netzstufe(0).ursprung, dtype=np.int64)
        zahl = len(basis.punkte)
        summe = np.zeros((zahl, 3))
        anzahl = np.zeros(zahl)
        np.add.at(summe, ursprung, np.asarray(paar['skaliert'], dtype=np.float64))
        np.add.at(anzahl, ursprung, 1.0)
        lage = summe / np.maximum(anzahl, 1.0)[:, None]
        # Quads als zwei Dreiecke, je Ecke ihre UV — Nähte bleiben je Insel richtig.
        ecken = np.concatenate([flaechen[:, [0, 1, 2]], flaechen[:, [0, 2, 3]]])
        uvs = np.concatenate([uv_ecken[:, [0, 1, 2]], uv_ecken[:, [0, 2, 3]]])
        teil = np.full(zahl, -1, dtype=np.int64)
        suchen = []
        for nr, (_name, (g9_idx, hb_idx)) in enumerate(paar['segmente'].items()):
            kaefig = ursprung[np.asarray(g9_idx, dtype=np.int64)]
            frei = teil[kaefig] < 0
            teil[kaefig[frei]] = nr
            drin = np.isin(ecken, np.asarray(hb_idx, dtype=np.int64)).any(axis=1)
            suchen.append(Hbdreiecksuche(hb['punkte'], ecken[drin], uvs[drin]) if drin.sum() >= 4 else None)
        self._netz = {'lage': lage, 'teil': teil, 'suchen': suchen}
        return self._netz

    # ----------------------------------------------------------- Backen

    def kachel(self, abtastung, nummer, feld):
        """`((S, S) float 0..1, mittlerer Abstand Texel → HumanBody-Fläche in m)` — Kachel `nummer`."""
        from humanbody_core.hautverschiebung import Hautverschiebung
        from scipy import ndimage

        d = self._vorbereiten()
        drin, ecken, anteile = abtastung.stellen(nummer)
        pos = np.einsum('nk,nkc->nc', anteile, d['lage'][ecken])
        teil = d['teil'][ecken[:, 0]]
        uv = np.zeros((len(pos), 2))
        abstand = np.zeros(len(pos))
        for nr, suche in enumerate(d['suchen']):
            m = teil == nr
            if not m.any() or suche is None:
                continue
            uv[m], abstand[m] = suche.uv(pos[m])
        s = abtastung.seite
        bild = np.full((s, s), self.MITTE, dtype=np.float64)
        bild[drin] = Hautverschiebung.abtasten(feld, uv)
        weg, (iy, ix) = ndimage.distance_transform_edt(~drin, return_indices=True)
        nah = (~drin) & (weg <= self.RAND_PX)
        bild[nah] = bild[iy[nah], ix[nah]]
        return bild, float(abstand.mean()) if len(abstand) else 0.0

    def backen(self, abtastung, ordner, melder=None):
        """Alle Kacheln schreiben → `({kachel: pfad}, bericht)`; bericht = Werte + Abstand + Dauer."""
        from PIL import Image

        from .verschiebungstextur import Verschiebungstextur

        werte = self.metawerte(self.person)
        feld = Verschiebungstextur.feld(self.GESCHLECHT, werte['age'], werte['tone'], werte['mass'])
        start = time.time()
        aus, abstaende = {}, []
        for i, nummer in enumerate(abtastung.kacheln):
            if melder:
                melder(0.9 + 0.08 * i / max(1, len(abtastung.kacheln)),
                       'Hautverschiebung (Alter/Tonus/Masse) Kachel %d' % nummer)
            bild, abstand = self.kachel(abtastung, nummer, feld)
            abstaende.append(abstand)
            pfad = os.path.join(str(ordner), '%s_%d.png' % (self.PRAEFIX, nummer))
            Image.fromarray(np.clip(bild * 255.0 + 0.5, 0, 255).astype(np.uint8), 'L').save(pfad, 'PNG')
            aus[nummer] = pfad
        bericht = dict(werte, abstand_mm=round(1000.0 * float(np.mean(abstaende)) if abstaende else 0.0, 2),
                       dauer_s=round(time.time() - start, 1))
        logger.info('Hautverschiebung: %d Kacheln, %s', len(aus), bericht)
        return aus, bericht

    @classmethod
    def anfuegen(cls, ergebnis, person, ordner, melder=None):
        """`ergebnis` (das `fototextur`-Dict) um `verschiebung` und `verschiebung_werte` ergänzen —
        neu gerechnet nur, wenn Werte oder Dateien fehlen. Ein Fehler kostet die Textur nicht."""
        alt = ergebnis.get('verschiebung') or {}
        da = alt and all(os.path.isfile(os.path.join(str(ordner), v)) for v in alt.values())
        if da and cls.gleich(person, ergebnis.get('verschiebung_werte')):
            return ergebnis
        try:
            from Genesis9.texturabtastung import G9texturabtastung

            abtastung = G9texturabtastung.holen(cls.SEITE)
            kacheln, bericht = cls(person, abtastung.seite).backen(abtastung, ordner, melder)
        except Exception as fehler:                      # noqa: BLE001 — Textur bleibt brauchbar
            logger.warning('Hautverschiebung nicht gebacken: %s', fehler, exc_info=True)
            return ergebnis
        ergebnis['verschiebung'] = {str(k): os.path.basename(v) for k, v in kacheln.items()}
        ergebnis['verschiebung_werte'] = bericht
        return ergebnis
