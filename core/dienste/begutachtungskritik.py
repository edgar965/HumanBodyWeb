# -*- coding: utf-8 -*-
"""Begutachtungskritik — die Prüf-KI nach einer automatischen Runde von „2D3D Kleider" (01.10.2026).

Fällig alle `pruefki_alle` Runden und nach `pruefki_stillstand` Runden ohne Besserung (Optionen der Gruppe
`iterationen`, dieselbe Regel wie `Iterationswahl.kritik_faellig`). Sie bekommt die Vergleichstafel der letzten Runde
und die Frage aus `Begutachtungsprompt`; zurück kommt JSON (`SCHEMA`) mit Urteil, Bereichen, fehlenden Einzelheiten,
`fertig` und Rezeptzeilen. Jede Zeile prüft `G9rezept.pruefen` für sich (eine schlechte Zeile kostet nicht die anderen);
dazu: keine Funktion aus `VERBOTEN` (die Haltung bleibt A-Pose; Hülle, Drapieren, Fototextur und Körperregler sind
Sache der Automatik), Stücke und Frisuren nur aus der Garderobe, Form- und Texturaufrufe nur an getragenen Stücken,
`morph_wert`/`bild_wert` nur an Reglern, die es schon gibt. Die angenommenen Zeilen kommen HINTER die der Automatik ins
Rezept der nächsten Runde — ein Fehler beim Anwenden träfe so nur sie. Sagt sie `fertig` bei Ähnlichkeit ≥ `FERTIG_AB`,
endet der automatische Lauf (Edgar: „so lange iterieren, bis das Ergebnis OK ist"). Ollama nicht erreichbar oder Unsinn
im JSON: ein Eintrag mit `fehler`, der Lauf geht ohne Prüf-KI weiter, nicht ohne Runden.
"""

import base64
import logging

from Genesis9.modellrezept import G9rezept

from .begutachtungsprompt import Begutachtungsprompt
from .iterationsoptionen import Iterationsoptionen
from .ollamamodelle import Ollamamodelle

logger = logging.getLogger('core')

__all__ = ['Begutachtungskritik']


class Begutachtungskritik:
    HOECHSTENS = 8
    FERTIG_AB = Begutachtungsprompt.FERTIG_AB
    KRITIKEN_HOECHSTENS = 30
    VERBOTEN = ('haltung', 'haltung_gelenk', 'kleid_huelle', 'koerper_huelle', 'kleid_drapieren', 'kleid_fototextur',
                'haar_fototextur', 'koerper_regler', 'koerper_regler_setzen', 'kleid_alle_aus')
    STUECKE = ('kleid_nur', 'kleid_anteil', 'kleid_aus')
    FRISUREN = ('haar_nur', 'haar_anteil')
    #: Aufrufe, deren erstes Argument ein GETRAGENES Stück bzw. die getragene Frisur sein muss.
    AN_KLEID = ('kleid_ring', 'kleid_welle', 'kleid_decal', 'kleid_falten', 'kleid_morph', 'kleid_farbe_je_stueck')
    AN_HAAR = ('haar_trim', 'haar_clump', 'haar_noise', 'haar_straighten', 'haar_biegen', 'haar_anlegen', 'haar_morph',
               'haar_achse')
    SCHEMA = {
        'type': 'object',
        'properties': {
            'fertig': {'type': 'boolean'},
            'aehnlichkeit': {'type': 'integer', 'enum': list(range(1, 11))},
            'urteil': {'type': 'string'},
            'bereiche': {'type': 'array', 'items': {'type': 'object', 'properties': {
                'bereich': {'type': 'string'}, 'passt': {'type': 'integer', 'enum': list(range(1, 11))},
                'abweichung': {'type': 'string'}}, 'required': ['bereich', 'passt', 'abweichung']}},
            'fehlt_im_modell': {'type': 'array', 'items': {'type': 'string'}},
            'rezept': {'type': 'array', 'items': {'type': 'string'}},
            'begruendung': {'type': 'string'},
        },
        'required': ['fertig', 'aehnlichkeit', 'urteil', 'bereiche', 'fehlt_im_modell', 'rezept', 'begruendung'],
    }

    def __init__(self, optionen, ablage, prompt=None):
        """`optionen`: Gruppe `iterationen` (`Iterationsoptionen.pruefen`), `ablage`: `Haarengineablage` (die Tafeln),
        `prompt`: ein `Begutachtungsprompt` — sonst der aus der Bibliothek beim ersten Fragen."""
        self.o = optionen or {}
        self.ablage = ablage
        self.prompt = prompt
        self.modell_name = str(self.o.get('pruefki') or Iterationsoptionen.AUS)

    # ---------------------------------------------------------------- Wann

    @staticmethod
    def ohne_besserung(verlauf):
        """Runden seit der besten Abweichung (Verlauf `[[runde, abweichung, …], …]`)."""
        werte = [float(p[1]) for p in verlauf if p and len(p) > 1 and p[1] is not None]
        if not werte:
            return 0
        beste = min(range(len(werte)), key=lambda i: werte[i])
        return len(werte) - 1 - beste

    def faellig(self, z):
        if self.modell_name == Iterationsoptionen.AUS:
            return False
        runde = int(z.get('letzte_runde') or 0)
        seit = runde - int(z.get('kritik_runde') or 0)
        if runde < 1 or seit < 1:
            return False
        alle = max(1, int(self.o.get('pruefki_alle') or 5))
        flaute = max(1, int(self.o.get('pruefki_stillstand') or 3))
        return runde % alle == 0 or (self.ohne_besserung(z.get('verlauf') or []) >= flaute and seit >= flaute)

    # -------------------------------------------------------------- Fragen

    def tafel(self, z):
        pfad = self.ablage.iterationen('runde_%03d_vergleich.png' % int(z.get('letzte_runde') or 0))
        return pfad if pfad.is_file() else None

    @staticmethod
    def _kodieren(pfad):
        with open(pfad, 'rb') as f:
            return base64.b64encode(f.read()).decode('ascii')

    def fragen(self, modell, z):
        """→ Eintrag `{runde, modell, aehnlichkeit, urteil, fertig, bereiche, fehlt, zeilen, verworfen, begruendung,
        sekunden}` — oder `{runde, modell, fehler}`."""
        runde = int(z.get('letzte_runde') or 0)
        eintrag = {'runde': runde, 'modell': self.modell_name}
        tafel = self.tafel(z)
        if tafel is None:
            return dict(eintrag, fehler='keine Vergleichstafel der Runde %d' % runde)
        try:
            prompt = self.prompt or Begutachtungsprompt.aus_bibliothek()
            self.prompt = prompt
            befund = z.get('befund') or {}
            text = prompt.text(modell, befund, befund.get('note') or z.get('letzte_note') or {}, runde, self.HOECHSTENS)
            antwort, zahlen = Ollamamodelle.fragen(self.modell_name, text, [self._kodieren(tafel)], self.SCHEMA)
        except Exception as fehler:  # noqa: BLE001 — Ollama weg, Unsinn im JSON: der Lauf geht ohne Prüf-KI weiter
            logger.warning('2D3D Kleider: Prüf-KI %s nach Runde %d: %s', self.modell_name, runde, fehler)
            return dict(eintrag, fehler=str(fehler)[:500])
        return dict(eintrag, **self.deuten(antwort, modell, prompt),
                    sekunden=round((zahlen.get('total_duration') or 0) / 1e9, 1))

    def deuten(self, antwort, modell, prompt):
        stufe = antwort.get('aehnlichkeit')
        zeilen, verworfen = self.zeilen(antwort.get('rezept'), modell, prompt)
        bereiche = [{'bereich': str(e.get('bereich') or '')[:40], 'passt': e['passt'],
                     'abweichung': str(e.get('abweichung') or '')[:240]}
                    for e in (antwort.get('bereiche') if isinstance(antwort.get('bereiche'), list) else [])
                    if isinstance(e, dict) and isinstance(e.get('passt'), int) and 1 <= e['passt'] <= 10][:12]
        return {'aehnlichkeit': stufe if isinstance(stufe, int) and 1 <= stufe <= 10 else None,
                'urteil': str(antwort.get('urteil') or '')[:500],
                'fertig': antwort.get('fertig') is True,
                'bereiche': bereiche,
                'fehlt': [str(x)[:120] for x in (antwort.get('fehlt_im_modell') or []) if isinstance(x, str)][:12],
                'zeilen': zeilen, 'verworfen': verworfen,
                'begruendung': str(antwort.get('begruendung') or '')[:1000]}

    # -------------------------------------------------------------- Zeilen

    def zeilen(self, roh, modell, prompt):
        """→ (angenommene Zeilen, [(Zeile, Grund)] der verworfenen)."""
        from iterationen2d3d.iterationkleider import IterationKleider
        kleider = {k for k, _a in IterationKleider.sorten(modell.kleidung, modell.SORTE)}
        frisuren = {k for k, _a in IterationKleider.sorten(modell.haar, modell.SORTE)}
        aus, verworfen = [], []
        for zeile in roh if isinstance(roh, list) else []:
            text = str(zeile or '').strip()
            if not text or text.startswith('#'):
                continue
            grund = self._pruefen(text, modell, prompt, kleider, frisuren)
            if grund:
                verworfen.append((text[:200], grund))
            elif len(aus) < self.HOECHSTENS:
                aus.append(text)
        return aus, verworfen

    def _pruefen(self, text, modell, prompt, kleider, frisuren):
        """'' wenn die Zeile gilt, sonst der Grund."""
        try:
            aufrufe = G9rezept.pruefen(text)
        except ValueError as fehler:
            return str(fehler)
        if len(aufrufe) != 1:
            return 'eine Zeile, ein Aufruf'
        _zeile, name, args, kwargs = aufrufe[0]
        erstes = args[0] if args else kwargs.get('kennung', kwargs.get('sorte'))
        if name in self.VERBOTEN:
            return '%s regelt die Automatik' % name
        if name in self.STUECKE:
            fremd = [a for a in args if not isinstance(a, str) or a not in prompt.garderobe_ids()]
            if fremd or not args:
                return 'nicht in der Garderobe: %s' % (fremd or args)
        elif name in self.FRISUREN:
            if not isinstance(erstes, str) or erstes not in prompt.frisur_ids():
                return 'nicht in der Garderobe: %r' % (erstes,)
        elif name in ('morph_ort', 'morph_neu'):
            art, kennung = (args[0] if args else None), (args[1] if len(args) > 1 else None)
            if kennung not in (frisuren if art == 'haar' else kleider):
                return 'nicht getragen: %r' % (kennung,)
        elif name in self.AN_KLEID and erstes not in kleider:
            return 'nicht getragen: %r' % (erstes,)
        elif name in self.AN_HAAR and erstes not in frisuren:
            return 'nicht getragen: %r' % (erstes,)
        elif name in ('morph_wert', 'bild_wert'):
            if len(args) < 3:
                return '%s(art, kennung, name, wert)' % name
            werte = modell.haar if args[0] == 'haar' else modell.kleidung
            praefix = modell.EIGEN if name == 'morph_wert' else getattr(modell, 'BILD', 'bild.')
            if '%s.%s%s' % (args[1], praefix, args[2]) not in werte:
                return 'Regler gibt es nicht: %s' % args[2]
        return ''

    # ------------------------------------------------------------ Ergänzen

    @staticmethod
    def beenden(lauf, z, beg, zusatz):
        """Die Prüf-KI hält das Ergebnis für OK (Edgar: „so lange iterieren, bis das Ergebnis OK ist"): Stand sichern,
        der Lauf endet ohne weitere Runde (`Begutachtungsrunde.ausfuehren`)."""
        beg.update(zustand='wartet', fertig={'runde': z.get('letzte_runde'), 'urteil': zusatz})
        lauf.job.ergebnis['kreislauf'] = z
        lauf.job.ergebnis['begutachtung'] = beg
        lauf.sichern('ergebnis')
        lauf.melden(1.0, 'Prüf-KI: Ergebnis OK nach Runde %s — Lauf beendet' % z.get('letzte_runde'))

    def ergaenzen(self, rezept, modell, z):
        """Das Rezept der Automatik um die Zeilen der Prüf-KI ergänzen, wenn sie fällig ist → (rezept, Zusatz zum
        Kommentar der Runde, fertig). Der Eintrag geht nach `z['kritiken']`, `z['kritik_runde']` merkt die Runde."""
        if not self.faellig(z):
            return rezept, '', False
        kritik = self.fragen(modell, z)
        z['kritik_runde'] = kritik['runde']
        z['kritiken'] = (list(z.get('kritiken') or []) + [kritik])[-self.KRITIKEN_HOECHSTENS:]
        if kritik.get('fehler'):
            return rezept, 'Prüf-KI %s: %s' % (self.modell_name, kritik['fehler']), False
        stufe = kritik.get('aehnlichkeit')
        fertig = bool(kritik.get('fertig')) and (stufe or 0) >= self.FERTIG_AB
        zusatz = 'Prüf-KI %s: Ähnlichkeit %s/10 — %s%s' % (self.modell_name, '?' if stufe is None else stufe,
                                                             kritik.get('urteil') or '', ' · fertig' if fertig else '')
        if kritik['zeilen']:
            kopf = '# Prüf-KI %s nach Runde %d: %s\n' % (self.modell_name, kritik['runde'],
                                                          (kritik.get('urteil') or '').replace('\n', ' ')[:120])
            rezept = (rezept or '') + kopf + '\n'.join(kritik['zeilen']) + '\n'
        return rezept, zusatz, fertig
