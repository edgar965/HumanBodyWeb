# -*- coding: utf-8 -*-
"""Blendimportlauf — ein Modell-Import von der .blend (oder OBJ/FBX) bis zum Genesis-Modell (läuft in `blendimport_fahren`).

Konzept und Messungen: Hilfe → Architektur → Genesis (08.10.2026). Die Schritte:

    umwandeln nur OBJ und FBX (`Blendimportformate`): Blender macht die Datei zur `quelle.blend` (`Blendimportumwandeln`); ab
              „export" ist alles wie bei einer .blend — dieselbe Kette für alle drei Formate (10.10.2026)
    export    Blender liest die .blend (`blendexport.py`): je Netz Punkte, Dreiecke, UV, Bilder; Rollen (`Blendimportrollen`)
    koerper   Körper + Augen als GLB mit einer Textur (`Blendimportkoerper`)
    figur     „Mesh to 3D" auf diesem Körper: Regler, Gesicht, Eigenmorph (`Blendimportfigur`, eigener Auftrag)
    finger    die Finger der Figur an die Hände des Originals anpassen (`Blendimportfinger`, 10.10.2026); Griff für das Requisit in der Hand
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
from .blendimportformate import Blendimportformate

logger = logging.getLogger('core')

__all__ = ['Blendimportlauf']


class Blendimportlauf:
    SCHRITTE = ('umwandeln', 'export', 'umposen', 'koerper', 'figur', 'finger', 'stuecke', 'haut', 'augen', 'modell')
    BAENDER = {'umwandeln': (0, 2), 'export': (2, 3), 'umposen': (3, 5), 'koerper': (5, 7), 'figur': (7, 70), 'finger': (70, 72),
               'stuecke': (72, 80), 'haut': (80, 95), 'augen': (95, 97), 'modell': (97, 100)}

    class Angehalten(Exception):
        """Der Nutzer hat angehalten."""

    @classmethod
    def schritte_fuer(cls, format):
        """Die Schritte eines Formats: „umwandeln" gibt es nur, wenn Blender die Datei erst zur .blend machen muss."""
        return tuple(s for s in cls.SCHRITTE if s != 'umwandeln' or Blendimportformate.umwandeln(format))

    def __init__(self, kennung):
        self.ablage = Blendimportablage(kennung)
        self.stand = self.ablage.stand()
        self.format = Blendimportformate.pruefen((self.stand.get('quelle') or {}).get('format'))
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

    def blend(self):
        """Die .blend, die Blender liest: bei OBJ/FBX die umgewandelte (`quelle.blend` in der Ablage), sonst die Datei selbst.
        `quelle.datei` bleibt die Datei des Nutzers — sie steht im Modell als Herkunft (`Blendimportmodell`)."""
        quelle = self.stand['quelle']
        return quelle.get('blend') or quelle['datei']

    def job(self):
        from ..models import Meshfigurauftrag

        figur = (self.stand.get('ergebnis') or {}).get('figur') or {}
        if not figur.get('id'):
            raise RuntimeError('Kein Auftrag „Mesh to 3D" — Schritt „figur" zuerst')
        return Meshfigurauftrag.objects.get(pk=figur['id'])

    # ------------------------------------------------------------ Ablauf

    def ausfuehren(self, ab=None):
        self.ablage.anlegen()
        schritte = self.schritte_fuer(self.format)
        start = schritte.index(ab) if ab in schritte else 0
        # `schritte` im Stand: die Seite zeigt genau die Schritte DIESES Imports (eine .blend hat kein „umwandeln").
        self.sichern(status='laeuft', fehler='', gestartet=timezone.now().isoformat(), ab=schritte[start], schritte=list(schritte))
        t0 = time.perf_counter()
        try:
            for name in schritte[start:]:
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

    def _umwandeln(self):
        from .blendimportumwandeln import Blendimportumwandeln

        quelle = self.stand['quelle']
        if not Blendimportformate.umwandeln(self.format):
            self.ergebnis('umwandeln', {'aus': True, 'grund': 'Die Datei ist schon eine .blend'})
            return
        bericht = Blendimportumwandeln(self.ablage, self.melden).wandeln(quelle['datei'], self.format)
        self.sichern(quelle={**quelle, 'blend': str(self.ablage.quelle_blend())})
        self.ergebnis('umwandeln', bericht)

    def _export(self):
        from .blendimportblender import Blendimportblender
        from .blendimportkoerperpruefung import Blendimportkoerperpruefung
        from .blendimportplausibel import Blendimportplausibel
        from .blendimportrollen import Blendimportrollen

        Blendimportblender(self.ablage, self.melden).laufen(
            'blendexport.py', self.blend(), ['--ziel', self.ablage.export()],
            self.ablage.export('inventar.json'))
        inventar = self.inventar()
        rollen = Blendimportrollen(inventar).zuordnen()
        self.sichern(rollen=rollen)
        # Wächter (10.10.2026, Rosemary Winters): deckt der Körper die ganze Figur? Sonst hält der Lauf HIER an (5 s) statt nach Stunden an einer
        # Figur zu enden, die nicht passt — das Ergebnis steht im Bericht, auch wenn der Import trotzdem weiterläuft.
        koerper = Blendimportkoerperpruefung.pruefen(inventar, rollen, self.stand['einstellungen'].get('unvollstaendig') == 'weiter')
        # Unabhängig von der Ursache: ist die Figur nach dem Maßstab keine menschliche Höhe, hält der Lauf hier an (Rainy, seori, Rosemary: 3,1–3,3 m).
        Blendimportplausibel.pruefen(Blendimportplausibel.figurhoehe(koerper))
        self.ergebnis('export', {'netze': len(rollen), 'koerper': koerper})

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
            bericht = Blendimportumposen(self.ablage, self.melden).umposen(self.blend())
        except RuntimeError as fehler:
            # Ein anderes Rig als Auto-Rig Pro (Daven.blend, Character Creator: Rigs `Armature` + `CC3_Base_Plus`, 09.10.2026): das
            # Blender-Skript endet ohne Ergebnis. Die Haltung der Datei gilt dann — wie bei `umposen = aus`, der Grund steht im Ergebnis.
            logger.warning('Blender-Import %s: Umposen gescheitert, Haltung der Datei gilt: %s', self.ablage.kennung, str(fehler)[:300])
            bericht = {'aus': True, 'grund': 'Umposen gescheitert: %s' % str(fehler)[:300]}
        self.ergebnis('umposen', bericht)

    def _koerper(self):
        from .blendimportkoerper import Blendimportkoerper

        ergaenzen = self.stand['einstellungen'].get('koerper_ergaenzen') == 'an'
        self.ergebnis('koerper', Blendimportkoerper(self.ablage, self.inventar(), self.stand['rollen'], ergaenzen).schreiben())

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
            bericht = {'aus': 'Scham kommt als Stück (Einstellung scham = objekt)'}
        else:
            try:
                bericht = Blendimportnachformung(self.ablage, job, self.inventar(), self.stand['rollen'],
                                                 self.stand['quelle']['name'], self.melden).formen()
            except Exception as fehler:  # noqa: BLE001 — Zusatzschritt: der Import läuft mit der Figur der Anpassung weiter
                logger.exception('Blender-Import %s: Nachformung gescheitert', self.ablage.kennung)
                bericht = {'fehler': str(fehler)[:300]}
        self.ergebnis('nachformung', self._unterkleid(job, bericht))

    def _unterkleid(self, job, bericht):
        """Die Haut hinter die Kleidung legen (`Blendimportunterkleid`, 10.10.2026: Rainys Haut stand am Schritt bis 62 mm vor der Hose). Der
        Regler kommt zu denen der Nachformung (`regler`), auch wenn sie `aus` ist; ein Fehler beendet den Import nicht."""
        from .blendimportunterkleid import Blendimportunterkleid

        # Wiederholbar: die Haut wird auf der Figur OHNE den eigenen Regler eines früheren Laufs gelegt.
        eigene = {k: v for k, v in (bericht.get('regler') or {}).items() if not k.endswith(Blendimportunterkleid.ENDUNG)}
        try:
            unter = Blendimportunterkleid(self.ablage, job, self.inventar(), self.stand['rollen'], self.stand['quelle']['name'],
                                          self.melden).formen(eigene)
        except Exception as fehler:  # noqa: BLE001 — Zusatzschritt: die Figur gilt dann, wie „Mesh to 3D" sie gebaut hat
            logger.exception('Blender-Import %s: Haut unter die Kleidung gescheitert', self.ablage.kennung)
            unter = {'fehler': str(fehler)[:300]}
        regler = {**eigene, **(unter.pop('regler', None) or {})}
        return {**{k: v for k, v in bericht.items() if k != 'regler'}, 'unterkleid': unter, **({'regler': regler} if regler else {})}

    def _finger(self):
        """Die Finger an die Hände des Originals anpassen (`Blendimportfinger`); ein Fehler beendet den Import nicht — die Hände bleiben gestreckt."""
        from .blendimportfinger import Blendimportfinger

        try:
            bericht = Blendimportfinger(self.ablage, self.job(), self.inventar(), self.stand['rollen'], self.zusatzregler(), self.melden).rechnen()
        except Exception as fehler:  # noqa: BLE001 — Zusatzschritt: die Figur gilt dann, wie „Mesh to 3D" sie gebaut hat
            logger.exception('Blender-Import %s: Finger gescheitert', self.ablage.kennung)
            bericht = {'aus': True, 'fehler': str(fehler)[:300]}
        self.ergebnis('finger', bericht)

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
        from .blendimportplausibel import Blendimportplausibel

        haut = Blendimporthaut(self.ablage, self.job(), self.inventar(), self.stand['rollen'],
                               self.stand['einstellungen']['kachel_px'], self.melden,
                               self.stand['einstellungen'].get('normalen_grenze'), self.zusatzregler(),
                               self.stand['einstellungen'].get('normalen_form') or 'weg')
        # Der Abstand Körper ↔ Figur wird vor dem Backen gemessen: passt die Figur nicht, hält der Lauf dort an (statt nach 20–40 Minuten „fertig").
        trotzdem = self.stand['einstellungen'].get('unvollstaendig') == 'weiter'
        kacheln, bericht = haut.backen(self.blend(), lambda abstand: Blendimportplausibel.pruefen(Blendimportplausibel.abstand(abstand), trotzdem))
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
