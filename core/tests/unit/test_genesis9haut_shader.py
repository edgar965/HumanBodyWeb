# -*- coding: utf-8 -*-
"""Der Durchlicht-Shader (`gemeinsam/genesis9haut.js`) übersteht Threes
ausgerollte Lichtschleife.

BEFUND (17.09.2026): Three ersetzt `#pragma unroll_loop_start … end` durch
eine Kopie des Rumpfs je Richtungslicht — im selben Block. Eine Deklaration
IM Rumpf (`vec3 lichtweg = …`) stand in der Szene mit drei Lichtern dreimal
da: „'lichtweg' : redefinition", der Fragment-Shader kompilierte nicht, die
Figur war unsichtbar. Die Sichtprobe mit EINEM Licht hatte das nicht gezeigt.

Das Modul importiert `three` — der Node-Harness löst das nicht auf, deshalb
wird der Quelltext gelesen: die Einhängung aus `genesis9haut.js`, die
GLSL-Stücke aus `genesis9hautglsl.js` (seit 18.09.2026 abends getrennt).
Sabotage-Gegenprobe: `vec3 lichtweg = …` zurück in den Rumpf → Fall 1 rot;
`step( 0.5, basisN )` im Overlay auf `step( 0.5, glitzer.xyz )` → Fall 6 rot.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class DurchlichtShader(SimpleTestCase):
    databases = set()

    @staticmethod
    def quelltext(datei='genesis9haut.js'):
        pfad = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'gemeinsam' / datei
        return pfad.read_text(encoding='utf-8')

    @classmethod
    def glsl(cls):
        return cls.quelltext('genesis9hautglsl.js')

    def rumpf(self):
        text = self.glsl()
        treffer = re.search(r'#pragma unroll_loop_start(.*?)#pragma unroll_loop_end', text, re.S)
        self.assertIsNotNone(treffer, 'keine ausgerollte Schleife im Shader')
        return treffer.group(1)

    def test_1_keine_deklaration_im_schleifenrumpf(self):
        # Der Schleifenkopf (`int i = 0`) gehört Three; geprüft wird der Rumpf.
        rumpf = self.rumpf().split('{', 1)[1]
        self.assertIsNone(
            re.search(r'\b(vec[234]|float|int)\s+\w+\s*=', rumpf),
            'Deklaration im Rumpf — nach dem Ausrollen doppelt:\n' + rumpf,
        )

    def test_2_schleife_liest_richtungslichter_mit_index(self):
        rumpf = self.rumpf()
        self.assertIn('directionalLights[ i ]', rumpf)
        self.assertIn('geometryViewDir', rumpf)

    def test_3_einhaengepunkte_und_uniforms(self):
        text = self.quelltext()
        for stueck in (
            '#include <lights_fragment_end>',
            'uDurchlicht',
            'uDurchlichtFarbe',
            'attribute float dicke',
            'vDuenne',
            'customProgramCacheKey',
        ):
            self.assertIn(stueck, text)

    def test_4_schminke_mischt_hinter_map_und_roughnessmap(self):
        """Schminke (18.09.2026): `mix(diffuseColor, farbe, gewicht)` hinter
        `map_fragment`, der Rauheitsfaktor hinter `roughnessmap_fragment`, das
        Gewicht `g9Schminke` VOR `map_fragment` deklariert (beide Bloecke lesen es)."""
        text = self.quelltext()
        for stueck in (
            'uSchminkeFarbe',
            'uSchminkeGewicht',
            'uSchminkeRauheit',
            'uSchminkeAn',
            r"'#include <roughnessmap_fragment>\n' "
            r'+ Genesis9hautGLSL.RAUHEIT',
            r"'float g9Schminke = 0.0;\n#include <map_fragment>\n'",
        ):
            self.assertIn(stueck, text, stueck)
        glsl = self.glsl()
        self.assertIn(
            'diffuseColor.rgb = mix( diffuseColor.rgb, schminkeFarbe.rgb, g9Schminke )',
            Genesis9hautQuelle.glsl(glsl, 'SCHMINKE'),
        )
        rauheit = Genesis9hautQuelle.glsl(glsl, 'RAUHEIT')
        # R = Faktor (Ursulas `Makeup Roughness Mult`), G/B = Ersatz mit Gewicht
        # (die `_R_`-Karten des Makeup-Systems ueber der Hautrauheit).
        self.assertIn('roughnessFactor *= mix( 1.0, schminkeRauheit.r, g9Schminke )', rauheit)
        self.assertIn('mix( roughnessFactor, schminkeRauheit.g, schminkeRauheit.b * uSchminkeAn )', rauheit)

    def test_5_detailnormalen_als_rnm_an_stelle_von_normal_fragment_maps(self):
        """8K-Detailnormalen (18.09.2026): Reoriented Normal Mapping wie MDLs
        `base::blend_normals` — n1.z += 1, n2.xy negiert, n1·dot/n1.z − n2 —
        an Stelle von `normal_fragment_maps` im Tangentenraum-Fall, sonst der
        Original-Include; Gewicht `uDetailGewicht`, Schalter `uDetailAn`."""
        text = self.quelltext()
        self.assertIn(
            "'#include <normal_fragment_maps>',\n                    Genesis9hautGLSL.normalen(", text
        )
        glsl = self.glsl()
        detail = Genesis9hautQuelle.glsl(glsl, 'DETAIL')
        for stueck in (
            'n1.z += 1.0;',
            'n2.xy = -n2.xy;',
            'vec3 gemischt = n1 * dot( n1, n2 ) / n1.z - n2;',
            'normal = normalize( tbn * gemischt );',
            'mix( vec3( 0.0, 0.0, 1.0 ), detailN, uDetailGewicht * uDetailAn )',
        ):
            self.assertIn(stueck, detail, stueck)
        rahmen = glsl[glsl.index('static normalen(') :]
        for stueck in (
            '#if defined( USE_NORMALMAP_TANGENTSPACE )',
            'vec3 mapN = basisN * 2.0 - 1.0;',
            'mapN.xy *= normalScale;',
            '#else\n    #include <normal_fragment_maps>',
        ):
            self.assertIn(stueck, rahmen, stueck)
        # Der Programmschluessel unterscheidet Material mit und ohne Detail.
        self.assertIn("zusatz.detail ? 'd' : 'x'", text)

    def test_6_glitzer_normalen_als_w3c_overlay_ueber_der_hautnormale(self):
        """Snow Queens Glitzer (18.09.2026 abends): Daz' LIE legt die Ebene mit
        `blend_overlay` UEBER die Normalenkarte — im Bildraum 0..1: Cb <= 0,5 ->
        2·Cb·Cs, sonst 1 − 2(1−Cb)(1−Cs); gemischt mit Alpha × Schalter, Modus
        1 = Overlay, 0 = Ersatz."""
        glitzer = Genesis9hautQuelle.glsl(self.glsl(), 'GLITZER')
        for stueck in (
            'texture2D( uSchminkeNormalen, vNormalMapUv )',
            'mix( 2.0 * basisN * glitzer.xyz,',
            '1.0 - 2.0 * ( 1.0 - basisN ) * ( 1.0 - glitzer.xyz ),',
            'step( 0.5, basisN ) );',
            'mix( glitzer.xyz, ueberlagert, uSchminkeNormalenModus )',
            'basisN = mix( basisN, ueberlagert, glitzer.a * uSchminkeNormalenAn )',
        ):
            self.assertIn(stueck, glitzer, stueck)
        text = self.quelltext()
        self.assertIn("uSchminkeNormalenModus.value = werte.normalenmodus === 'overlay' ? 1 : 0", text)

    def test_7_klarlackfarbe_und_bump(self):
        """Irays Top Coat Color toent die Klarlackschicht (`pbr_skin.mdl`:
        `ggx(tint: top_coat_color)`): Faktor am Clearcoat-Anteil der Ausgabe;
        Top Coat Bump Weight = Hautnormale als `clearcoatNormalMap` mit der
        Skalierung = Weight (Vorzeichen der DirectX-Achse bleibt)."""
        glsl = self.glsl()
        summe = '( clearcoatSpecularDirect + clearcoatSpecularIndirect )'
        self.assertIn("KLARLACK_ALT = '%s * material.clearcoat;'" % summe, glsl)
        self.assertIn("KLARLACK_NEU = '%s * material.clearcoat * uKlarlackFarbe;'" % summe, glsl)
        text = self.quelltext()
        for stueck in (
            '.replace(Genesis9hautGLSL.KLARLACK_ALT, Genesis9hautGLSL.KLARLACK_NEU)',
            'uniform vec3 uKlarlackFarbe;',
            'material.clearcoatNormalMap = material.normalMap;',
            'material.clearcoatNormalScale.set(w, w * Math.sign(material.normalScale.y || 1))',
            "zusatz.klarlack ? 'k' : 'x'",
        ):
            self.assertIn(stueck, text, stueck)


class Genesis9hautQuelle:
    """Ein GLSL-Block (`static NAME = ...`) aus dem Modultext."""

    @staticmethod
    def glsl(text, name):
        anfang = text.index('static %s = `' % name)
        ende = text.index('`;', anfang + len(name) + 10)
        return text[anfang:ende]
