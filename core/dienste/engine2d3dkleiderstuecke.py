# -*- coding: utf-8 -*-
"""Engine2d3dKleiderstuecke — Schritt „kleiderstuecke" von „2D3D Kleider": die Kleidung des Foto-Netzes als EIGENE Genesis-Stücke bauen und messen, VOR den Iterationen (04.10.2026).

Edgar: „die Kleider sind im 3D View noch nicht wegklickbar … wie ich das einbauen kann vor den Iterationen, wo ich mit dem Genesis modell starte" und „ein Schritt, der Modell und Kleider ‚besser als
Assets' macht: dafür fehlt mir eine Messgröße."

Bis dahin entstanden die Stücke (`Fotostuecke`: Oberteil, Hose, Socken aus Netz + Kleidungsmaske + Figur) erst in Runde 1 der Iterationen (`Begutachtungsrunde`); davor trug das Standmodell der Bühne keine
Kleider. Der Schritt ruft `Fotostuecke.holen()` — gemerkt in `job.ergebnis['fotostuecke']`, Runde 1 baut also nichts neu, solange sich Netz, Maske und Figur nicht ändern — und hängt die Stücke an das
Standmodell (`Standvorabkleider`): „Kleider" schaltet auf der Bühne schon vor der ersten Runde.

Dazu die MESSUNG (`Kleiderstueckmessung`, Maß: `Kleiderstuecknote`): Deckung, Treue und F-Wert je Stück gegen die Maskenflächen des Foto-Netzes in der Ruhelage, der Aufbau des Netzes (Inseln, Randschleifen),
der Abstand des Körpers zur nackten Haut und der Vergleich mit dem Bibliotheksstück als Maßstab. Gespeichert in `job.ergebnis['kleiderstuecke']`:

    stuecke     {name: {kennung, note, aufbau, angezogen}} — `angezogen`: Sitz auf der Figur aus dem Bau (`Fotostuecke`: median/p99/max mm)
    koerper     {haut_mm, haut_p95_mm, deckung} — Körper der Figur gegen die nackte Haut des Netzes
    abweichung  gesamt, nach Fläche gewogen (1 − F; kleiner ist besser)
    bibliothek  {name: {sorte, abweichung, f}} — derselbe Bezug, Bibliotheksstück statt Fotostück
    grund       warum es keine Stücke gibt (kein Körper, keine Kleidung in der Maske)

Kein Stück ist kein Fehler des Laufs: die Iterationen fallen dann auf die Bibliotheksstücke zurück (`Kleiderwahl.soll`).
"""

import logging
import time

from .fotostuecke import Fotostuecke
from .kleiderstueckbezug import Kleiderstueckbezug
from .kleiderstueckmessung import Kleiderstueckmessung
from .seitentiefemessung import Seitentiefemessung

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderstuecke']


class Engine2d3dKleiderstuecke:
    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def ausfuehren(self):
        bezug = Kleiderstueckbezug(self.job, self.ablage)
        grund = bezug.fehlt()
        if grund:
            return self._ohne(grund)
        t0 = time.perf_counter()
        self.lauf.melden(0.05, 'Kleiderstücke aus dem Netz bauen (beim ersten Mal rund 2–3 min)')
        stuecke = Fotostuecke(self.job, self.ablage).holen()
        bauen_s = time.perf_counter() - t0
        if not stuecke:
            fehler = ((self.job.ergebnis.get('fotostuecke') or {}).get('bericht') or {}).get('fehler')
            return self._ohne(fehler or 'Die Maske hat zu wenig Kleidung für ein Stück')
        self.lauf.melden(0.7, 'Kleiderstücke messen')
        t1 = time.perf_counter()
        messung = Kleiderstueckmessung.messen(bezug, stuecke)
        bericht = (self.job.ergebnis.get('fotostuecke') or {}).get('bericht') or {}
        for name, eintrag in messung['stuecke'].items():
            if (bericht.get(name) or {}).get('angezogen'):
                eintrag['angezogen'] = bericht[name]['angezogen']
        messung['bibliothek'] = Kleiderstueckmessung.bibliothek(self.job, bezug, list(stuecke))
        # Die Rumpftiefe gegen das Seitenfoto (05.10.2026): die Note oben misst gegen das Netz und sah den dicken Bauch nicht.
        messung['seitentiefe'] = Seitentiefemessung.messen(self.job, self.ablage, bezug, stuecke)
        messung['sekunden'] = {'bauen': round(bauen_s, 1), 'messen': round(time.perf_counter() - t1, 1)}
        self.job.ergebnis['kleiderstuecke'] = messung
        self.lauf.melden(1.0, 'Kleiderstücke: %s%s' % (', '.join(sorted(stuecke)), '' if messung['abweichung'] is None
                                                       else ' — Abweichung %.3f' % messung['abweichung']))
        logger.info('2D3D Kleider %s: Kleiderstücke %s, Abweichung %s (bauen %.0f s, messen %.0f s)', self.job.kennung, sorted(stuecke),
                    messung['abweichung'], bauen_s, messung['sekunden']['messen'])

    def _ohne(self, grund):
        """Keine Stücke — der Lauf geht weiter, die Iterationen nehmen Bibliotheksstücke."""
        self.job.ergebnis['kleiderstuecke'] = {'stuecke': {}, 'grund': grund}
        self.lauf.melden(1.0, 'Kleiderstücke: keine (%s)' % grund)
        logger.info('2D3D Kleider %s: keine Kleiderstücke (%s)', self.job.kennung, grund)
