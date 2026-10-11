# -*- coding: utf-8 -*-
"""Blendimporthaut — die Originalhaut der .blend auf die vier Haut-Kacheln von Genesis (Farbe, Normalen, Rauheit).

Kachel 1005 (Nägel) wird nicht gebacken (`Blendimportlage.NICHT_GEBACKEN`): Genesis' Nägel und der Nagellack-Preset gelten.

„Mesh to 3D" überträgt die Netzfarbe über rund 2 Mio. Proben (`meshfigur.md`, Schritt „textur") — für ein Scan-Netz genug, für eine 8K-Haut zu grob, und Normalen und Rauheit kennt es nicht.
Hier wird aus dem Original gebacken. Der Körper wird dafür in die Ruhelage der Figur gerechnet (`Blendimportlage.koerper_ruhelage`: jeder Punkt nur mit den Käfigpunkten seines Körperteils —
mit der Hand auf der Hüfte hing die Hüfte sonst an der Hand), die Figur selbst (Regler + Eigenmorph, Stufe 1) liegt je Kachel als OBJ daneben. Womit gebacken wird, wählt die Einstellung
Charakter → Backen (`Blendimportbackenwahl`, gelesen, wenn der Schritt beginnt):

    lokal    `Blendimporthautlokal`: auf der GPU im Speicher (NVIDIA Warp), ohne Blender; die Nacharbeit rechnet auf denselben Feldern, jede Datei wird einmal geschrieben.
    blender  `blendbacken.py`: Cycles „Selected to Active" auf der GPU; die Bilder gehen über die Platte, die rohen Karten bleiben in `arbeit/` (`farbe_roh_<k>.jpg`,
             `normalen_roh_<k>.png`, `rauheit_roh_<k>.jpg`) — Grenze, Saum und Fehlstellen lassen sich so ohne neues Backen (17 Minuten) ändern.

NACHARBEIT (`Blendimporthautnacharbeit`): Wo kein Strahl das Original trifft, ist die gebackene Farbe schwarz; dort gilt die Kachel von „Mesh to 3D", die Normale wird flach, die Rauheit
der Median der getroffenen Texel; gebackene Normalen werden gesäubert und auf ihr Feindetail begrenzt. Der Anteil getroffener Texel steht je Kachel im Bericht, dazu der Abstand der
Körperpunkte zur FLÄCHE der Figur in Ruhe (Median, p95, Maximum, RMS, Anteil über 8 mm) — er sagt, wie gut beide Flächen beim Backen übereinanderliegen. Gemessen am ersten Lauf
(08.10.2026): Median 0,99 mm, p95 14,4 mm, 12,3 % über 8 mm — die großen Abstände sitzen an Fingern, Brustwarzen, Lippen, Schritt und Zehen (Wärmekarte). Deutung, nicht geprüft: Dort
trifft der Strahl (Auszug 15 mm, Reichweite 35 mm) nicht oder die falsche Stelle.
"""

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from .blendimportbackenwahl import Blendimportbackenwahl
from .blendimportblender import Blendimportblender
from .blendimporthautnacharbeit import Blendimporthautnacharbeit
from .blendimportlage import Blendimportlage
from .flaechenabstand import Flaechenabstand
from .schammessungablage import Schammessungablage

logger = logging.getLogger('core')

__all__ = ['Blendimporthaut']


class Blendimporthaut:
    def __init__(self, ablage, job, inventar, rollen, px, melden=None, normalen_grenze=None, zusatz=None,
                 normalen_form='weg'):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.px = int(px)
        self.melden = melden or (lambda anteil, text: None)
        #: Grad ab denen eine gebackene Normale als falscher Treffer gilt; `None` = Vorgabe der Säuberung, `'aus'` = nie.
        self.normalen_grenze = normalen_grenze
        self.zusatz = dict(zusatz or {})
        #: `weg` (Vorgabe): nur das Feindetail der gebackenen Normalen gilt; `bleibt`: die ganze Karte.
        self.normalen_form = normalen_form
        #: Farbfüllung um das Scham-Stück (`Blendimportumfeld`): das Objekt (oder None ohne Stück).
        self.umfeld = None
        self.nach = Blendimporthautnacharbeit(ablage, job, px, None, normalen_grenze, normalen_form, self.melden)

    @staticmethod
    def gpu_geraet():
        """Das Warp-Gerät für die Nacharbeit (`core/dienste/hautnach`) — `None` ohne CUDA-GPU: dann rechnen die CPU-Fassungen."""
        try:
            import warp as wp

            wp.init()
            return 'cuda:0' if wp.get_cuda_device_count() else None
        except Exception as fehler:  # noqa: BLE001 — ohne Warp bleibt die CPU
            logger.warning('Blender-Import: Warp nicht nutzbar (%s) — die Nacharbeit rechnet auf der CPU', fehler)
            return None

    @property
    def normalen_flach(self):
        return self.nach.normalen_flach

    @property
    def umfeld_bericht(self):
        return self.nach.umfeld_bericht

    def _umfeld(self, figur, ruhe, name, dreiecke):
        """`Blendimportumfeld` des Scham-Stücks dieses Imports — None, wenn es keines gibt (`arbeit/scham_punkte.npy`) oder die
        Farbe des Originals nicht zu lesen ist."""
        pfad = self.ablage.arbeit('scham_punkte.npy')
        materialien = self.inventar[name].get('materialien') or [{}]
        farbe = (materialien[0] or {}).get('farbe')
        if not pfad.is_file() or not farbe:
            return None
        if len(materialien) != 1:
            # Mehrere Hautmaterialien (Character Creator): welches Bild zu welchem Dreieck gehört, entscheidet `Blendimportscham` — hier
            # bliebe nur das erste (die Kopfhaut). Lieber die Ersatzkachel als die Farbe des Gesichts auf der Scham.
            logger.info('Blender-Import %s: Körper mit %d Materialien — keine Originalfarbe im Umfeld des Scham-Stücks', self.ablage.kennung,
                        len(materialien))
            return None
        from PIL import Image

        from .blendimportumfeld import Blendimportumfeld

        Image.MAX_IMAGE_PIXELS = None
        with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
            uv_ecken = np.asarray(d['uv_ecken'], dtype=np.float64)
        with Image.open(farbe) as bild:
            farbbild = np.asarray(bild.convert('RGB'))
        original = {'punkte': ruhe, 'dreiecke': dreiecke, 'uv_ecken': uv_ecken}
        if self.nach.geraet:
            from .hautnach.hautnachumfeld import Hautnachumfeld     # dieselbe Rechnung auf der GPU (50 s → 3 s an Rosemarys Kachel 1001)

            return Hautnachumfeld(np.load(pfad), figur, original, farbbild, self.nach.geraet)
        return Blendimportumfeld(np.load(pfad), figur, original, farbbild)

    def _koerper(self):
        name = next(r['name'] for r in self.rollen if r['rolle'] == 'koerper')
        with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
            return name, np.asarray(d['punkte'], dtype=np.float64), np.asarray(d['dreiecke'], dtype=np.int64)

    def abstand(self, ruhe, figur, dreiecke):
        """Abstand jedes Körperpunkts zur FLÄCHE der Figur (mm) — Median, p95, Maximum, RMS und Anteil über 8 mm.
        Nicht zum nächsten Punkt: bei 104.480 Figurpunkten und 5–10 mm Punktabstand maß das den Punktabstand mit
        (Import 2026.10.08.11.28.06: Median 2,62 mm zum Punkt gegen 0,99 mm zur Fläche)."""
        # `Flaechenabstand` statt `trimesh.proximity.closest_point`: Rosemary (163.810 Körperpunkte, Figur passte nicht) brauchte dort 22,5 Minuten
        # und 28 GB — dasselbe Maß, gleiche Zahlen (Abweichung ≤ 0,015 mm), 164.000 Punkte in wenigen Sekunden.
        d = Flaechenabstand.abstand(ruhe, figur, dreiecke) * 1000.0
        return {'median_mm': round(float(np.median(d)), 2), 'p95_mm': round(float(np.percentile(d, 95)), 2),
                'max_mm': round(float(d.max()), 1), 'rms_mm': round(float(np.sqrt((d ** 2).mean())), 2),
                'ueber_8mm': round(float((d > 8.0).mean()), 4)}

    def backen(self, blend, pruefen=None, wahl=None):
        """`pruefen(abstand)` (der Lauf übergibt `Blendimportplausibel`) wirft, wenn die Figur nicht zum Körper passt — vor dem Backen. `wahl`: 'lokal' oder 'blender' (Vorgabe: die
        Einstellung, `Blendimportbackenwahl.gewaehlt`)."""
        wahl = wahl or Blendimportbackenwahl.gewaehlt()
        self.nach.geraet = self.gpu_geraet()
        lage = Blendimportlage(self.job, self.zusatz)
        name, punkte, dreiecke = self._koerper()
        ruhe = lage.koerper_ruhelage(punkte, dreiecke)
        np.save(self.ablage.arbeit('koerper_ruhe.npy'), Blendimportlage.blender(ruhe))
        ordner = self.ablage.arbeit('genesis')
        ordner.mkdir(parents=True, exist_ok=True)
        objs = lage.genesis_objs(ordner)
        figur = lage.genesis()
        self.umfeld = self.nach.umfeld = self._umfeld(figur, ruhe, name, dreiecke)
        # `nummern`, nicht `kacheln`: der Lauf legt unter `kacheln` die Dateien ab (`{**bericht}` überschrieb sie mit der Liste).
        bericht = {'abstand': self.abstand(ruhe, figur['punkte'], figur['dreiecke']), 'nummern': sorted(objs), 'backen': wahl}
        logger.info('Blender-Import %s: Körper in Ruhe, Abstand zur Figur %s', self.ablage.kennung, bericht['abstand'])
        if pruefen:
            pruefen(bericht['abstand'])
        if wahl == Blendimportbackenwahl.LOKAL:
            bericht['deckung'] = self._backen_lokal(name, ruhe, figur, sorted(objs), bericht)
        else:
            Blendimportblender(self.ablage, self.melden).laufen(
                'blendbacken.py', blend,
                ['--koerper', name, '--lage', self.ablage.arbeit('koerper_ruhe.npy'), '--genesis', ordner,
                 '--ziel', self.ablage.ergebnis(), '--px', self.px],
                self.ablage.ergebnis('gebacken.txt'))
            bericht['deckung'] = self.nacharbeiten(sorted(objs))
        bericht['umfeld'] = self.umfeld_bericht
        bericht['normalen_flach'] = self.normalen_flach
        bericht['normalen_form'] = self.normalen_form
        bericht['scham_farbe'] = Schammessungablage.nachtragen(self.ablage, figur)       # die Scham-Messung, zweiter Teil: die Hautkacheln sind jetzt da
        return self.kacheln(sorted(objs)), bericht

    # ------------------------------------------------------------ lokal

    def _backen_lokal(self, name, ruhe, figur, kacheln, bericht):
        """Backt und arbeitet nach, alles im Speicher; je Kachel werden die drei Dateien einmal geschrieben. `{kachel: Anteil getroffener Texel in %}`."""
        from PIL import Image

        from .blendimporthautlokal import Blendimporthautlokal      # erst hier: zieht Warp und die GPU-Rechnung herein
        from .hautbacken.graph import Hautgraphfehler

        Image.MAX_IMAGE_PIXELS = None
        with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
            npz = {k: d[k] for k in d.files}
        lokal = Blendimporthautlokal(self.ablage, self.inventar[name], npz, Blendimportlage.blender(ruhe), figur, self.px, self.melden)
        try:
            lokal.vorbereiten()
            deckung = {}
            # Die PNG-Kodierung einer 8K-Normalenkarte dauert 12 s (Pillow, gemessen 10.10.2026): ein Schreiber im Hintergrund kodiert die fertige Kachel, während die GPU die nächste backt
            # (zlib gibt die Python-Sperre frei). Eine Datei wird einmal geschrieben; Fehler des Schreibers kommen beim Warten auf ihn heraus.
            with ThreadPoolExecutor(max_workers=1) as schreiber:
                geschrieben = []
                for i, k in enumerate(kacheln):
                    self.melden(0.80 + 0.15 * i / len(kacheln), 'Kachel %d backen (lokal, GPU)' % k)
                    e = lokal.kachel(k)
                    n = self.nach.kachel(k, e['farbe'], e['normalen'], e['rauheit'], saum_schliessen=False)
                    geschrieben.append(schreiber.submit(self._schreiben, k, n))
                    deckung[str(k)] = n['deckung']
                for auftrag in geschrieben:
                    auftrag.result()
        except Hautgraphfehler as fehler:
            raise RuntimeError('Der lokale Backer kennt nicht alles, was das Material verlangt — Einstellungen → Charakter → Backen → „Blender" wählen. %s'
                               % ' | '.join(fehler.gruende)) from fehler
        bericht['ohne_graph'] = lokal.ohne_graph
        bericht['retri'] = lokal.retri
        bericht['glanz_gerechnet'] = lokal.glanz_gerechnet
        bericht['glanz_korrektur'] = lokal.glanz_korrektur
        if lokal.glanz_text():
            logger.warning('Blender-Import %s: %s', self.ablage.kennung, lokal.glanz_text())
            self.melden(0.95, lokal.glanz_text())
        return deckung

    def _schreiben(self, k, n, farbe=True):
        """Die fertigen Bilder einer Kachel — jede Datei einmal. `farbe=False` lässt die Farbdatei, wie Blender sie schrieb (nichts nachzuarbeiten: kein zweites JPEG)."""
        from PIL import Image

        if farbe:
            Image.fromarray(n['farbe']).save(self.ablage.ergebnis('haut_%d_farbe.jpg' % k), quality=95)
        Image.fromarray(n['normalen']).save(self.ablage.ergebnis('haut_%d_normalen.png' % k))
        Image.fromarray(n['rauheit']).save(self.ablage.ergebnis('haut_%d_rauheit.jpg' % k), quality=95)

    # ------------------------------------------------------------ Blender: Nacharbeit über die Platte

    def farbe_neu(self, kacheln):
        """Die Farbkacheln aus den rohen Blender-Ergebnissen (`arbeit/farbe_roh_<k>.jpg`) neu nacharbeiten — ohne neues Backen (je Kachel 80 s auf der GPU). Normalen und Rauheit
        bleiben. `{kachel: Zahlen des Umfelds}`."""
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
        self.nach.geraet = self.gpu_geraet()
        lage = Blendimportlage(self.job, self.zusatz)
        name, punkte, dreiecke = self._koerper()
        self.umfeld = self.nach.umfeld = self._umfeld(lage.genesis(), lage.koerper_ruhelage(punkte, dreiecke), name, dreiecke)
        self.nach.umfeld_bericht = {}
        for k in kacheln:
            farbe = np.asarray(Image.open(self.ablage.arbeit('farbe_roh_%d.jpg' % k)).convert('RGB'))
            leer = farbe.max(axis=2) <= self.nach.LEER_BIS
            farbe, _saum = self.nach.farbe_fuellen(k, farbe, leer)
            Image.fromarray(farbe).save(self.ablage.ergebnis('haut_%d_farbe.jpg' % k), quality=95)
            self.melden(0.95, 'Farbe der Kachel %d neu' % k)
        return self.umfeld_bericht

    def nacharbeiten(self, kacheln):
        """Blenders Bilder (`ergebnis/`) nacharbeiten und zurückschreiben; die rohen Karten bleiben in `arbeit/`. `{kachel: Anteil getroffener Texel in %}`."""
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
        deckung = {}
        self.nach.normalen_flach = {}
        for k in kacheln:
            farbe_pfad = self.ablage.ergebnis('haut_%d_farbe.jpg' % k)
            normal_pfad = self.ablage.ergebnis('haut_%d_normalen.png' % k)
            rauh_pfad = self.ablage.ergebnis('haut_%d_rauheit.jpg' % k)
            # Die rohen Karten bleiben in `arbeit/` — Grenze, Saum und Fehlstellen lassen sich so ohne neues Backen (17 Minuten) ändern.
            shutil.copyfile(farbe_pfad, self.ablage.arbeit('farbe_roh_%d.jpg' % k))
            shutil.copyfile(normal_pfad, self.ablage.arbeit('normalen_roh_%d.png' % k))
            shutil.copyfile(rauh_pfad, self.ablage.arbeit('rauheit_roh_%d.jpg' % k))
            n = self.nach.kachel(k, np.asarray(Image.open(farbe_pfad).convert('RGB')), np.asarray(Image.open(normal_pfad).convert('RGB')),
                                 np.asarray(Image.open(rauh_pfad).convert('RGB')))
            self._schreiben(k, n, farbe=n['farbe_geaendert'])
            deckung[str(k)] = n['deckung']
        return deckung

    def kacheln(self, kacheln):
        """`{1001: Datei, '1001:normalen': Datei, '1001:rauheit': Datei, …}` (Namen in `ergebnis/`)."""
        aus = {}
        for k in kacheln:
            aus[str(k)] = 'haut_%d_farbe.jpg' % k
            aus['%d:normalen' % k] = 'haut_%d_normalen.png' % k
            aus['%d:rauheit' % k] = 'haut_%d_rauheit.jpg' % k
        return aus
