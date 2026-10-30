# -*- coding: utf-8 -*-
"""Mesh3dailaufzeit — wie lange die Rechnung gedauert hat, deren Ergebnis die Seite zeigt (20.10.2026).

Edgar: „füge eine neue Spalte ein bei /mesh-3D-AI/#jobs und bei /mesh-3D-AI/#test mit der Laufzeit (also wieviel es gedauert hat das …“ (der Satz brach ab).
Gezählt werden nur GEMESSENE Zeiten, die die Rechenschritte selbst ablegen — nichts geschätzt; ein Schritt ohne abgelegte Zeit steht im Tooltip unter „ohne Zeitangabe“ und fehlt in der Summe.

Test (`_test/<kennung>/`, auch der Test eines Tripo-Jobs):
  * Vorstufe — `test.json` → `vorstufe.zeiten_s` (Pfad, Lage, MIA, Netz …; die Kette, aus der das gezeigte Ergebnis stammt);
  * Netz direkt — `test.json` → `dauer_s`, nur bei Tests ohne Vorstufe (`mesh3dai_test_rechnen.py`); mit Vorstufe gehört die Zahl zum ersetzten direkten Lauf und zählt nicht;
  * Figur bauen — `form_<g>/bau.log`, Zeilen „== … fertig nach X s“ (Teile, Anzeigenetz, Kinematik) des eingestellten Geschlechts;
  * Zerlegung — `zerlegung/zerlegung.json` → `sekunden`;
  * Kleider — Summe von `sekunden` der Einträge `kleider_<g>/<weg>/<id>/eintrag.json` der KI-Wege k, s, h; a/b (Mesh-3D-Lauf) und d/n (Vergleichslinien) nur im Tooltip;
  * ohne Zeitangabe: die Vorhersage des Formnetzes (`ergebnis_Form_<g>.npz` legt keine Zeit ab).
Job: ein Grundjob zeigt die Vorhersagen seines Trainings — Laufzeit = `dauer_s` aus `lauf_ergebnis.json` des Trainings, das „Zuletzt trainiert“ nennt (`Mesh3daitrainingsdatum`);
ein Tripo-Job zeigt das Ergebnis seines Tests (`_test/<id>/`) — Laufzeit wie beim Test.

    Mesh3dailaufzeit.test(ordner, geschlecht) -> None | {'sekunden': float, 'teile': [(Text, s)], 'ohne': [Text]}
    Mesh3dailaufzeit.job(job)                -> dasselbe, dazu 'quelle'
    Mesh3dailaufzeit.text(sekunden)          -> '3 min 12 s'
"""

import json
import logging
import re
import time

from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3daitrainingsdatum import Mesh3daitrainingsdatum

logger = logging.getLogger('core')

__all__ = ['Mesh3dailaufzeit']


class Mesh3dailaufzeit:
    FERTIG = re.compile(r'^== (\S+) fertig nach ([0-9.]+) s')
    #: Wege, deren Stücke das Ergebnis der KI zeigt (`Mesh3daitestkikleider`); a/b kommen aus dem Mesh-3D-Lauf, d/n sind Vergleichslinien — sie stehen nur im Tooltip
    KI_WEGE = ('k', 's', 'h')
    VORSTUFE = {'pfad': 'Pfad', 'lage': 'Lage', 'mia_stapel': 'MIA (Stapel)', 'mia': 'MIA', 'rig': 'Rig', 'figur': 'Figur der Vorstufe', 'apose': 'A-Pose', 'netz': 'Netz der Vorstufe'}

    @staticmethod
    def _json(datei):
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def test(cls, ordner, geschlecht):
        info = cls._json(ordner / 'test.json')
        if not isinstance(info, dict):
            return None
        teile, ohne = [], []
        vorstufe = (info.get('vorstufe') or {}).get('zeiten_s') or {}
        if vorstufe:
            teile.append(('Vorstufe (%s)' % ', '.join('%s %.0f s' % (cls.VORSTUFE.get(k, k), float(v)) for k, v in vorstufe.items()), sum(float(v) for v in vorstufe.values())))
        elif info.get('dauer_s') is not None:
            teile.append(('Netz direkt', float(info['dauer_s'])))
        bau = cls._bau(ordner / ('form_%s' % geschlecht) / 'bau.log')
        if bau is not None:
            teile.append(('Figur bauen (%s)' % geschlecht, bau))
        if info.get('form') and not info.get('form_ausgelassen'):
            ohne.append('Vorhersage des Formnetzes')
        zerlegung = cls._json(ordner / 'zerlegung' / 'zerlegung.json')
        if isinstance(zerlegung, dict) and zerlegung.get('sekunden') is not None:
            teile.append(('Zerlegung', float(zerlegung['sekunden'])))
        je_weg = cls._kleider(ordner / ('kleider_%s' % geschlecht))
        ki = [je_weg[w] for w in cls.KI_WEGE if w in je_weg]
        if ki:
            teile.append(('Kleider der KI (Wege %s, %d Stücke)' % ('/'.join(w for w in cls.KI_WEGE if w in je_weg), sum(z for _, z in ki)), sum(s for s, _ in ki)))
        andere = sorted(w for w in je_weg if w not in cls.KI_WEGE)
        if andere:
            ohne.append('Kleider der Wege %s (Mesh-3D-Lauf bzw. Vergleichslinien, %s)'
                        % ('/'.join(andere), ', '.join('%s %s' % (w, cls.text(je_weg[w][0])) for w in andere)))
        if not teile:
            return None
        return {'sekunden': sum(s for _, s in teile), 'teile': teile, 'ohne': ohne}

    @classmethod
    def _bau(cls, datei):
        """Summe der Zeilen „== <Schritt> fertig nach X s“ im Bau-Log der Figur, None ohne Log."""
        try:
            zeilen = datei.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            return None
        werte = [float(m.group(2)) for m in (cls.FERTIG.match(z) for z in zeilen) if m]
        return sum(werte) if werte else None

    @classmethod
    def _kleider(cls, ordner):
        """{Weg: (Sekunden, Stücke)} aus `<Weg>/<id>/eintrag.json` — nur Einträge mit `sekunden`."""
        aus = {}
        if not ordner.is_dir():
            return aus
        for datei in ordner.glob('*/*/eintrag.json'):
            sekunden = cls._sekunden(datei)
            if sekunden is not None:
                s, z = aus.get(datei.parent.parent.name, (0.0, 0))
                aus[datei.parent.parent.name] = (s + sekunden, z + 1)
        return aus

    #: `sekunden` je `eintrag.json`, neu gelesen nur bei geänderter Zeit oder Größe (30.10.2026): die Testtabelle las sonst bei jedem Aufruf von /mesh-3D-AI/ alle 838 Einträge
    _eintraege = {}

    @classmethod
    def _sekunden(cls, datei):
        try:
            st = datei.stat()
        except OSError:
            return None
        stand = (st.st_mtime_ns, st.st_size)
        alt = cls._eintraege.get(datei)
        if alt is not None and alt[0] == stand:
            return alt[1]
        e = cls._json(datei)
        sekunden = float(e['sekunden']) if isinstance(e, dict) and e.get('sekunden') is not None else None
        cls._eintraege[datei] = (stand, sekunden)
        return sekunden

    #: wie `Mesh3dairechendatum`: 30 s gemerkt — alle Jobs kalt 0,38 s (gemessen 20.10.2026, `laufzeit_spalte_zeit.py`), die Tabelle lädt bei jedem Aufruf
    MERKEN_S = 30
    _gemerkt = {}

    @classmethod
    def job(cls, job):
        schluessel = (job['id'], job['ordner'], bool(job.get('paar')))
        alt = cls._gemerkt.get(schluessel)
        if alt and time.monotonic() - alt[0] < cls.MERKEN_S:
            return alt[1]
        wert = cls._job(job)
        cls._gemerkt[schluessel] = (time.monotonic(), wert)
        return wert

    @classmethod
    def _job(cls, job):
        if job.get('paar'):
            from .mesh3daitest import Mesh3daitest
            ordner = Mesh3daitest.ordner() / job['id']
            info = cls._json(ordner / 'test.json')
            if not isinstance(info, dict):
                return None
            aus = cls.test(ordner, Mesh3daitest.geschlecht(ordner, info))
            if aus:
                aus['quelle'] = 'Ergebnis des Tripo-Jobs (Kette auf dem Tripo-Netz)'
            return aus
        letztes = Mesh3daitrainingsdatum.letztes(job['ordner'])
        if not letztes:
            return None
        if letztes['art'] == 'job':
            datei = Mesh3daidatensatz.ordner(job['ordner']) / '_laeufe' / letztes['lauf'] / Mesh3daitrainingsdatum.ERGEBNIS
        else:
            datei = Mesh3daidatensatz.ordner(Mesh3daitrainingsdatum.GEMEINSAM[0]) / Mesh3daitrainingsdatum.GEMEINSAM[1] / letztes['lauf'] / Mesh3daitrainingsdatum.ERGEBNIS
        e = cls._json(datei)
        if not isinstance(e, dict) or e.get('dauer_s') is None:
            logger.info('Mesh3dailaufzeit: %s ohne dauer_s', datei)
            return None
        return {'sekunden': float(e['dauer_s']), 'teile': [('Training %s (%s Epochen)' % (letztes['lauf'], e.get('epochen', '?')), float(e['dauer_s']))], 'ohne': [],
                'quelle': 'Training, das „Zuletzt trainiert“ nennt'}

    @staticmethod
    def text(sekunden):
        s = int(round(float(sekunden)))
        if s < 60:
            return '%d s' % s
        if s < 3600:
            return '%d min %02d s' % (s // 60, s % 60)
        return '%d h %02d min' % (s // 3600, (s % 3600) // 60)

    @classmethod
    def titel(cls, laufzeit):
        zeilen = ['%s: %s' % (was, cls.text(s)) for was, s in laufzeit['teile']]
        if laufzeit.get('quelle'):
            zeilen.insert(0, laufzeit['quelle'])
        if laufzeit.get('ohne'):
            zeilen.append('ohne Zeitangabe (nicht in der Summe): %s' % ', '.join(laufzeit['ohne']))
        return ' · '.join(zeilen)
