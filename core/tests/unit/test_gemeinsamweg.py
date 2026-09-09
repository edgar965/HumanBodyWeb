# -*- coding: utf-8 -*-
u"""Der Weg „Gemeinsam anziehen" — Endpunkt, Ordner, Verdrahtung.

WARUM DIESE FAELLE (09.09.2026)
==============================
Der gemeinsame Lauf haengt an drei Dingen, die jedes fuer sich STUMM
schiefgehen koennen:

1. **Je Stueck ein eigener Ordner.** `Stoffnachfuehrung.netzpfad` nimmt die
   ERSTE `*_sim_rig.json` eines Ordners, und die Ausgabe-Adresse kennt nur
   ein Pfadstueck. Zwei Ergebnisse in einem Ordner haetten still das
   falsche gebunden.
2. **Eine Marke je Kombination.** Zwei verschiedene Kombinationen im selben
   Ordner hiessen: Die zweite drapiert auf dem Schnitt der ersten — die
   Falle vom 06.09.2026 (`~/.claude/rules/artefakte-benennen.md`).
3. **Ein Einhaeng-Weg fuer beide.** Der Einzelbau und der gemeinsame Lauf
   muessen dieselbe Kette benutzen (Skelett, Anziehen, Ablage, Material,
   Vorschau). Zwei Fassungen liefen auseinander, und ein Stueck aus einem
   gemeinsamen Lauf waere in der Szene nicht mehr dasselbe wie ein einzeln
   gebautes.
"""
import io
import re

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse

from GarmentCode.gemeinsamdienst import Garmentgemeinsam, GemeinsamFehler

WURZEL = settings.BASE_DIR


def _quelle(*teile):
    return io.open(WURZEL.joinpath(*teile), encoding='utf-8').read()


class GemeinsamDienstTest(SimpleTestCase):

    databases = []

    def test_zwei_kombinationen_bekommen_verschiedene_marken(self):
        eine = Garmentgemeinsam._marke(
            [{'vorlage': 'hose'}, {'vorlage': 't-shirt'}], 'female')
        andere = Garmentgemeinsam._marke(
            [{'vorlage': 'hose'}, {'vorlage': 'kleid'}], 'female')
        self.assertNotEqual(eine, andere)

    def test_dieselbe_kombination_bekommt_dieselbe_marke(self):
        u"""Ein neuer Bau ersetzt seinen Vorgaenger — wie beim Einzelstueck.

        Und die REIHENFOLGE der Liste darf daran nichts aendern: Sie sagt
        nichts darueber, was aussen liegt (das entscheidet die Simulation).
        """
        eine = Garmentgemeinsam._marke(
            [{'vorlage': 'hose'}, {'vorlage': 't-shirt'}], 'female')
        andersherum = Garmentgemeinsam._marke(
            [{'vorlage': 't-shirt'}, {'vorlage': 'hose'}], 'female')
        self.assertEqual(eine, andersherum)

    def test_geschlecht_trennt_die_marken(self):
        self.assertNotEqual(
            Garmentgemeinsam._marke([{'vorlage': 'hose'}], 'female'),
            Garmentgemeinsam._marke([{'vorlage': 'hose'}], 'male'))

    def test_die_marke_taugt_als_ordner_und_adresse(self):
        u"""Sie steht im Dateisystem UND in `/api/garmentcode/datei/…/`."""
        marke = Garmentgemeinsam._marke(
            [{'vorlage': 'Sommer Kleid/../x'}], 'FEMALE')
        self.assertRegex(marke, r'^[a-z0-9_-]+$')

    def test_ein_stueck_wird_abgelehnt(self):
        with self.assertRaises(GemeinsamFehler) as fall:
            Garmentgemeinsam._pruefen([{'vorlage': 'hose'}])
        self.assertIn('zwei', str(fall.exception))

    def test_zu_viele_stuecke_werden_abgelehnt(self):
        zuviel = [{'vorlage': 'hose'}] * (Garmentgemeinsam.HOECHSTZAHL + 1)
        with self.assertRaises(GemeinsamFehler):
            Garmentgemeinsam._pruefen(zuviel)

    def test_unbekanntes_stueck_wird_abgelehnt(self):
        u"""Sonst baute `Entwurf` ins Leere, und der Fehler kaeme erst aus
        dem Unterprozess — nach Sekunden statt sofort."""
        with self.assertRaises(GemeinsamFehler) as fall:
            Garmentgemeinsam._pruefen([{'vorlage': 'hose'},
                                       {'vorlage': 'gibtsnicht'}])
        self.assertIn('gibtsnicht', str(fall.exception))

    def test_jedes_stueck_bekommt_einen_eigenen_ordnernamen(self):
        u"""Der Name des `Entwurf`s IST sein Ordner.

        Zwei Stuecke mit demselben Namen laegen im selben Ordner, und
        `netzpfad` naehme die erste Rig-Datei, die sie findet.
        """
        gewaehlt = [{'vorlage': 'hose', 'regler': {}},
                    {'vorlage': 't-shirt', 'regler': {}}]
        marke = Garmentgemeinsam._marke(gewaehlt, 'female')
        namen = ['%s_%s' % (marke, Garmentgemeinsam._sauber(e['vorlage']))
                 for e in gewaehlt]
        self.assertEqual(len(set(namen)), 2)
        for name in namen:
            self.assertNotEqual(name, marke)


class GemeinsamEndpunktTest(SimpleTestCase):

    databases = []

    def test_der_endpunkt_ist_eingetragen(self):
        self.assertEqual(reverse('garmentcode_gemeinsam'),
                         '/api/garmentcode/gemeinsam/')

    def test_ohne_stuecke_kommt_400(self):
        antwort = self.client.post('/api/garmentcode/gemeinsam/',
                                   {'geschlecht': 'female'})
        self.assertEqual(antwort.status_code, 400)

    def test_ein_referenzkoerper_wird_abgelehnt(self):
        u"""Ein SMPL-Koerper hat keine Skinning-Gewichte und bekommt keine
        Stoffkorrektur — der gemeinsame Weg braucht beides. Stillschweigend
        darauf zu drapieren waere der Fehler vom 06.09.2026."""
        antwort = self.client.post('/api/garmentcode/gemeinsam/', {
            'geschlecht': 'female', 'koerper': 'mean_all',
            'stuecke': '[{"vorlage":"hose"},{"vorlage":"t-shirt"}]'})
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('Referenzk', antwort.json()['fehler'])

    def test_nur_post(self):
        self.assertEqual(
            self.client.get('/api/garmentcode/gemeinsam/').status_code, 405)


class GemeinsamVerdrahtungTest(SimpleTestCase):
    u"""Was nur am Quelltext zu pruefen ist."""

    databases = []

    def test_die_vorlage_fuehrt_die_drei_bedienelemente(self):
        vorlage = _quelle('templates', '_garmentcode_panel.html')
        for kennung in ('gc-kombi-hinzu', 'gc-kombi-leeren', 'gc-kombi-liste',
                        'gc-kombi-bauen'):
            self.assertIn('id="%s"' % kennung, vorlage)
        self.assertIn('data-panel-key="gc_kombi"', vorlage)

    def test_der_reiter_haengt_die_liste_ein(self):
        self.assertIn('garmentcodeKombi.einhaengen(',
                      _quelle('static', 'viewer', 'scene', 'garmentcode.js'))

    def test_beide_wege_benutzen_denselben_einhaeng_weg(self):
        u"""Der Einzelbau UND der gemeinsame Lauf rufen `einhaengen`.

        Baut einer davon seine eigene Kette, ist ein Stueck aus einem
        gemeinsamen Lauf in der Szene nicht mehr dasselbe wie ein einzeln
        gebautes — es fehlte etwa der Eintrag in der Ablage, und beim
        naechsten Laden stuende die Figur nackt da (08.09.2026).
        """
        drapieren = _quelle('static', 'viewer', 'scene',
                            'garmentcode_drapieren.js')
        gemeinsam = _quelle('static', 'viewer', 'scene',
                            'garmentcode_gemeinsam.js')
        self.assertIn('static async einhaengen(figur, netz, stueck)',
                      drapieren)
        self.assertIn('GarmentcodeDrapierung.einhaengen(figur, netz',
                      drapieren)
        self.assertIn('GarmentcodeDrapierung.einhaengen(', gemeinsam)
        # Und der gemeinsame Weg baut die Kette NICHT selbst nach.
        for eigenbau in ('GarmentcodeAnziehen.anziehen(',
                         'GarmentcodeAblage.merken(',
                         'GarmentcodeMaterial.anwenden('):
            self.assertNotIn(eigenbau, gemeinsam)

    def test_die_knopfliste_steht_nur_an_einer_stelle(self):
        u"""Sonst bliebe ein Knopf klickbar, waehrend ein Bau laeuft."""
        ablauf = _quelle('static', 'viewer', 'scene', 'garmentcode_ablauf.js')
        gemeinsam = _quelle('static', 'viewer', 'scene',
                            'garmentcode_gemeinsam.js')
        self.assertIn("static KNOEPFE = ['gc-vorschau-2d'", ablauf)
        self.assertIn("'gc-kombi-bauen'", ablauf)
        self.assertIn('GarmentcodeAblauf.KNOEPFE', gemeinsam)
        self.assertNotIn('static KNOEPFE', gemeinsam)

    def test_der_gemeinsame_lauf_hat_eine_frist(self):
        u"""Ohne Frist bliebe der Reiter besetzt, wenn die Antwort
        ausbleibt — der Befund vom 09.09.2026 (`fristabruf.js`). Und die
        Frist muss laenger sein als die des Einzelbaus: Ein gemeinsamer
        Lauf kostet gemessen rund 30 s je Stueck."""
        gemeinsam = _quelle('static', 'viewer', 'scene',
                            'garmentcode_gemeinsam.js')
        self.assertIn('Fristabruf.formular(', gemeinsam)
        self.assertNotIn('Serverabruf.formular(', gemeinsam)
        frist = re.search(r'FRIST_S\s*=\s*(\d+)', gemeinsam)
        self.assertIsNotNone(frist)
        self.assertGreaterEqual(int(frist.group(1)), 300)
