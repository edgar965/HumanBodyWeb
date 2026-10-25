# -*- coding: utf-8 -*-
"""Mesh3daiflaeche — die Flächen von Ursula1 je Probe als Binärpaket für die Ansichtsarten der Seite „Mesh3D-AI" (15.10.2026).

Edgar: „wo ist die Umschaltung der Ansicht verschwunden auf Textur, Mesh usw?" — mit den echten Daten gab es bis dahin nur Punktwolke und Rig; die Knöpfe waren ausgeblendet. Jetzt liefert der Server je Probe die
gehäutete Figur (`proben/NNNN/flaeche.npz`, geschrieben von `ProjektTemp/_wegwerf/mesh3dai_ursula_flaechen.py`, nur zur Anzeige — das Training liest die Datei nicht): alle Dreiecke von Körper, Anatomie, Slip, Hose,
Shirt, vom Haar die sichtbaren; je Dreieck Teil (`etikett`) und ob es zur Außenfläche gehört (`aussen`, dieselbe Rechnung wie für `eingabe.npz`).

    Mesh3daiflaeche.paket(modell, nr) -> bytes | None

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, mit Leerzeichen auf ein Vielfaches von 4 aufgefüllt: {fassung, punkte, dreiecke, haut, teile, teilfarben}) · float32 punkte (V·3) · uint32 dreiecke (F·3)
· uint8 knochen (V·haut) · uint8 gewicht (V·haut) · uint8 etikett (F) · uint8 aussen (F). `haut` = Einflüsse je Punkt (Fassung 2; Fassung 1 hat keine Hautgewichte → 0): mit ihnen häutet die Seite die Figur
mit dem vorhergesagten Rig (Edgar: „im Ergebnis fenster werden 2 Rigs aber sonst nichts angezeigt“). Fehlt die Datei oder trägt sie eine unbekannte Fassung: `None` (die Seite zeigt dann die Punktwolke und sagt es).
"""

import json
import logging
import struct
import zipfile

import numpy as np

from .mesh3daidatensatz import Mesh3daidatensatz

logger = logging.getLogger('core')

__all__ = ['Mesh3daiflaeche']


class Mesh3daiflaeche:
    DATEI = 'flaeche.npz'
    #: Fassung 1 = ohne, Fassung 2 = mit Hautgewichten (`knochen`, `gewicht`); Fassung 3 (15.10.2026) = wie 2, `aussen` aus der berichtigten Sichtbarkeitsrechnung
    #: (pyrender-Tiefe bei orthografischer Kamera, `Ursula.SICHT_FASSUNG` 2 im Datenskript). Fassung 4 (15.10.2026) = nur `punkte_q` (int16 × `einheit_m`) und `aussen`; das Netz
    #: (volles Haar, UV, Material, Hautgewichte) steht einmal je Job in `anzeige/` (`Mesh3daiflaechennetz`).
    FASSUNGEN = (1, 2, 3, 4)
    #: Reihenfolge der Etiketten in `flaeche.npz` (= `Ursula.TEILE` im Datenskript).
    TEILE = ('koerper', 'anatomie', 'haar', 'slip', 'hose', 'hemd', 'augen')         # `augen` seit 24.10.2026 (Figuren der Tests, `Ursula.TEILE`)

    @classmethod
    def datei(cls, modell, nr):
        return Mesh3daidatensatz.ordner(modell) / 'proben' / ('%04d' % int(nr)) / cls.DATEI

    @classmethod
    def laden(cls, modell, nr):
        """Die Arrays der Probe oder `None` (Datei fehlt oder andere Fassung — dann mit Zeile im Log)."""
        datei = cls.datei(modell, nr)
        if not datei.is_file():
            return None
        try:
            with np.load(datei) as z:
                fassung = int(z['fassung'])
                if fassung not in cls.FASSUNGEN:
                    logger.warning('Mesh3daiflaeche: %s trägt Fassung %s (bekannt: %s) — nicht ausgeliefert', datei, fassung, cls.FASSUNGEN)
                    return None
                if fassung >= 4:
                    d = {'punkte_q': z['punkte_q'], 'einheit_m': float(z['einheit_m']), 'aussen': z['aussen']}
                else:
                    d = {k: z[k] for k in ('punkte', 'dreiecke', 'etikett', 'aussen', 'teilfarben')}
                    if fassung >= 2:
                        d['knochen'], d['gewicht'] = z['knochen'], z['gewicht']
                d['fassung'] = fassung
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as fehler:
            logger.warning('Mesh3daiflaeche: %s nicht lesbar (%s)', datei, fehler)
            return None
        if d['fassung'] >= 4:
            return cls._mit_netz(modell, d, datei)
        return d

    @staticmethod
    def _mit_netz(modell, d, datei):
        """Fassung 4: das gemeinsame Netz des Jobs dazu (`Mesh3daiflaechennetz`) — dieselben Schlüssel wie Fassung 2/3, damit die Animation (`Mesh3daiflaechenanimation`) unverändert liest."""
        from .mesh3daiflaechennetz import Mesh3daiflaechennetz

        netz = Mesh3daiflaechennetz.laden(modell)
        if netz is None or len(netz['uv']) != len(d['punkte_q']) or len(netz['dreiecke']) != len(d['aussen']):
            logger.warning('Mesh3daiflaeche: %s (Fassung 4) passt nicht zum Netz in anzeige/ (fehlt oder andere Größe) — nicht ausgeliefert', datei)
            return None
        d.update(punkte=d['punkte_q'].astype(np.float32) * np.float32(d['einheit_m']), dreiecke=netz['dreiecke'], etikett=netz['etikett'], teilfarben=netz['teilfarben'],
                 knochen=netz['knochen'], gewicht=netz['gewicht'], uv=netz['uv'], material=netz['material'])
        if 'ruhe' in netz:
            d['ruhe'] = netz['ruhe']
        return d

    @classmethod
    def paket(cls, modell, nr):
        d = cls.laden(modell, nr)
        if d is None:
            return None
        if d['fassung'] >= 4:
            # Nur Punkte und Außenfläche; das Netz holt die Seite EINMAL je Job (`…/flaeche/netz/`, `Mesh3daiflaechennetz.paket`).
            kopf = {'fassung': d['fassung'], 'punkte': int(len(d['punkte_q'])), 'dreiecke': int(len(d['aussen'])), 'einheit_m': d['einheit_m'], 'netz': True}
            text = json.dumps(kopf).encode('utf-8')
            text += b' ' * (-len(text) % 4)
            punkte = d['punkte_q'].astype('<i2').tobytes()
            punkte += b'\0' * (-len(punkte) % 4)
            return b''.join([struct.pack('<I', len(text)), text, punkte, d['aussen'].astype(np.uint8).tobytes()])
        haut = int(d['knochen'].shape[1]) if 'knochen' in d else 0
        kopf = {'fassung': d['fassung'], 'punkte': int(len(d['punkte'])), 'dreiecke': int(len(d['dreiecke'])), 'haut': haut, 'teile': list(cls.TEILE),
                'teilfarben': d['teilfarben'].astype(int).tolist()}
        text = json.dumps(kopf).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        teile = [struct.pack('<I', len(text)), text, d['punkte'].astype('<f4').tobytes(), d['dreiecke'].astype('<u4').tobytes()]
        if haut:
            teile += [d['knochen'].astype(np.uint8).tobytes(), d['gewicht'].astype(np.uint8).tobytes()]
        teile += [d['etikett'].astype(np.uint8).tobytes(), d['aussen'].astype(np.uint8).tobytes()]
        return b''.join(teile)
