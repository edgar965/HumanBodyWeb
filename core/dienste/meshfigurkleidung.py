# -*- coding: utf-8 -*-
"""Meshfigurkleidung — Schritt „kleidung" von „Mesh to 3D": die Kleidung aus dem Netz schneiden (Paket `Kleidung`).

Edgar, 29.09.2026: „Überleg dir was zu den Kleider, kannst du da auch sowas wie mit Haar Machen?" — und, als ich
nach der Erlaubnis fragte: „wegen kleider habe ich dir schon gesagt, du sollst das tun!" Das Netz trägt Shirt,
Hose und Socken als Teil EINER Fläche mit der Haut. Dieser Schritt trennt sie, und zwar mit demselben Hautmodell
der KAHLEN Stellen (`Meshfigurhautmodell`, Gesicht, Hände, Unterarme, Unterschenkel) wie die Körperkette und die
Textur — sonst hielte jeder Schritt etwas anderes für Kleidung.

Das Körpernetz ist gemeint, nicht das Kopfnetz: Der Kopf ist nie Kleidung (`Kleidungsmaske.HALS_UNTER_KINN`).

Ablage:
    arbeit/kleidung_maske.npz        je Fläche des Körpernetzes: kleidung (bool), stueck (int8), haut (bool)
    ergebnis/kleidung_<teil>_<ansicht>.png   teil = ohne | nur, ansicht = vorn | seite | hinten
    ergebnis/kleidung.glb            die Kleidung als Objekt in der RUHELAGE der Figur (nach „vorschau")
    ergebnis.kleidung                Kennzahlen (`Kleidungsteilung.kennzahlen`), Hautmodell, Bilder, Sekunden
"""

import logging
import os
import time

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurkleidung']


class Meshfigurkleidung:
    TEILE = ('ohne', 'nur')

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    @staticmethod
    def datei(teil, ansicht):
        return 'kleidung_%s_%s.png' % (teil, ansicht)

    # ---------------------------------------------------------------- Netz

    def koerpernetz(self):
        """`(scan, daten)` — das KÖRPERnetz in der Lage der Erkennung (nie das Kopfnetz) und die Daten des Runners."""
        from ..daten.meshto3dpfad import Meshto3dpfad

        arbeit = self.ablage.arbeit()
        with Meshto3dpfad():
            from meshfigur_daten import Meshfigurdaten
            from meshfigur_scan import Meshfigurscan

            daten = Meshfigurdaten(str(arbeit / 'auftrag.json'))
            scan = Meshfigurscan.laden(daten.auftrag['netz'])
            with np.load(arbeit / 'scan_lage.npz') as d:
                scan.anwenden(d['matrix'])
        return scan, daten

    # -------------------------------------------------------------- Schritt

    def ausfuehren(self):
        from Kleidung.kleidungsmaske import Kleidungsmaske
        from Kleidung.kleidungsteilung import Kleidungsteilung
        from Kleidung.sapiensmaske import Sapiensmaske

        from ..daten.meshto3dpfad import Meshto3dpfad
        from .meshfigurhaarabzug import Meshfigurhaarabzug

        t0 = time.perf_counter()
        scan, daten = self.koerpernetz()
        self.lauf.melden(0.1, 'Kleidung erkennen')
        # `hautkarte()` lädt Module des Runners nach — dafür muss `meshto3d` (samt den gemeinsamen Wrappern) im Pfad stehen.
        with Meshto3dpfad():
            from meshfigur_hautkarte import Meshfigurhautkarte

            modell = daten.hautkarte()[0]
            if modell is None:
                self.job.ergebnis['kleidung'] = {'fehler': 'Kein Hautmodell: zu wenige kahle Stellen (Gesicht, '
                                                           'Hände, Unterarme, Unterschenkel) sind erkannt'}
                return
            landmarken = daten.landmarken()
            karte = Meshfigurhautkarte(scan, modell, landmarken['koerper'], landmarken.get('treffer'))
            entscheidung = karte.rechnen()
        regel = Kleidungsmaske(scan.punkte, scan.flaechen, entscheidung['haut'], landmarken['koerper'],
                               landmarken.get('gesicht'), karte)
        maske, sapiens = self._sapiens(regel, regel.rechnen(), karte, scan, daten)
        maske, hut = self._kopfbedeckung(maske, regel)
        maske = self._bart_abziehen(maske, regel)
        # Mit der Sapiens-Maske reicht der Kragen über die Kopfgrenze (`Sapiensmaske.KRAGEN_M`) — das Bereinigen (Rand glätten, runden) muss ihn ebenso behandeln wie den Rest des Stoffs.
        kragen = Sapiensmaske.KRAGEN_M if (sapiens or {}).get('verwendet') else 0.0
        maske, bereinigung = self._bereinigen(maske, regel, np.asarray(modell.ist_haut(entscheidung['farben']), dtype=bool), kragen)
        maske = Meshfigurhaarabzug.abziehen(self.ablage, maske, regel)      # NACH dem Bereinigen: Löcher füllen und Rand glätten holten Haarflächen sonst zurück in den Stoff
        # `maske['haut']`, nicht `entscheidung['haut']`: der Hautton nur dort, wo kein Stück gilt (`Kleidungsmaske.abschliessen`) — mit der Sapiens-Maske stand er sonst auf Hose und Socken.
        # `hautfarbe`: nur die FARBE gegen das Hautmodell (nicht die Hautkarte, die Stoffbereiche ausnimmt) — damit schält `objekt` den hautfarbenen Textursaum an der Kante ab (`Kleidung.kleidungsrand`).
        np.savez_compressed(self.ablage.arbeit('kleidung_maske.npz'), kleidung=maske['kleidung'],
                            stueck=maske['stueck'], haut=maske['haut'], hautfarbe=np.asarray(modell.ist_haut(entscheidung['farben']), dtype=bool))
        teilung = Kleidungsteilung(scan.punkte, scan.flaechen, scan.uv_ecken, entscheidung['farben'], maske,
                                   karte.inhalt)
        t1 = time.perf_counter()
        self.lauf.melden(0.5, 'Bilder ohne Kleidung / nur Kleidung')
        bilder = self.bilder(scan, teilung)
        self.job.ergebnis['kleidung'] = {
            **teilung.kennzahlen(),
            'hautmodell': modell.befund(),
            'baender': entscheidung.get('baender'),
            'bilder': bilder,
            'sekunden': {'erkennen': round(t1 - t0, 1), 'bilder': round(time.perf_counter() - t1, 1)},
        }
        if sapiens is not None:
            self.job.ergebnis['kleidung']['sapiens'] = sapiens
        if hut is not None:
            self.job.ergebnis['kleidung']['kopfbedeckung'] = hut
        if bereinigung is not None:
            self.job.ergebnis['kleidung']['bereinigung'] = bereinigung

    @staticmethod
    def _hautrand_behandeln(scan, wahl, hautfarbe, art='umfaerben'):
        """`(wahl, uv_ecken, Bericht)` — der hautfarbene Textursaum an der Kante des Objekts (`Kleidung.kleidungsrand`): er stand an jedem Rand als oranger Streifen statt eines Saums. `art`:
        `umfaerben` (Vorgabe seit 13.10.2026) — die Flächen bleiben, bekommen aber die UV des Gewebes daneben; `entfernen` — sie kommen nicht ins Objekt (so bis 13.10.2026: Edgar „die Hose hat keinen Saum“, dann „der Saum der Hose fehlt“ —
        mit dem orangen Streifen ging die Saumfalte selbst verloren); `aus` — wie das Netz. Ohne `hautfarbe` in der Maske (Lauf vor dem 12.10.2026 abends) bleibt alles, wie es ist (Bericht None)."""
        if art == 'aus' or hautfarbe is None or len(hautfarbe) != len(wahl) or scan.uv_ecken is None:        # ohne UV (Farben je Punkt) gibt es keinen Textursaum
            return wahl, scan.uv_ecken, None
        from Kleidung.kleidungsrand import Kleidungsrand

        ids = np.flatnonzero(wahl)
        nachbarn = Kleidungsrand.nachbarn_aus(scan.flaechen[ids])
        band = Kleidungsrand.hautband(nachbarn, hautfarbe[ids], scan.flaecheninhalte()[ids])
        if not band.any():
            return wahl, scan.uv_ecken, None
        bericht = {'flaechen': int(band.sum()), 'anteil': round(float(band.mean()), 4), 'art': art}
        if art == 'entfernen':
            neu = wahl.copy()
            neu[ids[band]] = False
            return neu, scan.uv_ecken, bericht
        uv, umgefaerbt = Kleidungsrand.umfaerben(nachbarn, band, scan.uv_ecken[ids], np.asarray(scan.punkte)[np.asarray(scan.flaechen)[ids]].mean(axis=1))
        uv_ecken = np.array(scan.uv_ecken, copy=True)
        uv_ecken[ids] = uv
        bericht['umgefaerbt'] = int(umgefaerbt.sum())
        return wahl, uv_ecken, bericht

    def _bart_abziehen(self, maske, regel):
        """Was der Schritt „haar" als langen Bart ablegt (`haar_maske.npz`, `langer_bart`, `Sapienshaar.langer_bart`), ist Haar und nicht Kleidung. Fehlt die Ablage oder der Schlüssel: die Maske, wie sie ist."""
        pfad = self.ablage.arbeit('haar_maske.npz')
        if not os.path.isfile(pfad):
            return maske
        with np.load(pfad) as d:
            bart = d['langer_bart'] if 'langer_bart' in d.files else None
        stueck = np.asarray(maske['stueck'])
        if bart is None or len(bart) != len(stueck) or not (bart & (stueck > 0) & (stueck != 4)).any():
            return maske
        stueck = stueck.copy()
        stueck[bart & (stueck > 0) & (stueck != 4)] = 0
        return regel.abschliessen(stueck)

    def _bereinigen(self, maske, regel, hautfarbe=None, kragen=0.0):
        """`(maske, bericht)`: Löcher im Stoff füllen, Zubehör über nicht hautfarbene Nachbarflächen vervollständigen und den Rand glätten (`Kleidung.kleidungsbereinigung`; `hautfarbe` (F,) bool: die Farbe gegen das Hautmodell) — die Sapiens-Maske lässt Flächen mitten in Hose und Hemd als Haut stehen
        (Edgar: „Haut geht durch die Hose"), ihr Rand ist eine Zackenreihe, die Uhr fehlen Teile des Armbands. Ändert sich nichts, bleibt die Maske, wie sie ist (None)."""
        from Kleidung.kleidungsbereinigung import Kleidungsbereinigung

        stueck, bericht = Kleidungsbereinigung(regel.karte.nachbarn(), regel.inhalt, regel.mitte[:, 1], regel.kopf_ab() + kragen).bereinigen(maske['stueck'], hautfarbe)
        if not (bericht['loch_flaechen'] or bericht['rand_geaendert_flaechen']):
            return maske, None
        return regel.abschliessen(stueck), bericht

    def _kopfbedeckung(self, maske, regel):
        """`(maske, bericht)`: ein Hut ist Zubehör, nicht Haar und nicht Kopf. Der Schritt „haar" legt die Flächen ab, die Sapiens als `Apparel` im Haarbereich sieht (`haar_maske.npz`, `kopfbedeckung`,
        `Sapienshaar.kopfbedeckung`); der Kopf ist sonst nie Kleidung (`Kleidungsmaske.kopf_ab`), also gehören sie hier ausdrücklich dazu — als Stück „Zubehör", damit sie im Objekt „Kleidung" stehen
        und nicht im Haar. Fehlt die Ablage oder ist kein Hut da, bleibt die Maske, wie sie ist (None)."""
        pfad = self.ablage.arbeit('haar_maske.npz')
        if not os.path.isfile(pfad):
            return maske, None
        with np.load(pfad) as d:
            hut = d['kopfbedeckung'] if 'kopfbedeckung' in d.files else None
        if hut is None or not hut.any() or len(hut) != len(maske['stueck']):
            return maske, None
        from Kleidung.kleidungsmaske import Kleidungsmaske

        stueck = np.asarray(maske['stueck']).copy()
        stueck[hut] = Kleidungsmaske.ZUBEHOER
        neu = regel.abschliessen(stueck)
        return neu, {'flaechen': int(hut.sum()), 'cm2': round(float(regel.inhalt[hut].sum()) * 1e4, 0)}

    def _sapiens(self, regel, maske, karte, scan, daten):
        """`(maske, bericht)`: die Sapiens-Fassung der Maske (`Kleidung/sapiensmaske.py`), wenn der Lauf sie verlangt — `lauf.sapiens_maske` setzt nur „2D3D Kleider" aus der Option
        `segmentierung.verwenden`, „Mesh to 3D" hat das Attribut nicht — UND die Stimmen des Schritts „Segmentierung" zu diesem Netz passen. Sonst die Regel unverändert; der
        Grund steht im Bericht (`ergebnis.kleidung.sapiens`), nie ein stilles Zurückfallen."""
        if not getattr(self.lauf, 'sapiens_maske', False):
            return maske, None
        from Kleidung.sapiensmaske import Sapiensmaske
        from Kleidung.sapienszuordnung import Sapienszuordnung

        from .engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen

        einstellungen = getattr(self.lauf, 'sapiens_einstellungen', None) or {}
        try:
            # Das Netz des Schritts „netz" (`original=True`), nicht `daten.auftrag['netz']`: Mit Option `koerper.tiefe` ist das die Tiefenfassung — die Stimmen wurden auf dem Original gerechnet.
            klassen = Sapiensmaske.laden(self.ablage.arbeit(), self.ablage.netzdatei(original=True), len(scan.flaechen),
                                         Engine2d3dKleidersegmentierungsoptionen.rechenoptionen(einstellungen))
        except Sapiensmaske.Unbrauchbar as grund:
            logger.warning('Kleidung %s: Sapiens-Maske nicht benutzt (%s) — Farbe und Lage gelten', self.job.kennung, grund)
            return maske, {'verwendet': False, 'grund': str(grund)}
        stimmen = Sapienszuordnung.stimmen(klassen, einstellungen)          # Schuhe, Socken, Zubehör nach den Optionen
        stueck, bericht = Sapiensmaske(stimmen, karte, karte.inhalt, regel.mitte, regel.kopf_ab(), **Sapiensmaske.aus_optionen(einstellungen)).verbinden(maske['stueck'])
        logger.info('Kleidung %s: Sapiens-Maske, %d von %d Flächen anders als die Regel', self.job.kennung,
                    bericht['flaechen_geaendert'], len(scan.flaechen))
        return regel.abschliessen(stueck), bericht

    def bilder(self, scan, teilung):
        """`{teil: {ansicht: Datei}}` — beide Teile im selben Ausschnitt (der ganze Körper)."""
        from Genesis9.offscreenwerk import G9offscreenwerk
        from Kleidung.kleidungsbild import Kleidungsbild

        bild = Kleidungsbild(scan.textur)
        fenster = bild.fenster(scan.punkte)
        netze = {'ohne': teilung.ohne_kleidung(), 'nur': teilung.nur_kleidung()}
        aus = {}
        # Ein Renderer und ein Netz je Teil für alle drei Ansichten (siehe `Meshfigurhaar.bilder`).
        with G9offscreenwerk.sitzung():
            for teil in self.TEILE:
                wahl = ~teilung.maske['kleidung'] if teil == 'ohne' else teilung.maske['kleidung']
                farben = teilung.farben[wahl]
                for ansicht in Kleidungsbild.ANSICHTEN:
                    name = self.datei(teil, ansicht)
                    bild.speichern(netze[teil], ansicht, fenster, self.ablage.ergebnis(name), farben=farben)
                    aus.setdefault(teil, {})[ansicht] = name
            bild.freigeben()
        return aus

    # --------------------------------------------------------------- Objekt

    def objekt(self):
        """Die Kleidung als eigenes Objekt für die Bühne: `ergebnis/kleidung.glb` in der RUHELAGE der Figur.

        Das Netz steht in der Haltung der Person; `Kleidungsentposen` rechnet es mit dem Käfig der Figur (in Ruhe
        `genesis_ende.npz`, in der Haltung `posiert.npy`) zurück. Deshalb erst im Schritt „vorschau", wenn beide zur
        aktuellen Figur gehören. Scheitert es, steht der Grund in `ergebnis.kleidung.objekt.fehler`."""
        from Kleidung.kleidungsobjekt import Kleidungsobjekt

        from .meshfigurkleidungsruhelage import Meshfigurkleidungsruhelage

        kleidung = self.job.ergebnis.get('kleidung')
        if not kleidung or kleidung.get('fehler'):
            return None
        pfad = self.ablage.arbeit('kleidung_maske.npz')
        ruhe, posiert = self.ablage.arbeit('genesis_ende.npz'), self.ablage.arbeit('posiert.npy')
        if not (pfad.is_file() and ruhe.is_file() and posiert.is_file()):
            kleidung['objekt'] = {'fehler': 'Maske oder Figur fehlen'}
            return None
        scan, _ = self.koerpernetz()
        with np.load(pfad) as d:
            wahl = d['kleidung']
            hautfarbe = d['hautfarbe'] if 'hautfarbe' in d.files else None
        if len(wahl) != len(scan.flaechen):
            kleidung['objekt'] = {'fehler': 'Maske passt nicht zum Netz'}
            return None
        if not wahl.any():
            # Keine Kleidung erkannt (nackter Körper, wie Damira): kein Fehler, nur kein Objekt — die Bühne zeigt
            # von `fehler` eine Meldung, von `hinweis` nichts.
            kleidung['objekt'] = {'hinweis': 'Keine Kleidung erkannt'}
            return None
        if not scan.hat_aussehen():
            kleidung['objekt'] = {'fehler': 'Netz ohne Textur und ohne Farben je Punkt'}
            return None
        with np.load(ruhe) as d:
            kaefig_ruhe = np.asarray(d['punkte'], dtype=np.float64)
            teil = np.asarray(d['teil']) if 'teil' in d.files else None
        # Mit Körperteilen (12.10.2026): eine Hand neben dem Saum zog die Unterhose mit nach außen (Fahne bis 131 mm) — `Meshfigurkleidungsruhelage`.
        ruhelage = Meshfigurkleidungsruhelage(kaefig_ruhe, np.load(posiert).astype(np.float64), teil)
        wahl, uv_ecken, hautband = self._hautrand_behandeln(scan, wahl, hautfarbe, str((self.job.optionen or {}).get('hautband') or 'umfaerben'))
        if hautband:
            kleidung['objekt_hautrand'] = hautband
        # Was als eigener Bestandteil ein Objekt hat (Stab, Tasche — `Meshfigurteile`, SAM 3), steht nicht noch einmal im Kleidungsobjekt.
        from .meshfigurteile import Meshfigurteile

        eigene = Meshfigurteile.maske_eigene(Meshfigurteile.holen(self.lauf))
        if eigene is not None and len(eigene) == len(wahl):
            abgezogen = int((wahl & eigene).sum())
            wahl = wahl & ~eigene
            kleidung['teile_abgezogen'] = abgezogen
            if not wahl.any():
                kleidung['objekt'] = {'hinweis': 'Die Kleidung besteht nur aus eigenen Bestandteilen'}
                return None
        from .meshfigurobjektflaechen import Meshfigurobjektflaechen

        Meshfigurobjektflaechen.schreiben(self.ablage, 'kleidung', wahl)       # für die Abnahme: welche Flächen dieses Objekt wirklich trägt
        genutzt, neu = np.unique(scan.flaechen[wahl].reshape(-1), return_inverse=True)
        punkte = ruhelage.punkte(scan.punkte[genutzt], neu.reshape(-1, 3))
        # Knochen und Gewichte für die Animation (`Meshfigurhautgewichte`): aus der Käfig-Nachbarschaft, die auch die Rückrechnung benutzt hat.
        from .meshfigurhautgewichte import Meshfigurhautgewichte

        from .meshfigurtanzpruefung import Meshfigurtanzpruefung

        # Animationsprüfung (13.10.2026): reißt der Stoff im Tanz, wählt sie die weichen statt der alten Gewichte (`ergebnis.animation`); Option `animationspruefung`.
        haut = Meshfigurhautgewichte.kaefig_von(self.ablage, ruhelage, scan.punkte[genutzt], Meshfigurtanzpruefung.fuer(self.lauf), 'kleidung', neu.reshape(-1, 3), punkte)
        steckbrief = Kleidungsobjekt.schreiben(self.ablage.ergebnis('kleidung.glb'), punkte, neu.reshape(-1, 3),
                                               haut=haut, **scan.aussehen(wahl, genutzt, uv_ecken))
        kleidung['objekt'] = {'datei': 'kleidung.glb', **steckbrief, 'entposen': ruhelage.entposen.pruefen(), 'ruhelage': ruhelage.befund}
        # Dasselbe Stück unverändert in der Haltung des Netzes (`Meshfighaltung`): für die Bühne mit gebackener Haltung, ohne Rückrechnung.
        from .meshfighaltung import Meshfighaltung

        haltung = Meshfighaltung.holen(self.lauf)
        if haltung is not None:
            steckbrief = Kleidungsobjekt.schreiben(self.ablage.ergebnis('kleidung_haltung.glb'), haltung.punkte(scan.punkte[genutzt]), neu.reshape(-1, 3),
                                                   **scan.aussehen(wahl, genutzt, uv_ecken))
            kleidung['objekt']['haltung'] = {'datei': 'kleidung_haltung.glb', **steckbrief}
        return kleidung['objekt']
