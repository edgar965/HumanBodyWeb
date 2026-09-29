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
       (Weg B: auch Teile an/aus). Übernommen wird der beste Optimierer-Kandidat, wenn er besser ist;
       der Vorschlag der Prüf-KI, wenn er um höchstens `toleranz` % schlechter ist (er hat Vorrang)
    4. Halt nach `runden`, nach `stillstand` Runden ohne Besserung oder auf „Anhalten"
    5. Das beste Kostüm als `ergebnis/kostuem.glb` und `kostuem.blend` (mit Körper)

Jeder Lauf setzt beim Besten an — beliebig oft „Weiter iterieren" verliert nie etwas. Zustand in
`ergebnis['kostuem']`: `parameter`, `note`, `runde_bester`, `schritt`, `ohne_besserung`, `verlauf`
([runde, beste Abweichung, beste der Runde]).

Zwei Befunde des ersten echten Laufs (29.09.2026) stecken in dieser Fassung: Eine automatische Messung der
Blickwinkel (Umriss-Note im ±40°-Fenster) schob klare Seitenansichten jedesmal an den Rand des Fensters (−90°
→ −50°, 90° → 130°) — die Note bevorzugt breitere Umrisse, sie findet den Winkel nicht; die Winkel kommen
seither aus Name, Rolle oder von Hand (`Kostuemreferenz`). Und der Optimierer schaltete den Hut AB (−14 %),
weil die Normierung auf die Figurhöhe eine zu hohe Hutspitze bestraft — Teile schaltet seither nur die
Prüf-KI, der Optimierer muss den Hut niedriger machen.
"""

import logging

from .blendermodellgrundfigur import Blendermodellgrundfigur
from .kostuemkritik import Kostuemkritik
from .kostuemoptimierer import Kostuemoptimierer
from .kostuemoptionen import Kostuemoptionen
from .kostuemparameter import Kostuemparameter
from .kostuemreferenz import Kostuemreferenz
from .kostuemrunde import Kostuemrunde

logger = logging.getLogger('core')

__all__ = ['Kostuemkreislauf']


class Kostuemkreislauf:
    GLB, BLEND = 'kostuem.glb', 'kostuem.blend'
    KRITIK_NACH_STILLSTAND = 3
    VERLAUF_HOECHSTENS = 5000

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.o = Kostuemoptionen.pruefen((self.job.optionen or {}).get('kostuem'))

    def _letzte_runde(self):
        return max([int(r.get('runde') or 0) for r in self.job.ergebnis.get('iterationen') or []] or [0])

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
        return koerper, z, Kostuemrunde(self.lauf, koerper, referenzen)

    def ausfuehren(self):
        _, z, runde_ = self._vorbereiten()
        werte = Kostuemparameter.pruefen(z.get('parameter'))
        runde = self._letzte_runde() + 1
        self.lauf.melden(0.03, 'Ausgangslage benoten')
        erg = runde_.bewerten(runde, [('ausgang', werte)])[0]
        tafel = runde_.ablegen(
            runde,
            'ausgang',
            erg,
            'Ausgangslage dieses Laufs: bestes bisheriges Kostüm auf der '
            'Grundfigur, gegen %d Vorlagenbilder' % len(runde_.referenzen),
        )
        runde_.aufraeumen(runde)
        bester, note = werte, erg['note']
        z.update(parameter=bester, note=note, runde_bester=runde, vorn_grad=erg['vorn_grad'])
        verlauf = list(z.get('verlauf') or []) + [[runde, note['abweichung'], note['abweichung']]]
        optimierer = Kostuemoptimierer(self.job.kennung, z.get('schritt'))
        ohne, seit_kritik = 0, 0
        for i in range(int(self.o['runden'])):
            if self.lauf.angehalten():
                raise self.lauf.Angehalten()
            runde += 1
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
            kritik = None
            if self._kritik_faellig(i, ohne, seit_kritik):
                self.lauf.melden(
                    anteil, '%s · Prüf-KI %s sieht sich die Tafel an' % (text, self.o['pruefki'])
                )
                kritik, vorschlag = self._kritik(bester, tafel)
                seit_kritik = 0
                if vorschlag is not None:
                    kandidaten.append(('ki', vorschlag))
            else:
                seit_kritik += 1
            ergebnisse = runde_.bewerten(
                runde, kandidaten, lambda t, s=text, a=anteil: self.lauf.melden(a, '%s · %s' % (s, t))
            )
            wahl, art = self._auswaehlen(ergebnisse, note['abweichung'])
            opt_bester = min(e['note']['abweichung'] for e in ergebnisse if e['name'] != 'ki')
            if wahl is not None:
                notiz = self._notiz(art, note, wahl, kritik)
                t = runde_.ablegen(
                    runde, art, wahl, notiz, Kostuemparameter.unterschiede(bester, wahl['werte']), kritik
                )
                bester, note, tafel, ohne = wahl['werte'], wahl['note'], t, 0
                z.update(parameter=bester, note=note, runde_bester=runde)
            else:
                ohne += 1
                ki = next((e for e in ergebnisse if e['name'] == 'ki'), None)
                if ki is not None:
                    runde_.ablegen(
                        runde,
                        'ki_verworfen',
                        ki,
                        self._notiz('ki_verworfen', note, ki, kritik),
                        Kostuemparameter.unterschiede(bester, ki['werte']),
                        kritik,
                        uebernommen=False,
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
        self._abschluss(runde_, bester, z)

    # ------------------------------------------------------------ Teile

    def _kritik_faellig(self, i, ohne, seit_kritik):
        if self.o['pruefki'] == Kostuemoptionen.AUS:
            return False
        alle = int(self.o['pruefki_alle'])
        return (i + 1) % alle == 0 or (
            ohne >= self.KRITIK_NACH_STILLSTAND and seit_kritik >= self.KRITIK_NACH_STILLSTAND
        )

    def _kritik(self, bester, tafel):
        """→ (kritik-Bericht, Wertesatz oder None). Ein Fehler der KI hält den Lauf nicht an — er steht im
        Bericht."""
        try:
            vorschlag, bericht = Kostuemkritik(self.o['pruefki']).vorschlagen(bester, tafel)
        except Exception as fehler:  # noqa: BLE001 — Ollama weg, Modell fehlt, kaputtes JSON: Runde ohne KI
            logger.warning('BlenderModel %s: Prüf-KI %s: %s', self.job.kennung, self.o['pruefki'], fehler)
            return {'modell': self.o['pruefki'], 'fehler': str(fehler)[:500]}, None
        if not bericht['aenderungen']:
            return dict(bericht, fehler='Kein verwertbarer Vorschlag'), None
        return bericht, vorschlag

    def _auswaehlen(self, ergebnisse, jetzt):
        ki = next((e for e in ergebnisse if e['name'] == 'ki'), None)
        if ki is not None and ki['note']['abweichung'] <= jetzt * (1 + self.o['toleranz'] / 100.0):
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

    def _abschluss(self, runde_, bester, z):
        """Das beste Kostüm einmal mit .blend (Körper + Kostüm) bauen und nach `ergebnis/` legen."""
        import shutil

        self.lauf.melden(0.97, 'Bestes Kostüm als GLB und .blend ablegen')
        aus = runde_.ordner(999999)
        bericht = runde_.blender.rendern(runde_.koerper, aus, [('bester', bester)], [0], glb=True, blend=True)
        eintrag = bericht['kandidaten']['bester']
        for quelle, ziel in ((eintrag.get('glb'), self.GLB), (eintrag.get('blend'), self.BLEND)):
            if quelle and (aus / 'bester' / quelle).is_file():
                shutil.copyfile(aus / 'bester' / quelle, self.ablage.ergebnis(ziel))
        z.update(glb=self.GLB, blend=self.BLEND, teile=eintrag.get('teile') or {})
        self._sichern(z)
        shutil.rmtree(aus, ignore_errors=True)
        self.lauf.melden(
            1.0, 'Kostüm: Abweichung %.4f (Runde %d)' % (z['note']['abweichung'], z['runde_bester'])
        )
