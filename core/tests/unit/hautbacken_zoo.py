# -*- coding: utf-8 -*-
"""Hautbackenzoo — die Prüfwerkstatt des lokalen Backers gegen Blender: viele kleine Materialien (`hautbacken_zoo_materialien.py`), die Blender selbst bäckt (`hautbacken_zoo_blender.py`)
und der lokale Backer (`core/dienste/hautbacken/graph`) nachrechnet. Die Ergebnisse je Material stehen nebeneinander (Mittel, p99 und größte Abweichung in Stufen von 255, auf den Texeln, die
das Material trifft, ohne die Randtexel zum Nachbarmaterial).

    zoo = Hautbackenzoo(ordner, px=256)
    zoo.vorbereiten()                 # Szene, Bilder (einmal)
    zoo.blender_satz(0)               # Blender backt Satz 0 (acht Materialien) — nur zum (Neu-)Erzeugen der Golden-Sätze
    zoo.vergleichen(0)                # lokal rechnen und vergleichen: [{'name', 'farbe': {...}, 'rauheit': {...}, 'normalen': {...}}]
"""

import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from core.dienste.hautbacken import Hautbackenquelle
from core.dienste.hautbacken.graph import Hautbackengraph, Hautgraph, Hautschattungbau
from core.tests.unit.hautbacken_szene import Hautbackenszene
from core.tests.unit.hautbacken_zoo_materialien import definitionen

__all__ = ['Hautbackenzoo']

BLENDER = r'A:\3DTools\tools\blender-5.2.2-windows-x64\blender.exe'
HIER = Path(__file__).resolve().parent


class Hautbackenzoo:
    KANAELE = ('farbe', 'rauheit', 'normalen')

    def __init__(self, ordner, px=256, je_satz=8, geraet='GPU'):
        """`geraet`: womit Blender die Vergleichsbilder backt — 'GPU' (wie der Import) oder 'CPU' (ohne die Rundung der GPU-Texturhardware, Ordner `ergebnis_cpu`)."""
        self.ordner, self.px, self.je_satz, self.geraet = Path(ordner), px, je_satz, geraet

    def saetze(self):
        return (len(definitionen()) + self.je_satz - 1) // self.je_satz

    # ------------------------------------------------------------------ Eingabe

    def vorbereiten(self):
        """Szene (Körper-Kappe mit zweiter UV, Figur-Kachel, Ruhelage), Bilder und `szene.json`."""
        szene = Hautbackenszene(self.px)
        szene.schreiben(self.ordner)
        q = szene.quelle()
        uv = q.uv_ecken
        uv2 = np.stack([0.9 - 0.8 * uv[..., 1], 0.1 + 0.7 * uv[..., 0]], axis=-1)
        np.savez(self.ordner / 'szene.npz', punkte=q.punkte, dreiecke=q.dreiecke, uv_ecken=uv, uv2_ecken=uv2)
        bilder = self.ordner / 'bilder'
        bilder.mkdir(exist_ok=True)
        for name, feld in self.bilder().items():
            self.bild_schreiben(bilder / (name + '.png'), feld)
        return self.ordner

    @staticmethod
    def bild_schreiben(pfad, feld):
        """Ein PNG; 16 Bit je Kanal schreibt OpenCV (Pillow kann kein 16-Bit-RGB)."""
        if feld.dtype == np.uint16:
            bgr = feld if feld.ndim == 2 else np.concatenate([feld[..., 2::-1], feld[..., 3:]], axis=-1)
            ok, puffer = cv2.imencode('.png', bgr)
            if not ok:
                raise RuntimeError('PNG nicht zu schreiben: %s' % pfad)
            Path(pfad).write_bytes(puffer.tobytes())
        else:
            Image.fromarray(feld).save(pfad, optimize=True)

    @staticmethod
    def bilder(n=512):
        """Die Eingangsbilder: `farbe`, `grau` (RGB-Grau), `alpha` (RGBA), `grau1` (ein Kanal), `rgb3` (drei Kanäle), `hoehe`, `normal` — und mit 16 Bit je Kanal `farbe16` (RGB),
        `alpha16` (RGBA), `grau16` (ein Kanal), deren niedrige Bits etwas tragen (ein 8-Bit-Bild hätte sie nicht)."""
        basis = Hautbackenszene(256).bilder()
        v, u = np.meshgrid(1 - (np.arange(n) + 0.5) / n, (np.arange(n) + 0.5) / n, indexing='ij')
        tau = 2 * np.pi
        zu8 = lambda a: np.clip(a + 0.5, 0, 255).astype(np.uint8)                   # noqa: E731
        farbe = basis['farbe']
        alpha_kanal = 40 + 215 * (0.5 + 0.5 * np.sin(tau * (1.3 * u + 0.7 * v)))
        alpha = np.concatenate([zu8(farbe * 0.7 + np.array([40, 30, 20])), zu8(alpha_kanal)[..., None]], axis=-1)
        rgb3 = zu8(np.stack([128 + 100 * np.sin(tau * 3 * u), 128 + 100 * np.cos(tau * 2 * v), 128 + 100 * np.sin(tau * (u + v))], axis=-1))
        hoehe = zu8(np.stack([128 + 100 * np.sin(tau * 4 * u) * np.cos(tau * 3 * v)] * 3, axis=-1))
        fein = (60.0 + 55.0 * np.sin(tau * (7 * u + 5 * v)))[..., None] * np.array([1.0, 0.7, 0.4])
        farbe16 = np.clip(farbe.astype(np.float64) * 257.0 + fein, 0, 65535).astype(np.uint16)
        alpha_kanal16 = np.clip(alpha_kanal * 257.0 + 90.0 * np.sin(tau * (9 * u - 4 * v)), 0, 65535).astype(np.uint16)
        alpha16 = np.concatenate([np.clip(alpha[..., :3].astype(np.float64) * 257.0 + fein, 0, 65535).astype(np.uint16), alpha_kanal16[..., None]], axis=-1)
        grau16 = np.clip((0.5 + 0.5 * np.sin(tau * (3 * u + 2 * v))) * 65535.0 + 300.0 * np.cos(tau * 11 * u), 0, 65535).astype(np.uint16)
        return {'farbe': farbe, 'grau': basis['rauheit'], 'alpha': alpha, 'grau1': basis['rauheit'][..., 0], 'rgb3': rgb3, 'hoehe': hoehe, 'normal': basis['normalen'],
                'farbe16': farbe16, 'alpha16': alpha16, 'grau16': grau16}

    # ------------------------------------------------------------------ Blender

    def blender_satz(self, satz):
        """Blender backt Satz `satz` (nur zum Erzeugen des Golden-Satzes)."""
        r = subprocess.run([BLENDER, '-b', '--factory-startup', '--python', str(HIER / 'hautbacken_zoo_blender.py'), '--', str(self.ordner), str(satz), str(self.je_satz), self.geraet],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode or 'Traceback' in r.stdout or 'Traceback' in r.stderr:
            raise RuntimeError('Blender-Satz %d: Exitcode %d\n%s\n%s' % (satz, r.returncode, r.stdout[-3000:], r.stderr[-2000:]))
        return self.ordner / ('satz_%02d' % satz)

    def golden(self, satz):
        """`{kanal: (px, px, 3) uint8}` — Blenders Bilder dieses Satzes."""
        e = self.ordner / ('satz_%02d' % satz) / ('ergebnis' if self.geraet == 'GPU' else 'ergebnis_cpu')
        return {k: np.asarray(Image.open(e / ('haut_1001_%s.png' % k)).convert('RGB')) for k in self.KANAELE}

    # ------------------------------------------------------------------ lokal

    def lage(self):
        """Die Körperpunkte in der Ruhelage der Figur (Blender-Achsen)."""
        return np.load(self.ordner / 'lage.npy')

    def satz_daten(self, satz):
        """`(netz-Eintrag, npz, Namen, spec_lesen(material))` aus dem Arbeitsordner — `Hautbackenzoogolden` liest sie aus den gepackten Daten."""
        s = self.ordner / ('satz_%02d' % satz)
        netz = json.loads((s / 'export' / 'inventar.json').read_text(encoding='utf-8'))['netze'][0]
        npz = dict(np.load(s / 'export' / netz['datei']))
        namen = json.loads((s / 'namen.json').read_text(encoding='utf-8'))
        return netz, npz, namen, lambda m: json.loads((s / 'export' / m['graph']).read_text(encoding='utf-8'))

    def lokal(self, satz, kanaele=KANAELE):
        """Der lokale Backer rechnet Satz `satz`: `{kanal: Bild, 'material': (px, px), 'namen': [...]}`; scheitert ein Graph, kommt der `Hautgraphfehler` je Material in `fehler`."""
        netz, npz, namen, spec = self.satz_daten(satz)
        figur = Hautbackenszene(self.px).figur()
        quelle = Hautbackenquelle(self.lage(), npz['dreiecke'], npz['uv_ecken'])
        schattung = Hautschattungbau.aus_export(quelle.flaeche.punkte, npz, netz)
        texturen, graphen, fehler = {}, {}, {}
        for i, m in enumerate(netz['materialien']):
            try:
                graphen[i] = Hautgraph(m['name'], spec(m), texturen=texturen) if m.get('graph') else None
            except Exception as e:  # noqa: BLE001 — der Fehler gehört ins Ergebnis des Materials
                graphen[i], fehler[i] = None, str(e)
        e = Hautbackengraph(schattung, graphen, self.px).backen(quelle, figur, Hautschattungbau.figur_tangenten(figur), kanaele)
        e['namen'] = namen
        e['fehler'] = fehler
        return e

    # ------------------------------------------------------------------ Vergleich

    @staticmethod
    def statistik(a, b, maske):
        """Abweichung zweier uint8-Bilder auf `maske`: mittel, p99 und größte (in Stufen von 255)."""
        if not maske.any():
            return {'texel': 0}
        d = np.abs(a[maske].astype(np.int16) - b[maske].astype(np.int16))
        return {'texel': int(maske.sum()), 'mittel': float(d.mean()), 'p99': float(np.percentile(d, 99)), 'max': int(d.max())}

    def vergleichen(self, satz, kanaele=KANAELE):
        gold = self.golden(satz)
        lokal = self.lokal(satz, kanaele)
        aus = []
        for i, name in enumerate(lokal['namen']):
            region = lokal['material'] == i
            innen = cv2.erode(region.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            eintrag = {'name': name, 'texel': int(region.sum()), 'korrektur': int(lokal['glanz_korrektur'].get(name, {'texel': 0})['texel']), 'gerechnet': int(lokal['glanz_gerechnet'].get(name, 0))}
            if i in lokal['fehler']:
                eintrag['fehler'] = lokal['fehler'][i]
            else:
                for k in kanaele:
                    eintrag[k] = self.statistik(gold[k], lokal[k], innen)
            aus.append(eintrag)
        return aus
