# -*- coding: utf-8 -*-
"""„Farbe im Umkreis“ im Netzwerkzeug der Jobseite Mesh-3D (13.10.2026): die Farbe jeder Fläche im Browser (`Mesh3dnetzfarbe`) und die zwei Zahlen der Leiste (`Mesh3dnetzfarbwahl`).

Edgar: „dieser kleine weisse Flügel am Arm ist nicht als extra Objekt erkannt, das möchte ich auch löschen“. Der Server wählt über `Mesh3dnetzauswahl` (`farbe`), der Browser rechnet für die Anzeige dasselbe auf dem gezeigten Netz; maßgeblich ist der Server.
Damit beide dasselbe meinen, muss der Browser Lab-Farbe und Pixel wie der Server lesen:

    LabTest       `Mesh3dnetzfarbe.lab` (Node) gleich `Mesh3dnetzkatalog.lab_von` (Python) an Grau, Weiß, Haut, Rot, Blau — auf 0,01; `abstand` ist der euklidische Abstand
    PixelTest     `labfarben` liest die Textur an der UV der Flächenmitte, glTF-UV ohne Spiegelung (Pixel (u·(b−1), v·(h−1))); ohne Textur oder UV nimmt es die Vertexfarben (Mittel der drei Ecken — die Vorschau
                  großer Netze hat nur diese; 14.10.2026), ohne beides `null`; derselbe Weg auf dem Server (`Mesh3dnetzkatalog.farben` mit einer GLB aus trimesh)
    FarbwahlTest  Umkreis in cm → Einheiten der Szene (durch den Maßstab der Wurzel), Grenzen 1–200 cm und ΔE 1–80, Komma als Dezimalzeichen, leer oder Unsinn gibt die Vorgabe
    DrahtTest     Quelltext: Knopf, Felder und Cursor stehen in Vorlage und CSS, das Werkzeug kennt den Modus `farbe`, die Auswahl schickt die Schritte mit `flaeche` (der Server prüft die Startfläche daran)

Sabotage: in `Mesh3dnetzfarbe.labfarben` `v / 3` durch `1 - v / 3` ersetzen → `PixelTest` rot (die Zeile wäre gespiegelt); in `lab` den Faktor `0.95047` streichen → `LabTest` rot; in `Mesh3dnetzfarbwahl._zahl` die Klemmung entfernen
→ `FarbwahlTest` rot. Nicht gelaufen im Browser: der Klick im Chrome ist am 13.10.2026 von Hand gesehen (240 Flächen im Browser 235, Server 240 — alle 240 im Flügel, keine fremde).
"""

import shutil
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.mesh3dnetzkatalog import Mesh3dnetzkatalog
from core.projekt_temp import ProjektTemp

from ..jsmodul import Jsmodul

FARBE = Jsmodul('mesh3d', 'mesh3dnetzfarbe.js')
FARBWAHL = Jsmodul('mesh3d', 'mesh3dnetzfarbwahl.js')
WEB = Path(settings.BASE_DIR)

PROBEN = [[128, 128, 128], [255, 255, 255], [201, 141, 115], [255, 0, 0], [0, 0, 255], [10, 200, 30]]

SKRIPT_LAB = """
const { Mesh3dnetzfarbe } = await import(MODUL);
const proben = %(proben)s;
const soll = %(soll)s;
proben.forEach((rgb, i) => {
    const lab = Mesh3dnetzfarbe.lab(rgb);
    lab.forEach((w, k) => { if (Math.abs(w - soll[i][k]) > 0.01) throw new Error('Lab ' + JSON.stringify(rgb) + ' Wert ' + k + ': ' + w + ' statt ' + soll[i][k]); });
});
// Abstand = euklidisch über die drei Lab-Werte
const lab = new Float32Array([0, 0, 0, 3, 4, 0, 10, 0, 0]);
pruefe('abstand 3-4-5', Mesh3dnetzfarbe.abstand(lab, 0, 1), 5);
pruefe('abstand 10', Mesh3dnetzfarbe.abstand(lab, 0, 2), 10);
pruefe('abstand zu sich', Mesh3dnetzfarbe.abstand(lab, 1, 1), 0);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_PIXEL = """
const { Mesh3dnetzfarbe } = await import(MODUL);
// Textur 4 × 4: der Pixel (x, y) trägt die Farbe (10·x, 10·y, 0) — daran sieht man, welcher gelesen wird.
const B = 4, H = 4, daten = new Uint8ClampedArray(B * H * 4);
for (let y = 0; y < H; y++) for (let x = 0; x < B; x++) daten.set([10 * x, 10 * y, 0, 255], (y * B + x) * 4);
globalThis.document = { createElement: () => ({ width: 0, height: 0, getContext: () => ({ drawImage() {}, getImageData: () => ({ data: daten }) }) }) };
const uv = [[0.7, 0.2], [0.7, 0.2], [0.7, 0.2],   // Fläche 0: Mitte (0,7 | 0,2) → Pixel (2, 0)
            [0.1, 0.9], [0.1, 0.9], [0.1, 0.9]];  // Fläche 1: Mitte (0,1 | 0,9) → Pixel (0, 2)
const netz = (bild, mitUv) => ({ material: { map: bild ? { image: { width: B, height: H } } : null },
    geometry: { attributes: mitUv ? { uv: { getX: i => uv[i][0], getY: i => uv[i][1] } } : {} } });
const lab = Mesh3dnetzfarbe.labfarben(netz(true, true), null, 2);
const erwartet = [Mesh3dnetzfarbe.lab([20, 0, 0]), Mesh3dnetzfarbe.lab([0, 20, 0])];
erwartet.forEach((e, f) => e.forEach((w, k) => pruefe('Fläche ' + f + ' Wert ' + k, Math.abs(lab[f * 3 + k] - w) < 1e-3, true)));
// mit Index: die Fläche 0 nimmt die Punkte 3, 4, 5 (die der zweiten Hälfte)
const lab2 = Mesh3dnetzfarbe.labfarben(netz(true, true), new Uint32Array([3, 4, 5]), 1);
erwartet[1].forEach((w, k) => pruefe('Index Wert ' + k, Math.abs(lab2[k] - w) < 1e-3, true));
pruefe('ohne Textur', Mesh3dnetzfarbe.labfarben(netz(false, true), null, 2), null);
pruefe('ohne UV', Mesh3dnetzfarbe.labfarben(netz(true, false), null, 2), null);
// ohne Textur zählen die Vertexfarben: das Mittel der drei Ecken je Fläche (0…1 → 0…255); mit Index die Ecken der Fläche, nicht die ersten
const ecken = [[0.1, 0.2, 0.3], [0.3, 0.4, 0.5], [0.2, 0.3, 0.4], [1, 1, 1], [1, 1, 1], [1, 1, 1]];
const mitFarbe = (itemSize = 3) => ({ material: {}, geometry: { attributes: { color: { itemSize, getX: i => ecken[i][0], getY: i => ecken[i][1], getZ: i => ecken[i][2] } } } });
const vf = Mesh3dnetzfarbe.labfarben(mitFarbe(), null, 2);
const vfErwartet = [Mesh3dnetzfarbe.lab([0.2 * 255, 0.3 * 255, 0.4 * 255]), Mesh3dnetzfarbe.lab([255, 255, 255])];
vfErwartet.forEach((e, f) => e.forEach((w, k) => pruefe('Vertexfarbe Fläche ' + f + ' Wert ' + k, Math.abs(vf[f * 3 + k] - w) < 1e-3, true)));
const vf2 = Mesh3dnetzfarbe.labfarben(mitFarbe(4), new Uint32Array([3, 4, 5]), 1);
vfErwartet[1].forEach((w, k) => pruefe('Vertexfarbe mit Index Wert ' + k, Math.abs(vf2[k] - w) < 1e-3, true));
pruefe('Vertexfarben ohne Farbkanäle', Mesh3dnetzfarbe.labfarben(mitFarbe(1), null, 2), null);
// ein Bild, das sich nicht lesen lässt (fremder Ursprung wirft beim Auslesen), gibt null statt einer Ausnahme
globalThis.document = { createElement: () => ({ getContext: () => ({ drawImage() {}, getImageData() { throw new Error('tainted'); } }) }) };
pruefe('Bild nicht lesbar', Mesh3dnetzfarbe.labfarben(netz(true, true), null, 2), null);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_FARBWAHL = """
const { Mesh3dnetzfarbwahl } = await import(MODUL);
const felder = { 'netz-wz-farbradius': { value: '' }, 'netz-wz-farbtoleranz': { value: '' } };
globalThis.document = { getElementById: id => felder[id] || null };
let w = new Mesh3dnetzfarbwahl();
pruefe('Vorgabe Radius gesetzt', felder['netz-wz-farbradius'].value, 18);
pruefe('Vorgabe ΔE gesetzt', felder['netz-wz-farbtoleranz'].value, 14);
const wurzel = massstab => ({ updateWorldMatrix() {}, matrixWorld: { getMaxScaleOnAxis: () => massstab } });
pruefe('18 cm bei Maßstab 1', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 0.18);
pruefe('18 cm bei Szene in Zentimetern', Math.round(w.radiusSzene(wurzel(0.01)) * 1e6) / 1e6, 18);
felder['netz-wz-farbradius'].value = '12,5';
pruefe('Komma', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 0.125);
felder['netz-wz-farbradius'].value = '500'; pruefe('zu groß', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 2);
felder['netz-wz-farbradius'].value = '0'; pruefe('zu klein', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 0.01);
felder['netz-wz-farbradius'].value = 'abc'; pruefe('Unsinn', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 0.18);
felder['netz-wz-farbradius'].value = ''; pruefe('leer', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 0.18);
felder['netz-wz-farbtoleranz'].value = '30'; pruefe('ΔE 30', w.farbabstand(), 30);
felder['netz-wz-farbtoleranz'].value = '200'; pruefe('ΔE zu groß', w.farbabstand(), 80);
felder['netz-wz-farbtoleranz'].value = '-3'; pruefe('ΔE zu klein', w.farbabstand(), 1);
felder['netz-wz-farbtoleranz'].value = 'x'; pruefe('ΔE Unsinn', w.farbabstand(), 14);
// ein Feld, das es nicht gibt (Vorlage ohne die Felder), wirft nicht und gibt die Vorgaben
globalThis.document = { getElementById: () => null };
w = new Mesh3dnetzfarbwahl();
pruefe('ohne Felder: ΔE', w.farbabstand(), 14);
pruefe('ohne Felder: Radius', Math.round(w.radiusSzene(wurzel(1)) * 1e6) / 1e6, 0.18);
console.log(JSON.stringify({ ok: true }));
"""


class LabTest(SimpleTestCase):
    databases = set()

    def test_lab_im_browser_gleich_lab_auf_dem_server(self):
        soll = Mesh3dnetzkatalog.lab_von(PROBEN).tolist()
        ausgabe = FARBE.laufen(SKRIPT_LAB % {'proben': PROBEN, 'soll': soll})
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class PixelTest(SimpleTestCase):
    databases = set()

    def test_die_textur_wird_an_der_uv_der_flaechenmitte_gelesen(self):
        ausgabe = FARBE.laufen(SKRIPT_PIXEL)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_der_server_nimmt_ohne_textur_die_vertexfarben(self):
        """Ein Foto-Scan trägt Farben an den Punkten: `Mesh3dnetzkatalog.farben` liest das Mittel der drei Ecken je Fläche (vorher: `ValueError`, die Auswahl nach Farbe ging nicht)."""
        import trimesh

        ordner = Path(ProjektTemp.ordner(prefix='netzfarbe_'))
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        punkte = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float)
        farben = np.array([[10, 20, 30, 255], [30, 40, 50, 255], [20, 30, 40, 255], [250, 250, 250, 255]], dtype=np.uint8)
        netz = trimesh.Trimesh(vertices=punkte, faces=[[0, 1, 2], [1, 3, 2]], vertex_colors=farben, process=False)
        datei = ordner / 'farbig.glb'
        netz.export(str(datei), file_type='glb')
        rgb = Mesh3dnetzkatalog.farben(datei)
        self.assertEqual(rgb.shape, (2, 3))
        np.testing.assert_allclose(rgb[0], [20, 30, 40], atol=1, err_msg='Fläche 0: Mittel der Ecken 0, 1, 2')
        np.testing.assert_allclose(rgb[1], farben[[1, 3, 2], :3].mean(axis=0), atol=1, err_msg='Fläche 1: Mittel der Ecken 1, 3, 2')

    def test_ohne_textur_und_ohne_vertexfarben_bleibt_es_bei_der_absage(self):
        import trimesh

        ordner = Path(ProjektTemp.ordner(prefix='netzfarbe_'))
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        datei = ordner / 'grau.glb'
        trimesh.Trimesh(vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]], faces=[[0, 1, 2]], process=False).export(str(datei), file_type='glb')
        with self.assertRaisesRegex(ValueError, 'weder Farbtextur noch Vertexfarben'):
            Mesh3dnetzkatalog.farben(datei)


class FarbwahlTest(SimpleTestCase):
    databases = set()

    def test_umkreis_und_farbabstand_der_leiste(self):
        ausgabe = FARBWAHL.laufen(SKRIPT_FARBWAHL)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class DrahtTest(SimpleTestCase):
    databases = set()

    def _text(self, *teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_knopf_felder_und_cursor_stehen_in_vorlage_und_css(self):
        vorlage = self._text('templates', 'mesh3d_auftrag.html')
        for kennung in ('netz-wz-farbe', 'netz-wz-farbradius', 'netz-wz-farbtoleranz'):
            self.assertIn('id="%s"' % kennung, vorlage, kennung)
        css = self._text('static', 'css', 'mesh3d.css')
        self.assertIn('.mesh3d-netzbetrachter.wz-farbe canvas', css)

    def test_das_werkzeug_kennt_den_modus_farbe_und_schickt_die_startflaeche(self):
        werkzeug = self._text('static', 'viewer', 'mesh3d', 'mesh3dnetzwerkzeug.js')
        self.assertIn("this.knoepfe.farbe.addEventListener('click', () => this._umschalten('farbe'))", werkzeug)
        self.assertIn("for (const art of ['hover', 'teil', 'rahmen', 'farbe'])", werkzeug)
        self.assertIn('this.wahl.farbe(t.flaeche, t.punkt,', werkzeug)
        wahl = self._text('static', 'viewer', 'mesh3d', 'mesh3dnetzwahl.js')
        self.assertIn("{ art: 'farbe', punkt: [punkt.x, punkt.y, punkt.z], radius, toleranz, flaeche,", wahl)

    def test_der_server_kennt_denselben_schritt(self):
        auswahl = self._text('core', 'dienste', 'mesh3dnetzauswahl.py')
        self.assertIn("if art == 'farbe':", auswahl)
        self.assertIn("schritt.get('flaeche')", auswahl)
