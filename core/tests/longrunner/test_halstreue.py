# -*- coding: utf-8 -*-
u"""Der Retarget beugt den Hals um genau die vorgegebenen Grad.

DER EICHFALL, und warum es ihn braucht
======================================
Am 09.09.2026 wurde der „Schwanenhals" gesucht (Edgar: „es gibt den
«Schwanenhals» Syndrom"). Fuenf Fassungen eines Halsmasses gaben fuenf
verschiedene Antworten, weil jede zwei echte Bewegungen verglich —
Quelle und Ziel haben aber verschiedene Ruheformen UND verschiedene
Kettenlaengen (BVH zwei Halsglieder, Rigify drei). Eine davon war
mathematisch blind und meldete fuer JEDE Variante 0,0 Grad Fehler.

Hier gibt es keine echte Bewegung. Die Quelle ist KONSTRUIERT: alle
Drehungen Identitaet, nur der Hals um einen vorgegebenen Winkel
gebeugt. Damit ist die Wahrheit bekannt, und die Frage ist nicht mehr
„welche Variante ist besser", sondern „kommt die Beugung an".

WAS DIESE FAELLE FESTHALTEN
==========================
Der Eichfall hat zwei offene Punkte SICHTBAR gemacht, und beide sind
noch offen:

  * OpenPose bewegt den Hals ueberhaupt nicht (0,0 von 30 Grad).
    `DEF-spine.004` haengt dort an `neck1`, das 19 von 29 Dateien nicht
    fuehren; unzuordenbare Namen werden still uebersprungen.
  * CMU traegt 1,6 Grad Beugungsfehler.

Ein Versuch, beides zu beheben, wurde am 09.09.2026 zurueckgenommen:
Edgar sah danach eine schlechtere A-Pose und verdrehte SCHULTERN. Der
Eichfall prueft nur den Hals — er reicht als Beleg nicht aus, und ein
Beleg, der die Schultern mitprueft, fehlt noch.

Die Faelle halten deshalb den IST-Zustand fest, nicht den Wunsch. Wer
den Retarget verbessert, dreht sie um.

WARUM DIE BEUGEACHSE GERECHNET WIRD
===================================
Eine feste Weltachse taugt nicht: Bei Bandai liegt x auf der
Knochenlaengsachse, und eine Drehung darum aendert die Halsneigung um
exakt 0,0 Grad. Der erste Lauf mass dort nichts und meldete das als
Retarget-Fehler von 19 Grad. Genommen wird das Kreuzprodukt aus
Knochenrichtung und Blickrichtung.
"""
import os

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from humanbody_core.quaternion import Quat
from humanbody_core.skeleton import Skeleton, SkeletonRigify
from humanbody_core.skeleton.retarget.motor import Retargetlauf
from core.dienste.skelettgeometrie import Skelettgeometrie

#: Je Format: (Halsknochen, Rumpf von, Rumpf bis, Hals von, Hals bis).
EICHKNOCHEN = {
    'CMU':    ('Neck', 'Spine', 'Spine1', 'Neck', 'Head'),
    'MIXAMO': ('Neck', 'Spine1', 'Spine2', 'Neck', 'Head'),
    'AIST':   ('Neck', 'Spine2', 'Spine3', 'Neck', 'Head'),
    'BANDAI': ('Neck', 'Spine', 'Chest', 'Neck', 'Head'),
    'MOCAPNET': ('neck', 'abdomen', 'chest', 'neck', 'head'),
    'OPENPOSE': ('neck', 'abdomen', 'chest', 'neck', 'head'),
}
ZIEL = ('DEF-spine.002', 'DEF-spine.003', 'DEF-spine.004', 'DEF-spine.006')
VORN = np.array([0.0, 0.0, 1.0])
GRADE = (-30.0, -20.0, -10.0, 10.0, 20.0, 30.0)

#: Je Format eine Datei, an der geeicht wird. Relativ zu OBJECTS_ROOT.
DATEIEN = {
    'CMU': 'animations/bvh/A_Pose/13_07.bvh',
    'MIXAMO': 'animations/bvh/Mixamo/2hand_idle.bvh',
    # OHNE `neck1` — das ist der Punkt: 19 von 29 OpenPose-Dateien
    # fuehren es nicht, und dort war `DEF-spine.004` bis zum 09.09.2026
    # unzugeordnet. Eine Datei MIT `neck1` wuerde den Fix nicht pruefen.
    'OPENPOSE': 'animations/bvh/Dance/05_02_expressive_arms_pirouette.bvh',
    'MOCAPNET': 'animations/bvh/MocapNET/mocapnet_doubleclap.bvh',
}


def _neigung(brust, hals):
    brust = brust / max(np.linalg.norm(brust), 1e-12)
    hals = hals / max(np.linalg.norm(hals), 1e-12)
    grad = float(np.degrees(np.arccos(np.clip(brust @ hals, -1, 1))))
    quer = hals - (hals @ brust) * brust
    return grad if float(quer @ VORN) >= 0 else -grad


def _beugeachse(bvh, nummer):
    kinder = [k for k in range(len(bvh.names))
              if int(bvh.parents[k]) == nummer]
    if not kinder:
        return None
    richtung = np.asarray(bvh.offsets[kinder[0]], dtype=float)
    laenge = np.linalg.norm(richtung)
    if laenge < 1e-9:
        return None
    achse = np.cross(richtung / laenge, VORN)
    laenge = np.linalg.norm(achse)
    return achse / laenge if laenge > 1e-9 else None


def _bvh_lagen(bvh, bild):
    wq, wp = {}, {}
    for i in range(len(bvh.names)):
        e = int(bvh.parents[i])
        lokal = np.asarray(bvh.quats[bild][i], dtype=float)
        versatz = np.asarray(bvh.offsets[i], dtype=float)
        if e < 0:
            wq[i], wp[i] = lokal, versatz
        else:
            wq[i] = Quat.mul(wq[e], lokal)
            wp[i] = wp[e] + Quat.rotate(wq[e], versatz)
    return {bvh.names[i]: wp[i] for i in range(len(bvh.names))}


def _ziel_lagen(skel, quats, bild):
    wq, wp = {}, {}
    for name in skel.bone_order:
        bone = skel.bones[name]
        spur = quats.get(name)
        lokal = (np.asarray(spur[bild * 4:bild * 4 + 4], dtype=float)
                 if spur is not None else bone.rest_local_quat)
        oben = bone.parent_name
        if oben and oben in wq:
            wq[name] = Quat.norm(Quat.mul(wq[oben], lokal))
            wp[name] = wp[oben] + Quat.rotate(wq[oben], bone.local_pos)
        else:
            wq[name] = Quat.norm(np.asarray(lokal, dtype=float))
            wp[name] = np.asarray(bone.local_pos, dtype=float)
    return wp


def eichlauf(pfad, skip=None, rumpfgrad=0.0):
    u"""``(quellwinkel, zielwinkel)`` je Vorgabe, als Aenderung zu Bild 0.

    `skip=None` nimmt die Liste des Formats — also den Zustand, der
    wirklich laeuft.
    """
    bvh = SkeletonRigify.parse_bvh(pfad)
    bauart = Skeleton.detect_format(bvh.names)
    eich = EICHKNOCHEN.get(bauart.FORMAT)
    if not eich:
        return None
    hals, q_ra, q_rb, q_ha, q_hb = eich
    if hals not in bvh.names:
        return None
    nummer = bvh.names.index(hals)
    achse = _beugeachse(bvh, nummer)
    if achse is None:
        return None

    anzahl = len(GRADE) + 1
    quats = np.zeros((anzahl, len(bvh.names), 4))
    quats[:, :, 3] = 1.0
    if abs(rumpfgrad) > 1e-9 and q_ra in bvh.names:
        rachse = _beugeachse(bvh, bvh.names.index(q_ra))
        if rachse is not None:
            halb = np.radians(rumpfgrad) / 2.0
            q = np.zeros(4)
            q[:3] = rachse * np.sin(halb)
            q[3] = np.cos(halb)
            quats[:, bvh.names.index(q_ra)] = q
    for i, grad in enumerate(GRADE, start=1):
        halb = np.radians(grad) / 2.0
        q = np.zeros(4)
        q[:3] = achse * np.sin(halb)
        q[3] = np.cos(halb)
        quats[i, nummer] = q
    bvh.quats = quats
    bvh.frame_count = anzahl
    # `positions` ist (Bilder, Knochen, 3) — mit (Bilder, 3) bricht
    # `Wurzelspur.spur` mit einem matmul-Fehler ab.
    if getattr(bvh, 'positions', None) is not None:
        bvh.positions = np.zeros((anzahl, len(bvh.names), 3))

    skel = Skelettgeometrie.holen()
    liste = list(bauart.SKIP_DIR_CORRECTION) if skip is None else list(skip)
    spuren = Retargetlauf(
        bvh, skel, mapping=bauart.BONE_MAP_TO_RIGIFY, skip_bones=liste,
        body_height=1.68,
        use_delta=getattr(bauart, 'USE_DELTA', False),
        use_delta_dir=getattr(bauart, 'USE_DELTA_DIR', False)).fahren()
    quatspuren = spuren.als_dict()['tracks']

    def quelle(bild):
        p = _bvh_lagen(bvh, bild)
        return _neigung(p[q_rb] - p[q_ra], p[q_hb] - p[q_ha])

    def ziel(bild):
        p = _ziel_lagen(skel, quatspuren, bild)
        return _neigung(p[ZIEL[1]] - p[ZIEL[0]], p[ZIEL[3]] - p[ZIEL[2]])

    q0, z0 = quelle(0), ziel(0)
    return [(quelle(i) - q0, ziel(i) - z0)
            for i in range(1, anzahl)]


def _pfad(format_name):
    rel = DATEIEN.get(format_name)
    if not rel:
        return None
    voll = os.path.join(str(settings.OBJECTS_ROOT), *rel.split('/'))
    return voll if os.path.isfile(voll) else None


def fehlende():
    u"""Eingetragene Dateien, die es nicht gibt.

    WARUM DAS GEPRUEFT WIRD: Der erste Lauf trug
    `MocapNET/01_01.bvh` ein — die Datei existiert nicht, der Eintrag
    wurde still uebersprungen, und der Test meldete trotzdem GRUEN.
    Ein Prueferr, der nichts findet und gruen sagt, ist die teuerste
    Sorte Fehlalarm (`~/.claude/rules/analysewerkzeuge.md`;
    `Humanbodybaum.fehlende` gibt es aus demselben Grund).

    Fehlen ALLE, ist das kein Fehler — dann steht `OBJECTS_ROOT` in
    einem Testbaum, und die Faelle ueberspringen sich mit Meldung.
    """
    return sorted(name for name in DATEIEN if _pfad(name) is None)


class HalstreueTest(SimpleTestCase):

    databases = []

    #: Wie weit die Beugung danebenliegen darf. Mixamo, MocapNET und
    #: OpenPose liefern gemessen exakt 0,0 — die Schwelle ist Luft
    #: fuer Gleitkommarauschen, kein Spielraum fuer eine Regression.
    SCHWELLE = 0.5

    #: CMU laeuft bewusst ohne Ausnahmeliste und traegt dafuer im
    #: Mittel 1,6 Grad, im schlimmsten Einzelfall 2,37 (Begruendung im
    #: Kopf dieser Datei und in `formats/cmu.py`). Die Grenze ist knapp
    #: darueber gesetzt: Wird sie ueberschritten, hat sich an der
    #: Rechnung etwas geaendert, das gemessen gehoert.
    SCHWELLE_CMU = 2.5

    def _schwelle(self, format_name):
        return (self.SCHWELLE_CMU if format_name == 'CMU'
                else self.SCHWELLE)

    def test_jede_eingetragene_datei_gibt_es(self):
        u"""Eine fehlende Datei faellt auf, statt still zu fehlen."""
        fehlt = fehlende()
        if len(fehlt) == len(DATEIEN):
            self.skipTest('OBJECTS_ROOT fuehrt keine der Dateien '
                          '(Testbaum) — dann greift keiner der Faelle')
        self.assertEqual(fehlt, [],
                         'Eingetragen, aber nicht vorhanden: %s. Der Fall '
                         'zu diesem Format prueft dann NICHTS.'
                         % ', '.join('%s (%s)' % (n, DATEIEN[n])
                                     for n in fehlt))

    def test_die_quelle_folgt_den_vorgaben(self):
        u"""Erst die Probe auf den Eichfall selbst.

        Beugt die konstruierte Quelle sich nicht um die vorgegebenen
        Grad, misst der Fall nichts und jede Zahl darunter ist wertlos.
        Genau das ist beim ersten Lauf passiert: Bei Bandai lag die
        Beugeachse auf der Knochenlaengsachse, die Quelle bewegte sich
        um 0,0 Grad, und der Retarget sah aus wie 19 Grad daneben.
        """
        geprueft = 0
        for name in DATEIEN:
            pfad = _pfad(name)
            if not pfad:
                continue
            reihe = eichlauf(pfad)
            self.assertIsNotNone(reihe, name)
            for (quelle, _), soll in zip(reihe, GRADE):
                self.assertAlmostEqual(quelle, soll, delta=1.5,
                                       msg='%s: Quelle %.2f statt %.2f'
                                           % (name, quelle, soll))
            geprueft += 1
        if not geprueft:
            self.skipTest('keine BVH-Datei unter OBJECTS_ROOT')

    #: Formate, deren Beugung heute ankommt.
    TRAGEND = ('CMU', 'MIXAMO', 'MOCAPNET')

    def test_die_beugung_kommt_am_ziel_an(self):
        u"""Vorgabe rein, dieselbe Beugung raus — wo das heute gilt."""
        geprueft = 0
        for name in DATEIEN:
            if name not in self.TRAGEND:
                continue
            pfad = _pfad(name)
            if not pfad:
                continue
            reihe = eichlauf(pfad)
            self.assertIsNotNone(reihe, name)
            for (_, ziel), soll in zip(reihe, GRADE):
                self.assertAlmostEqual(
                    ziel, soll, delta=self._schwelle(name),
                    msg='%s: Ziel beugt %.2f statt %.2f Grad'
                        % (name, ziel, soll))
            geprueft += 1
        if not geprueft:
            self.skipTest('keine BVH-Datei unter OBJECTS_ROOT')

    def test_openpose_bewegt_den_hals_nicht(self):
        u"""EIN OFFENER PUNKT, hier festgehalten statt verschwiegen.

        `DEF-spine.004` ist bei OpenPose auf `neck1` zugeordnet, und 19
        von 29 Dateien fuehren das nicht — der Halsknochen bleibt
        unzugeordnet und steht in jedem Bild in der Ruhelage. Am
        Eichfall kommen 0,0 von 30 Grad an.

        Die Behebung (`neck` als zweiter Traeger) war am 09.09.2026
        eingebaut und wurde mit dem uebrigen Retarget-Umbau
        zurueckgenommen, weil Edgar danach verdrehte Schultern sah.

        FAELLT DIESER FALL, ist der Fehler behoben — dann gehoert er
        umgedreht und OpenPose in `TRAGEND`.
        """
        pfad = _pfad('OPENPOSE')
        if not pfad:
            self.skipTest('OpenPose-Datei fehlt')
        reihe = eichlauf(pfad)
        schlimmster = max(abs(ziel - soll)
                          for (_, ziel), soll in zip(reihe, GRADE))
        self.assertGreater(
            schlimmster, 10.0,
            'OpenPose beugt den Hals jetzt (%.2f Grad Abweichung). Wenn '
            'das gewollt ist: diesen Fall umdrehen und OPENPOSE in '
            'TRAGEND aufnehmen.' % schlimmster)

    def test_auch_bei_gebeugtem_rumpf(self):
        u"""Der Hals erbt die Korrektur des Rumpfes.

        Mit einem Rumpf in Ruhelage prueft der Eichfall nur den halben
        Weg — deshalb dieselbe Messung ueber vier Rumpfhaltungen.
        """
        pfad = _pfad('CMU')
        if not pfad:
            self.skipTest('CMU-Datei fehlt')
        for rumpf in (-20.0, 20.0, 40.0):
            reihe = eichlauf(pfad, rumpfgrad=rumpf)
            for (_, ziel), soll in zip(reihe, GRADE):
                self.assertAlmostEqual(
                    ziel, soll, delta=self.SCHWELLE_CMU,
                    msg='Rumpf %+.0f: Ziel beugt %.2f statt %.2f'
                        % (rumpf, ziel, soll))

    def test_der_hals_ist_in_jedem_format_zugeordnet(self):
        u"""Ein Zielknochen ohne Zuordnung bleibt stumm in der Ruhelage.

        `Retargetlauf._zuordnung_bauen` nimmt nur Knochen auf, die es
        BEIDSEITIG gibt — ein BVH-Name, den das Format nicht fuehrt,
        wird still uebersprungen. Bei OpenPose zeigte die Halszuordnung
        auf `neck1`, das 19 von 29 Dateien nicht haben; der Hals stand
        in jedem Bild in der Ruhelage.

        Dieser Fall braucht keine BVH-Datei und faellt deshalb auch
        dort, wo `OBJECTS_ROOT` leer ist.
        """
        from humanbody_core.skeleton.formats.cmu import SkeletonCMU
        from humanbody_core.skeleton.formats.mixamo import SkeletonMixamo
        from humanbody_core.skeleton.formats.aist_smpl import (
            SkeletonAIST_SMPL)
        from humanbody_core.skeleton.formats.bandai import SkeletonBandai
        from humanbody_core.skeleton.formats.mocapnet import SkeletonMocapNet
        from humanbody_core.skeleton.formats.openpose import (
            SkeletonOpenPose)
        for klasse in (SkeletonCMU, SkeletonMixamo, SkeletonAIST_SMPL,
                       SkeletonBandai, SkeletonMocapNet, SkeletonOpenPose):
            ziele = set(klasse.BONE_MAP_TO_RIGIFY.values())
            for knochen in ('DEF-spine.004', 'DEF-spine.006'):
                self.assertIn(knochen, ziele,
                              '%s ordnet %s niemandem zu'
                              % (klasse.FORMAT, knochen))

    def test_gegenprobe_die_reparatur_wuerde_wirken(self):
        u"""Sabotage in die andere Richtung: `neck` als zweiter Traeger.

        Damit ist belegt, dass der Fall oben eine ECHTE Ursache misst
        und nicht bloss eine zu enge Schwelle: Mit der Zuordnung kommt
        die Beugung an, ohne sie nicht.
        """
        from unittest import mock
        from humanbody_core.skeleton.formats.openpose import (
            SkeletonOpenPose)
        pfad = _pfad('OPENPOSE')
        if not pfad:
            self.skipTest('OpenPose-Datei fehlt')
        heil = {}
        for bvh_name, ziel in SkeletonOpenPose.BONE_MAP_TO_RIGIFY.items():
            heil[bvh_name] = ('DEF-spine.004' if bvh_name == 'neck'
                              else ziel)
        with mock.patch.object(SkeletonOpenPose, 'BONE_MAP_TO_RIGIFY', heil), \
             mock.patch.object(SkeletonOpenPose,
                               'MEHRERE_SCHREIBWEISEN', True):
            reihe = eichlauf(pfad)
            schlimmster = max(abs(ziel - soll)
                              for (_, ziel), soll in zip(reihe, GRADE))
        self.assertLess(
            schlimmster, self.SCHWELLE,
            'Auch mit zugeordnetem Hals liegt die Beugung %.2f Grad '
            'daneben — dann ist die Zuordnung nicht die Ursache.'
            % schlimmster)
