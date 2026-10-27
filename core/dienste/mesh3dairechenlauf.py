# -*- coding: utf-8 -*-
"""Mesh3dairechenlauf — EIN Lauf mit festen Schritten: Mesh rein → Testseite fertig (23.10.2026, Edgar: „Die Rechenkette gehört ins Projekt … Knopf auf der Seite: Mesh hochladen,
„Rechnen“, Fortschritt sehen“ — „tu das, aber schnell und mit EINEM Testjob“).

Bis heute entstand jedes Ergebnis aus Bash-Ketten unter `ProjektTemp/_wegwerf/` (`mesh3dai_test_einzeln2.sh`, `mesh3dai_kostuem_lauf.py`, …), deren Skripte ihre Netze selbst wählten. Hier stehen
die Schritte fest, in dieser Reihenfolge, mit den Netzen aus `Mesh3daikifassungen`; Stand und Log liegen im Testordner (`rechnen/stand.json`, `rechnen/lauf.log`), die Seite fragt den Stand ab.
**Der Rechencode liegt seit 23.10.2026 nachts im Projekt, `A:\\3DTools\\mesh3dai\\`** (Edgar: „Die 8 Schritte rufen noch die Skripte unter ProjektTemp/_wegwerf/ auf … mach alles“): die 185 Module,
die die Schritte brauchen, aus `_wegwerf/` kopiert (`ProjektTemp/_wegwerf/rechenkette_ins_projekt.py`; `sys.path`, Unterprozesse und Arbeitsverzeichnis zeigen auf den neuen Ordner, Daten wie `teile.pkl`,
GPU-Sperre und Ablagen bleiben, wo sie sind). Änderungen an der Kette gehören dorthin; die Originale in `_wegwerf/` sind das Archiv der Versuche und laufen hier nicht mehr.
GPU: jeder Schritt nimmt die Sperre selbst (`mesh3dai_stimmen_lauf.py`, `Gpusperre`); Warteschlange: `Mesh3dairechenschlange` (ein Lauf zur Zeit).

    Mesh3dairechenlauf(kennung).ausfuehren()      # im Arbeitsprozess (`manage.py mesh3dai_rechnen`)
"""
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

from django.conf import settings

from core.atomic_write import AtomarSchreiber

from .mesh3daikifassungen import Mesh3daikifassungen

logger = logging.getLogger('core')

__all__ = ['Mesh3dairechenlauf']


class Mesh3dairechenlauf:
    #: (Schlüssel, Klartext, Skript und Argumente — {k} Kennung, {…} aus den KI-Fassungen)
    SCHRITTE = (
        ('rig', 'Rig und A-Pose (Make-It-Animatable, Netz der Vorstufe)', ['-u', 'mesh3dai_vorstufe.py', 'test', '{k}', '--weg', 'mia', '--netz-mia', '{vorstufe_mia_pfad}',
                                                                                  '--netz', '{vorstufe_pfad}']),
        ('haltung', 'Haltung aus der KI', ['mesh3dai_stimmen_lauf.py', 'mesh3dai_test_form.py', '--vorhersagen', '--lauf', '{haltung}', '--nur', '{k}']),
        ('form', 'Form aus der KI (Genesis-Regler)', ['mesh3dai_stimmen_lauf.py', 'mesh3dai_test_form_apose.py', '--lauf', '{formkopf}', '--als-form', '--nur', '{k}']),
        ('figur', 'Figur bauen', ['mesh3dai_formfigur.py', '--parallel', '2', '--nur', '{k}']),
        ('anpassen', 'Figur in die Haltung legen', ['mesh3dai_stimmen_lauf.py', 'mesh3dai_test_form.py', '--anpassen', '--nur', '{k}']),
        ('haltung2', 'Haltung aus Gelenken und Enden', ['mesh3dai_stimmen_lauf.py', 'mesh3dai_test_form_haltung.py', '--nur', '{k}']),
        ('segmentierung', 'Bilderkennung vorbereiten (Sapiens2 + SAM 3)', ['mesh3dai_kostuem_segmentierung.py', '{k}']),
        # Haut aus der KI (23.10.2026 nachts, Edgar: „Haut: Die Haut-KI ist nicht angebunden“ → „mach alles“): Stufe 2 braucht die Zerlegung des Tests; sie schreibt `haut_<g>/` und Stücke des
        # Wegs g — die Kleider der Seite kommen danach aus dem Kostüm-Weg (der Schritt danach schreibt `ki.json` neu, die Wahl je Stück bleibt „k“).
        ('zerlegung', 'Zerlegung aus der KI (Haut, Haar, Kleidungsstücke je Punkt)', ['mesh3dai_stimmen_lauf.py', 'mesh3dai_kleider_zerlegung.py', '--nur', '{k}', '--lauf', '{zerlegung}']),
        # Kopf an das Mesh (24.10.2026, Edgar: „eine Logik … NACH dem Kopfnetz, die noch ein paar weitere Iterationen macht falls zu weit auseinander, und das Tripo nutzt in Zusammenspiel mit den
        # Messungen der Nase usw. und den Genesis reglern“): Kopfnetz, dann die Kopfregler gegen Gesichtsmaße, Landmarken und Haut des Eingangs (`Kopfangleich`); braucht Haltung und Zerlegung,
        # baut bei Übernahme die Figur neu und rechnet „anpassen“ und „haltung2“ selbst nach — die Haut danach liegt schon auf dem neuen Kopf
        ('kopf', 'Kopf an das Mesh angleichen (Kopfnetz, Gesichtsmaße, Haut — in Runden)', ['-u', 'mesh3dai_kopfangleich_lauf.py', '--nur', '{k}', '--geschlecht', '{g}', '--kopfnetz', '{kopfnetz}']),
        # Haltung an den Eingang (24.10.2026 nachts, Edgar zu randy: „rumpf nun zu groß … mit mediapipe, rechne das aus … und korrigiere“): ViTPose an Eingang und Figur aus vier Richtungen,
        # Versatz je Gelenk in die Ziele der Winkelanpassung, in Runden (`Lageangleich`); NACH „kopf“, weil dessen Neubau die Ziele ändert (die Korrektur gilt nur für die gemessenen)
        ('lage', 'Haltung an den Eingang angleichen (Messpunkte an Eingang und Figur, in Runden)', ['-u', 'mesh3dai_lageangleich_lauf.py', '--nur', '{k}']),
        # Körper in die Außenmaße des Eingangs (25.10.2026, Edgar: „Körper muss in die aussenmasse reinkommen“, „Warum machst du keine Angleichungen für den Körper??“): Körperregler,
        # Proportionen und Haltung gegen Umriss, Haut und anliegenden Stoff des Eingangs (`Koerperangleich`); NACH „lage“ (er schreibt die Haltung selbst, eine Winkelanpassung danach nähme sie
        # zurück) und VOR „haut“ (die Haut-KI liest die Figur)
        ('koerper', 'Körper in die Außenmaße des Eingangs (Form, Proportionen, Haltung — in Runden)', ['-u', 'mesh3dai_koerperangleich_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
        # `--hautki` (24.10.2026 abends): steht in den KI-Fassungen ein Lauf der Haut-KI im Bildraum, schreibt sie die Hautkacheln (`Hautkieinsatz`), sonst das Netz `haut` von Stufe 2
        ('haut', 'Haut aus der KI (Stufe 2: Farbe je Texel)', ['-u', 'mesh3dai_stufe2_lauf.py', '--nur-einsatz', '{stufe2}', '--fassung', '{stufe2_fassung}', '--test', '{k}', '--job', '',
                                                                '--geschlecht', '{g}', '--hautki', '{hautki}']),
        ('kleider', 'Kleider und Haar aus dem Mesh ausschneiden und auflegen, Hautmasken, Prüfung', ['-u', 'mesh3dai_kostuem_lauf.py', '--nur', '{k}', '--stufe', '{kostuem_stufe}']),
    )
    #: Schritt „form“ aus der Regler-KI statt aus dem Formkopf — nur für einen Test, dessen `einstellung.json` es nennt (`form_ki`: {"art": "reglerki", "lauf": <Lauf unter
    #: `_reglerki/laeufe`>}), nie als Vorgabe (27.10.2026, Edgar: „ich will bei einem Trainings oder Testjob mal ergebnisse sehen“)
    FORM_REGLERKI = ('form', 'Form aus der Regler-KI (Genesis-Regler, Hauptregler und Anfasser)', ['-u', 'mesh3dai_reglerki_test.py', '--lauf', '{reglerki_lauf}', '--als-form', '--nur', '{k}'])
    #: Rückfall (27.10.2026, Edgar: „In der Kette automatisch auf den Formkopf zurückfallen, sobald MIA durchfällt“): die Regler-KI kennt nur MIAs A-Pose; stammt die jüngste A-Pose vom Rig
    #: (MIAs Prüfung nicht bestanden) und hat der gewählte Lauf den Weg „Rig“ nicht gelernt (`reglerki_wege`), rechnet der Schritt „form“ mit dem Formkopf der KI-Fassungen
    RUECKFALL_TEXT = 'Form aus der KI (Formkopf) — Rückfall: MIAs A-Pose ist durch die Prüfung gefallen, die Regler-KI kennt nur MIAs A-Pose'
    #: Was ein Schritt im Log schreibt, wenn er scheitert, ohne mit einem Fehlercode zu enden (die Kostüm-Kette fängt Fehler je Test ab)
    FEHLERZEILEN = ('GESCHEITERT', 'Traceback (most recent call last)')
    HAUT = 'Haut: aus der KI (Stufe 2, Lauf in den KI-Fassungen) für das eingestellte Geschlecht; das andere Geschlecht trägt die Grundhaut.'

    def __init__(self, kennung):
        from .mesh3daitest import Mesh3daitest
        self.kennung = str(kennung)
        self.test = Mesh3daitest.ordner() / self.kennung
        self.ordner = self.test / 'rechnen'

    @staticmethod
    def kette():
        """Ordner des Rechencodes (Arbeitsverzeichnis jedes Schritts)."""
        return Path(settings.TOOLS_ROOT) / 'mesh3dai'

    def form_ki(self):
        """`{'art': 'reglerki', 'lauf': …}` aus `einstellung.json` des Tests oder None (dann der Formkopf der KI-Fassungen)."""
        try:
            wahl = json.loads((self.test / 'einstellung.json').read_text(encoding='utf-8')).get('form_ki')
        except (OSError, ValueError):
            return None
        return wahl if isinstance(wahl, dict) and wahl.get('art') == 'reglerki' and wahl.get('lauf') else None

    def schritte(self):
        """Die Schritte dieses Tests: `SCHRITTE`, mit `FORM_REGLERKI`, wenn der Test die Regler-KI wählt."""
        if self.form_ki() is None:
            return self.SCHRITTE
        return tuple(self.FORM_REGLERKI if s[0] == 'form' else s for s in self.SCHRITTE)

    def mia_apose(self):
        """Ob die jüngste A-Pose der Vorstufe von MIA stammt (`apose.npz` → `weg` = 'mia'); dieselbe Kette wie `Kleiderzerlegung.kette`, die auch die Regler-KI liest."""
        import numpy as np
        ketten = sorted(p.parent for p in (self.test / 'vorstufe').glob('*/apose.npz'))
        if not ketten:
            return False
        with np.load(ketten[-1] / 'apose.npz') as ap:
            return 'weg' in ap.files and str(ap['weg']) == 'mia'

    def reglerki_wege(self):
        """Die Wege der A-Pose, die der gewählte Lauf der Regler-KI gelernt hat (`lauf_ergebnis.json` → `wege`; Läufe bis 27.10.2026 nur MIA)."""
        try:
            datei = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_reglerki' / 'laeufe' / self.form_ki()['lauf'] / 'lauf_ergebnis.json'
            return list(json.loads(datei.read_text(encoding='utf-8')).get('wege') or ['mia'])
        except (OSError, ValueError, TypeError):
            return ['mia']

    def stand(self):
        try:
            return json.loads((self.ordner / 'stand.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    def _schreiben(self, stand):
        self.ordner.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(self.ordner / 'stand.json', stand)

    def vorbereiten(self, status='wartet', ab=None):
        """Stand „wartet“ mit allen Schritten — vor dem Start, damit die Seite sofort die Liste zeigt. `ab` (Schlüssel eines Schritts): die Schritte davor rechnet der Lauf nicht neu, ihr Ergebnis
        liegt schon im Testordner (23.10.2026 nachts: ein neuer Haut-Schritt soll nicht das Rig von 4 min wiederholen)."""
        schluessel = [s for s, _t, _a in self.schritte()]
        if ab is not None and ab not in schluessel:
            raise ValueError('Schritt „%s“ gibt es nicht (%s)' % (ab, ', '.join(schluessel)))
        alt = {s.get('schluessel'): s for s in (self.stand() or {}).get('schritte', [])} if ab else {}
        vor = set(schluessel[:schluessel.index(ab)]) if ab else set()
        stand = {'kennung': self.kennung, 'status': status, 'angefragt': time.strftime('%Y-%m-%dT%H:%M:%S'), 'fassungen': Mesh3daikifassungen.lesen(), 'haut': self.HAUT, 'ab': ab,
                 'schritte': [dict(alt.get(s) or {}, schluessel=s, text=t, status='fertig', uebernommen=True) if s in vor else {'schluessel': s, 'text': t, 'status': 'offen'}
                              for s, t, _a in self.schritte()]}
        self._schreiben(stand)
        self._warteschlange_eintragen()
        return stand

    def _warteschlange_eintragen(self):
        """Eintrag dieses Laufs in `ProjektTemp/mia_daten/warteschlange.json` (jede Kette braucht dort einen, sonst steht sie in „Lauf Aktuell“ nur unter „nicht beschrieben“): Log, Endmarke, je Schritt
        die Marke, die `ausfuehren` ins Log schreibt. Ein Fehler hier hält keinen Lauf auf."""
        import os
        try:
            datei = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / 'mia_daten' / 'warteschlange.json'
            plan = json.loads(datei.read_text(encoding='utf-8')) if datei.is_file() else {'ketten': []}
            log = os.path.relpath(self.ordner / 'lauf.log', datei.parent).replace('\\', '/')
            schritte = [{'marke': '== %d %s' % (nr + 1, text), 'titel': text,
                         'prozess': next((a[:-3] for a in roh if a.endswith('.py') and a != 'mesh3dai_stimmen_lauf.py'), roh[0])} for nr, (_s, text, roh) in enumerate(self.schritte())]
            eintrag = {'skript': 'mesh3dai_rechnen', 'titel': 'Rechnen per Knopf: Test „%s“' % self.kennung, 'log': log, 'ende': 'RECHENLAUF FERTIG', 'schritte': schritte}
            plan['ketten'] = [k for k in plan.get('ketten', []) if k.get('log') != log] + [eintrag]
            AtomarSchreiber.json_schreiben(datei, plan)
        except (OSError, ValueError) as fehler:
            logger.warning('Mesh3D-AI Rechenlauf %s: Warteschlange nicht eingetragen (%s)', self.kennung, fehler)

    def _geschlecht(self):
        """Das eingestellte Geschlecht des Tests (`einstellung.json`, sonst `test.json` → `geschlecht_vorgabe`) — wie `Kostuemlauf.geschlecht`; gelesen erst, wenn ein Schritt es braucht."""
        for datei, feld in (('einstellung.json', 'geschlecht'), ('test.json', 'geschlecht_vorgabe'), ('anlage.json', 'geschlecht')):
            try:
                g = json.loads((self.test / datei).read_text(encoding='utf-8')).get(feld)
            except (OSError, ValueError):
                continue
            if g in ('weiblich', 'maennlich'):
                return g
        return 'weiblich'

    def _argumente(self, roh, f):
        werte = dict(f, k=self.kennung, vorstufe_mia_pfad=str(Mesh3daikifassungen.vorstufe_pfad(f['vorstufe_mia'])),
                     vorstufe_pfad=str(Mesh3daikifassungen.vorstufe_pfad(f['vorstufe'])))
        if any('{g}' in a for a in roh):
            werte['g'] = self._geschlecht()
        if any('{reglerki_lauf}' in a for a in roh):
            werte['reglerki_lauf'] = self.form_ki()['lauf']
        return [a.format(**{x: str(y) for x, y in werte.items()}) for a in roh]

    def ausfuehren(self):
        """Alle Schritte der Reihe nach; hält beim ersten Fehler an. → Stand."""
        f = Mesh3daikifassungen.lesen()
        stand = self.stand() or self.vorbereiten()
        stand.update(status='laeuft', beginn=time.strftime('%Y-%m-%dT%H:%M:%S'), fassungen=f, fehler=None)
        self._schreiben(stand)
        log = self.ordner / 'lauf.log'
        t_alles = time.perf_counter()
        with open(log, 'a', encoding='utf-8') as aus:
            aus.write('\n==== Lauf %s, KI-Fassungen %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), json.dumps(f, ensure_ascii=False)))
            for nr, (schluessel, text, roh) in enumerate(self.schritte()):
                eintrag = stand['schritte'][nr]
                if eintrag.get('uebernommen'):
                    aus.write('== %d %s %s (übernommen, nicht neu gerechnet)\n' % (nr + 1, text, time.strftime('%H:%M:%S')))
                    continue
                if roh is self.FORM_REGLERKI[2] and not self.mia_apose() and 'rig' not in self.reglerki_wege():
                    text, roh = self.RUECKFALL_TEXT, next(s[2] for s in self.SCHRITTE if s[0] == 'form')
                    eintrag['text'] = text
                eintrag.update(status='laeuft', beginn=time.strftime('%H:%M:%S'))
                stand['schritt'] = nr + 1
                self._schreiben(stand)
                befehl = [sys.executable] + self._argumente(roh, f)
                aus.write('== %d %s %s\n%s\n' % (nr + 1, text, time.strftime('%H:%M:%S'), ' '.join(befehl)))
                aus.flush()
                t0 = time.perf_counter()
                zeilen, rc = self._schritt(befehl, aus)
                eintrag['dauer_s'] = round(time.perf_counter() - t0, 1)
                if rc != 0:
                    fehler = 'Fehlercode %d — %s' % (rc, ' / '.join(zeilen[-5:]))
                else:
                    fehler = next((z for z in zeilen if any(m in z for m in self.FEHLERZEILEN)), None)
                if fehler:
                    eintrag['status'] = 'fehler'
                    stand.update(status='fehler', fehler='Schritt „%s“: %s' % (text, fehler), ende=time.strftime('%Y-%m-%dT%H:%M:%S'),
                                 dauer_s=round(time.perf_counter() - t_alles, 1))
                    self._schreiben(stand)
                    logger.warning('Mesh3D-AI Rechenlauf %s: %s', self.kennung, stand['fehler'])
                    return stand
                eintrag['status'] = 'fertig'
                self._schreiben(stand)
            aus.write('RECHENLAUF FERTIG %s\n' % time.strftime('%H:%M:%S'))         # Endmarke der Warteschlange (`warteschlange.json`)
        stand.update(status='fertig', ende=time.strftime('%Y-%m-%dT%H:%M:%S'), dauer_s=round(time.perf_counter() - t_alles, 1))
        self._schreiben(stand)
        logger.info('Mesh3D-AI Rechenlauf %s fertig in %.0f s', self.kennung, stand['dauer_s'])
        return stand

    @classmethod
    def _skriptdienst(cls):
        """`Skriptdienstruf` aus dem Rechencode (24.10.2026: ein Dauerprozess je Umgebung, Importe einmal geladen) — geladen über den Dateipfad, ohne `sys.path` des Arbeitsprozesses zu ändern."""
        import importlib.util
        name = 'mesh3dai_skriptdienstruf'
        if name not in sys.modules:
            spec = importlib.util.spec_from_file_location(name, cls.kette() / (name + '.py'))
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
            sys.modules[name] = modul
        return sys.modules[name].Skriptdienstruf

    def _schritt(self, befehl, aus):
        """Einen Schritt rechnen, Ausgabe ins Log. → (letzte Zeilen, Rückgabewert). Ein Skript aus `Skriptdienstruf.ERLAUBT` rechnet der Skriptdienst von python14; ohne ihn ein eigener Prozess."""
        import os
        # reproduzierbar (26.10.2026, Edgar: „kette muss Reproduzierbar sein“): `mesh3dai/mesh3dai_determinismus.py` schaltet damit in jedem Prozess der Kette ein, Kindprozesse erben es
        env = dict(os.environ, PYTHONIOENCODING='utf-8', MESH3DAI_DETERMINISTISCH='1', CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONHASHSEED='0')
        roh = [a for a in befehl[1:] if a != '-u']
        if roh and roh[0].endswith('.py'):
            letzte = []

            def zeile(z):
                aus.write(z + '\n')
                aus.flush()
                letzte.append(z)
                del letzte[:-200]
            try:
                erg = self._skriptdienst().ausfuehren('python14', roh[0], roh[1:], cwd=self.kette(), ausgabe=zeile, env=env)
            except Exception as fehler:      # noqa: BLE001 — der Dienst ist eine Beschleunigung, kein Weg: ohne ihn rechnet der Schritt wie bisher
                logger.warning('Mesh3D-AI Rechenlauf %s: Skriptdienst nicht nutzbar (%s) — eigener Prozess', self.kennung, fehler)
                erg = None
            if erg is not None:
                return letzte, erg[0]
        p = subprocess.Popen(befehl, cwd=str(self.kette()), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding='utf-8', errors='replace')
        letzte = []
        for zeile in p.stdout:
            aus.write(zeile)
            aus.flush()
            letzte.append(zeile.rstrip())
            letzte = letzte[-200:]
        return letzte, p.wait()
