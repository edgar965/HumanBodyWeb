# -*- coding: utf-8 -*-
"""Begutachtungsrunde — Runden der Iterationen von „2D3D Kleider" im Modus „Begutachtung" (30.09.2026).

Edgar: „jede iteration wird von dir begutachtet, und dann neuer Code erzeugt." Der Code ist ein Rezept
(`G9rezept`: Aufrufe an `ModellMitKleidern`), das der Prüfer (Fable) oder der Nutzer nach dem Ansehen der Bilder
schreibt (`POST …/begutachtung/`) — oder das `IterationModell` (Ordner `2d3DIterationen`) aus dem Befund der
letzten Runde selbst schreibt (`naechste.automatisch`, bis zu `naechste.runden` Runden in einem Lauf). Eine Runde:

    1. das Modell der letzten Runde (`kreislauf.modell`) — oder, in der ersten Runde, der Ausgangszustand
    2. das nächste Rezept anwenden — ein Fehler darin wird abgelegt, das Modell bleibt
    3. bauen (`Kleidermodellbau`), rendern aus den Blickwinkeln der Vorlagen (`Genesishaarrender`), benoten gegen die
       Fotos (`Iterationsnote`) und in 3D gegen das Netz (`Iterationsnetznote`), messen (`Begutachtungsbefund`)
    4. ablegen wie `Iterationsrunde.ablegen` (Tafel, Renders, GLB, Eintrag in `ergebnis['iterationen']`) — dazu
       `aufrufe`, `kommentar`, `rezept` (die wirksam gewordenen Aufrufe), `fehler`, `befund`
    5. `begutachtung.zustand = 'wartet'`: der Lauf endet mit Status „Wartet auf Begutachtung" (`Haarenginelauf`)

Das beste Modell (kleinste Gesamtabweichung) liegt als `ergebnis/modell.glb`; Export, Film und Speichern lesen das
Modell aus `kreislauf.modell`. Die Fotonote fehlt, wenn kein Foto einen Blickwinkel hat — dann zählt nur das Netz.
"""

import logging
import shutil
import time

import numpy as np
from django.utils import timezone
from Genesis9.rezeptumgebung import Rezeptumgebung

from .begutachtungsbefund import Begutachtungsbefund
from .haarenginegrundfigur import Haarenginegrundfigur
from .iterationsbild import Iterationsbild
from .iterationsnetznote import Iterationsnetznote
from .iterationsnote import Iterationsnote
from .iterationsoptionen import Iterationsoptionen
from .iterationsreferenz import Iterationsreferenz
from .iterationsrunde import Iterationsrunde
from .iterationstafel import Iterationstafel

logger = logging.getLogger('core')

__all__ = ['Begutachtungsrunde']


class Begutachtungsrunde:
    GLB = 'modell.glb'
    #: Gewicht der 3D-Note in der Gesamtabweichung (die Fotonote liegt meist bei 0,2–0,6, die Netznote ebenso).
    NETZGEWICHT = 1.0
    VERLAUF_HOECHSTENS = 5000
    RUNDEN_HOECHSTENS = 50

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.o = Iterationsoptionen.pruefen((self.job.optionen or {}).get('iterationen'))
        self._lage = (0, 1)

    def _melden(self, anteil, text):
        i, n = self._lage
        self.lauf.melden((i + anteil) / n, text)

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        if not self.ablage.arbeit(Haarenginegrundfigur.DATEI).is_file():
            raise RuntimeError('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
        z = dict(self.job.ergebnis.get('kreislauf') or {})
        beg = dict(self.job.ergebnis.get('begutachtung') or {})
        referenzen, ausgelassen = Iterationsreferenz.laden(self.job)
        z['ausgelassen'] = ausgelassen
        z['winkel'] = {r.original: r.winkel for r in referenzen}
        modell = ModellMitKleidern.aus(z['modell']) if z.get('modell') else self._start()
        naechste = beg.pop('naechste', None) or {}
        runden = 1
        if naechste.get('automatisch'):
            runden = max(1, min(self.RUNDEN_HOECHSTENS, int(naechste.get('runden') or 1)))
        for i in range(runden):
            if i and self.lauf.angehalten():
                break
            self._lage = (i, runden)
            if naechste.get('automatisch'):
                naechste = dict(naechste, aufrufe=self._automatisch(modell, z),
                                kommentar=naechste.get('kommentar') or 'automatisch (IterationModell)')
            modell = self._runde(z, beg, modell, naechste, referenzen)

    def _automatisch(self, modell, z):
        """Das Rezept der nächsten Runde aus dem Befund der letzten (`IterationModell`)."""
        from iterationen2d3d.iterationmodell import IterationModell
        kandidaten = [k.get('kennung') for k in (self.job.ergebnis.get('frisur') or {}).get('kandidaten') or []
                      if k.get('kennung')]
        return IterationModell(modell, z.get('befund'), z.get('verlauf_befunde'), kandidaten).rezept()

    def _runde(self, z, beg, modell, naechste, referenzen):
        from Genesis9.modellrezept import G9rezept

        from .genesishaarrender import Genesishaarrender
        from .kleidermodellbau import Kleidermodellbau
        start = time.perf_counter()
        runde = self._letzte_runde() + 1
        rezept, fehler = [], None
        # Der Sichtkörper der Vorlagen (Konzept 4.1) steht dem Rezept zur Verfügung (`kleid_huelle`, `koerper_huelle`)
        # — gebaut aus den Silhouetten der Note und der Höhe des Modells der LETZTEN Runde (erste Runde: Körper).
        sicht = self._sichtkoerper(referenzen, z)
        modell.umgebung = Rezeptumgebung(sichtkoerper=sicht, drapierer=self._drapierer())
        if naechste.get('aufrufe'):
            try:
                rezept = [text for _zeile, text in G9rezept.anwenden(modell, naechste['aufrufe'])]
            except ValueError as f:
                fehler = str(f)
                logger.warning('2D3D Kleider %s: Rezept der Runde %d: %s', self.job.kennung, runde, fehler)
        self._melden(0.1, 'Runde %d: Modell bauen' % runde)
        bau = Kleidermodellbau(self.job.stellung(), modell.drehung())
        teile = bau.teile(modell)
        z['modell_hoehe'] = round(float(max(float(np.asarray(t['punkte'])[:, 1].max()) for t in teile)), 4)
        breite = int(self.o.get('bildbreite') or 256)
        groesse = (breite, int(breite * 1.5))
        render = Genesishaarrender(None)
        aus = self.ablage.arbeit('runden') / ('runde_%04d' % runde)
        netznote = Iterationsnetznote.laden(self.ablage)
        messung = Begutachtungsbefund(netznote, sicht)
        je_ansicht, renders, paare = [], {}, []
        fototextur = {}
        try:
            # 1. Kennfarben je Ansicht (Teilmasken für Befund und Fotoprojektion), 2. Fotoprojektion, wenn das Rezept sie
            # will (die Schicht liegt danach neben der Bibliothek, die Teile bekommen ihre Texturen neu),
            # 3. der Render mit Texturen, der benotet wird (30.09.2026, nachts).
            for r in referenzen:
                messung.masken(render, teile, r, aus / ('kennung_%+04d.png' % int(round(r.winkel))), groesse)
            if getattr(modell, 'fotowuensche', None):
                self._melden(0.25, 'Runde %d: Fotoprojektion auf %s' % (runde, ', '.join(sorted(modell.fotowuensche))))
                fototextur = self._fototextur(modell, teile, referenzen, render, bau, aus)
            for nummer, r in enumerate(referenzen):
                self._melden(0.3 + 0.4 * nummer / max(1, len(referenzen)),
                             'Runde %d: Rendern %d von %d' % (runde, nummer + 1, len(referenzen)))
                pfad = aus / ('ansicht_%+04d.png' % int(round(r.winkel)))
                render.bild_teile([(t['punkte'], t['dreiecke'], t['farbe'], self._textur(t)) for t in teile],
                                  r.winkel, pfad, groesse=groesse)
                bild = Iterationsbild.aus_render(pfad)
                note = Iterationsnote.vergleichen(r.bild, bild)
                renders[r.datei] = bild
                je_ansicht.append({'datei': r.datei, 'original': r.original, 'winkel': r.winkel, 'bild': pfad, **note})
                paare.append((r.gewicht, note))
                messung.render_dazu(r, bild)
        finally:
            render.schliessen()
        foto = Iterationsnote.gesamt(paare) if paare else {'abweichung': 0.0, 'iou': 0.0, 'farbe': 0.0}
        netz = netznote.vergleichen(teile) if netznote is not None else None
        note = dict(foto, netz=netz, foto=foto['abweichung'] if paare else None)
        note['abweichung'] = round(float(foto['abweichung'] if paare else 0.0)
                                   + self.NETZGEWICHT * float(netz['abweichung'] if netz else 0.0), 4)
        befund = messung.befund(teile)
        if fototextur:
            befund['fototextur'] = fototextur
        self._melden(0.8, 'Runde %d: ablegen (Abweichung %.3f)' % (runde, note['abweichung']))
        erg = {'werte': modell.als_dict(), 'note': note, 'je_ansicht': je_ansicht, 'renders': renders,
               'teile': {t['sorte']: 1 for t in teile if t['art'] != 'koerper'}, 'befund': befund}
        self._ablegen(runde, erg, naechste, rezept, fehler, teile, bau, start)
        self._stand(z, beg, modell, runde, note, rezept, naechste, fehler, befund)
        shutil.rmtree(aus, ignore_errors=True)
        self._melden(1.0, 'Runde %d: Abweichung %.4f — wartet auf Begutachtung' % (runde, note['abweichung']))
        return modell

    @staticmethod
    def _textur(teil):
        """Das Texturpaket eines Teils für `Genesishaarrender.bild_teile` — None ohne Bild."""
        if teil.get('uv') is None or not teil.get('textur'):
            return None
        return {'uv': teil['uv'], 'gruppen': teil['textur']}

    def _fototextur(self, modell, teile, referenzen, render, bau, aus):
        """Die Fotoprojektion der gewünschten Stücke (`Kleidfotoprojektion`) und die Texturen der Teile danach neu."""
        from .kleidfotoprojektion import Kleidfotoprojektion
        bericht = Kleidfotoprojektion(self.ablage, render, aus).bauen(modell, teile, referenzen)
        gebaut = [k for k, b in bericht.items() if not b.get('fehler')]
        if gebaut:
            bau.textur_auffrischen(teile, modell, set(gebaut))
        return bericht

    def _drapierer(self):
        """Die Stofflöser für `kleid_drapieren` — Newton (Vorgabe) und Blender, beide im Arbeitsordner des Auftrags."""
        from .haarengineblender import Haarengineblender
        from .kleiddrapierung import Kleiddrapierung
        return {'newton': Kleiddrapierung(self.ablage.arbeit('stoff')),
                'blender': Haarengineblender(self.ablage.arbeit('blender'))}

    def _sichtkoerper(self, referenzen, z):
        """`Sichtkoerper` aus den Silhouetten der Vorlagen — je Lauf einmal je Modellhöhe (auf den cm); None ohne Fotos."""
        from iterationen2d3d.sichtkoerper import Sichtkoerper

        from .kleidermodellbau import Kleidermodellbau
        if not referenzen:
            return None
        if getattr(self, '_koerper_punkte', None) is None:
            self._koerper_punkte = np.asarray(Kleidermodellbau(self.job.stellung()).koerper()['punkte'])
        hoehe = round(float(z.get('modell_hoehe') or self._koerper_punkte[:, 1].max()), 2)
        alt = getattr(self, '_sicht', None)
        if alt is not None and alt[0] == hoehe:
            return alt[1]
        sicht = Sichtkoerper([(r.winkel, r.bild.maske) for r in referenzen], hoehe, self._koerper_punkte)
        self._sicht = (hoehe, sicht)
        return sicht

    def _start(self):
        """Der Ausgangszustand: die Frisur, die „Mesh to 3D" als beste gemessen hat (sonst die Vorgabe), keine
        Kleider."""
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.modellmitkleidern import ModellMitKleidern
        modell = ModellMitKleidern()
        kandidaten = (self.job.ergebnis.get('frisur') or {}).get('kandidaten') or []
        frisur = (kandidaten[0].get('kennung') if kandidaten else None) or G9haargenerisch.VORGABE
        modell.haar_nur(frisur)
        return modell

    def _letzte_runde(self):
        ergebnis = self.job.ergebnis
        eintraege = [int(r.get('runde') or 0) for r in ergebnis.get('iterationen') or []]
        verlauf = [int(p[0]) for p in (ergebnis.get('kreislauf') or {}).get('verlauf') or [] if p]
        return max(eintraege + verlauf + [0])

    # -------------------------------------------------------------- ablegen

    def _ablegen(self, runde, erg, naechste, rezept, fehler, teile, bau, start):
        ziel = self.ablage.iterationen()
        ziel.mkdir(parents=True, exist_ok=True)
        dateien = {}
        if erg['je_ansicht']:
            tafel = 'runde_%03d_vergleich.png' % runde
            referenzen = {r.datei: r for r in Iterationsreferenz.laden(self.job)[0]}
            Iterationstafel.bauen(
                [(a['winkel'], referenzen[a['datei']].bild, erg['renders'][a['datei']], a) for a in erg['je_ansicht']],
                ziel / tafel)
            dateien['vergleich'] = tafel
        je_ansicht = []
        for a in erg['je_ansicht']:
            bild = 'runde_%03d_%s' % (runde, a['bild'].name)
            if a['bild'].is_file():
                Iterationsrunde.zuschneiden(a['bild'], ziel / bild)
            je_ansicht.append({k: a[k] for k in ('original', 'winkel', 'iou', 'farbe')} | {'render': bild})
        dateien['modell'] = 'runde_%03d_modell.glb' % runde
        bau.glb(teile, ziel / dateien['modell'])
        netz = erg['note'].get('netz') or {}
        notiz = naechste.get('kommentar') or ('Ausgangslage: Frisur aus „Mesh to 3D", keine Kleider' if runde == 1
                                              else '')
        if netz:
            notiz = (notiz + ' · ' if notiz else '') + 'Netz: Stoff %s mm zum Netz, Deckung %.0f %%' % (
                netz.get('modell_mm'), 100.0 * float(netz.get('deckung') or 0))
        eintrag = {
            'runde': runde,
            'zeit': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            'sekunden': round(time.perf_counter() - start, 1),
            'art': 'begutachtung' if naechste else 'ausgang',
            'uebernommen': fehler is None,
            'notiz': notiz,
            'note': erg['note'],
            'je_ansicht': je_ansicht,
            'werte': erg['werte'],
            'aenderungen': {},
            'teile': erg['teile'],
            'dateien': dateien,
            'aufrufe': naechste.get('aufrufe') or '',
            'kommentar': naechste.get('kommentar') or '',
            'automatisch': bool(naechste.get('automatisch')),
            'rezept': rezept,
            'befund': erg['befund'],
        }
        if fehler:
            eintrag['fehler'] = fehler
        self.job.ergebnis.setdefault('iterationen', []).append(eintrag)

    def _stand(self, z, beg, modell, runde, note, rezept, naechste, fehler, befund):
        """`kreislauf` und `begutachtung` im Ergebnis fortschreiben; das beste Modell als `ergebnis/modell.glb`."""
        from iterationen2d3d.iterationmodell import IterationModell
        verlauf = list(z.get('verlauf') or []) + [[runde, note['abweichung'], note['abweichung']]]
        besser = z.get('note') is None or note['abweichung'] <= float((z.get('note') or {}).get('abweichung', 1e9))
        befunde = list(z.get('verlauf_befunde') or []) + [IterationModell.verlaufseintrag(runde, modell, befund, note)]
        z.update(modell=modell.als_dict(), verlauf=verlauf[-self.VERLAUF_HOECHSTENS:], modus=self.o.get('modus'),
                 letzte_runde=runde, letzte_note=note, befund=dict(befund, runde=runde, note=note),
                 verlauf_befunde=befunde[-self.VERLAUF_HOECHSTENS:])
        if besser:
            z.update(note=note, runde_bester=runde, glb=self.GLB)
            quelle = self.ablage.iterationen('runde_%03d_modell.glb' % runde)
            if quelle.is_file():
                shutil.copyfile(quelle, self.ablage.ergebnis(self.GLB))
        alle = list(beg.get('rezept') or [])
        if rezept and fehler is None:
            alle.append({'runde': runde, 'aufrufe': rezept, 'kommentar': naechste.get('kommentar') or ''})
        beg.update(zustand='wartet', runde=runde, rezept=alle, fehler=fehler)
        self.job.ergebnis['kreislauf'] = z
        self.job.ergebnis['begutachtung'] = beg
        self.lauf.sichern('ergebnis')
