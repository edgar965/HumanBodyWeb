# -*- coding: utf-8 -*-
"""Meshgenesistestmodell — „Übernehmen und speichern“ eines Tests von Mesh-Genesis: die vorhergesagte Figur mit den gewählten Kleidern und Bestandteilen als Genesis-Modell (17.10.2026 nachts).

Edgar: „Button zum übernehmen von Option a oder b in das End-Modell, mit speichern des Modells“. Das Modell hat die Form wie „Modell speichern“ der Szene und `Blendimportmodell`
(`{name, quelle: genesis9, figur: {figur (Haut), regler, kleidung, herkunft, …}}`) und steht danach unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“:
  * Regler: die der vorhergesagten Figur dieses Geschlechts (`_test/<kennung>/form_<g>/modell.json`), Haut wie dort (Ursula1 bzw. Mann1).
  * je Stück mit Wahl „a“ das Katalogstück (Kennung aus `stuecke.json`) mit der Umfärbung aus dem Netz; „b“ das Stück aus dem Netz als eigenes Genesis-Stück (`Meshgenesistesteigenstueck`);
    „aus“ nichts.
Gerechnet wird in einem eigenen Prozess (`manage.py meshgenesis_testmodell`): ein Stück aus dem Netz kostet Minuten (`G9gcfigurbau`). Stand in `kleider_<g>/modell_stand.json`, Ausgabe in `modell.log`.
Ein gleichnamiges Modell, das nicht aus DIESEM Test und Geschlecht stammt, wird nie überschrieben — der Name bekommt dann eine Nummer.
"""

import json
import logging
import re
import sys
import time
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber
from .meshgenesistest import Meshgenesistest
from .meshgenesistestkleider import Meshgenesistestkleider
from .meshgenesistestkleidspeichern import Meshgenesistestkleidspeichern

logger = logging.getLogger(__name__)

__all__ = ['Meshgenesistestmodell']


class Meshgenesistestmodell:
    BEFEHL = 'meshgenesis_testmodell'
    STAND = 'modell_stand.json'
    LOG = 'modell.log'
    HERKUNFT = 'meshgenesis test'
    #: Datei, ohne die der Ordner keine Stücke hat (Foto-Genesis: `ki.json`, `Fotogenesismodell`)
    STUECKE = 'stuecke.json'

    # Die Quelle (31.10.2026, `Fotogenesismodell` überschreibt diese drei): Ordner der Stücke und des Stands, Form der Figur, Liste der Stücke mit Wahl.
    @classmethod
    def ordner(cls, kennung, geschlecht):
        return Meshgenesistestkleider.ordner(kennung, geschlecht)

    @classmethod
    def form(cls, kennung, geschlecht):
        return json.loads((Meshgenesistest.pfad(kennung) / ('form_%s' % geschlecht) / 'modell.json').read_text(encoding='utf-8'))

    @classmethod
    def liste(cls, kennung, geschlecht):
        return Meshgenesistestkleider.liste(kennung, geschlecht)

    @classmethod
    def kacheln(cls, kennung, geschlecht):
        """Fotohaut `{kachel: Adresse}`, wenn die Liste keine „Haut b“ trägt — hier keine."""
        return None

    @classmethod
    def stand(cls, kennung, geschlecht):
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None:
            return None
        try:
            stand = json.loads((ordner / cls.STAND).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {'status': 'nie'}
        if stand.get('status') == 'laeuft' and stand.get('pid'):
            from ..pipelines.prozesspruefung import Prozesspruefung
            if not Prozesspruefung.lebt(int(stand['pid'])):
                stand.update(status='fehler', meldung='Der Prozess lebt nicht mehr (abgebrochen?) — siehe %s' % (ordner / cls.LOG))
        return stand

    @classmethod
    def _schreiben(cls, ordner, **felder):
        try:
            stand = json.loads((ordner / cls.STAND).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            stand = {}
        stand.update(felder, aktualisiert=time.strftime('%Y-%m-%dT%H:%M:%S'))
        AtomarSchreiber.json_schreiben(ordner / cls.STAND, stand)
        return stand

    @staticmethod
    def name_saeubern(wunsch):
        return re.sub(r'[^\w\s\-]', '', str(wunsch or ''), flags=re.UNICODE).strip()[:80]

    @classmethod
    def starten(cls, kennung, geschlecht, name):
        """(Antwort, HTTP-Status) — startet den Prozess; 409, wenn für diesen Test und dieses Geschlecht schon einer läuft."""
        from .auftragsarbeiter import Auftragsarbeiter
        ordner = cls.ordner(kennung, geschlecht)
        if ordner is None or not (ordner / cls.STUECKE).is_file():
            return {'error': 'Für Test %s (%s) sind keine Kleider gerechnet' % (kennung, geschlecht)}, 404
        name = cls.name_saeubern(name)
        if not name:
            return {'error': 'Name fehlt'}, 400
        if (cls.stand(kennung, geschlecht) or {}).get('status') == 'laeuft':
            return {'error': 'Die Übernahme läuft schon', 'stand': cls.stand(kennung, geschlecht)}, 409
        cls._schreiben(ordner, status='laeuft', name=name, meldung='startet', gestartet=time.strftime('%Y-%m-%dT%H:%M:%S'), modell=None, fehler=None)
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), cls.BEFEHL, kennung, geschlecht, name]
        with open(ordner / cls.LOG, 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        stand = cls._schreiben(ordner, pid=prozess.pid)
        logger.info('%s %s (%s): Übernahme ins Modell „%s“, Prozess %s', cls.HERKUNFT, kennung, geschlecht, name, prozess.pid)
        return {'ok': True, 'stand': stand}, 202

    @classmethod
    def _eigenes(cls, pfad, kennung, geschlecht):
        try:
            herkunft = (json.loads(pfad.read_text(encoding='utf-8')).get('figur') or {}).get('herkunft') or {}
        except (OSError, ValueError):
            return False
        return herkunft.get('art') == cls.HERKUNFT and herkunft.get('test') == kennung and herkunft.get('geschlecht') == geschlecht

    @classmethod
    def freier_name(cls, wunsch, kennung, geschlecht, ordner=None):
        ordner = Path(ordner or settings.HUMANBODY_MODELS_DIR)
        stamm = cls.name_saeubern(wunsch) or 'Mesh-Genesis Modell'
        name, n = stamm, 2
        while (ordner / (name + '.json')).is_file() and not cls._eigenes(ordner / (name + '.json'), kennung, geschlecht):
            name, n = '%s %d' % (stamm, n), n + 1
        return name

    @classmethod
    def modelldaten(cls, name, kennung, geschlecht, form, kleidung, fototextur=None):
        """Das Modell als Wörterbuch (ohne Platte) — `form` = `modell.json` der vorhergesagten Figur, `kleidung` = `{stück: {farbe, …}}`,
        `fototextur` = `{kachel: Adresse}` bei „Haut b“ (die Kacheln des Mesh-3D-Laufs, wie ein Modell aus „Mesh to 3D“ sie trägt — `Meshfigurspeichern.modelldaten`)."""
        from .blendimportmodell import Blendimportmodell
        # 'regler' (12.11.2026): die Regler des Stücks (Weg z, „Genesis zuerst“: Passform aus der Messung am Netzstück, `Garderoberegler`), sonst leer
        eintraege = {k: {'variante': '', 'stil': '', 'stile': {}, 'regler': dict(w.get('regler') or {}), 'farbe': w.get('farbe'), 'gruppenfarben': {}, 'griff': Blendimportmodell.griff(k),
                         'knochen': False}
                     for k, w in kleidung.items()}
        figur = form.get('figur') or {}
        aus = {'name': name, 'quelle': 'genesis9',
               'figur': {'figur': figur.get('figur') or 'basis', 'regler': dict(figur.get('regler') or {}), 'haut': '', 'augen': '01', 'brauen': '', 'brauenstil': '', 'praesets': {},
                         'pose': '', 'ausdruck': '', 'kleidung': eintraege,
                         'herkunft': {'art': cls.HERKUNFT, 'test': kennung, 'geschlecht': geschlecht, 'form': form.get('quelle')}}}
        if fototextur:
            aus['figur']['fototextur'] = dict(fototextur)
        return aus

    @classmethod
    def ausfuehren(cls, kennung, geschlecht, wunsch, ziel_ordner=None):
        """Im Arbeitsprozess: Stücke sammeln (b → eigene Stücke), Modell schreiben. `ziel_ordner` nur für Probeläufe (sonst `HUMANBODY_MODELS_DIR`). Gibt den Namen."""
        from .meshgenesisrig import Meshgenesisrig
        from .meshgenesistesteigenstueck import Meshgenesistesteigenstueck
        ordner = cls.ordner(kennung, geschlecht)
        try:
            form = cls.form(kennung, geschlecht)
            name = cls.freier_name(wunsch, kennung, geschlecht, ziel_ordner)
            liste = cls.liste(kennung, geschlecht)
            kleidung, bericht, fototextur = {}, [], None
            for st in liste['stuecke']:
                wahl = st['wahl']
                if st.get('art') == 'haut':
                    # Die Haut ist kein Kleidungsstück: a = Haut der Figur (nichts zu tun), b = Kacheln des Mesh-3D-Laufs als Fotohaut (`meshgenesis_kleider_haut.py`).
                    if wahl == 'b':
                        fototextur = st['b'].get('adressen') or None
                    bericht.append({'id': 'haut', 'wahl': wahl, 'kacheln': sorted(fototextur or {})})
                    continue
                cls._schreiben(ordner, meldung='%s: %s' % (st['name'], {'a': 'Katalogstück', 'b': 'Stück aus dem Netz', 'k': 'KI: aus dem Netz geschnitten', 's': 'KI: Schnitt',
                                                                         'f': 'KI: Schnitt aus der Fläche', 'g': 'KI: Schicht', 'h': 'KI: Frisur der Garderobe',
                                                                         'z': 'Garderobe (Genesis zuerst)', 'aus': 'aus'}.get(wahl, wahl)))
                if wahl in ('a', 'h', 'z'):
                    # a: Katalogstück; h (KI, 20.10.2026): die Frisur der Garderobe nach den Haarmaßen der KI; z (12.11.2026, „Genesis zuerst“): Stück der Garderobe mit seinen
                    # Passform-Reglern (`regler_stueck`) — alle drei ein Stück der Garderobe mit Umfärbung
                    kleidung[st[wahl]['kennung']] = {'farbe': st[wahl].get('farbe'), 'regler': st[wahl].get('regler_stueck') or {}}
                    bericht.append({'id': st['id'], 'wahl': wahl, 'stueck': st[wahl]['kennung']})
                elif wahl in Meshgenesistestkleidspeichern.EIGENE:
                    # b: Objekt des Mesh-3D-Laufs; k, s, f, g (KI): geschnitten, GarmentCode-Schnitt, Schnitt aus der Fläche, Schicht — alle liegen als Anzeigenetz auf der Figur und werden eigene
                    # Genesis-Stücke (`Meshgenesistesteigenstueck` liest den Übertrag unter `b`). f und g fehlten hier bis 22.10.2026: Stücke aus dem Schichtkopf kamen nie ins Modell.
                    eigen = Meshgenesistesteigenstueck(ordner / wahl / st['id'], dict(st, b=st[wahl]), form['figur']['regler'], name, Meshgenesisrig.namen()).holen()
                    kleidung[eigen['stueck']] = {'farbe': None}
                    # Name und Kategorie in der Garderobe, wie in der Karte gewählt (`Meshgenesistestkleidspeichern`)
                    from Genesis9.garderobe import G9garderobe
                    sp = st.get('speichern') or {}
                    garderobe = Meshgenesistestkleidspeichern.anwenden(eigen['stueck'], {'name': sp.get('name'), 'kategorie': sp.get('kategorie')}, G9garderobe.eintrag(eigen['stueck']))
                    bericht.append({'id': st['id'], 'wahl': wahl, 'stueck': eigen['stueck'], 'angezogen': eigen.get('angezogen'), 'gemerkt': bool(eigen.get('gemerkt')), 'garderobe': garderobe})
            fototextur = fototextur or cls.kacheln(kennung, geschlecht)
            daten = cls.modelldaten(name, kennung, geschlecht, form, kleidung, fototextur)
            if fototextur and ziel_ordner is None:
                # Die Kacheln neben das Modell (überleben das Löschen des Mesh-3D-Laufs) — wie jedes Speichern mit Fotohaut. Ein Probelauf mit `ziel_ordner` behält die Adressen des Laufs.
                from .modelltexturen import Modelltexturen
                daten['figur'] = Modelltexturen.sichern(name, daten['figur'])
            ziel = Path(ziel_ordner or settings.HUMANBODY_MODELS_DIR) / (name + '.json')
            ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding='utf-8')
            cls._schreiben(ordner, status='fertig', modell=name, meldung='Modell „%s“ gespeichert (%d Stücke)' % (name, len(kleidung)), stuecke=bericht, datei=str(ziel))
            logger.info('%s %s (%s): Modell %s gespeichert, %s', cls.HERKUNFT, kennung, geschlecht, name, bericht)
            return name
        except Exception as fehler:
            logger.exception('%s %s (%s): Übernahme gescheitert', cls.HERKUNFT, kennung, geschlecht)
            cls._schreiben(ordner, status='fehler', fehler='%s: %s' % (type(fehler).__name__, fehler), meldung='gescheitert')
            raise
