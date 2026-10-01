# -*- coding: utf-8 -*-
"""Haarenginestandmodell — das 3D-Modell des LETZTEN Stands eines Auftrags „2D3D Kleider" als fertige GLB
(01.10.2026).

Edgar: „das laden des 3d modells dauert immer lange, meldung: es wird gebaut. Baue beim letzten stand ein 3d modell
(Genesis mit assets) und lades es gleich, das muss schnell gehen."

Der Stand: die Stellung des Auftrags (Körper-Fit), darüber die Körper- und Gesichtsregler der Iterationen
(`kreislauf.modell.koerper`, wie `Haarengineexport.stellung`), die gebackenen Kacheln samt Augenbild und — wenn
Iterationen gelaufen sind — Kleider und Haar des Modells der letzten Runde (`kreislauf.modell`). Geschrieben wird es
von `Standmodellglb`; gebaut im Arbeitsprozess (am Ende eines Laufs, `Haarenginelauf._standmodell`, oder einzeln über
`manage.py haarengine_standmodell`), nie im Server — die Bühne lädt nur noch die Datei.

Ablage (Regel artefakte-benennen): `ergebnis/stand_<fassung>.glb` und `ergebnis/stand.json`. Die Fassung ist der
Fingerabdruck des Stands; ändert er sich (neue Runde, neue Kacheln, neuer Schreiber), ist die Datei veraltet
(`eintrag()['aktuell']`) und wird neu gebaut. Die Seite lädt `?v=<fassung>` — der Browser behält die Datei, bis sich
der Stand ändert.
"""

import hashlib
import json
import logging
import os
import time

from ..daten.haarengineablage import Haarengineablage

logger = logging.getLogger('core')

__all__ = ['Haarenginestandmodell']


class Haarenginestandmodell:
    BERICHT = 'stand.json'
    #: Ein gescheiterter Bau dieser Fassung (`{fassung, fehler}`) — die Bühne baut die Figur dann im Browser.
    FEHLER = 'stand_fehler.json'
    MUSTER = 'stand_%s.glb'
    #: Gehört zur Fassung: Ändert sich der Schreiber (`Standmodellglb`), werden alte Dateien neu gebaut.
    SCHREIBER = 3

    def __init__(self, job, ablage=None):
        self.job = job
        self.ablage = ablage or Haarengineablage(job.kennung)

    # ------------------------------------------------------------------ Stand

    def _kreislaufmodell(self):
        return ((self.job.ergebnis or {}).get('kreislauf') or {}).get('modell') or None

    def stellung(self):
        stellung = dict(self.job.stellung() or {})
        stellung.update({str(k): v for k, v in ((self._kreislaufmodell() or {}).get('koerper') or {}).items()})
        return stellung

    def baubar(self):
        return bool(self.job.stellung())

    def fassung(self):
        """Fingerabdruck des Stands — 12 Zeichen."""
        f = (self.job.ergebnis or {}).get('fototextur') or {}
        roh = json.dumps([self.SCHREIBER, self.stellung(), self._kreislaufmodell(), f.get('kacheln'), f.get('augen'),
                          f.get('stand')], sort_keys=True, default=str)
        return hashlib.md5(roh.encode('utf-8')).hexdigest()[:12]

    def bericht(self, name=BERICHT):
        pfad = self.ablage.ergebnis(name)
        try:
            return json.loads(pfad.read_text(encoding='utf-8')) if pfad.is_file() else None
        except (OSError, ValueError) as fehler:
            logger.warning('2D3D Kleider %s: %s nicht lesbar (%s)', self.job.kennung, pfad.name, fehler)
            return None

    def eintrag(self):
        """Für den Zustand der Seite: None, solange es keine Figur gibt; sonst `{datei, fassung, aktuell, bytes, …}`
        — `datei` None, wenn noch keine gebaut ist; `fehler`, wenn der Bau DIESER Fassung gescheitert ist."""
        if not self.baubar():
            return None
        jetzt = self.fassung()
        b = self.bericht() or {}
        if not b.get('datei') or not self.ablage.ergebnis(b['datei']).is_file():
            b = {'datei': None}
        # `fassung`: die der Datei (die Seite lädt sie mit `?v=`); `soll`: die des Stands — darauf bestellt die Seite.
        aus = dict(b, fassung=b.get('fassung') or jetzt, soll=jetzt,
                   aktuell=bool(b.get('datei')) and b.get('fassung') == jetzt)
        f = self.bericht(self.FEHLER) or {}
        if f.get('fassung') == jetzt and not aus['aktuell']:
            aus['fehler'] = f.get('fehler') or 'unbekannt'
        return aus

    def scheitern(self, fehler):
        """Den Fehler dieser Fassung merken — die Seite bestellt sie dann nicht wieder und baut im Browser."""
        try:
            self.ablage.ergebnis(self.FEHLER).write_text(
                json.dumps({'fassung': self.fassung(), 'fehler': str(fehler)[:500]}, ensure_ascii=False),
                encoding='utf-8')
        except OSError as nicht:
            logger.warning('2D3D Kleider %s: Fehler des Modells nicht gemerkt (%s)', self.job.kennung, nicht)

    # ------------------------------------------------------------------ Bauen

    def _kacheln(self):
        aus = {}
        for k, name in (((self.job.ergebnis or {}).get('fototextur') or {}).get('kacheln') or {}).items():
            if str(k).isdigit() and self.ablage.ergebnis(name).is_file():
                aus[int(k)] = str(self.ablage.ergebnis(name))
        return aus

    def _augenbild(self):
        name = ((self.job.ergebnis or {}).get('fototextur') or {}).get('augen')
        return str(self.ablage.ergebnis(name)) if name and self.ablage.ergebnis(name).is_file() else None

    def bauen(self):
        """`ergebnis/stand_<fassung>.glb` schreiben → Bericht (steht auch in `stand.json`)."""
        from Genesis9.charaktere import G9charaktere
        from Genesis9.formung import G9formung
        from Genesis9.koerpernetz import G9koerpernetz

        from .standmodellglb import Standmodellglb
        if not self.baubar():
            raise ValueError('Noch keine Figur — erst nach dem Schritt „Körper"')
        t = time.perf_counter()
        fassung = self.fassung()
        netz = G9koerpernetz(G9formung.aus_abfrage(self.stellung(), {}), G9charaktere.eintrag('basis'),
                             anhaenge=True, stufen=0).bauen()
        glb = Standmodellglb(netz['skelett']['knochen'])
        glb.koerper(netz, self._kacheln())
        glb.anhaenge(netz, self._augenbild())
        teile = []
        daten = self._kreislaufmodell()
        if daten:
            from Genesis9.modellmitkleidern import ModellMitKleidern

            from .kleidermodellbau import Kleidermodellbau
            modell = ModellMitKleidern.aus(daten)
            teile = [x for x in Kleidermodellbau(self.job.stellung(), None, koerper=modell.koerper).teile(modell)
                     if x.get('art') != 'koerper']
            glb.teile(teile)
        name = self.MUSTER % fassung
        ziel = self.ablage.ergebnis(name)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        zwischen = ziel.with_name(name + '.teil')
        laenge = glb.schreiben(zwischen)
        os.replace(zwischen, ziel)
        bericht = {'datei': name, 'fassung': fassung, 'bytes': int(laenge),
                   'sekunden': round(time.perf_counter() - t, 1), 'knochen': len(glb.knochen),
                   'knochen_ohne_gelenk': sorted(glb.fehlend), **glb.zahl,
                   'teile': sorted({'%s:%s' % (x.get('art'), x.get('sorte')) for x in teile}),
                   # Der Stand ist die BESTE Runde (`Begutachtungsstand`, 01.10.2026), nicht die letzte.
                   'runde': ((self.job.ergebnis or {}).get('kreislauf') or {}).get('runde_bester')
                   or ((self.job.ergebnis or {}).get('kreislauf') or {}).get('letzte_runde')}
        zettel = self.ablage.ergebnis(self.BERICHT + '.teil')
        zettel.write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
        os.replace(zettel, self.ablage.ergebnis(self.BERICHT))
        self.ablage.ergebnis(self.FEHLER).unlink(missing_ok=True)
        self._aufraeumen(name)
        logger.info('2D3D Kleider %s: Modell des Stands %s (%.1f MB, %d Netze, %.1f s)', self.job.kennung, name,
                    laenge / 1e6, glb.zahl['netze'], bericht['sekunden'])
        return bericht

    def _aufraeumen(self, behalten):
        """Ältere Fassungen weg — eine, die der Server gerade ausliefert, bleibt bis zum nächsten Bau liegen."""
        for pfad in self.ablage.ergebnis().glob(self.MUSTER % '*'):
            if pfad.name == behalten:
                continue
            try:
                pfad.unlink()
            except OSError as fehler:
                logger.info('2D3D Kleider %s: %s bleibt vorerst (%s)', self.job.kennung, pfad.name, fehler)
