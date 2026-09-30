# -*- coding: utf-8 -*-
"""Iterationskreislauf — Schritt „iterationen" von „Haar Engine": das Modell per Knopfdruck Runde um Runde
verbessern (30.09.2026).

Kopie von `Kostuemkreislauf` (BlenderModel): ein Code, der per Knopfdruck durch alle Iterationen läuft;
beliebig oft „Weiter iterieren". Gebaut und gerendert wird von der Genesis Haar Engine
(`Genesishaarengine`) statt von Blender.

Ablauf eines Laufs (Optionen `iterationen`, `Iterationsoptionen`):
    1. Vorlagen aus der Bildauswahl samt Blickwinkel (`Iterationsreferenz`)
    2. Ausgangslage: den BESTEN bisherigen Wertesatz neu benoten — Grundfigur, Fotos oder Gewichte können sich seit dem letzten Lauf
       geändert haben, eine gemerkte Note gehörte dann zu einem anderen Vergleich
    3. `runden` Runden: Kandidaten des Optimierers (Weg A: nur Maße, Farben); alle `pruefki_alle` Runden und nach `pruefki_stillstand`
       Runden ohne Besserung zusätzlich ein Vorschlag der Prüf-KI (Weg B: auch Teile an/aus). Wer gewinnt: `Iterationswahl`. Der
       Arbeitsstand kann kurz schlechter sein als das Beste — gemerkt, gezeigt, als GLB abgelegt und beim nächsten Lauf fortgesetzt
       wird immer das Beste (`top`)
    4. Halt nach `runden`, nach `stillstand` Runden ohne Besserung DES BESTEN oder auf „Anhalten"
    5. Das beste Modell als `ergebnis/haar.glb`

Zu Beginn jeder Runde arbeitet der Lauf die Löschwünsche der Tabelle „Iterationen" ab (`Iterationsloeschung`).

Jeder Lauf setzt beim Besten an — beliebig oft „Weiter iterieren" verliert nie etwas. Zustand in
`ergebnis['kreislauf']`: `parameter`, `note`, `runde_bester` (das Beste), `schritt`, `ohne_besserung`,
`verlauf` ([runde, beste Abweichung, beste der Runde]).
"""

import logging
import shutil
import time

from .haarenginegrundfigur import Haarenginegrundfigur
from .haarparameter import Haarparameter
from .iterationskritik import Iterationskritik
from .iterationsloeschung import Iterationsloeschung
from .iterationsoptimierer import Iterationsoptimierer
from .iterationsoptionen import Iterationsoptionen
from .iterationsreferenz import Iterationsreferenz
from .iterationsrunde import Iterationsrunde
from .iterationswahl import Iterationswahl

logger = logging.getLogger('core')

__all__ = ['Iterationskreislauf']


class Iterationskreislauf:
    GLB = 'haar.glb'
    VERLAUF_HOECHSTENS = 5000

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.o = Iterationsoptionen.pruefen((self.job.optionen or {}).get('iterationen'))
        self.regeln = Iterationswahl(self.o)

    def _letzte_runde(self):
        """Die höchste Rundennummer, die je vergeben wurde — auch die gelöschter Runden (Tabelle
        „Iterationen"): Sonst bekäme eine neue Runde die Nummer und die Dateinamen einer gelöschten, und die
        Kurve hätte zwei Punkte für dieselbe Runde."""
        ergebnis = self.job.ergebnis
        eintraege = [int(r.get('runde') or 0) for r in ergebnis.get('iterationen') or []]
        verlauf = [int(p[0]) for p in (ergebnis.get('kreislauf') or {}).get('verlauf') or [] if p]
        return max(eintraege + verlauf + [0])

    def _loeschungen(self):
        """Löschwünsche der Seite abarbeiten (`Iterationsloeschung`) — nur der Lauf schreibt `ergebnis`."""
        if Iterationsloeschung(self.job).abarbeiten():
            self.lauf.sichern('ergebnis')

    def _vorbereiten(self):
        koerper = self.ablage.arbeit(Haarenginegrundfigur.DATEI)
        if not koerper.is_file():
            raise RuntimeError('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
        z = dict(self.job.ergebnis.get('kreislauf') or {})
        referenzen, ausgelassen = Iterationsreferenz.laden(self.job)
        if not referenzen:
            raise RuntimeError(
                'Keine Vorlage mit Blickwinkel in der Bildauswahl (Rolle vorne/links/rechts/hinten '
                'oder Schnittbild „ansicht_R_S" des Ansichtenbogens)'
            )
        z['ausgelassen'] = ausgelassen
        z['winkel'] = {r.original: r.winkel for r in referenzen}
        return z, Iterationsrunde(self.lauf, koerper, referenzen, parallel=int(self.o['parallel']))

    def ausfuehren(self):
        # Modus „Begutachtung" (30.09.2026, „2D3D Kleider"): eine Runde je Rezept, dann wartet der Auftrag
        # (`Begutachtungsrunde`) — die Schleife unten ist der Modus „automatisch".
        if self.o.get('modus') == Iterationsoptionen.BEGUTACHTUNG:
            from .begutachtungsrunde import Begutachtungsrunde
            Begutachtungsrunde(self.lauf).ausfuehren()
            return
        z, runde_ = self._vorbereiten()
        try:
            self._runden(z, runde_)
        finally:
            runde_.schliessen()  # die Prozesse der Engine — auch nach einem Fehler oder „Anhalten"

    def _runden(self, z, runde_):
        self._loeschungen()
        neu = z.get('modellversion') != Haarparameter.VERSION
        if neu:
            # Ein neues Haarmodell (`Haarparameter.VERSION`): Die Werte des alten passen nicht mehr zu seinen Formen —
            # Start mit den Startwerten des neuen.
            z.update(
                parameter=Haarparameter.start(),
                modellversion=Haarparameter.VERSION,
                schritt=None,
                ohne_besserung=0,
            )
        werte = Haarparameter.pruefen(z.get('parameter'))
        runde = self._letzte_runde() + 1
        self.lauf.melden(0.03, 'Ausgangslage benoten')
        start = time.perf_counter()
        erg = runde_.bewerten(runde, [('ausgang', werte)])[0]
        tafel = runde_.ablegen(
            runde,
            'ausgang',
            erg,
            (
                'Modell Version %d: Startwerte' % Haarparameter.VERSION
                if neu
                else 'Ausgangslage dieses Laufs: bestes bisheriges Modell'
            )
            + ' auf der Grundfigur, gegen %d Vorlagenbilder' % len(runde_.referenzen),
            start=start,
            mit_modell=runde_.modell_faellig(),
        )
        runde_.aufraeumen(runde)
        # `bester` ist der ARBEITSSTAND (eine Übernahme der Prüf-KI darf bis zur Toleranz schlechter sein); `top` das beste Modell
        # ALLER Runden — es steht als „bestes" im Zustand, ist der Start des nächsten Laufs und wird am Ende als GLB abgelegt.
        bester, note, arbeit_runde = werte, erg['note'], runde
        top = {'werte': bester, 'note': note, 'runde': runde}
        z.update(parameter=bester, note=note, runde_bester=runde, vorn_grad=erg['vorn_grad'])
        verlauf = list(z.get('verlauf') or []) + [[runde, note['abweichung'], note['abweichung']]]
        optimierer = Iterationsoptimierer(self.job.kennung, z.get('schritt'))
        ohne, seit_kritik = 0, 0
        mix = None
        for i in range(int(self.o['runden'])):
            if self.lauf.angehalten():
                raise self.lauf.Angehalten()
            self._loeschungen()
            runde += 1
            start = time.perf_counter()
            text = 'Runde %d (%d von %d) · Abweichung %.3f' % (
                runde,
                i + 1,
                self.o['runden'],
                note['abweichung'],
            )
            anteil = 0.05 + 0.9 * i / self.o['runden']
            self.lauf.melden(anteil, text)
            kandidaten = [
                ('k%d' % j, p)
                for j, p in enumerate(optimierer.kandidaten(bester, int(self.o['kandidaten']), runde))
            ]
            if (
                mix is not None
            ):  # die Änderungen der Runde davor, die nicht gewonnen haben (`Iterationswahl.mischen`)
                kandidaten.append(('mix', mix))
                mix = None
            kritik = None
            if self.regeln.kritik_faellig(i, ohne, seit_kritik):
                self.lauf.melden(
                    anteil, '%s · Prüf-KI %s sieht sich die Tafel an' % (text, self.o['pruefki'])
                )
                kritik, vorschlag = self._kritik(bester, runde_.kritiktafel(arbeit_runde) or tafel)
                seit_kritik = 0
                if vorschlag is not None:
                    kandidaten.append(('ki', vorschlag))
            else:
                seit_kritik += 1
            ergebnisse = runde_.bewerten(
                runde, kandidaten, lambda t, s=text, a=anteil: self.lauf.melden(a, '%s · %s' % (s, t))
            )
            wahl, art = self.regeln.auswaehlen(ergebnisse, note['abweichung'], top['note']['abweichung'])
            if art == 'optimierer':
                mix = self.regeln.mischen(bester, wahl, ergebnisse, note['abweichung'])
            opt_bester = min(e['note']['abweichung'] for e in ergebnisse if e['name'] != 'ki')
            ki = next((e for e in ergebnisse if e['name'] == 'ki'), None)
            if ki is not None and kritik is not None:
                # Was aus dem Vorschlag der Prüf-KI wurde — die Tabelle „Iterationen" zeigt es in der Runde.
                kritik['vorschlag'] = {
                    'abweichung': round(ki['note']['abweichung'], 4),
                    'vorher': round(note['abweichung'], 4),
                    'uebernommen': art == 'ki',
                }
            if wahl is not None:
                t = runde_.ablegen(
                    runde,
                    art,
                    wahl,
                    self.regeln.notiz(art, note, wahl, kritik),
                    Haarparameter.unterschiede(bester, wahl['werte']),
                    kritik,
                    start=start,
                    mit_modell=runde_.modell_faellig(),
                )
                bester, note, tafel, arbeit_runde = wahl['werte'], wahl['note'], t, runde
                if note['abweichung'] < top['note']['abweichung']:
                    top = {'werte': bester, 'note': note, 'runde': runde}
                    ohne = 0
                else:
                    ohne += 1
                z.update(parameter=top['werte'], note=top['note'], runde_bester=top['runde'])
            else:
                ohne += 1
                if ki is not None:
                    runde_.ablegen(
                        runde,
                        'ki_verworfen',
                        ki,
                        self.regeln.notiz('ki_verworfen', note, ki, kritik),
                        Haarparameter.unterschiede(bester, ki['werte']),
                        kritik,
                        uebernommen=False,
                        start=start,
                        mit_modell=False,
                    )
            optimierer.anpassen(art == 'optimierer')
            verlauf.append([runde, note['abweichung'], round(opt_bester, 4)])
            z.update(
                schritt=optimierer.schritt,
                ohne_besserung=ohne,
                verlauf=verlauf[-self.VERLAUF_HOECHSTENS :],
                sekunden_je_runde=ergebnisse[0].get('sekunden'),
            )
            self._sichern(z)
            runde_.aufraeumen(runde)
            if self.o['stillstand'] and ohne >= self.o['stillstand']:
                logger.info('Haar Engine %s: %d Runden ohne Besserung — Halt', self.job.kennung, ohne)
                break
        self._abschluss(runde_, top['werte'], z)

    # ------------------------------------------------------------ Teile

    def _kritik(self, bester, tafel):
        """→ (kritik-Bericht, Wertesatz oder None). Ein Fehler der KI hält den Lauf nicht an — er steht im Bericht."""
        try:
            vorschlag, bericht = Iterationskritik(self.o['pruefki']).vorschlagen(bester, tafel)
        except Exception as fehler:  # noqa: BLE001 — Ollama weg, Modell fehlt, kaputtes JSON: Runde ohne KI
            logger.warning('Haar Engine %s: Prüf-KI %s: %s', self.job.kennung, self.o['pruefki'], fehler)
            return {'modell': self.o['pruefki'], 'fehler': str(fehler)[:500]}, None
        if not bericht['aenderungen']:
            return dict(bericht, fehler='Kein verwertbarer Vorschlag'), None
        return bericht, vorschlag

    def _sichern(self, z):
        self.job.ergebnis['kreislauf'] = z
        self.lauf.sichern('ergebnis')

    def _abschluss(self, runde_, bester, z):
        """Das beste Modell einmal bauen (Figur + Haar + Rig in der RUHELAGE — dieselbe wie `figur.glb`,
        darauf laufen Film und Bühne) und nach `ergebnis/` legen."""
        self.lauf.melden(0.97, 'Bestes Modell als GLB ablegen')
        aus = runde_.ordner(999999)
        bericht = runde_.engine.rendern(
            runde_.koerper, aus, [('bester', bester)], [0], glb=True, haltung=False
        )
        eintrag = bericht['kandidaten']['bester']
        quelle = aus / 'bester' / eintrag['glb'] if eintrag.get('glb') else None
        if quelle is not None and quelle.is_file():
            shutil.copyfile(quelle, self.ablage.ergebnis(self.GLB))
            z.update(glb=self.GLB)
        z.update(teile=eintrag.get('teile') or {})
        self._sichern(z)
        shutil.rmtree(aus, ignore_errors=True)
        self.lauf.melden(
            1.0, 'Haar: Abweichung %.4f (Runde %d)' % (z['note']['abweichung'], z['runde_bester'])
        )
