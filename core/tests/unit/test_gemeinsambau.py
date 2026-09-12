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
// --- Material je Stueck (11.09.2026: „es wurde nur 1 Farbe genommen")
const stand = { farbe: '#ff0000', rauheit: 0.9, metall: 0, gewebe: { art: 'koeper', faeden: 6 } };
const mitFarbe = new Kombiliste();
mitFarbe.hinzufuegen('hose', 'Hose', {}, {}, stand);
stand.farbe = '#00ff00'; stand.gewebe.art = 'satin';       // naechstes Stueck
mitFarbe.hinzufuegen('t-shirt', 'T-Shirt', {}, {}, stand);
pruefe('Farbe eingefroren', mitFarbe.eintraege[0].material.farbe, '#ff0000');
pruefe('Gewebe tief kopiert', mitFarbe.eintraege[0].material.gewebe.art, 'koeper');
pruefe('zweites Stueck eigene Farbe', mitFarbe.eintraege[1].material.farbe, '#00ff00');
pruefe('Material bleibt im Browser', 'material' in mitFarbe.fuerServer()[0], false);
pruefe('gesichert', mitFarbe.sichern(speicher), true);
const wieder = new Kombiliste(); wieder.laden(speicher);
pruefe('Material ueberlebt', wieder.eintraege[1].material.farbe, '#00ff00');
console.log(JSON.stringify({ok: true}));
"""


def _lies(*teile):
    return io.open(settings.BASE_DIR.joinpath(*teile), encoding='utf-8').read()


class KombilisteBauTest(SimpleTestCase):

    databases = set()

    def test_die_liste_traegt_die_bauwerte_je_stueck(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_uebernehmen_gibt_die_bauregler_mit(self):
        kombi = _lies('static', 'viewer', 'scene', 'garmentcode_kombi.js')
        self.assertIn('GarmentcodeBauregler.werte(), material)', kombi)
        bauregler = _lies('static', 'viewer', 'scene', 'garmentcode_bauregler.js')
        self.assertIn('static werte()', bauregler)

    def test_jedes_stueck_bekommt_sein_material(self):
        u"""Der gemeinsame Weg legt nach dem Einhaengen das Aussehen des
        GETRAGENEN Stuecks wieder auf — das ist die Farbe, die der Nutzer
        ihm gegeben hat; erst dann den Listeneintrag (ueber `nummer`)."""
        gemeinsam = _lies('static', 'viewer', 'scene', 'garmentcode_gemeinsam.js')
        self.assertIn('liste?.eintraege?.[stueck.nummer]', gemeinsam)
        eines = gemeinsam.index('static async _eines(')
        bisher = gemeinsam.index('GarmentcodeMaterial.getragen(figur, stueck.stueck)', eines)
        einhaengen = gemeinsam.index('GarmentcodeDrapierung.einhaengen(', eines)
        self.assertLess(bisher, einhaengen, 'das Aussehen muss VOR dem Ersetzen gelesen werden')
        self.assertIn('const werte = bisher || material;', gemeinsam)
        self.assertIn('GarmentcodeMaterial.aufStueck(figur, stueck.stueck, werte)', gemeinsam)
        material = _lies('static', 'viewer', 'scene', 'garmentcode_material.js')
        self.assertIn('static aufStueck(figur, stueck, werte = null)', material)
        self.assertIn('static getragen(figur, stueck)', material)
        self.assertIn('werte || GarmentcodeMaterial.stand', material)
        # und „Uebernehmen" nimmt das Aussehen vom getragenen Stueck, nicht
        # den Panel-Stand, der fuer alle Stuecke derselbe ist
        kombi = _lies('static', 'viewer', 'scene', 'garmentcode_kombi.js')
        self.assertIn('GarmentcodeMaterial.getragen(\n            GarmentcodeMaterial.figur(), vorlage) '
                      '|| GarmentcodeMaterial.stand', kombi)

    def test_nur_die_juengste_reglerantwort_zeichnet(self):
        u"""Zwei Anfragen in der Luft (Seitenstart: Vorgabe + gemerkte
        Vorlage): Kam die aeltere zuletzt, merkte ihr Preset `bau.*` unter
        der Vorlage im Feld — die 2 mm der Leggings landeten beim T-Shirt."""
        regler = _lies('static', 'viewer', 'scene', 'garmentcode_regler.js')
        laden = regler.index('async laden(vorlage)')
        block = regler[laden:regler.index('zeichnen(ziel, gruppen)', laden)]
        self.assertIn('const meine = (this.laufnummer = (this.laufnummer || 0) + 1);', block)
        antwort = block.index('await Serverabruf.json(')
        self.assertIn('if (meine !== this.laufnummer) return;',
                      block[antwort:block.index('this.fuerVorlage = vorlage', antwort)])

    def test_eine_alte_kombiliste_wird_im_reiter_gesagt(self):
        kombi = _lies('static', 'viewer', 'scene', 'garmentcode_kombi.js')
        self.assertIn('this.liste.verworfen', kombi)
        self.assertIn('aus einer älteren Fassung', kombi)


class EndpunktBauTest(SimpleTestCase):

    databases = set()

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
        # `nummer` = Stelle in der Wunschliste — auch ueber Luecken hinweg
        self.assertEqual([e['nummer'] for e in gewaehlt], [0, 1])
        mit_luecke = self._stuecke([{'vorlage': 'hose'}, 'muell', {'vorlage': 't-shirt'}])
        self.assertEqual([e['nummer'] for e in mit_luecke], [0, 2])

    def test_unsinn_im_bau_faellt_auf_die_vorgabe(self):
        gewaehlt = self._stuecke([{'vorlage': 'hose', 'bau': 'quatsch'},
                                  {'vorlage': 'hose', 'bau': {'anliegen_mm': 'x'}}])
        for eintrag in gewaehlt:
            self.assertEqual(eintrag['fein'].hautabstand_mm,
                             Baufeineinstellung.HAUTABSTAND_VORGABE)
            self.assertIsNone(eintrag['fein'].anliegen_mm)


class DienstBauTest(SimpleTestCase):

    databases = set()

    def test_pruefen_reicht_fein_durch_und_setzt_sonst_die_vorgabe(self):
        fein = Baufeineinstellung(anliegen_mm=2.0)
        gewaehlt = Garmentgemeinsam._pruefen([
            {'vorlage': 'hose', 'fein': fein}, {'vorlage': 't-shirt'}])
        self.assertIs(gewaehlt[0]['fein'], fein)
        self.assertIsInstance(gewaehlt[1]['fein'], Baufeineinstellung)
        self.assertIsNone(gewaehlt[1]['fein'].anliegen_mm)
        # und die Nummer geht bis in den Bericht je Stueck
        gewaehlt = Garmentgemeinsam._pruefen([
            {'vorlage': 'hose', 'nummer': 3}, {'vorlage': 't-shirt', 'nummer': 0}])
        self.assertEqual([e['nummer'] for e in gewaehlt], [3, 0])
        ablage = _lies_assets('gemeinsamablage.py')
        self.assertIn("'nummer': schnitt.get('nummer')", ablage)

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

    databases = set()

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
        with mock.patch('GarmentCode.gemeinsamablage.Hautmitstoff') as klasse:
            haut = klasse.return_value
            haut.anleger.return_value = anleger
            haut.stuecke = ['shirt']
            neu, anlage, normalen = Gemeinsamablage._anlegen(
                schnitt, 'alt', 'dreiecke', ('kp', 'kf'), {'shirt': 'sp'})
        klasse.assert_called_once_with('kp', 'kf')
        haut.aufnehmen.assert_called_once_with('sp', 'shirt')
        haut.anleger.assert_called_once_with('dreiecke')
        anleger.anlegen.assert_called_once_with('alt', 2.0, None)
        self.assertEqual((neu, anlage['angelegt'], normalen), ('neu', 3, 'normalen'))
        self.assertEqual(anlage['ueber_getragene'], ['shirt'])

    def test_das_stueck_legt_vor_dem_anziehen_an(self):
        quelle = _lies_assets('gemeinsamablage.py')
        ablegen = quelle.index('def _stueck_ablegen')
        anlegen = quelle.index('cls._anlegen(', ablegen)
        anziehen = quelle.index('anzieher.anziehen(punkte)', ablegen)
        self.assertLess(anlegen, anziehen)
        self.assertIn('normalen=normalen', quelle[anziehen:])


def _lies_assets(name):
    return io.open(settings.ASSETS_ROOT / 'GarmentCode' / name,
                   encoding='utf-8').read()
