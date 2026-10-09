# -*- coding: utf-8 -*-
"""Blendimportlauf — ein Blender-Import von der .blend bis zum Genesis-Modell (läuft in `blendimport_fahren`).

Konzept und Messungen: Hilfe → Architektur → Genesis (08.10.2026). Die Schritte:

    export    Blender liest die .blend (`blendexport.py`): je Netz Punkte, Dreiecke, UV, Bilder; Rollen (`Blendimportrollen`)
    koerper   Körper + Augen als GLB mit einer Textur (`Blendimportkoerper`)
    figur     „Mesh to 3D" auf diesem Körper: Regler, Gesicht, Eigenmorph (`Blendimportfigur`, eigener Auftrag)
    stuecke   Kleider und Haar als Genesis-Stücke in der Bibliothek (`Blendimportstuecke`)
    haut      die Originalhaut auf die Genesis-Kacheln backen (`Blendimporthaut`, Blender auf der GPU)
    augen     Originalaugen ins Genesis-Augenbild (`Blendimportaugen`) — oder das Daz-Bild aus „Mesh to 3D"
    modell    `data/models/<Name>.json` mit Reglern, Stücken, Haut, Augen (`Blendimportmodell`)

Der Stand steht in `stand.json` (`Blendimportablage`); jeder Schritt legt sein Ergebnis dort ab, ein späterer Lauf kann
`ab` einem Schritt neu rechnen und liest den Rest aus dem Stand. Ein Fehler beendet den Lauf sichtbar (`status`,
`fehler`), ein Stück, das scheitert, nicht (es steht im Bericht).
"""

import json
import logging
import time

from django.utils import timezone

from ..daten.blendimportablage import Blendimportablage

logger = logging.getLogger('core')

__all__ = ['Blendimportlauf']


class Blendimportlauf:
    SCHRITTE = ('export', 'umposen', 'koerper', 'figur', 'stuecke', 'haut', 'augen', 'modell')
    BAENDER = {'export': (0, 3), 'umposen': (3, 5), 'koerper': (5, 7), 'figur': (7, 72), 'stuecke': (72, 80),
               'haut': (80, 95), 'augen': (95, 97), 'modell': (97, 100)}

    class Angehalten(Exception):
        """Der Nutzer hat angehalten."""

    def __init__(self, kennung):
        self.ablage = Blendimportablage(kennung)
        self.stand = self.ablage.stand()
        self._band = (0, 100)
        self._letzte = 0.0

    # ------------------------------------------------------------ Stand

    def sichern(self, **felder):
        self.stand.update(felder, aktualisiert=timezone.now().isoformat())
        self.ablage.stand_schreiben(self.stand)

    def melden(self, anteil, text):
        jetzt = time.monotonic()
        if jetzt - self._letzte < 0.5 and anteil < 1.0:
            return
        self._letzte = jetzt
        von, bis = self._band
        if self.ablage.stand().get('status') == 'angehalten':
            raise self.Angehalten()
        self.sichern(fortschritt=max(int(self.stand.get('fortschritt') or 0),
                                     int(von + (bis - von) * max(0.0, min(1.0, anteil)))), detail=str(text)[:200])

    def ergebnis(self, schritt, wert):
        e = dict(self.stand.get('ergebnis') or {})
        e[schritt] = wert
        self.sichern(ergebnis=e)

    def inventar(self):
        return json.loads(self.ablage.export('inventar.json').read_text(encoding='utf-8'))

    def job(self):
        from ..models import Meshfigurauftrag

        figur = (self.stand.get('ergebnis') or {}).get('figur') or {}
        if not figur.get('id'):
            raise RuntimeError('Kein Auftrag „Mesh to 3D" — Schritt „figur" zuerst')
        return Meshfigurauftrag.objects.get(pk=figur['id'])

    # ------------------------------------------------------------ Ablauf

    def ausfuehren(self, ab=None):
        self.ablage.anlegen()
        start = self.SCHRITTE.index(ab) if ab in self.SCHRITTE else 0
        self.sichern(status='laeuft', fehler='', gestartet=timezone.now().isoformat(), ab=self.SCHRITTE[start])
        t0 = time.perf_counter()
        try:
            for name in self.SCHRITTE[start:]:
                if self.ablage.stand().get('status') == 'angehalten':
                    raise self.Angehalten()
                self._band = self.BAENDER[name]
                self.sichern(schritt=name)
                self.melden(0.0, name)
                t = time.perf_counter()
                getattr(self, '_' + name)()
                dauer = dict(self.stand.get('dauer') or {}, **{name: round(time.perf_counter() - t, 1)})
                self.sichern(dauer=dauer)
        except self.Angehalten:
            logger.info('Blender-Import %s: angehalten', self.ablage.kennung)
            return
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler beendet den Lauf sichtbar
            logger.exception('Blender-Import %s: Schritt %s gescheitert', self.ablage.kennung, self.stand.get('schritt'))
            self.sichern(status='gescheitert', fehler='%s: %s' % (self.stand.get('schritt'), fehler))
            return
        self.sichern(status='fertig', fortschritt=100, detail='Fertig', dauer_s=round(time.perf_counter() - t0, 1),
                     beendet=timezone.now().isoformat())
        logger.info('Blender-Import %s: fertig', self.ablage.kennung)

    # ----------------------------------------------------------- Schritte

    def _export(self):
        from .blendimportblender import Blendimportblender
        from .blendimportrollen import Blendimportrollen

        Blendimportblender(self.ablage, self.melden).laufen(
            'blendexport.py', self.stand['quelle']['datei'], ['--ziel', self.ablage.export()],
            self.ablage.export('inventar.json'))
        rollen = Blendimportrollen(self.inventar()).zuordnen()
        self.sichern(rollen=rollen)
        self.ergebnis('export', {'netze': len(rollen)})

    def _umposen(self):
        from .blendimportumposen import Blendimportumposen

        if self.stand['einstellungen'].get('umposen') != 'rig':
            self.ergebnis('umposen', {'aus': True})
            return
        if self.inventar().get('ohne_rig'):
            # Ohne Armatur gibt es nichts, womit sich umposen ließe: Punkte bleiben, wie der Export sie las; „Mesh to 3D" schätzt die Haltung.
            self.ergebnis('umposen', {'aus': True, 'grund': 'Die Datei hat kein Skelett'})
            return
        try:
            bericht = Blendimportumposen(self.ablage, self.melden).umposen(self.stand['quelle']['datei'])
        except RuntimeError as fehler:
            # Ein anderes Rig als Auto-Rig Pro (Daven.blend, Character Creator: Rigs `Armature` + `CC3_Base_Plus`, 09.10.2026): das
            # Blender-Skript endet ohne Ergebnis. Die Haltung der Datei gilt dann — wie bei `umposen = aus`, der Grund steht im Ergebnis.
            logger.warning('Blender-Import %s: Umposen gescheitert, Haltung der Datei gilt: %s', self.ablage.kennung, str(fehler)[:300])
            bericht = {'aus': True, 'grund': 'Umposen gescheitert: %s' % str(fehler)[:300]}
        self.ergebnis('umposen', bericht)

    def _koerper(self):
        from .blendimportkoerper import Blendimportkoerper

        self.ergebnis('koerper', Blendimportkoerper(self.ablage, self.inventar(), self.stand['rollen']).schreiben())

    def _figur(self):
        from .blendimportfigur import Blendimportfigur
        from .blendimportkoerper import Blendimportkoerper

        figur = Blendimportfigur(self.ablage, self.stand['quelle']['name'], self.stand['einstellungen']['basis'])
        job = figur.anlegen(self.ablage.arbeit(Blendimportkoerper.DATEI))
        self.ergebnis('figur', {'id': str(job.id), 'kennung': job.kennung})
        job = figur.rechnen(job)
        self.ergebnis('figur', {'id': str(job.id), 'kennung': job.kennung, 'regler': len(job.stellung() or {}),
                                'rest': (job.ergebnis or {}).get('rest', {}).get('regler')})
        self._nachformung(job)

    def _nachformung(self, job):
        """Scham (und was `Blendimportnachformung.REGIONEN` sonst nennt) an das Original angleichen; ein Fehler dort
        beendet den Import nicht — die Figur gilt dann, wie „Mesh to 3D" sie gebaut hat."""
        from .blendimportnachformung import Blendimportnachformung

        if self.stand['einstellungen'].get('scham') in ('objekt', 'mann'):
            # Die Scham kommt als Stück (`Blendimportscham`); eine nachgeformte Haut darunter ergäbe sie doppelt
            # (Edgar, 09.10.2026: „die hat im moment zwei mal Geschlechtsorgane" — facettierte Nachformung + Stück).
            self.ergebnis('nachformung', {'aus': 'Scham kommt als Stück (Einstellung scham = objekt)'})
            return
        try:
            bericht = Blendimportnachformung(self.ablage, job, self.inventar(), self.stand['rollen'],
                                             self.stand['quelle']['name'], self.melden).formen()
        except Exception as fehler:  # noqa: BLE001 — Zusatzschritt: der Import läuft mit der Figur der Anpassung weiter
            logger.exception('Blender-Import %s: Nachformung gescheitert', self.ablage.kennung)
            bericht = {'fehler': str(fehler)[:300]}
        self.ergebnis('nachformung', bericht)

    def zusatzregler(self):
        """Die neuen Regler der Nachformung (`{eigen:…: 1.0}`), die zur Figur dieses Imports gehören — leer ohne sie."""
        from .blendimportnachformung import Blendimportnachformung

        return Blendimportnachformung.zusatzregler(self.stand)

    def _stuecke(self):
        from .blendimportstuecke import Blendimportstuecke

        if self.stand['einstellungen'].get('stuecke') != 'an':
            self.ergebnis('stuecke', {'aus': True, 'stuecke': {}})
            return
        bau = Blendimportstuecke(self.ablage, self.job(), self.inventar(), self.stand['rollen'],
                                 self.stand['quelle']['name'], self.melden,
                                 self.stand['einstellungen'].get('augen'), self.zusatzregler(),
                                 self.stand['einstellungen'].get('scham'))
        stuecke, bericht = bau.bauen()
        self.ergebnis('stuecke', {'stuecke': stuecke, 'bericht': bericht, 'bogen': bau.bogen_pfad})

    def _haut(self):
        from .blendimporthaut import Blendimporthaut

        haut = Blendimporthaut(self.ablage, self.job(), self.inventar(), self.stand['rollen'],
                               self.stand['einstellungen']['kachel_px'], self.melden,
                               self.stand['einstellungen'].get('normalen_grenze'), self.zusatzregler(),
                               self.stand['einstellungen'].get('normalen_form') or 'weg')
        kacheln, bericht = haut.backen(self.stand['quelle']['datei'])
        self.ergebnis('haut', {**bericht, 'kacheln': kacheln})

    def _augen(self):
        from ..daten.meshfigurablage import Meshfigurablage
        from .blendimportaugen import Blendimportaugen

        job = self.job()
        # `objekt`: dieselbe Irisübertragung — sie bleibt der Rückfall, wenn jemand das Augen-Stück auszieht.
        if self.stand['einstellungen'].get('augen') in ('original', 'objekt'):
            e = Blendimportaugen(self.ablage, self.inventar(), self.stand['rollen']).schreiben()
            if e:
                self.ergebnis('augen', {**e, 'art': 'original', 'pfad': str(self.ablage.ergebnis(e['datei']))})
                return
        name = ((job.ergebnis or {}).get('fototextur') or {}).get('augen')
        pfad = Meshfigurablage(job.kennung).ergebnis(name) if name else None
        self.ergebnis('augen', {'art': 'genesis', 'pfad': str(pfad) if pfad and pfad.is_file() else None})

    def _modell(self):
        from .blendimportmodell import Blendimportmodell

        e = self.stand.get('ergebnis') or {}
        modell = Blendimportmodell(self.ablage, self.job(), self.stand['quelle']['datei'],
                                   self.stand['einstellungen']['browser_px'], self.zusatzregler())
        name = modell.schreiben(self.stand['quelle']['name'], (e.get('haut') or {}).get('kacheln') or {},
                                (e.get('augen') or {}).get('pfad'), (e.get('stuecke') or {}).get('stuecke') or {})
        self.ergebnis('modell', {'name': name})
