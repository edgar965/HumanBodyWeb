# -*- coding: utf-8 -*-
"""Meshfigurkaefigfelder — die Verschiebung je Regler auf Daz' KÄFIGPUNKTEN (14.10.2026).

Edgar: „JCM (Gelenkkorrekturen) - warum wendest du die denn nicht an?? das mesh-3d sollte wie Charakter / Studio sein!" `G9reglerfelder` legt die Felder der Gelenkkorrekturen auf die BROWSERPUNKTE einer Stufe (Matrix der Unterteilung).
Die Objekte aus dem Netz in Mesh-3D (Kleidung, Haar, Bestandteile) haben keine Browserpunkte der Figur — sie bekommen ihr Feld aus den Verschiebungen des KÄFIGS dort, wo sie anliegen (`Meshfigurobjektfelder`). Dafür dieselben
Verschiebungen ohne Matrix::

    feld(r) = morphpunkte({r: 1}) − basis            (Meter, auf den 25.182 Punkten des Daz-Käfigs)

Wie `G9reglerfelder` dünn abgelegt (`Genesis9/ablage/kaefigfelder_<gruppe>_f<FASSUNG>.npz` + `.json`, Bestand der Morphdateien im Kopf, der Kopf wird zuletzt geschrieben): `{kanal: (Nummern uint32, Deltas float32 (n, 3))}`, nur Kanäle, die sich bewegen.
Hier und nicht in `Genesis9/`: jede Änderung dort entwertet die Antwort- und Frisurenablagen (`meshfigur-tempo.md`).
"""

import json
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurkaefigfelder']


class Meshfigurkaefigfelder:
    FASSUNG = 1
    _gemerkt = {}

    @classmethod
    def holen(cls, gruppe, kanaele):
        """`{kanal: (nummern uint32, deltas float32 (n, 3))}` der Gruppe auf dem Käfig."""
        from Genesis9.morphablage import G9morphablage

        kanaele = list(kanaele)
        schluessel = (str(gruppe), tuple(kanaele), G9morphablage.bestandsschluessel())
        felder = cls._gemerkt.get(schluessel)
        if felder is None:
            felder = cls._aus_ablage(gruppe, kanaele)
            if felder is None:
                felder = cls.rechnen(kanaele)
                cls._ablegen(gruppe, kanaele, felder)
            cls._gemerkt = {schluessel: felder}
        return felder

    @classmethod
    def rechnen(cls, kanaele):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.reglerfelder import G9reglerfelder

        basis = G9basisnetz.holen().punkte
        aus = {}
        for kanal in kanaele:
            nummern, deltas = G9reglerfelder.duenn(G9formung({kanal: 1.0}).morphpunkte() - basis)
            if len(nummern):
                aus[kanal] = (nummern, deltas)
        return aus

    # --------------------------------------------------------------- Ablage

    @classmethod
    def pfad(cls, gruppe, endung):
        from Genesis9.pfade import G9pfade

        return G9pfade.ablage() / ('kaefigfelder_%s_f%d.%s' % (gruppe, cls.FASSUNG, endung))

    @classmethod
    def _ablegen(cls, gruppe, kanaele, felder):
        from Genesis9.morphablage import G9morphablage
        from Genesis9.pfade import G9pfade

        kopf = {'fassung': cls.FASSUNG, 'bestand': G9morphablage.bestandsschluessel(), 'kanaele': kanaele, 'mit_feld': list(felder)}
        arrays = {}
        for nummer, (nummern, deltas) in enumerate(felder.values()):
            arrays['n%d' % nummer] = nummern
            arrays['d%d' % nummer] = deltas
        try:
            G9pfade.ablage().mkdir(parents=True, exist_ok=True)
            np.savez(cls.pfad(gruppe, 'npz'), **arrays)
            with open(cls.pfad(gruppe, 'json'), 'w', encoding='utf-8') as datei:      # der Kopf zuletzt: er gilt erst, wenn die Felder da sind
                json.dump(kopf, datei)
        except (OSError, TypeError, ValueError) as fehler:
            logger.warning('Käfigfelder %s nicht schreibbar: %s', gruppe, fehler)

    @classmethod
    def _aus_ablage(cls, gruppe, kanaele):
        from Genesis9.morphablage import G9morphablage

        json_pfad, npz_pfad = cls.pfad(gruppe, 'json'), cls.pfad(gruppe, 'npz')
        if not json_pfad.is_file() or not npz_pfad.is_file():
            return None
        try:
            with open(json_pfad, encoding='utf-8') as datei:
                kopf = json.load(datei)
            if (kopf.get('fassung') != cls.FASSUNG or kopf.get('bestand') != G9morphablage.bestandsschluessel()
                    or list(kopf.get('kanaele') or []) != list(kanaele)):
                return None
            with np.load(npz_pfad, allow_pickle=False) as d:
                return {kanal: (d['n%d' % nummer], d['d%d' % nummer]) for nummer, kanal in enumerate(kopf['mit_feld'])}
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Käfigfelder %s unlesbar (%s), werden neu gerechnet', gruppe, fehler)
            return None
