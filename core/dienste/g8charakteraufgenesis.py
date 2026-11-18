# -*- coding: utf-8 -*-
u"""G8charakteraufgenesis — Genesis-8-Charaktere (KT Margie …) als Genesis-9-Morphs bauen (16.11.2026).

Edgar, 16.11.2026: „erweitere ggf. den G1-G9 so dass auch G8-G9 funktioniert“ — „ja, mach G8 → G9 mit Margie“. Der Weg der Genesis-1-Kinder
(`G1morpheaufgenesis`) mit drei Unterschieden:

1. QUELLE: ein Charakterpreset (`People/Genesis 8 Female/Characters/**/*.duf`, Typ `character`) statt eines festen Morphs. Seine Form ist
   die Summe der gesetzten Morphs, die auf dem Körper von Genesis 8 sitzen (`parent` = die Figur) und Deltas tragen — bei KT Margie nur
   `KT Margie V8` (16.556 Deltas, 968 Gelenkformeln); die drei Wimpernregler (`PHMEyelashes…`) sitzen auf dem Wimpernnetz und fallen weg.
2. KLON: `G8klonuebertragung` mit `CloneGenesis8Female`/`CloneGenesis8Male`, je nach Ordner des Presets.
3. GRUNDFORM: Die Charakterform ist ein Feld RELATIV zur Grundfigur von Genesis 8 — auf Genesis 9 gehört deshalb die Gestalt von Genesis 8
   darunter. Der Regler trägt beides: Klon-Gestalt (`G9autofit.punkte` − Grundnetz) plus übertragene Form. `g8:<Kennung>` auf 1 ist der Charakter.

Erwachsene haben kein `scale/general` in den Formeln (s = 1): keine Ähnlichkeit abzuspalten, das Feld ist ganz Form. Das Skelett folgt über
`G9gelenkversatz.fuer_morph` aus der Haut geschätzt. Bauen: `manage.py g8charaktere_bauen [--nur "KT Margie G8"]`.
"""
import logging
import time
from urllib.parse import unquote

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from Genesis9.dson import G9dson
from Genesis9.g8morphe import G9g8morphe
from Genesis9.gelenkversatz import G9gelenkversatz

from .g1morpheaufgenesis import G1morpheaufgenesis
from .g8charakterquellen import G8charakterquellen
from .g8hautaufgenesis import G8hautaufgenesis
from .g8klonuebertragung import G8klonuebertragung

logger = logging.getLogger('core')

__all__ = ['G8charakteraufgenesis']


class G8charakteraufgenesis(G1morpheaufgenesis):
    u"""Charakterpresets von Genesis 8 als Genesis-9-Morphs (`g8:`)."""

    def __init__(self, melden=None):
        super().__init__(melden)
        self._uebertragungen = {}

    @staticmethod
    def auftraege(nur=None):
        u"""Charakterpresets und Apply-Sätze von Genesis 8 Female/Male (`G8charakterquellen`)."""
        return G8charakterquellen.auftraege(nur)

    # -------------------------------------------------------------- Lesen

    def vorbereiten(self, klon='CloneGenesis8Female'):
        if klon not in self._uebertragungen:
            self._uebertragungen[klon] = G8klonuebertragung(klon)
        self.uebertragung = self._uebertragungen[klon]
        if self.basis is None:
            from Genesis9.basisnetz import G9basisnetz
            self.basis = Torchfeld.feld(G9basisnetz.holen().punkte, dtype=torch.float64)
        return self

    def morphsumme(self, auftrag):
        u"""`(delta (N, 3) m, formeln, namen)`: Σ Wert × Delta der Morphs, die das Preset setzt und die auf dem Körper sitzen; die Formeln aller."""
        u = self.uebertragung
        delta = torch.zeros_like(u.grund)
        formeln, namen = [], []
        for pfad, wert, bezeichnung in G8charakterquellen.verweise(auftrag):
            if pfad is None:
                logger.warning('G8-Charakter %s: Morph fehlt %s', auftrag['kennung'], bezeichnung)
                continue
            mod = (G9dson.roh(pfad).get('modifier_library') or [{}])[0]
            if auftrag['figur'] not in unquote(str(mod.get('parent') or '')):
                continue                                                    # Wimpern, Brauen: eigenes Netz
            werte = (((mod.get('morph') or {}).get('deltas') or {}).get('values')) or []
            if werte:
                w = Torchfeld.feld(werte, dtype=torch.float64)
                delta[Torchfeld.astype(w[:, 0], torch.int64)] += w[:, 1:] * (self.CM * float(wert))
            formeln += mod.get('formulas') or []
            namen.append((mod.get('name') or mod.get('id'), float(wert), len(werte)))
        return delta, formeln, namen

    # ----------------------------------------------------------- Rechnen

    def zerlegen(self, auftrag):
        u"""`(s, unter_m, form (N, 3) m in Genesis-8-Stellung, versatz, ausrichtung)` — für `feld` (geerbt)."""
        u = self.uebertragung
        delta, formeln, namen = self.morphsumme(auftrag)
        s, versatz, ausrichtung, uebergangen = self.formelwerte(formeln)
        logger.info('G8-Charakter %s: Morphs %s — s %.3f, %d Gelenke aus Formeln, %d übergangen', auftrag['kennung'], namen, s, len(versatz), uebergangen)
        return s, float(u.grund[u.hautpunkte, 1].min()), delta, versatz, ausrichtung

    # -------------------------------------------------------------- Bauen

    def bauen(self, nur=None, haut=True):
        u"""Die Charaktere bauen (`nur`: Dateinamen ohne Endung; `haut`: die Hautbilder mit umbacken); gibt `[{name, punkte, plus_mm, hoehe_m}]` zurück."""
        start = time.perf_counter()
        auftraege = self.auftraege(nur)
        aus = []
        gelenkversatz = G9gelenkversatz()
        for nr, a in enumerate(auftraege, 1):
            self.vorbereiten(a['klon'])
            klonfeld = Torchfeld.feld(self.uebertragung.autofit.punkte, dtype=torch.float64) - self.basis
            plus, _rest, _s, _unter, _zentrum = self.feld(a)
            gesamt = klonfeld + plus                                            # bei Erwachsenen s = 1: plus ist ganz übertragene Form
            nummern = torch.nonzero(Torchfeld.amax(Torchfeld.abs(gesamt), dim=1) > 0, as_tuple=True)[0]
            null = torch.zeros((len(nummern), 3), dtype=torch.float64, device='cuda')
            gelenke = gelenkversatz.fuer_morph(nummern, gesamt[nummern], null)
            hoehe = float(Torchfeld.ptp(self.basis[:, 1] + gesamt[:, 1]))
            quelle = {'quelle': u'%s (Genesis 8), über den Klon %s' % (a['datei'].name, a['klon']), 'anzeige': a['anzeige'], 'kategorie': 'Charaktere',
                      'bereich': 'g8_charaktere', 'reihe': a['reihe'], 'min': 0.0, 'max': 1.0, 'rig': True, 'geschlecht': a['geschlecht'],
                      'hoehe_m': round(hoehe, 3), 'preset': str(a['datei']),
                      'hinweis': u'%s für Genesis 8 — Gestalt von Genesis 8 (Daz’ Klon %s) plus die Charakterform, übertragen auf Genesis 9; Größe %.2f m.'
                                 % (a['anzeige'].split('  ')[0], a['klon'], hoehe)}
            G9g8morphe.ablegen(a['kennung'], nummern, gesamt[nummern], null, quelle, gelenke)
            brief = G9g8morphe.steckbrief(a['kennung'])
            hautquelle = G8charakterquellen.hautquelle(a) if haut else None
            if hautquelle is not None:
                # Die Hautbilder des Charakters auf die G9-Kacheln (`G8hautaufgenesis`); der Katalog nimmt `bilder` aus dem Steckbrief.
                brief['bilder'] = G8hautaufgenesis(self.uebertragung, hautquelle, a['kennung'], a['geschlecht']).backen()
                brief['haut_quelle'] = str(hautquelle)
                G9g8morphe.steckbrief_schreiben(a['kennung'], brief)
            elif haut:
                logger.warning('G8-Charakter %s: keine Haut mit Face und Torso gefunden — Genesis 9 behält seine eigene', a['kennung'])
            aus.append({'name': a['kennung'], 'punkte': brief.get('punkte'), 'plus_mm': brief.get('plus_mm'), 'hoehe_m': round(hoehe, 3)})
            self.melden(nr, len(auftraege), a['kennung'], brief)
        G9g8morphe.bestand_schreiben({'zahl': len(aus), 'sekunden': round(time.perf_counter() - start, 1)})
        logger.info('G8-Charaktere auf Genesis 9: %d Regler in %.1f s nach %s', len(aus), time.perf_counter() - start, G9g8morphe.ordner())
        return aus
