# -*- coding: utf-8 -*-
"""Meshfigurgenesis — die Genesis-9-Figur als Datei für die Registrierung auf der Karte (python10).

„Mesh to 3D" (27.09.2026): Die Anpassung an das Netz rechnet in `python10` mit torch
(`VideoToBVH/wrappers/meshfigur_registrierung.py`), Genesis 9 lebt in `python14`. Hier wird
alles, was die Registrierung von Genesis braucht, EINMAL je Runde in ein npz geschrieben:

    punkte, dreiecke          Käfig der Reglerstellung (Füße auf 0), Vierecke halbiert
    knochen, eltern, kopf,    die 138 Knochen: Gelenk in der Ruhelage DIESER Stellung (Gelenke
    orientierung, reihenfolge wandern mit den Reglern), Daz-Achsen und Drehreihenfolge — damit
                              die Registrierung posiert wie `G9knochenmatrizen` und der Browser
    haut_index, haut_gewicht  vier Einflüsse je Punkt (`G9haut`), Knochennummer in `knochen`
    bereich, spiegel, teil    `G9netzbereiche`, `G9koerperteile`
    frei, frei_skala          welche Knochen sich drehen dürfen (Rumpf, Hals, Kopf, Arme, Beine —
                              nicht Finger, Zehen, Gesicht, Verdrillung) und wie weit (weicher Prior)
    lm_*                      Ziele der Landmarken aus `G9netzlandmarken` (Genesis durch denselben
                              Detektor geschickt): Gelenke als Anker + Versatz, Ferse, Zeh und die
                              478 Gesichtspunkte als Dreieck + Anteile
    jcm                       Gelenkkorrekturen (Daz-JCMs) der Haltung der letzten Runde — die
                              Registrierung posiert damit wie Daz, und der Ruhe-Rest enthält keine
                              JCM-Ausgleiche (0 in der ersten Runde)
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurgenesis']


class Meshfigurgenesis:
    #: Knochen mit Drehfreiheit und ihr weicher Prior (Grad, je Achse x, y, z). Nicht `hip`: die
    #: Wurzel dreht die ganze Figur — das tut schon die Lage (Rg) der Registrierung.
    FREI = {
        'pelvis': (25, 25, 25),
        'spine1': (25, 20, 20),
        'spine2': (25, 20, 20),
        'spine3': (20, 20, 20),
        'spine4': (20, 20, 20),
        'neck1': (30, 30, 25),
        'neck2': (30, 30, 25),
        'head': (35, 45, 30),
        'shoulder': (20, 20, 25),
        'upperarm': (90, 30, 90),
        'forearm': (90, 45, 90),
        'hand': (60, 45, 60),
        'thigh': (90, 30, 60),
        'shin': (90, 20, 20),
        'foot': (45, 30, 30),
    }

    def __init__(self, stellung, drehung=None):
        #: `{regler: wert}` samt Grundfigur (BaseFeminine …), ohne Eigenmorph der laufenden Runde.
        self.stellung = dict(stellung or {})
        #: `{knochen: {'rotation/x': Grad, …}}` der letzten Runde — nur für die JCMs.
        self.drehung = dict(drehung or {})

    # -------------------------------------------------------------- bauen

    def daten(self):
        from Genesis9.formung import G9formung
        from Genesis9.haut import G9haut
        from Genesis9.kaefigumriss import G9kaefigumriss
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.netzbereiche import G9netzbereiche
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.skelett import G9skelett

        formung = G9formung(self.stellung)
        punkte, _, _ = G9reglerableitung.lage(formung)
        roh = {k['name']: k for k in G9skelett.roh()}
        knochen = formung.skelett().gelenkknochen()
        namen = [k['name'] for k in knochen]
        nummer = {n: i for i, n in enumerate(namen)}
        haut = G9haut.holen()
        umrechnen = np.array([nummer.get(n, 0) for n in haut.knochen], dtype=np.int32)
        dreiecke = np.asarray(G9kaefigumriss.dreiecke(), dtype=np.int32)
        aus = {
            'punkte': np.asarray(punkte, np.float32),
            'dreiecke': dreiecke,
            'knochen': np.array(namen),
            'eltern': np.array(
                [nummer.get(k['eltern'], -1) if k['eltern'] else -1 for k in knochen], np.int32
            ),
            'kopf': np.array([k['kopf'] for k in knochen], np.float32),
            'orientierung': np.array([np.asarray(roh[n]['orientation'], float) for n in namen], np.float32),
            'reihenfolge': np.array([roh[n]['reihenfolge'] for n in namen]),
            'haut_index': umrechnen[np.asarray(haut.index, np.int64)],
            'haut_gewicht': np.asarray(haut.gewicht, np.float32),
            'bereich': G9netzbereiche.bereiche().astype(np.int8),
            'gesichtskern': G9netzbereiche.gesichtskern(),
            'spiegel': G9netzbereiche.spiegel().astype(np.int32),
            'teil': G9koerperteile.genesis_punkte(haut).astype(np.int8),
            'jcm': self.jcm(formung).astype(np.float32),
        }
        aus.update(self._frei(namen))
        aus.update(self._landmarken(nummer))
        return aus

    def speichern(self, pfad):
        daten = self.daten()
        np.savez(pfad, **daten)
        return {
            'punkte': int(len(daten['punkte'])),
            'knochen': int(len(daten['knochen'])),
            'frei': int(len(daten['frei'])),
            'jcm_mm': round(float(np.linalg.norm(daten['jcm'], axis=1).max()) * 1000.0, 1),
        }

    # --------------------------------------------------------------- Teile

    def _frei(self, namen):
        frei, skala = [], []
        for i, n in enumerate(namen):
            kurz = n[2:] if n[:2] in ('l_', 'r_') else n
            if kurz in self.FREI:
                frei.append(i)
                skala.append(self.FREI[kurz])
        return {'frei': np.array(frei, np.int32), 'frei_skala': np.array(skala, np.float32)}

    def _landmarken(self, nummer):
        """Die Landmarken-Tabelle (`G9netzlandmarken`, vom Detektor selbst kalibriert) als Arrays:
        Gelenke als Anker-Knochen + Versatz, Ferse/Zeh und die 478 Gesichtspunkte als Dreieck +
        Anteile. Ohne Tabelle kein Lauf — `Meshfigurlauf` kalibriert vorher."""
        from Genesis9.netzlandmarken import G9netzlandmarken

        tabelle = G9netzlandmarken.holen()
        if tabelle is None:
            raise RuntimeError('Landmarken-Tabelle fehlt (Schritt „kalibrierung")')
        d = tabelle.daten
        quelle, index, dreieck, bary = [], [], [], []
        for art, praefix in ((0, 'pose'), (1, 'gesicht')):
            for i in np.flatnonzero(d[praefix + '_dreieck'] >= 0):
                quelle.append(art)
                index.append(int(i))
                dreieck.append(int(d[praefix + '_dreieck'][i]))
                bary.append(d[praefix + '_bary'][i])
        knochen = [str(k) for k in d['gelenk_knochen']]
        return {
            'lm_gelenk_nummer': np.asarray(d['gelenk_nummer'], np.int32),
            'lm_gelenk_knochen': np.array([nummer[k] for k in knochen], np.int32),
            'lm_gelenk_versatz': np.asarray(d['gelenk_versatz'], np.float32),
            'lm_flaeche_quelle': np.array(quelle, np.int8),
            'lm_flaeche_nummer': np.array(index, np.int32),
            'lm_flaeche_dreieck': np.array(dreieck, np.int32),
            'lm_flaeche_bary': np.array(bary, np.float32).reshape(-1, 3),
        }

    # ---------------------------------------------------------------- JCMs

    def jcm(self, formung):
        """(N, 3) Meter: Deltas der Gelenkkorrekturen für `drehung` — 0 ohne Haltung."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
        from Genesis9.morphablage import G9morphablage

        n = len(G9basisnetz.holen().punkte)
        feld = np.zeros((n, 3))
        if not self.drehung:
            return feld
        werte = G9gelenkkorrekturen.werte(self.drehung, regler=G9gelenkkorrekturen.regler(formung))
        ablage = G9morphablage.holen()
        for name, wert in werte.items():
            paar = ablage.deltas(name)
            if paar is None:
                continue
            nummern, deltas = paar
            gueltig = nummern < n
            np.add.at(feld, nummern[gueltig], deltas[gueltig] * wert)
        self.jcm_werte = werte
        return feld
