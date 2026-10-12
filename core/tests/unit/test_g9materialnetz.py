# -*- coding: utf-8 -*-
"""`G9materialwahl` und `G9materialnetz`: die Materialien einer Genesis-9-Figur ohne Punkte (12.10.2026).

Edgar: „Bei einem reinen Hautwechsel das Netz nicht neu holen und nur die Texturen tauschen." Ein Hautwechsel holte die ganze Netzantwort noch einmal
(10 MB, Serverzeit 0,9–1,4 s); jetzt gibt es `POST …/material/` mit nur den `gruppen` (`core/api/g9materialnetzapi.py`). Geprüft ohne Daz-Bibliothek,
mit Attrappen für Basisnetz, Hautbilder und Anhänge:

1. `G9materialwahl.aus`: ohne Angabe im Rumpf gelten Haut, Augen und Brauen des Eintrags — die Haut nur bei einem GESPEICHERTEN Modell —, die Augen
   sonst `01`; Namen mit Pfadzeichen fallen weg.
2. `G9materialnetz.aus` liefert Stufe, die Gruppen des Körpers mit den Bildern der Haut (Presets darüber) und je Anhang seine Gruppen mit den Bildern
   der Wahl — Stranghaar bringt die Gruppen selbst mit, alles andere liest sie aus der Stufe des Anhangs.
3. Ohne Anhänge (`anhaenge=False`) keine Anhangsgruppen, und `G9anhang.alle` wird nicht einmal gefragt.

NICHT hier geprüft (braucht die Daz-Bibliothek): dass die leichte Antwort bitgleich zur vollen Netzantwort ist. Das ist am 12.10.2026 im Chrome gegen
`…/netz/` verglichen worden — 24 Fälle (fünf Häute, zwei Augenbilder, zwei Brauenfarben, fünf Brauenstile, vier Presets, fünf Figuren): `gruppen` und
Anhangsgruppen gleich.

Sabotage-Gegenprobe (nicht gefahren): in `_gruppen` den Strang-Zweig streichen → Fall 2 rot; `if netz.anhaenge` in `aus` streichen → Fall 3 rot;
in `G9materialwahl.aus` die Prüfung `gespeichert` streichen → Fall 1 rot.
"""
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.materialnetz import G9materialnetz

from core.api.g9materialwahl import G9materialwahl


class _Stufe:
    def __init__(self, stufen, gruppen):
        self.stufen = stufen
        self.gruppen = gruppen


class _Folger:
    ART = None

    def __init__(self, gruppen):
        self._gruppen = gruppen
        self.gefragt = []

    def netzstufe(self, stufen):
        self.gefragt.append(stufen)
        return _Stufe(stufen, self._gruppen)


class _Strang(_Folger):
    ART = 'strang'

    def dreiecke_und_gruppen(self):
        return ['dreiecke'], self._gruppen


class _Basis:
    def __init__(self, stufe):
        self._stufe = stufe

    def netzstufe(self, stufen=None):
        return self._stufe


def _gruppen_mit_bildern(gruppen, bilder):
    """Wie `G9koerpernetz.gruppen_mit_bildern`, nur ohne die Browserbilder: jede Gruppe mit dem, was `bilder` für ihren Namen führt."""
    return [dict(g, bilder=dict(bilder.get(g['name'], {}))) for g in gruppen]


class G9materialwahlTest(SimpleTestCase):

    def test_ohne_angabe_gelten_die_des_eintrags_die_haut_nur_beim_gespeicherten_modell(self):
        eintrag = {'haut': 'Eintragshaut', 'augen': '04', 'brauen': 'Brown', 'brauenstil': 'card02', 'praesets': {'wimpern': 'x'}}
        katalog = G9materialwahl.aus({}, eintrag)
        self.assertIsNone(katalog['hautpreset'], 'ein Katalogeintrag führt seine Haut im Bild, nicht als Wahl')
        self.assertEqual((katalog['augen'], katalog['brauen'], katalog['brauenstil']), ('04', 'Brown', 'card02'))
        self.assertEqual(katalog['praesets'], {'wimpern': 'x'})
        gespeichert = G9materialwahl.aus({}, dict(eintrag, gespeichert=True))
        self.assertEqual(gespeichert['hautpreset'], 'Eintragshaut')

    def test_der_rumpf_geht_vor_und_augen_haben_eine_vorgabe(self):
        wahl = G9materialwahl.aus({'haut': 'G9 Feminine Skin 03 MAT', 'augen': '07', 'praesets': {'lippen': 'rot'}}, {'augen': '04', 'praesets': {'a': 'b'}})
        self.assertEqual((wahl['hautpreset'], wahl['augen'], wahl['praesets']), ('G9 Feminine Skin 03 MAT', '07', {'lippen': 'rot'}))
        self.assertEqual(G9materialwahl.aus({}, {})['augen'], '01')

    def test_pfadzeichen_im_namen_werden_verworfen(self):
        for boese in ('../x', 'a/b', 'a\\b', '  ', '', None):
            self.assertIsNone(G9materialwahl.name(boese), repr(boese))
        self.assertEqual(G9materialwahl.name(' Brown '), 'Brown')
        self.assertEqual(len(G9materialwahl.name('x' * 200)), 80)
        wahl = G9materialwahl.aus({'haut': '../geheim', 'brauenstil': 'a/b'}, {})
        self.assertIsNone(wahl['hautpreset'])
        self.assertIsNone(wahl['brauenstil'])


class G9materialnetzTest(SimpleTestCase):

    def _netz(self, **wahl):
        return G9koerpernetz(None, {'name': 'x'}, **wahl)

    def _aus(self, netz, folger, stufe):
        with (mock.patch('Genesis9.materialnetz.G9basisnetz.holen', return_value=_Basis(stufe)),
              mock.patch('Genesis9.materialnetz.G9charaktere.hautbilder', return_value={'Torso': {'albedo': 'haut.jpg'}}) as haut,
              mock.patch('Genesis9.materialnetz.G9anhang.alle', return_value=folger) as alle,
              mock.patch('Genesis9.materialnetz.G9anhang.bilder', side_effect=lambda s, a, b, st: {'Eye Left': {'albedo': f'{s}-{a}.jpg'}}),
              mock.patch.object(G9koerpernetz, 'gruppen_mit_bildern', side_effect=_gruppen_mit_bildern)):
            return G9materialnetz.aus(netz), haut, alle

    def test_koerper_und_anhaenge_mit_den_bildern_der_wahl(self):
        stufe = _Stufe(1, [{'name': 'Torso', 'index_ab': 0, 'index_anzahl': 6, 'kachel': 1002}])
        augen = _Folger([{'name': 'Eye Left', 'index_ab': 0, 'index_anzahl': 3, 'kachel': 1006}])
        brauen = _Strang([{'name': 'Eyebrows', 'index_ab': 0, 'index_anzahl': 0, 'kachel': 1001}])
        aus, haut, alle = self._aus(self._netz(hautpreset='Skin 03', augen='05', brauenstil='fiber02'), [('augen', augen), ('brauen', brauen)], stufe)
        self.assertEqual(aus['stufen'], 1)
        self.assertEqual(aus['gruppen'][0]['bilder'], {'albedo': 'haut.jpg'})
        self.assertEqual([a['schluessel'] for a in aus['anhaenge']], ['augen', 'brauen'])
        self.assertEqual(aus['anhaenge'][0]['gruppen'][0]['bilder'], {'albedo': 'augen-05.jpg'}, 'das Augenbild der Wahl')
        self.assertEqual(augen.gefragt, [1], 'die Stufe des Anhangs ist die des Körpers')
        self.assertEqual(aus['anhaenge'][1]['gruppen'][0]['name'], 'Eyebrows', 'Stranghaar bringt seine Gruppen selbst mit')
        self.assertEqual(brauen.gefragt, [], 'das Strang-Haar hat keine Stufe')
        self.assertEqual(haut.call_args.args[1], 'Skin 03')
        self.assertEqual(alle.call_args.args[0], 'fiber02', 'der Brauenstil wählt die Anhänge')

    def test_ohne_anhaenge_keine_anhangsgruppen(self):
        stufe = _Stufe(0, [{'name': 'Torso', 'index_ab': 0, 'index_anzahl': 6, 'kachel': 1002}])
        aus, _haut, alle = self._aus(self._netz(anhaenge=False), [('augen', _Folger([]))], stufe)
        self.assertEqual(aus['anhaenge'], [])
        self.assertEqual(aus['stufen'], 0)
        alle.assert_not_called()
