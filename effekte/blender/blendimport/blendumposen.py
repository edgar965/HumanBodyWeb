# -*- coding: utf-8 -*-
"""Blendumposen — alle Netze einer fremden .blend in die Genesis-Haltung bringen (Blender-Import, 08.10.2026).

Aufruf (aus `core/dienste/blendimportumposen.py`), MIT `--factory-startup`:

    blender -b --factory-startup <quelle.blend> --python blendumposen.py -- --ziel <export-ordner> --karte <karte.json>

`karte.json` ist `G9arpknochenkarte.karte()`: je Segment (Oberarm, Unterschenkel, …) die Gelenke im Rig, die RICHTUNG des
Genesis-Gliedes in Ruhe und die Hautgruppen. Rechnung:

  1. Das Rig auf `REST` stellen und die Netze neu auswerten — die Gewichte gelten für die Ruhelage, nicht für die Pose,
     in der die Datei zufällig gespeichert wurde.
  2. Je Segment, Eltern zuerst: Drehung des KÜRZESTEN Bogens von der (mit dem Elternsegment mitgewanderten) Richtung des
     Gliedes auf die Genesis-Richtung, starr um sein Gelenk; das Gelenk wandert mit dem Elternsegment.
  3. Jeder Punkt = Summe aus Gewicht × Bewegung des Segments seiner Hautgruppe (Gruppen ohne Segment bleiben stehen; die
     Gewichte werden über alle deformierenden Gruppen auf 1 gebracht) — lineare Häutung, wie der Armature-Modifier.

Geschrieben wird in die `<nr>.npz` des Exports: `punkte` = Genesis-Haltung, `punkte_vorher` = die Punkte aus dem Export
(einmal, ein zweiter Lauf lässt sie stehen); dazu `umposen.json` mit Drehung je Segment und Streckung der Kanten.
Nichts in der .blend wird gespeichert.
"""

import argparse
import json
import os
import re
import sys

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np


class Blendumposen:
    def __init__(self, ziel, karte):
        self.ziel = ziel
        self.karte = karte
        self._rigs = {}

    @staticmethod
    def argumente(argv):
        parser = argparse.ArgumentParser(prog='blendumposen')
        parser.add_argument('--ziel', required=True)
        parser.add_argument('--karte', required=True)
        trenner = argv.index('--') if '--' in argv else len(argv)
        return parser.parse_args(argv[trenner + 1:])

    # ----------------------------------------------------------- Mathematik

    @staticmethod
    def bogen(a, b):
        """Drehmatrix des kürzesten Bogens a -> b (Einheitsvektoren)."""
        achse = np.cross(a, b)
        s, c = np.linalg.norm(achse), float(np.dot(a, b))
        if s < 1e-9:
            if c > 0:
                return np.eye(3)
            hilfe = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
            achse = np.cross(a, hilfe)
            achse /= np.linalg.norm(achse)
            return 2.0 * np.outer(achse, achse) - np.eye(3)
        k = achse / s
        kreuz = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        return np.eye(3) + s * kreuz + (1.0 - c) * (kreuz @ kreuz)

    # --------------------------------------------------------------- Rig

    @staticmethod
    def punkt(rig, angabe):
        """Kopf (oder `schwanz:<Name>` = Schwanz) des Knochens in Weltkoordinaten, None wenn es ihn nicht gibt."""
        art, _, name = angabe.rpartition(':')
        knochen = rig.data.bones.get(name)
        if knochen is None:
            return None
        welt = np.array(rig.matrix_world, dtype=np.float64)
        p = np.array(knochen.tail_local if art == 'schwanz' else knochen.head_local, dtype=np.float64)
        return welt[:3, :3] @ p + welt[:3, 3]

    def bewegungen(self, rig):
        """`{segment: (M 4x4, drehung_grad oder None)}` für dieses Rig — Eltern zuerst (so steht die Karte)."""
        if rig.name in self._rigs:
            return self._rigs[rig.name]
        aus = {}
        for s in self.karte:
            eltern = aus.get(s['eltern'], (np.eye(4), None, None))[0] if s['eltern'] else np.eye(4)
            von, bis = self.punkt(rig, s['arp_von']), self.punkt(rig, s['arp_bis'])
            if von is None or bis is None:
                aus[s['name']] = (eltern, None, 'Knochen fehlt: %s' % (s['arp_von'] if von is None else s['arp_bis']))
                continue
            rest = (bis - von) / np.linalg.norm(bis - von)
            ziel = np.asarray(s['ziel'], dtype=np.float64)
            vom_eltern = eltern[:3, :3] @ rest
            r = self.bogen(vom_eltern, ziel)
            m = np.eye(4)
            m[:3, :3] = r @ eltern[:3, :3]
            gelenk = eltern[:3, :3] @ von + eltern[:3, 3]
            m[:3, 3] = gelenk - m[:3, :3] @ von
            winkel = float(np.degrees(np.arccos(np.clip(vom_eltern @ ziel, -1.0, 1.0))))
            aus[s['name']] = (m, winkel, None)
        self._rigs[rig.name] = aus
        return aus

    # -------------------------------------------------------------- Netze

    def segment_je_gruppe(self, obj, rig, bew):
        """`{Gruppenindex: Segmentname oder None}` für die deformierenden Gruppen (None = bleibt stehen); andere fehlen."""
        regeln = [(re.compile(g), s['name']) for s in self.karte for g in s['gruppen']]
        aus = {}
        for gruppe in obj.vertex_groups:
            knochen = rig.data.bones.get(gruppe.name)
            if knochen is None or not knochen.use_deform:
                continue
            aus[gruppe.index] = next((n for r, n in regeln if r.fullmatch(gruppe.name)), None)
        return aus

    def umposen(self, obj, graph):
        rig = next(m.object for m in obj.modifiers if m.type == 'ARMATURE' and m.object)
        bew = self.bewegungen(rig)
        zuordnung = self.segment_je_gruppe(obj, rig, bew)
        auswertung = obj.evaluated_get(graph)
        me = auswertung.to_mesh()
        try:
            n = len(me.vertices)
            if n != len(obj.data.vertices):
                raise RuntimeError('%s: ausgewertetes Netz hat %d Punkte, das Netz %d' % (obj.name, n, len(obj.data.vertices)))
            co = np.empty(n * 3, dtype=np.float64)
            me.vertices.foreach_get('co', co)
        finally:
            auswertung.to_mesh_clear()
        welt = np.array(obj.matrix_world, dtype=np.float64)
        ruhe = co.reshape(-1, 3) @ welt[:3, :3].T + welt[:3, 3]
        namen = sorted({s for s in zuordnung.values() if s})
        spalte = {s: i for i, s in enumerate(namen)}
        gewicht = np.zeros((n, len(namen) + 1))
        for i, v in enumerate(obj.data.vertices):
            for g in v.groups:
                if g.group in zuordnung and g.weight > 0.0:
                    s = zuordnung[g.group]
                    gewicht[i, spalte[s] if s else len(namen)] += g.weight
        summe = gewicht.sum(axis=1)
        gewicht[summe > 0] /= summe[summe > 0][:, None]
        gewicht[summe <= 0, len(namen)] = 1.0
        neu = gewicht[:, len(namen)][:, None] * ruhe
        for s, i in spalte.items():
            m = bew[s][0]
            neu += gewicht[:, i][:, None] * (ruhe @ m[:3, :3].T + m[:3, 3])
        return ruhe, neu, rig

    def schreiben(self, datei, neu):
        pfad = os.path.join(self.ziel, datei)
        with np.load(pfad) as d:
            inhalt = {k: d[k] for k in d.files}
        inhalt.setdefault('punkte_vorher', inhalt['punkte'])
        inhalt['punkte'] = neu
        np.savez_compressed(pfad, **inhalt)
        return inhalt

    @staticmethod
    def kanten(dreiecke, vorher, nachher):
        """Streckung der Dreieckskanten: (Anteil über 1,25 oder unter 0,8, größtes Verhältnis, kleinstes)."""
        e = np.unique(np.sort(np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]]), axis=1), axis=0)
        a = np.linalg.norm(vorher[e[:, 0]] - vorher[e[:, 1]], axis=1)
        b = np.linalg.norm(nachher[e[:, 0]] - nachher[e[:, 1]], axis=1)
        brauchbar = a > 1e-6
        v = b[brauchbar] / a[brauchbar]
        return float(((v > 1.25) | (v < 0.8)).mean()), float(v.max()), float(v.min())

    # ----------------------------------------------------------------- Lauf

    def laufen(self):
        with open(os.path.join(self.ziel, 'inventar.json'), encoding='utf-8') as f:
            inventar = json.load(f)
        rigs = {m.object.name: m.object for n in inventar['netze'] for m in bpy.data.objects[n['name']].modifiers
                if m.type == 'ARMATURE' and m.object}
        abweichend = {}
        for rig in rigs.values():
            abweichend[rig.name] = [pb.name for pb in rig.pose.bones if tuple(pb.rotation_quaternion) != (1.0, 0.0, 0.0, 0.0)
                                    or any(pb.location) or tuple(pb.scale) != (1.0, 1.0, 1.0)]
            rig.data.pose_position = 'REST'
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        netze = []
        for i, n in enumerate(inventar['netze']):
            print('[fortschritt] %d %s' % (int(100 * i / max(1, len(inventar['netze']))), n['name']))
            obj = bpy.data.objects[n['name']]
            ruhe, neu, rig = self.umposen(obj, graph)
            inhalt = self.schreiben(n['datei'], neu)
            export_gegen_ruhe = np.linalg.norm(inhalt['punkte_vorher'] - ruhe, axis=1) * 1000.0
            bewegt = np.linalg.norm(neu - ruhe, axis=1) * 1000.0
            anteil, groesst, kleinst = self.kanten(inhalt['dreiecke'], ruhe, neu)
            netze.append({
                'name': n['name'], 'punkte': int(len(neu)),
                'export_gegen_ruhe_max_mm': round(float(export_gegen_ruhe.max()), 2),
                'bewegt_max_mm': round(float(bewegt.max()), 1), 'bewegt_p50_mm': round(float(np.median(bewegt)), 1),
                'kanten_ausser_0_8_bis_1_25': round(anteil, 5), 'kante_max': round(groesst, 3), 'kante_min': round(kleinst, 3),
            })
        segmente = []
        for rig in rigs.values():
            for name, (_, winkel, grund) in self.bewegungen(rig).items():
                segmente.append({'rig': rig.name, 'segment': name, 'drehung_grad': None if winkel is None else round(winkel, 1),
                                 'grund': grund})
        ergebnis = {'rigs': sorted(rigs), 'posebones_abweichend': abweichend, 'segmente': segmente, 'netze': netze}
        with open(os.path.join(self.ziel, 'umposen.json'), 'w', encoding='utf-8') as f:
            json.dump(ergebnis, f, ensure_ascii=False, indent=1)
        print('[blendumposen] %d Netze in Genesis-Haltung, %d Segmente' % (len(netze), len(segmente)))


if __name__ == '__main__':
    argumente = Blendumposen.argumente(sys.argv)
    with open(argumente.karte, encoding='utf-8') as datei:
        Blendumposen(argumente.ziel, json.load(datei)).laufen()
