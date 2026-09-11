# -*- coding: utf-8 -*-
u"""Die Bauregler im gemeinsamen Weg (11.09.2026).

Edgar, mit Bild einer weiten Hose: „ich habe gerade T-Shirt und Hose auf
einmal gebaut, die leggins ist schon wieder weit". Der Einzelbau bekam
`anliegen_mm` seit dem Vormittag, der gemeinsame Weg nicht: Die Kombiliste
kopierte nur die Schnittwerte, der Endpunkt las kein `bau`, und
`Gemeinsamablage` korrigierte nur, legte nie an.

Vier Stellen, vier Faelle — je eine Sabotage macht ihn rot:

1. `Kombiliste.hinzufuegen` nimmt `bau` mit, `fuerServer` gibt es weiter,
   und es ueberlebt `sichern`/`laden` (Node).
2. `Garmentgemeinsamendpunkte._stuecke` macht aus `bau` je Stueck eine
   `Baufeineinstellung` — die Hose mit 2 mm, das T-Shirt ohne.
3. `Garmentgemeinsam._pruefen` reicht `fein` durch (und setzt die Vorgabe,
   wo keines kommt); `bauwerte` nennt die des ERSTEN Stuecks.
4. `Gemeinsamablage._anlegen` ruft `Stoffanlegen` nur, wenn das Stueck es
   verlangt, und gibt die Koerpernormalen zurueck; `_stueck_ablegen`
   reicht sie an `Anziehen.ablegen`.
"""
import io
import json
from unittest import mock

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from GarmentCode.baufeineinstellung import Baufeineinstellung
from GarmentCode.gemeinsamablage import Gemeinsamablage
from GarmentCode.gemeinsamdienst import Garmentgemeinsam
from core.api.garmentgemeinsam import Garmentgemeinsamendpunkte

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'kombiliste.js')

SKRIPT = """
const { Kombiliste } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
let liste = new Kombiliste();
const bau = { hautabstand_mm: 1, aufloesung: 1, anliegen_mm: 2 };
liste.hinzufuegen('hose', 'Hose', { 'pants.flare': 0.5 }, bau);
liste.hinzufuegen('t-shirt', 'T-Shirt', {});
bau.anliegen_mm = 9;                       // spaeterer Reglerzug
pruefe('Bau kopiert', liste.eintraege[0].bau.anliegen_mm, 2);
pruefe('ohne Bau leer', liste.fuerServer()[1].bau, {});
pruefe('an den Server', liste.fuerServer()[0].bau, { hautabstand_mm: 1, aufloesung: 1, anliegen_mm: 2 });
// sichern/laden mit einem Attrappen-Speicher
const ablage = {}; const speicher = { setItem: (k, v) => { ablage[k] = v; }, getItem: (k) => ablage[k] ?? null };
pruefe('gesichert', liste.sichern(speicher), true);
const neu = new Kombiliste();
pruefe('geladen', neu.laden(speicher), true);
pruefe('Bau ueberlebt', neu.fuerServer()[0].bau.anliegen_mm, 2);
console.log(JSON.stringify({ok: true}));
"""


def _lies(*teile):
    return io.open(settings.BASE_DIR.joinpath(*teile), encoding='utf-8').read()


class KombilisteBauTest(SimpleTestCase):

    databases = []

    def test_die_liste_traegt_die_bauwerte_je_stueck(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_uebernehmen_gibt_die_bauregler_mit(self):
        kombi = _lies('static', 'viewer', 'scene', 'garmentcode_kombi.js')
        self.assertIn('GarmentcodeBauregler.werte()', kombi)
        bauregler = _lies('static', 'viewer', 'scene', 'garmentcode_bauregler.js')
        self.assertIn('static werte()', bauregler)


class EndpunktBauTest(SimpleTestCase):

    databases = []

    def _stuecke(self, liste):
        anfrage = RequestFactory().post('/x/', {'stuecke': json.dumps(liste)})
        return Garmentgemeinsamendpunkte._stuecke(anfrage)

    def test_bau_je_stueck_wird_zur_feineinstellung(self):
        gewaehlt = self._stuecke([
            {'vorlage': 'hose', 'regler': {'pants.flare': 0.5},
             'bau': {'hautabstand_mm': 1, 'aufloesung': 1, 'anliegen_mm': 2}},
            {'vorlage': 't-shirt', 'regler': {}}])
        self.assertIsInstance(gewaehlt[0]['fein'], Baufeineinstellung)
        self.assertEqual(gewaehlt[0]['fein'].anliegen_mm, 2.0)
        self.assertIsNone(gewaehlt[1]['fein'].anliegen_mm)

    def test_unsinn_im_bau_faellt_auf_die_vorgabe(self):
        gewaehlt = self._stuecke([{'vorlage': 'hose', 'bau': 'quatsch'},
                                  {'vorlage': 'hose', 'bau': {'anliegen_mm': 'x'}}])
        for eintrag in gewaehlt:
            self.assertEqual(eintrag['fein'].hautabstand_mm,
                             Baufeineinstellung.HAUTABSTAND_VORGABE)
            self.assertIsNone(eintrag['fein'].anliegen_mm)


class DienstBauTest(SimpleTestCase):

    databases = []

    def test_pruefen_reicht_fein_durch_und_setzt_sonst_die_vorgabe(self):
        fein = Baufeineinstellung(anliegen_mm=2.0)
        gewaehlt = Garmentgemeinsam._pruefen([
            {'vorlage': 'hose', 'fein': fein}, {'vorlage': 't-shirt'}])
        self.assertIs(gewaehlt[0]['fein'], fein)
        self.assertIsInstance(gewaehlt[1]['fein'], Baufeineinstellung)
        self.assertIsNone(gewaehlt[1]['fein'].anliegen_mm)

    def test_die_simulation_nimmt_die_werte_des_ersten_stuecks(self):
        erstes = Baufeineinstellung(hautabstand_mm=4.0, aufloesung=1.5)
        zweites = Baufeineinstellung(hautabstand_mm=1.0)
        gilt = Garmentgemeinsam.bauwerte([{'vorlage': 'a', 'fein': erstes},
                                          {'vorlage': 'b', 'fein': zweites}])
        self.assertIs(gilt, erstes)
        # und die Drapierung bekommt genau diese Feinheit
        dienst = _lies_assets('gemeinsamdienst.py')
        self.assertIn('aufloesung=cls.bauwerte(schnitte).aufloesung', dienst)


class AblageBauTest(SimpleTestCase):

    databases = []

    def test_ohne_anliegen_bleibt_alles_wie_es_ist(self):
        punkte = [[0.0, 0.0, 0.0]]
        schnitt = {'vorlage': 'hose', 'fein': Baufeineinstellung()}
        neu, anlage, normalen = Gemeinsamablage._anlegen(
            schnitt, punkte, [[0, 0, 0]], (None, None))
        self.assertIs(neu, punkte)
        self.assertEqual(anlage, {})
        self.assertIsNone(normalen)

    def test_mit_anliegen_wird_angelegt_und_die_normalen_kommen_mit(self):
        anleger = mock.Mock()
        anleger.anlegen.return_value = ('neu', {'angelegt': 3, 'median_weg_mm': 1.0})
        anleger.koerpernormalen.return_value = 'normalen'
        schnitt = {'vorlage': 'hose', 'fein': Baufeineinstellung(anliegen_mm=2.0)}
        with mock.patch('GarmentCode.gemeinsamablage.Stoffanlegen') as klasse:
            klasse.aus_netz.return_value = anleger
            neu, anlage, normalen = Gemeinsamablage._anlegen(
                schnitt, 'alt', 'dreiecke', ('kp', 'kf'))
        klasse.aus_netz.assert_called_once_with('kp', 'kf', 'dreiecke')
        anleger.anlegen.assert_called_once_with('alt', 2.0)
        self.assertEqual((neu, anlage['angelegt'], normalen), ('neu', 3, 'normalen'))

    def test_das_stueck_legt_vor_dem_anziehen_an(self):
        quelle = _lies_assets('gemeinsamablage.py')
        ablegen = quelle.index('def _stueck_ablegen')
        anlegen = quelle.index('cls._anlegen(schnitt, punkte, dreiecke', ablegen)
        anziehen = quelle.index('anzieher.anziehen(punkte)', ablegen)
        self.assertLess(anlegen, anziehen)
        self.assertIn('normalen=normalen', quelle[anziehen:])


def _lies_assets(name):
    return io.open(settings.ASSETS_ROOT / 'GarmentCode' / name,
                   encoding='utf-8').read()
