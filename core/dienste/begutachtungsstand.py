# -*- coding: utf-8 -*-
u"""Begutachtungsstand — nach jeder Runde von „2D3D Kleider": Gesamtnote, Auswahl, Stand (01.10.2026, Punkt 2).

Aus `Begutachtungsrunde._stand` herausgelöst (die Datei stand bei 302 Zeilen). Bis dahin war der Stand die LETZTE Runde
und jede Runde wurde übernommen, auch eine schlechtere. Jetzt:

    1. `Gesamtnote` der Runde (Foto + Farbe je Teil + Gesicht, ohne die Netznote) — in `note.gesamt`/`note.teilnoten`
       des Rundeneintrags, sichtbar in der Notiz
    2. `Rundenauswahl`: besser → beste Runde; Umbau → Probe; sonst verworfen (Zeilen für die Lage gesperrt)
    3. der Stand (`kreislauf.modell`, `befund`, `note`, `ergebnis/modell.glb`) ist die BESTE Runde; eine laufende Probe
       steht in `kreislauf.weiter` — von dort geht die nächste Runde aus (`Begutachtungsrunde.ausfuehren`)

`fortschreiben` gibt das Modell zurück, mit dem es weitergeht.
"""

import logging
import shutil

logger = logging.getLogger('core')

__all__ = ['Begutachtungsstand']


class Begutachtungsstand:
    AKTION = {'besser': 'übernommen — beste Runde', 'probe': 'Probe (Umbau, %d von %d)',
              'verworfen': 'verworfen — zurück zu Runde %d', 'probe_verworfen': 'Probe verworfen — zurück zu Runde %d'}

    def __init__(self, runde):
        self.r = runde
        self.lauf, self.job, self.ablage = runde.lauf, runde.job, runde.ablage

    # ------------------------------------------------------------- Rezepte

    @staticmethod
    def normalisieren(rezept):
        """Rezepttext mit Aufrufen in der Schreibweise von `G9rezept.text` (so stehen sie im Rundeneintrag und in den
        Sperren) — Kommentare bleiben; ein unlesbarer Text bleibt, wie er ist."""
        from Genesis9.modellrezept import G9rezept
        aus = []
        for zeile in str(rezept or '').splitlines():
            if not zeile.strip() or zeile.strip().startswith('#'):
                aus.append(zeile)
                continue
            try:
                aus += [G9rezept.text(n, a, k) for _z, n, a, k in G9rezept.pruefen(zeile)]
            except ValueError:
                aus.append(zeile)
        return '\n'.join(aus) + ('\n' if aus else '')

    @classmethod
    def ohne_gesperrte(cls, rezept, z):
        """Das Rezept der Automatik ohne die Zeilen, die aus dieser Lage schon verworfen wurden ('' = nichts übrig)."""
        from iterationen2d3d.rundenauswahl import Rundenauswahl
        return Rundenauswahl.filtern(cls.normalisieren(rezept), Rundenauswahl(z.get('auswahl')).verboten())

    @staticmethod
    def befund(z):
        """Der Befund, von dem die nächste Runde ausgeht: der der Probe, sonst der des Stands."""
        return (z.get('weiter') or {}).get('befund') or z.get('befund')

    @classmethod
    def befund_fuer_regeln(cls, z):
        """`befund(z)` für die Automatik — ohne die Renderfarben, wenn er unter einem anderen Renderer gemessen wurde
        als dem, der die nächste Runde rendert (oder ohne Angabe, vor dem 01.10.2026 nachmittags). Mitsuba rechnet die
        Mehrfachstreuung zwischen den Haarkarten: dasselbe Mavick Hair kam dort 131/109/84 statt 152/140/124 (pyrender);
        mit der Schicht `grau` treffen beide (161 / 155, `haartoenung.py`). Ein Farbschritt aus einem pyrender-Befund
        für eine Mitsuba-Runde lief am `_test_fixe` von Runde 40 auf 41 über: Render 0,64 → 0,27 bei Foto 0,44."""
        from .mitsubaszene import Mitsubaszene
        from .renderwahl import Renderwahl
        befund = cls.befund(z)
        motor = Renderwahl.gewaehlt()
        motor = 'pyrender' if motor == 'mitsuba' and Mitsubaszene.mitsuba() is None else motor
        if not befund or befund.get('motor') == motor:
            return befund
        teile = {k: dict(v or {}, render_farbe=None) for k, v in (befund.get('teile') or {}).items()}
        return dict(befund, teile=teile)

    # ------------------------------------------------------------ fortschreiben

    def _eintrag(self, runde):
        alle = self.job.ergebnis.get('iterationen') or []
        return next((e for e in reversed(alle) if int(e.get('runde') or 0) == runde), None)

    def _ansichten_gewechselt(self, auswahl, runde):
        """Zählt diese Runde mehr oder weniger Ansichten (Fotos mit Winkel in der Note, `je_ansicht`) als die beste, sind ihre
        Noten nicht vergleichbar: Zwischen Runde 37 (vier Ansichten, Abweichung 0,3652) und Runde 39 (acht, 0,4466) lag
        nur ein anderer Satz Fotos — die Schrägansichten passen schlechter, ohne dass das Modell schlechter wäre
        (Edgar, 03.10.2026: „du benutzt nicht alle Bilder"; die Schrägen stehen auf „Nur Iterationen")."""
        beste = auswahl.beste
        if not beste:
            return False
        neu = len((self._eintrag(runde) or {}).get('je_ansicht') or [])
        alt = len((self._eintrag(int(beste['runde'])) or {}).get('je_ansicht') or [])
        return bool(neu and alt and neu != alt)

    def _gesicht_nachziehen(self, auswahl, teilnoten, befund):
        """Misst diese Runde das Gesicht in anderer Fassung (`Gesichtsmasse.FASSUNG`) als die beste Runde, zählt die
        beste mit dem Gesichtsterm DIESER Runde (Kopf als unverändert angenommen) — sonst verwürfe ein Wechsel der
        Messung jede Runde: am `_test_fixe` (01.10.2026) gab dasselbe Modell 0,9365 (Einzelwurf) und 0,9481 (Median)."""
        fassung = ((befund or {}).get('gesicht') or {}).get('fassung')
        beste = auswahl.beste
        if not beste or fassung is None:
            return
        alt = self._eintrag(int(beste['runde'])) or {}
        if (beste.get('gesicht_fassung') or ((alt.get('befund') or {}).get('gesicht') or {}).get('fassung')) == fassung:
            return
        alt_gesicht = ((alt.get('note') or {}).get('teilnoten') or {}).get('gesicht')
        if alt_gesicht is None:
            return
        logger.info('2D3D Kleider %s: Gesichtsmessung Fassung %s — beste Runde %s neu gezählt (%.4f → %.4f)',
                    self.job.kennung, fassung, beste['runde'], float(beste['gesamt']),
                    float(beste['gesamt']) - float(alt_gesicht) + teilnoten['gesicht'])
        beste.update(gesamt=round(float(beste['gesamt']) - float(alt_gesicht) + teilnoten['gesicht'], 4),
                     gesicht_fassung=fassung)

    def _haar_nachziehen(self, auswahl, teilnoten, befund):
        """Wie `_gesicht_nachziehen` für den Haarterm (`Haarabgleich.FASSUNG`, 02.10.2026): Misst die beste Runde das
        Haar nicht oder anders, zählt sie mit dem Haarterm DIESER Runde. Ehrlich ist das nur, wenn diese Runde das Haar
        nicht ändert — deshalb kommt nach einem Wechsel der Messung zuerst eine Runde ohne Rezept."""
        fassung = ((befund or {}).get('haarabgleich') or {}).get('fassung')
        beste = auswahl.beste
        if not beste or fassung is None:
            return
        eintrag = self._eintrag(int(beste['runde'])) or {}
        if (beste.get('haar_fassung') or ((eintrag.get('befund') or {}).get('haarabgleich') or {}).get('fassung')) \
                == fassung:
            return
        alt = (((eintrag.get('note') or {}).get('teilnoten') or {}).get('haar') or 0.0)
        logger.info('2D3D Kleider %s: Haarabgleich Fassung %s — beste Runde %s neu gezählt (%.4f → %.4f)',
                    self.job.kennung, fassung, beste['runde'], float(beste['gesamt']),
                    float(beste['gesamt']) - float(alt) + teilnoten['haar'])
        beste.update(gesamt=round(float(beste['gesamt']) - float(alt) + teilnoten['haar'], 4), haar_fassung=fassung)
        if eintrag:                                 # dasselbe Modell: die Haarregeln lesen den Befund der besten Runde
            eintrag.setdefault('befund', {})['haarabgleich'] = befund['haarabgleich']

    def fortschreiben(self, z, beg, modell, runde, note, rezept, naechste, fehler, befund):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        from iterationen2d3d.gesamtnote import Gesamtnote
        from iterationen2d3d.iterationmodell import IterationModell
        from iterationen2d3d.rundenauswahl import Rundenauswahl
        teilnoten = Gesamtnote.berechnen(note, befund)
        note.update(gesamt=teilnoten['gesamt'], teilnoten=teilnoten)
        auswahl = Rundenauswahl(z.get('auswahl'))
        if naechste.get('messrunde'):   # neue Auflösungsstufe: die Noten und Sperren der alten gelten nicht mehr
            auswahl.beste, auswahl.probe, auswahl.gesperrt = None, None, {}      # (`Aufloesungsstufe`, 02.10.2026)
        elif self._ansichten_gewechselt(auswahl, runde):       # anderer Satz Ansichten: dasselbe, diese Runde ist die Messung
            logger.info('2D3D Kleider %s: Runde %d zählt andere Ansichten als die beste (Runde %s) — neue Messung', self.job.kennung,
                        runde, auswahl.beste['runde'])
            auswahl.beste, auswahl.probe, auswahl.gesperrt = None, None, {}
        self._gesicht_nachziehen(auswahl, teilnoten, befund)
        self._haar_nachziehen(auswahl, teilnoten, befund)
        aktion, weiter = auswahl.nach_runde(runde, teilnoten['gesamt'], rezept if fehler is None else [])
        beste = auswahl.beste
        eintrag = self._eintrag(runde)
        text = self.AKTION[aktion]
        text = (text % ((auswahl.probe or {}).get('runden', 1), auswahl.PROBE_RUNDEN) if aktion == 'probe'
                else text % beste['runde'] if '%d' in text else text)
        if eintrag is not None:
            eintrag['auswahl'] = {'aktion': aktion, 'beste': beste['runde'], 'gesamt': teilnoten['gesamt']}
            vorn = (eintrag.get('notiz') + ' · ') if eintrag.get('notiz') else ''
            eintrag['notiz'] = '%sGesamtnote %.4f · %s' % (vorn, teilnoten['gesamt'], text)
        hoechstens = self.r.VERLAUF_HOECHSTENS
        verlauf = list(z.get('verlauf') or []) + [[runde, note['abweichung'], note['abweichung']]]
        befunde = list(z.get('verlauf_befunde') or []) + [IterationModell.verlaufseintrag(runde, modell, befund, note)]
        z.update(verlauf=verlauf[-hoechstens:], verlauf_befunde=befunde[-hoechstens:], modus=self.r.o.get('modus'),
                 letzte_runde=runde, letzte_note=note, auswahl=auswahl.zustand, runde_bester=beste['runde'])
        stand = self._eintrag(beste['runde']) or eintrag
        z.update(modell=stand['werte'], note=stand['note'],
                 befund=dict(stand.get('befund') or {}, runde=stand['runde'], note=stand['note']))
        if weiter['runde'] != beste['runde']:
            fort = self._eintrag(weiter['runde'])
            z['weiter'] = {'runde': fort['runde'], 'modell': fort['werte'],
                           'befund': dict(fort.get('befund') or {}, runde=fort['runde'], note=fort['note'])}
        else:
            z.pop('weiter', None)
        z['glb'] = self.r.GLB
        quelle = self.ablage.iterationen('runde_%03d_modell.glb' % beste['runde'])
        if quelle.is_file():
            shutil.copyfile(quelle, self.ablage.ergebnis(self.r.GLB))
        alle = list(beg.get('rezept') or [])
        if rezept and fehler is None:
            alle.append({'runde': runde, 'aufrufe': rezept, 'kommentar': naechste.get('kommentar') or ''})
        beg.update(zustand='wartet', runde=runde, rezept=alle, fehler=fehler)
        self.job.ergebnis['kreislauf'] = z
        self.job.ergebnis['begutachtung'] = beg
        self.lauf.sichern('ergebnis')
        logger.info('2D3D Kleider %s: Runde %d Gesamtnote %.4f — %s', self.job.kennung, runde, teilnoten['gesamt'],
                    text)
        if weiter['runde'] == runde:
            return modell
        return ModellMitKleidern.aus((self._eintrag(weiter['runde']) or {}).get('werte'))
