# -*- coding: utf-8 -*-
"""Meshfigurobjektfelder — Daz' Gelenkkorrekturen (JCMs) für die Objekte aus dem Netz (14.10.2026).

Edgar: „JCM (Gelenkkorrekturen) - warum wendest du die denn nicht an?? das mesh-3d sollte wie Charakter / Studio sein!" In Charakter und Studio verformt der Browser die Haut je Bild mit den Korrekturen der Knochenwinkel (`Genesis9gelenke`);
der Stoff folgt dort mit eigenen Feldern (Daz' Auto-Follow, `G9stueckfelder`). In Mesh-3D sind Kleidung, Haar und Bestandteile aber GLB-Objekte aus dem Netz, keine Stücke der Garderobe — ihr Feld kommt hier aus den Verschiebungen des KÄFIGS
(`Meshfigurkaefigfelder`), und zwar dort, wo das Objekt anliegt::

    feld(objekt, p) = λ(d) · Σₖ wₖ · feld(kaefig, nₖ)        nₖ: die `NACHBARN` nächsten Käfigpunkte in der Ruhelage, wₖ ~ exp(−(dₖ² − d₀²) / 2σ²)

`λ` ist `Kleidunghautgewichte.naehe` (1 bis 2 cm Abstand zum Käfig, 0 ab 5 cm — dieselbe Grenze, bis zu der der Stoff die Gewichte der Haut übernimmt): was anliegt, bewegt sich mit der korrigierten Haut, was weit absteht (Robe, Rock), folgt
nur dem Skelett — wie vorher. Ein Objekt, das ganz an EINEM Knochen hängt (Stab, Bart, Tasche, Haar am Kopf: `Hautdatei`, ein Knochen mit Gewicht 1), bekommt kein Feld: ein starrer Gegenstand verformt sich nicht.

Ergebnis `{kanal: (nummern uint32, deltas float32 (n, 3))}` auf den Punkten der GLB (Reihenfolge der Datei = Reihenfolge der Hautdatei), im selben Format wie die Felder der Stücke (`Genesis9felder.anwenden`). Abgelegt neben den Arbeitsdateien des Laufs
(`arbeit/objektfelder_<datei>.npz/.json`), gültig, solange GLB, Hautdatei, Käfig und Morphdateien dieselben sind.
"""

import json
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurobjektfelder']


class Meshfigurobjektfelder:
    FASSUNG = 1
    GRUPPE = 'gelenke'
    #: Käfig-Nachbarn je Punkt und ihre Breite σ (m). Die Verschiebungen sind auf Zellen von 1–2 cm glatt; σ 1 cm lässt bei anliegendem Stoff die Zelle darunter zählen (eine Setzung, nicht gemessen gegen eine Wahrheit).
    NACHBARN = 6
    SIGMA_M = 0.01
    #: Darunter zählt ein Punkt nicht als bewegt (0,1 mm; die Felder der Haut nehmen 0,01 mm). Die Gelenkkorrekturen bewegen höchstens zwei bis drei Zentimeter — 0,1 mm ist unsichtbar und spart die langen Ausläufer.
    SCHWELLE_M = 1e-4

    def __init__(self, ablage):
        self.ablage = ablage

    # ---------------------------------------------------------------- holen

    def holen(self, datei):
        """`{kanal: (nummern, deltas)}` der GLB `datei` im Ergebnisordner — leer, wenn das Objekt starr ist oder keine Hautdatei hat; `ValueError` bei einem Namen, den es nicht gibt."""
        from Kleidung.hautdatei import Hautdatei

        pfad = self.ablage.datei('ergebnis', datei)
        if pfad.suffix.lower() != '.glb' or not pfad.is_file():
            raise ValueError('Keine GLB: %s' % datei)
        haut, ende = Path(Hautdatei.pfad(pfad)), self.ablage.arbeit('genesis_ende.npz')
        if not haut.is_file() or not ende.is_file():
            return {}
        marke = self._marke(pfad, haut, ende)
        felder = self._aus_ablage(datei, marke)
        if felder is None:
            felder = self.rechnen(pfad, haut, ende)
            self._ablegen(datei, marke, felder)
        return felder

    def rechnen(self, pfad, haut, ende):
        from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
        from Kleidung.hautdatei import Hautdatei

        from .meshfigurkaefigfelder import Meshfigurkaefigfelder
        from .mesh3dglbschnitt import Mesh3dglbschnitt

        index, gewicht = Hautdatei.lesen(haut)
        if self.starr(index, gewicht):
            return {}
        punkte = Mesh3dglbschnitt.punkte(pfad)
        if len(punkte) != len(index):
            raise ValueError('%d Punkte in der GLB, %d in der Hautdatei' % (len(punkte), len(index)))
        with np.load(ende) as d:
            kaefig = np.asarray(d['punkte'], dtype=np.float64)
        zeilen, nachbar, mischung = self.nachbarschaft(punkte, kaefig)
        if not len(zeilen):
            return {}
        return self.uebertragen(Meshfigurkaefigfelder.holen(self.GRUPPE, G9gelenkkorrekturen.graph()['morphe']), len(kaefig), zeilen, nachbar, mischung)

    @staticmethod
    def starr(index, gewicht):
        """Hängt jeder Punkt mit Gewicht 255 am selben Knochen (`Hautdatei.starr`)?"""
        return bool(len(index) and len(np.unique(index[:, 0])) == 1 and (np.asarray(gewicht)[:, 0] == 255).all())

    # ------------------------------------------------------------- Rechnung

    @classmethod
    def nachbarschaft(cls, punkte, kaefig):
        """`(zeilen, nachbar, mischung)` — die Punkte des Objekts, die dem Käfig nahe genug liegen, ihre `NACHBARN` nächsten Käfigpunkte (Ruhelage) und die Gewichte (Summe = λ des Abstands, also 0 … 1)."""
        from scipy.spatial import cKDTree

        from Kleidung.kleidunghautgewichte import Kleidunghautgewichte

        abstand, nachbar = cKDTree(kaefig).query(punkte, k=min(cls.NACHBARN, len(kaefig)), workers=-1)
        lam = Kleidunghautgewichte.naehe(abstand[:, 0])
        zeilen = np.flatnonzero(lam > 0)
        abstand, nachbar, lam = abstand[zeilen], nachbar[zeilen], lam[zeilen]
        w = np.exp(-0.5 * (abstand ** 2 - abstand[:, :1] ** 2) / cls.SIGMA_M ** 2) + 1e-9
        return zeilen, nachbar, w / w.sum(axis=1, keepdims=True) * lam[:, None]

    @classmethod
    def uebertragen(cls, kaefigfelder, anzahl, zeilen, nachbar, mischung):
        """Die Felder des Käfigs auf die Punkte `zeilen` des Objekts — je Kanal nur Punkte, deren Nachbarn sich bewegen und die mehr als `SCHWELLE_M` wandern."""
        dicht = np.zeros((anzahl, 3), dtype=np.float32)
        betroffen = np.zeros(anzahl, dtype=bool)
        aus = {}
        for kanal, (nummern, deltas) in kaefigfelder.items():
            dicht[nummern] = deltas
            betroffen[nummern] = True
            wahl = np.flatnonzero(betroffen[nachbar].any(axis=1))
            if len(wahl):
                werte = np.einsum('mk,mkc->mc', mischung[wahl], dicht[nachbar[wahl]])
                stark = np.abs(werte).max(axis=1) > cls.SCHWELLE_M
                if stark.any():
                    aus[kanal] = (zeilen[wahl[stark]].astype(np.uint32), werte[stark].astype(np.float32))
            dicht[nummern] = 0.0
            betroffen[nummern] = False
        return aus

    # --------------------------------------------------------------- Ablage

    def _marke(self, pfad, haut, ende):
        from Genesis9.morphablage import G9morphablage

        def stand(p):
            s = Path(p).stat()
            return [s.st_size, s.st_mtime_ns]

        return {'fassung': self.FASSUNG, 'glb': stand(pfad), 'haut': stand(haut), 'ende': stand(ende), 'bestand': G9morphablage.bestandsschluessel()}

    def _ablage_pfade(self, datei):
        stamm = Path(datei).stem
        return self.ablage.arbeit('objektfelder_%s.json' % stamm), self.ablage.arbeit('objektfelder_%s.npz' % stamm)

    def _ablegen(self, datei, marke, felder):
        json_pfad, npz_pfad = self._ablage_pfade(datei)
        arrays = {}
        for nummer, (nummern, deltas) in enumerate(felder.values()):
            arrays['n%d' % nummer] = nummern
            arrays['d%d' % nummer] = deltas
        try:
            np.savez(npz_pfad, **arrays)
            with open(json_pfad, 'w', encoding='utf-8') as ziel:          # der Kopf zuletzt: er gilt erst, wenn die Felder da sind
                json.dump({'marke': marke, 'kanaele': list(felder)}, ziel)
        except (OSError, TypeError, ValueError) as fehler:
            logger.warning('Objektfelder %s nicht schreibbar: %s', datei, fehler)

    def _aus_ablage(self, datei, marke):
        json_pfad, npz_pfad = self._ablage_pfade(datei)
        if not json_pfad.is_file() or not npz_pfad.is_file():
            return None
        try:
            with open(json_pfad, encoding='utf-8') as quelle:
                kopf = json.load(quelle)
            if kopf.get('marke') != marke:
                return None
            with np.load(npz_pfad, allow_pickle=False) as d:
                return {kanal: (d['n%d' % nummer], d['d%d' % nummer]) for nummer, kanal in enumerate(kopf['kanaele'])}
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Objektfelder %s unlesbar (%s), werden neu gerechnet', datei, fehler)
            return None
