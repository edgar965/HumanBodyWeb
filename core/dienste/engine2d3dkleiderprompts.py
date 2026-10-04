# -*- coding: utf-8 -*-
"""Engine2d3dKleiderprompts — alle Prompts eines Auftrags „2D3D Kleider", je Runde der Iterationen (04.10.2026).

Edgar: „speicher in dem Job alle review Prompts aller Iterationen" und „speicher auch meine Prompts, die ich dir gegeben habe, zu
den einzelnen Iterationen". Eine Datei im Auftrag, `iterationen/prompts.json` (liegt neben den Tafeln, über `datei/iterationen/prompts.json`
lesbar), je Runde drei Arten:

    review    die Frage an die Prüf-KI im Wortlaut (`Begutachtungskritik.fragen`) — nur in Runden, in denen sie gefragt wurde
    begutachtung  was der Begutachter der Runde mitgab: Kommentar und Rezeptzeilen (`POST …/begutachtung/`)
    nutzer    die Nachrichten des Nutzers, mit Zeit; `zuordnung` sagt, wie sie zur Runde kamen: `angabe` (mit dem Aufruf mitgeschickt) oder
              `zeit` (nachträglich der ersten Runde zugeordnet, die nach der Nachricht begann — eine Nachricht, die während einer Runde
              kam, konnte sie nicht mehr beeinflussen)

Nachrichten nach der letzten Runde stehen unter `offen` und wandern in die nächste. Schreiben ist atomar (Datei daneben, dann ersetzen);
ein Fehler beim Ablegen bricht keine Runde ab — der Aufrufer loggt ihn.
"""

import json
import os
from datetime import datetime, timedelta

from django.utils import timezone

__all__ = ['Engine2d3dKleiderprompts']


class Engine2d3dKleiderprompts:
    DATEI = 'prompts.json'
    VERSION = 1
    FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, ablage):
        self.pfad = ablage.iterationen(self.DATEI)

    # ----------------------------------------------------------------- Lesen und Schreiben

    def lesen(self):
        # Dictionary gewollt: so liegt es als JSON im Auftrag
        if self.pfad.is_file():
            return json.loads(self.pfad.read_text(encoding='utf-8'))
        return {'version': self.VERSION, 'runden': {}, 'offen': {'nutzer': []}}

    def _schreiben(self, daten):
        self.pfad.parent.mkdir(parents=True, exist_ok=True)
        zwischen = self.pfad.with_name(self.pfad.name + '.neu')
        zwischen.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding='utf-8')
        os.replace(zwischen, self.pfad)

    @staticmethod
    def _runde(daten, runde):
        return daten['runden'].setdefault(str(int(runde)), {'review': [], 'begutachtung': {}, 'nutzer': []})

    def jetzt(self):
        return timezone.localtime().strftime(self.FORMAT)

    @classmethod
    def nachrichten(cls, roh):
        """Aus der Angabe eines Aufrufs (Text oder Liste von Texten oder `{zeit, text}`) die Liste `[{zeit, text}]`."""
        if not roh:
            return []
        liste = [roh] if isinstance(roh, (str, dict)) else list(roh)
        jetzt = timezone.localtime().strftime(cls.FORMAT)
        aus = []
        for e in liste:
            text = str(e.get('text') if isinstance(e, dict) else e or '').strip()
            if text:
                aus.append({'zeit': str(e.get('zeit') or jetzt) if isinstance(e, dict) else jetzt, 'text': text[:20000]})
        return aus

    # ----------------------------------------------------------------- Eintragen

    def review(self, runde, modell, text):
        """Die Frage an die Prüf-KI nach `runde` im Wortlaut."""
        daten = self.lesen()
        self._runde(daten, runde)['review'].append({'zeit': self.jetzt(), 'modell': str(modell), 'text': str(text)})
        self._schreiben(daten)

    def runde(self, eintrag, nutzer=None):
        """Die Runde `eintrag` (Eintrag aus `ergebnis['iterationen']`) ablegen: Kommentar, Rezeptzeilen, die Nachrichten der Angabe und
        die offenen von vorher."""
        daten = self.lesen()
        feld = self._runde(daten, eintrag['runde'])
        feld['zeit'] = eintrag.get('zeit')
        feld['begutachtung'] = {'kommentar': eintrag.get('kommentar') or '', 'aufrufe': eintrag.get('aufrufe') or '',
                                'automatisch': bool(eintrag.get('automatisch'))}
        neu = [dict(n, zuordnung='angabe') for n in self.nachrichten(nutzer)]
        neu += [dict(n, zuordnung='zeit') for n in daten['offen']['nutzer']]
        daten['offen']['nutzer'] = []
        self._dazu(feld['nutzer'], neu)
        self._schreiben(daten)

    @staticmethod
    def _dazu(liste, neu):
        vorhanden = {(n['zeit'], n['text']) for n in liste}
        liste.extend(n for n in neu if (n['zeit'], n['text']) not in vorhanden)
        liste.sort(key=lambda n: n['zeit'])

    # ----------------------------------------------------------------- Nachtragen

    @classmethod
    def beginn(cls, runden, i):
        """Wann Runde `i` der Liste begann: Ende minus Dauer; ohne Dauer das Ende der Vorgängerin."""
        r = runden[i]
        ende = datetime.strptime(r['zeit'], cls.FORMAT)
        if r.get('sekunden'):
            return ende - timedelta(seconds=float(r['sekunden']))
        return datetime.strptime(runden[i - 1]['zeit'], cls.FORMAT) if i else ende

    def nachtragen(self, nachrichten, runden):
        """Nachrichten `[{zeit, text}]` den Runden `[{runde, zeit, sekunden, kommentar, aufrufe, automatisch}]` zuordnen: jede der ersten
        Runde, die NACH ihr begann; danach unter `offen`. Wiederholbar (doppelte Einträge entfallen). → (zugeordnet, offen)."""
        runden = sorted(runden, key=lambda r: int(r['runde']))
        daten = self.lesen()
        for feld in [*daten['runden'].values(), daten['offen']]:       # die Zuordnung nach Zeit wird neu abgeleitet
            feld['nutzer'] = [n for n in feld['nutzer'] if n.get('zuordnung') != 'zeit']
        mitgegeben = {n['text'] for f in [*daten['runden'].values(), daten['offen']] for n in f['nutzer']}
        for r in runden:
            feld = self._runde(daten, r['runde'])
            feld['zeit'] = r.get('zeit')
            feld['begutachtung'] = {'kommentar': r.get('kommentar') or '', 'aufrufe': r.get('aufrufe') or '',
                                    'automatisch': bool(r.get('automatisch'))}
        beginne = [self.beginn(runden, i) for i in range(len(runden))]
        zugeordnet, offen = 0, []
        for n in sorted(nachrichten, key=lambda m: m['zeit']):
            if n['text'] in mitgegeben:         # mit dem Aufruf einer Runde schon abgelegt (`angabe`)
                continue
            zeit = datetime.strptime(n['zeit'], self.FORMAT)
            ziel = next((i for i, b in enumerate(beginne) if b > zeit), None)
            if ziel is None:
                offen.append(dict(n, zuordnung='zeit'))
                continue
            self._dazu(self._runde(daten, runden[ziel]['runde'])['nutzer'], [dict(n, zuordnung='zeit')])
            zugeordnet += 1
        self._dazu(daten['offen']['nutzer'], offen)
        self._schreiben(daten)
        return zugeordnet, len(offen)
