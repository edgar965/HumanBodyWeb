# -*- coding: utf-8 -*-
"""kostuembau — Blender-Seite des Schritts „kostuem" von BlenderModel: Kandidaten bauen und rendern.

Aufruf (aus `core.dienste.kostuemblender.Kostuemblender`, Blender ohne Fenster, Werksprofil):

    blender -b --factory-startup --python kostuembau.py -- --auftrag <auftrag.json>

`auftrag.json`: `koerper` (GLB der Grundfigur, mit Rig), `aus` (Ordner), `breite`/`hoehe` (px), `winkel`
(Grad, siehe `Ansichten`), `kandidaten` ([{name, parameter}] — vollständige Wertesätze, `Kostuemparameter`),
`glb`/`blend` (je Kandidat das Kostüm als GLB bzw. die Szene als .blend ablegen). Je Kandidat: Haltung stellen
(`Koerperpose`, Werte `pose.*`), an der gestellten Figur messen (`Koerpermasse`), Kostüm bauen, rendern.
Ergebnis: `<aus>/<name>/ansicht_±WWW.png` (RGBA), `kostuem.glb`, `zauberer.blend` und `<aus>/bericht.json`.

ZWEI BETRIEBSARTEN
    einmalig  (`aus` im Auftrag): Körper laden, die Kandidaten des Auftrags abarbeiten, Ende.
    Dienst    (`dienst` im Auftrag = Postfach-Ordner): Körper EINMAL laden, dann Befehle abarbeiten, bis `ende` kommt
              oder `LEERLAUF_S` lang nichts. Ein Befehl ist ein Auftrag wie oben (ohne
              `koerper`/`breite`/`hoehe`) in `befehl_<nr>.json`; die Antwort — der Bericht, bei einem Fehler
              `{"fehler": …}` — liegt danach in `antwort_<nr>.json`. Gemessen (30.09.2026, unter Last):
              Blender starten und die Figur laden kosten je Aufruf 4–9 s, ein Kandidat danach nur 0,6–0,8 s —
              bei einer Runde von acht Kandidaten war es also fast nur das Laden. Das Postfach ist ein Ordner
              statt stdin: Blender im Hintergrund liest stdin nicht verlässlich, und Dateien lassen sich
              unteilbar ersetzen (`os.replace`).

Je Kandidat eine Zeile `Kostuem: Kandidat i von n` für den Fortschritt (einmalig).
"""

import argparse
import glob
import json
import os
import sys
import time
import traceback

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WURZEL not in sys.path:
    sys.path.insert(0, WURZEL)

import bpy  # noqa: E402  # pyright: ignore[reportMissingImports]

__all__ = ['Kostuembau']


class Kostuembau:
    #: sRGB — gemessen an der Vorlage (Gesicht 161/119/101 von 255), etwas heller wegen der Studiobeleuchtung.
    HAUT = (0.66, 0.50, 0.42)
    #: So lange wartet der Dienst auf einen Befehl, bevor er sich beendet (der Vater ist dann weg).
    LEERLAUF_S = 900
    TAKT_S = 0.02

    def __init__(self, auftrag):
        self.a = auftrag
        self.rig = self.koerper = self.masse = self.pose = self.ansichten = self.bindung = None
        self.kopf = {}
        self.foto = self.projektion = self.huellen = self._textur_stand = None
        self._fotoschluessel = None

    @staticmethod
    def melden(text):
        print(text, flush=True)

    def koerper_laden(self):
        """→ (rig oder None, Körpernetz). Workbench zeigt im Modus MATERIAL die Ansichtsfarbe, nicht die
        Textur der GLB — ohne Hautfarbe stünde ein hellgraues Gesicht gegen das hautfarbene der Vorlage."""
        from effekte.blender.kostuem.rohr import Rohr

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
                    mat.diffuse_color = (*Rohr.linear(self.HAUT), 1.0)
        return (rigs[0] if rigs else None), koerper

    def vorbereiten(self):
        """Körper laden, messen, Kamera und Bühne anlegen — einmal je Prozess."""
        from effekte.blender.kostuem.ansichten import Ansichten
        from effekte.blender.kostuem.huellenstand import Huellenstand
        from effekte.blender.kostuem.koerpermasse import Koerpermasse
        from effekte.blender.kostuem.koerperpose import Koerperpose
        from effekte.blender.kostuem.projektion import Projektion

        self.melden('Kostuem: Körper laden')
        self.rig, self.koerper = self.koerper_laden()
        self.masse = Koerpermasse(Koerperpose(self.rig, self.koerper, 90).punkte())
        vorn_grad, zaehlung = self.masse.vorn_grad()
        self.pose = Koerperpose(self.rig, self.koerper, vorn_grad) if self.rig else None
        self.ansichten = Ansichten(self.masse, vorn_grad, int(self.a['breite']), int(self.a['hoehe']))
        self.projektion = Projektion(self.ansichten, int(self.a['breite']), int(self.a['hoehe']))
        self.huellen = Huellenstand(self)
        self.kopf = {
            'vorn_grad': vorn_grad,
            'vorn_punkte': zaehlung,
            'rig': self.rig is not None,
            'koerper': self.masse.bericht(),
        }

    def gestellt(self, p):
        """Die Haltung nach `p` stellen (`pose.*`) → die Körpermaße dieser Haltung (`Koerpermasse`)."""
        from effekte.blender.kostuem.koerpermasse import Koerpermasse

        if self.pose is None:
            return self.masse
        stab_arm = p.get('pose.ellbogen_stab')
        self.pose.stellen(
            float(p.get('pose.arme', 0.0)),
            float(p.get('pose.ellbogen', 0.0)),
            float(stab_arm) if stab_arm is not None else None,
            float(p.get('pose.arm_vor', 0.0)),
        )
        return Koerpermasse(self.pose.punkte(), self.pose.arme(), self.pose.ellbogen())

    def abarbeiten(self, auftrag):
        """Die Kandidaten eines Auftrags bauen und rendern. → der Bericht (dict)."""
        from effekte.blender.kostuem.kostuem import Kostuem
        from effekte.blender.kostuem.kostuembindung import Kostuembindung

        t0 = time.perf_counter()
        aus = os.path.abspath(auftrag['aus'])
        os.makedirs(aus, exist_ok=True)
        bericht = dict(self.kopf, kandidaten={})
        kandidaten = auftrag['kandidaten']
        huelle = self.huellen.fuer(auftrag, aus)
        if huelle is not None:
            bericht['huelle_s'] = round(time.perf_counter() - t0, 3)
        for i, k in enumerate(kandidaten, 1):
            self.melden('Kostuem: Kandidat %d von %d' % (i, len(kandidaten)))
            p = k['parameter']
            t1 = time.perf_counter()
            Kostuem.entfernen()
            gestellt = self.gestellt(p)
            t2 = time.perf_counter()
            teile = Kostuem(gestellt, self.kopf['vorn_grad'], huelle).bauen(p)
            t3 = time.perf_counter()
            ordner = os.path.join(aus, k['name'])
            eintrag = {
                'teile': {o.name: len(o.data.vertices) for o in teile},
                'bilder': self.ansichten.rendern(auftrag['winkel'], ordner),
            }
            eintrag['zeiten'] = {
                'haltung': round(t2 - t1, 3),
                'bau': round(t3 - t2, 3),
                'render': round(time.perf_counter() - t3, 3),
            }
            exportteile, farbig = teile, False
            if (auftrag.get('glb') or auftrag.get('texturen')) and self.pose is not None:
                # Erst die groben Teile binden (schnell: ~15.000 Punkte) — die dichten Kopien der Fototextur
                # erben die Gewichte über die Unterteilung.
                self.bindung = self.bindung or Kostuembindung(self.rig, self.koerper)
                eintrag['bindung_mm'] = self.bindung.binden(teile, self.pose.punkte())
            if auftrag.get('texturen'):
                # Fotoprojektion: dichte Kopien der Teile und der Körper bekommen Vertexfarben aus den
                # Vorlagen
                exportteile, farbig = self._textur(auftrag, teile, ordner, eintrag)
            if auftrag.get('glb') and self.pose is not None:
                eintrag['glb'] = self._glb(
                    self.rig, self.koerper, exportteile, ordner, auftrag.get('haltung', True), farbig
                )
            if auftrag.get('sicht') and farbig and huelle is not None:
                # Das zweite Modell: der Sichtkörper der Vorlage mit Fototextur (`Sichtmodell`)
                from effekte.blender.kostuem.sichtmodell import Sichtmodell

                dichte, abbildungen = self._textur_stand
                eintrag.update(Sichtmodell(self).bauen(auftrag, huelle, teile, dichte, abbildungen, ordner))
            if auftrag.get('blend'):
                if (
                    farbig
                ):  # die groben Teile stehen neben den dichten Kopien — in der .blend nur die farbigen zeigen
                    for o in teile:
                        o.hide_viewport = o.hide_render = True
                eintrag['blend'] = self._blend(ordner)
            bericht['kandidaten'][k['name']] = eintrag
        bericht['sekunden'] = round(time.perf_counter() - t0, 1)
        return bericht

    def _foto(self, texturen):
        """Die Fototextur der Vorlagen — je Satz Bilder einmal geladen (sie ändern sich im Lauf nicht)."""
        schluessel = json.dumps(texturen, sort_keys=True)
        if self._fotoschluessel != schluessel:
            from effekte.blender.kostuem.fototextur import Fototextur

            self.foto = Fototextur(texturen, self.projektion)
            self._fotoschluessel = schluessel
        return self.foto

    def _textur(self, auftrag, teile, ordner, eintrag):
        """Vertexfarben aus den Vorlagen (`Fototextur`) auf dichte Kopien der Teile und auf den Körper, dazu
        Renders der `textur_winkel` mit diesen Farben. → (die Teile für den Export, True). Die flachen Renders
        der `winkel` müssen die Winkel der Vorlagen enthalten: Ihr Umriss legt die Projektion fest."""
        foto = self._foto(auftrag['texturen'])
        flach = eintrag['bilder']
        abbildungen = {
            w: self.projektion.abbildung(os.path.join(ordner, flach[str(int(round(w)))]))
            for w in foto.bilder
            if str(int(round(w))) in flach
        }
        dichte = [foto.verdichten(o, self.rig) for o in teile]
        for o in dichte:
            foto.einfaerben(o, abbildungen, ausgewertet=self.pose is not None)
        foto.einfaerben(self.koerper, abbildungen, ausgewertet=True)
        self._textur_stand = (dichte, abbildungen)  # für das Sichtmodell (`abarbeiten`)
        winkel = auftrag.get('textur_winkel')
        if winkel:
            for o in teile:
                o.hide_render = True
            eintrag['textur_bilder'] = self.ansichten.rendern(winkel, ordner, 'textur_', 'VERTEX')
            for o in teile:
                o.hide_render = False
        return dichte, True

    # ------------------------------------------------------------ Betriebsarten

    def fahren(self):
        """Einmalig: Körper laden, den Auftrag abarbeiten, `bericht.json` schreiben."""
        t0 = time.perf_counter()
        aus = os.path.abspath(self.a['aus'])
        os.makedirs(aus, exist_ok=True)
        self.vorbereiten()
        bericht = self.abarbeiten(self.a)
        bericht['sekunden'] = round(time.perf_counter() - t0, 1)
        self._schreiben(os.path.join(aus, 'bericht.json'), bericht)
        self.melden('Kostuem: fertig in %.1f s' % bericht['sekunden'])

    def dienst(self):
        """Körper laden, `bereit.json` schreiben, dann Befehle aus dem Postfach abarbeiten."""
        postfach = os.path.abspath(self.a['dienst'])
        self.vorbereiten()
        self._schreiben(os.path.join(postfach, 'bereit.json'), {'pid': os.getpid(), 'kopf': self.kopf})
        self.melden('Kostuem: bereit')
        letzte = time.time()
        while time.time() - letzte < self.LEERLAUF_S:
            befehle = sorted(glob.glob(os.path.join(postfach, 'befehl_*.json')))
            if not befehle:
                time.sleep(self.TAKT_S)
                continue
            pfad = befehle[0]
            nummer = os.path.basename(pfad)[len('befehl_') : -len('.json')]
            try:
                with open(pfad, encoding='utf-8') as f:
                    auftrag = json.load(f)
                os.remove(pfad)
            except (OSError, ValueError):
                time.sleep(self.TAKT_S)  # wird noch geschrieben
                continue
            if auftrag.get('ende'):
                break
            try:
                antwort = self.abarbeiten(auftrag)
            except Exception:  # noqa: BLE001 — der Fehler geht an den Vater, der Dienst bleibt bereit
                antwort = {'fehler': traceback.format_exc()[-1500:]}
            self._schreiben(os.path.join(postfach, 'antwort_%s.json' % nummer), antwort)
            letzte = time.time()
        self.melden('Kostuem: Dienst beendet')

    @staticmethod
    def _schreiben(pfad, daten):
        """Unteilbar: erst in eine Nebendatei, dann ersetzen — der Leser sieht nie eine halbe Datei."""
        neben = pfad + '.tmp'
        with open(neben, 'w', encoding='utf-8') as f:
            json.dump(daten, f, ensure_ascii=False, indent=1)
        os.replace(neben, pfad)

    # ------------------------------------------------------------------ Ablage

    @classmethod
    def _glb(cls, rig, koerper, teile, ordner, haltung, vertexfarbe=False, name='kostuem.glb'):
        """Figur MIT Kostüm und Rig (Edgar: „bitte auch Modell in den Runden"). `haltung`: die Knoten tragen
        die gestellte Haltung (Runden — die GLB zeigt, was benotet wurde); sonst die Ruhelage des Rigs
        (Ergebnis — für Bewegung auf Genesis 9, dieselbe Ruhelage wie `figur.glb`)."""
        for obj in [koerper, *teile]:
            for mat in obj.data.materials:
                cls._grundfarbe(mat, weiss=vertexfarbe)
        bpy.ops.object.select_all(action='DESELECT')
        for o in [rig, koerper, *teile]:
            o.select_set(True)
        # Vertexfarben (Fototextur):  schreibt COLOR_0; die Grundfarbe der Materialien ist dann
        # weiß, sonst würde sie mit der Vertexfarbe malgenommen (gemessen an einer Kugel, 30.09.2026).
        farbe = {'export_vertex_color': 'ACTIVE'} if vertexfarbe else {}
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(ordner, name),
            use_selection=True,
            export_apply=True,
            export_yup=True,
            export_rest_position_armature=not haltung,
            **farbe,
        )
        if vertexfarbe:
            cls._farben_ablegen(teile, os.path.join(ordner, name))
        return name

    @staticmethod
    def _farben_ablegen(teile, glb):
        """Die flachen Materialfarben der Teile neben die GLB (`<name>.farben.json`): Ihre Materialien sind weiß, die
        Farbe steckt in den Vertexfarben, und der Blender-Film (Workbench, Modus „Textur") zeigt keine Vertexfarben. Ein
        glTF-Zusatzfeld (`extras`) kam nicht in der Datei an (gemessen 30.09.2026) — daher die Begleitdatei."""
        farben = {
            mat.name: [round(c, 4) for c in mat.diffuse_color[:3]]
            for obj in teile
            for mat in obj.data.materials
            if mat is not None
        }
        with open(os.path.splitext(glb)[0] + '.farben.json', 'w', encoding='utf-8') as f:
            json.dump(farben, f)

    @staticmethod
    def _grundfarbe(mat, weiss=False):
        """Der glTF-Export liest die Grundfarbe des Principled-Knotens, nicht die Ansichtsfarbe, mit der
        Workbench rendert — ohne das käme alles in Blenders Grau an."""
        baum = mat.node_tree if mat is not None else None
        knoten = baum.nodes.get('Principled BSDF') if baum is not None else None
        if knoten is None or knoten.inputs['Base Color'].is_linked:
            return
        knoten.inputs['Base Color'].default_value = (
            (1.0, 1.0, 1.0, 1.0) if weiss else tuple(mat.diffuse_color)
        )

    @staticmethod
    def _blend(ordner):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ordner, 'zauberer.blend'), copy=True)
        return 'zauberer.blend'


def main():
    rest = sys.argv[sys.argv.index('--') + 1 :] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--auftrag', required=True)
    with open(p.parse_args(rest).auftrag, encoding='utf-8') as f:
        bau = Kostuembau(json.load(f))
    if bau.a.get('dienst'):
        bau.dienst()
    else:
        bau.fahren()


if __name__ == '__main__':
    main()
