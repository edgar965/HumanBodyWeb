# -*- coding: utf-8 -*-
u"""G9lagenanfrage — die getragenen Stuecke aus dem Anfragerumpf, fuer die
Kollision Stueck gegen Stueck (`Genesis9/lagen.py`, 19.09.2026).

Der Browser schickt zu jedem Stueck die ANDEREN getragenen Stuecke mit
(`getragen: [{kennung, stil, regler_stueck}]`, in Anziehreihenfolge) und
seinen eigenen Platz darin (`rang`). Hier werden deren Kaefige gerechnet,
gegen das angefragte Stueck eingeordnet und die Kollisionsflaeche gebaut:
Haut plus innere Stuecke. Die Antwort traegt `innen` (worueber das Stueck
gehoben wurde) und `aussen` (Stuecke, die UEBER ihm liegen — die muss der
Browser neu holen, denn ihre Flaeche hat sich mit diesem Stueck geaendert).

Ein getragenes Stueck, das nicht ladbar ist, faellt still aus der Rechnung —
mit Log, nicht mit Fehlerantwort: Das angefragte Stueck ist trotzdem zeigbar.

DIE KAEFIGE DER GETRAGENEN STUECKE WERDEN GEMERKT (`_kaefige`): Ein
Reglerzug holt alle Stuecke neu, und jedes fragt nach den anderen — ohne
Vorrat rechnete ein Outfit mit sieben Teilen 42 Kaefige statt sieben.
Schluessel: Kennung, Reglerstellung, Stile, Stueckregler.
"""
import base64
import json
import logging
import os
import threading
from collections import OrderedDict

import numpy as np
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.lagen import G9lagen

logger = logging.getLogger('core')

__all__ = ['G9lagenanfrage']


class G9lagenanfrage:
    u"""`vorbereiten(kennung, kaefig)` -> (Flaeche, innen, aussen)."""

    #: Mehr getragene Stuecke rechnet niemand gegen — ein Outfit hat sieben Teile.
    HOECHSTENS = 24
    #: Gemerkte Kaefige getragener Stuecke (Schluessel -> (N, 3)), die juengsten.
    KAEFIGE_MAX = 32
    #: Vorsatz der Kennung eines GarmentCode-Stuecks in `innen`/`aussen`.
    GC = 'gc:'
    _kaefige = OrderedDict()
    _schloss = threading.Lock()

    def __init__(self, rumpf, formung, koerper, grob=None, gc=None):
        u"""`koerper`: Haut der Anfragestufe; `grob`: Haut auf Stufe 0 (sonst aus
        `formung` gerechnet, nur wenn Stuecke getragen sind). `gc`: getragene
        GarmentCode-Stuecke `[{stueck, ordner, rig_datei}]` (24.09.2026)."""
        self.formung = formung
        roh = rumpf.get('getragen') if isinstance(rumpf, dict) else None
        self.eintraege = [e for e in (roh or []) if isinstance(e, dict)][:self.HOECHSTENS]
        self.gc = [e for e in (gc or []) if isinstance(e, dict)][:self.HOECHSTENS]
        if grob is None and (self.eintraege or self.gc) and formung is not None:
            grob = G9koerpernetz(formung, stufen=0).koerperflaeche()
        self.lagen = G9lagen(koerper, grob)
        try:
            self.rang = int(rumpf.get('rang', len(self.eintraege)))
        except (TypeError, ValueError, AttributeError):
            self.rang = len(self.eintraege)

    def vorbereiten(self, kennung, teile):
        u"""`teile`: `[(G9folger, Kaefigpunkte)]` des angefragten Stuecks.
        Ohne getragene Stuecke die Haut selbst und zwei leere Listen."""
        if not self.eintraege and not self.gc:
            return self.lagen.koerper, [], []
        kaefig = np.vstack([self.lagen.gehoben(folger, punkte) for folger, punkte in teile]
                           or [np.zeros((0, 3))])
        andere = []
        for nummer, eintrag in enumerate(self.eintraege):
            andere_kennung = self._kennung(eintrag.get('kennung'))
            if not andere_kennung or andere_kennung == kennung:
                continue
            try:
                punkte = self._kaefig(andere_kennung, self._namen(eintrag.get('stil')),
                                      eintrag.get('regler_stueck'))
            except (ValueError, OSError, KeyError) as fehler:
                logger.warning('Genesis 9: getragenes Stück %s nicht rechenbar: %s',
                               andere_kennung, fehler)
                continue
            andere.append((andere_kennung, punkte, nummer >= self.rang))
        # GarmentCode-Stuecke (24.09.2026): ihr fertiges Netz ist der Kaefig —
        # schon aus der Haut gehoben. Frueher angezogen, also `spaeter` False.
        for eintrag in self.gc:
            punkte = self._gc_kaefig(eintrag)
            if punkte is not None:
                andere.append((self.GC + str(eintrag.get('stueck') or '?'), punkte, False))
        innen, aussen = self.lagen.einordnen(kaefig, andere)
        # Ein GarmentCode-Stueck ist EINE Stofflage — ohne `aussenlage` (24.09.2026,
        # `Genesis9/lagenflaeche.py`: 22 % der Kleidpunkte fielen dort heraus).
        unten = [(k, p) for k, p, _s in andere if k in innen]
        flaeche = self.lagen.flaeche([p for _k, p in unten],
                                     einlagig=[k.startswith(self.GC) for k, _p in unten])
        return flaeche, innen, aussen

    def _kaefig(self, kennung, stile, regler):
        u"""Der gehobene Kaefig eines getragenen Stuecks — aus dem Vorrat oder gerechnet."""
        schluessel = json.dumps([kennung, self.formung.fingerabdruck(), stile, regler],
                                sort_keys=True, default=str)
        with self._schloss:
            punkte = self._kaefige.get(schluessel)
            if punkte is not None:
                self._kaefige.move_to_end(schluessel)
                return punkte
        punkte = self.lagen.kaefig(kennung, self.formung, stile, regler)
        with self._schloss:
            self._kaefige[schluessel] = punkte
            while len(self._kaefige) > self.KAEFIGE_MAX:
                self._kaefige.popitem(last=False)
        return punkte

    def _gc_kaefig(self, eintrag):
        u"""Die Punkte eines getragenen GarmentCode-Stuecks (Rig-Datei) im Rahmen
        der Daz-Stuecke — oder None (Pfad ungueltig, Datei unlesbar, leer).
        Vom Browser mitgeschickte Punkte (`_gc_punkte`) gehen vor."""
        mitgebracht = self._gc_punkte(eintrag)
        netz = self._gc_netz(eintrag)
        if netz is None:
            return None
        return mitgebracht if mitgebracht is not None else netz[0]

    def huellen(self, innen):
        u"""`G9stoffhuelle` je GarmentCode-Stueck in `innen` (24.09.2026, Haar ueber dem
        Kleid): das Netz mit Dreiecken, gegen das `G9stueckteile` die Punkte zuletzt hebt."""
        from Genesis9.stoffhuelle import G9stoffhuelle
        huellen = []
        for eintrag in self.gc:
            if self.GC + str(eintrag.get('stueck') or '?') not in innen:
                continue
            netz = self._gc_netz(eintrag)
            punkte = self._gc_kaefig(eintrag)
            if netz is None or punkte is None or not len(netz[1]) or netz[1].max() >= len(punkte):
                continue
            huelle = G9stoffhuelle(punkte, netz[1], haut=self.lagen.grob)
            if not huelle.leer:
                huellen.append(huelle)
        return huellen

    def _gc_netz(self, eintrag):
        u"""`(Punkte, Dreiecke)` der Rig-Datei im Rahmen der Daz-Stuecke — oder None.

        Die Rig-Datei liegt in GarmentCodes Projektlage (m, Z oben,
        `G9garmentfigur.projekt`: (x, -z, y)); zurueck heisst (x, z_p, -y_p).
        Gemerkt je Pfad UND Aenderungszeit: ein Neubau schreibt dieselbe Datei."""
        from .gcrigpfad import Gcrigpfad
        pfad = Gcrigpfad.pfad(eintrag)
        if pfad is None:
            return None
        schluessel = json.dumps(['gc', pfad, os.path.getmtime(pfad)])
        with self._schloss:
            netz = self._kaefige.get(schluessel)
            if netz is not None:
                self._kaefige.move_to_end(schluessel)
                return netz
        try:
            with open(pfad, encoding='utf-8') as datei:
                daten = json.load(datei)
            projekt = np.asarray(daten.get('punkte') or [], dtype=np.float64)
            dreiecke = np.asarray(daten.get('dreiecke') or [], dtype=np.int64).reshape(-1, 3)
        except (OSError, ValueError) as fehler:
            logger.warning('Genesis 9: GarmentCode-Stück %s nicht lesbar: %s',
                           os.path.basename(pfad), fehler)
            return None
        if projekt.ndim != 2 or projekt.shape[1] != 3 or not len(projekt):
            return None
        netz = (np.column_stack([projekt[:, 0], projekt[:, 2], -projekt[:, 1]]), dreiecke)
        with self._schloss:
            self._kaefige[schluessel] = netz
            while len(self._kaefige) > self.KAEFIGE_MAX:
                self._kaefige.popitem(last=False)
        return netz

    #: Mehr Punkte nimmt `_gc_punkte` nicht an (die Harem Pants hat 9.966).
    GC_PUNKTE_MAX = 400000

    @classmethod
    def _gc_punkte(cls, eintrag):
        u"""Vom Browser mitgeschickte Punkte (Three-Lage, float32, base64) eines
        GarmentCode-Stuecks, das einem Reglerzug nachgeformt wurde
        (`Gcreglerfolge`, 24.09.2026) — die Rig-Datei kennt nur die Form vom Bau.
        None ohne Angabe; kaputte Angaben ebenso, mit Warnung."""
        roh = eintrag.get('punkte') if isinstance(eintrag, dict) else None
        if not roh:
            return None
        try:
            feld = np.frombuffer(base64.b64decode(roh, validate=True), dtype=np.float32)
        except (ValueError, TypeError) as fehler:
            logger.warning('Genesis 9: Punkte von %s nicht lesbar: %s', eintrag.get('stueck'), fehler)
            return None
        zahl = len(feld) // 3
        if not len(feld) or len(feld) % 3 or zahl > cls.GC_PUNKTE_MAX or not np.isfinite(feld).all():
            logger.warning('Genesis 9: Punkte von %s verworfen (%d Werte)', eintrag.get('stueck'), len(feld))
            return None
        return feld.reshape(-1, 3).astype(np.float64)

    @staticmethod
    def _kennung(wert):
        text = str(wert or '').strip()
        if not text or '/' in text or '\\' in text or '..' in text:
            return None
        return text[:80]

    @classmethod
    def _namen(cls, wert):
        roh = wert if isinstance(wert, (list, tuple)) else [wert]
        return [n for n in (cls._kennung(w) for w in roh) if n]
