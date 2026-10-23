# -*- coding: utf-8 -*-
"""Mesh3daiprobenkleider — die Kleider aus der KI im Feld „Ergebnis“ einer GRUNDJOB-Probe (20.10.2026, Edgar: „Bei den Grundjobs wie MannLaufen zeigt das Ergebnis noch keine KI-Kleider … Warum??“ → „baue“).

Gerechnet von `ProjektTemp/_wegwerf/mesh3dai_kikleider_proben.py` (+ `mesh3dai_schnittvergleich.py` für s, d, n) unter `<Job>/kleider_ki/<nnnn>/`: `form/` (die Figur des Ergebnisses), `kleider/` (Wege und
`ki.json`, Aufbau wie beim Test), `probe.json` (Stempel der Regler). Gezeigt wird nur, was die KI ausgibt (k, s, h) — in der Reihenfolge der Vorgabe `ki` (`Mesh3daitestkleider.wirksam`; eine Wahl je Stück
gibt es auf der Jobseite nicht), die Vergleichslinien d und n nie. Die Kleider passen nur zu der Figur, für die sie gerechnet sind: trägt die Ergebnisfigur heute andere Regler (neuer Formlauf), liefert
`fuer` nichts und schreibt es ins Log. Die Haltung ist die des Ergebnisses (`Mesh3daiprobenhaltung`, gewählter Weg); die Gelenke rechnet die Figur selbst aus den Drehungen (Vorwärtsrechnung über ihre
Ruhezentren) — die Seite legt die Gruppe wie die Figur starr auf das gezeigte Rig (`Mesh3daikikleiderfeld.einhaengen`).

    Mesh3daiprobenkleider.fuer(job, nr, figur_ergebnis, weg) -> {probe, liste, rig, dreh, ruhezentren} oder None
    Mesh3daiprobenkleider.liste(job, nr) -> {stuecke: [...], ki: {...}} oder None
"""
import hashlib
import json
import logging
import re

import numpy as np

from .mesh3daidaten import Mesh3daidaten
from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3daiflaechennetz import Mesh3daiflaechennetz
from .mesh3daiprobenhaltung import Mesh3daiprobenhaltung
from .mesh3daitestkikleider import Mesh3daitestkikleider
from .mesh3daitestkleider import Mesh3daitestkleider

logger = logging.getLogger('core')

__all__ = ['Mesh3daiprobenkleider']


class Mesh3daiprobenkleider:
    ID = re.compile(r'^[a-z0-9_]{1,64}$')

    @staticmethod
    def ordner(job, nr):
        return Mesh3daidatensatz.ordner(job['ordner']) / 'kleider_ki' / ('%04d' % int(nr))

    @staticmethod
    def stempel(regler):
        """Wie `Probenziel.stempel` (Kette): Regler auf 4 Stellen, sortiert, SHA-1, 12 Zeichen."""
        text = json.dumps({k: round(float(v), 4) for k, v in (regler or {}).items()}, sort_keys=True)
        return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]

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
        adresse = '/api/mesh3dai/%s/kleid/%d/{weg}/{id}' % (job['id'], int(nr))
        zeilen, info = Mesh3daitestkikleider.zeilen(o / 'kleider', job['id'], None, adresse)
        for z in zeilen:
            z['eigene_wahl'] = None
            z['wahl'] = Mesh3daitestkleider.wirksam(z, None, 'ki')
        return {'vorgabe': 'ki', 'stuecke': zeilen, 'ki': info, 'probe': cls._json(o / 'probe.json'), 'wege_texte': Mesh3daitestkikleider.TEXTE}

    @classmethod
    def fuer(cls, job, nr, figur_ergebnis, weg=None):
        o = cls.ordner(job, nr)
        if not (o / 'kleider' / 'ki.json').is_file():
            return None
        probe = cls._json(o / 'probe.json') or {}
        jetzt = cls.stempel((figur_ergebnis or {}).get('regler'))
        if probe.get('regler_stempel') != jetzt:
            logger.warning('Mesh3daiprobenkleider: %s Probe %s — Kleider für die Figur %s gerechnet, das Ergebnis zeigt %s (neuer Formlauf?); nicht gezeigt',
                           job.get('id'), nr, probe.get('regler_stempel'), jetzt)
            return None
        haltung = Mesh3daiprobenhaltung.fuer(job, nr, weg)
        try:
            kin = json.loads((o / 'form' / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Mesh3daiprobenkleider: %s Probe %s ohne Figur (%s)', job.get('id'), nr, fehler)
            return None
        if haltung is None or len(haltung['dreh']) != len(kin):
            return None
        zentren = np.array([k['zentrum'] for k in kin], dtype=float)
        dreh = haltung['dreh']
        rig = np.zeros_like(zentren)
        for b, k in enumerate(kin):
            e = int(k['eltern'])
            rig[b] = zentren[b] if e < 0 else rig[e] + dreh[e] @ (zentren[b] - zentren[e])
        return {'test': None, 'probe': int(nr), 'weg': haltung.get('weg'), 'liste': '/api/mesh3dai/%s/kleider/%d/' % (job['id'], int(nr)),
                'rig': np.round(rig, 4).tolist(), 'dreh': np.round(Mesh3daidaten._quaternionen(dreh), 5).tolist(), 'ruhezentren': np.round(zentren, 6).tolist()}

    @classmethod
    def stueck_ordner(cls, job, nr, weg, stueck):
        """Ordner des Stücks relativ zu `mesh3dai/` (für `Mesh3daiflaechennetz`) oder None — alle Teile aus der Adresse, geprüft."""
        if weg not in Mesh3daitestkikleider.WEGE or not cls.ID.match(str(stueck)):
            return None
        if not (cls.ordner(job, nr) / 'kleider' / weg / stueck / 'anzeige' / 'netz.npz').is_file():
            return None
        return '%s/kleider_ki/%04d/kleider/%s/%s' % (job['ordner'], int(nr), weg, stueck)

    @classmethod
    def paket(cls, job, nr, weg, stueck):
        modell = cls.stueck_ordner(job, nr, weg, stueck)
        return Mesh3daiflaechennetz.paket(modell) if modell else None

    @classmethod
    def bild(cls, job, nr, weg, stueck, name):
        modell = cls.stueck_ordner(job, nr, weg, stueck)
        return Mesh3daiflaechennetz.bild(modell, name) if modell else None
