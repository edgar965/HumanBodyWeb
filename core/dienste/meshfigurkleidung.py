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
        from ..daten.wrapperpfad import Wrapperpfad

        arbeit = self.ablage.arbeit()
        with Wrapperpfad():
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

        from ..daten.wrapperpfad import Wrapperpfad

        t0 = time.perf_counter()
        scan, daten = self.koerpernetz()
        self.lauf.melden(0.1, 'Kleidung erkennen')
        # `hautkarte()` lädt Module des Runners nach — dafür muss das Wrapper-Verzeichnis im Pfad stehen.
        with Wrapperpfad():
            from meshfigur_hautkarte import Meshfigurhautkarte

            modell = daten.hautkarte()[0]
            if modell is None:
                self.job.ergebnis['kleidung'] = {'fehler': 'Kein Hautmodell: zu wenige kahle Stellen (Gesicht, '
                                                           'Hände, Unterarme, Unterschenkel) sind erkannt'}
                return
            landmarken = daten.landmarken()
            karte = Meshfigurhautkarte(scan, modell, landmarken['koerper'], landmarken.get('treffer'))
            entscheidung = karte.rechnen()
        maske = Kleidungsmaske(scan.punkte, scan.flaechen, entscheidung['haut'], landmarken['koerper'],
                               landmarken.get('gesicht'), karte).rechnen()
        np.savez_compressed(self.ablage.arbeit('kleidung_maske.npz'), kleidung=maske['kleidung'],
                            stueck=maske['stueck'], haut=entscheidung['haut'])
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

    def bilder(self, scan, teilung):
        """`{teil: {ansicht: Datei}}` — beide Teile im selben Ausschnitt (der ganze Körper)."""
        from Kleidung.kleidungsbild import Kleidungsbild

        bild = Kleidungsbild(scan.textur)
        fenster = bild.fenster(scan.punkte)
        netze = {'ohne': teilung.ohne_kleidung(), 'nur': teilung.nur_kleidung()}
        aus = {}
        for teil in self.TEILE:
            wahl = ~teilung.maske['kleidung'] if teil == 'ohne' else teilung.maske['kleidung']
            for ansicht in Kleidungsbild.ANSICHTEN:
                name = self.datei(teil, ansicht)
                bild.speichern(netze[teil], ansicht, fenster, self.ablage.ergebnis(name), farben=teilung.farben[wahl])
                aus.setdefault(teil, {})[ansicht] = name
        return aus

    # --------------------------------------------------------------- Objekt

    def objekt(self):
        """Die Kleidung als eigenes Objekt für die Bühne: `ergebnis/kleidung.glb` in der RUHELAGE der Figur.

        Das Netz steht in der Haltung der Person; `Kleidungsentposen` rechnet es mit dem Käfig der Figur (in Ruhe
        `genesis_ende.npz`, in der Haltung `posiert.npy`) zurück. Deshalb erst im Schritt „vorschau", wenn beide zur
        aktuellen Figur gehören. Scheitert es, steht der Grund in `ergebnis.kleidung.objekt.fehler`."""
        from Kleidung.kleidungsentposen import Kleidungsentposen
        from Kleidung.kleidungsobjekt import Kleidungsobjekt

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
        if len(wahl) != len(scan.flaechen):
            kleidung['objekt'] = {'fehler': 'Maske passt nicht zum Netz'}
            return None
        if not wahl.any():
            # Keine Kleidung erkannt (nackter Körper, wie Damira): kein Fehler, nur kein Objekt — die Bühne zeigt
            # von `fehler` eine Meldung, von `hinweis` nichts.
            kleidung['objekt'] = {'hinweis': 'Keine Kleidung erkannt'}
            return None
        if scan.uv_ecken is None or scan.textur is None:
            kleidung['objekt'] = {'fehler': 'Netz ohne Textur'}
            return None
        with np.load(ruhe) as d:
            kaefig_ruhe = np.asarray(d['punkte'], dtype=np.float64)
        entposen = Kleidungsentposen(kaefig_ruhe, np.load(posiert).astype(np.float64))
        genutzt, neu = np.unique(scan.flaechen[wahl].reshape(-1), return_inverse=True)
        punkte = entposen.ruhelage(scan.punkte[genutzt])
        steckbrief = Kleidungsobjekt.schreiben(self.ablage.ergebnis('kleidung.glb'), punkte, neu.reshape(-1, 3),
                                               scan.uv_ecken[wahl], scan.textur)
        kleidung['objekt'] = {'datei': 'kleidung.glb', **steckbrief, 'entposen': entposen.pruefen()}
        return kleidung['objekt']
