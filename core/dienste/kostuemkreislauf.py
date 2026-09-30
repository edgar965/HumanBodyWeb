# -*- coding: utf-8 -*-
"""Kostuemkreislauf — Schritt „kostuem" von BlenderModel: das Kostüm per Knopfdruck Runde um Runde verbessern.

Edgar (29.09.2026): „für das Verfahren brauche ich einen Code der dann später per Knopfdruck durch alle
Iterationen bis zum fertigen Ergebnis läuft. Ich kann beliebig Iterationen weiter laufen lassen, um das Mesh
und Modell zu verbessern" — Vorschlag A + B angenommen („a und b"), Prüf-KI lokal statt über eine Cloud-API.

Ablauf eines Laufs (Optionen `kostuem`, `Kostuemoptionen`):
    1. Vorlagen aus der Bildauswahl samt Blickwinkel (`Kostuemreferenz`)
    2. Ausgangslage: den BESTEN bisherigen Wertesatz neu benoten — Grundfigur, Fotos oder Gewichte
       können sich seit dem letzten Lauf geändert haben, eine gemerkte Note gehörte dann zu einem anderen
       Vergleich
    3. `runden` Runden: Kandidaten des Optimierers (Weg A: nur Maße, Farben, Haltung); alle
       `pruefki_alle` Runden und nach drei Runden ohne Besserung zusätzlich ein Vorschlag der Prüf-KI
       (Weg B: auch Teile an/aus). Übernommen wird der beste Optimierer-Kandidat, wenn er besser ist als der
       Arbeitsstand; der Vorschlag der Prüf-KI, wenn er um höchstens `toleranz` % schlechter ist als das BESTE
       Modell aller Runden (er hat Vorrang). Der Arbeitsstand kann damit kurz schlechter sein als das Beste —
       gemerkt, gezeigt, als GLB abgelegt und beim nächsten Lauf fortgesetzt wird immer das Beste (`top`)
    4. Halt nach `runden`, nach `stillstand` Runden ohne Besserung DES BESTEN oder auf „Anhalten"
    5. Das beste Kostüm als `ergebnis/kostuem.glb` und `kostuem.blend` (mit Körper)

Zu Beginn jeder Runde arbeitet der Lauf die Löschwünsche der Tabelle „Iterationen" ab (`Kostuemloeschung`).

Jeder Lauf setzt beim Besten an — beliebig oft „Weiter iterieren" verliert nie etwas. Zustand in
`ergebnis['kostuem']`: `parameter`, `note`, `runde_bester` (das Beste), `schritt`, `ohne_besserung`, `verlauf`
([runde, beste Abweichung, beste der Runde]).

Zwei Befunde des ersten echten Laufs (29.09.2026) stecken in dieser Fassung: Eine automatische Messung der
Blickwinkel (Umriss-Note im ±40°-Fenster) schob klare Seitenansichten jedesmal an den Rand des Fensters (−90°
→ −50°, 90° → 130°) — die Note bevorzugt breitere Umrisse, sie findet den Winkel nicht; die Winkel kommen
seither aus Name, Rolle oder von Hand (`Kostuemreferenz`). Und der Optimierer schaltete den Hut AB (−14 %),
weil die Normierung auf die Figurhöhe eine zu hohe Hutspitze bestraft — Teile schaltet seither nur die
Prüf-KI, der Optimierer muss den Hut niedriger machen.
"""

import logging
import time

from .blendermodellgrundfigur import Blendermodellgrundfigur
from .kostuemabschluss import Kostuemabschluss
from .kostuemkritik import Kostuemkritik
from .kostuemloeschung import Kostuemloeschung
from .kostuemoptimierer import Kostuemoptimierer
from .kostuemoptionen import Kostuemoptionen
from .kostuemparameter import Kostuemparameter
from .kostuemreferenz import Kostuemreferenz
from .kostuemrunde import Kostuemrunde

logger = logging.getLogger('core')

__all__ = ['Kostuemkreislauf']


class Kostuemkreislauf:
    VERLAUF_HOECHSTENS = 5000

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.o = Kostuemoptionen.pruefen((self.job.optionen or {}).get('kostuem'))

    def _letzte_runde(self):
        """Die höchste Rundennummer, die je vergeben wurde — auch die gelöschter Runden (Tabelle
        „Iterationen"): Sonst bekäme eine neue Runde die Nummer und die Dateinamen einer gelöschten, und die
        Kurve hätte zwei Punkte für dieselbe Runde."""
        ergebnis = self.job.ergebnis
        eintraege = [int(r.get('runde') or 0) for r in ergebnis.get('iterationen') or []]
        verlauf = [int(p[0]) for p in (ergebnis.get('kostuem') or {}).get('verlauf') or [] if p]
        return max(eintraege + verlauf + [0])

    def _loeschungen(self):
        """Löschwünsche der Seite abarbeiten (`Kostuemloeschung`) — nur der Lauf schreibt `ergebnis`."""
        if Kostuemloeschung(self.job).abarbeiten():
            self.lauf.sichern('ergebnis')

    def _vorbereiten(self):
        koerper = self.ablage.arbeit(Blendermodellgrundfigur.DATEI)
        if not koerper.is_file():
            raise RuntimeError('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
        z = dict(self.job.ergebnis.get('kostuem') or {})
        referenzen, ausgelassen = Kostuemreferenz.laden(self.job)
        if not referenzen:
            raise RuntimeError(
                'Keine Vorlage mit Blickwinkel in der Bildauswahl (Rolle vorne/links/rechts/hinten '
                'oder Schnittbild „ansicht_R_S" des Ansichtenbogens)'
            )
        z['ausgelassen'] = ausgelassen
        z['winkel'] = {r.original: r.winkel for r in referenzen}
        return (
            koerper,
            z,
            Kostuemrunde(
                self.lauf,
                koerper,
                referenzen,
                parallel=int(self.o['parallel']),
                textur=self.o['textur'] == 'an',
                huelle=self.o['huelle'] == 'an',
                sicht=self.o['sichtmodell'] == 'an',
            ),
        )

    def ausfuehren(self):
        _, z, runde_ = self._vorbereiten()
        try:
            self._runden(z, runde_)
        finally:
            runde_.schliessen()  # die dauerhaften Blender-Arbeiter — auch nach einem Fehler oder „Anhalten"

    def _runden(self, z, runde_):
        self._loeschungen()
        neu = z.get('modellversion') != Kostuemparameter.VERSION
        if neu:
            # Ein neues Kostümmodell (`Kostuemparameter.VERSION`): Die Werte des alten passen nicht mehr zu
            # seinen Formen — Start mit den Startwerten des neuen.
            z.update(
                parameter=Kostuemparameter.start(),
                modellversion=Kostuemparameter.VERSION,
                schritt=None,
                ohne_besserung=0,
            )
        werte = Kostuemparameter.pruefen(z.get('parameter'))
        runde = self._letzte_runde() + 1
        self.lauf.melden(0.03, 'Ausgangslage benoten')
        start = time.perf_counter()
        erg = runde_.bewerten(runde, [('ausgang', werte)], basis=werte)[0]
        tafel = runde_.ablegen(
            runde,
            'ausgang',
            erg,
            (
                'Kostümmodell Version %d: Startwerte' % Kostuemparameter.VERSION
                if neu
                else 'Ausgangslage dieses Laufs: bestes bisheriges Modell'
            )
            + ' auf der Grundfigur, gegen %d Vorlagenbilder' % len(runde_.referenzen),
            start=start,
            mit_modell=runde_.modell_faellig(),
        )
        runde_.aufraeumen(runde)
        # `bester` ist der ARBEITSSTAND (eine Übernahme der Prüf-KI darf bis zur Toleranz schlechter sein);
        # `top` das beste Modell ALLER Runden — es steht als „bestes" im Zustand, ist der Start des nächsten
        # Laufs und wird am Ende als GLB abgelegt.
        bester, note, arbeit_runde = werte, erg['note'], runde
        top = {'werte': bester, 'note': note, 'runde': runde}
        z.update(parameter=bester, note=note, runde_bester=runde, vorn_grad=erg['vorn_grad'])
        verlauf = list(z.get('verlauf') or []) + [[runde, note['abweichung'], note['abweichung']]]
        optimierer = Kostuemoptimierer(self.job.kennung, z.get('schritt'))
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
            if mix is not None:  # die Änderungen der Runde davor, die nicht gewonnen haben (`_mischen`)
                kandidaten.append(('mix', mix))
                mix = None
            kritik = None
            if self._kritik_faellig(i, ohne, seit_kritik):
                self.lauf.melden(
                    anteil, '%s · Prüf-KI %s sieht sich die Tafel an' % (text, self.o['pruefki'])
                )
                kritik, vorschlag = self._kritik(
                    bester, runde_.kritiktafel(arbeit_runde) or tafel, runde_.detailtafel(arbeit_runde)
                )
                seit_kritik = 0
                if vorschlag is not None:
                    kandidaten.append(('ki', vorschlag))
            else:
                seit_kritik += 1
            ergebnisse = runde_.bewerten(
                runde,
                kandidaten,
                lambda t, s=text, a=anteil: self.lauf.melden(a, '%s · %s' % (s, t)),
                basis=bester,
            )
            wahl, art = self._auswaehlen(ergebnisse, note['abweichung'], top['note']['abweichung'])
            if art == 'optimierer':
                mix = self._mischen(bester, wahl, ergebnisse, note['abweichung'])
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
                notiz = self._notiz(art, note, wahl, kritik)
                t = runde_.ablegen(
                    runde,
                    art,
                    wahl,
                    notiz,
                    Kostuemparameter.unterschiede(bester, wahl['werte']),
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
                        self._notiz('ki_verworfen', note, ki, kritik),
                        Kostuemparameter.unterschiede(bester, ki['werte']),
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
                logger.info('BlenderModel %s: Kostüm %d Runden ohne Besserung — Halt', self.job.kennung, ohne)
                break
        Kostuemabschluss(self.lauf).ausfuehren(runde_, top['werte'], z)

    # ------------------------------------------------------------ Teile

    MISCHEN_HOECHSTENS = 3

    @classmethod
    def _mischen(cls, alt, wahl, ergebnisse, jetzt):
        """Bessern sich mehrere Kandidaten einer Runde, geht nur der beste in den neuen Stand — die Änderungen der
        anderen (an anderen Maßen) gingen verloren, obwohl sie einzeln etwas brachten. Sie werden dem neuen Stand
        aufgesetzt und als weiterer Kandidat (`mix`) in die nächste Runde gegeben. → Wertesatz oder None."""
        besser = sorted(
            (
                e
                for e in ergebnisse
                if e is not wahl and e['name'] != 'ki' and e['note']['abweichung'] < jetzt
            ),
            key=lambda e: e['note']['abweichung'],
        )
        if not besser:
            return None
        mix = dict(wahl['werte'])
        for e in besser[: cls.MISCHEN_HOECHSTENS]:
            for k, v in e['werte'].items():
                if v != alt.get(k):
                    mix[k] = v
        mix = Kostuemparameter.pruefen(mix)
        return None if mix == wahl['werte'] else mix

    def _kritik_faellig(self, i, ohne, seit_kritik):
        if self.o['pruefki'] == Kostuemoptionen.AUS:
            return False
        alle = int(self.o['pruefki_alle'])
        flaute = int(self.o['pruefki_stillstand'])
        return (i + 1) % alle == 0 or (ohne >= flaute and seit_kritik >= flaute)

    def _kritik(self, bester, tafel, detail=None):
        """→ (kritik-Bericht, Wertesatz oder None). Ein Fehler der KI hält den Lauf nicht an — er steht im
        Bericht."""
        try:
            vorschlag, bericht = Kostuemkritik(self.o['pruefki']).vorschlagen(bester, tafel, detail)
        except Exception as fehler:  # noqa: BLE001 — Ollama weg, Modell fehlt, kaputtes JSON: Runde ohne KI
            logger.warning('BlenderModel %s: Prüf-KI %s: %s', self.job.kennung, self.o['pruefki'], fehler)
            return {'modell': self.o['pruefki'], 'fehler': str(fehler)[:500]}, None
        if not bericht['aenderungen']:
            return dict(bericht, fehler='Kein verwertbarer Vorschlag'), None
        return bericht, vorschlag

    def _auswaehlen(self, ergebnisse, jetzt, beste=None):
        """`jetzt`: Abweichung des Arbeitsstands (ein Optimierer-Kandidat muss besser sein), `beste`: die des
        besten Modells aller Runden — an ihr misst sich die Toleranz der Prüf-KI, damit der Arbeitsstand nie
        weiter als `toleranz` % vom Besten wegdriftet (ohne `beste`: an `jetzt`)."""
        ki = next((e for e in ergebnisse if e['name'] == 'ki'), None)
        massstab = jetzt if beste is None else min(jetzt, beste)
        if ki is not None and ki['note']['abweichung'] <= massstab * (1 + self.o['toleranz'] / 100.0):
            return ki, 'ki'
        opt = min((e for e in ergebnisse if e['name'] != 'ki'), key=lambda e: e['note']['abweichung'])
        if opt['note']['abweichung'] < jetzt:
            return opt, 'optimierer'
        return None, None

    def _notiz(self, art, note, erg, kritik):
        vorher, nachher = note['abweichung'], erg['note']['abweichung']
        prozent = (nachher - vorher) / vorher * 100 if vorher else 0.0
        zahlen = 'Abweichung %.4f → %.4f (%+.1f %%)' % (vorher, nachher, prozent)
        if art == 'optimierer':
            return 'Optimierer: %s' % zahlen
        grund = (kritik or {}).get('begruendung') or ''
        if art == 'ki':
            return 'Prüf-KI %s übernommen: %s. %s' % (self.o['pruefki'], zahlen, grund)
        return 'Prüf-KI %s verworfen (Toleranz %s %%): %s. %s' % (
            self.o['pruefki'],
            self.o['toleranz'],
            zahlen,
            grund,
        )

    def _sichern(self, z):
        self.job.ergebnis['kostuem'] = z
        self.lauf.sichern('ergebnis')
