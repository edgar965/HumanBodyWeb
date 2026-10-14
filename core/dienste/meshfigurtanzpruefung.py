# -*- coding: utf-8 -*-
"""Meshfigurtanzpruefung — die Animationsprüfung von „Mesh to 3D" und Mesh-3D: reißt der Stoff im Tanz, und wenn ja, mit welchen Gewichten reißt er am wenigsten? (13.10.2026)

Edgar (Zauberer, Ballerina): „Kleider dehnen sich extrem, Haut ist sichtbar unter den Kleidern, Kleider verformen sich winkelförmig", „die Ballerina verliert ihre Kleider während des Tanzes", dann: „das Testscript für Animation brauche ich auch generisch,
so dass ich das auswählen kann beim Bauen des Mesh to 3D, und das gleich korrigiert werden kann. Als extra Option im Job, default: An."

Die Prüfung läuft im Schritt „vorschau" bei jedem Objekt, dessen Punkte der Figur über Käfig-Gewichte folgen (`bewegung = folgt`: Kleidung, Bart, Tasche — Hut und Stab hängen starr an EINEM Knochen und können nicht reißen):
1. Eine Bewegung (Vorgabe `A_Results/DanceKurz`, sonst der Tanz der Bibliothek) wird einmal auf die Figur gelegt (`Engine2d3dKleiderbewegung`, wie die Animationsleiste), `BILDER` Bilder daraus dienen als Probe.
2. Für jede Kandidatin der Gewichte — die alten (`basis`: Käfig-Nachbarschaft, `Kleidunghautgewichte`) und die weichen (`Hautnaehe`) in den Breiten `ADAPTIV` — misst `Dehnungsmessung` die Dehnung jeder Kante gegen ihre Länge im Netz.
3. Die Kandidatin mit den wenigsten gerissenen Kanten (`Dehnungsmessung.punkte`) gewinnt; ihre Gewichte gehen in die `.haut`-Datei. Der Bericht (`ergebnis.animation.objekte[name]`) nennt alle Kandidatinnen mit ihren Kennzahlen.

Ohne Prüfung (Option `animationspruefung = aus`, oder die Bewegung lässt sich nicht legen) gelten die alten Gewichte, mit dem Grund im Bericht.
"""

import logging
import os
import threading
from types import SimpleNamespace

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurtanzpruefung']


class Meshfigurtanzpruefung:
    #: Option des Auftrags (`Meshfiguranimationsoptionen`).
    OPTION = 'animationspruefung'
    #: Bilder der Bewegung, an denen gemessen wird.
    BILDER = 8
    #: Breiten der weichen Gewichte (`Hautnaehe.ADAPTIV`), die neben den alten Gewichten antreten. Gemessen: Zauberer 0,3 → p99,9 13,5×, 0,5 → 13,8×, 1,0 → 19,9× (alte Gewichte 78×); Ballerina 0,3 und 0,5 je 6,0×, 1,0 → 8,0× (alte 21×).
    ADAPTIV = (0.3, 0.5, 1.0)

    def __init__(self, lauf):
        self.lauf = lauf
        self.ablage = lauf.ablage
        self.job = lauf.job
        self.tanzhaut = None
        self.spuren = None
        self.bilder = []
        self._verformungen = {}
        self.fehler = ''
        self._bereiten()

    # ------------------------------------------------------------------ Einstieg

    _sperre = threading.Lock()

    @classmethod
    def fuer(cls, lauf):
        """Die Prüfung dieses Laufs (einmal je Lauf gebaut, die Fäden der Vorschau fragen nacheinander) — `None`, wenn die Option ausgeschaltet ist."""
        optionen = getattr(lauf.job, 'optionen', None) or {}
        if str(optionen.get(cls.OPTION, 'an')) == 'aus':
            lauf.job.ergebnis.setdefault('animation', {}).update({'pruefung': 'aus'})
            return None
        with cls._sperre:
            if getattr(lauf, '_tanzpruefung', None) is None:
                lauf._tanzpruefung = cls(lauf)
            return lauf._tanzpruefung

    # ------------------------------------------------------------------ Vorbereitung

    @staticmethod
    def bvh():
        """Die Bewegung der Prüfung: `A_Results/DanceKurz.bvh`, sonst der Tanz der Bibliothek."""
        from .bvhverzeichnis import Bvhverzeichnis
        from .mesh3danimationswahl import Mesh3danimationswahl
        from .mesh3dbewegung import Mesh3dbewegung

        kategorie, name = Mesh3danimationswahl.STANDARD
        verzeichnis = Bvhverzeichnis()
        if kategorie in verzeichnis.kategorienamen():
            for datei in verzeichnis.dateien(kategorie):
                if datei.name == name and os.path.isfile(datei.pfad):
                    return datei.pfad
        return Mesh3dbewegung.bvh('')

    def _bereiten(self):
        """Skelett und Bewegung der Figur; scheitert es, steht der Grund in `self.fehler` und die Prüfung gibt alle Gewichte unverändert zurück."""
        try:
            from Genesis9.formung import G9formung
            from Genesis9.tanzhaut import G9tanzhaut

            from .engine2d3dkleiderbewegung import Engine2d3dKleiderbewegung

            stellung = self.job.stellung()
            if not stellung:
                raise ValueError('Noch keine Stellung der Figur')
            self.tanzhaut = G9tanzhaut(G9formung(dict(stellung)).skelett().kette().bauplan())
            ordner = self.ablage.arbeit('animationspruefung')
            ordner.mkdir(parents=True, exist_ok=True)
            huelle = SimpleNamespace(job=SimpleNamespace(stellung=self.job.stellung, optionen={'figur': {'hoehe_cm': float((self.job.optionen or {}).get('hoehe_cm') or 0)}}))
            _pfad, self.spuren = Engine2d3dKleiderbewegung(huelle).rechnen(self.bvh(), ordner)
            from Kleidung.dehnungsmessung import Dehnungsmessung

            self.bilder = Dehnungsmessung.bilder(self.BILDER, int(self.spuren.frame_count))
        except Exception as fehler:  # noqa: BLE001 — eine Prüfung ist ein Zusatz: scheitert sie, gelten die alten Gewichte, der Grund steht im Bericht
            logger.exception('Mesh to 3D %s: Animationsprüfung nicht vorbereitet', getattr(self.job, 'kennung', '?'))
            self.fehler = '%s: %s' % (type(fehler).__name__, fehler)

    def _verformung(self, knochen):
        schluessel = tuple(knochen)
        if schluessel not in self._verformungen:
            from Kleidung.dehnungsmessung import Dehnungsmessung

            self._verformungen[schluessel] = Dehnungsmessung.verformungen(self.tanzhaut, self.spuren, self.bilder, knochen)
        return self._verformungen[schluessel]

    # ------------------------------------------------------------------ Wahl

    def waehlen(self, name, gewichte, ruhelage, netz, ruhe, dreiecke, index, gewicht):
        """`(index, gewicht, bericht)` — die besten Gewichte für das Objekt `name`. `gewichte`: `Meshfigurhautgewichte` (Käfig, Knochennamen), `ruhelage`: `Meshfigurkleidungsruhelage`, `netz`/`ruhe` (M, 3): die Punkte im Netz und in der Ruhelage,
        `index`/`gewicht` (M, 4): die alten Gewichte (`basis`)."""
        bericht = {'pruefung': 'an', 'bewegung': os.path.basename(self.bvh()) if not self.fehler else None, 'bilder': self.bilder, 'punkte': int(len(netz)), 'kandidaten': {}}
        if self.fehler:
            bericht.update({'pruefung': 'nicht gelaufen', 'grund': self.fehler, 'gewaehlt': 'basis'})
            self._eintragen(name, bericht)
            return index, gewicht, bericht
        try:
            return self._waehlen(name, gewichte, ruhelage, netz, ruhe, dreiecke, index, gewicht, bericht)
        except Exception as fehler:  # noqa: BLE001
            logger.exception('Mesh to 3D %s: Animationsprüfung von %s gescheitert', getattr(self.job, 'kennung', '?'), name)
            bericht.update({'pruefung': 'gescheitert', 'grund': '%s: %s' % (type(fehler).__name__, fehler), 'gewaehlt': 'basis'})
            self._eintragen(name, bericht)
            return index, gewicht, bericht

    def _waehlen(self, name, gewichte, ruhelage, netz, ruhe, dreiecke, index, gewicht, bericht):
        from Kleidung.dehnungsmessung import Dehnungsmessung
        from Kleidung.hautnaehe import Hautnaehe

        verformung = self._verformung(gewichte.knochen)
        kanten = Dehnungsmessung.kanten(dreiecke)
        abstand, _ = ruhelage.entposen.baum.query(np.asarray(netz, dtype=np.float64), workers=-1)
        from .meshfigurhautgewichte import Meshfigurhautgewichte

        ruhe_abstand = Meshfigurhautgewichte.abstand_ruhe(ruhelage, ruhe)
        if ruhe_abstand is not None:
            abstand = np.minimum(abstand, ruhe_abstand)                      # anliegend in der Haltung des Netzes ODER in der Ruhelage (an der Hüfte liegt die Figur unter der Hose tiefer als das Netz)
        kandidaten = {'basis': (index, gewicht)}
        for adaptiv in self.ADAPTIV:
            n = Hautnaehe(ruhelage.entposen.posiert, gewichte.index, gewichte.gewicht, gewichte.knochen, adaptiv=adaptiv)
            kandidaten['weich_%g' % adaptiv] = n.berechnen(netz, index, gewicht, abstand)
        punkte = {}
        for titel, (i, g) in kandidaten.items():
            kennzahlen = Dehnungsmessung.messen(ruhe, netz, dreiecke, i, g, verformung, kanten)
            bericht['kandidaten'][titel] = {k: round(v, 4 if abs(v) < 1 else 2) for k, v in kennzahlen.items()}
            punkte[titel] = Dehnungsmessung.punkte(kennzahlen)
        beste = min(punkte, key=punkte.get)
        bericht['gewaehlt'] = beste
        i, g = kandidaten[beste]
        i, g = self._gewebe(name, bericht, gewichte, netz, ruhe, dreiecke, i, g, abstand, verformung, kanten, punkte[beste], ruhelage.entposen.ruhe)
        self._eintragen(name, bericht)
        logger.info('Mesh to 3D %s: Animationsprüfung %s — gewählt %s (%s)%s', getattr(self.job, 'kennung', '?'), name, beste,
                    ', '.join('%s %.3f' % (t, p) for t, p in punkte.items()), ' + Gewebe-Regel' if bericht.get('gewebe', {}).get('angewandt') else '')
        return i, g, bericht

    #: Die Gewebe-Regel wird nur übernommen, wenn die Streckung dadurch nicht schlechter wird als `GEWEBE_FAKTOR` · Punkte der gewählten Gewichte + `GEWEBE_PLUS` (Setzungen; die Punkte liegen bei 0,0005–0,005)
    #: UND wenn dadurch nicht MEHR Stoff weit vom Arm Armgewicht trägt (`Kleidungarmprobe`) — das ist das Maß, das die Regel beheben soll.
    GEWEBE_FAKTOR = 1.5
    GEWEBE_PLUS = 0.001

    def _gewebe(self, name, bericht, gewichte, netz, ruhe, dreiecke, index, gewicht, abstand, verformung, kanten, punkte_beste, kaefig_ruhe):
        """Die gewählten Gewichte durch `Kleidunggewebe` schicken (14.10.2026, Edgar: „ballerina riggt den Rock an die Hände“): Stoff, der weit vom Körper hängt, folgt dem, woran er im Gewebe hängt, nicht jedem Glied, an dem er im Raum vorbeikommt.
        Die Streckungsprüfung sieht den Fehler nicht (ein an die Hand gehängter Rock reißt nicht, er folgt nur dem Falschen) — sie schützt nur davor, dass die Regel den Stoff reißen lässt. Dafür zählt `Kleidungarmprobe`, wie viel Stoff weit vom Arm Armgewicht trägt: steigt
        die Zahl, bleibt es bei den gewählten Gewichten (am Zauberer hängte die Regel die weite Robe an die Arme: 0,9 % → 21 % des Stoffs ab 25 cm vom Arm; gemessen 14.10.2026). `(index, gewicht)`; der Bericht trägt `gewebe`."""
        from Kleidung.kleidungarmprobe import Kleidungarmprobe
        from Kleidung.dehnungsmessung import Dehnungsmessung
        from Kleidung.kleidunggewebe import Kleidunggewebe

        regel = Kleidunggewebe()
        try:
            neu_index, neu_gewicht = regel.berechnen(netz, dreiecke, index, gewicht, abstand, len(gewichte.knochen))
        except Exception as fehler:  # noqa: BLE001 — die Regel ist ein Zusatz: scheitert sie, gelten die gewählten Gewichte
            logger.exception('Mesh to 3D %s: Gewebe-Regel für %s gescheitert', getattr(self.job, 'kennung', '?'), name)
            bericht['gewebe'] = {'angewandt': False, 'grund': '%s: %s' % (type(fehler).__name__, fehler)}
            return index, gewicht
        befund = dict(regel.befund)
        if befund.get('uebersprungen') or not befund.get('frei'):
            bericht['gewebe'] = {**befund, 'angewandt': False}
            return index, gewicht
        kennzahlen = Dehnungsmessung.messen(ruhe, netz, dreiecke, neu_index, neu_gewicht, verformung, kanten)
        punkte = Dehnungsmessung.punkte(kennzahlen)
        bericht['kandidaten']['gewebe'] = {k: round(v, 4 if abs(v) < 1 else 2) for k, v in kennzahlen.items()}
        probe = Kleidungarmprobe(kaefig_ruhe, gewichte.index, gewichte.gewicht, gewichte.knochen)
        fern = probe.fern(ruhe)
        arm_vorher, arm_nachher = probe.zaehlen(fern, index, gewicht), probe.zaehlen(fern, neu_index, neu_gewicht)
        streckung_ok = punkte <= self.GEWEBE_FAKTOR * punkte_beste + self.GEWEBE_PLUS
        angewandt = streckung_ok and arm_nachher <= arm_vorher
        bericht['gewebe'] = {**befund, 'angewandt': bool(angewandt), 'punkte': round(float(punkte), 4), 'punkte_vorher': round(float(punkte_beste), 4), 'arm_fern_vorher': arm_vorher, 'arm_fern_nachher': arm_nachher}
        if streckung_ok and not angewandt:
            bericht['gewebe']['grund'] = 'mehr Stoff weit vom Arm trägt Armgewicht (%d statt %d)' % (arm_nachher, arm_vorher)
        return (neu_index, neu_gewicht) if angewandt else (index, gewicht)

    def _eintragen(self, name, bericht):
        a = self.job.ergebnis.setdefault('animation', {})
        a.setdefault('objekte', {})[name] = bericht
        a['pruefung'] = 'an'
