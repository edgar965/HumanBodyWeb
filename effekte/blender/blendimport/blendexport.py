# -*- coding: utf-8 -*-
"""Blendexport — die Netze einer fremden .blend als Rohdaten ablegen (Blender-Import, 08.10.2026).

Aufruf (aus `core/dienste/blendimportblender.py`), MIT `--factory-startup` (siehe `modellexportblend.py`):

    blender -b --factory-startup <quelle.blend> --python blendexport.py -- --ziel <ordner>

Je Netz, das an einer Armatur hängt (Körper, Kleider, Haar, Augen, Zähne), eine `<nummer>.npz` mit den Punkten so,
wie Blender sie zeigt (ausgewertet, Weltkoordinaten, Blender-Achsen: Meter, Z oben), Dreiecken, UV je Dreiecksecke und
der Summe der Hautgewichte je Knochen; dazu `inventar.json` mit Bildern je Materialkanal (absolute Pfade) und Maßen.
Die Rolle (Körper, Kleid, Haar, …) entscheidet python14 (`Blendimportrollen`) — hier wird nur gelesen, nichts an der
.blend geändert. Steuerformen von Rigs (`cs_*`, `WGT-*`, Netze ohne Flächen) fallen weg.

Hat die Datei GAR KEINE Armatur (Character-Creator-Export, 15 Netze, gemessen 09.10.2026), kommen alle Netze ohne
Hautgewichte heraus und das Inventar trägt `ohne_rig: true` — der Import überspringt dann das Umposen. Ist das höchste
Netz nicht 0,5–2,5 m hoch (die Asian girl: 3,26 m), werden alle Punkte auf 1,75 m umgerechnet (`massstab`, `hoehe_original_m`
im Inventar); mit Rig bleibt der Maßstab, wie er ist.

Gemessen an `cute girl 5.0.blend` (08.10.2026): Körper 54.369 Punkte, Haar 34.637, Shirt 8.045, Jeans 5.272, je Auge
770, Zähne/Zunge 5.766; die Bilder liegen NICHT gepackt neben der Datei (`//textures\\…`).
"""

import argparse
import json
import os
import sys

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np


class Blendexport:
    #: Steuerformen der Rigs (Auto-Rig Pro `cs_*`, Rigify `WGT-*`) sind keine Netze der Figur.
    STEUERFORMEN = ('cs_', 'WGT-')
    #: Eingänge des Principled BSDF → Kanalname der Ablage.
    KANAELE = {'Base Color': 'farbe', 'Roughness': 'rauheit', 'Alpha': 'alpha', 'Normal': 'normalen'}
    #: Höhe, auf die ein Modell OHNE Rig gebracht wird, wenn es nicht als Mensch in Metern gelten kann (Genesis' Ruhehöhe).
    #: „Mesh to 3D" liest Längen über 3 als Zentimeter (`meshfigur_scan.einheit_anpassen`): die Asian girl misst 3,26 m, wurde so
    #: auf 3,3 cm geschrumpft, und die Posenerkennung fand nichts („index 11 is out of bounds … size 0", 09.10.2026).
    REFERENZ_M = 1.75
    PLAUSIBEL_M = (0.5, 2.5)

    def __init__(self, ziel):
        self.ziel = ziel
        #: Maßstab, mit dem alle Punkte geschrieben werden (1,0 = Original); nur bei einer Datei ohne Rig ≠ 1.
        self.faktor = 1.0
        os.makedirs(ziel, exist_ok=True)

    @classmethod
    def massstab(cls, hoehe_m):
        """1,0 für eine Höhe, die ein stehender Mensch haben kann; sonst der Faktor, der sie auf `REFERENZ_M` bringt."""
        if cls.PLAUSIBEL_M[0] <= hoehe_m <= cls.PLAUSIBEL_M[1] or hoehe_m <= 0:
            return 1.0
        return cls.REFERENZ_M / hoehe_m

    @staticmethod
    def hoehe(obj, graph):
        """Höhe (Welt-Z) der ausgewerteten Begrenzungsbox eines Objekts in Metern."""
        ecken = np.array(obj.evaluated_get(graph).bound_box, dtype=np.float64)
        welt = np.array(obj.matrix_world, dtype=np.float64)
        z = ecken @ welt[2, :3] + welt[2, 3]
        return float(z.max() - z.min())

    @staticmethod
    def argumente(argv):
        parser = argparse.ArgumentParser(prog='blendexport')
        parser.add_argument('--ziel', required=True)
        trenner = argv.index('--') if '--' in argv else len(argv)
        return parser.parse_args(argv[trenner + 1:])

    # ----------------------------------------------------------------- Netze

    def netze(self):
        aus = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.name.startswith(self.STEUERFORMEN) or not len(obj.data.polygons):
                continue
            if not any(m.type == 'ARMATURE' and m.object for m in obj.modifiers):
                continue
            aus.append(obj)
        if not aus and not len(bpy.data.armatures):
            # Eine Datei ganz ohne Skelett (Character-Creator-Export, gemessen 09.10.2026 an „Beautiful Asian girl"): alle
            # Netze, ohne Hautgewichte. Die Rollen kommen dann aus Maßen, Material und Namen (`Blendimportrollen`).
            aus = [o for o in bpy.data.objects
                   if o.type == 'MESH' and not o.name.startswith(self.STEUERFORMEN) and len(o.data.polygons)]
        return aus

    def netz(self, obj, nummer, graph):
        auswertung = obj.evaluated_get(graph)
        me = auswertung.to_mesh()
        try:
            me.calc_loop_triangles()
            n = len(me.vertices)
            co = np.empty(n * 3, dtype=np.float64)
            me.vertices.foreach_get('co', co)
            welt = np.array(obj.matrix_world, dtype=np.float64)
            punkte = (co.reshape(-1, 3) @ welt[:3, :3].T + welt[:3, 3]) * self.faktor
            t = len(me.loop_triangles)
            dreiecke = np.empty(t * 3, dtype=np.int64)
            me.loop_triangles.foreach_get('vertices', dreiecke)
            schleifen = np.empty(t * 3, dtype=np.int64)
            me.loop_triangles.foreach_get('loops', schleifen)
            material = np.empty(t, dtype=np.int64)
            me.loop_triangles.foreach_get('material_index', material)
            uv_ecken = np.zeros((t * 3, 2), dtype=np.float64)
            if me.uv_layers.active is not None:
                uv = np.empty(len(me.loops) * 2, dtype=np.float64)
                me.uv_layers.active.data.foreach_get('uv', uv)
                uv_ecken = uv.reshape(-1, 2)[schleifen]
        finally:
            auswertung.to_mesh_clear()
        datei = '%02d.npz' % nummer
        np.savez_compressed(os.path.join(self.ziel, datei), punkte=punkte, dreiecke=dreiecke.reshape(-1, 3),
                            uv_ecken=uv_ecken.reshape(-1, 3, 2), material=material)
        return {
            'name': obj.name,
            'datei': datei,
            'punkte': int(n),
            'dreiecke': int(t),
            'min': [round(float(v), 4) for v in punkte.min(axis=0)],
            'max': [round(float(v), 4) for v in punkte.max(axis=0)],
            'materialien': [self.material(slot.material) for slot in obj.material_slots],
            'gewichte': self.gewichte(obj),
        }

    @staticmethod
    def gewichte(obj):
        """`{knochen: Summe der Gewichte}` — nur benutzte Gruppen, absteigend."""
        namen = {g.index: g.name for g in obj.vertex_groups}
        summe = {}
        for v in obj.data.vertices:
            for g in v.groups:
                if g.weight > 0 and g.group in namen:
                    summe[namen[g.group]] = summe.get(namen[g.group], 0.0) + g.weight
        return {k: round(w, 2) for k, w in sorted(summe.items(), key=lambda kv: -kv[1])}

    # ------------------------------------------------------------ Materialien

    def material(self, mat):
        """`{name, farbe, rauheit, alpha, normalen, ueberblendung}` — je Kanal das Bild (absoluter Pfad) oder None."""
        aus = {'name': mat.name if mat else '', 'ueberblendung': getattr(mat, 'blend_method', '') if mat else ''}
        if not mat or not mat.node_tree:
            return aus
        for knoten in mat.node_tree.nodes:
            if knoten.type != 'BSDF_PRINCIPLED':
                continue
            for eingang, kanal in self.KANAELE.items():
                buchse = knoten.inputs.get(eingang)
                if buchse is not None and buchse.is_linked:
                    fest = self.festfarbe(buchse.links[0].from_node) if kanal == 'farbe' else None
                    if fest is not None:
                        aus['farbe_wert'] = fest
                        continue
                    aus[kanal] = self.bild_vor(buchse.links[0].from_node, set())
                    if kanal == 'alpha':
                        aus['alpha_ausgang'] = self.ausgang(buchse.links[0])
            aus.update(self.detailnormale(knoten, mat.name))
        return aus

    @staticmethod
    def ausgang(link):
        """Welche Buchse des Bildknotens speist Alpha: `Alpha` (die Deckkraft des Bilds) oder `Color` (ein Graubild, dessen
        Alpha-Kanal überall 1 ist — die Maske steht in R = G = B). Gemessen 09.10.2026 an „Asian girl": `hair1_alpha.png` und
        `bra_alpha.png` (Non-Color, Ausgang `Color`, Alpha-Kanal 255 überall) gegen `sock_basecolor.png` und
        `eyelashes_basecolor_opacity.png` (sRGB, Ausgang `Alpha`). Wer immer den Alpha-Kanal nahm, bekam für das Haar eine
        weiße Karte — volle Haarkarten statt einzelner Strähnen. Läuft die Kette über weitere Knoten, bleibt `Alpha`."""
        return link.from_socket.name if link.from_node.type == 'TEX_IMAGE' else 'Alpha'

    def detailnormale(self, bsdf, materialname):
        """Eine ZWEITE Normalenkarte mit Kachelung: der Normal-Eingang hängt an einem Vector-Math-Knoten über zwei
        Normal-Map-Knoten, der zweite trägt eine kleine Detailnormale, die das Mapping vielfach wiederholt. Gemessen
        08.10.2026 an „cute girl": Bluse `ACVI_Detail_Cloth_Cotton3_Normal.dds` (256 px) mit Mapping-Skalierung 75 × 75 —
        das Fischgrät-Gewebe —, Jeans dasselbe Bild 25 × 25. Gibt `{detailnormalen: <PNG im Export>, detail_kachel: [u, v]}`
        oder `{}`. Ein DDS liest der Browser nicht: das Bild wird als PNG neben den Export gelegt (Pixel unverändert, das
        Bild ist „Non-Color")."""
        buchse = bsdf.inputs.get('Normal')
        if buchse is None or not buchse.is_linked or buchse.links[0].from_node.type != 'VECT_MATH':
            return {}
        karten = [b.links[0].from_node for b in buchse.links[0].from_node.inputs
                  if b.is_linked and b.links[0].from_node.type == 'NORMAL_MAP']
        if len(karten) < 2:
            return {}
        bildknoten = self.bildknoten_vor(karten[1], set())
        if bildknoten is None:
            return {}
        pfad = self.bildpfad(bildknoten.image)
        if not pfad.lower().endswith('.png'):
            pfad = self.als_png(bildknoten.image, 'detail_%s.png' % ''.join(c if c.isalnum() else '_' for c in materialname))
        return {'detailnormalen': pfad, 'detail_kachel': self.kachelung(bildknoten)}

    def bildpfad(self, bild):
        """Absoluter Pfad der Bilddatei. Fehlt die Datei und ist das Bild in die .blend GEPACKT (Character Creator bettet seine Texturen
        ein und merkt sich nur den Pfad seines Temp-Ordners — „Daven.blend": 70 von 72 Bildern gepackt, alle Pfade unter
        `C:\\Users\\<Autor>\\AppData\\Local\\Temp\\CharacterCreator4Temp`, gemessen 09.10.2026), schreibt der Export die Bytes unverändert nach
        `<ziel>/bilder/<Bildname><Endung>` und gibt diesen Pfad zurück."""
        roh = bpy.path.abspath(bild.filepath, library=bild.library) if bild.filepath else ''
        pfad = os.path.normpath(roh) if roh else ''
        if (pfad and os.path.isfile(pfad)) or bild.packed_file is None:
            return pfad
        ordner = os.path.join(self.ziel, 'bilder')
        os.makedirs(ordner, exist_ok=True)
        endung = os.path.splitext(pfad)[1] or '.png'
        name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in bild.name)
        ziel = os.path.join(ordner, name if name.lower().endswith(endung.lower()) else name + endung)
        if not os.path.isfile(ziel):
            with open(ziel, 'wb') as datei:
                datei.write(bild.packed_file.data)
        return ziel

    def als_png(self, bild, dateiname):
        """Die Pixel eines Bilds unverändert als PNG neben den Export legen (über eine Kopie: `filepath_raw` am geladenen
        Bild zu ändern verwirft dessen Daten — „does not have any image data", gemessen 08.10.2026) — absoluter Pfad."""
        breite, hoehe = bild.size
        pixel = np.empty(breite * hoehe * 4, dtype=np.float32)
        bild.pixels.foreach_get(pixel)
        kopie = bpy.data.images.new(os.path.splitext(dateiname)[0], breite, hoehe, alpha=True, float_buffer=False)
        kopie.colorspace_settings.name = 'Non-Color'
        kopie.pixels.foreach_set(pixel)
        ziel = os.path.join(self.ziel, dateiname)
        kopie.filepath_raw = ziel
        kopie.file_format = 'PNG'
        kopie.save()
        return ziel

    def bildknoten_vor(self, knoten, gesehen):
        """Der erste Bildknoten stromaufwärts von `knoten` (mit Bild) oder None."""
        if knoten is None or knoten.name in gesehen:
            return None
        gesehen.add(knoten.name)
        if knoten.type == 'TEX_IMAGE' and knoten.image is not None:
            return knoten
        for buchse in knoten.inputs:
            if buchse.is_linked:
                treffer = self.bildknoten_vor(buchse.links[0].from_node, gesehen)
                if treffer is not None:
                    return treffer
        return None

    @staticmethod
    def kachelung(bildknoten):
        """Skalierung (u, v) des Mapping-Knotens vor dem Bild; ohne Mapping `[1.0, 1.0]`."""
        vektor = bildknoten.inputs.get('Vector')
        if vektor is not None and vektor.is_linked and vektor.links[0].from_node.type == 'MAPPING':
            skala = vektor.links[0].from_node.inputs['Scale'].default_value
            return [round(float(skala[0]), 4), round(float(skala[1]), 4)]
        return [1.0, 1.0]

    @staticmethod
    def festfarbe(knoten):
        """Ein Mix-Knoten (Farbe, Überblendung „Mix", gleichmäßig) mit Faktor 0 oder 1 und festem Eingang an der Stelle, die
        zählt, ergibt eine FESTE Farbe — das Bild davor trägt dann nichts bei. Gemessen 08.10.2026 am Haar von „cute
        girl": Faktor 1,0, B = (0,0232 | 0,0062 | 0,0041) linear; das PNG liefert nur die Deckkraft, seine Farbe
        (Mittel 0,49 | 0,36 | 0,40, Streuung ~0,18) ist Rohmaterial. Gibt `[r, g, b]` (linear) oder None."""
        if knoten.type != 'MIX' or knoten.data_type != 'RGBA' or knoten.blend_type != 'MIX' \
                or knoten.factor_mode != 'UNIFORM':
            return None
        faktor = next((b for b in knoten.inputs if b.identifier == 'Factor_Float'), None)
        if faktor is None or faktor.is_linked or not (faktor.default_value >= 0.999 or faktor.default_value <= 0.001):
            return None
        eingang = next((b for b in knoten.inputs if b.identifier == ('B_Color' if faktor.default_value >= 0.999
                                                                       else 'A_Color')), None)
        if eingang is None or eingang.is_linked:
            return None
        return [round(float(w), 5) for w in eingang.default_value[:3]]

    def bild_vor(self, knoten, gesehen):
        """Das erste Bild stromaufwärts (über Mix-, Normal-Map- und andere Knoten) — absoluter Pfad oder None."""
        if knoten is None or knoten.name in gesehen:
            return None
        gesehen.add(knoten.name)
        if knoten.type == 'TEX_IMAGE' and knoten.image is not None:
            return self.bildpfad(knoten.image) or None
        # Normal Map: zuerst ihr Farbeingang; Mix: die Eingänge der Reihe nach.
        for buchse in knoten.inputs:
            if buchse.is_linked:
                bild = self.bild_vor(buchse.links[0].from_node, gesehen)
                if bild:
                    return bild
        return None

    # ------------------------------------------------------------------ Lauf

    def laufen(self):
        graph = bpy.context.evaluated_depsgraph_get()
        mit_rig = self.netze()
        ohne_rig = not len(bpy.data.armatures) and bool(mit_rig)
        hoehe_original = max((self.hoehe(o, graph) for o in mit_rig), default=0.0)
        if ohne_rig:
            # Nur ohne Rig: `blendumposen.py` liest die Punkte später selbst aus der .blend und schriebe das Original zurück.
            self.faktor = self.massstab(hoehe_original)
        netze = [self.netz(obj, i, graph) for i, obj in enumerate(mit_rig)]
        inventar = {
            'blender': bpy.app.version_string,
            'datei': bpy.data.filepath,
            'einheit': bpy.context.scene.unit_settings.scale_length,
            'netze': netze,
            # Was die Datei sonst enthält: Netze ohne Armatur-Modifikator werden nicht exportiert (der Import
            # braucht Hautgewichte) — hat die Datei kein Skelett, steht es hier statt „kein Körper".
            'armaturen': len(bpy.data.armatures),
            'ohne_rig': ohne_rig,
            # Die Punkte der Netze sind mit `massstab` multipliziert; `hoehe_original_m` ist die Höhe des höchsten Netzes davor.
            'massstab': self.faktor,
            'hoehe_original_m': round(hoehe_original, 4),
            'ohne_armatur': [o.name for o in bpy.data.objects
                             if o.type == 'MESH' and not o.name.startswith(self.STEUERFORMEN)
                             and len(o.data.polygons) and o not in mit_rig],
        }
        with open(os.path.join(self.ziel, 'inventar.json'), 'w', encoding='utf-8') as f:
            json.dump(inventar, f, ensure_ascii=False, indent=1)
        print('[blendexport] %d Netze nach %s' % (len(netze), self.ziel))


if __name__ == '__main__':
    Blendexport(Blendexport.argumente(sys.argv).ziel).laufen()
