# -*- coding: utf-8 -*-
"""kostuembau — Blender-Seite des Schritts „kostuem" von BlenderModel: Kandidaten bauen und rendern.

Aufruf (aus `core.dienste.kostuemblender.Kostuemblender`, Blender ohne Fenster, Werksprofil):

    blender -b --factory-startup --python kostuembau.py -- --auftrag <auftrag.json>

`auftrag.json`: `koerper` (GLB der Grundfigur, mit Rig), `aus` (Ordner), `breite`/`hoehe` (px), `winkel`
(Grad, siehe `Ansichten`), `kandidaten` ([{name, parameter}] — vollständige Wertesätze, `Kostuemparameter`),
`glb`/`blend` (je Kandidat das Kostüm als GLB bzw. die Szene als .blend ablegen). Der Körper wird EINMAL
geladen; je Kandidat: Haltung stellen (`Koerperpose`, Werte `pose.*`), an der gestellten Figur messen
(`Koerpermasse`), Kostüm bauen, rendern. Ergebnis: `<aus>/<name>/ansicht_±WWW.png` (RGBA), `kostuem.glb`,
`zauberer.blend` und `<aus>/bericht.json`. Je Kandidat eine Zeile `Kostuem: Kandidat i von n` für den
Fortschritt.
"""

import argparse
import json
import os
import sys
import time

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WURZEL not in sys.path:
    sys.path.insert(0, WURZEL)

import bpy  # noqa: E402  # pyright: ignore[reportMissingImports]

__all__ = ['Kostuembau']


class Kostuembau:
    HAUT = (0.72, 0.55, 0.45)

    def __init__(self, auftrag):
        self.a = auftrag
        self.aus = os.path.abspath(auftrag['aus'])

    @staticmethod
    def melden(text):
        print(text, flush=True)

    def koerper_laden(self):
        """→ (rig oder None, Körpernetz). Workbench zeigt im Modus MATERIAL die Ansichtsfarbe, nicht die
        Textur der GLB — ohne Hautfarbe stünde ein hellgraues Gesicht gegen das hautfarbene der Vorlage."""
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.import_scene.gltf(filepath=os.path.abspath(self.a['koerper']))
        rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
        netze = [o for o in bpy.data.objects if o.type == 'MESH']
        koerper = max(netze, key=lambda o: len(o.data.vertices))
        koerper.name = 'Koerper'
        for netz in netze:
            for mat in netz.data.materials:
                if mat is not None:
                    mat.diffuse_color = (*self.HAUT, 1.0)
        return (rigs[0] if rigs else None), koerper

    def fahren(self):
        from effekte.blender.kostuem.ansichten import Ansichten
        from effekte.blender.kostuem.koerpermasse import Koerpermasse
        from effekte.blender.kostuem.koerperpose import Koerperpose
        from effekte.blender.kostuem.kostuem import Kostuem
        from effekte.blender.kostuem.kostuembindung import Kostuembindung

        t0 = time.perf_counter()
        os.makedirs(self.aus, exist_ok=True)
        self.melden('Kostuem: Körper laden')
        rig, koerper = self.koerper_laden()
        masse = Koerpermasse(Koerperpose(rig, koerper, 90).punkte())
        vorn_grad, zaehlung = masse.vorn_grad()
        pose = Koerperpose(rig, koerper, vorn_grad) if rig else None
        ansichten = Ansichten(masse, vorn_grad, int(self.a['breite']), int(self.a['hoehe']))
        bericht = {
            'vorn_grad': vorn_grad,
            'vorn_punkte': zaehlung,
            'rig': rig is not None,
            'koerper': masse.bericht(),
            'kandidaten': {},
        }
        kandidaten = self.a['kandidaten']
        bindung = None
        for i, k in enumerate(kandidaten, 1):
            self.melden('Kostuem: Kandidat %d von %d' % (i, len(kandidaten)))
            p = k['parameter']
            Kostuem.entfernen()
            gestellt = masse
            if pose is not None:
                pose.stellen(float(p.get('pose.arme', 0.0)), float(p.get('pose.ellbogen', 0.0)))
                gestellt = Koerpermasse(pose.punkte(), pose.arme())
            teile = Kostuem(gestellt, vorn_grad).bauen(p)
            ordner = os.path.join(self.aus, k['name'])
            eintrag = {
                'teile': {o.name: len(o.data.vertices) for o in teile},
                'bilder': ansichten.rendern(self.a['winkel'], ordner),
            }
            if self.a.get('glb') and pose is not None:
                t = time.perf_counter()
                bindung = bindung or Kostuembindung(rig, koerper)
                eintrag['bindung_mm'] = bindung.binden(teile, pose.punkte())
                t_glb = time.perf_counter()
                eintrag['glb'] = self._glb(rig, koerper, teile, ordner, self.a.get('haltung', True))
                eintrag['sekunden_bindung'] = round(t_glb - t, 2)
                eintrag['sekunden_glb'] = round(time.perf_counter() - t_glb, 2)
            if self.a.get('blend'):
                eintrag['blend'] = self._blend(ordner)
            bericht['kandidaten'][k['name']] = eintrag
        bericht['sekunden'] = round(time.perf_counter() - t0, 1)
        with open(os.path.join(self.aus, 'bericht.json'), 'w', encoding='utf-8') as f:
            json.dump(bericht, f, ensure_ascii=False, indent=1)
        self.melden('Kostuem: fertig in %.1f s' % bericht['sekunden'])

    @classmethod
    def _glb(cls, rig, koerper, teile, ordner, haltung):
        """Figur MIT Kostüm und Rig (Edgar: „bitte auch Modell in den Runden"). `haltung`: die Knoten tragen die
        gestellte Haltung (Runden — die GLB zeigt, was benotet wurde); sonst die Ruhelage des Rigs (Ergebnis —
        für Bewegung auf Genesis 9, dieselbe Ruhelage wie `figur.glb`)."""
        for obj in [koerper, *teile]:
            for mat in obj.data.materials:
                cls._grundfarbe(mat)
        bpy.ops.object.select_all(action='DESELECT')
        for o in [rig, koerper, *teile]:
            o.select_set(True)
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(ordner, 'kostuem.glb'),
            use_selection=True,
            export_apply=True,
            export_yup=True,
            export_rest_position_armature=not haltung,
        )
        return 'kostuem.glb'

    @staticmethod
    def _grundfarbe(mat):
        """Der glTF-Export liest die Grundfarbe des Principled-Knotens, nicht die Ansichtsfarbe, mit der
        Workbench rendert — ohne das käme alles in Blenders Grau an."""
        baum = mat.node_tree if mat is not None else None
        knoten = baum.nodes.get('Principled BSDF') if baum is not None else None
        if knoten is None or knoten.inputs['Base Color'].is_linked:
            return
        knoten.inputs['Base Color'].default_value = tuple(mat.diffuse_color)

    @staticmethod
    def _blend(ordner):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ordner, 'zauberer.blend'), copy=True)
        return 'zauberer.blend'


def main():
    rest = sys.argv[sys.argv.index('--') + 1 :] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--auftrag', required=True)
    with open(p.parse_args(rest).auftrag, encoding='utf-8') as f:
        Kostuembau(json.load(f)).fahren()


if __name__ == '__main__':
    main()
