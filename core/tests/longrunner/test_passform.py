# -*- coding: utf-8 -*-
u"""Die Passform-Voreinstellungen — zeigen sie nur, was auch wirkt?

Edgar, 08.09.2026: „Mach mir die Voreinstellungen fuer die Kleider, oben im
Tab … mit Voreinstellungen fuer eng anliegend, und 2 anderen."

WAS HIER GEPRUEFT WIRD — UND WAS NICHT
======================================
Nicht die Texte und nicht die gemessenen Zahlen: Die stehen in
`Assets/GarmentCode/passform.py` mit ihrer Quelle. Geprueft wird die
Eigenschaft, an der ein Preset scheitern kann, ohne dass es jemand merkt:
**dass jeder gezeigte Wert an diesem Stueck ueberhaupt etwas tut.**

Ein Kaestchen „Eng anliegend", das an einem Kleid `shirt.flare` setzt, sieht
aus wie eine Einstellung und ist keine — `FittedShirt` liest den Wert nicht
(`bodice.py` Zeile 17: `m_bust = body['bust']`). Genau diese Klasse Fehler
hatte der erste Bau: Kleid und Traegertop bekamen Werte, die dort messbar
folgenlos sind.
"""
import sys

from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:      # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from GarmentCode.katalog import Katalog                        # noqa: E402
from GarmentCode.passform import Passformpresets               # noqa: E402
from GarmentCode.regler import Regler                          # noqa: E402


class PassformTest(SimpleTestCase):
    u"""Die Voreinstellungen fuer das ganze Kleidungsstueck."""

    def test_tshirt_bekommt_rumpf_und_aermel(self):
        u"""Beim ungefitteten Shirt wirken beide Weiteregler."""
        presets = Katalog.passform('t-shirt')
        # Seit dem 11.09.2026 ein Oberteil mit Formen: „Eng anliegend" des
        # geraden Shirts und das des taillierten verschmelzen zu einem
        # Kaestchen (`passform_eng+passform_eng_fitted`).
        eng = [p for p in presets if 'passform_eng' in p['schluessel'].split('+')]
        self.assertEqual(len(eng), 1, 'Eng anliegend fehlt beim T-Shirt')
        self.assertIn('shirt.flare', eng[0]['werte'])
        self.assertIn('sleeve.end_width', eng[0]['werte'])

    def test_kleid_bekommt_keine_rumpfweite(self):
        u"""`FittedShirt` liest `width`/`flare` nicht — also stehen sie nicht drin.

        Belegt mit zwei Drapierlaeufen (08.09.2026): `hemd` mit width 1,3 und
        flare 1,6 ergibt Saum 108,3 cm und Hautabstand 6,6 mm — dieselben
        Werte wie die Vorgabe.
        """
        from GarmentCode.regler import Regler
        # Am Anzug (nur FittedShirt) fehlen sie ganz; Kleid und Oberteil
        # fuehren sie seit dem 11.09.2026 fuer ihre Shirt-Formen
        # (Sommerkleid, T-Shirt) mit — ohne die Formen nicht.
        for vorlage in ('anzug', 'jumpsuit'):
            for preset in Katalog.passform(vorlage):
                self.assertNotIn('shirt.width', preset['werte'], vorlage)
                self.assertNotIn('shirt.flare', preset['werte'], vorlage)
        for vorlage in ('kleid', 'hemd'):
            for preset in Regler.passform(Katalog.entwurf(vorlage)):
                self.assertNotIn('shirt.width', preset['werte'], vorlage)
                self.assertNotIn('shirt.flare', preset['werte'], vorlage)

    def test_aermelloses_stueck_bekommt_keine_aermelwerte(self):
        u"""An der Unterwaesche (BH ohne Aermel) laeuft jeder Aermelregler
        ins Leere. Das Traegertop ist seit dem 11.09.2026 eine FORM des
        Oberteils, und das Oberteil fuehrt die Passform aller seiner Formen
        — der Reiter zeichnet sie einmal je Stueck."""
        for preset in Katalog.passform('unterwaesche'):
            if preset.get('form'):
                continue
            for pfad in preset['werte']:
                self.assertFalse(pfad.startswith('sleeve.'),
                                 'Aermelwert am aermellosen Stueck: %s' % pfad)
        top = next(p for p in Katalog.passform('oberteil') if p['titel'] == u'Trägertop')
        self.assertTrue(top['werte']['sleeve.sleeveless'])
        self.assertIn('sleeve.length', top['zurueck'])

    def test_hose_bekommt_ihre_eigenen(self):
        u"""Seit dem 08.09.2026 hat jedes Stueck welche.

        Edgar: „ich hatte dir aufgetragen fuer jedes Kleidungsstueck
        voreinstellungen zu machen «eng anliegend» usw." Die Hose bekommt
        `pants.width`/`pants.flare` — und KEINE Oberteilwerte, die sie
        nicht liest.
        """
        presets = Katalog.passform('hose')
        self.assertTrue(presets, 'Hose ohne Passform-Voreinstellung')
        for preset in presets:
            for pfad in preset['werte']:
                # `bau.*` sind Bauwerte (Leggings: an die Haut ziehen), keine
                # Schnittwerte — erlaubt, wenn in `BAU_PFADE` angemeldet.
                if pfad.startswith('bau.'):
                    self.assertIn(pfad, Passformpresets.BAU_PFADE)
                    continue
                self.assertTrue(pfad.startswith('pants.'), pfad)

    def test_traegertop_bekommt_keine(self):
        u"""Ein aermelloses, tailliertes Top hat keine Weiteregler.

        Das ist der Fall, in dem „keine" die richtige Antwort ist: Rumpf
        aus den Massen (`FittedShirt`), kein Aermel. Seit dem 11.09.2026
        ist das Traegertop eine Form des Oberteils; ohne die Formen und
        ohne die Varianten der anderen Formen bleibt nichts.
        """
        from GarmentCode.regler import Regler
        self.assertEqual(Regler.passform(Katalog.entwurf('traegertop')), [])
        self.assertTrue(any(p.get('form') for p in Katalog.passform('traegertop')))

    def test_kleid_fasst_oberteil_und_rock_zusammen(self):
        u"""Ein Titel, ein Kaestchen — auch wenn zwei Presets zutreffen.

        Ohne `_verschmelzen` stuenden am Kleid ZWEI „Eng anliegend"
        untereinander (eines fuers Oberteil, eines fuer den Rock). Nicht
        zu bedienen: Man sieht nicht, welches welches ist.
        """
        presets = Katalog.passform('kleid')
        titel = [p['titel'] for p in presets]
        self.assertEqual(len(titel), len(set(titel)), titel)
        eng = [p for p in presets if p['titel'] == u'Eng anliegend'][0]
        gruppen = {pfad.split('.')[0] for pfad in eng['werte']}
        self.assertIn('sleeve', gruppen)
        self.assertIn('pencil-skirt', gruppen)
        # Und der zusammengesetzte Schluessel muss beide Teile finden.
        self.assertEqual(sorted(Passformpresets.werte(eng['schluessel'])),
                         sorted(eng['werte']))

    def test_kein_preset_ist_leer(self):
        u"""Ein Preset ohne wirksame Werte darf nicht erscheinen."""
        for vorlage in Katalog.STUECKE:
            for preset in Katalog.passform(vorlage):
                self.assertTrue(preset['werte'],
                                'leeres Preset bei %s' % vorlage)

    def test_jeder_wert_zeigt_auf_einen_echten_regler(self):
        u"""Ein Pfad, den es nicht gibt, wuerde stumm verworfen."""
        for vorlage in Katalog.STUECKE:
            pfade = self._pfade(vorlage)
            if not pfade:
                continue
            for preset in Katalog.passform(vorlage):
                for pfad in preset['werte']:
                    if pfad in Passformpresets.BAU_PFADE:
                        continue
                    # Die Bausteinfelder einer Form (`meta.*`) sind keine
                    # Regler — `Regler.anwenden` kennt sie trotzdem.
                    if pfad.startswith('meta.'):
                        continue
                    self.assertIn(pfad, pfade,
                                  '%s: %s gibt es nicht' % (vorlage, pfad))

    def test_jeder_wert_liegt_in_seinem_bereich(self):
        u"""Ausserhalb des Bereichs klemmt der Schieber — sichtbar falsch."""
        for vorlage in Katalog.STUECKE:
            bereiche = self._bereiche(vorlage)
            for preset in Katalog.passform(vorlage):
                for pfad, wert in preset['werte'].items():
                    grenzen = bereiche.get(pfad)
                    if not grenzen or not isinstance(wert, (int, float)):
                        continue
                    unten, oben = grenzen
                    self.assertGreaterEqual(wert, unten, '%s %s' % (vorlage, pfad))
                    self.assertLessEqual(wert, oben, '%s %s' % (vorlage, pfad))

    def test_jedes_preset_hat_einen_hinweis_mit_zahl(self):
        u"""Der Hinweis ist der Grund, ein Preset zu nehmen.

        Ohne Messwert ist er eine Behauptung — dann lieber keinen.
        """
        for preset in Passformpresets.PRESETS:
            self.assertTrue(preset.get('hinweis'), preset['schluessel'])
            self.assertTrue(any(z.isdigit() for z in preset['hinweis']),
                            'Hinweis ohne Zahl: %s' % preset['schluessel'])

    def test_gegenprobe_ohne_filter_kaemen_tote_werte_durch(self):
        u"""Sabotage: Ohne die meta-Pruefung stuenden sie im Kleid.

        Ohne diese Gegenprobe pruefte der Test oben eine Eigenschaft, die
        vielleicht ohnehin gilt — und bliebe gruen, wenn der Filter
        ausfaellt (`~/.claude/rules/analysewerkzeuge.md`).
        """
        entwurf = Katalog.entwurf('kleid')
        # Dem Filter wird `Shirt` vorgegaukelt, obwohl das Kleid ein
        # `FittedShirt` ist. Dann MUSS der tote Wert durchkommen — sonst
        # prueft `test_kleid_bekommt_keine_rumpfweite` etwas, das ohnehin
        # gilt, und bliebe gruen, wenn `NUR_UNGEFITTET` ausfaellt.
        roh = Passformpresets.fuer_stueck(
            Regler._gruppennamen(entwurf), {'upper': 'Shirt'}, entwurf)
        pfade = {p for preset in roh for p in preset['werte']}
        self.assertIn('shirt.flare', pfade,
                      'mit vorgetaeuschtem Shirt muesste der Wert durchkommen')

    # -- Hilfen ---------------------------------------------------------------

    def _blaetter(self, gruppen, hinaus=None):
        u"""Alle Reglerpfade eines Stuecks, ueber alle Ebenen."""
        hinaus = {} if hinaus is None else hinaus
        for gruppe in gruppen:
            for feld in gruppe.get('felder', ()):
                hinaus[feld['pfad']] = feld.get('bereich')
            self._blaetter(gruppe.get('untergruppen', ()), hinaus)
        return hinaus

    def _pfade(self, vorlage):
        return set(self._blaetter(Katalog.regler(vorlage)))

    def _bereiche(self, vorlage):
        u"""Pfad -> (unten, oben), nur fuer Zahlenregler."""
        werte = {}
        for pfad, bereich in self._blaetter(Katalog.regler(vorlage)).items():
            if (isinstance(bereich, (list, tuple)) and len(bereich) == 2
                    and all(isinstance(g, (int, float)) for g in bereich)):
                werte[pfad] = (min(bereich), max(bereich))
        return werte
