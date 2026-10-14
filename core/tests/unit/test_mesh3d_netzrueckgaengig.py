# -*- coding: utf-8 -*-
"""Netz bearbeiten: der Arm der Ballerina und das Rückgängig (14.10.2026).

Edgar: „nach dem Entfernen per Auswahl aus Ballerina hast du einen Teil des Arms entfernt, mach das wieder rückgängig und fixe“ — und: „ich brauche auch einen Undo-Button für Löschen, bzw. Strg+Z und Strg+Y“.

    DreieckTest      `Mesh3dnetzdreieck.abstand`: Abstand zur Fläche, zur Kante, zur Ecke; ein entartetes Dreieck zählt über seine Kanten
    StartflaecheTest die Startfläche des Klicks gilt, wenn der Punkt auf IHREM Dreieck liegt (nicht, wenn die Mitte nah ist): Flügel mit 0,4 m langen Kanten über einem Arm aus kleinen Dreiecken — vorher nahm der Server die
                     nächste MITTE (eine Armfläche, 537 statt 20 Flächen); ohne Datei im Katalog bleibt die alte Regel; eine fremde Nummer (vereinfachte Kopie) fällt auf die Fläche unter dem Klick zurück
    VorquelleTest    `Mesh3dnetzschnitt.vorquelle`: die Datei vor dem Schnitt steht in der Begleitdatei der bearbeiteten Quelle; ohne Begleitdatei, mit fehlender Datei und bei einer nicht bearbeiteten Quelle ein `ValueError`
    UndoTest         `Mesh3dnetzwahl.zurueck/wiederholen` (Node, `three` als Attrappe): „Entfernen“ lässt sich zurücknehmen und wiederholen, ein neuer Schritt leert das Wiederholen, `Mesh3dnetztasten` (Strg+Z, Strg+Y,
                     Strg+Umschalt+Z, nicht in Eingabefeldern, nicht ohne Leiste)
    DrahtTest        Quelltext: Knöpfe in der Vorlage, die Adresse `netzzurueck`, der Aufruf im Browser

Sabotage: in `Mesh3dnetzauswahl._startflaeche` die Prüfung wieder auf die Mitte stellen (`self.katalog.mitte[int(nummer)] …` ohne `abstand_zu_flaechen`) → `StartflaecheTest` rot; in `Mesh3dnetzwahl._sichern` `this.zukunft = []`
streichen → `UndoTest` rot; in `Mesh3dnetzdreieck.abstand` `innen` durch `False` ersetzen → `DreieckTest` rot. Im Chrome gesehen (14.10.2026): Strg+Z und Strg+Y auf der Seite (Fokus auf dem Körper), der Knopf „Gespeicherten Schnitt zurücknehmen“ an der
Kopie der Spiralballerina (44.796 → 45.338 Flächen, Arm vollständig im Bild), die zwei Klicks von Edgar auf dem Server 5 und 20 Flächen (vorher 5 und 537), im Browser 5 und 19. Nicht gelaufen im Chrome: ein „Entfernen“ mit der Maus am Flügel.
"""

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.mesh3dnetzauswahl import Mesh3dnetzauswahl
from core.dienste.mesh3dnetzdreieck import Mesh3dnetzdreieck
from core.dienste.mesh3dnetzkatalog import Mesh3dnetzkatalog
from core.dienste.mesh3dnetzschnitt import Mesh3dnetzschnitt
from core.projekt_temp import ProjektTemp

WEB = Path(settings.BASE_DIR)
VIEWER = WEB / 'static' / 'viewer' / 'mesh3d'

DREI = """
export const DynamicDrawUsage = 35048;
export const DoubleSide = 2;
export class BufferAttribute { constructor(array, size) { this.array = array; this.itemSize = size; } }
export class BufferGeometry { constructor() { this.attributes = {}; this.index = null; } setIndex(i) { this.index = i; return this; } setAttribute(n, a) { this.attributes[n] = a; return this; } dispose() {} }
export class Raycaster {}
export class MeshBasicMaterial {}
export class Mesh {}
"""

PROBE = r"""
import { Mesh3dnetzwahl } from './mesh3dnetzwahl.js';
import { Mesh3dnetztasten } from './mesh3dnetztasten.js';
import * as THREE from './three.js';
const aus = {};

// Sechs Flächen; `Object.create` überspringt den Aufbau (Inselzerlegung braucht eine echte Geometrie), die Abläufe sind die echten.
const baue = () => {
    const w = Object.create(Mesh3dnetzwahl.prototype);
    Object.assign(w, { flaechen: 6, index0: Uint32Array.from({ length: 18 }, (_, i) => i), geometrie: new THREE.BufferGeometry(), auswahl: new Uint8Array(6), entfernt: new Uint8Array(6),
        schritte: [], schnitte: [], historie: [], zukunft: [], nummern: null, geaendert: 0 });
    w._fertig = () => { w.geaendert++; };
    return w;
};
const stand = w => ({ auswahl: w.nAuswahl, entfernt: w.nEntfernt, schnitte: w.schnitte.length, historie: w.historie.length, zukunft: w.zukunft.length, nummern: w.nummern ? Array.from(w.nummern) : null });
const waehle = (w, bis) => w._schritt({ art: 'insel', aktion: 'plus' }, f => f < bis);

{
    const w = baue();
    waehle(w, 2);
    aus.gewaehlt = stand(w);
    w.entfernen();
    aus.entfernt = stand(w);
    aus.zurueck_ok = w.zurueck();
    aus.nach_zurueck = stand(w);                    // das Entfernen ist zurückgenommen: die Auswahl steht wieder da, nichts ist entfernt
    aus.wiederholen_ok = w.wiederholen();
    aus.nach_wiederholen = stand(w);
    w.zurueck(); w.zurueck();
    aus.ganz_zurueck = stand(w);
    w.wiederholen(); w.wiederholen();
    aus.ganz_vor = stand(w);
    aus.leer_wiederholen = w.wiederholen();         // nichts mehr zu wiederholen
}
{
    const w = baue();
    waehle(w, 2); w.entfernen(); w.zurueck();
    aus.vor_neuem_schritt = w.zukunft.length;
    waehle(w, 4);                                   // ein neuer Schritt verwirft das Wiederholen
    aus.nach_neuem_schritt = { zukunft: w.zukunft.length, wiederholen: w.wiederholen() };
    w.zuruecksetzen = Mesh3dnetzwahl.prototype.zuruecksetzen;
    w._indexNeu = () => {};
    w.zuruecksetzen();
    aus.nach_zuruecksetzen = { historie: w.historie.length, zukunft: w.zukunft.length };
}

// Tasten
{
    const aufrufe = [];
    const wahl = { zurueck: () => aufrufe.push('zurueck'), wiederholen: () => aufrufe.push('wiederholen') };
    const taste = (key, o = {}) => Mesh3dnetztasten.rueckgaengig({ key, ctrlKey: true, metaKey: false, shiftKey: false, altKey: false, ...o }, wahl);
    aus.tasten = { z: taste('z'), Z_gross: taste('Z'), y: taste('y'), umschalt_z: taste('z', { shiftKey: true }), cmd_z: taste('z', { ctrlKey: false, metaKey: true }),
        ohne_ctrl: taste('z', { ctrlKey: false }), alt: taste('z', { altKey: true }), andere: taste('x'), ohne_wahl: Mesh3dnetztasten.rueckgaengig({ key: 'z', ctrlKey: true }, null) };
    aus.tasten.aufrufe = [...aufrufe];              // eine Kopie: `aufrufe` wird gleich für den nächsten Teil geleert
    const e = (ziel, o = {}) => ({ key: 'z', ctrlKey: true, defaultPrevented: false, target: ziel, ...o });
    const feld = { hidden: false }, versteckt = { hidden: true };
    aufrufe.length = 0;
    aus.seite = { koerper: Mesh3dnetztasten.seite(e({ tagName: 'BODY' }), wahl, feld), eingabe: Mesh3dnetztasten.seite(e({ tagName: 'INPUT' }), wahl, feld),
        textfeld: Mesh3dnetztasten.seite(e({ tagName: 'TEXTAREA' }), wahl, feld), auswahlfeld: Mesh3dnetztasten.seite(e({ tagName: 'SELECT' }), wahl, feld),
        bearbeitbar: Mesh3dnetztasten.seite(e({ tagName: 'DIV', isContentEditable: true }), wahl, feld), leiste_versteckt: Mesh3dnetztasten.seite(e({ tagName: 'BODY' }), wahl, versteckt),
        schon_behandelt: Mesh3dnetztasten.seite(e({ tagName: 'BODY' }, { defaultPrevented: true }), wahl, feld), ohne_wahl: Mesh3dnetztasten.seite(e({ tagName: 'BODY' }), null, feld), aufrufe: aufrufe.length };
}
console.log(JSON.stringify(aus));
"""


def quelltext(*teile):
    return WEB.joinpath(*teile).read_text(encoding='utf-8')


class DreieckTest(SimpleTestCase):
    databases = set()
    DREIECK = [[[0, 0, 0], [1, 0, 0], [0, 1, 0]]]

    def test_abstand_zur_flaeche_zur_kante_und_zur_ecke(self):
        d = lambda p, t=None: float(Mesh3dnetzdreieck.abstand(p, t or self.DREIECK)[0])  # noqa: E731
        self.assertAlmostEqual(d([0.2, 0.2, 0.5]), 0.5, places=9, msg='über der Fläche: die Höhe')
        self.assertAlmostEqual(d([0.2, 0.2, 0.0]), 0.0, places=9, msg='auf der Fläche')
        self.assertAlmostEqual(d([0.5, -1.0, 0.0]), 1.0, places=9, msg='unter der Kante')
        self.assertAlmostEqual(d([2.0, 0.0, 0.0]), 1.0, places=9, msg='neben der Ecke (1, 0, 0)')
        self.assertAlmostEqual(d([1.0, 1.0, 0.0]), 0.5 ** 0.5, places=9, msg='neben der Hypotenuse')

    def test_viele_dreiecke_auf_einmal_und_entartete(self):
        t = [[[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 0, 1], [0, 1, 1]], [[0, 0, 0], [1, 0, 0], [2, 0, 0]]]
        d = Mesh3dnetzdreieck.abstand([0.2, 0.2, 0.5], t)
        self.assertEqual(d.shape, (3,))
        self.assertAlmostEqual(float(d[0]), 0.5, places=9)
        self.assertAlmostEqual(float(d[1]), 0.5, places=9)
        self.assertAlmostEqual(float(d[2]), (0.2 ** 2 + 0.5 ** 2) ** 0.5, places=9, msg='ein Dreieck ohne Fläche (alle Punkte auf einer Geraden) zählt über seine Kanten')


class _Katalog:
    """Ein Katalog aus Hand gebauten Dreiecken: ein Flügel (Fläche 0, Kanten bis 0,4 m, z = 0,005) über einem Arm aus kleinen Dreiecken (z = 0)."""

    @staticmethod
    def bauen(mit_datei=True):
        gross = [[0.0, 0.0, 0.005], [0.4, 0.0, 0.005], [0.0, 0.4, 0.005]]
        dreiecke = [gross]
        for i in range(20):                                         # kleine Dreiecke unter dem Klickpunkt (0,05 | 0,05)
            x, y = 0.03 + 0.01 * (i % 5), 0.03 + 0.01 * (i // 5)
            dreiecke.append([[x, y, 0.0], [x + 0.005, y, 0.0], [x, y + 0.005, 0.0]])
        punkte = np.array(dreiecke, dtype=np.float32).reshape(-1, 3)
        flaechen = np.arange(len(punkte), dtype=np.int32).reshape(-1, 3)
        mitte = punkte[flaechen].mean(axis=1).astype(np.float32)
        katalog = Mesh3dnetzkatalog(len(flaechen), mitte, np.zeros(len(flaechen), dtype=np.int32), [1, 0, 0])
        if mit_datei:
            katalog.pfad = 'attrappe.glb'
            katalog._eck = (punkte, flaechen)
            katalog._flaechenradius = float(np.linalg.norm(punkte[flaechen] - mitte[:, None, :], axis=2).max())
        return katalog


class StartflaecheTest(SimpleTestCase):
    databases = set()
    KLICK = [0.05, 0.05, 0.005]                                     # liegt auf dem Flügel (Fläche 0), seine Mitte ist 0,13 entfernt

    def test_die_mitte_des_fluegels_ist_weit_weg_der_klick_liegt_auf_ihm(self):
        k = _Katalog.bauen()
        self.assertGreater(float(np.linalg.norm(k.mitte[0] - np.array(self.KLICK))), 0.1)
        self.assertLess(float(k.abstand_zu_flaechen(self.KLICK, [0])[0]), 1e-6)
        self.assertNotEqual(k.naechste_flaeche(self.KLICK), 0, 'die nächste MITTE ist eine Armfläche — das war der Fehler')

    def test_die_flaeche_des_browsers_gilt_wenn_der_klick_auf_ihr_liegt(self):
        a = Mesh3dnetzauswahl(_Katalog.bauen())
        self.assertEqual(a._startflaeche(self.KLICK, 0), 0)

    def test_ohne_nummer_gilt_die_flaeche_unter_dem_klick_nicht_die_nahe_mitte(self):
        a = Mesh3dnetzauswahl(_Katalog.bauen())
        self.assertEqual(a._startflaeche(self.KLICK, None), 0)

    def test_eine_fremde_nummer_faellt_auf_die_flaeche_unter_dem_klick_zurueck(self):
        a = Mesh3dnetzauswahl(_Katalog.bauen())
        self.assertEqual(a._startflaeche(self.KLICK, 20), 0, 'Fläche 20 liegt 0,05 daneben (vereinfachte Kopie: andere Nummern)')

    def test_eine_nummer_ausserhalb_des_netzes_wird_ignoriert(self):
        a = Mesh3dnetzauswahl(_Katalog.bauen())
        self.assertEqual(a._startflaeche(self.KLICK, 9999), 0)
        self.assertEqual(a._startflaeche(self.KLICK, -1), 0)
        self.assertEqual(a._startflaeche(self.KLICK, True), 0)

    def test_ein_katalog_ohne_datei_bleibt_bei_der_alten_regel(self):
        k = _Katalog.bauen(mit_datei=False)
        self.assertIsNone(k.abstand_zu_flaechen(self.KLICK, [0]))
        a = Mesh3dnetzauswahl(k)
        self.assertEqual(a._startflaeche(self.KLICK, 13), 13, 'die Mitte von Fläche 13 liegt unter 3 cm vom Klick')
        self.assertEqual(a._startflaeche(self.KLICK, 0), k.naechste_flaeche(self.KLICK), 'Mitte weit weg → nächste Mitte')

    def test_die_auswahl_nach_farbe_nimmt_die_referenz_vom_fluegel(self):
        k = _Katalog.bauen()
        k._lab = np.array([[90, 0, 0]] + [[70, 25, 20]] * 20, dtype=np.float32)          # Flügel weiß, Arm Haut
        a = Mesh3dnetzauswahl(k)
        m = a.maske([{'art': 'farbe', 'punkt': self.KLICK, 'radius': 0.5, 'toleranz': 14, 'flaeche': 0}])
        self.assertEqual(np.flatnonzero(m).tolist(), [0], 'nur der Flügel, nicht der Arm unter ihm')


class VorquelleTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = Path(ProjektTemp.ordner(prefix='netzzurueck_'))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)

    def _dienst(self, quelle):
        d = object.__new__(Mesh3dnetzschnitt)
        d.stand = {'quelle': {'datei': str(quelle)}}
        return d

    def _datei(self, name, inhalt=b'glb'):
        pfad = self.ordner / name
        pfad.write_bytes(inhalt)
        return pfad

    def test_die_datei_vor_dem_schnitt_steht_in_der_begleitdatei(self):
        alt = self._datei('Figur_2026.10.13.19.01.28.glb')
        neu = self._datei('Figur_bearbeitet_2026.10.14.10.41.30.glb')
        (self.ordner / 'Figur_bearbeitet_2026.10.14.10.41.30.json').write_text(json.dumps({'quelle': {'datei': str(alt)}}), encoding='utf-8')
        self.assertEqual(self._dienst(neu).vorquelle(), alt)

    def test_ohne_begleitdatei_oder_bei_nicht_bearbeiteter_quelle_gibt_es_nichts_zurueckzunehmen(self):
        neu = self._datei('Figur_bearbeitet_2026.10.14.10.41.30.glb')
        with self.assertRaisesRegex(ValueError, 'keinen Schnitt'):
            self._dienst(neu).vorquelle()
        original = self._datei('Figur.glb')
        (self.ordner / 'Figur.json').write_text(json.dumps({'quelle': {'datei': str(original)}}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'keinen Schnitt'):
            self._dienst(original).vorquelle()

    def test_die_fruehere_datei_fehlt_oder_die_begleitdatei_ist_kaputt(self):
        neu = self._datei('Figur_bearbeitet_2026.10.14.10.41.30.glb')
        begleit = self.ordner / 'Figur_bearbeitet_2026.10.14.10.41.30.json'
        begleit.write_text(json.dumps({'quelle': {'datei': str(self.ordner / 'weg.glb')}}), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'gibt es nicht mehr'):
            self._dienst(neu).vorquelle()
        begleit.write_text('{kaputt', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'nicht lesbar'):
            self._dienst(neu).vorquelle()


class UndoTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — ohne node kein Ergebnis (jsmodul.py).')
        ordner = Path(ProjektTemp.ordner(prefix='netzundo_'))
        try:
            for name in ('mesh3dnetzwahl.js', 'mesh3dnetzfarbe.js', 'mesh3dnetzinseln.js', 'mesh3dnetztasten.js'):
                (ordner / name).write_text((VIEWER / name).read_text(encoding='utf-8').replace("from 'three'", "from './three.js'"), encoding='utf-8')
            (ordner / 'three.js').write_text(DREI, encoding='utf-8')
            (ordner / 'probe.mjs').write_text(PROBE, encoding='utf-8')
            lauf = subprocess.run(['node', str(ordner / 'probe.mjs')], capture_output=True, text=True, encoding='utf-8', timeout=60)
        finally:
            shutil.rmtree(ordner, ignore_errors=True)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.aus = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_entfernen_laesst_sich_zurueckholen_und_wiederholen(self):
        a = self.aus
        self.assertEqual(a['gewaehlt'], {'auswahl': 2, 'entfernt': 0, 'schnitte': 0, 'historie': 1, 'zukunft': 0, 'nummern': None})
        self.assertEqual(a['entfernt'], {'auswahl': 0, 'entfernt': 2, 'schnitte': 1, 'historie': 2, 'zukunft': 0, 'nummern': [2, 3, 4, 5]})
        self.assertTrue(a['zurueck_ok'])
        self.assertEqual(a['nach_zurueck'], {'auswahl': 2, 'entfernt': 0, 'schnitte': 0, 'historie': 1, 'zukunft': 1, 'nummern': None},
                         'das Entfernen ist zurückgenommen: die Flächen sind wieder da und gewählt')
        self.assertTrue(a['wiederholen_ok'])
        self.assertEqual(a['nach_wiederholen'], a['entfernt'], 'Wiederholen stellt genau den Stand nach dem Entfernen wieder her')

    def test_ganz_zurueck_und_wieder_vor(self):
        a = self.aus
        self.assertEqual(a['ganz_zurueck'], {'auswahl': 0, 'entfernt': 0, 'schnitte': 0, 'historie': 0, 'zukunft': 2, 'nummern': None})
        self.assertEqual(a['ganz_vor'], a['entfernt'])
        self.assertFalse(a['leer_wiederholen'])

    def test_ein_neuer_schritt_leert_das_wiederholen(self):
        a = self.aus
        self.assertEqual(a['vor_neuem_schritt'], 1)
        self.assertEqual(a['nach_neuem_schritt'], {'zukunft': 0, 'wiederholen': False})
        self.assertEqual(a['nach_zuruecksetzen'], {'historie': 0, 'zukunft': 0})

    def test_tasten(self):
        t = self.aus['tasten']
        self.assertEqual([t['z'], t['Z_gross'], t['y'], t['umschalt_z'], t['cmd_z']], [True] * 5)
        self.assertEqual([t['ohne_ctrl'], t['alt'], t['andere'], t['ohne_wahl']], [False] * 4)
        self.assertEqual(t['aufrufe'], ['zurueck', 'zurueck', 'wiederholen', 'wiederholen', 'zurueck'], 'Strg+Z, Strg+Z mit großem Z, Strg+Y, Strg+Umschalt+Z, Cmd+Z')

    def test_die_tasten_gelten_auf_der_seite_aber_nicht_in_eingabefeldern(self):
        s = self.aus['seite']
        self.assertTrue(s['koerper'])
        for name in ('eingabe', 'textfeld', 'auswahlfeld', 'bearbeitbar', 'leiste_versteckt', 'schon_behandelt', 'ohne_wahl'):
            self.assertFalse(s[name], name)
        self.assertEqual(s['aufrufe'], 1, 'nur der Körper hat etwas ausgelöst')


class DrahtTest(SimpleTestCase):
    databases = set()

    def test_die_knoepfe_stehen_in_vorlage_und_werkzeug(self):
        vorlage = quelltext('templates', 'mesh3d_auftrag.html')
        werkzeug = quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzwerkzeug.js')
        for kennung in ('netz-wz-wiederholen', 'netz-wz-rueckgaengig'):
            self.assertIn('id="%s"' % kennung, vorlage, kennung)
        self.assertIn("'wiederholen', 'speichern', 'rechnen', 'rueckgaengig'", werkzeug)
        self.assertIn("this.knoepfe.wiederholen.addEventListener('click', () => w()?.wiederholen())", werkzeug)
        self.assertIn('Mesh3dnetztasten.seite(e, this.wahl, this.feld)', werkzeug, 'Strg+Z/Strg+Y gelten auf der ganzen Seite')
        self.assertIn('Mesh3dnetztasten.rueckgaengig(e, this.wahl)', werkzeug, 'und auf der Leinwand')
        self.assertIn('rueckgaengig: !w || this._arbeitet || !this._quelleBearbeitet()', werkzeug)

    def test_der_browser_ruft_die_adresse_die_der_server_kennt(self):
        speichern = quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzspeichern.js')
        self.assertIn('/netzzurueck/', speichern)
        urls = quelltext('core', 'urls_mesh3d.py')
        self.assertIn("'api/mesh3d/<kennung:kennung>/netzzurueck/', Mesh3dnetzschnittendpunkte.zurueck", urls)
        self.assertIn('def zurueck(request, kennung)', quelltext('core', 'api', 'mesh3dnetzschnitt.py'))

    def test_der_server_prueft_die_startflaeche_am_dreieck(self):
        auswahl = quelltext('core', 'dienste', 'mesh3dnetzauswahl.py')
        self.assertIn('abstand_zu_flaechen(punkt, [int(nummer)])', auswahl)
        self.assertIn('naechste_flaeche_genau(punkt)', auswahl)
