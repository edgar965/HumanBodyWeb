# -*- coding: utf-8 -*-
u"""Oberflächenbindung und Körperlage im Browser (Konzept Fitting, 21.09.2026) — am Quelltext.

Warum Quelltext statt Node: `koerperlage.js` und `oberflaechenbindung.js` hängen an
Three (RenderTarget, Points, Shaderpatch); geprüft wird, was in den Sichtproben
die Fehler machte:

1. Die Körperlage zeichnet OHNE Index: ein indiziertes `Points` zeichnet nur die Punkte
   im Index, und die Hautmaske nimmt verdeckte Dreiecke heraus — der gebundene Stoff
   schoss zum Ursprung (Spitzen zu einer senkrechten Linie). Eigene Geometrie, die
   Attribute teilt, `setDrawRange`; der Bildstempel wird NACH den eigenen Renderläufen
   gelesen (jeder zählt `info.render.frame` hoch).
2. Die Kapseln (Schicht 3) drücken FREIE Punkte immer, GEBUNDENE nur aus FREMDEN
   Gliedmaßen (`bindgruppe` vs. der Gruppe der Kapsel, seit 22.09.2026 — davor liefen
   sie nur bei `mischung <= 0.0`, und ein Arm konnte ein gebundenes Hosenbein nie aus
   sich herausdrücken). Die Kapseln sind 90. Perzentil der Haut und drückten
   halbgebundene Punkte der EIGENEN Gliedmaße 3,8 cm heraus (Sandale als Fleck) —
   der Gruppenfilter verhindert das weiterhin, ohne fremde Gliedmaßen auszuschließen.
3. Die Bindung gilt nur, wenn Körper und Bindung auf derselben Stufe stehen, und die
   Uniform-Objekte entstehen einmal je Material.
4. Verdrahtung: `Genesis9kleidung.anziehen` legt die Attribute an, `Genesis9Modell._einhaengen`
   verdrahtet (auch nach jedem Neubinden), `genesis9modell.js` importiert die Hautverdeckung
   (Schicht 1 auf allen Seiten), `stoffkapseln.js` liegt in `gemeinsam/` ohne `state.js`.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class OberflaechenbindungJsTest(SimpleTestCase):
    databases = set()

    def test_1_koerperlage_ohne_index_stempel_danach(self):
        text = quelltext('gemeinsam', 'koerperlage.js')
        self.assertIn('const lage = new THREE.BufferGeometry();', text)
        self.assertIn('lage.setDrawRange(0, n);', text)
        self.assertIn('new THREE.Points(lage, material)', text)
        self.assertNotIn('new THREE.Points(geo, material)', text, 'nie die indizierte Koerpergeometrie')
        self.assertIn('punkte.isSkinnedMesh = true;', text)
        self.assertIn('s.bild = renderer.info.render.frame;', text)
        self.assertIn("static ATTRIBUTE = ['position', 'normal', 'skinIndex', 'skinWeight', 'punktnummer'];", text)

    def test_2_kapseln_fuer_alle_punkte_ausser_der_eigenen_gliedmasse(self):
        glsl = quelltext('gemeinsam', 'oberflaecheglsl.js')
        self.assertIn('if (uKapselAn > 0.5) {', glsl)
        self.assertNotIn('mischung <= 0.0) {', glsl, 'die Schleife laeuft jetzt fuer alle Punkte')
        self.assertIn('if (mischung > 0.0 && bindgruppe > 0.5 && abs(ka.w - bindgruppe) < 0.5) continue;', glsl)
        self.assertIn('attribute float bindgruppe;', glsl)
        self.assertIn('texelFetch(uKoerperLage', glsl)
        self.assertIn('#include <skinning_vertex>', glsl, 'die Bindung kommt NACH dem Skinning')

    def test_6_nur_hinaus_nie_hinziehen(self):
        """24.09.2026: Die erste Fassung SETZTE jeden gebundenen Punkt auf die
        Oberflaeche (`mix(transformed, q + d·n, mischung)`) — Sneaker und
        Schulternaht rissen, die Bindung war seit 23.09. aus. Jetzt wird nur
        geschoben, wo der Punkt tiefer liegt als in Ruhe (hoechstens `uLuft`)."""
        glsl = quelltext('gemeinsam', 'oberflaecheglsl.js')
        self.assertNotIn('mix(transformed, q + bindabstand * n, mischung)', glsl, 'keine Projektion mehr')
        self.assertIn('float tief = min(bindabstand, uLuft) - hoehe;', glsl)
        self.assertIn('if (tief > 0.0 && tief < uTiefGrenze && length(o - hoehe * n) < uSeitGrenze) {', glsl)
        self.assertIn('transformed += tief * n;', glsl)

    def test_7_schalter_aus_den_einstellungen(self):
        """Einstellungen → Kleider (24.09.2026, Vorgabe An): je Bild gelesen, nicht
        beim Verdrahten festgehalten — die Vorlieben kommen oft nach dem ersten Stueck."""
        text = quelltext('gemeinsam', 'oberflaechenbindung.js')
        self.assertIn("Kleidereinstellungen.an('kleider_oberflaechenbindung')", text)
        self.assertIn("Kleidereinstellungen.an('kleider_normalen_aus_flaeche')", text)
        self.assertNotIn('static AKTIV', text, 'kein fest verdrahteter Schalter mehr')
        einstellungen = quelltext('gemeinsam', 'kleidereinstellungen.js')
        self.assertIn('kleider_oberflaechenbindung: true,', einstellungen)
        self.assertIn('kleider_normalen_aus_flaeche: true,', einstellungen)
        pfad = Path(settings.BASE_DIR) / 'core' / 'api' / 'seite_kleider_einstellungen.py'
        seite = pfad.read_text(encoding='utf-8')
        self.assertIn("'kleider_oberflaechenbindung': '1',", seite, 'Seite und Browser mit derselben Vorgabe')
        self.assertIn("'kleider_normalen_aus_flaeche': '1',", seite)

    def test_8_normale_aus_der_flaeche_im_fragment(self):
        glsl = quelltext('gemeinsam', 'oberflaecheglsl.js')
        self.assertIn('#include <normal_fragment_begin>', glsl)
        self.assertIn('cross(dFdx(vViewPosition), dFdy(vViewPosition))', glsl)
        text = quelltext('gemeinsam', 'oberflaechenbindung.js')
        self.assertIn(".replace('#include <normal_fragment_begin>', OberflaecheGLSL.FRAGMENT)", text)

    def test_3_stufe_muss_passen_uniforms_einmal(self):
        text = quelltext('gemeinsam', 'oberflaechenbindung.js')
        self.assertIn("=== netz.geometry.userData.bindung.stufen", text)
        self.assertIn('if (material.userData.oberflaeche) return;', text)
        self.assertIn("if (!b || !geo?.attributes?.position || teil.stoff) return false;", text,
                      'Stoffschwung-Stuecke bleiben beim Worker')

    def test_4_verdrahtung_auf_allen_seiten(self):
        kleidung = quelltext('gemeinsam', 'genesis9kleidung.js')
        self.assertIn('Oberflaechenbindung.anlegen(netz, teil);', kleidung)
        modell = quelltext('gemeinsam', 'genesis9modell.js')
        self.assertIn('Oberflaechenbindung.verdrahten(this, gebunden);', modell)
        self.assertIn("import './hautverdeckung.js';", modell)
        kapseln = quelltext('gemeinsam', 'stoffkapseln.js')
        self.assertIn("import * as THREE from 'three';", kapseln)
        self.assertNotIn("state.js", kapseln)
        antwort = (Path(settings.BASE_DIR) / 'core' / 'api' / 'g9netzantwort.py').read_text(encoding='utf-8')
        self.assertIn("antwort['bindung']['stufen'] = int(b.get('stufen') or 0)", antwort,
                      'die Stufe des KOERPERS, nicht des Stuecks')

    def test_5_bindgruppe_bei_jedem_verdrahten_nachgetragen(self):
        """22.09.2026: `anlegen` kennt den Koerper oft noch nicht (Koerper und
        Kleidung laufen gleichzeitig, `genesis9aufbau.js`) — `bindgruppe` muss
        deshalb bei JEDEM `verdrahten` (auch nach `_kleiderBinden`) aktuell
        gehalten werden, nicht nur beim ersten Anlegen."""
        text = quelltext('gemeinsam', 'oberflaechenbindung.js')
        self.assertIn("geo.setAttribute('bindgruppe', new THREE.BufferAttribute(new Float32Array(n), 1));", text)
        self.assertIn('Oberflaechenbindung._bindgruppenNachtragen(inst, netz);', text)
        self.assertRegex(text, r'static verdrahten\(inst, netz\) \{[^}]*_bindgruppenNachtragen')
        self.assertIn("import { Koerperzuordnung } from './koerperzuordnung.js';", text)
