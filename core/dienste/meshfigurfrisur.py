# -*- coding: utf-8 -*-
"""Meshfigurfrisur — Schritt „frisur" von „Mesh to 3D": eine echte Frisur statt der Haarschale des Netzes.

Edgar, 29.09.2026: „das haar soll aber etwas natürlicher anschauen, wie war das mit den Morphs und dem Genesis
Modell für Haar?" → „mach a-b, c als option parallel". Das Haar aus Schritt „haar" ist ein Stück Netz mit
eingebackenem Licht, ohne Strähnen und ohne Durchsicht. Hier wird es zum ZIEL:

A  Frisurwahl: jede Frisur der Garderobe (Daz, Genesis-8/1/2-Klone, ohne Bart und Toon) in jedem formenden
   Stil auf die angepasste Figur (`Meshfigurfrisurstueck`), gemessen als Hülle gegen die Hülle des Netzhaars
   (`Haar.haarhuelle`: je Richtung vom Kopf der weiteste Punkt; fehlendes und überzähliges Haar zählen mit).
   Die besten `OBERSTE` Daz-Frisuren und „Haar Eigen" bekommen ihre Formregler gestellt
   (`Haar.frisurregler`), die kleinste Hülle gewinnt. Farbe = Median des Netzhaars als Umfärbung (`farbe`).
B  „Haar Eigen" (`G9haareigen`): Kin als eigenes Stück mit Länge, Kurz, Dichte, Wellig, Dutt — gebaut, wenn
   es fehlt, und in der Wahl wie jede andere Frisur.
C  Haarkarten aus der Schale (`Haar.haarkarten`, Option `haarkarten`): Strähnen von der Kopfhaut an der Schale
   entlang, als eigenes Objekt `ergebnis/haarkarten.glb` — parallel zu A, die Bühne wählt.

Nach „vorschau" (erst dann gehören `genesis_ende.npz`/`posiert.npy` und damit die Ruhelage des Netzhaars zur
Figur), vor „speichern" (das Modell trägt die gewählte Frisur als `kleidung`, `Meshfigurspeichern`).

    ergebnis.frisur = {kandidaten: [{kennung, name, stil, mm, deckung, …}],
                       fein: [{…, regler, vorher, nachher}],
                       wahl: {kennung, name, stil, regler, farbe, abstand}, kleidung: {kennung: {…}},
                       karten: {datei, strähnen, …} | {fehler}, sekunden: {…}}
"""

import logging
import re
import time

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurfrisur']


class Meshfigurfrisur:
    PROBEN = 60000
    OBERSTE = 2
    #: Bärte und Toon-Frisuren (für die Anime-Figur gebaut) sind keine Kandidaten.
    AUSSCHLUSS = re.compile(r'beard|bart|toon', re.IGNORECASE)
    MITTE_UNTER_SCHEITEL_M = 0.10
    ANZEIGE = 12

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = lauf.optionen

    def ausfuehren(self):
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        from .meshfigurhaar import Meshfigurhaar

        wahl = self.optionen.get('frisur') or 'beste'
        aus = self.job.ergebnis['frisur'] = {'option': wahl, 'sekunden': {}}
        netz = Meshfigurhaar(self.lauf).ruhenetz()
        if netz is None:
            aus['fehler'] = 'Kein Haar aus Schritt „haar" (Maske oder Registrierung fehlen)'
            return
        scan, punkte, haar = netz
        t0 = time.perf_counter()
        formung = G9formung(self.job.stellung())
        figur, _, _ = G9reglerableitung.lage(formung)
        self.messung, haar = self._messung(punkte, scan.flaechen, haar, figur)
        aus['sekunden']['vorbereiten'] = round(time.perf_counter() - t0, 1)
        if wahl != 'aus':
            self.waehlen(wahl, formung, aus)
        if self.optionen.get('haarkarten') == 'an':
            t = time.perf_counter()
            aus['karten'] = self.karten(scan, punkte, haar, figur)
            aus['sekunden']['karten'] = round(time.perf_counter() - t, 1)

    # ------------------------------------------------------------ Messung

    def _messung(self, punkte, flaechen, haar, figur):
        """`(messen, haar)` — `messen(punkte) -> {mm, deckung, …}` gegen die Hülle des Netzhaars; die
        Richtungen des geschützten inneren Gesichts (`Haarmaske`, `geschuetzt`) kosten Haar extra
        (`Haarhuelle.GESICHT_M`). `haar` ohne die Flächen, die in diese Richtungen liegen: die Maske ließ
        bei Auftrag 2026.09.28.23.42.28 Inseln an Braue und Nase stehen, an denen Haarkarten übers Gesicht
        wuchsen (im Chrome gesehen, 29.09.2026)."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Haar.haarhuelle import Haarhuelle

        kopf = figur[G9koerperteile.genesis_punkte(G9haut.holen()) == 0]
        scheitel = float(kopf[:, 1].max())
        self.mitte = np.array([float(kopf[:, 0].mean()), scheitel - self.MITTE_UNTER_SCHEITEL_M,
                               0.5 * float(kopf[:, 2].min() + kopf[:, 2].max())])
        huelle = Haarhuelle(self.mitte)
        with np.load(self.ablage.arbeit('haar_maske.npz')) as d:
            geschuetzt = d['geschuetzt']
        gesicht = None
        if len(geschuetzt) == len(flaechen) and geschuetzt.any():
            gesicht = ~np.isnan(huelle.karte(Haarhuelle.proben(punkte, flaechen[geschuetzt], 20000)))
            feld, _r = huelle.felder(punkte[flaechen].mean(axis=1))
            haar = haar & ~gesicht.reshape(-1)[feld]
        ziel = huelle.karte(Haarhuelle.proben(punkte, flaechen[haar], self.PROBEN))
        haut = huelle.karte(figur)
        return (lambda p: huelle.abstand(ziel, huelle.karte(p), haut, gesicht)), haar

    # ------------------------------------------------------------- Wahl A

    def kennungen(self, wahl):
        from Genesis9.garderobe import G9garderobe
        from Genesis9.haareigen import G9haareigen

        eigen = G9haareigen.kennung()
        if wahl == 'eigen':
            return [eigen]
        return [e['id'] for e in G9garderobe.liste()
                if e.get('art') == 'haar' and e.get('zeigbar')
                and not self.AUSSCHLUSS.search(e.get('name') or '')
                and (wahl == 'beste' or e['id'] != eigen)]

    def waehlen(self, wahl, formung, aus):
        from Genesis9.haareigen import G9haareigen

        from .meshfigurfrisurstueck import Meshfigurfrisurstueck

        t = time.perf_counter()
        if wahl in ('beste', 'eigen'):
            try:
                G9haareigen.sicherstellen(melden=lambda text: self.lauf.melden(0.02, text))
            except Exception as fehler:  # noqa: BLE001 — ohne „Haar Eigen" wählen die Daz-Frisuren weiter
                logger.exception('Mesh to 3D %s: Haar Eigen nicht gebaut', self.job.kennung)
                aus['eigen_fehler'] = str(fehler)[:300]
        kennungen = self.kennungen(wahl)
        messungen, stuecke = [], {}
        for i, kennung in enumerate(kennungen):
            try:
                stueck = stuecke[kennung] = Meshfigurfrisurstueck(kennung, formung)
                self.lauf.melden(0.05 + 0.5 * i / max(len(kennungen), 1), 'Frisur messen: %s' % stueck.name)
                for stil in stueck.stile():
                    messungen.append({'kennung': kennung, 'name': stueck.name, 'stil': stil,
                                      **self.messung(stueck.punkte(stil))})
            except Exception as fehler:  # noqa: BLE001 — eine unlesbare Frisur fällt heraus, sichtbar
                logger.warning('Mesh to 3D %s: Frisur %s nicht messbar: %s', self.job.kennung, kennung,
                               fehler)
                messungen.append({'kennung': kennung, 'name': kennung, 'stil': None,
                                  'fehler': str(fehler)[:200]})
        aus['sekunden']['messen'] = round(time.perf_counter() - t, 1)
        beste = self._je_stueck(messungen)
        aus['kandidaten'] = [self._zeile(m) for m in sorted(messungen, key=lambda m: m.get('mm', 1e9))]
        aus['kandidaten'] = aus['kandidaten'][: self.ANZEIGE]
        t = time.perf_counter()
        fein = [self.feinsuche(stuecke[m['kennung']], m, i, len(beste)) for i, m in enumerate(beste)]
        aus['sekunden']['regler'] = round(time.perf_counter() - t, 1)
        aus['fein'] = [{k: v for k, v in f.items() if k != 'stueck'} for f in fein]
        if not fein:
            aus['fehler'] = 'Keine Frisur messbar'
            return aus
        sieger = min(fein, key=lambda f: f['nachher']['mm'])
        farbe = self.farbe()
        aus['wahl'] = {'kennung': sieger['kennung'], 'name': sieger['name'], 'stil': sieger['stil'],
                       'regler': sieger['regler'], 'farbe': farbe, 'abstand': sieger['nachher']}
        stil = next((s for s in sieger['stueck'].stile() if s and s['id'] == sieger['stil_id']), None)
        aus['kleidung'] = {sieger['kennung']: sieger['stueck'].kleidung(stil, sieger['regler'], farbe)}
        return aus

    def _je_stueck(self, messungen):
        """Je Stück die beste Stilvariante; davon die `OBERSTE` Daz-Frisuren und „Haar Eigen"."""
        from Genesis9.haareigen import G9haareigen

        je = {}
        for m in messungen:
            if 'mm' in m and (m['kennung'] not in je or m['mm'] < je[m['kennung']]['mm']):
                je[m['kennung']] = m
        reihe = sorted(je.values(), key=lambda m: m['mm'])
        eigen = [m for m in reihe if m['kennung'] == G9haareigen.kennung()]
        return [m for m in reihe if m['kennung'] != G9haareigen.kennung()][: self.OBERSTE] + eigen

    def feinsuche(self, stueck, messung, i, n):
        from Haar.frisurregler import Frisurregler

        stil = messung['stil']
        self.lauf.melden(0.6 + 0.35 * i / max(n, 1), 'Regler stellen: %s' % stueck.name)
        grenzen = stueck.grenzen()
        grund, deltas = stueck.deltas(stil, list(grenzen))
        suche = Frisurregler(lambda p: self.messung(p)['mm'], grund, deltas, grenzen).suchen()
        nachher = self.messung(stueck.punkte(stil, suche['werte']))
        return {'stueck': stueck, 'kennung': stueck.kennung, 'name': stueck.name,
                'stil': stil['name'] if stil else None, 'stil_id': stil['id'] if stil else None,
                'regler': suche['werte'], 'versuche': suche['versuche'], 'schwach': suche['schwach'],
                'vorher': {k: messung[k] for k in ('mm', 'deckung', 'fehlt_mm', 'zuviel_mm', 'gemeinsam_mm')},
                'nachher': nachher}

    @staticmethod
    def _zeile(m):
        stil = m.get('stil')
        return {**{k: v for k, v in m.items() if k != 'stil'}, 'stil': stil['name'] if stil else None}

    def farbe(self):
        """`#rrggbb` — das belichtete Haar des Netzes (`Haarteilung.kennzahlen`, `farbe.haar`), sonst der
        Median der Haarflächen (Läufe vor dem 29.09.2026 kennen nur ihn).

        Der Median liegt zu dunkel: Ein Netz backt sein Licht ein, Haar im Nacken und unter dem Scheitel ist
        schattig — und die Frisur wird in Genesis noch einmal schattiert (Lauf 13.42.12: Median 86/73/75,
        das Haar im Bild silbrig)."""
        farbe = (self.job.ergebnis.get('haar') or {}).get('farbe') or {}
        wert = farbe.get('haar') or farbe.get('median') or [80, 60, 45]
        return '#%02x%02x%02x' % tuple(int(max(0, min(255, round(w)))) for w in wert[:3])

    # ------------------------------------------------------------ Karten C

    def karten(self, scan, punkte, haar, figur):
        """Haarkarten aus der Schale → `ergebnis/haarkarten.glb`; `{datei, …}` oder `{fehler}`."""
        from Haar.haarkarten import Haarkarten

        self.lauf.melden(0.96, 'Haarkarten aus der Schale')
        try:
            wahl = np.where(haar)[0]
            farben = scan.farben(wahl, np.tile((1 / 3, 1 / 3, 1 / 3), (len(wahl), 1)))
            karten = Haarkarten(punkte, scan.flaechen[wahl], np.asarray(farben, dtype=np.float64), figur,
                                self.mitte)
            return {'datei': 'haarkarten.glb', **karten.schreiben(self.ablage.ergebnis('haarkarten.glb'))}
        except Exception as fehler:  # noqa: BLE001 — Option C darf A und das Modell nie verhindern
            logger.exception('Mesh to 3D %s: Haarkarten gescheitert', self.job.kennung)
            return {'fehler': str(fehler)[:300]}
