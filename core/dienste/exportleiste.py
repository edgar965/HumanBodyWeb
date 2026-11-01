# -*- coding: utf-8 -*-
"""Exportleiste — Export, Render und Regler eines Modells, für jede Seite mit einer Figur (31.10.2026).

Edgar: „baue die ganze Exportleiste auf mit Physik usw." (Vorbild: die rechte Spalte von „2D3D Kleider"), „mach das als wiederverwendbares Modul". Was den Bereich ausmacht, liefert
eine `Exportleistequelle` (`Exportleistebereiche`); die Figur baut der Browser und schickt sie als GLB mit Rig und Textur (`Exportleistemodell` auf der Seite).

Export (`exportieren`): GLB oder Blender, der Körper ohne die Haut unter den Stücken (`Exportleistehautmaske`, wie im Render), wahlweise mit der BVH als glTF-Animation
(`Exportleistebewegung` → `G9glbanimation`) und mit Audio (als Datei daneben, in der .blend
als Tonstreifen — `Engine2d3dKleiderblender.exportieren`, derselbe Blender-Arbeiter wie bei 2D3D Kleider). Ziel ist der Ordner der Seite (Vorgabe `quelle.exportordner()`);
eine vorhandene Datei wird nie überschrieben (`Modellexportziel.eindeutiger_stamm`: `_2`, `_3` …). OBJ schreibt der Browser selbst (`Modellexport`, ohne Animation).
Mit `EIGENES_MODELL` (2D3D Kleider) kommt das Modell vom Bereich (`quelle.modell()`, ohne Hautmaske wie dort bisher), die Bewegung ebenso (`quelle.bewegung`).
Render: `Exportleisterender`. Regler für Rendering und Physik: die fünf Gruppen von `Figurfilm.Filmregler`, abgelegt in `arbeit/regler_werte.json`.
"""

import json
import logging
import shutil
import time

from .exportleisteablage import Exportleisteablage
from .exportleistebewegung import Exportleistebewegung
from .exportleistehautmaske import Exportleistehautmaske
from .exportleisterendermodell import Exportleisterendermodell
from .modellexportziel import Modellexportziel

logger = logging.getLogger('core')

__all__ = ['Exportleiste']


class Exportleiste:
    REGLER = 'regler_werte.json'
    BLENDER_ZEIT_S = 300

    def __init__(self, quelle):
        self.quelle = quelle
        self.ablage = Exportleisteablage(quelle.arbeitsordner())

    # ------------------------------------------------------------------ Zustand

    def zustand(self, bvh=''):
        """Alles, was die Leiste zeigt; mit `bvh` (Pfad oder `Kategorie/Name`) dazu Pfad und Länge dieser BVH."""
        from Figurfilm.filmregler import Filmregler

        from .exportleisterender import Exportleisterender
        # Dictionary gewollt: geht als JSON an die Seite.
        aus = {'bereich': self.quelle.BEREICH, 'kennung': self.quelle.kennung, 'name': self.quelle.name(), 'exportordner': str(self.quelle.exportordner()),
               'ton_vorgabe': self.quelle.ton_vorgabe(), 'optionen': self.optionen(), 'render': Exportleisterender(self).bericht(), 'pfade': self.quelle.pfade(),
               'eigenes_modell': self.quelle.EIGENES_MODELL, 'sperre': self.quelle.sperre(),
               'katalog': {g: dict(Filmregler.katalog(g), titel=t) for g, t in Filmregler.GRUPPEN.items()}}
        aus['bvh_vorgabe'] = self.quelle.bvh_vorgabe()
        bvh = str(bvh or '').strip() or aus['bvh_vorgabe']
        if bvh:
            try:
                pfad = Exportleistebewegung.pfad(bvh)
                bilder, sekunden = Exportleistebewegung.dauer(pfad)
                aus['bvh'] = {'pfad': str(pfad), 'bilder': bilder, 'sekunden': sekunden}
            except (OSError, ValueError) as fehler:
                aus['bvh'] = {'fehler': str(fehler)}
        return aus

    # ------------------------------------------------------------------ Regler

    def optionen(self):
        """`{gruppe: {schluessel: wert}}` — geprüft, fehlende Werte als Vorgabe des Katalogs; ohne eigene Datei die Werte, die der Bereich schon hat (`regler_vorgabe`)."""
        from Figurfilm.filmregler import Filmregler
        pfad = self.ablage.arbeit(self.REGLER)
        try:
            roh = json.loads(pfad.read_text(encoding='utf-8')) if pfad.is_file() else self.quelle.regler_vorgabe()
        except (OSError, ValueError) as fehler:
            logger.warning('Exportleiste %s/%s: %s nicht lesbar (%s) — es gelten die Vorgaben', self.quelle.BEREICH, self.quelle.kennung, pfad, fehler)
            roh = {}
        return {g: Filmregler.pruefen(g, (roh or {}).get(g)) for g in Filmregler.GRUPPEN}

    def optionen_speichern(self, roh):
        from Figurfilm.filmregler import Filmregler
        werte = {g: Filmregler.pruefen(g, (roh or {}).get(g)) for g in Filmregler.GRUPPEN}
        pfad = self.ablage.arbeit(self.REGLER)
        zwischen = pfad.with_name(pfad.name + '.teil')
        zwischen.write_text(json.dumps(werte, ensure_ascii=False, indent=1), encoding='utf-8')
        zwischen.replace(pfad)
        return werte

    # ------------------------------------------------------------------ Export

    def exportieren(self, glb_datei, angaben):
        """`glb_datei`: die GLB der Seite (hochgeladen); `angaben`: {format: glb|blend, animation, bvh, stellung, audio, audio_pfad, name, ordner}.
        → `{ordner, dateien: [{name, bytes}], bilder, sekunden, kanaele, fehlend, bvh, audio}`; ValueError (Eingabe) oder RuntimeError (Blender)."""
        from Genesis9.glbanimation import G9glbanimation

        from .studioton import Studioton
        art = str(angaben.get('format') or '')
        if art not in ('glb', 'blend'):
            raise ValueError('Format: glb oder blend')
        if self.quelle.sperre():
            raise ValueError(self.quelle.sperre())
        ordner = Modellexportziel.ordner(angaben.get('ordner') or str(self.quelle.exportordner()))
        stamm = Modellexportziel.name(angaben.get('name') or self.quelle.name())
        bvh = Exportleistebewegung.pfad(angaben.get('bvh')) if angaben.get('animation') else None
        if bvh is not None:
            stamm = '%s_%s' % (stamm, Modellexportziel.name(bvh.stem, 'bewegung'))
        ton = Studioton.pruefen(angaben.get('audio_pfad')) if angaben.get('audio') else None
        stamm = Modellexportziel.eindeutiger_stamm(ordner, stamm, ('.glb', '.blend', '_export.json'))
        arbeit = self.ablage.arbeitsordner('export')
        eingang = arbeit / ('eingang_%d.glb' % time.time_ns())
        animiert = eingang.with_name(eingang.stem + '_animiert.glb')
        try:
            stellung = angaben.get('stellung') or {}
            if self.quelle.EIGENES_MODELL:
                # Das Modell des Bereichs, wie er es selbst exportiert und rendert (2D3D Kleider: das Stand-Modell, ohne Maske wie bis 31.10.2026 auf der Seite)
                modell, verdeckung = G9glbanimation(self.quelle.modell()), None
            else:
                with open(eingang, 'wb') as d:
                    for stueck in glb_datei.chunks():
                        d.write(stueck)
                modell = G9glbanimation(eingang)
                # Die Haut unter den Stücken fällt aus dem Körper wie im Render (`Exportleistehautmaske`, Edgar 31.10.2026: sonst sticht sie in der Bewegung durch den Stoff)
                stuecke = [(s['punkte'], s['dreiecke']) for s in Exportleisterendermodell().stuecke(modell, stellung.get('haut_deckt')) if s['deckt']]
                verdeckung = Exportleistehautmaske.glb(modell, stuecke)
            bewegung = self.quelle.bewegung(bvh, stellung) if bvh is not None else None
            bericht = ({'kanaele': 0, 'fehlend': [], 'bilder': 0, 'sekunden': 0.0} if bewegung is None
                       else modell.einbauen(bewegung, name=bvh.stem))
            bericht['hautverdeckung'] = verdeckung
            kollision = self.quelle.kollision() if bewegung is not None else None
            if kollision is not None:          # Stücke aus fremden Gliedern geschoben wie auf der Seite, als Morph-Ziele (`Exportleistekollision`, 31.10.2026 nachts)
                from .exportleistekollision import Exportleistekollision
                bericht['kollision'] = Exportleistekollision(modell).einbauen(*kollision)
            dateien = []
            if art == 'glb':
                modell.schreiben(ordner / (stamm + '.glb'))
                dateien.append(stamm + '.glb')
            else:
                modell.schreiben(animiert)
                fps = round((bericht['bilder'] - 1) / bericht['sekunden']) if bericht['sekunden'] else 30
                from .engine2d3dkleiderblender import (
                    Engine2d3dKleiderblender,  # der EINE Blender-Arbeiter (`BlenderNurUeberEinenArbeiterTest`)
                )
                Engine2d3dKleiderblender(self.ablage.arbeit('blender')).exportieren(animiert, ordner / (stamm + '.blend'), fps, ton, self.BLENDER_ZEIT_S)
                dateien.append(stamm + '.blend')
        finally:
            eingang.unlink(missing_ok=True)
            animiert.unlink(missing_ok=True)
        if ton:
            shutil.copyfile(ton, ordner / (stamm + '_audio' + ton.suffix.lower()))
            dateien.append(stamm + '_audio' + ton.suffix.lower())
        bericht.update(bvh=str(bvh) if bvh else None, audio=str(ton) if ton else None, format=art, quelle='%s/%s' % (self.quelle.BEREICH, self.quelle.kennung))
        (ordner / (stamm + '_export.json')).write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
        dateien.append(stamm + '_export.json')
        logger.info('Exportleiste %s/%s: %s nach %s (%s)', self.quelle.BEREICH, self.quelle.kennung, art, ordner, ', '.join(dateien))
        return dict(bericht, ordner=str(ordner), dateien=[{'name': n, 'bytes': (ordner / n).stat().st_size} for n in dateien])
