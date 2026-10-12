# -*- coding: utf-8 -*-
"""Engine2d3dKleiderpose — Schritt „pose" von „2D3D Kleider": die Gelenke der Person am Foto finden, ins Netz legen und den Maßstab ableiten (11.10.2026).

Edgar (11.10.2026), nach den Proben am Gemälde „Modigliani": „baue das in die Job Pipeline hinein, als extra Schritt, wo man auch das Ergebnis sehen kann". Warum: an einem liegenden Netz findet die Körper-Kette
(MediaPipe auf Renderings) 1 von 33 Landmarken und hält ein 3,62 langes Netz für Zentimeter (Tor „Rumpftiefe nicht messbar"); SAM 3D Body findet die Gelenke am FOTO (Drehung gewählt, `_run_sam3dpose.py`).
Konzept, Proben, Zahlen: `Docu/konzepte/2026-10-11_gemaelde-schnelldurchlauf-und-freie-pose-konzept.md`.

Ablauf: (1) das vorbereitete Foto mit Rolle „vorne" durch SAM 3D Body in allen vier Drehungen (`pose/sam3d.json`; der Lauf ist an Foto und Fassung gebunden — dieselben Gelenke werden nicht neu gerechnet,
wenn nur die Drehung oder die Auswahl der Gelenke wechselt); (2) die Gelenke der gewählten Drehung ins Netz (`Engine2d3dKleiderposeabbildung`) → `pose/landmarken.npz` (`roh` (33, 3), `treffer` (33)),
dazu der Maßstab; (3) Kontrollbilder (`Engine2d3dKleiderposebilder`); (4) `ergebnis.pose`. Die Körper-Kette nimmt Landmarken und Maßstab mit dem Häkchen `pose.rechnen`
(`fuer_koerper` → `Engine2d3dKleiderkoerperlauf.zusatz` → `auftrag.json` → `Meshfigurerkennungsschritt`). Der Schritt allein ändert die Figur nicht; sie ändert sich, wenn „Körper" neu rechnet.

Ist das Häkchen an und die Pose veraltet oder nie gerechnet, bricht die Körper-Kette mit einer Meldung ab, statt still ohne Pose zu rechnen (`artefakte-benennen.md`).
"""

import logging
import os

import numpy as np
from django.utils import timezone

from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .engine2d3dkleiderposebilder import Engine2d3dKleiderposebilder
from .engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke
from .posebestimmung import Posebestimmung

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderpose']


class Engine2d3dKleiderpose:
    #: SAM 3D Body, Fassung der Ablage `pose/sam3d.json` und Drehungen stehen in `Posebestimmung` (11.10.2026 herausgelöst).
    DREHUNGEN = Posebestimmung.DREHUNGEN
    #: Ist die Person breiter als hoch um diesen Faktor, sagt die Karte „liegt“.
    LIEGT_AB = 1.3

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Engine2d3dKleideroptionen.pose(self.job.optionen)

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self):
        if self.optionen['rechnen'] != 'an' and getattr(self.lauf, 'ab', None) != 'pose':
            logger.info('2D3D Kleider %s: Schritt „pose“ übersprungen (Häkchen aus)', self.job.kennung)
            self.lauf.melden(1.0, 'Pose übersprungen — Häkchen „Pose aus dem Foto rechnen“ ist aus')
            return
        foto = self._foto()
        netz = self.ablage.netzdatei(original=True)
        if netz is None:
            raise RuntimeError('Kein Netz — erst der Schritt „netz“')
        self.ablage.pose().mkdir(parents=True, exist_ok=True)
        self.lauf.melden(0.0, 'Pose: SAM 3D Body am Foto %s' % foto['datei'])
        sam, neu = self._sam(foto)
        self.lauf.melden(0.6, 'Pose: Gelenke ins Netz legen')
        ergebnis = self._abbilden(foto, netz, sam)
        ergebnis['sam_neu_gerechnet'] = neu
        self.job.ergebnis = {**(self.job.ergebnis or {}), 'pose': ergebnis}
        self.lauf.sichern('ergebnis')
        logger.info('2D3D Kleider %s: Pose fertig (Drehung %s°, %s Gelenke, Maßstab %.4f)', self.job.kennung, ergebnis['drehung'], ergebnis['gelenke']['gesetzt'],
                    (ergebnis.get('masstab') or {}).get('faktor') or 0.0)

    def _foto(self):
        """Das vorbereitete Foto mit Rolle „vorne“ — das Netz liegt auf ihm (Hunyuan3D/TRELLIS: Fotoseite nach +Z)."""
        from .engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung
        for bild in Engine2d3dKleidersegmentierung.bilder_fuer(self.job, self.ablage):
            if bild['rolle'] == 'vorne':
                return bild
        raise RuntimeError('Kein vorbereitetes Foto mit der Rolle „vorne“ — erst „Vorbereitung“ oder „Netz“ rechnen und dem Foto die Rolle geben')

    @staticmethod
    def _stand(pfad):
        s = os.stat(str(pfad))
        return [s.st_size, s.st_mtime_ns]

    # ------------------------------------------------------------- SAM 3D Body

    def _bestimmung(self):
        """Der gemeinsame Weg (`Posebestimmung`): SAM 3D Body und Gelenke im Netz — derselbe, den der Import der Jobseite „Mesh-3D“ geht."""
        return Posebestimmung(self.ablage.pose(), '2D3D Kleider %s' % self.job.kennung, self.lauf.melden, self.lauf.angehalten, self.lauf.Angehalten)

    def _sam(self, foto):
        """`(sam3d.json als dict, neu_gerechnet)` — aus der Ablage, wenn Foto, Fassung und Drehungen stimmen."""
        return self._bestimmung().sam(foto['png'], self.DREHUNGEN)

    # --------------------------------------------------------------- Abbildung

    def _abbilden(self, foto, netz, sam):
        grad = int(self.optionen['drehung'])
        weglassen = tuple(self.optionen['weglassen'])
        ergebnis = self._bestimmung().abbilden(netz, foto['png'], sam, grad, weglassen, self.optionen['masstab'] == 'an')
        abbildung, scan, alpha = ergebnis['abbildung'], ergebnis['scan'], ergebnis['alpha']
        treffer, liste, masstab = ergebnis['treffer'], ergebnis['liste'], ergebnis['masstab']
        bilder = self._bilder(foto, sam, abbildung, liste, weglassen)
        x0, y0, x1, y1 = abbildung.kasten
        haupt = [n for n in Engine2d3dKleiderposegelenke.HAUPT if n not in weglassen]
        return {
            'stand': timezone.now().isoformat(), 'drehung': grad, 'optionen': {k: self.optionen[k] for k in ('drehung', 'weglassen', 'masstab')},
            'quelle': {'foto': self._stand(foto['png']), 'netz': self._stand(netz)},
            'foto': {'datei': foto['datei'], 'rolle': foto['rolle'], 'breite': int(alpha.shape[1]), 'hoehe': int(alpha.shape[0]), 'person': [x0, y0, x1, y1],
                     'liegt': bool((x1 - x0) > self.LIEGT_AB * (y1 - y0)), 'seitenverhaeltnis': round((x1 - x0) / float(y1 - y0), 2)},
            'abbildung': {'variante': abbildung.variante, 'iou': round(abbildung.iou, 3), 'alle_iou': {k: round(v, 3) for k, v in abbildung.alle_iou.items()},
                          'pixel_je_einheit': [round(abbildung.sx, 2), round(abbildung.sy, 2)]},
            'netz_ausdehnung': [round(float(w), 4) for w in np.ptp(scan.punkte, axis=0)],
            'gelenke': {'gesetzt': int((treffer > 0).sum()), 'haupt_gesetzt': sum(1 for g in liste if g['name'] in haupt), 'weggelassen': list(weglassen),
                        'ausserhalb': [g['name'] for g in liste if g['stand'] == 'ausserhalb'], 'liste': liste},
            'masstab': masstab, 'bilder': bilder, 'datei': 'landmarken.npz', 'dauer_sam_s': sam.get('dauer_s'),
        }

    def _bilder(self, foto, sam, abbildung, liste, weglassen):
        zeichner = Engine2d3dKleiderposebilder()
        rgb = zeichner.foto(foto['png'])
        namen = {}
        for grad in self.DREHUNGEN:
            e = sam['drehungen'].get(str(grad)) or {}
            if 'k2' not in e:
                continue
            datei = 'skelett_%03d.webp' % grad
            zeichner.skelett(rgb, e['k2'], sam['namen'], grad, weglassen if grad == int(self.optionen['drehung']) else ()).save(self.ablage.pose(datei), 'WEBP', quality=85)
            namen['skelett_%d' % grad] = datei
        zeichner.netz(abbildung, liste).save(self.ablage.pose('netz.webp'), 'WEBP', quality=85)
        namen['netz'] = 'netz.webp'
        return namen

    # ------------------------------------------------------- Stand und Körper

    @classmethod
    def stand(cls, job, ablage):
        """`(ergebnis.pose oder None, grund)` — `grund` leer, wenn die Pose zu den jetzigen Optionen, dem Foto und dem Netz passt, sonst was sich geändert hat."""
        pose = (job.ergebnis or {}).get('pose')
        if not pose:
            return None, 'noch nicht gerechnet'
        if not ablage.pose(str(pose.get('datei') or '-')).is_file():
            return pose, 'Landmarken-Datei fehlt'
        jetzt = Engine2d3dKleideroptionen.pose(job.optionen)
        anders = [k for k in ('drehung', 'weglassen', 'masstab') if (pose.get('optionen') or {}).get(k) != jetzt[k]]
        if anders:
            return pose, 'Optionen seit dem Lauf geändert: %s' % ', '.join(anders)
        try:
            if (pose.get('quelle') or {}).get('netz') != cls._stand(ablage.netzdatei(original=True)):
                return pose, 'das Netz hat sich seit dem Lauf geändert'
        except (OSError, TypeError):
            return pose, 'Netz nicht lesbar'
        return pose, ''

    @classmethod
    def fuer_koerper(cls, job, ablage):
        """Was die Körper-Kette nimmt: `{'landmarken': Pfad, 'masstab': Faktor oder None}` — `None` ohne Häkchen `pose.rechnen`. Ist das Häkchen an und die Pose veraltet oder nie gerechnet,
        wirft es: eine Kette ohne die gewählte Pose darf nicht still durchlaufen."""
        if Engine2d3dKleideroptionen.pose(job.optionen)['rechnen'] != 'an':
            return None
        pose, grund = cls.stand(job, ablage)
        if grund:
            raise RuntimeError('Pose: %s — erst „Pose rechnen“ (Schritt „pose“) oder das Häkchen „Pose aus dem Foto rechnen“ ausschalten' % grund)
        masstab = (pose.get('masstab') or {}).get('faktor')
        return {'landmarken': ablage.pose(pose['datei']), 'masstab': float(masstab) if masstab else None}
