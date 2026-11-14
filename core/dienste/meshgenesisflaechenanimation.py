# -*- coding: utf-8 -*-
"""Meshgenesisflaechenanimation — die Flächen ALLER Bilder der Bewegung (Spagat) in einem Paket, damit Play auf der Seite „Mesh-Genesis" die gehäutete Figur zeigt (15.10.2026, Edgar: „fixe alles").

Je Probe liegt `flaeche.npz` (`Meshgenesisflaeche`, rund 2,7 MB je Bild im Paket) — 125 Einzelabrufe während Play kämen nicht hinterher. Hier deshalb EIN Paket mit fester Verbindung:
die Dreiecke von Körper, Anatomie, Slip, Hose und Shirt sind in jedem Bild dieselben (nur die Lage ändert sich), das Haar fehlt (welche Haardreiecke sichtbar sind, wechselt von Bild zu Bild; ohne sie
wäre die Verbindung nicht fest). Die Lage geht als int16 in Zehntelmillimetern, die Außenfläche je Bild als Bitfeld.

    Meshgenesisflaechenanimation.paket(modell, nummern) -> bytes | None     (nummern = Proben in der Reihenfolge der Bilder)

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf 4 aufgefüllt: {bilder, punkte, dreiecke, haut, einheit_m, teile, teilfarben}) · uint32 dreiecke (F·3) · int16 lage (Bilder·V·3)
· uint8 knochen (V·haut) · uint8 gewicht (V·haut) · uint8 etikett (F) · uint8 aussen (Bilder · ⌈F/8⌉, `np.packbits`, höchstes Bit zuerst) · mit `textur` im Kopf (Flächen der Fassung 4)
dahinter, auf 4 aufgefüllt: float32 uv (V·2) · int16 material (F) · mit `ruhe` im Kopf (16.10.2026) dahinter, auf 4 aufgefüllt: float32 ruhe (V·3), die Punkte in der Ruhelage
(`Meshgenesisflaechennetz`) — damit häutet die Seite das Ergebnis eines Laufs mit Daz-Winkeln auch beim Abspielen genau.
`None`, wenn ein Bild keine Fläche der Fassung 2 hat oder die Verbindung zwischen den Bildern abweicht (beides mit Zeile im Log). Zwischengespeichert je Stand der Dateien.
"""

import json
import logging
import struct

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .meshgenesisflaeche import Meshgenesisflaeche

logger = logging.getLogger('core')

__all__ = ['Meshgenesisflaechenanimation']


class Meshgenesisflaechenanimation:
    EINHEIT_M = 1e-4
    _ablage = {}

    @classmethod
    def paket(cls, modell, nummern):
        dateien = [Meshgenesisflaeche.datei(modell, nr) for nr in nummern]
        if not dateien or not all(d.is_file() for d in dateien):
            logger.warning('Meshgenesisflaechenanimation: %d von %d Bildern ohne flaeche.npz', sum(1 for d in dateien if not d.is_file()), len(dateien))
            return None
        from .meshgenesisflaechennetz import Meshgenesisflaechennetz

        # Mit dem Stand des gemeinsamen Netzes (Fassung 4 liest Hautgewichte, UV und Ruhelage von dort).
        stand = tuple((str(d), d.stat().st_mtime_ns) for d in dateien) + (Meshgenesisflaechennetz._stand(Meshgenesisflaechennetz.ordner(modell)),)
        # Je Datensatz EIN Paket (rund 40 MB; seit Ursula_Pose1 zwei Jobs — ein gemeinsamer Platz baute bei jedem Wechsel 18 s neu).
        gemerkt = cls._ablage.get(str(modell))
        if gemerkt is None or gemerkt['stand'] != stand:
            cls._ablage[str(modell)] = gemerkt = {'stand': stand, 'paket': cls._bauen(modell, nummern)}
        return gemerkt['paket']

    @classmethod
    def _bauen(cls, modell, nummern):
        haar = Meshgenesisflaeche.TEILE.index('haar')
        verbindung = ecken = kopf_daten = None
        lagen, aussen = [], []
        for nr in nummern:
            d = Meshgenesisflaeche.laden(modell, nr)
            if d is None or 'knochen' not in d:
                logger.warning('Meshgenesisflaechenanimation: Probe %s ohne Fläche der Fassung 2 — Play zeigt keine Flächen', nr)
                return None
            ohne_haar = d['etikett'] != haar
            f = d['dreiecke'][ohne_haar]
            e = Torchfeld.unique(f)
            v = Torchfeld.astype(Torchfeld.searchsorted(e, f), torch.uint32)
            if verbindung is None:
                verbindung, ecken = v, len(e)
                kopf_daten = {'etikett': d['etikett'][ohne_haar], 'knochen': d['knochen'][e], 'gewicht': d['gewicht'][e], 'teilfarben': d['teilfarben']}
                if 'uv' in d:
                    # Fassung 4: UV und Material des gemeinsamen Netzes (`Meshgenesisflaechennetz`) — „Textur" zeigt beim Abspielen dieselben Bilder wie bei einer Probe.
                    kopf_daten.update(uv=d['uv'][e], material=d['material'][ohne_haar])
                if 'ruhe' in d:
                    kopf_daten['ruhe'] = d['ruhe'][e]
            elif len(e) != ecken or not Torchfeld.equal(v, verbindung):
                logger.warning('Meshgenesisflaechenanimation: Probe %s hat eine andere Verbindung als das erste Bild — Play zeigt keine Flächen', nr)
                return None
            p = d['punkte'][e]
            if Torchfeld.abs(p).max() >= 32767 * cls.EINHEIT_M:
                logger.warning('Meshgenesisflaechenanimation: Probe %s liegt außerhalb ±3,27 m — Play zeigt keine Flächen', nr)
                return None
            lagen.append(Torchfeld.astype(Torchfeld.round(p / cls.EINHEIT_M), Torchfeld.dtype('<i2')))
            aussen.append(Torchfeld.packbits(Torchfeld.astype(d['aussen'][ohne_haar], torch.bool)))
        haut = int(kopf_daten['knochen'].shape[1])
        textur = 'uv' in kopf_daten
        kopf = {'bilder': len(nummern), 'punkte': int(ecken), 'dreiecke': int(len(verbindung)), 'haut': haut, 'einheit_m': cls.EINHEIT_M, 'teile': list(Meshgenesisflaeche.TEILE),
                'teilfarben': Torchfeld.astype(kopf_daten['teilfarben'], torch.int64).tolist(), 'textur': textur, 'ruhe': 'ruhe' in kopf_daten}
        text = json.dumps(kopf).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        teile = [struct.pack('<I', len(text)), text, Torchfeld.als_bytes(Torchfeld.astype(verbindung, Torchfeld.dtype('<u4'))), Torchfeld.als_bytes(Torchfeld.cat(lagen)),
                 Torchfeld.als_bytes(Torchfeld.astype(kopf_daten['knochen'], torch.uint8)), Torchfeld.als_bytes(Torchfeld.astype(kopf_daten['gewicht'], torch.uint8)),
                 Torchfeld.als_bytes(Torchfeld.astype(kopf_daten['etikett'], torch.uint8)), Torchfeld.als_bytes(Torchfeld.cat(aussen))]
        if textur:
            # Hinter dem Bitfeld, auf 4 aufgefüllt: float32 uv (V·2) · int16 material (F).
            laenge = sum(len(t) for t in teile)
            teile += [b'\0' * (-laenge % 4), Torchfeld.als_bytes(Torchfeld.astype(kopf_daten['uv'], Torchfeld.dtype('<f4'))), Torchfeld.als_bytes(Torchfeld.astype(kopf_daten['material'], Torchfeld.dtype('<i2')))]
        if 'ruhe' in kopf_daten:
            laenge = sum(len(t) for t in teile)
            teile += [b'\0' * (-laenge % 4), Torchfeld.als_bytes(Torchfeld.astype(kopf_daten['ruhe'], Torchfeld.dtype('<f4')))]
        return b''.join(teile)
