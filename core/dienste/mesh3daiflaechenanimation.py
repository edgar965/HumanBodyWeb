# -*- coding: utf-8 -*-
"""Mesh3daiflaechenanimation — die Flächen ALLER Bilder der Bewegung (Spagat) in einem Paket, damit Play auf der Seite „Mesh3D-AI" die gehäutete Figur zeigt (15.10.2026, Edgar: „fixe alles").

Je Probe liegt `flaeche.npz` (`Mesh3daiflaeche`, rund 2,7 MB je Bild im Paket) — 125 Einzelabrufe während Play kämen nicht hinterher. Hier deshalb EIN Paket mit fester Verbindung:
die Dreiecke von Körper, Anatomie, Slip, Hose und Shirt sind in jedem Bild dieselben (nur die Lage ändert sich), das Haar fehlt (welche Haardreiecke sichtbar sind, wechselt von Bild zu Bild; ohne sie
wäre die Verbindung nicht fest). Die Lage geht als int16 in Zehntelmillimetern, die Außenfläche je Bild als Bitfeld.

    Mesh3daiflaechenanimation.paket(modell, nummern) -> bytes | None     (nummern = Proben in der Reihenfolge der Bilder)

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf 4 aufgefüllt: {bilder, punkte, dreiecke, haut, einheit_m, teile, teilfarben}) · uint32 dreiecke (F·3) · int16 lage (Bilder·V·3)
· uint8 knochen (V·haut) · uint8 gewicht (V·haut) · uint8 etikett (F) · uint8 aussen (Bilder · ⌈F/8⌉, `np.packbits`, höchstes Bit zuerst) · mit `textur` im Kopf (Flächen der Fassung 4)
dahinter, auf 4 aufgefüllt: float32 uv (V·2) · int16 material (F) · mit `ruhe` im Kopf (16.10.2026) dahinter, auf 4 aufgefüllt: float32 ruhe (V·3), die Punkte in der Ruhelage
(`Mesh3daiflaechennetz`) — damit häutet die Seite das Ergebnis eines Laufs mit Daz-Winkeln auch beim Abspielen genau.
`None`, wenn ein Bild keine Fläche der Fassung 2 hat oder die Verbindung zwischen den Bildern abweicht (beides mit Zeile im Log). Zwischengespeichert je Stand der Dateien.
"""

import json
import logging
import struct

import numpy as np

from .mesh3daiflaeche import Mesh3daiflaeche

logger = logging.getLogger('core')

__all__ = ['Mesh3daiflaechenanimation']


class Mesh3daiflaechenanimation:
    EINHEIT_M = 1e-4
    _ablage = {}

    @classmethod
    def paket(cls, modell, nummern):
        dateien = [Mesh3daiflaeche.datei(modell, nr) for nr in nummern]
        if not dateien or not all(d.is_file() for d in dateien):
            logger.warning('Mesh3daiflaechenanimation: %d von %d Bildern ohne flaeche.npz', sum(1 for d in dateien if not d.is_file()), len(dateien))
            return None
        from .mesh3daiflaechennetz import Mesh3daiflaechennetz

        # Mit dem Stand des gemeinsamen Netzes (Fassung 4 liest Hautgewichte, UV und Ruhelage von dort).
        stand = tuple((str(d), d.stat().st_mtime_ns) for d in dateien) + (Mesh3daiflaechennetz._stand(Mesh3daiflaechennetz.ordner(modell)),)
        # Je Datensatz EIN Paket (rund 40 MB; seit Ursula_Pose1 zwei Jobs — ein gemeinsamer Platz baute bei jedem Wechsel 18 s neu).
        gemerkt = cls._ablage.get(str(modell))
        if gemerkt is None or gemerkt['stand'] != stand:
            cls._ablage[str(modell)] = gemerkt = {'stand': stand, 'paket': cls._bauen(modell, nummern)}
        return gemerkt['paket']

    @classmethod
    def _bauen(cls, modell, nummern):
        haar = Mesh3daiflaeche.TEILE.index('haar')
        verbindung = ecken = kopf_daten = None
        lagen, aussen = [], []
        for nr in nummern:
            d = Mesh3daiflaeche.laden(modell, nr)
            if d is None or 'knochen' not in d:
                logger.warning('Mesh3daiflaechenanimation: Probe %s ohne Fläche der Fassung 2 — Play zeigt keine Flächen', nr)
                return None
            ohne_haar = d['etikett'] != haar
            f = d['dreiecke'][ohne_haar]
            e = np.unique(f)
            v = np.searchsorted(e, f).astype(np.uint32)
            if verbindung is None:
                verbindung, ecken = v, len(e)
                kopf_daten = {'etikett': d['etikett'][ohne_haar], 'knochen': d['knochen'][e], 'gewicht': d['gewicht'][e], 'teilfarben': d['teilfarben']}
                if 'uv' in d:
                    # Fassung 4: UV und Material des gemeinsamen Netzes (`Mesh3daiflaechennetz`) — „Textur" zeigt beim Abspielen dieselben Bilder wie bei einer Probe.
                    kopf_daten.update(uv=d['uv'][e], material=d['material'][ohne_haar])
                if 'ruhe' in d:
                    kopf_daten['ruhe'] = d['ruhe'][e]
            elif len(e) != ecken or not np.array_equal(v, verbindung):
                logger.warning('Mesh3daiflaechenanimation: Probe %s hat eine andere Verbindung als das erste Bild — Play zeigt keine Flächen', nr)
                return None
            p = d['punkte'][e]
            if np.abs(p).max() >= 32767 * cls.EINHEIT_M:
                logger.warning('Mesh3daiflaechenanimation: Probe %s liegt außerhalb ±3,27 m — Play zeigt keine Flächen', nr)
                return None
            lagen.append(np.round(p / cls.EINHEIT_M).astype('<i2'))
            aussen.append(np.packbits(d['aussen'][ohne_haar].astype(bool)))
        haut = int(kopf_daten['knochen'].shape[1])
        textur = 'uv' in kopf_daten
        kopf = {'bilder': len(nummern), 'punkte': int(ecken), 'dreiecke': int(len(verbindung)), 'haut': haut, 'einheit_m': cls.EINHEIT_M, 'teile': list(Mesh3daiflaeche.TEILE),
                'teilfarben': kopf_daten['teilfarben'].astype(int).tolist(), 'textur': textur, 'ruhe': 'ruhe' in kopf_daten}
        text = json.dumps(kopf).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        teile = [struct.pack('<I', len(text)), text, verbindung.astype('<u4').tobytes(), np.concatenate(lagen).tobytes(),
                 kopf_daten['knochen'].astype(np.uint8).tobytes(), kopf_daten['gewicht'].astype(np.uint8).tobytes(),
                 kopf_daten['etikett'].astype(np.uint8).tobytes(), np.concatenate(aussen).tobytes()]
        if textur:
            # Hinter dem Bitfeld, auf 4 aufgefüllt: float32 uv (V·2) · int16 material (F).
            laenge = sum(len(t) for t in teile)
            teile += [b'\0' * (-laenge % 4), kopf_daten['uv'].astype('<f4').tobytes(), kopf_daten['material'].astype('<i2').tobytes()]
        if 'ruhe' in kopf_daten:
            laenge = sum(len(t) for t in teile)
            teile += [b'\0' * (-laenge % 4), kopf_daten['ruhe'].astype('<f4').tobytes()]
        return b''.join(teile)
