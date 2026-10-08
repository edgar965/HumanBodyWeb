# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopf — Schritt „kopf" von „2D3D Kleider": den Kopf aus den drei Fotos schneiden und als eigenes Netz rechnen (07.10.2026).

Edgar: „mach einen extra Kopf lauf, extrahiere dazu die bilder vom Kopf, von alle drei seiten … Kopf Lauf als extra schritt und extra UI. Per Check box (default an) anwählbar. wenn das
ausgewählt ist, erstellst und zeigst du die 3 Kopf Bilder im UI und rechnest den Kopf extra."

Ablauf: (1) die Kopfausschnitte aus den vorbereiteten Fotos (`vorbereitet/<name>.png`, `Engine2d3dKleiderkopfausschnitt`) nach `kopf/ausschnitt_<rolle>.png`; sie stehen sofort in `ergebnis.kopf` —
die Seite zeigt sie, solange das Netz rechnet; (2) der Runner rechnet daraus das Kopfnetz (`Engine2d3dKleiderkopfnetz`); (3) die Körper-Kette setzt es ein (`Engine2d3dKleiderkoerperlauf.kopfnetz`
→ `netz_fuer` → `auftrag['kopfnetz']` → `Meshfigurkopfnetz`, dieselbe Einpassung wie in „Mesh to 3D").

Das Häkchen `kopf.rechnen` (Vorgabe an) entscheidet zweimal: ohne Häkchen entfällt der Schritt im vollen Lauf — ausdrücklich gestartet („Kopf rechnen", `ab = kopf`) läuft er trotzdem, wie die
Segmentierung — und ohne Häkchen nimmt die Körper-Kette auch ein vorhandenes Kopfnetz nicht.

Nicht geprüft (07.10.2026): ob das Kopfnetz das Gesicht der Figur verbessert — die Dichte am Kopf ist rund elfmal so hoch (`mesh-trellis2.md`), ob die Körper-Kette sie nutzt, zeigt erst ein Lauf.
"""

import logging
import os

from django.utils import timezone
from PIL import Image

from .engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen
from .engine2d3dkleiderkopfausschnitt import Engine2d3dKleiderkopfausschnitt
from .engine2d3dkleiderkopfnetz import Engine2d3dKleiderkopfnetz
from .engine2d3dkleiderkopfstreckung import Engine2d3dKleiderkopfstreckung
from .engine2d3dkleidernetz import Engine2d3dKleidernetz
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderkopf']


class Engine2d3dKleiderkopf:
    #: Rollen der Ganzkörperfotos, aus denen ein Kopf geschnitten wird (die Nahaufnahme „gesicht" und „nur Iterationen" nicht).
    ROLLEN = ('vorne', 'hinten', 'rechts', 'links')

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Engine2d3dKleideroptionen.kopf(self.job.optionen)

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self):
        if self.optionen['rechnen'] != 'an' and getattr(self.lauf, 'ab', None) != 'kopf':
            logger.info('2D3D Kleider %s: Schritt „kopf" übersprungen (Häkchen „Kopf extra rechnen" aus)', self.job.kennung)
            self.lauf.melden(1.0, 'Kopf übersprungen — Häkchen „Kopf extra rechnen“ ist aus')
            return
        self.lauf.melden(0.0, 'Kopf aus den Fotos schneiden …')
        bilder = self._ausschnitte()
        # Die Ausschnitte stehen sofort in der Datenbank: die Seite zeigt sie, während Hunyuan rechnet (netz = None: das alte Kopfnetz gilt nicht mehr für sie).
        self._ablegen(bilder, None)
        netz = Engine2d3dKleiderkopfnetz(self.lauf, [{'rolle': b['rolle'], 'datei': b['datei']} for b in bilder])
        netz.ausfuehren()
        self._ablegen(bilder, netz.bericht)

    @classmethod
    def netz_fuer(cls, job, ablage):
        """Der Pfad des Kopfnetzes für die Körper-Kette — nur mit Häkchen `kopf.rechnen` UND gerechnetem Netz, sonst None."""
        if Engine2d3dKleideroptionen.kopf(job.optionen)['rechnen'] != 'an':
            return None
        if not ((job.ergebnis or {}).get('kopf') or {}).get('netz'):
            return None
        # Option `koerper.kopfstreckung` (08.10.2026): das Netz senkrecht strecken — `kopf/mesh.glb` bleibt, die Körper-Kette bekommt `kopf/mesh_gestreckt_<Zehntelprozent>.glb`.
        prozent = Engine2d3dKleiderkoerperoptionen.pruefen((job.optionen or {}).get('koerper'))['kopfstreckung']
        return Engine2d3dKleiderkopfstreckung.gestreckt(ablage.netzdatei('kopf'), prozent)

    # ----------------------------------------------------------- Ausschnitte

    def _ausschnitte(self):
        """Je Ansicht der Kopfausschnitt als `kopf/ausschnitt_<rolle>.png` → `[{rolle, quelle, datei, …Befund}]`."""
        ablage = self.ablage
        ablage.kopf().mkdir(parents=True, exist_ok=True)
        for alt in ablage.kopf().glob('ausschnitt_*.png'):
            alt.unlink()
        ergebnis, fehler = [], []
        for foto in Engine2d3dKleidernetz.bilder_fuer(self.job, ablage):
            rolle = foto['rolle'] if foto['rolle'] != 'auto' else (self.job.bild(foto['datei']) or {}).get('erkannt')
            if rolle not in self.ROLLEN or any(e['rolle'] == rolle for e in ergebnis):
                continue
            quelle = ablage.unter(ablage.VORBEREITET) / (os.path.splitext(foto['datei'])[0] + '.png')
            if not quelle.is_file():
                raise RuntimeError('Das vorbereitete Foto %s fehlt — erst „Vorbereitung“ und „Netz“ rechnen' % foto['datei'])
            try:
                with Image.open(quelle) as roh:
                    bild, befund = Engine2d3dKleiderkopfausschnitt.ausschnitt(roh)
            except ValueError as grund:
                fehler.append('%s (%s): %s' % (foto['datei'], rolle, grund))
                logger.warning('2D3D Kleider %s: kein Kopfausschnitt aus %s (%s): %s', self.job.kennung, foto['datei'], rolle, grund)
                continue
            name = 'ausschnitt_%s.png' % rolle
            bild.save(ablage.kopf(name))
            ergebnis.append({'rolle': rolle, 'quelle': foto['datei'], 'datei': name, **befund})
            self.lauf.melden(0.05 * len(ergebnis), 'Kopfausschnitt %s' % rolle)
        if not any(e['rolle'] == 'vorne' for e in ergebnis):
            raise RuntimeError('Kein Kopfausschnitt von „vorne“: %s' % ('; '.join(fehler) or 'kein Foto mit dieser Rolle'))
        return ergebnis

    def _ablegen(self, bilder, netz):
        job = self.job
        job.ergebnis = {**(job.ergebnis or {}), 'kopf': {
            'stand': timezone.now().isoformat(), 'bilder': bilder, 'netz': netz,
            'optionen': {k: self.optionen[k] for k in ('modell', 'flaechen')},
        }}
        self.lauf.sichern('ergebnis')
