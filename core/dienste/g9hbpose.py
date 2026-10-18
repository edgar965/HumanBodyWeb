# -*- coding: utf-8 -*-
u"""G9hbpose — eine HumanBody-Pose auf Genesis 9: Daz-Drehwinkel aus den DEF-Quaternionen.

WARUM (Edgar, 17.10.2026: „HumanBody Poses funktionieren gar nicht (nichts reagiert)" — „Human Body
Poses auf Genesis - funktionieren die nicht?" — „baue die Übertragung … das soll auch schnell gehen"):
Eine HumanBody-Pose speichert Quaternionen der Rigify-Knochen (`DEF-thigh.L` …), Genesis 9 dreht 138
Daz-Knochen mit eigenen Achsen. Bis dahin lehnte der Klick ab (`Posenanwendung.pruefen`, seit 09.09.2026).

Auf der Figur heißt die Pose `hb:<Kennung>` (im `pose`-Feld wie ein Daz-Preset): So geht sie unverändert
durch Speichern, Körper- und Stückanfragen, Antwortvorrat und Sofortvorschau; `G9figur.formung` macht
daraus `drehung`, wie aus einem Preset.

DIE RECHNUNG
1. Das Rigify-Skelett (`def_skeleton.json`, Blender) in Three.js-Achsen — (x, z, −y), Quaternion
   (x, z, −y, w), wie `rigify_skeleton_builder.js` —, gestellt wie `Posenanwendung.anwenden`: lokale
   Ruhe · Delta, danach die Gliedwurzeln (Oberarm, Oberschenkel) um die Änderung ihres Elternteils
   zurück; bei einer T-Pose die Oberschenkel senkrecht (`oberschenkelGeradeStellen`).
2. Je DEF-Knochen die Weltbewegung D = Pose · Ruhe⁻¹, auf den Genesis-Knochen derselben Zuordnung wie
   der Retarget (`DEF_ZU_G9`). Ohne Gegenstück (spine4, neck2, Drehknochen, Mittelhand, Gesicht) erbt
   ein Knochen die Bewegung seines Elternteils, dreht also selbst nicht.
3. Arme und Beine Gelenk zu Gelenk: HumanBody hält die Arme flacher und die Beine weiter
   (`G9hbknochen`); mit derselben Weltbewegung zeigte das Genesis-Glied daneben. Eine Schwenkung legt
   es auf die Richtung der Quelle (wie die `Richtungskorrektur` des Retargets) — das Schlüsselbein nicht
   (`g9_zuordnung.SCHULTERN`, „Stiernacken").
4. Daz dreht lokal um die Achsen der Ruhelage (`G9knochenmatrizen`: L = L_eltern · O·E·Oᵀ):
   r = D_eltern⁻¹ · D, E = Oᵀ · r · O, zerlegt in der Reihenfolge des Knochens (erste Achse zuerst,
   wie `G9knochenmatrizen.euler`).

GEMESSEN (17.10.2026, `ProjektTemp/_wegwerf/hbpose_probe.py`, T-Pose, sit_basic, standing_basic, a-pose):
die gebackenen Daz-Matrizen treffen die geplanten Weltbewegungen auf 0,0° (bis 86° Drehung an der
Hand), die Glieder liegen auf 0,0° in der HumanBody-Richtung; 0,03–0,05 s je Pose. Im Chrome
(Ursula mit fünf Stücken): T-Pose Arme 3° unter der Waagerechten, Beine 0,5° neben der Senkrechten.

Gemerkt je Pose und Reglerstellung — Körper, jedes Stück und die Vorschau fragen dieselbe Stellung.
"""
import json
import logging
import threading
from collections import OrderedDict
from pathlib import Path

import numpy as np
from django.conf import settings
from scipy.spatial.transform import Rotation

logger = logging.getLogger('core')

__all__ = ['G9hbpose']


class G9hbpose:
    u"""`ist(wert)`, `drehung(wert, regler)` -> `{g9knochen: {'rotation/x': Grad, …}}`."""

    PRAEFIX = 'hb:'
    GLIEDWURZELN = ('DEF-upper_arm.L', 'DEF-upper_arm.R', 'DEF-thigh.L', 'DEF-thigh.R')
    #: (DEF-Glied, DEF-Kind, Genesis-Glied, Genesis-Kind) ohne Seite — Richtung von Gelenk zu Gelenk.
    GLIEDER = (('DEF-upper_arm', 'DEF-forearm', 'upperarm', 'forearm'),
               ('DEF-forearm', 'DEF-hand', 'forearm', 'hand'),
               ('DEF-thigh', 'DEF-shin', 'thigh', 'shin'),
               ('DEF-shin', 'DEF-foot', 'shin', 'foot'))
    SEITEN = (('L', 'l_'), ('R', 'r_'))
    UNTEN = np.array([0.0, -1.0, 0.0])
    VORRAT_MAX = 16
    _vorrat = OrderedDict()
    _skelett = None
    _schloss = threading.Lock()

    @classmethod
    def ist(cls, wert):
        return isinstance(wert, str) and wert.startswith(cls.PRAEFIX) and len(wert) > len(cls.PRAEFIX)

    @classmethod
    def drehung(cls, wert, regler):
        u"""Daz-Drehwinkel der HumanBody-Pose `hb:<Kennung>` auf der Figur mit `regler` (`{}`: unbekannt)."""
        from Genesis9.formung import G9formung

        kennung = str(wert)[len(cls.PRAEFIX):]
        ruhe = G9formung.aus_abfrage(regler)
        schluessel = (kennung, ruhe.fingerabdruck())
        with cls._schloss:
            if schluessel in cls._vorrat:
                cls._vorrat.move_to_end(schluessel)
                return cls._vorrat[schluessel]
        deltas = cls._deltas(kennung)
        aus = cls._rechnen(deltas, ruhe, cls._tpose(kennung)) if deltas else {}
        with cls._schloss:
            cls._vorrat[schluessel] = aus
            while len(cls._vorrat) > cls.VORRAT_MAX:
                cls._vorrat.popitem(last=False)
        return aus

    @staticmethod
    def _tpose(kennung):
        return 't-pose' in kennung or 'tpose' in kennung

    @staticmethod
    def _deltas(kennung):
        u"""`{DEF-Name: [x, y, z, w]}` in Three.js-Achsen — wie `/api/character/pose/<id>/` `threejs`."""
        from humanbody_core.pose import load_pose

        from .absatzpose import Absatzpose
        try:
            return Absatzpose.to_threejs(load_pose(kennung).def_bones)
        except FileNotFoundError:
            logger.warning('HumanBody-Pose für Genesis 9 unbekannt: %s', kennung)
            return {}

    # ------------------------------------------------------------ HumanBody

    @classmethod
    def _knochen(cls):
        u"""`{name: {eltern, pos, quat}}` des Rigify-Skeletts in Three.js-Achsen, Eltern vor Kindern."""
        if cls._skelett is None:
            datei = Path(settings.HUMANBODY_DATA_DIR) / 'def_skeleton.json'
            daten = json.loads(datei.read_text(encoding='utf-8'))
            roh = {b['name']: b for b in daten['bones']}
            geordnet = OrderedDict()
            while len(geordnet) < len(roh):
                for name, b in roh.items():
                    if name not in geordnet and (b.get('parent') not in roh or b.get('parent') in geordnet):
                        p, q = b['local_position'], b['local_quaternion']
                        geordnet[name] = {'eltern': b.get('parent') if b.get('parent') in roh else None,
                                          'pos': np.array([p[0], p[2], -p[1]], dtype=np.float64),
                                          'quat': (q[1], q[3], -q[2], q[0])}
            cls._skelett = geordnet
        return cls._skelett

    @staticmethod
    def _matrix(q):
        return Rotation.from_quat(np.asarray(q, dtype=np.float64)).as_matrix()   # (x, y, z, w)

    @classmethod
    def _welt(cls, lokal):
        u"""`{name: (R, kopf)}` aus `{name: (R_lokal, pos_lokal)}`."""
        welt = {}
        for name, k in cls._knochen().items():
            r, p = lokal[name]
            if k['eltern'] in welt:
                re, pe = welt[k['eltern']]
                welt[name] = (re @ r, pe + re @ p)
            else:
                welt[name] = (r, p)
        return welt

    @classmethod
    def gestellt(cls, deltas):
        u"""(Ruhe, Pose) als `{name: (R, kopf)}` — wie `Posenanwendung.anwenden` samt Gliedwurzeln."""
        knochen = cls._knochen()
        lokal = {n: (cls._matrix(k['quat']), k['pos']) for n, k in knochen.items()}
        ruhe = cls._welt(lokal)
        for name, q in deltas.items():
            if name in lokal:
                lokal[name] = (lokal[name][0] @ cls._matrix(q), lokal[name][1])
        vorher = cls._welt(lokal)
        for name in cls.GLIEDWURZELN:
            eltern = knochen.get(name, {}).get('eltern')
            if eltern in vorher:
                lokal[name] = (vorher[eltern][0].T @ ruhe[eltern][0] @ lokal[name][0], lokal[name][1])
        return ruhe, cls._welt(lokal)

    # ------------------------------------------------------------- Genesis 9

    @classmethod
    def _rechnen(cls, deltas, ruhe_formung, tpose=False):
        from Genesis9.knochenmatrizen import G9knochenmatrizen
        from Genesis9.skelett import G9skelett
        from humanbody_core.skeleton.formats.g9_zuordnung import DEF_ZU_G9

        ruhe, pose = cls.gestellt(deltas)
        bewegung = {n: pose[n][0] @ ruhe[n][0].T for n in pose}
        aus_def = {g9: d for d, g9 in DEF_ZU_G9.items() if g9 and d in bewegung}
        gelenke = {k['name']: np.asarray(k['kopf'], dtype=np.float64) for k in
                   G9skelett(ruhe_formung.formeln.knochen(), 0.0, ruhe_formung.matrizen()).gelenkknochen()}
        ziele = cls._ziele(pose, gelenke, tpose)
        welt, drehung = {}, {}
        for k in G9skelett.roh():
            name, eltern = k['name'], k['eltern']
            d_eltern = welt.get(eltern, np.eye(3))
            d = bewegung[aus_def[name]] if name in aus_def else d_eltern
            if name in ziele:
                d = cls._schwenkung(d @ ziele[name][0], ziele[name][1]) @ d
            welt[name] = d
            kanaele = cls._kanaele(d_eltern.T @ d, k['orientation'], k['reihenfolge'], G9knochenmatrizen)
            if kanaele:
                drehung[name] = kanaele
        return drehung

    @classmethod
    def _ziele(cls, pose, gelenke, tpose):
        u"""`{g9: (Ruherichtung Genesis, Zielrichtung HumanBody)}` der Glieder — Gelenk zu Gelenk."""
        ziele = {}
        for seite, vor in cls.SEITEN:
            for d, d_kind, g, g_kind in cls.GLIEDER:
                quelle, kind = '%s.%s' % (d, seite), '%s.%s' % (d_kind, seite)
                ziel, ziel_kind = vor + g, vor + g_kind
                if quelle not in pose or kind not in pose or ziel not in gelenke or ziel_kind not in gelenke:
                    continue
                richtung = cls.UNTEN if tpose and d == 'DEF-thigh' else pose[kind][1] - pose[quelle][1]
                ziele[ziel] = (gelenke[ziel_kind] - gelenke[ziel], richtung)
        return ziele

    @staticmethod
    def _schwenkung(von, nach):
        u"""Die kleinste Drehung, die die Richtung `von` auf `nach` legt."""
        a, b = von / np.linalg.norm(von), nach / np.linalg.norm(nach)
        achse = np.cross(a, b)
        sinus = np.linalg.norm(achse)
        if sinus < 1e-9:
            return np.eye(3)
        return Rotation.from_rotvec(achse / sinus * np.arctan2(sinus, float(np.dot(a, b)))).as_matrix()

    @staticmethod
    def _kanaele(r, orientierung, reihenfolge, matrizen):
        u"""`{'rotation/x': Grad, …}` einer lokalen Drehung `r` (Achsen der Ruhelage) — leer ohne Drehung."""
        if np.allclose(r, np.eye(3), atol=1e-7):
            return {}
        o = matrizen.euler(orientierung, 'XYZ')
        winkel = Rotation.from_matrix(o.T @ r @ o).as_euler(str(reihenfolge).lower(), degrees=True)
        paare = zip(str(reihenfolge), winkel, strict=True)
        return {'rotation/%s' % achse.lower(): float(w) for achse, w in paare if abs(w) > 1e-4}
