# -*- coding: utf-8 -*-
u"""Zwei Schnitte zu einem Netz vereinen — und zurueck zerlegen.

WARUM (Edgar, 09.09.2026: „mach das gleichzeitige Anziehen mehrere
Stuecke")
=====================================================================
`run_sim` nimmt genau eine Spezifikation, und die Stoff-gegen-Stoff-
Kollision des Upstream gilt innerhalb dieses einen Netzes. Damit zwei
Stuecke einander verdraengen, muessen sie in EINER Spezifikation stehen.

DIE FAELLE HIER RECHNEN AUF KUNSTSCHNITTEN, nicht auf den Dateien unter
`Assets/GarmentCode/ausgabe/`: Die entstehen bei jedem Bau neu, und ein
Test, der an ihnen haengt, meldet irgendwann etwas ueber den letzten Lauf
statt ueber den Code (`~/.claude/rules/test-isolation.md`).

Jeder Fall hat eine Gegenprobe: Was er verlangt, muss ohne die
entsprechende Zeile im Code rot werden.
"""
import json
import os
import tempfile

from django.test import SimpleTestCase

from GarmentCode.schnittvereinigung import (Schnittvereinigung,
                                            VereinigungsFehler)
from GarmentCode.stoffteilung import Stoffteilung, TeilungsFehler


def _schnitt(panels, naehte, einheiten=100):
    """Eine minimale, gueltige Spezifikation."""
    return {
        'pattern': {
            'panels': {name: {'translation': [0, 0, 0], 'rotation': [0, 0, 0],
                              'vertices': [[0, 0], [1, 0], [1, 1]],
                              'edges': [], 'label': name}
                       for name in panels},
            'stitches': naehte,
            'panel_order': list(panels),
        },
        'parameters': {}, 'parameter_order': [],
        'properties': {'curvature_coords': 'relative',
                       'normalize_panel_translation': False,
                       'normalized_edge_loops': True,
                       'units_in_meter': einheiten},
    }


class SchnittvereinigungTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(
            dir=os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__))))), 'ProjektTemp'))
        self.addCleanup(self.ordner.cleanup)

    def _ablegen(self, name, spez):
        pfad = os.path.join(self.ordner.name, '%s_specification.json' % name)
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(spez, datei)
        return {'name': name, 'spezifikation': pfad}

    def _paar(self):
        hose = self._ablegen('hose', _schnitt(
            ['wb_front', 'wb_back'],
            [[{'panel': 'wb_front', 'edge': 6},
              {'panel': 'wb_back', 'edge': 0}]]))
        shirt = self._ablegen('t-shirt', _schnitt(
            ['left_ftorso', 'left_btorso'],
            [[{'panel': 'left_ftorso', 'edge': 1},
              {'panel': 'left_btorso', 'edge': 2}]]))
        return hose, shirt

    def _vereint(self):
        ziel = os.path.join(self.ordner.name, 'gem_specification.json')
        bericht = Schnittvereinigung(list(self._paar())).vereinen(ziel)
        with open(ziel, 'r', encoding='utf-8') as quelle:
            return bericht, json.load(quelle)

    # -------------------------------------------------------------- vereinen

    def test_alle_panels_und_naehte_kommen_mit(self):
        u"""Kein Panel darf verlorengehen — es wuerde nie vernetzt.

        `BoxMesh.load_panels` laeuft nur ueber `panel_order`; ein Panel,
        das dort fehlt, verschwindet ohne Fehlermeldung.
        """
        _, vereint = self._vereint()
        panels = vereint['pattern']['panels']
        self.assertEqual(sorted(panels), [
            'hose__wb_back', 'hose__wb_front',
            't-shirt__left_btorso', 't-shirt__left_ftorso'])
        self.assertEqual(sorted(vereint['pattern']['panel_order']),
                         sorted(panels))
        self.assertEqual(len(vereint['pattern']['stitches']), 2)

    def test_naehte_zeigen_auf_die_umbenannten_panels(self):
        u"""Eine Naht verweist ueber den NAMEN — der muss mitwandern."""
        _, vereint = self._vereint()
        for naht in vereint['pattern']['stitches']:
            for seite in naht:
                self.assertIn(Schnittvereinigung.TRENNER, seite['panel'])
                self.assertIn(seite['panel'], vereint['pattern']['panels'])

    def test_keine_naht_ueber_die_stueckgrenze(self):
        u"""Genau das unterscheidet zwei Stuecke von einem Jumpsuit.

        `MetaGarment` NAEHT Oberteil und Unterteil zusammen; hier duerfen
        sie sich nur beruehren. Waere eine Naht dazwischen, waere es EIN
        Kleidungsstueck, und die Teilung danach unmoeglich.
        """
        _, vereint = self._vereint()
        for naht in vereint['pattern']['stitches']:
            stuecke = {Schnittvereinigung.stueck_von(s['panel'])
                       for s in naht}
            self.assertEqual(len(stuecke), 1, naht)

    def test_parameters_stehen_drin_auch_wenn_sie_leer_sind(self):
        u"""`VisPattern` erbt von `ParametrizedPattern`.

        Dessen `__init__` greift ungeprueft auf `spec['parameters']` zu.
        Ohne die beiden Felder bricht die Simulation mit
        `KeyError: 'parameters'` ab, bevor sie beginnt (09.09.2026
        gemessen).
        """
        _, vereint = self._vereint()
        self.assertEqual(vereint['parameters'], {})
        self.assertEqual(vereint['parameter_order'], [])

    def test_gleiches_stueck_zweimal_bekommt_eigene_praefixe(self):
        u"""Zwei Roecke uebereinander sind erlaubt.

        Mit demselben Praefix nahm das zweite dem ersten die Panels — der
        vereinte Schnitt haette stumm nur eines gehabt.
        """
        hose, _ = self._paar()
        ziel = os.path.join(self.ordner.name, 'zwei_specification.json')
        bericht = Schnittvereinigung([hose, dict(hose)]).vereinen(ziel)
        self.assertEqual([s['name'] for s in bericht['stuecke']],
                         ['hose', 'hose_2'])
        self.assertEqual(len(bericht['panels']), 4)

    # ------------------------------------------------------------- Abbrueche

    def test_verschiedene_einheiten_brechen_ab(self):
        u"""`units_in_meter` deutet JEDE Koordinate.

        Gemittelt oder ignoriert laege ein Stueck um Faktor 100 daneben —
        und niemand saehe einen Fehler, nur ein absurdes Ergebnis.
        """
        hose, shirt = self._paar()
        with open(shirt['spezifikation'], 'w', encoding='utf-8') as datei:
            json.dump(_schnitt(['x'], [], einheiten=1), datei)
        with self.assertRaises(VereinigungsFehler) as fall:
            Schnittvereinigung([hose, shirt]).vereinen(
                os.path.join(self.ordner.name, 'k_specification.json'))
        self.assertIn('units_in_meter', str(fall.exception))

    def test_ein_einzelnes_stueck_wird_abgelehnt(self):
        hose, _ = self._paar()
        with self.assertRaises(VereinigungsFehler):
            Schnittvereinigung([hose]).vereinen(
                os.path.join(self.ordner.name, 'e_specification.json'))

    def test_altes_parameterformat_wird_abgelehnt(self):
        u"""Die `influence`-Listen nennen PANELNAMEN.

        Umbenannt zeigten sie ins Leere; der Schnitt baute weiter und
        waere ein anderer als der gemeinte.
        """
        hose, shirt = self._paar()
        spez = _schnitt(['x'], [])
        spez['parameters'] = {'length': {'value': 1, 'influence': {}}}
        with open(shirt['spezifikation'], 'w', encoding='utf-8') as datei:
            json.dump(spez, datei)
        with self.assertRaises(VereinigungsFehler) as fall:
            Schnittvereinigung([hose, shirt]).vereinen(
                os.path.join(self.ordner.name, 'p_specification.json'))
        self.assertIn('Parameterformat', str(fall.exception))

    def test_fehlende_datei_wird_gemeldet(self):
        hose, _ = self._paar()
        with self.assertRaises(VereinigungsFehler):
            Schnittvereinigung(
                [hose, {'name': 'x', 'spezifikation': 'gibtsnicht.json'}]
            ).vereinen(os.path.join(self.ordner.name, 'f_specification.json'))

    # --------------------------------------------------------------- teilen

    def _netz_und_segmentierung(self):
        u"""Ein Kunstnetz: zwei Dreiecke Hose, zwei Dreiecke T-Shirt.

        Punkt 2 ist ein NAHTpunkt der Hose: In der Segmentierung steht
        dort nur `stitch_0`, das Stueck ergibt sich aus der Naht.
        """
        ziel = os.path.join(self.ordner.name, 'gem_specification.json')
        Schnittvereinigung(list(self._paar())).vereinen(ziel)
        netz = os.path.join(self.ordner.name, 'gem_sim.obj')
        with open(netz, 'w', encoding='utf-8') as datei:
            for nummer in range(8):
                datei.write('v %d 0 0\n' % nummer)
            datei.write('f 1 2 3\nf 2 3 4\nf 5 6 7\nf 6 7 8\n')
        seg = os.path.join(self.ordner.name, 'gem_sim_segmentation.txt')
        with open(seg, 'w', encoding='utf-8') as datei:
            datei.write('hose__wb_front\nhose__wb_front\nstitch_0\n'
                        'hose__wb_back\n')
            datei.write('t-shirt__left_ftorso\nt-shirt__left_ftorso\n'
                        'stitch_1\nt-shirt__left_btorso\n')
        return ziel, netz, seg

    def test_die_teilung_verliert_nichts(self):
        ziel, netz, seg = self._netz_und_segmentierung()
        teile = Stoffteilung(ziel).teilen(netz, seg)
        self.assertEqual(sorted(teile), ['hose', 't-shirt'])
        self.assertEqual(sum(len(t['punkte']) for t in teile.values()), 8)
        self.assertEqual(sum(len(t['dreiecke']) for t in teile.values()), 4)
        self.assertEqual(sum(t['fremd'] for t in teile.values()), 0)

    def test_nahtpunkte_finden_ihr_stueck_ueber_die_naht(self):
        u"""In der Segmentierung steht bei ihnen KEIN Panelname.

        Ohne diesen Weg fielen sie heraus — gemessen 1.014 von 17.316
        Punkten des ersten Paarlaufs, und jedes Stueck haette Loecher an
        allen Naehten.
        """
        ziel, _, seg = self._netz_und_segmentierung()
        zuordnung = Stoffteilung(ziel).stueck_je_punkt(seg)
        self.assertEqual(zuordnung[2], 'hose')
        self.assertEqual(zuordnung[6], 't-shirt')
        self.assertNotIn(None, zuordnung)

    def test_die_indizes_bilden_auf_das_ganze_netz_ab(self):
        u"""Die Verankerung rechnet auf den KORRIGIERTEN Punkten.

        Die liegen in Projektkoordinaten neben der Datei; nur ueber die
        Punktnummern lassen sich beide Reihenfolgen aufeinander abbilden.
        """
        ziel, netz, seg = self._netz_und_segmentierung()
        teile = Stoffteilung(ziel).teilen(netz, seg)
        self.assertEqual(teile['hose']['indizes'], [0, 1, 2, 3])
        self.assertEqual(teile['t-shirt']['indizes'], [4, 5, 6, 7])
        for teil in teile.values():
            self.assertEqual(len(teil['indizes']), len(teil['punkte']))

    def test_flaeche_ueber_die_grenze_wird_gezaehlt_nicht_verschluckt(self):
        u"""Sie KANN nicht auftreten — und wenn doch, wird sie gemeldet."""
        ziel, netz, seg = self._netz_und_segmentierung()
        with open(netz, 'a', encoding='utf-8') as datei:
            datei.write('f 1 2 5\n')          # Hose + T-Shirt in einer Flaeche
        teile = Stoffteilung(ziel).teilen(netz, seg)
        self.assertEqual(teile['hose']['fremd'], 1)
        self.assertEqual(sum(len(t['dreiecke']) for t in teile.values()), 4)

    def test_segmentierung_passt_nicht_zum_netz(self):
        ziel, netz, seg = self._netz_und_segmentierung()
        with open(seg, 'a', encoding='utf-8') as datei:
            datei.write('hose__wb_front\n')
        with self.assertRaises(TeilungsFehler):
            Stoffteilung(ziel).teilen(netz, seg)

    def test_geschriebenes_teilnetz_ist_wieder_lesbar(self):
        u"""Die Indizes im OBJ sind 1-basiert — ein Versatz von eins gibt
        ein Netz, das laedt und falsche Dreiecke hat."""
        ziel, netz, seg = self._netz_und_segmentierung()
        teile = Stoffteilung(ziel).teilen(netz, seg)
        pfad = os.path.join(self.ordner.name, 'hose_sim.obj')
        Stoffteilung.netz_schreiben(pfad, teile['hose']['punkte'],
                                    teile['hose']['dreiecke'])
        punkte, dreiecke = Stoffteilung.netz_lesen(pfad)
        self.assertEqual(punkte, teile['hose']['punkte'])
        self.assertEqual(dreiecke, teile['hose']['dreiecke'])
        self.assertEqual(max(max(d) for d in dreiecke), len(punkte) - 1)
