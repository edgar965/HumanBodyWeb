# -*- coding: utf-8 -*-
u"""Der Unterprozess hinter „Video erzeugen" im Animations-Reiter.

Bekommt einen Auftrag als JSON, baut die Figur MIT ihren Morphs und ihren
Kleidern, rechnet die Bewegung (mit Weichgewebe, wenn gewuenscht) und
schreibt das MP4. Waehrenddessen steht der Fortschritt in einer zweiten
Datei, die der Server je Anfrage liest.

EIN EIGENER PROZESS, kein Thread im Server: Das Rendern braucht einen
OpenGL-Kontext und zwei bis drei Minuten. Ein Serverneustart mitten im Lauf
bricht ihn sauber ab, statt eine halbe Antwort zu hinterlassen.

Auftrag (JSON):
    body_type, morphs {name: wert}          die Figur
    stuecke [{name, pfad, farbe}]           `*_sim_rig.json` je Stueck
    bvh                                     Pfad der Bewegungsdatei
    sekunden, fps                           Laenge und Bildrate des Videos
    physik_mm                               0 = aus
    ziel                                    Pfad des MP4
    fortschritt                             Pfad der Fortschrittsdatei

Aufruf:  python filmlauf.py <auftrag.json>
"""
import json
import os
import sys
import time

import numpy as np

ORDNER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ORDNER)


class Filmlauf:
    u"""Ein Auftrag, ein Video."""

    def __init__(self, auftrag_pfad):
        with open(auftrag_pfad, encoding='utf-8') as datei:
            self.auftrag = json.load(datei)
        self.fortschritt = self.auftrag['fortschritt']
        self.begonnen = time.time()
        self._melden(u'Start', 0.0)

    def _melden(self, phase, anteil, fehler=None, fertig=False):
        u"""Schreibt den Stand — ATOMAR, ueber eine Zwischendatei.

        Der Server liest die Datei jederzeit; eine halb geschriebene JSON
        waere fuer ihn ein Fehler, obwohl nichts kaputt ist.
        """
        stand = {
            'phase': phase, 'anteil': round(float(anteil), 3),
            'sekunden': round(time.time() - self.begonnen, 1),
            'fertig': fertig, 'fehler': fehler,
        }
        vorlaeufig = self.fortschritt + '.neu'
        with open(vorlaeufig, 'w', encoding='utf-8') as datei:
            json.dump(stand, datei)
        os.replace(vorlaeufig, self.fortschritt)

    def _figurpunkte(self):
        u"""Alle Basispunkte der Figur, mit ihren Morphs — ueber Django.

        Derselbe Weg wie die Szene (`Charakterdaten.koerper_aus`): Eine
        zweite Morph-Rechnung hier liefe irgendwann auseinander.
        """
        from bvh_nach_anim import Animschreiber
        Animschreiber._django()
        from core.dienste.charakterdaten import Charakterdaten
        parameter = {'body_type': self.auftrag.get('body_type')
                     or 'Female_Caucasian'}
        for name, wert in (self.auftrag.get('morphs') or {}).items():
            parameter['morph_%s' % name] = wert
        koerper = Charakterdaten.koerper_aus(parameter)
        if koerper.vertices is None:
            raise ValueError(u'Die Figur liefert kein Netz (Morphdaten?).')
        # KOPIE, nicht der Puffer: `CharacterState.compute()` gibt dasselbe
        # Feld zurueck, das der naechste Reglerzug ueberschreibt (CLAUDE.md,
        # 08.09.2026, „Zwei Stufen statt einer").
        return np.array(koerper.vertices, dtype=np.float64), koerper.geschlecht

    def laufen(self):
        from hbfilm import Hbfilm
        try:
            punkte, geschlecht = self._figurpunkte()
            fps = float(self.auftrag.get('fps') or 24.0)
            bilder = int(round(float(self.auftrag.get('sekunden') or 5.0)
                               * fps))
            film = Hbfilm(
                self.auftrag['bvh'], bilder, fps,
                ab_sekunden=float(self.auftrag.get('ab_sekunden') or 0.0),
                stuecke=self.auftrag.get('stuecke') or [],
                physik=float(self.auftrag.get('physik_mm') or 0.0),
                geschlecht=geschlecht, figurpunkte=punkte,
                melder=self._melden)
            proben = film.proben()
            film.rechnen()
            pfad, zahl = film.schreiben(self.auftrag['ziel'], fps=fps,
                                        schleifen=1)
            self._melden(u'Fertig', 1.0, fertig=True)
            self._bilanz(film, proben, zahl)
            return 0
        except Exception as fehler:                              # noqa: BLE001
            import traceback
            self._melden(u'Abgebrochen', 0.0,
                         fehler=u'%s\n%s' % (fehler, traceback.format_exc()))
            return 1

    def _bilanz(self, film, proben, bilder):
        u"""Die Messwerte neben das Video — sie sind der Beleg."""
        bilanz = {
            'bilder': bilder, 'wurzelweg_m': film.bahn.wurzelweg(),
            'quell_fps': film.bahn.quell_fps, 'schritt': film.bahn.schritt,
            'teile': [],
        }
        for (name, punkte, ruhe, sitz, _leer), teil in zip(proben,
                                                            film.teile):
            eintrag = {'name': name, 'punkte': punkte,
                       'ruheprobe_mm': round(ruhe, 6),
                       'sitz_mm': round(sitz, 1) if sitz is not None else None}
            physik = teil.get('physik')
            if physik:
                eintrag['zuschlag_mm'] = round(physik['groesster_mm'], 1)
                if 'durchstich' in physik:
                    eintrag['stoff_im_koerper_prozent'] = round(
                        physik['durchstich'], 2)
            bilanz['teile'].append(eintrag)
        for name, werte in film.gleichlauf():
            for eintrag in bilanz['teile']:
                if eintrag['name'] == name:
                    eintrag['gleichlauf_mm'] = [round(w, 1) for w in werte]
        with open(self.auftrag['ziel'] + '.json', 'w',
                  encoding='utf-8') as datei:
            json.dump(bilanz, datei, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(Filmlauf(sys.argv[1]).laufen())
