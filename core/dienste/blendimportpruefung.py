# -*- coding: utf-8 -*-
"""Blendimportpruefung — die Abnahme eines Stücks nach der Rückrechnung in die Ruhelage (Stufe 7 des Konzepts
`Docu/konzepte/2026-10-09_blend-import-kleidung-in-die-ruhelage-konzept.md`).

Vier Kennzahlen, je Stück im Bericht des Schritts „stücke" und eine Warnung, wo eine Schwelle reißt — nie stilles Durchlaufen:

    Kantenverzerrung   Anteil der Kanten, deren Länge in der Ruhelage um mehr als 0,75…1,33 vom Original abweicht, und die größte
                       Streckung (die Rückrechnung darf Stoff nicht dehnen oder zerreißen)
    Frei hängend       Anteil der Punkte weiter als 3 h vom Käfig (`Blendimportlage.befund`): dort taugt die Käfigbewegung nicht
    Haltungstreue      Abstand des Stücks zum Original, wenn die Figur es in der Haltung des Originals trägt (`Blendimporthaltung`)
    Angezogen          wie bisher (`G9gcfigurbau.pruefen`): folgt das Stück der Figur

Die Schwellen waren die Vorschläge des Konzepts (3 % / 3× / 50 % frei / Median 3 mm / p99 10 mm) und lösten bei guten Stücken Hinweise aus. Seit dem 09.10.2026
abends sind sie an den Messwerten dreier Modelle gesetzt (`stand.json` der Läufe cute girl, Asian Female, Fallout ranger; Tabelle in `blendimport-kleidung.md`,
festgehalten in `test_blendimport_abnahme.KalibrierungTest`) und in Käfigeinheiten `h` (Median des Punktabstands des posierten Käfigs, 3,9–4,3 mm):

    Kantenverzerrung    guter Stoff höchstens 2,2 % (Socken), schlecht 6,0 % (Hemd) und 7,9 % (der von der ersten Sohlenfassung zerstörte Stiefel): 3 % / 3× bleiben
    Haltungstreue p99   anliegend 1,0–10,8 mm (Jeans 17,0, Stiefel 11,0, Socken 10,7), hängend 40,9 (Hemd-Ärmel) und 108 (Mantel), der zerstörte Stiefel 28,4:
                        6 h (≈ 24 mm) trennt sie; Median 1,5 h (≈ 6 mm) fängt eine Verschiebung des ganzen Stücks (Schuh mit falschem Drehpunkt: 8,5 mm)
    frei hängend        sagt nichts über den Sitz (Helm 98 %, Seil 87 %, Stiefel 41–88 % sitzen auf 1–5 mm): nur noch ein Hinweis, wo die Haltungstreue FEHLT

Die Trennschärfe an so wenigen schlechten Stücken (zwei hängende, ein zerstörtes) ist dünn — die Schwellen bleiben ein Hinweis, kein Urteil.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportpruefung']


class Blendimportpruefung:
    #: Kanten, deren Längenverhältnis (Ruhelage / Original) außerhalb liegt, gelten als verzerrt.
    KANTEN_VON, KANTEN_BIS = 0.75, 1.33
    #: Hinweis ab diesem Anteil verzerrter Kanten / dieser größten Streckung.
    KANTEN_ANTEIL, STRECKUNG = 0.03, 3.0
    #: Hinweis „lose Kleidung, Sitz ungeprüft" ab diesem Anteil frei hängender Punkte — nur, wenn keine Haltungstreue gemessen wurde.
    FREI_ANTEIL = 0.5
    #: Haltungstreue: Median und p99 in Käfigeinheiten `h` (≈ 6 mm / 24 mm bei h = 4 mm), darüber ein Hinweis.
    HALTUNG_MEDIAN_H, HALTUNG_P99_H = 1.5, 6.0
    #: Käfigeinheit (mm), wenn der Befund sie nicht nennt.
    H_MM = 4.0

    def __init__(self, lage, haltung=None):
        from .blendimportbogen import Blendimportbogen
        from .blendimporthaltung import Blendimporthaltung

        self.lage = lage
        self.haltung = haltung or Blendimporthaltung(lage)
        #: Kontaktbogen aller geprüften Stücke (`Blendimportbogen`), geschrieben vom Aufrufer am Ende.
        self.bogen = Blendimportbogen(lage.kaefig_ruhe, lage.kaefig_posiert)

    @classmethod
    def kanten(cls, ruhe, original, dreiecke):
        """`{ausserhalb, streckung_max, streckung_min}` — Kanten der Ruhelage gegen die des Originals (gleiche Dreiecke)."""
        d = np.asarray(dreiecke, dtype=np.int64)
        a = np.concatenate([d[:, 0], d[:, 1], d[:, 2]])
        b = np.concatenate([d[:, 1], d[:, 2], d[:, 0]])
        verhaeltnis = np.linalg.norm(ruhe[a] - ruhe[b], axis=1) / np.maximum(np.linalg.norm(original[a] - original[b], axis=1), 1e-9)
        return {'ausserhalb': round(float(((verhaeltnis < cls.KANTEN_VON) | (verhaeltnis > cls.KANTEN_BIS)).mean()), 4),
                'streckung_max': round(float(verhaeltnis.max()), 2), 'streckung_min': round(float(verhaeltnis.min()), 3)}

    @classmethod
    def warnungen(cls, kanten, befund, haltung):
        """Die Hinweise zu den Kennzahlen eines Stücks (Texte für den Bericht)."""
        aus = []
        h_mm = float((befund or {}).get('h_mm') or cls.H_MM)
        gemessen = bool(haltung) and 'median_mm' in haltung
        if kanten and (kanten['ausserhalb'] > cls.KANTEN_ANTEIL or kanten['streckung_max'] > cls.STRECKUNG):
            aus.append('Kantenverzerrung %.1f %% (größte Streckung %.1f×) — Stoff in der Ruhelage gedehnt oder gestaucht'
                       % (100.0 * kanten['ausserhalb'], kanten['streckung_max']))
        if not gemessen and befund and befund.get('frei_anteil', 0.0) > cls.FREI_ANTEIL:
            aus.append('%.0f %% der Punkte hängen frei (> 3 h vom Käfig) — lose Kleidung, Sitz ungeprüft' % (100.0 * befund['frei_anteil']))
        if gemessen and (haltung['median_mm'] > cls.HALTUNG_MEDIAN_H * h_mm or haltung['p99_mm'] > cls.HALTUNG_P99_H * h_mm):
            aus.append('Haltungstreue Median %.1f mm, p99 %.1f mm (%.1f %% über 25 mm)'
                       % (haltung['median_mm'], haltung['p99_mm'], 100.0 * haltung['ueber_25']))
        return aus

    def pruefen(self, stueck, ruhe, original, dreiecke, fuss=None, name=None):
        """`{kanten, befund, haltung, warnungen}` für das gespeicherte Stück `stueck`; das Stück kommt auch in den Kontaktbogen. Ein Fehler
        in der Prüfung lässt den Schritt nicht scheitern: er steht im Bericht. `fuss`: der `Blendimportfuss` eines Schuhs — sein Griff geht in die Haltung,
        seine Hinweise in die Warnungen."""
        hinweise = fuss.hinweise() if fuss else []
        try:
            kanten = self.kanten(ruhe, original, dreiecke)
            befund = dict(self.lage.befund or {})
            haltung = self.haltung.treue(stueck, original, fuss.griff() if fuss else None)
            letzte = self.haltung.letzte if haltung and 'median_mm' in haltung else None
            self.bogen.stueck(name or stueck, original, ruhe, dreiecke, self.bogen.schlechte_dreiecke(ruhe, original, dreiecke),
                              letzte and letzte['gestellt'], letzte and letzte['abstand_mm'])
        except Exception as fehler:  # noqa: BLE001 — die Abnahme ist keine Voraussetzung für das Stück
            logger.exception('Blender-Import: Abnahme von %s gescheitert', stueck)
            return {'fehler': str(fehler)[:300]}
        return {'kanten': kanten, 'befund': befund, 'haltung': haltung, 'warnungen': self.warnungen(kanten, befund, haltung) + hinweise}
