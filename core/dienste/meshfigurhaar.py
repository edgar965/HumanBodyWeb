# -*- coding: utf-8 -*-
"""Meshfigurhaar — Schritt „haar" von „Mesh to 3D": das Haar aus dem Netz schneiden (Paket `Haar`).

Edgar, 27.09.2026: „mach dir eine Methode, mit der du das Haar extrahierst aus dem Mesh, und zeige es in
dem Jobverlauf, wie das Mesh ohne Haar ausschaut".

Netz ist das Kopfnetz, sonst das Körpernetz — in der Lage der Erkennung (`Gesichtsformziel.laden`), mit den
Gesichtspunkten derselben Erkennung. Unter der Schnittebene des Kopfnetzes (`erkennung.kopf.ebene`) ist
Rumpf; ohne Kopfnetz alles ab 12 cm unter dem Kinn (`Haarmaske.UNTER_KINN`).

Ablage:
    arbeit/haar_maske.npz          je Fläche des Netzes: haar, geschuetzt, unten, bart (bool) — der Bart
                                   (nur bei kurzem Haar, `Haarmaske._bart`) ist NICHT Haar
    ergebnis/haar_<teil>_<ansicht>.png   teil = ohne | nur, ansicht = vorn | seite | hinten
    ergebnis.haar                  Kennzahlen (`Haarteilung.kennzahlen`), Quelle, Bilder, Sekunden
"""

import logging
import time

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurhaar']


class Meshfigurhaar:
    KANTE = 600
    TEILE = ('ohne', 'nur')
    #: Farbe je Fläche = Mittel aus Schwerpunkt und drei eckennahen Proben (Textur bilinear).
    PROBEN = ((1 / 3, 1 / 3, 1 / 3), (0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6))

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    @staticmethod
    def datei(teil, ansicht):
        return 'haar_%s_%s.png' % (teil, ansicht)

    def ausfuehren(self):
        from Genesis9.gesichtsrahmen import G9gesichtsrahmen
        from Haar.haarmaske import Haarmaske
        from Haar.haarteilung import Haarteilung

        from .gesichtsformziel import Gesichtsformziel

        t0 = time.perf_counter()
        ziel = Gesichtsformziel(self.job)
        scan, gesicht = ziel.laden()
        if not G9gesichtsrahmen.gueltig(gesicht):
            # Kein Rand-, sondern ein Komplettausfall der Erkennung (Bart, Hut, ungewöhnliche Proportionen —
            # 478 von 478 Landmarken NaN, Zauberer-Vorlage 29.09.2026): ohne Rahmen kann `Haarmaske` weder
            # Gesicht schützen noch Bartzone noch Hautton an der Nase bestimmen. Der Lauf bricht deshalb
            # NICHT ab — das Netz bleibt ohne Haar/Kopfhaut-Trennung, sichtbar im Ergebnis.
            self.job.ergebnis['haar'] = {'uebersprungen': 'Kein Gesicht erkannt (Landmarken fehlen komplett)'}
            self.lauf.melden(1.0, 'Haar übersprungen: kein Gesicht erkannt')
            return
        kopf = (self.job.ergebnis.get('erkennung') or {}).get('kopf') or {}
        ebene = kopf.get('ebene') if not kopf.get('fehler') else None
        farben = self.farben(scan)
        self.lauf.melden(0.2, 'Haar erkennen')
        t1 = time.perf_counter()
        hauttest, hautquelle = self.hauttest()
        haar = Haarmaske(scan.punkte, scan.flaechen, farben, gesicht, hauttest, ebene)
        maske = haar.rechnen()
        # Die Haarmaske aus der Sapiens-Klasse „Hair" (Option `segmentierung.haar`, 05.10.2026) — nur in 2D3D Kleider; „farbe" (Vorgabe) ändert nichts.
        from .sapienshaar import Sapienshaar
        sapiens = Sapienshaar(self.lauf).anwenden(maske, haar, len(scan.flaechen))
        np.savez_compressed(self.ablage.arbeit('haar_maske.npz'),
                            **{k: maske[k] for k in ('haar', 'geschuetzt', 'unten', 'bart')},
                            # Sapiens sieht einen Hut als `Apparel`, nicht als Haar (`Sapienshaar.kopfbedeckung`); der Schritt „kleidung" macht daraus Zubehör. Ohne Sapiens: nichts.
                            kopfbedeckung=maske.get('kopfbedeckung', np.zeros(len(scan.flaechen), dtype=bool)),
                            # Ein Bart unter der Schnittebene (`Sapienshaar.langer_bart`): nur im Haar-Objekt, nicht in `haar` (die Frisurwahl misst die Hülle des Kopfhaars).
                            langer_bart=maske.get('langer_bart', np.zeros(len(scan.flaechen), dtype=bool)))
        teilung = Haarteilung(scan.punkte, scan.flaechen, scan.uv_ecken, farben, maske, haar.rahmen)
        t2 = time.perf_counter()
        self.lauf.melden(0.5, 'Bilder ohne Haar / nur Haar')
        bilder = self.bilder(scan, maske, teilung, haar.rahmen)
        self.job.ergebnis['haar'] = {
            **teilung.kennzahlen(),
            'hauttest': hautquelle,
            'quelle': 'Kopfnetz' if (self.job.eingang or {}).get('kopf') and ebene else 'Körpernetz',
            'bilder': bilder,
            'sekunden': {'laden': round(t1 - t0, 1), 'maske': round(t2 - t1, 1),
                         'bilder': round(time.perf_counter() - t2, 1)},
        }
        if sapiens is not None:
            self.job.ergebnis['haar']['sapiens'] = sapiens

    def objekt(self):
        """Das Haar als eigenes Objekt für die Bühne: `ergebnis/haar.glb` in der RUHELAGE der Figur.

        Das Netz kommt über die Registrierung der Anpassung dorthin (`Gesichtsformziel.lage`: Kopf aus
        `genesis_ende.npz` gegen `posiert.npy`, Kabsch) — deshalb erst im Schritt „vorschau", wenn beide
        zur aktuellen Figur gehören (nach einem neuen Lauf lägen hier sonst die der alten)."""
        from Haar.haarobjekt import Haarobjekt

        haar = self.job.ergebnis.get('haar')
        netz = self.ruhenetz()
        if not haar:
            return None
        if netz is None:
            haar['objekt'] = {'fehler': 'Maske, Registrierung oder Netz fehlen oder passen nicht zusammen'}
            return None
        scan, punkte, wahl = netz
        if not scan.hat_aussehen():
            haar['objekt'] = {'fehler': 'Netz ohne Textur und ohne Farben je Punkt'}
            return None
        with np.load(self.ablage.arbeit('haar_maske.npz')) as d:
            bart = d['langer_bart'] if 'langer_bart' in d.files else None
        # Ein Bart, den SAM 3 als Bestandteil mit eigenem Objekt gefunden hat (`Meshfigurteile`, Gruppe „haar"), ist dieses Objekt — es steht neben JEDER Frisur der Bühne und nicht nur in „Haar aus dem Netz".
        from .meshfigurteile import Meshfigurteile

        teile = Meshfigurteile.holen(self.lauf)
        eigene = Meshfigurteile.maske_eigene(teile)                     # jeder Bestandteil mit eigenem Objekt (Bart, aber auch ein Helm, den die Farbregel zum Haar zählte) steht nicht im Haarobjekt
        eigener_bart = Meshfigurteile.maske_eigene(teile, ('haar',))
        if eigene is not None and len(eigene) == len(wahl):
            haar['teile_abgezogen'] = int((wahl & eigene).sum())
            wahl = wahl & ~eigene
        if eigener_bart is not None and len(eigener_bart) == len(wahl):
            haar['bart_eigenes_objekt'] = int(eigener_bart.sum())
        elif bart is not None and len(bart) == len(wahl) and bart.any():
            wahl = wahl | bart                                       # der lange Bart hängt am Kopf, wie das Haar
            haar['langer_bart'] = int(bart.sum())
        from .meshfigurobjektflaechen import Meshfigurobjektflaechen

        Meshfigurobjektflaechen.schreiben(self.ablage, 'haar', wahl)              # für die Abnahme: welche Flächen dieses Objekt wirklich trägt
        genutzt, neu = np.unique(scan.flaechen[wahl].reshape(-1), return_inverse=True)
        # Haar und Bart hängen am Kopf (die Ruhelage ist eine Starrkörperbewegung des Kopfes): ganz an `head` gebunden, damit die Animation sie mitnimmt (`Meshfigurhautgewichte`).
        from .meshfigurhautgewichte import Meshfigurhautgewichte

        haut = Meshfigurhautgewichte.starr_von(self.ablage, len(genutzt), 'head')
        steckbrief = Haarobjekt.schreiben(self.ablage.ergebnis('haar.glb'), punkte[genutzt],
                                          neu.reshape(-1, 3), haut=haut, **scan.aussehen(wahl, genutzt))
        haar['objekt'] = {'datei': 'haar.glb', **steckbrief}
        # Dasselbe Haar unverändert in der Haltung des Netzes (`Meshfighaltung`): für die Bühne mit gebackener Haltung.
        from .meshfighaltung import Meshfighaltung

        haltung = Meshfighaltung.holen(self.lauf)
        if haltung is not None:
            steckbrief = Haarobjekt.schreiben(self.ablage.ergebnis('haar_haltung.glb'), haltung.punkte(scan.punkte[genutzt]),
                                              neu.reshape(-1, 3), **scan.aussehen(wahl, genutzt))
            haar['objekt']['haltung'] = {'datei': 'haar_haltung.glb', **steckbrief}
        return haar['objekt']

    def ruhenetz(self):
        """`(scan, punkte in der Ruhelage der Figur (P, 3), Haarflächen (F,) bool)` — oder None, wenn Maske,
        Registrierung oder Netz fehlen oder nicht zusammenpassen. Auch die Frisurwahl und die Haarkarten
        (`Meshfigurfrisur`) nehmen das Haar von hier."""
        from .gesichtsformziel import Gesichtsformziel

        pfad = self.ablage.arbeit('haar_maske.npz')
        ziel = Gesichtsformziel(self.job)
        if not pfad.is_file() or not ziel.vorhanden():
            return None
        with np.load(pfad) as d:
            wahl = d['haar']
        scan, _ = ziel.laden()
        if len(wahl) != len(scan.flaechen) or not wahl.any():
            return None
        r, t = ziel.lage()
        return scan, (np.asarray(scan.punkte, dtype=np.float64) - t) @ r, wahl

    def hauttest(self):
        """`(test(farben) → bool, Quelle)` — das Hautmodell der KAHLEN Stellen (`Meshfigurhautmodell`, dasselbe
        wie in der Körperkette), sonst der alte Test (rot vor blau, gesättigt).

        Der alte Test hielt die wenig bunte Haut im Lauf 13.42.12 (a* 8,4 / b* 4,7) samt Stirn und Wangen für
        Haar — in „nur Haar" stand eine Kapuze um das Gesicht. Das Modell kommt aus den Proben des ganzen Körpers,
        nicht des Kopfnetzes: Hände, Unterarme und Unterschenkel liegen nur dort."""
        from .gesichtsformziel import Gesichtsformziel

        try:
            from ..daten.meshto3dpfad import Meshto3dpfad

            with Meshto3dpfad():
                from meshfigur_daten import Meshfigurdaten

                modell = Meshfigurdaten(str(self.ablage.arbeit('auftrag.json'))).hautkarte()[0]
        except Exception:  # noqa: BLE001 — ohne Hautmodell gilt der alte Test, sichtbar im Ergebnis
            logger.exception('Mesh to 3D %s: Hautmodell für das Haar nicht gerechnet', self.job.kennung)
            modell = None
        if modell is None:
            return Gesichtsformziel._ist_haut, 'alter Test (Rot vor Blau, gesättigt)'
        return modell.ist_haut, 'Hautmodell der kahlen Stellen'

    def farben(self, scan):
        alle = np.arange(len(scan.flaechen))
        proben = [scan.farben(alle, np.tile(b, (len(alle), 1))).astype(np.float64) for b in self.PROBEN]
        return np.mean(proben, axis=0)

    def bilder(self, scan, maske, teilung, rahmen):
        """`{teil: {ansicht: Datei}}` — beide Teile im selben Ausschnitt (der Kopf ohne Rumpf)."""
        from Genesis9.offscreenwerk import G9offscreenwerk
        from Haar.haarbild import Haarbild

        bild = Haarbild(rahmen, scan.textur, self.KANTE)
        kopf = np.unique(scan.flaechen[~maske['unten']])
        fenster = bild.fenster(scan.punkte[kopf])
        netze = {'ohne': teilung.ohne_haar(), 'nur': teilung.nur_haar()}
        aus = {}
        # Ein Renderer und ein Netz je Teil für alle drei Ansichten (`Haarbild._teil` erkennt es an der Identität von `netz` und `farben`) — vorher sechsmal Renderer, Netz und Textur neu (20 s von 37 s).
        with G9offscreenwerk.sitzung():
            for teil in self.TEILE:
                farben = teilung.farben[~maske['haar'] if teil == 'ohne' else maske['haar']]
                for ansicht in Haarbild.ANSICHTEN:
                    name = self.datei(teil, ansicht)
                    bild.speichern(netze[teil], ansicht, fenster, self.ablage.ergebnis(name), farben=farben)
                    aus.setdefault(teil, {})[ansicht] = name
            bild.freigeben()
        return aus
