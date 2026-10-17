# -*- coding: utf-8 -*-
"""Meshfigurlauf — ein Auftrag „Mesh to 3D" vom Netz bis zur Genesis-Figur (läuft in `meshfigur_fahren`).

Zwei Welten wechseln sich ab: Die Registrierung rechnet auf der Karte in python10
(`meshto3d/_run_meshfigur.py`, ein Schritt je Aufruf), Genesis 9 lebt hier in
python14 — zwischen den Runden wird die Figur ECHT nachgerechnet (Formelketten, Knochen-
skalierung, Gelenkkorrekturen), bevor die nächste Runde auf ihr aufsetzt.

    erkennung     Netz ausrichten, Landmarken (Körper 33, Gesicht 478), Übersichtsbilder, Vorlagebild
    haar          das Haar aus dem Kopfnetz schneiden (`Meshfigurhaar`, Paket `Haar`)
    kleidung      die Kleidung aus dem Körpernetz schneiden (`Meshfigurkleidung`, Paket `Kleidung`) — Hautton der
                  kahlen Stellen, Bänder, Stücke; das Objekt auf der Figur entsteht am Ende von „vorschau"
    kalibrierung  nur einmal je Rechner: Genesis durch denselben Detektor (`G9netzlandmarken`)
    koerper       Körperkette in Runden (`Meshfigurkette`), dazwischen ggf. auf „Körpergröße"
    gesicht       Gesichtskette (296 Kopfregler, 478 Gesichtspunkte)
    rest          Eigenmorph aus dem Rest (`Meshfigurende`)
    textur        Farbe des Netzes auf die Genesis-Kacheln (`Meshfigurende`)
    vorschau      Bilder, Abstände, Vergleich, Testfall (`Meshfigurvorschau`)
    frisur        Daz-Frisur / „Haar Eigen" gegen das Netzhaar, Haarkarten (`Meshfigurfrisur`)
    speichern     Modell und Ablage in `output/Export/MeshTo3D` (`Meshfigurspeichern`)

Runner-Zeilen: `[fortschritt] <0..100> <Text>` (je Schritt auf sein Band umgerechnet),
`[ergebnis] {…}`, `[fehler] {…}`. Alles, was die Seite zeigt, steht in `job.ergebnis`.
"""

import json
import logging
import time

from django.conf import settings
from django.utils import timezone

from ..daten.meshfigurablage import Meshfigurablage
from ..models import Meshfigurauftrag
from .meshfigurdauerprozess import Meshfigurdauerprozess
from .meshfigurnebenlauf import Meshfigurnebenlauf
from .meshfiguroptionen import Meshfiguroptionen
from .meshfigurrunnerbahn import Meshfigurrunnerbahn

logger = logging.getLogger('core')

__all__ = ['Meshfigurlauf']


class Meshfigurlauf:
    SCHRITTE = ('erkennung', 'haar', 'kleidung', 'kalibrierung', 'koerper', 'gesicht', 'rest', 'textur',
                'vorschau', 'frisur', 'speichern')
    BAENDER = {
        'erkennung': (0, 10),
        'haar': (10, 11),
        'kleidung': (11, 12),
        'kalibrierung': (12, 14),
        'koerper': (14, 62),
        'gesicht': (62, 80),
        'rest': (80, 85),
        'textur': (85, 92),
        'vorschau': (92, 95),
        'frisur': (95, 99),
        'speichern': (99, 100),
    }
    RUNNER = '_run_meshfigur.py'
    #: So lange darf der Runner schweigen (Modelle laden, eine lange Stufe).
    STILLE_S = 900
    #: Schritte, die nur mit Dateien rechnen (CPU, kein Runner) und neben den Ketten in einem Faden laufen: „haar" und „kleidung" brauchen die Erkennung, aber nicht die Körperkette — ihre Zeit
    #: (Zauberer: 80 und 49 s) verschwindet hinter „koerper"/„gesicht"/„rest" (170 s auf der GPU, ein Kern). „frisur" startet, sobald der Runner der Textur die Figur festgelegt hat
    #: (`Meshfigurende.textur` → `nebenlauf_frueh`) und rechnet neben dem Backen der Kacheln und der Vorschau (gemessen 12.10.2026: Frisur 99 s statt 114 s dahinter, die Textur bleibt bei 114 s). Eine Unterklasse mit anderen Voraussetzungen setzt `()`.
    NEBENLAEUFIG = ('haar', 'kleidung', 'frisur')
    #: Ein Nebenlauf, der erst rechnet, wenn ein anderer fertig ist (der Faden wartet, der Hauptfaden nicht — die Ketten laufen weiter): „kleidung" liest die Hutflächen aus `haar_maske.npz`
    #: (13.10.2026: ohne das hing der Hut in der Kleidung davon ab, welcher Faden zuerst fertig war — `Meshfigurnebenlauf.voraussetzungen`). Eine Unterklasse ohne Nebenläufe setzt `{}`.
    NEBEN_NACH = {'kleidung': ('haar',)}
    #: Nach diesen Schritten starten Nebenläufe, die nicht schon früher gestartet sind, vor ihrem Platz in `SCHRITTE` (`nebenlauf_frueh`) — die Figur steht dann fest (`genesis_ende.npz`, `posiert.npy`); gilt, wenn die Textur „aus" ist.
    NACH_SCHRITT = {'textur': ('frisur',)}
    #: Vor diesen Schritten müssen die Nebenläufe fertig sein (sie lesen deren Ergebnis).
    WARTEN_VOR = {'vorschau': ('haar', 'kleidung'), 'frisur': ('haar', 'kleidung'), 'speichern': ('haar', 'kleidung', 'frisur')}

    class Angehalten(Exception):
        """Der Nutzer hat angehalten — kein Fehler, der Lauf endet still."""

    def __init__(self, job_id):
        self.job = Meshfigurauftrag.objects.get(pk=job_id)
        self.ablage = Meshfigurablage(self.job.kennung)
        self.optionen = Meshfiguroptionen.pruefen(self.job.optionen)
        self.zusatz = {}
        self._band = (0, 100)
        self._letzte_db = 0.0
        #: Der python10-Prozess für alle Runner-Schritte dieses Laufs (`Meshfigurdauerprozess`, 12.10.2026) — immer dasselbe Objekt, auch in den Kopien der Nebenläufe.
        self.dauer = Meshfigurdauerprozess()

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self, ab=None):
        from .meshfigurende import Meshfigurende
        from .meshfigurfrisur import Meshfigurfrisur
        from .meshfigurhaar import Meshfigurhaar
        from .meshfigurkette import Meshfigurkette
        from .meshfigurkleidung import Meshfigurkleidung
        from .meshfigurspeichern import Meshfigurspeichern
        from .meshfigurumfangoptionen import Meshfigurumfangoptionen
        from .meshfigurvorschau import Meshfigurvorschau

        # „Nur Rig“ (Option `umfang`, 16.10.2026): das Skelett steht nach der Körperkette — ohne Haar, Kleidung und Frisur (Nebenläufe) und ohne die Schritte danach.
        nur_rig = Meshfigurumfangoptionen.nur_rig(self.optionen)
        job = self.job
        self.ablage.anlegen()
        job.ergebnis = dict(job.ergebnis or {})
        start = self.SCHRITTE.index(ab) if ab in self.SCHRITTE else 0
        # Je Schritt eine Fabrik, die den Lauf bekommt: ein Nebenlauf (unten) rechnet mit einer Kopie des Laufs.
        fabriken = {
            'erkennung': lambda lauf: lauf._erkennung(),
            'haar': lambda lauf: Meshfigurhaar(lauf).ausfuehren(),
            'kleidung': lambda lauf: Meshfigurkleidung(lauf).ausfuehren(),
            'kalibrierung': lambda lauf: lauf._kalibrierung(),
            'koerper': lambda lauf: Meshfigurkette(lauf).koerper(),
            'gesicht': lambda lauf: Meshfigurkette(lauf).gesicht(),
            'rest': lambda lauf: Meshfigurende(lauf).rest(),
            'textur': lambda lauf: Meshfigurende(lauf).textur(),
            'vorschau': lambda lauf: Meshfigurvorschau(lauf).ausfuehren(),
            'frisur': lambda lauf: Meshfigurfrisur(lauf).ausfuehren(),
            'speichern': lambda lauf: Meshfigurspeichern(lauf).ausfuehren(),
        }
        t0 = time.perf_counter()
        nebenlaeufe = {}
        self._laufend = (nebenlaeufe, fabriken)             # für `nebenlauf_frueh`
        try:
            for name in self.SCHRITTE[start:]:
                if nur_rig and name in self.NEBENLAEUFIG:
                    continue
                self._nebenlaeufe_abwarten(nebenlaeufe, self.WARTEN_VOR.get(name, ()))
                self._schritt(name)
                if name in self.NEBENLAEUFIG:
                    if name not in nebenlaeufe:             # „frisur" läuft meist schon (`nebenlauf_frueh`)
                        nebenlaeufe[name] = self._nebenlauf(name, fabriken[name])
                    continue
                t = time.perf_counter()
                fabriken[name](self)
                job.ergebnis.setdefault('dauer', {})[name] = round(time.perf_counter() - t, 1)
                self.sichern('ergebnis')
                for folge in self.NACH_SCHRITT.get(name, ()):
                    self.nebenlauf_frueh(folge)
                if nur_rig and name == Meshfigurumfangoptionen.RIG_BIS:
                    break
            self._nebenlaeufe_abwarten(nebenlaeufe, tuple(nebenlaeufe))
        except self.Angehalten:
            logger.info('Mesh to 3D %s: angehalten', job.kennung)
            return
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler beendet den Lauf sichtbar
            logger.exception('Mesh to 3D %s: Schritt %s gescheitert', job.kennung, job.schritt)
            self._scheitern('%s: %s' % (job.schritt, fehler))
            return
        finally:
            for faden, _proxy, _erg in nebenlaeufe.values():       # ein Abbruch lässt keinen Faden zurück, der noch Dateien schreibt
                faden.join()
            self.dauer.schliessen()                                  # der Runner-Prozess endet mit dem Lauf (GPU-Speicher frei für den nächsten Schritt des Imports)
        job.ergebnis['dauer_s'] = round(time.perf_counter() - t0, 1)
        job.status = 'fertig'
        job.progress = 100
        job.progress_detail = 'Fertig'
        job.finished_at = timezone.now()
        job.save(
            update_fields=['ergebnis', 'status', 'progress', 'progress_detail', 'finished_at', 'updated_at']
        )
        logger.info('Mesh to 3D %s: fertig in %.0f s', job.kennung, job.ergebnis['dauer_s'])

    def _schritt(self, name):
        if Meshfigurauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists():
            raise self.Angehalten()
        self._band = self.BAENDER[name]
        self.job.schritt = name
        self.job.save(update_fields=['schritt', 'updated_at'])
        self.melden(0, name)

    def _nebenlauf(self, name, fabrik):
        """Den Schritt `name` in einem Faden starten (`Meshfigurnebenlauf.starten`): Kopie des Auftrags, keine Fortschrittsmeldung; der Faden wartet auf die Fäden aus `NEBEN_NACH`."""
        laufend = getattr(self, '_laufend', None)
        return Meshfigurnebenlauf.starten(self, name, fabrik, Meshfigurnebenlauf.voraussetzungen(self, laufend[0] if laufend else {}, name))

    def _nebenlaeufe_abwarten(self, nebenlaeufe, namen):
        """Wartet auf die Nebenläufe `namen` und übernimmt ihr Ergebnis in `job.ergebnis` (`Meshfigurnebenlauf.abwarten`)."""
        Meshfigurnebenlauf.abwarten(self, nebenlaeufe, namen)

    def nebenlauf_frueh(self, name):
        """Der Nebenlauf `name` startet schon vor seinem Platz in `SCHRITTE` (`NACH_SCHRITT`); ohne laufendes `ausfuehren` (2D3D Kleider) geschieht nichts."""
        return Meshfigurnebenlauf.frueh(self, name)

    def sichern(self, *felder):
        self.job.save(update_fields=list(felder) + ['updated_at'])

    def melden(self, anteil, text):
        """Fortschritt im Band des Schritts — höchstens zweimal je Sekunde in die Datenbank."""
        jetzt = time.monotonic()
        if jetzt - self._letzte_db < 0.5 and anteil < 1.0:
            return
        self._letzte_db = jetzt
        von, bis = self._band
        self.job.progress = max(self.job.progress or 0, int(von + (bis - von) * max(0.0, min(1.0, anteil))))
        self.job.progress_detail = str(text)[:200]
        self.sichern('progress', 'progress_detail')

    # --------------------------------------------------------------- Runner

    def auftrag(self):
        """`arbeit/auftrag.json` — Netz, Ordner, Optionen und was die Schritte dazulegen."""
        pfad = self.ablage.arbeit('auftrag.json')
        netz = self.ablage.netzdatei()
        if netz is None:
            raise RuntimeError('Kein Netz im Eingang')
        daten = {
            'kennung': self.job.kennung,
            'name': self.job.name,
            'netz': str(netz),
            'optionen': dict(self.optionen, daempfung_wert=Meshfiguroptionen.daempfung(self.optionen)),
            'ordner': {'arbeit': str(self.ablage.arbeit()), 'ergebnis': str(self.ablage.ergebnis())},
            **self.zusatz,
        }
        kopf = self.kopfnetz()
        if kopf is not None:
            daten['kopfnetz'] = str(kopf)
        pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding='utf-8')
        return pfad

    def kopfnetz(self):
        """Das Kopfnetz, das der Runner einsetzen soll, oder None: hier das Netz aus `eingang['kopf']` („Mesh to 3D", Schalter „Kopfnetz verwenden"); „2D3D Kleider" nimmt das des Schritts „kopf" (`Engine2d3dKleiderkoerperlauf`)."""
        return self.ablage.netzdatei('kopf') if (self.job.eingang or {}).get('kopf') else None

    def runner(self, schritt, runde=None, von=0.0, bis=1.0):
        """Einen Schritt des Runners rechnen — sein `[ergebnis]` (dict) oder ein Fehler. Im Dauerprozess des Laufs (`self.dauer`), sonst in einem eigenen (`Meshfigurrunnerbahn`)."""
        return Meshfigurrunnerbahn(self).rechnen(schritt, runde, von, bis)

    def umgebung(self):
        """Zwischendateien im Auftrag (nie System-Temp), Modelle aus der Projektablage."""
        tmp = self.ablage.arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        return {
            'TMP': str(tmp),
            'TEMP': str(tmp),
            'HF_HOME': str(settings.HF_HOME_DIR),
            'TORCH_HOME': str(settings.VIDEOTOBVH_ROOT / 'models' / 'torch_hub'),
            'PYTHONIOENCODING': 'utf-8',
        }

    # ------------------------------------------------------------- Schritte

    def _erkennung(self):
        e = self.runner('erkennung')
        self.job.ergebnis['erkennung'] = e
        self.job.ergebnis['vorlage'] = self.vorlage()

    def vorlage(self):
        """Tabellenbild des Körpernetzes (`ergebnis/vorlage.png`, Edgar 27.09.2026: „eine Spalte
        für die Vorlage … so ähnlich wie bei #mesh"), von vorn in der Lage der Erkennung — hier
        in python14 gerendert wie `Meshicon` im Reiter „Mesh". None, wenn es scheitert."""
        import numpy as np

        from .meshicon import Meshicon

        lage, matrix = self.ablage.arbeit('scan_lage.npz'), None
        if lage.is_file():
            with np.load(lage) as d:
                matrix = d['matrix']
        netz = self.ablage.netzdatei()
        return Meshicon.schreiben(netz, self.ablage.ergebnis(), Meshicon.VORLAGE, matrix) or None

    def _kalibrierung(self):
        """Genesis durch denselben Detektor — nur, wenn die Tabelle auf diesem Rechner fehlt."""
        import numpy as np
        from Genesis9.figurglb import G9figurglb
        from Genesis9.netzlandmarken import G9netzlandmarken

        from .meshfigurregler import Meshfigurregler

        if G9netzlandmarken.holen() is not None:
            self.job.ergebnis['kalibrierung'] = {'vorhanden': True, **G9netzlandmarken.holen().steckbrief()}
            return
        grund = Meshfigurregler.GRUNDFIGUREN['feminine']
        G9figurglb(grund).schreiben(self.ablage.arbeit('genesis_kalibrierung.glb'))
        self.runner('kalibrierung')
        with np.load(self.ablage.arbeit('kalibrierung.npz')) as d:
            tabelle = G9netzlandmarken.bauen(grund, d['koerper'], d['gesicht'], d['gesicht_treffer'])
        tabelle.speichern()
        self.job.ergebnis['kalibrierung'] = {'vorhanden': False, **tabelle.steckbrief()}

    def _scheitern(self, text):
        job = self.job
        job.refresh_from_db()
        if job.status == 'angehalten':
            return
        job.status = 'gescheitert'
        job.error_message = text[:4000]
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at', 'updated_at'])
