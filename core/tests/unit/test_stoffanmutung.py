# -*- coding: utf-8 -*-
u"""Der Weg der UV vom Server bis ans Material — geprüft am Quelltext.

WARUM AM QUELLTEXT: Die Kette läuft über vier Module und einen
WebGL-Kontext; im Testlauf gibt es keinen. Was hier geprüft wird, sind die
Entscheidungen, die still danebengehen können — nicht das Bild.

DIE STILLEN STELLEN
===================
* **Eine Normalkarte ohne UV tut nichts.** Three.js meldet das nicht: Das
  Material ist gültig, der Shader läuft, die Fläche bleibt glatt. Deshalb
  wird die Karte nur aufgelegt, wenn das Netz UVs führt — und die Bedingung
  muss im Code stehen, nicht in der Absicht.
* **`MeshStandardMaterial` kann keinen Glanzsaum.** `sheen` ist eine
  Eigenschaft von `MeshPhysicalMaterial`; auf dem Standardmaterial gesetzt
  bleibt sie ein Feld ohne Wirkung. Genau so sähe der Rückschritt aus, wenn
  jemand das Material zurückstellt.
* **Eine Textur je Stück.** Ohne `clone()` teilen sich alle Stücke eine
  Textur — und damit die Wiederholung des zuletzt gebauten. Eine Hose
  braucht eine andere als ein T-Shirt (1,70 gegen 1,07 Meter Stoff je
  UV-Einheit).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul


def _lies(*teile):
    u"""Ein Viewer-Modul als Text.

    Über `Jsmodul`, nicht über eine eigene `.parent`-Kette: Die zeigt nach
    dem nächsten Umzug still ins Leere, und ein Test, der eine leere Datei
    liest, findet nichts und meldet grün
    (`~/.claude/rules/projektpfade.md`).
    """
    return Jsmodul(*teile).pfad.read_text(encoding='utf-8')


class DasNetzBekommtSeineUvTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        # Die Geometrie liegt seit dem 11.09.2026 in `garmentcode_geometrie.js`
        # (herausgeloest, als die Koerpernormalen dazukamen); das Material
        # weiter in `garmentcode_anziehen.js`.
        self.geometrie = _lies('scene', 'garmentcode_geometrie.js')
        self.quelle = _lies('scene', 'garmentcode_anziehen.js')

    def test_das_uv_attribut_wird_gesetzt(self):
        self.assertIn("geometrie.setAttribute('uv'", self.geometrie)
        self.assertIn("GarmentcodeGeometrie.aus(daten)", self.quelle)

    def test_die_laenge_wird_gegen_die_punkte_geprueft(self):
        u"""Eine UV-Liste anderer Länge gehört nicht an dieses Netz."""
        self.assertIn('uv.length === punkte.length', self.geometrie)

    def test_die_uv_wird_nicht_in_three_achsen_gedreht(self):
        u"""Die Punkte werden von Z-oben auf Y-oben gedreht; eine UV ist eine
        Lage im flachen Schnittmuster und davon unberührt. Wer sie mitdreht,
        legt das Gewebe quer."""
        stelle = self.geometrie.index("setAttribute('uv'")
        block = self.geometrie[stelle - 400:stelle]
        self.assertIn('flaeche[i * 2] = uv[i][0]', block)
        self.assertIn('flaeche[i * 2 + 1] = uv[i][1]', block)

    def test_die_stoffangaben_gehen_ans_material(self):
        self.assertIn('hatUv:', self.quelle)
        self.assertIn('uvMeter: daten.uv_meter', self.quelle)
        self.assertIn('Garmentstoff.neu(bisher, stoff)', self.quelle)


class DasMaterialIstStoffTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.quelle = _lies('scene', 'garmentcode_stoff.js')

    def test_glanzsaum_braucht_das_physical_material(self):
        # Geprueft wird der AUFRUF, nicht das Wort: Der Modulkopf nennt
        # `MeshStandardMaterial` als das, was es vorher war — auf das blosse
        # Vorkommen zu pruefen war ein Fehlalarm des eigenen Pruefers
        # (`~/.claude/rules/analysewerkzeuge.md`).
        self.assertIn('new THREE.MeshPhysicalMaterial(', self.quelle)
        self.assertNotIn('new THREE.MeshStandardMaterial(', self.quelle)
        for feld in ('sheen:', 'sheenRoughness:', 'sheenColor:'):
            self.assertIn(feld, self.quelle, feld)

    def test_die_karte_kommt_nur_mit_uv(self):
        # Seit dem 11.09.2026 entscheidet `gewebeAuflegen` selbst: ohne UV,
        # ohne Hoehenfunktion („glatt") oder ohne Staerke keine Karte.
        self.assertIn("if (!hatUv || !art.hoehe || !(wahl.staerke > 0))", self.quelle)
        self.assertIn('material.normalMap = null', self.quelle)

    def test_je_stueck_eine_eigene_textur(self):
        self.assertIn('.clone()', self.quelle)
        self.assertIn('karte.repeat.set(', self.quelle)

    def test_die_kachel_wird_nur_einmal_gerechnet(self):
        u"""128×128 RGBA je Stück neu zu rechnen wäre Verschwendung — und
        vier Texturen statt einer im Speicher."""
        self.assertIn('if (Garmentstoff._kacheln[artname]) '
                      'return Garmentstoff._kacheln[artname]', self.quelle)

    def test_die_kachel_wiederholt_sich(self):
        u"""Ohne `RepeatWrapping` läuft die Kachel EINMAL über das Stück, und
        aus dem Gewebe wird ein aufgedrucktes Bild."""
        self.assertIn('THREE.RepeatWrapping', self.quelle)

    def test_mipmaps_und_anisotropie(self):
        u"""Bei rund fünfzig Wiederholungen flimmert eine Karte ohne
        Mipmaps, und an flach stehenden Flächen verschwindet sie ohne
        Anisotropie."""
        self.assertIn('generateMipmaps = true', self.quelle)
        self.assertIn('anisotropy', self.quelle)

    def test_der_glanzsaum_traegt_die_stofffarbe(self):
        u"""Ein weißer Saum auf schwarzer Satin-Leggings stand in der
        Animation als helle Flecken — Edgar hielt sie für Haut (11.09.2026).
        Mit ausgeblendetem Körper blieben sie, mit `sheen = 0` waren sie
        weg. Deshalb gehen Farbe und Glanzfarbe nur noch ZUSAMMEN über
        `faerben`; eine feste weiße Glanzfarbe darf es nicht mehr geben."""
        self.assertIn('static faerben(material, farbe)', self.quelle)
        self.assertIn('material.sheenColor.copy(material.color)', self.quelle)
        self.assertNotIn('GLANZ_FARBE', self.quelle)
        self.assertNotIn('0xffffff', self.quelle)
        # `neu` und `auflegen` setzen die Farbe über `faerben`, nie allein.
        self.assertIn('Garmentstoff.faerben(material, bisher?.farbe', self.quelle)
        self.assertIn('Garmentstoff.faerben(m, werte.farbe)', self.quelle)
        self.assertNotIn('m.color?.set(werte.farbe)', self.quelle)

    def test_auch_die_kleiderregler_ziehen_den_glanzsaum_nach(self):
        u"""Der Assets-Reiter greift jedes `cloth`-Teilnetz, also auch ein
        GarmentCode-Stück; sein Farbfeld darf den weißen Saum nicht
        zurückbringen."""
        for teile in (('scene', 'stueckbedienung.js'), ('scene', 'materialregler.js')):
            quelle = _lies(*teile)
            self.assertIn('material.sheenColor?.copy(material.color)', quelle, teile)
            self.assertNotIn('auswahl.mesh.material.color.set(', quelle, teile)

    def test_die_rechnung_liegt_ausserhalb(self):
        u"""`gemeinsam/gewebe.js` kennt weder DOM noch Three.js — nur so ist
        sie in node prüfbar."""
        self.assertIn("from '../gemeinsam/gewebe.js'", self.quelle)
        gewebe = _lies('gemeinsam', 'gewebe.js')
        self.assertNotIn("from 'three'", gewebe)
        self.assertNotIn('document.', gewebe)
