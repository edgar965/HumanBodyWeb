# -*- coding: utf-8 -*-
u"""Hbmorpheaufgenesis — die HumanBody-Regler auf den Genesis-9-Kaefig uebertragen.

WARUM (Edgar, 20.09.2026: „kannst du diese Body Shapes nicht selber bauen?
… HumanBody hat doch mehr Regler als MakeHuman?" — „fang schon mal an mit
dem Bau der HumanBody Regler fuer Genesis"): Die Daz-Bibliothek hat ohne
Kaufpakete keine Einzelformregler; HumanBody hat 204 (MB-Lab). Ein Regler
ist eine Verschiebung je Netzpunkt — und die Paarung der beiden Grundnetze
gibt es schon: `G9aufhumanbody.paarung_bauen` (fuer Daz-Kleider auf
HumanBody) kennt zu jedem Genesis-Browserpunkt seinen HumanBody-Punkt, mit
lokalen Rahmen (Normale, Aufwaerts, Quer) auf beiden Seiten.

DIE UEBERTRAGUNG ist der Kleiderweg rueckwaerts, nur ohne Versatz:

    1. HumanBody-Delta des Reglers je Punkt (`CharacterState`, +1 und -1
       gegen die Grundfigur — so sind Kombis wie BreastMass x BreastTone
       gleich richtig, MB-Lab rechnet sie selbst), in Three-Lage.
    2. Je Genesis-Browserpunkt die KANDIDATEN naechsten HumanBody-Punkte
       DESSELBEN Koerperteils um seine geschaetzte Lage (`skaliert`,
       `segmente` der Paarung), gewichtet 1/Abstand; Kandidaten mit
       gegenlaeufiger Normale (Skalarprodukt < EINIG: Ober- gegen Unterlippe,
       Innenseite gegen Aussenseite) zaehlen nicht — es sei denn, keiner
       stimmt, dann der naechste. Das ist die Paarung der Kleider (`zu`, ein
       Punkt), nur ueber mehrere Punkte: Mit EINEM Punkt je Genesis-Punkt
       kamen nur 7.894 der 18.210 HumanBody-Punkte je vor, und ein Morph auf
       den uebrigen war weg (Ears Lobe 7,2 -> 0,1 mm, Mouth SizeX 14,7 -> 3,5
       mm — gemessen 20.09.2026, `_wegwerf/hbmorphe_vergleich.py`).
    3. Jedes Kandidaten-Delta in DESSEN Rahmen zerlegen und im Rahmen des
       Genesis-Punkts wieder zusammensetzen — ein Delta entlang der Normale
       bleibt entlang der Normale, auch wo die Figuren anders stehen (Arme,
       Beine). Geteilt durch den Hoehenmassstab.
    4. Von den 27.087 Browserpunkten (Naehte doppelt) auf die 25.182
       Kaefigpunkte mitteln (`ursprung`), dann das Feld ueber die GLAETTUNG
       naechsten Kaefigpunkte glaetten, DURCHGAENGE mal — HumanBody ist
       groeber, ohne Glaettung stuende die Verschiebung stufig auf dem
       feineren Kaefig.
    5. Ablegen als `hb:<HumanBody-Name>` (`G9hbmorphe.ablegen`), zweiseitig.
       Ein Regler, der keinen Kaefigpunkt erreicht (Iris, Zaehne — bei
       Genesis Anhaenge, nicht Koerper), wird uebergangen.
    6. Ein Regler, der Gelenke verschiebt (`Hbmorphrig`: Kopfgelenk ab 5 mm
       oder ein Knochenabstand ab 7,5 mm — Body Size, alle Laengen, Winkel),
       bekam bis zum 17.10.2026 NUR den Steckbrief (`rig: true`): ohne
       Skelett-Nachzug blaehte er die projizierten Anhaenge auf (Mund
       6,8 -> 94 cm bei Body Size -100 %, Edgar mit Bild, 20.09.2026).
       Seit dem 17.10.2026 haben auch diese 21 Regler eine Datei, mit den
       Gelenkversaetzen (`G9gelenkversatz`, abgelegt in der `.npz`), die
       `G9formelnfremd` ins Skelett mischt. `bestand.json` fuehrt sie unter
       `rig_mit_skelett`.

Was NICHT drin ist: der Umfangsmassstab je Rumpfhoehe (`G9hbsitz`), den die
Kleider brauchen — eine Verschiebung von 2 cm bleibt 2 cm mal Hoehenmassstab.
Und die Grundfigur ist die weibliche Paarung (`female`, Standardbauart);
die maennlichen HumanBody-Pakete tragen dieselben Reglernamen.

Bauen: `manage.py hbmorphe_bauen` (Ablage `Genesis9/ablage/hbmorphe/`,
mit `bestand.json`). Gemessen wird beim ersten Lauf, siehe Befehl.
"""
import logging
import os
import time

import numpy as np
from Genesis9.gelenkversatz import G9gelenkversatz
from Genesis9.hbmorphe import G9hbmorphe

from .hbmorphuebertragung import Hbmorphuebertragung
from .hbtraeger import Hbtraeger

logger = logging.getLogger('core')

__all__ = ['Hbmorpheaufgenesis']


class Hbmorpheaufgenesis(Hbmorphuebertragung):
    u"""Alle HumanBody-Regler als Genesis-9-Morphs bauen (Zuordnung und Uebertragung: `Hbmorphuebertragung`)."""

    #: Die Regler, die in HumanBody das Skelett veraendern (Laengen, Gesamtgroesse, Winkel, Kopf-/Hand-/Fussgroesse). Aus der ersten Messung vom 20.09.2026
    #: (`Hbmorphrig`, Kopfgelenk ab 5 mm oder Knochenabstand ab 7,5 mm), ohne die Fantasy-Ohren (Spitzen, keine Gelenke), dazu die zwei Armlaengen
    #: (der alte Schaetzer sah die Arm-Gelenke nicht: auf `l_upperarm` liegt kein Hautgewicht, nur auf den Verdrillungsknochen). Volumenregler (Mass, Tone,
    #: Girth) stehen nicht hier — eine Schaetzung aus der Haut ueberzeichnet sie (Torso Mass: 55 mm „Laenge“ nach dem Familienschaetzer, gemessen 17.10.2026).
    SKELETT = frozenset((
        'Arms_ForearmLength', 'Arms_UpperarmLength', 'Body_Size', 'Chest_SizeZ', 'Feet_Size', 'Feet_SizeZ', 'Hands_FingersLength', 'Hands_Length',
        'Hands_PalmLength', 'Hands_Size', 'Head_Size', 'Head_SizeX', 'Head_SizeZ', 'Legs_Bow', 'Legs_LowerlegLength', 'Legs_UpperlegLength',
        'Neck_Angle', 'Neck_Length', 'Pelvis_Angle', 'Pelvis_Length', 'Torso_Length'))

    def __init__(self, melden=None):
        super().__init__()
        self.melden = melden or (lambda *a: None)
        self._zustand = None
        self._basis = None
        self._gelenke = None

    def zustand(self):
        u"""Der HumanBody-Rechner auf der Grundfigur der Paarung."""
        if self._zustand is None:
            from GarmentCode.dienst import GarmentcodeDienst
            from humanbody_core import CharacterState

            from .charakterdaten import Charakterdaten
            zustand = CharacterState(Charakterdaten.morphdaten(),
                                     Charakterdaten.voreinstellungen())
            zustand.set_body_type(self.BAUART or GarmentcodeDienst.BAUART.get(
                self.GESCHLECHT, 'Female_Caucasian'))
            self._basis = Hbtraeger.three(np.array(zustand.compute(), dtype=np.float64))
            abweichung = float(np.abs(self._basis - self.humanbody()['punkte']).max())
            if abweichung > 1e-6:
                raise ValueError('HumanBody-Grundfigur der Paarung und des Rechners '
                                 'weichen ab (%.4f m)' % abweichung)
            self._zustand = zustand
        return self._zustand

    # ------------------------------------------------------------ Regler

    def namen(self):
        return [m['name'] for m in self.zustand().get_morph_list()]

    def hb_delta(self, name, wert):
        u"""(18210, 3) Verschiebung des Reglers bei `wert` gegen die Grundfigur."""
        zustand = self.zustand()
        zustand.set_morph(name, float(wert))
        try:
            punkte = Hbtraeger.three(np.array(zustand.compute(), dtype=np.float64))
        finally:
            zustand.set_morph(name, 0.0)
        return punkte - self._basis

    # -------------------------------------------------------------- Bauen

    def gelenkversatz(self):
        u"""Die Schaetzung der Gelenkversaetze (`G9gelenkversatz`) — gleich fuer alle Familien."""
        if self._gelenke is None:
            self._gelenke = G9gelenkversatz()
        return self._gelenke

    def bauen(self):
        u"""Alle Regler bauen; gibt `[{name, punkte, plus_mm, minus_mm}]` zurueck."""
        start = time.perf_counter()
        namen = self.namen()
        G9hbmorphe.leeren()
        aus, rig_weg = [], []
        for nr, name in enumerate(namen, 1):
            plus = self.uebertragen(self.hb_delta(name, 1.0))
            minus = self.uebertragen(self.hb_delta(name, -1.0))
            nummern = np.nonzero((np.abs(plus).max(axis=1) > 0) | (np.abs(minus).max(axis=1) > 0))[0]
            if not len(nummern):
                logger.info('HB-Morphs: %s erreicht keinen Kaefigpunkt — uebergangen', name)
                self.melden(nr, len(namen), name, None)
                continue
            modus = 'rahmen'
            if name in self.SKELETT:
                # Ein Regler, der Gelenke verschiebt, ist eine grosse, fast starre Verschiebung: im Weltraum uebertragen (siehe `uebertragen`).
                plus, minus = self.uebertragen(self.hb_delta(name, 1.0), welt=True), self.uebertragen(self.hb_delta(name, -1.0), welt=True)
                nummern = np.nonzero((np.abs(plus).max(axis=1) > 0) | (np.abs(minus).max(axis=1) > 0))[0]
                modus = 'welt'
            mass = self.gelenkversatz().beide(nummern, plus[nummern], minus[nummern])
            mass['rig'] = name in self.SKELETT
            quelle = {'quelle': 'HumanBody %s' % self.zustand().body_type, 'modus': modus, **mass}
            # Gelenke nur fuer Regler, die Laengen aendern (`SKELETT`): ein Volumenmorph (Mass, Tone) verschiebt die Oberflaeche, nicht das Gelenk.
            gelenke = self.gelenkversatz().fuer_morph(nummern, plus[nummern], minus[nummern]) if mass['rig'] else None
            if mass['rig']:
                rig_weg.append(name)
                logger.info('HB-Morphs: %s verschiebt Gelenke (Kopf %.1f mm, Laenge %.1f mm) — das Skelett folgt',
                            name, mass['kopf_mm'], mass['laenge_mm'])
            G9hbmorphe.ablegen(name, nummern, plus[nummern], minus[nummern], quelle, gelenke)
            brief = G9hbmorphe.steckbrief(name)
            aus.append({'name': name, 'punkte': brief['punkte'],
                        'plus_mm': brief['plus_mm'], 'minus_mm': brief['minus_mm']})
            self.melden(nr, len(namen), name, brief)
        G9hbmorphe.bestand_schreiben({
            'paarung': '%s/%s' % (self.GESCHLECHT, self.BAUART or '-'),
            'bauart': self.zustand().body_type,
            'hb_stand': self.hb_stand(), 'zahl': len(aus),
            'rig_mit_skelett': rig_weg,
            'rig_regeln': 'Namensliste Hbmorpheaufgenesis.SKELETT',
            'massstab': round(float(self.paarung()['massstab']), 4),
            'kandidaten': self.KANDIDATEN,
            'glaettung': {'nachbarn': self.GLAETTUNG, 'durchgaenge': self.DURCHGAENGE},
            'sekunden': round(time.perf_counter() - start, 1)})
        logger.info('HB-Morphs auf Genesis 9: %d Regler in %.1f s nach %s',
                    len(aus), time.perf_counter() - start, G9hbmorphe.ordner())
        return aus

    @staticmethod
    def hb_stand():
        u"""Juengste Aenderung (ns) der HumanBody-Morphpakete — der Bestand."""
        from django.conf import settings
        wurzel = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'morphs')
        juengste = 0
        for ordner, _u, dateien in os.walk(wurzel):
            for datei in dateien:
                juengste = max(juengste, os.stat(os.path.join(ordner, datei)).st_mtime_ns)
        return juengste

    @classmethod
    def veraltet(cls):
        u"""Fehlt die Ablage oder ist sie aelter als die HumanBody-Morphs?"""
        bestand = G9hbmorphe.bestand()
        return (not bestand or bestand.get('fassung') != G9hbmorphe.FASSUNG
                or bestand.get('hb_stand', 0) < cls.hb_stand())
