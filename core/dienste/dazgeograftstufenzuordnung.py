# -*- coding: utf-8 -*-
"""Dazgeograftstufenzuordnung — welcher Punkt der Stufe 2 ist welcher Punkt der Stufe 1? (11.10.2026)

Edgar: „Stufe 2 als Standard — die Regler am Basis-Stück müssen dann auch gehen". Das Basis-Stück „Daz Anatomie Frau" liegt auf Stufe 1 (4.211 Punkte), das angepasste Stück auf Stufe 2 (16.741
Punkte vor der Naht). `Dazgeograftmorphbasis` legte die Regler bisher über „Punkt i ↔ Punkt i". Das geht über zwei Stufen nicht, und zwar aus zwei Gründen (gemessen am 11.10.2026, Frau):

1. Die Punkte der Stufe 1 stehen in der Stufe 2 VORNE und liegen dort fast an derselben Stelle (Catmull-Clark behält die alten Punkte an ihren Nummern): Rohpunkt i der Stufe 2 gegen Rohpunkt i der
   Stufe 1 Median 0,04 mm, p90 0,12 mm, größter Abstand 0,62 mm (zufällig gepaart: Median 33,3 mm).
2. In das Stück kommen die Punkte aber NACH dem Verschweißen der UV-Nähte (`Dazgeograft.nahtfrei`), und das sortiert sie nach ihrer Lage. Die Nummer im Stück ist deshalb nicht die Rohnummer:
   „gleiche Nummer" über die Stufen gepaart gibt Median 35,9 mm Abstand.

Die Zuordnung geht darum über die Rohnummer: Punkt `j` der Stufe 1 (im Stück) → Rohnummer `erste1[j]` → derselbe Rohpunkt in der Stufe 2 → sein Punkt im Stück `rep2[erste1[j]]`. Gemessen:
alle 4.211 Punkte der Stufe 1 haben ein eigenes Gegenstück (4.211 verschiedene Ziele), Abstand Median 0,04 mm, größter 0,62 mm.

Die Reihenfolge im Stück hängt am Käfig (Lage, Realism-Morph 1): beide Stücke müssen aus demselben Käfig gebaut sein, sonst passt die Zuordnung nicht — dagegen steht die Abstandsgrenze.
"""
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Dazgeograftstufenzuordnung']


class Dazgeograftstufenzuordnung:
    #: Unterteilungsstufen, die ein Stück haben kann (`Dazgeograft.STUFE`).
    STUFEN = (1, 2)
    #: Größter Abstand (mm) zwischen Rohpunkt i der groben und der feinen Stufe, bis zu dem die Nummern als „derselbe Punkt" gelten. Gemessen 0,62 mm (Frau, Stufe 1 gegen 2);
    #: ein anderer Käfig oder eine andere Unterteilung liegt Zentimeter daneben.
    MAX_ABSTAND_MM = 3.0
    #: So viele Punkte am Ende der Stufe darf `Dazgeograftmorphbasis` dem Ringschwanz zugeschlagen haben (Punkt auf einer Ringecke).
    SCHWANZ_FEHLER = 3

    @classmethod
    def zuordnen(cls, geschlecht, anzahl_grob, anzahl_fein):
        """Nummern, ein Eintrag je Punkt der groben Stufe: Punkt `j` des groben Stücks (Stufe mit `anzahl_grob` Punkten vor dem Ringschwanz, siehe `SCHWANZ_FEHLER`) → Nummer desselben Punkts im feinen Stück.

        `ValueError`, wenn eine der Zahlen zu keiner Stufe passt, das grobe Stück nicht gröber ist oder die Punkte nicht an derselben Stelle liegen."""
        from .dazgeograft import Dazgeograft
        from .dazgeograftquelle import Dazgeograftquelle

        quelle = Dazgeograftquelle(geschlecht)
        kaefig = quelle.punkte + 1.0 * quelle.morph(Dazgeograft.REALISM)
        stufen = {}
        for stufe in cls.STUFEN:
            bau = Dazgeograft(geschlecht)
            bau.STUFE = stufe
            roh = bau.stufe_punkte(quelle, kaefig)
            erste, rep = bau.nahtfrei(roh)
            stufen[stufe] = (roh, erste, rep)
        return cls.aus_stufen(stufen, anzahl_grob, anzahl_fein, geschlecht)

    @classmethod
    def aus_stufen(cls, stufen, anzahl_grob, anzahl_fein, geschlecht=''):
        """Die reine Rechnung zu `zuordnen`: `stufen` ist `{stufe: (roh, erste, rep)}` (Rohpunkte, `Dazgeograft.nahtfrei`) — ohne Daz-Bibliothek prüfbar."""
        grob = cls._stufe_mit(stufen, anzahl_grob)
        fein = cls._stufe_mit(stufen, anzahl_fein)
        if fein <= grob:
            raise ValueError('das angepasste Stück (Stufe %d) ist nicht feiner als das Basis-Stück (Stufe %d)' % (fein, grob))
        roh_g, erste_g, _rep_g = stufen[grob]
        roh_f, _erste_f, rep_f = stufen[fein]
        abstand = np.linalg.norm(roh_f[erste_g] - roh_g[erste_g], axis=1) * 1000.0
        if float(abstand.max()) > cls.MAX_ABSTAND_MM:
            raise ValueError('Stufe %d und %d tragen die Punkte nicht an denselben Nummern (größter Abstand %.1f mm, Grenze %.1f mm)' % (grob, fein, abstand.max(), cls.MAX_ABSTAND_MM))
        zu = rep_f[erste_g]
        logger.info('Stufenzuordnung %s: Stufe %d → %d, %d Punkte, Abstand Median %.2f mm, größter %.2f mm, %d verschiedene Ziele',
                    geschlecht, grob, fein, len(zu), float(np.median(abstand)), float(abstand.max()), len(np.unique(zu)))
        return zu

    @classmethod
    def _stufe_mit(cls, stufen, anzahl):
        """Die Stufe, die nach dem Verschweißen `anzahl` Punkte hat — bis zu `SCHWANZ_FEHLER` weniger zählt mit: liegt der letzte Punkt der Stufe auf einer Ringecke, rechnet ihn
        `Dazgeograftmorphbasis._stufe_punkte` zum Schwanz (gesehen 11.10.2026: Basis-Stück 4.210 statt 4.211)."""
        for stufe, (_roh, erste, _rep) in stufen.items():
            if 0 <= len(erste) - anzahl <= cls.SCHWANZ_FEHLER:
                return stufe
        raise ValueError('keine Stufe hat %d Punkte (Stufen %s: %s)' % (anzahl, list(stufen), {s: len(v[1]) for s, v in stufen.items()}))
