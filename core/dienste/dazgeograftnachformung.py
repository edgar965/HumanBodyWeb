# -*- coding: utf-8 -*-
"""Dazgeograftnachformung — Nachformung und Unterkleid für das angepasste Daz-Geograft, wenn der Import sie nicht passend mitbringt (11.10.2026).

BEFUND (cute girl, Import 11.10.2026 08:45, Einstellung `scham = objekt`): (1) Bei `scham = objekt` kommt die Scham als Stück, und `Blendimportlauf._nachformung` schaltet die Nachformung der Haut ab
(„zwei Mal Geschlechtsorgane"). Das Daz-Geograft braucht sie aber: ohne sie steht die Haut am Becken 10–25 mm vor dem Original, der Ring des Lochs sitzt auf dieser Haut, und das Stück erreicht
das Original nicht (Form Original → Modell p90 3,69 statt 2,92 mm, 4 Ringkanten über 60° statt 0). Ein Neuimport ersetzt zudem den Körpermorph (`…_193211` → `…_084515`): der alte `…_scham`-Morph gehört
dann zu keinem Modell mehr, und der Bau lief still ohne Nachformung weiter. (2) Der Unterkleid-Morph des Imports (`Blendimportunterkleid`) ist ohne Nachformung gerechnet und zählt die Hautpunkte IM
LOCH mit, die das Stück ersetzt: er schob die Haut bis 33,9 mm zurück (im Loch bis 32 mm, am Ring Median 1,6 mm) und kippte die Haut rund um den Ring — Knick über die Naht Median 22° (Nachformung 0 / 0,2 / 0,4:
26,4° / 24,6° / 22,0°) gegen 9,8° ohne ihn; Randband (6–20 mm) und Einlauf am Ring (4–12 mm) änderten daran nichts (Median 20–23°) und verschlechterten die Form.

HIER: (1) Fehlt zu einem Körper-Regler des Modells der Morph `<Regler>_scham`, rechnet `Blendimportnachformung.formen` ihn aus dem Import des Modells (`figur.herkunft.import`) nach — dasselbe Verfahren
wie im Import; der Stand des Imports bleibt unberührt (das Blender-Stück des Imports sitzt auf der Haut OHNE ihn). (2) Der Unterkleid-Morph wird auf der Figur MIT dieser Nachformung und ohne die Hautpunkte im
Loch neu gerechnet und unter eigenem Namen abgelegt (`<Regler>_unterkleid_daz`); der des Imports kommt aus dem Daz-Modell. Gemessen (Probebau, `Schammessung`): Form Original → Modell Median 0,73 / p90 2,62 mm
(alt 0,76 / 2,92), Knick über die Naht Median 12,0° / p90 36,7° / größter 54,0° (alt 10,2° / 32,6° / 51,3°), Kanten über 60°: 0; Zusatz des Unterkleids 3,6 mm, danach 0 Hautpunkte vor der Kleidung.
Gehört der Körper-Regler nicht zum aktuellen Lauf des Imports (der Import wurde danach ersetzt), wird nichts gerechnet und gewarnt.
"""
import logging

import numpy as np

__all__ = ['Dazgeograftnachformung']

logger = logging.getLogger('core')


class Dazgeograftnachformung:
    #: Endungen der Regler, die selbst keine Körper-Regler sind.
    ENDUNGEN = ('_scham', '_unterkleid', '_unterkleid_daz', '_unterkleid_umriss')
    #: Name des Unterkleid-Morphs: mit dem Loch des Geografts `_unterkleid_daz`, mit dem Loch des Blender-Stücks (`Dazgeograftumriss`) `_unterkleid_umriss` — eigener Name, damit die Modelle „cute girl Daz",
    #: „Daz1" und „Daz2" (Loch des Geografts) ihren Morph behalten.
    UNTER_ENDUNG = '_unterkleid_daz'
    UNTER_ENDUNG_UMRISS = '_unterkleid_umriss'

    @staticmethod
    def ist_zusatz(regler):
        """Ist `regler` ein Zusatz-Regler dieses Baus (Nachformung `…_scham`, Unterkleid `…_unterkleid…`) und kein Körper-Regler?"""
        return regler.endswith('_scham') or '_unterkleid' in regler

    @classmethod
    def sichern(cls, daten, wert, loch_maske=None, name=None):
        """`(regler, entfernen)`: `regler` = `{Regler: Wert}`, die das Daz-Modell zusätzlich trägt (Nachformung mit `wert`, Unterkleid `…_unterkleid_daz` mit 1); `entfernen` = Regler des Imports, die es
        nicht trägt (`…_unterkleid`). Fehlende Morphe werden hier gerechnet und abgelegt. `daten`: Inhalt von `data/models/<Modell>.json`.
        `loch_maske`: bool je Dreieck der Haut — das Loch des Blender-Stücks, wenn das Daz-Stück dessen Umriss hat; das Unterkleid lässt dann DIESE Haut aus (Name `…_unterkleid_umriss`), sonst die im Loch des Geografts.
        `name`: kommt der Umriss von einem ANDEREN Stück als dem Vorbild (`Dazgeograftangepasst.UMRISS_VON`), hängt er am Namen des Morphs (`…_unterkleid_umriss_<name>`) — sonst überschriebe der Bau den Morph der Modelle, die den
        Umriss des Vorbilds tragen (am 11.10.2026 passiert: „cute girl daz2" mit dem Loch von alt2 legte den Morph von „Daz3" neu an)."""
        from Genesis9.eigenmorphe import G9eigenmorphe

        figur = daten.get('figur') or {}
        regler = dict(figur.get('regler') or {})
        kennung = (figur.get('herkunft') or {}).get('import')
        neu, entfernen = {}, []
        for koerper in [k for k in regler if k.startswith(G9eigenmorphe.PRAEFIX) and not cls.ist_zusatz(k)]:
            lauf_job = cls._lauf(kennung, koerper)
            scham = koerper + '_scham'
            if not G9eigenmorphe.vorhanden(scham) and not (lauf_job and cls._nachformung(*lauf_job)):
                logger.warning('Daz-Geograft: zu %s fehlt der Nachformungs-Morph und ist aus dem Import nicht zu rechnen — Bau OHNE Nachformung', koerper)
                continue
            neu[scham] = float(wert)
            if koerper + '_unterkleid' in regler:
                entfernen.append(koerper + '_unterkleid')
                unter = lauf_job and cls._unterkleid(*lauf_job, regler, {scham: float(wert)}, loch_maske, name)
                if unter:
                    neu[unter] = 1.0
        return neu, entfernen

    @staticmethod
    def _lauf(kennung, koerper):
        """`(Lauf, Auftrag)` des Imports `kennung`, wenn `koerper` der Körpermorph seines letzten Laufs ist — sonst `None` (mit Warnung)."""
        from .blendimportlauf import Blendimportlauf

        if not kennung:
            logger.warning('Daz-Geograft: das Modell nennt keinen Import (`herkunft.import`) zu %s', koerper)
            return None
        lauf = Blendimportlauf(kennung)
        job = lauf.job()
        aktuell = ((job.ergebnis or {}).get('rest') or {}).get('regler')
        if aktuell != koerper:
            logger.warning('Daz-Geograft: %s gehört nicht zum letzten Lauf des Imports %s (der hat %s) — nichts gerechnet', koerper, kennung, aktuell)
            return None
        return lauf, job

    @staticmethod
    def _nachformung(lauf, job):
        """Die Nachformung des Imports rechnen und ablegen → ob jetzt ein Morph da ist."""
        from .blendimportnachformung import Blendimportnachformung

        bericht = Blendimportnachformung(lauf.ablage, job, lauf.inventar(), lauf.stand['rollen'], lauf.stand['quelle']['name']).formen()
        logger.info('Daz-Geograft: Nachformung aus Import %s gerechnet: %s', lauf.ablage.kennung, {k: v for k, v in bericht.items() if k != 'regler'})
        return bool(bericht.get('regler'))

    @classmethod
    def _unterkleid(cls, lauf, job, regler, zusatzregler, loch_maske=None, name=None):
        """Der Unterkleid-Morph auf der Figur mit `zusatzregler` (Nachformung) ohne die Hautpunkte im Loch, abgelegt als `…_unterkleid_daz` (Loch des Geografts) oder `…_unterkleid_umriss` (`loch_maske`,
        das Loch des Blender-Stücks) → sein Name oder `None` (keine Haut vor der Kleidung)."""
        from .blendimportunterkleid import Blendimportunterkleid

        u = Blendimportunterkleid(lauf.ablage, job, lauf.inventar(), lauf.stand['rollen'], lauf.stand['quelle']['name'])
        endung = cls.UNTER_ENDUNG if loch_maske is None else cls.UNTER_ENDUNG_UMRISS + ('_' + name if name else '')
        bericht = u.formen(zusatzregler, ausnehmen=cls._lochpunkte(regler, loch_maske), endung=endung)
        logger.info('Daz-Geograft: Unterkleid für die Figur mit Nachformung gerechnet: %s', {k: v for k, v in bericht.items() if k != 'regler'})
        return next(iter(bericht.get('regler') or {}), None)

    @classmethod
    def _lochpunkte(cls, regler, loch_maske=None):
        """Maske der Hautpunkte (Stufe 1) im Loch des Daz-Geografts (`Dazgeograftquelle.versteckt`) oder im `loch_maske` des Blender-Stücks, ohne die Punkte auf dem Ring — sie sind topologisch fest."""
        from .blendimportschamloch import Blendimportschamloch
        from .dazgeografthaut import Dazgeografthaut
        from .dazgeograftquelle import Dazgeograftquelle

        grund = Dazgeografthaut.grundfigur({k: v for k, v in regler.items() if '_unterkleid' not in k})
        if loch_maske is not None:
            maske = np.asarray(loch_maske, dtype=bool)
        else:
            maske, _bericht = Dazgeografthaut.loch(grund, Dazgeograftquelle('frau').versteckt)
        haut = Blendimportschamloch(grund['punkte'], grund['dreiecke'])
        ring = [int(x) for x in haut.ringpunkte(haut.ring(maske))]
        innen = np.zeros(len(grund['punkte']), dtype=bool)
        innen[np.unique(np.asarray(grund['dreiecke'])[np.flatnonzero(maske)])] = True
        innen[ring] = False
        return innen
