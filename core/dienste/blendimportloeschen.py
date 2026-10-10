# -*- coding: utf-8 -*-
"""Blendimportloeschen — einen Blender-Import samt allem, was er angelegt hat, entfernen (10.10.2026).

Edgar (10.10.2026, am Rosemary-Import, der 22 Minuten ohne Meldung rechnete und eine unbrauchbare Figur ergab): „mach einen
Button zum Löschen eines Imports oder verwaisten Imports" und „mach einen Button zum Abbrechen des Jobs — der Abbrechen
löscht auch alle Importdaten". Es gab bis dahin keinen Weg: Ordner, Auftrag „Mesh to 3D" und Garderobenstücke eines Imports
standen nur von Hand zu finden.

Was zu einem Import gehört (`plan`):
    Ordner       `3DObjects/blendimport/<kennung>/` — Rohdaten, Netze, gebackene Kacheln, Stand und Log
    Auftrag      der Auftrag „Mesh to 3D" des Schritts „figur" (`stand.ergebnis.figur.id`), samt Ordner
    Stücke       die Kleider, das Haar, die Augen und die Scham des Schritts „stücke" (`stand.ergebnis.stuecke.stuecke`) — eigene
                 Stücke gehen in den Papierkorb der Garderobe (zurückholbar, `G9garderobepflege.loeschen`)
    Modell       die gespeicherten Genesis-9-Modelle mit `herkunft.import == <kennung>` (`Modellablage.loeschen`, samt Fotokacheln)

Nicht dazu gehört, was ein früherer Lauf desselben Imports angelegt hat und was der Stand nicht mehr nennt (ein erneuter Lauf ab „stücke"
überschreibt die Liste), und die gemerkten Einstellungen des Dialogs (`einstellungen.json`).

Verwaist ist ein Import, den niemand mehr braucht und der nicht rechnet: ein Ordner ohne Stand, ein Lauf, dessen Arbeitsprozess weg ist,
ein gescheiterter oder angehaltener Lauf und ein fertiger, dessen Modell es nicht mehr gibt (`grund`).

Vor dem Löschen wird frisch geprüft, ob ein Prozess aus dem Ordner arbeitet (`~/.claude/rules/rekursiv-loeschen.md`): ein laufender Import
wird nur mit `anhalten=True` gelöscht — dann stirbt der Arbeitsprozess samt Kindern (Blender, Runner), und erst danach fällt der Ordner.
Windows sperrt die Dateien eines gerade beendeten Prozesses noch einen Augenblick: das Löschen des Ordners wird wiederholt.
"""

import logging
import shutil
import threading
import time
from pathlib import Path

from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter

logger = logging.getLogger('core')

__all__ = ['Blendimportloeschen', 'ImportLaeuft', 'ImportNichtGeloescht']


class ImportLaeuft(RuntimeError):
    """Der Import rechnet noch — gelöscht wird er erst nach dem Anhalten."""


class ImportNichtGeloescht(RuntimeError):
    """Etwas blieb liegen (gesperrte Datei, Prozess lässt sich nicht beenden) — der Text sagt was."""


class Blendimportloeschen:
    #: So lange wartet das Anhalten auf das Ende des Arbeitsprozesses, und so oft wird ein gesperrter Ordner noch einmal versucht.
    WARTEN_S = 15
    VERSUCHE = 10
    PAUSE_S = 1.5
    #: Ein Löschen zugleich: zwei Anfragen auf denselben Ordner (Doppelklick) fänden sonst einen halb gelöschten.
    _SCHLOSS = threading.Lock()

    def __init__(self, kennung):
        self.ablage = Blendimportablage(kennung)            # ValueError bei einer Kennung, die keine ist
        self.kennung = self.ablage.kennung

    # ------------------------------------------------------------------ Was gehört dazu

    def stand(self):
        return self.ablage.stand()

    def vorhanden(self):
        return self.ablage.ordner().is_dir()

    def laeuft(self):
        """Arbeitet ein Prozess an diesem Import? Der Stand muss „läuft" sagen — Windows vergibt PIDs rasch neu (`laufender`)."""
        return Blendimportarbeiter.lebt(self.ablage) and self.stand().get('status') in ('laeuft', 'neu')

    def name(self):
        return (self.stand().get('quelle') or {}).get('name') or self.kennung

    @staticmethod
    def modelle_lesen():
        """`[{name, import, kleidung}]` aller gespeicherten Genesis-9-Modelle — die Dateien einmal gelesen."""
        from .modellkatalog import Modellkatalog

        aus = []
        for eintrag in Modellkatalog.gespeicherte():
            if eintrag['quelle'] != 'genesis9':
                continue
            figur = Modellkatalog.gespeichert(eintrag['name'], 'genesis9') or {}
            herkunft = figur.get('herkunft') if isinstance(figur.get('herkunft'), dict) else {}
            aus.append({'name': eintrag['name'], 'import': str(herkunft.get('import') or ''),
                        'kleidung': {str(k) for k in (figur.get('kleidung') or {})}})
        return aus

    def modelle(self, gelesen=None):
        """Namen der gespeicherten Genesis-9-Modelle, die dieser Import angelegt hat (`herkunft.import`)."""
        return [m['name'] for m in (self.modelle_lesen() if gelesen is None else gelesen) if m['import'] == self.kennung]

    @staticmethod
    def _genannte_stuecke(stand):
        return {str(k) for k in (((stand.get('ergebnis') or {}).get('stuecke') or {}).get('stuecke') or {}).values()}

    def benutzer(self, stueck, gelesen, mit_modell):
        """Wer außer diesem Import noch an einem Stück hängt: Modelle, die es tragen, und andere Importe, die es geschrieben haben.
        Gemessen 10.10.2026: der Lauf 09.54.27 „Fallout ranger" (verwaist, sein Modell gehört dem Lauf 11.42.36) und der spätere nennen
        dieselben Stücke `fallout_ranger_*` — das Löschen des alten ließe dem Modell die Kleidung nehmen. Eigene Modelle zählen nicht,
        wenn sie mit gelöscht werden (`mit_modell`)."""
        wer = ['Modell „%s"' % m['name'] for m in gelesen
               if stueck in m['kleidung'] and not (mit_modell and m['import'] == self.kennung)]
        for kennung in Blendimportablage.alle():
            if kennung != self.kennung and stueck in self._genannte_stuecke(Blendimportablage(kennung).stand()):
                wer.append('Import %s' % kennung)
        return wer

    @staticmethod
    def grund_behalten(benutzer):
        """Warum ein Stück stehen bleibt — ein Satz für die Rückfrage (Edgar, 10.10.2026: „warum wird nicht alles gelöscht? Mach eindeutige Meldung
        für den Grund"). `benutzer` kommt aus `benutzer`: `Modell „X"` oder `Import <Kennung>`. Ein Import nennt dasselbe Stück, wenn ein späterer Lauf es
        unter derselben Kennung neu geschrieben hat — dann ist es dort das aktuelle Stück, und das Modell dieses Laufs trägt es."""
        teile = []
        for wer in benutzer:
            if wer.startswith('Import '):
                teile.append('der %s hat sie unter derselben Kennung neu geschrieben (dort sind es die aktuellen Stücke)' % wer)
            else:
                teile.append('das %s trägt sie als Kleidung' % wer)
        satz = '; '.join(teile)
        return satz[:1].upper() + satz[1:]

    def stuecke(self, frisch=False, mit_modell=True, gelesen=None):
        """`[{kennung, name, eintrag, benutzer}]` der Garderobenstücke, die der Schritt „stücke" geschrieben hat und die es noch gibt.
        `benutzer` nennt, wer sie sonst noch braucht (dann bleiben sie).

        `frisch=False` (Plan, Liste der Verwaisten) liest nur die zuletzt fertige Garderobenliste — ein Neuaufbau kostet 6–55 s
        (`G9garderobe.eintrag` baute für jedes fehlende Stück neu); `frisch=True` (Löschen) findet auch ein eben geschriebenes."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.pfade import G9pfade

        if not G9pfade.vorhanden():
            return []
        gelesen = self.modelle_lesen() if gelesen is None else gelesen
        bekannt = {e['id']: e for e in G9garderobe.liste(veraltet_ok=True)}
        aus = []
        for kennung in sorted(self._genannte_stuecke(self.stand())):
            eintrag = bekannt.get(kennung) or (G9garderobe.eintrag(kennung) if frisch else None)
            if eintrag is not None and eintrag.get('eigen'):
                aus.append({'kennung': kennung, 'name': eintrag.get('name') or kennung, 'eintrag': eintrag,
                            'benutzer': self.benutzer(kennung, gelesen, mit_modell)})
        return aus

    def auftrag(self):
        """Der Auftrag „Mesh to 3D" des Schritts „figur" oder `None`."""
        from ..models import Meshfigurauftrag

        figur_id = ((self.stand().get('ergebnis') or {}).get('figur') or {}).get('id')
        if not figur_id:
            return None
        try:
            return Meshfigurauftrag.objects.filter(pk=figur_id).first()
        except (ValueError, TypeError):                     # keine gültige UUID im Stand
            return None

    def megabyte(self):
        ordner = self.ablage.ordner()
        if not ordner.is_dir():
            return 0.0
        summe = 0
        for datei in ordner.rglob('*'):
            try:
                summe += datei.stat().st_size if datei.is_file() else 0
            except OSError:
                continue
        return round(summe / 1048576, 1)

    def grund_verwaist(self, modelle, gelesen=()):
        """Warum dieser Import niemandem mehr dient — oder `None`, wenn er läuft oder sein Modell noch da ist."""
        stand = self.stand()
        if self.laeuft() or modelle:
            return None
        status = stand.get('status')
        if not stand:
            return 'Ordner ohne Stand (Rest eines abgebrochenen Imports)'
        if status in ('laeuft', 'neu'):
            return 'Der Arbeitsprozess ist weg, der Import wurde nie fertig'
        if status == 'gescheitert':
            return 'Gescheitert: %s' % (stand.get('fehler') or 'ohne Angabe')[:160]
        if status == 'angehalten':
            return 'Angehalten'
        gewesen = ((stand.get('ergebnis') or {}).get('modell') or {}).get('name')
        spaeter = next((m['import'] for m in gelesen if gewesen and m['name'] == gewesen and m['import']), None)
        if spaeter:           # derselbe Name, ein späterer Lauf hat das Modell neu geschrieben
            return 'Fertig, ersetzt: das Modell „%s" stammt jetzt aus dem Import %s' % (gewesen, spaeter)
        return 'Fertig, aber das Modell%s gibt es nicht mehr' % (' „%s"' % gewesen if gewesen else '')

    def kurzplan(self, gelesen):
        """Der Teil des Plans, der ohne Garderobe und Datenbank zu haben ist: Name, Stand, Größe, eigene Modelle, Grund der Verwaisung."""
        stand = self.stand()
        eigene = self.modelle(gelesen)
        return {
            'kennung': self.kennung, 'name': self.name(), 'status': stand.get('status') or '', 'schritt': stand.get('schritt') or '',
            'angelegt': stand.get('angelegt') or '', 'laeuft': self.laeuft(), 'mb': self.megabyte(),
            'modelle': eigene, 'verwaist': self.grund_verwaist(eigene, gelesen),
        }

    def plan(self, modelle=None):
        """Was ein Löschen entfernte — für die Rückfrage im Browser (`modelle`: schon gelesen)."""
        gelesen = self.modelle_lesen() if modelle is None else modelle
        plan = self.kurzplan(gelesen)
        job = self.auftrag()
        stuecke = self.stuecke(gelesen=gelesen)
        plan.update({
            'auftrag': {'kennung': job.kennung, 'name': getattr(job, 'name', '') or job.kennung} if job is not None else None,
            'stuecke': [{'kennung': s['kennung'], 'name': s['name']} for s in stuecke if not s['benutzer']],
            'behalten': [{'kennung': s['kennung'], 'name': s['name'], 'benutzer': s['benutzer'], 'grund': self.grund_behalten(s['benutzer'])}
                         for s in stuecke if s['benutzer']],
        })
        return plan

    @classmethod
    def verwaiste(cls):
        """Die KURZPLÄNE aller verwaisten Importe, neueste zuerst — ohne Stücke, Auftrag und Garderobe.

        Die Liste „Gespeicherte Modelle" und die Rückfrage „Alle verwaisten löschen" brauchen Name, Kennung, Größe und Grund. Der volle Plan
        (`plan`) las je Import die Garderobenliste und alle anderen Stände: gemessen 10.10.2026 (`ProjektTemp/_wegwerf/dialog_verwaist_profil.py`)
        warm 1,1–1,7 s, kalt 20 s (Neuaufbau der Garderobenliste) — und der Dialog „Charakter hinzufügen" wartete darauf (im `client.log` heute 1,5 bis
        41 s). Den vollen Plan holt die Rückfrage je Import über `…/loeschplan/`."""
        gelesen = cls.modelle_lesen()
        aus = []
        for kennung in Blendimportablage.alle():
            import_ = cls(kennung)
            if import_.grund_verwaist(import_.modelle(gelesen), gelesen):
                aus.append(import_.kurzplan(gelesen))
        return aus

    # ------------------------------------------------------------------ Löschen

    def loeschen(self, mit_modell=True, anhalten=False, stuecke_trotzdem=False):
        """Alles entfernen, was der Import angelegt hat. → `{kennung, stuecke, behalten, modelle, auftrag, ordner_mb}`.

        `ImportLaeuft` (→ 409), wenn er rechnet und `anhalten` fehlt; `ImportNichtGeloescht`, wenn etwas liegen blieb.
        `stuecke_trotzdem`: auch Stücke entfernen, die ein Modell oder ein anderer Import noch braucht (Papierkorb, zurückholbar) —
        Edgar, 10.10.2026: „möglichst alles weg". Das Modell verliert sie dann; nur auf ausdrückliche Zusage des Nutzers."""
        with self._SCHLOSS:
            if not self.vorhanden():
                raise FileNotFoundError('Kein Import %s' % self.kennung)
            if self.laeuft():
                if not anhalten:
                    raise ImportLaeuft('Import %s rechnet noch (Schritt „%s")' % (self.kennung, self.stand().get('schritt') or '?'))
                self._anhalten()
            ergebnis = {'kennung': self.kennung, 'stuecke': [], 'behalten': [], 'modelle': [], 'auftrag': None, 'ordner_mb': self.megabyte()}
            ergebnis['auftrag'] = self._auftrag_entfernen()
            ergebnis['stuecke'], ergebnis['behalten'] = self._stuecke_entfernen(mit_modell, stuecke_trotzdem)
            if mit_modell:
                ergebnis['modelle'] = self._modelle_entfernen()
            self._ordner_entfernen()
            logger.info('Blender-Import %s gelöscht: %s', self.kennung, ergebnis)
            return ergebnis

    @classmethod
    def verwaiste_loeschen(cls, kennungen=None):
        """Alle verwaisten Importe (oder nur die genannten, sofern sie es noch sind) löschen
        → `{geloescht: [...], fehler: {kennung: Text}, behalten: {kennung: [{kennung, name, benutzer, grund}]}}`.
        Stücke, die ein Modell oder ein anderer Import braucht, bleiben (`behalten`, mit Grund) — verwaiste Importe sind meist ältere Läufe, deren
        Stücke ein späterer unter derselben Kennung überschrieben hat."""
        geloescht, fehler, behalten = [], {}, {}
        for plan in cls.verwaiste():
            if kennungen is not None and plan['kennung'] not in kennungen:
                continue
            try:
                ergebnis = cls(plan['kennung']).loeschen(mit_modell=False)
                geloescht.append(plan['kennung'])
                if ergebnis['behalten']:
                    behalten[plan['kennung']] = ergebnis['behalten']
            except (ImportLaeuft, ImportNichtGeloescht, OSError) as grund:
                fehler[plan['kennung']] = str(grund)
        return {'geloescht': geloescht, 'fehler': fehler, 'behalten': behalten}

    def _anhalten(self):
        """Stand und Prozess samt Kindern (`Blendimportarbeiter.anhalten`), dann warten, bis der Arbeitsprozess weg ist."""
        job = self.auftrag()
        if job is not None and job.laeuft:
            from .meshfigurarbeiter import Meshfigurarbeiter

            Meshfigurarbeiter.anhalten(job)
        Blendimportarbeiter.anhalten(self.ablage)
        ende = time.monotonic() + self.WARTEN_S
        while Blendimportarbeiter.lebt(self.ablage) and time.monotonic() < ende:
            time.sleep(0.5)
        if Blendimportarbeiter.lebt(self.ablage):
            raise ImportNichtGeloescht('Der Arbeitsprozess von Import %s lässt sich nicht beenden' % self.kennung)

    def _auftrag_entfernen(self):
        """Der Auftrag „Mesh to 3D" mit Ordner (wie `Meshfigurendpunkte._entfernen`) — das gespeicherte Modell gehört nicht dazu."""
        job = self.auftrag()
        if job is None:
            return None
        from ..daten.meshfigurablage import Meshfigurablage

        kennung = job.kennung
        if job.laeuft:
            from .meshfigurarbeiter import Meshfigurarbeiter

            Meshfigurarbeiter.anhalten(job)
        Meshfigurablage(kennung).loeschen()
        job.delete()
        return kennung

    def _stuecke_entfernen(self, mit_modell, trotzdem=False):
        """Die eigenen Stücke in den Papierkorb der Garderobe → `(gelöscht, behalten)`. Ein Stück, das ein Modell oder ein anderer Import
        noch braucht, bleibt (außer `trotzdem`, dann steht im Protokoll, wer es verliert); eines, das nicht geht, steht im Protokoll —
        es bricht das Löschen nicht ab. `behalten` trägt Name und Grund für die Meldung an den Nutzer."""
        from Genesis9.garderobepflege import G9garderobepflege

        weg, behalten = [], []
        for stueck in self.stuecke(frisch=True, mit_modell=mit_modell):
            if stueck['benutzer'] and not trotzdem:
                behalten.append({'kennung': stueck['kennung'], 'name': stueck['name'], 'benutzer': stueck['benutzer'],
                                 'grund': self.grund_behalten(stueck['benutzer'])})
                continue
            if stueck['benutzer']:
                logger.warning('Blender-Import %s: Stück %s auf Wunsch entfernt, obwohl es noch gebraucht wird: %s',
                               self.kennung, stueck['kennung'], ', '.join(stueck['benutzer']))
            try:
                G9garderobepflege.loeschen(stueck['eintrag'])
                weg.append(stueck['kennung'])
            except (OSError, ValueError):
                logger.exception('Blender-Import %s: Stück %s nicht gelöscht', self.kennung, stueck['kennung'])
        return weg, behalten

    def _modelle_entfernen(self):
        from .modellablage import Modellablage

        weg = []
        for name in self.modelle():
            Modellablage.loeschen(name)
            weg.append(name)
        return weg

    def _ordner_entfernen(self):
        """Den Ordner löschen, mit Wiederholung: eben beendete Prozesse (Blender) halten ihre Dateien noch kurz. Danach NACHZÄHLEN."""
        ordner = self._sicherer_ordner()
        for _versuch in range(self.VERSUCHE):
            shutil.rmtree(ordner, ignore_errors=True)
            if not ordner.exists():
                return
            time.sleep(self.PAUSE_S)
        rest = sum(1 for p in ordner.rglob('*') if p.is_file())
        raise ImportNichtGeloescht('Im Ordner von Import %s blieben %d Dateien liegen (gesperrt?) — später noch einmal löschen' % (self.kennung, rest))

    def _sicherer_ordner(self):
        """Der Ordner dieses Imports — und nur der: direkt unter der Wurzel, keine Verknüpfung nach draußen."""
        ordner = self.ablage.ordner()
        wurzel = Blendimportablage.wurzel().resolve()
        if ordner.is_symlink() or Path(ordner).resolve().parent != wurzel:
            raise ImportNichtGeloescht('Der Ordner von Import %s liegt nicht unter %s' % (self.kennung, wurzel))
        return ordner
