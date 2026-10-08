# -*- coding: utf-8 -*-
"""Blendimportmodell — das Ergebnis eines Blender-Imports als Genesis-Modell (`data/models/<Name>.json`).

Dieselbe Form wie „Modell speichern" der Szene und `Meshfigurspeichern.modelldaten`: `{name, quelle: genesis9, figur:
{regler, kleidung, fototextur, herkunft, …}}` — so erscheint die Figur unter „Charakter hinzufügen → Genesis 9 →
Gespeicherte Modelle" und lädt in Szene, Studio und Theatre.

    regler      die Stellung aus „Mesh to 3D" samt Eigenmorph (`Meshfigurauftrag.stellung`); der Eigenmorph wird im
                Steckbrief als Eigenform des Modells gekennzeichnet (`G9modellmorphe`) und hat dadurch einen Schieber im
                Bereich „Modell-Eigen" des Reglerfelds
    kleidung    die Stücke des Imports (`Blendimportstuecke`), je `{variante, stil, stile, regler, farbe, …}` wie
                `Meshfigurfrisurstueck.kleidung`
    fototextur  je Kachel Farbe, `<k>:normalen`, `<k>:rauheit` (`Blendimporthaut`) und `augen` (Original oder Daz-Bild
                in der Irisfarbe); daneben je Bild eine verkleinerte Fassung `<stamm>.klein.<endung>` mit `browser_px`
                Kante — die bekommt der Browser ohne Strg+Alt+H (`G9fototextur`)

Ein gleichnamiges Modell, das nicht aus DIESER .blend stammt, wird nicht überschrieben (wie `Meshfigurspeichern`): Dann
bekommt der Name eine Nummer.
"""

import json
import logging
import re
import shutil
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Blendimportmodell']


class Blendimportmodell:
    def __init__(self, ablage, job, quelle, browser_px, zusatz=None):
        self.ablage = ablage
        self.job = job
        self.quelle = str(quelle)
        self.browser_px = int(browser_px)
        #: Weitere Regler der Figur (Nachformung der Scham): gehen mit Wert 1 ins Modell und bekommen einen Schieber.
        self.zusatz = dict(zusatz or {})

    def name(self, wunsch):
        ordner = Path(settings.HUMANBODY_MODELS_DIR)
        stamm = re.sub(r'[^\w\s\-]', '', str(wunsch)).strip() or 'Blender Modell'
        name, n = stamm, 2
        while (ordner / (name + '.json')).is_file() and not self._eigenes(ordner / (name + '.json')):
            name, n = '%s %d' % (stamm, n), n + 1
        return name

    def _eigenes(self, pfad):
        try:
            with open(pfad, encoding='utf-8') as f:
                herkunft = (json.load(f).get('figur') or {}).get('herkunft') or {}
        except (OSError, ValueError):
            return False
        return herkunft.get('art') == 'blend import' and herkunft.get('datei') == self.quelle

    def klein(self, pfad):
        """Die verkleinerte Fassung neben das Bild legen (längste Kante `browser_px`); nur wenn das Bild größer ist."""
        from PIL import Image

        from .modelltexturen import Modelltexturen

        Image.MAX_IMAGE_PIXELS = None
        with Image.open(pfad) as bild:
            if max(bild.size) <= self.browser_px:
                return None
            ziel = Modelltexturen.klein(pfad)
            kopie = bild.convert('L' if bild.mode == 'L' else 'RGB')
            kopie.thumbnail((self.browser_px, self.browser_px), Image.LANCZOS)
            if ziel.suffix.lower() in ('.jpg', '.jpeg'):
                kopie.save(ziel, quality=92)
            else:
                kopie.save(ziel)
        return ziel

    @staticmethod
    def eigenform_markieren(name, regler):
        """Die Eigenmorphe der Stellung als „Modell-Eigen" kennzeichnen (`G9modellmorphe`): so bekommen sie einen Schieber.

        Der kürzeste Name ist der Hauptmorph, ein längerer (Mund, Augen …) heißt nach dem Rest des Namens."""
        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.modellmorphe import G9modellmorphe

        namen = sorted((k for k in regler if G9eigenmorphe.ist_eigen(k)), key=len)
        for schluessel in namen:
            teil = schluessel[len(namen[0]):].strip('_') if schluessel != namen[0] else ''
            try:
                G9modellmorphe.markieren(schluessel, name, teil)
            except ValueError as fehler:
                logger.warning('Blender-Import: Eigenmorph %s ohne Schieber (%s)', schluessel, fehler)
        return namen

    def schreiben(self, wunsch, kacheln, augen, stuecke):
        """`kacheln` `{schluessel: Datei in ergebnis/}`, `augen` Pfad oder None, `stuecke` `{name: kennung}` → Name."""
        from .modelltexturen import Modelltexturen

        name = self.name(wunsch)
        ordner = Modelltexturen.ordner(name)
        ordner.mkdir(parents=True, exist_ok=True)
        fototextur = {}
        dateien = dict(kacheln)
        if augen:
            dateien['augen'] = augen
        for schluessel, datei in dateien.items():
            quelle = Path(datei) if Path(datei).is_absolute() else self.ablage.ergebnis(datei)
            ziel = ordner / Modelltexturen._NAME.sub('_', quelle.name)
            shutil.copy2(quelle, ziel)
            self.klein(ziel)
            fototextur[schluessel] = Modelltexturen.adresse(name, ziel.name, ziel.stat().st_mtime)
        kleidung = {k: {'variante': '', 'stil': '', 'stile': {}, 'regler': {}, 'farbe': None, 'gruppenfarben': {},
                        'griff': False, 'knochen': False} for k in stuecke.values()}
        daten = {
            'name': name,
            'quelle': 'genesis9',
            'figur': {
                'figur': 'basis', 'regler': {**(self.job.stellung() or {}), **self.zusatz}, 'haut': '', 'augen': '01', 'brauen': '',
                'brauenstil': '', 'praesets': {}, 'pose': '', 'ausdruck': '', 'kleidung': kleidung,
                'fototextur': fototextur,
                'herkunft': {'art': 'blend import', 'datei': self.quelle, 'import': self.ablage.kennung,
                             'auftrag': self.job.kennung},
            },
        }
        pfad = Path(settings.HUMANBODY_MODELS_DIR) / (name + '.json')
        pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding='utf-8')
        eigenformen = self.eigenform_markieren(name, daten['figur']['regler'])
        logger.info('Blender-Import %s: Modell %s (%d Bilder, %d Stücke, %d Eigenform)', self.ablage.kennung, name,
                    len(fototextur), len(kleidung), len(eigenformen))
        return name
