# -*- coding: utf-8 -*-
"""Blendimportpose — Schritt „pose“ des Modell-Imports: die Haltung des Körpers mit SAM 3D Body bestimmen (11.10.2026).

Edgar (11.10.2026, Jobseite „Mesh-3D“): „Entposen — wenn das Modell in einer anderen Pose als A-Pose ist, bitte berücksichtige das, mit SAM 3D.“ Steht das Modell nicht in A-Haltung und hat kein Auto-Rig-Pro-Rig
(`umposen`), muss „Mesh to 3D“ die Haltung aus 8 Renderings des Körpers mit MediaPipe schätzen — bei liegenden, sitzenden oder stark verdrehten Figuren findet MediaPipe sie nicht (am Gemälde „Modigliani“ 1 von 33 Punkten).
Mit der Einstellung `pose = sam` rendert dieser Schritt den Körper (`koerper.glb`) von vorn (`Mesh3dansicht`), SAM 3D Body findet die Gelenke (`Posebestimmung`, python12), sie werden ins Netz gelegt und als
`landmarken_hand` an „Mesh to 3D“ gereicht (`Meshfigurerkennungsschritt._von_hand`: ersetzt dessen Detektor). Danach findet die Anpassung die Haltung, und `Kleidungsentposen` rechnet die Kleidung mit dem Käfig der
gefundenen Haltung in die Ruhelage zurück (`Blendimportlage`).

Ergebnis in `stand.ergebnis.pose`: Drehung, Gelenke, Silhouetten-IoU Netz ↔ Rendering, die gemessene Haltung (Winkel der Oberarme, Oberschenkel, Neigung des Rumpfs — zum Vergleich mit der A-Haltung von Genesis, Oberarme etwa 43°
zur Senkrechten, gemessen am Bauplan 30.09.2026) und Kontrollbilder (`arbeit/pose/`). Ist die Einstellung `sam`, aber die Pose veraltet oder nie gerechnet, bricht „figur“ ab (`zusatz`), statt still ohne Pose zu rechnen.
**Nicht gemessen:** ob die Pose die Anpassung an einem Modell außerhalb der A-Haltung verbessert — an keinem solchen Modell gerechnet.
"""

import logging

import numpy as np
from django.utils import timezone

from .engine2d3dkleiderposebilder import Engine2d3dKleiderposebilder
from .engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke
from .mesh3dansicht import Mesh3dansicht
from .posebestimmung import Posebestimmung

logger = logging.getLogger('core')

__all__ = ['Blendimportpose']


class Blendimportpose:
    ORDNER = 'pose'
    #: Oberarme der Genesis-A-Haltung zur Senkrechten (Grad), gemessen am Bauplan (Schulter → Ellbogen).
    A_OBERARM_GRAD = 43.0

    def __init__(self, ablage, einstellungen, melden, angehalten=lambda: False, abbrechen=RuntimeError):
        self.ablage = ablage
        self.einstellungen = einstellungen
        self.melden = melden
        self.angehalten = angehalten
        self.abbrechen = abbrechen

    @classmethod
    def modus(cls, einstellungen):
        return 'sam' if (einstellungen or {}).get('pose') == 'sam' else 'aus'

    @classmethod
    def drehung(cls, einstellungen):
        try:
            grad = int((einstellungen or {}).get('pose_drehung') or 0)
        except (TypeError, ValueError):
            grad = 0
        return grad if grad in Posebestimmung.DREHUNGEN else 0

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self, glb):
        """Das Ergebnis des Schritts (für `stand.ergebnis.pose`). `glb`: `arbeit/koerper.glb`."""
        if self.modus(self.einstellungen) != 'sam':
            return {'aus': True, 'grund': 'Einstellung „Pose bestimmen“ steht auf „Aus“ — „Mesh to 3D“ findet die Haltung selbst'}
        ordner = self.ablage.arbeit(self.ORDNER)
        ordner.mkdir(parents=True, exist_ok=True)
        grad = self.drehung(self.einstellungen)
        self.melden(0.0, 'Pose: Körper rendern')
        ansicht = Mesh3dansicht.vorne(glb, ordner / 'ansicht_vorne.png')
        best = Posebestimmung(ordner, 'Mesh-3D %s' % self.ablage.kennung, self.melden, self.angehalten, self.abbrechen)
        sam, neu = best.sam(ansicht, schluessel=Mesh3dansicht.eingaben(glb))
        self.melden(0.7, 'Pose: Gelenke ins Netz legen')
        e = best.abbilden(glb, ansicht, sam, grad)
        abbildung, liste = e['abbildung'], e['liste']
        bilder = self._bilder(ordner, ansicht, sam, abbildung, liste, grad)
        haupt = [n for n in Engine2d3dKleiderposegelenke.HAUPT]
        bericht = {
            'stand': timezone.now().isoformat(), 'modus': 'sam', 'drehung': grad,
            'optionen': {'pose': 'sam', 'pose_drehung': str(grad)},
            'quelle': {'koerper': Posebestimmung.stand(glb)},
            'gelenke': {'gesetzt': int((e['treffer'] > 0).sum()), 'haupt_gesetzt': sum(1 for g in liste if g['name'] in haupt and g['stand'] != 'weggelassen'),
                        'ausserhalb': [g['name'] for g in liste if g['stand'] == 'ausserhalb'], 'liste': liste},
            'abbildung': {'variante': abbildung.variante, 'iou': round(abbildung.iou, 3)},
            'haltung': self.haltung(sam, grad),
            'bilder': bilder, 'datei': 'landmarken.npz', 'dauer_sam_s': sam.get('dauer_s'), 'sam_neu_gerechnet': neu,
        }
        logger.info('Mesh-3D %s: Pose fertig (Drehung %d°, %d Gelenke, IoU %.3f)', self.ablage.kennung, grad, bericht['gelenke']['gesetzt'], abbildung.iou)
        return bericht

    def _bilder(self, ordner, ansicht, sam, abbildung, liste, grad):
        zeichner = Engine2d3dKleiderposebilder()
        rgb = zeichner.foto(ansicht)
        namen = {}
        for g in Posebestimmung.DREHUNGEN:
            e = sam['drehungen'].get(str(g)) or {}
            if 'k2' not in e:
                continue
            datei = 'skelett_%03d.webp' % g
            zeichner.skelett(rgb, e['k2'], sam['namen'], g).save(ordner / datei, 'WEBP', quality=85)
            namen['skelett_%d' % g] = datei
        zeichner.netz(abbildung, liste).save(ordner / 'netz.webp', 'WEBP', quality=85)
        namen['netz'] = 'netz.webp'
        return namen

    # --------------------------------------------------------------- Haltung

    @classmethod
    def haltung(cls, sam, grad):
        """Wie weit steht das Modell von der A-Haltung ab? Winkel (Grad) aus den 2D-Gelenken der gewählten Drehung — zwischen Segment und der Körperachse (Hüftmitte → Schultermitte), also
        unabhängig davon, wie das Bild gedreht ist; in der Bildebene gemessen (Verkürzung nach vorn oder hinten sieht sie nicht)."""
        e = sam['drehungen'].get(str(grad)) or {}
        index = Engine2d3dKleiderposegelenke.index(sam['namen'])
        k2 = np.asarray(e['k2'], dtype=np.float64)

        def p(name):
            return k2[index[name]]

        achse = (p('left-shoulder') + p('right-shoulder')) / 2.0 - (p('left-hip') + p('right-hip')) / 2.0
        laenge = float(np.linalg.norm(achse))
        if laenge < 1e-6:
            return None

        def winkel(vektor, bezug):
            c = float(np.dot(vektor, bezug) / (np.linalg.norm(vektor) * np.linalg.norm(bezug) + 1e-12))
            return round(float(np.degrees(np.arccos(max(-1.0, min(1.0, c))))), 1)

        runter = -achse
        return {
            'rumpf_neigung_grad': winkel(achse, np.array([0.0, -1.0])),
            'oberarm_links_grad': winkel(p('left-elbow') - p('left-shoulder'), runter),
            'oberarm_rechts_grad': winkel(p('right-elbow') - p('right-shoulder'), runter),
            'unterarm_links_grad': winkel(p('left-wrist') - p('left-elbow'), runter),
            'unterarm_rechts_grad': winkel(p('right-wrist') - p('right-elbow'), runter),
            'oberschenkel_links_grad': winkel(p('left-knee') - p('left-hip'), runter),
            'oberschenkel_rechts_grad': winkel(p('right-knee') - p('right-hip'), runter),
            'a_haltung_oberarm_grad': cls.A_OBERARM_GRAD,
        }

    # ------------------------------------------------------- Stand und Figur

    @classmethod
    def zusatz(cls, ablage, stand, glb):
        """Was „Mesh to 3D“ bekommt: `{'landmarken_hand': Pfad}` — leer, wenn die Einstellung `aus` ist. Ist sie `sam` und die Pose veraltet oder nie gerechnet, wirft es
        (kein stiller Rückfall auf MediaPipe, `artefakte-benennen.md`)."""
        einstellungen = stand.get('einstellungen') or {}
        if cls.modus(einstellungen) != 'sam':
            return {}
        pose = (stand.get('ergebnis') or {}).get('pose') or {}
        grund = cls._veraltet(ablage, pose, einstellungen, glb)
        if grund:
            raise RuntimeError('Pose: %s — Schritt „pose“ neu rechnen (ab „Pose“) oder „Pose bestimmen“ auf „Aus“ stellen' % grund)
        return {'landmarken_hand': str(ablage.arbeit(cls.ORDNER) / pose['datei'])}

    @classmethod
    def _veraltet(cls, ablage, pose, einstellungen, glb):
        if not pose or pose.get('aus') or not pose.get('datei'):
            return 'noch nicht gerechnet'
        if not (ablage.arbeit(cls.ORDNER) / pose['datei']).is_file():
            return 'Landmarken-Datei fehlt'
        if (pose.get('optionen') or {}).get('pose_drehung') != str(cls.drehung(einstellungen)):
            return 'Drehung seit dem Lauf geändert'
        try:
            if (pose.get('quelle') or {}).get('koerper') != Posebestimmung.stand(glb):
                return 'das Körpernetz hat sich seit dem Lauf geändert'
        except OSError:
            return 'Körpernetz nicht lesbar'
        return ''
