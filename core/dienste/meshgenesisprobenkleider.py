# -*- coding: utf-8 -*-
"""Meshgenesisprobenkleider — die Kleider aus der KI im Feld „Ergebnis“ einer GRUNDJOB-Probe (20.10.2026, Edgar: „Bei den Grundjobs wie MannLaufen zeigt das Ergebnis noch keine KI-Kleider … Warum??“ → „baue“).

Gerechnet von `ProjektTemp/_wegwerf/meshgenesis_kikleider_proben.py` (+ `meshgenesis_schnittvergleich.py` für s, d, n) unter `<Job>/kleider_ki/<nnnn>/`: `form/` (die Figur des Ergebnisses), `kleider/` (Wege und
`ki.json`, Aufbau wie beim Test), `probe.json` (Stempel der Regler). Gezeigt wird nur, was die KI ausgibt (k, s, h) — in der Reihenfolge der Vorgabe `ki` (`Meshgenesistestkleider.wirksam`; eine Wahl je Stück
gibt es auf der Jobseite nicht), die Vergleichslinien d und n nie. Die Kleider passen nur zu der Figur, für die sie gerechnet sind: trägt die Ergebnisfigur heute andere Regler (neuer Formlauf), liefert
`fuer` nichts und schreibt es ins Log. Die Haltung ist die des Ergebnisses (`Meshgenesisprobenhaltung`, gewählter Weg); die Gelenke rechnet die Figur selbst aus den Drehungen (Vorwärtsrechnung über ihre
Ruhezentren) — die Seite legt die Gruppe wie die Figur starr auf das gezeigte Rig (`Meshgenesiskikleiderfeld.einhaengen`).

    Meshgenesisprobenkleider.fuer(job, nr, figur_ergebnis, weg) -> {probe, liste, rig, dreh, ruhezentren} oder None
    Meshgenesisprobenkleider.liste(job, nr) -> {stuecke: [...], ki: {...}} oder None
"""
import json
import logging
import re

import numpy as np

from .meshgenesisdaten import Meshgenesisdaten
from .meshgenesisdatensatz import Meshgenesisdatensatz
from .meshgenesisflaechennetz import Meshgenesisflaechennetz
from .meshgenesisprobenhaltung import Meshgenesisprobenhaltung
from .meshgenesistestkikleider import Meshgenesistestkikleider
from .meshgenesistestkleider import Meshgenesistestkleider

logger = logging.getLogger('core')

__all__ = ['Meshgenesisprobenkleider']


class Meshgenesisprobenkleider:
    ID = re.compile(r'^[a-z0-9_]{1,64}$')

    @staticmethod
    def ordner(job, nr):
        return Meshgenesisdatensatz.ordner(job['ordner']) / 'kleider_ki' / ('%04d' % int(nr))

    @staticmethod
    def stempel(regler):
        """Die Kennung einer Reglerstellung aus der Kette (`Probenziel.stempel`, seit 09.11.2026 keine Kopie mehr)."""
        from .meshgenesisrechenlauf import Meshgenesisrechenlauf
        return Meshgenesisrechenlauf.modul('meshgenesis_probenziel').Probenziel.stempel(regler)

    @staticmethod
    def _json(pfad):
        try:
            wert = json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return wert if isinstance(wert, dict) else None

    @classmethod
    def liste(cls, job, nr):
        o = cls.ordner(job, nr)
        if not (o / 'kleider' / 'ki.json').is_file():
            return None
        adresse = '/api/meshgenesis/%s/kleid/%d/{weg}/{id}' % (job['id'], int(nr))
        zeilen, info = Meshgenesistestkikleider.zeilen(o / 'kleider', job['id'], None, adresse)
        for z in zeilen:
            z['eigene_wahl'] = None
            z['wahl'] = Meshgenesistestkleider.wirksam(z, None, 'ki')
        return {'vorgabe': 'ki', 'stuecke': zeilen, 'ki': info, 'probe': cls._json(o / 'probe.json'), 'wege_texte': Meshgenesistestkikleider.TEXTE}

    @classmethod
    def fuer(cls, job, nr, figur_ergebnis, weg=None):
        o = cls.ordner(job, nr)
        if not (o / 'kleider' / 'ki.json').is_file():
            return None
        probe = cls._json(o / 'probe.json') or {}
        jetzt = cls.stempel((figur_ergebnis or {}).get('regler'))
        if probe.get('regler_stempel') != jetzt:
            logger.warning('Meshgenesisprobenkleider: %s Probe %s — Kleider für die Figur %s gerechnet, das Ergebnis zeigt %s (neuer Formlauf?); nicht gezeigt',
                           job.get('id'), nr, probe.get('regler_stempel'), jetzt)
            return None
        haltung = Meshgenesisprobenhaltung.fuer(job, nr, weg)
        try:
            kin = json.loads((o / 'form' / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Meshgenesisprobenkleider: %s Probe %s ohne Figur (%s)', job.get('id'), nr, fehler)
            return None
        if haltung is None or len(haltung['dreh']) != len(kin):
            return None
        zentren = np.array([k['zentrum'] for k in kin], dtype=float)
        dreh = haltung['dreh']
        rig = np.zeros_like(zentren)
        for b, k in enumerate(kin):
            e = int(k['eltern'])
            rig[b] = zentren[b] if e < 0 else rig[e] + dreh[e] @ (zentren[b] - zentren[e])
        return {'test': None, 'probe': int(nr), 'weg': haltung.get('weg'), 'liste': '/api/meshgenesis/%s/kleider/%d/' % (job['id'], int(nr)),
                'rig': np.round(rig, 4).tolist(), 'dreh': np.round(Meshgenesisdaten._quaternionen(dreh), 5).tolist(), 'ruhezentren': np.round(zentren, 6).tolist()}

    @classmethod
    def stueck_ordner(cls, job, nr, weg, stueck):
        """Ordner des Stücks relativ zu `meshgenesis/` (für `Meshgenesisflaechennetz`) oder None — alle Teile aus der Adresse, geprüft."""
        if weg not in Meshgenesistestkikleider.WEGE or not cls.ID.match(str(stueck)):
            return None
        if not (cls.ordner(job, nr) / 'kleider' / weg / stueck / 'anzeige' / 'netz.npz').is_file():
            return None
        return '%s/kleider_ki/%04d/kleider/%s/%s' % (job['ordner'], int(nr), weg, stueck)

    @classmethod
    def paket(cls, job, nr, weg, stueck):
        modell = cls.stueck_ordner(job, nr, weg, stueck)
        return Meshgenesisflaechennetz.paket(modell) if modell else None

    @classmethod
    def bild(cls, job, nr, weg, stueck, name):
        modell = cls.stueck_ordner(job, nr, weg, stueck)
        return Meshgenesisflaechennetz.bild(modell, name) if modell else None
