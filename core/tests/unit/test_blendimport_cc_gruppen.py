# -*- coding: utf-8 -*-
"""Blender-Import: Character-Creator-Materialien und -Rollen (Edgar, 09.10.2026: „beim Import des Modells ‚Asian' ist das Kleid /
oder die Textur nicht richtig importiert worden").

Gemessen an `Asian_Girl.blend` (Character Creator mit Rig, `ProjektTemp/_wegwerf/asian/gruppen_dump.py`, `…/materialien_neu.py`):

1. Die Materialien hängen am Principled BSDF über eine Node-GRUPPE (`rl_pbr_shader`, `rl_hair_shader`), die alle Bilder des Materials
   trägt. Der Exporter nahm für Rauheit, Alpha UND Normalen das erste Bild stromaufwärts — das Diffuse: Das Kleid (nur Diffuse) bekam sein
   Farbbild als Deckkraft und verlor die schwarze Hälfte, das Haar bekam die Farbe statt seiner Opacity-Karte, die Schuhe ebenso.
2. Rollen: alle fünf Frisurnetze (Gewichte auf `CC_Base_Head`, dazu NeckTwist/Spine/Schlüsselbeine), die Augen in EINEM Netz (8,4 cm) und
   EyeOcclusion/TearLine landeten als „Shirt" in der Garderobe; mehrere Frisurnetze trugen sonst alle den Namen „Haar".

Sabotage-Gegenprobe: in `Blendexport.bild_vor` den Zweig `if knoten.type == 'GROUP'` streichen → `ExporterGruppenTest.test_1` rot;
`HAAR_KOPFANTEIL` auf 1.0 → `RollenTest.test_1` rot (Real_Hair 0,94); `AUGE_MAX_M` zurück auf 0.05 → `test_2` rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import mock

import numpy  # noqa: F401 — VORAB laden (`mock.patch.dict(sys.modules)` trüge numpy beim Verlassen aus)
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.blendimportrollen import Blendimportrollen
from core.dienste.blendimportstuecke import Blendimportstuecke


class _Eingaenge(list):
    def get(self, name):
        return next((b for b in self if b.name == name), None)


def _buchse(name, von=None, ausgang='Color'):
    links = [SimpleNamespace(from_node=von, from_socket=SimpleNamespace(name=ausgang))] if von is not None else []
    return SimpleNamespace(name=name, is_linked=von is not None, links=links, default_value=None)


def _bild(name):
    return SimpleNamespace(type='TEX_IMAGE', name='tex_' + name, inputs=_Eingaenge(),
                           image=SimpleNamespace(filepath=name, library=None, packed_file=None))


def _gruppe(name, **belegt):
    """Eine CC-Gruppe: `Diffuse Map=<Bild>` … — Schlüssel mit Unterstrich statt Leerzeichen."""
    eingaenge = _Eingaenge(_buchse(k.replace('_', ' '), _bild(v)) for k, v in belegt.items())
    return SimpleNamespace(type='GROUP', name=name, inputs=eingaenge)


def _material(gruppe):
    """Principled BSDF, dessen vier Kanäle ALLE an derselben Gruppe hängen (wie `cc3iid_(rl_pbr_shader_BSDF)`)."""
    eingaenge = _Eingaenge(_buchse(n, gruppe, ausgang=n) for n in ('Base Color', 'Roughness', 'Alpha', 'Normal'))
    bsdf = SimpleNamespace(type='BSDF_PRINCIPLED', name='bsdf', inputs=eingaenge)
    return SimpleNamespace(name='Mat', blend_method='HASHED', node_tree=SimpleNamespace(nodes=[bsdf]))


def _exporter():
    bpy = ModuleType('bpy')
    bpy.path = SimpleNamespace(abspath=lambda pfad, library=None: pfad)
    pfad = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport' / 'blendexport.py'
    with mock.patch.dict(sys.modules, {'bpy': bpy}):
        spec = importlib.util.spec_from_file_location('blendexport_cc_test', pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    with mock.patch('os.makedirs'), mock.patch('os.path.isfile', return_value=True):
        return modul.Blendexport('exportziel')


class ExporterGruppenTest(SimpleTestCase):
    databases = set()

    def _lesen(self, gruppe):
        with mock.patch('os.path.isfile', return_value=True):
            return _exporter().material(_material(gruppe))

    def test_1_nur_diffuse_belegt_dann_keine_deckkraft_und_keine_normalen(self):
        """Das Kleid: die Gruppe trägt NUR das Farbbild — Alpha, Rauheit und Normalen bleiben leer (opak, keine Karte)."""
        m = self._lesen(_gruppe('rl_pbr_shader', Diffuse_Map='kleid_diffuse.jpg'))
        self.assertEqual(m['farbe'], 'kleid_diffuse.jpg')
        for kanal in ('rauheit', 'alpha', 'normalen'):
            self.assertIsNone(m.get(kanal), kanal)

    def test_2_jeder_kanal_nimmt_sein_bild(self):
        """Haar/Schuh: Opacity-Karte als Deckkraft (Ausgang `Color`, ein Graubild), Normalenkarte als Normalen, nicht das Diffuse."""
        m = self._lesen(_gruppe('rl_pbr_shader', Diffuse_Map='d.png', Alpha_Map='opacity.jpg', Normal_Map='normal.png'))
        self.assertEqual((m['farbe'], m['alpha'], m['normalen']), ('d.png', 'opacity.jpg', 'normal.png'))
        self.assertEqual(m['alpha_ausgang'], 'Color')
        self.assertIsNone(m.get('rauheit'), 'ohne Roughness-Karte gibt es keine Rauheitskarte')

    def test_3_eine_unbekannte_gruppe_bleibt_beim_ersten_bild(self):
        """Eingänge ohne Kanalnamen (eine fremde Gruppe): wie vor dem 09.10.2026 — das erste Bild, nichts wird verworfen."""
        m = self._lesen(_gruppe('fremd', Tex='irgendein.png'))
        self.assertEqual((m['farbe'], m['rauheit'], m['alpha'], m['normalen']), ('irgendein.png',) * 4)

    def test_4_ein_bild_ohne_gruppe_bleibt_wie_es_war(self):
        eingang = _buchse('Alpha', _bild('socke_alpha.png'), ausgang='Alpha')
        bsdf = SimpleNamespace(type='BSDF_PRINCIPLED', name='bsdf', inputs=_Eingaenge([eingang]))
        mat = SimpleNamespace(name='M', blend_method='', node_tree=SimpleNamespace(nodes=[bsdf]))
        with mock.patch('os.path.isfile', return_value=True):
            m = _exporter().material(mat)
        self.assertEqual((m['alpha'], m['alpha_ausgang']), ('socke_alpha.png', 'Alpha'))


def _netz(name, z0, z1, gewichte, alpha=False, breite=0.1, punkte=1000):
    material = [{'name': 'm', 'farbe': 'f.png', **({'alpha': 'a.png'} if alpha else {})}]
    return {'name': name, 'datei': name + '.npz', 'punkte': punkte, 'min': [0.0, 0.0, z0], 'max': [breite, breite, z1],
            'gewichte': gewichte, 'materialien': material}


def _asian_cc():
    """Maße und Gewichte von `Asian_Girl.blend` (Blender-Achsen, Meter; Körper 0,021–1,789 m)."""
    kopf = {'CC_Base_Head': 7000.0}
    return {'netze': [
        _netz('CC_Base_Body', 0.021, 1.789, {'CC_Base_Spine02': 9000.0, 'CC_Base_Head': 3000.0, 'CC_Base_L_Hand': 800.0}, breite=0.5, punkte=14164),
        _netz('Bang', 1.600, 1.774, {'CC_Base_Head': 7149.34, 'CC_Base_NeckTwist02': 3.09, 'CC_Base_NeckTwist01': 3.0, 'CC_Base_JawRoot': 0.57},
              alpha=True, breite=0.208),
        _netz('Bun', 1.714, 1.824, kopf, alpha=True, breite=0.116),
        _netz('Female_Angled', 1.674, 1.704, kopf, alpha=True, breite=0.116),
        _netz('Hair_Base', 1.550, 1.821, {'CC_Base_Head': 7466.46, 'CC_Base_NeckTwist01': 42.92, 'CC_Base_Spine02': 0.0}, alpha=True, breite=0.199),
        _netz('Real_Hair', 1.523, 1.749, {'CC_Base_Head': 4051.06, 'CC_Base_NeckTwist01': 2463.54, 'CC_Base_NeckTwist02': 420.33,
                                          'CC_Base_Spine02': 254.43, 'CC_Base_R_Clavicle': 86.6, 'CC_Base_L_Clavicle': 86.03}, alpha=True, breite=0.257),
        _netz('CC_Base_Eye', 1.659, 1.687, {'CC_Base_L_Eye': 324.0, 'CC_Base_R_Eye': 324.0, 'CC_Eye_Displacement_L': 17.0}, breite=0.084),
        _netz('CC_Base_EyeOcclusion', 1.665, 1.676, {'CC_Base_Head': 182.0, 'CC_EyeOcclusion_All_R': 91.0, 'CC_EyeOcclusion_Top_L': 44.0}, breite=0.083),
        _netz('CC_Base_TearLine', 1.665, 1.675, {'CC_Base_Head': 190.0, 'CC_Tearline_All_R': 95.0}, breite=0.082),
        _netz('CC_Base_Teeth', 1.584, 1.639, {'CC_Base_Teeth02': 5.0, 'CC_Base_Teeth01': 4.0}, breite=0.07),
        _netz('Dress_48788_Shape', 0.889, 1.519, {'CC_Base_Spine02': 7000.0, 'CC_Base_Pelvis': 5000.0, 'CC_Base_L_Clavicle': 900.0}, breite=0.413),
        _netz('High_heels', 0.004, 0.174, {'CC_Base_L_Foot': 400.0, 'CC_Base_R_Foot': 400.0}, alpha=True, breite=0.208),
    ], 'armaturen': 1, 'ohne_armatur': []}


class RollenTest(SimpleTestCase):
    databases = set()

    def _rollen(self):
        return {r['name']: r for r in Blendimportrollen(_asian_cc()).zuordnen()}

    def test_1_frisuren_haengen_an_kopf_und_hals(self):
        """Alle fünf Frisurnetze sind Haar — auch Real_Hair (Kopf + Hals 0,94 des Gewichts, der Rest am Schlüsselbein)."""
        rollen = self._rollen()
        for name in ('Bang', 'Bun', 'Female_Angled', 'Hair_Base', 'Real_Hair'):
            self.assertEqual(rollen[name]['rolle'], 'haar', name)

    def test_2_beide_augen_in_einem_netz_und_ihre_hilfsnetze(self):
        rollen = self._rollen()
        self.assertEqual(rollen['CC_Base_Eye']['rolle'], 'auge')
        self.assertEqual(rollen['CC_Base_EyeOcclusion']['rolle'], 'augenzubehoer')
        self.assertEqual(rollen['CC_Base_TearLine']['rolle'], 'augenzubehoer')
        self.assertEqual(rollen['CC_Base_Teeth']['rolle'], 'mund')

    def test_3_kleid_und_schuhe_bleiben_kleidung(self):
        rollen = self._rollen()
        self.assertEqual((rollen['Dress_48788_Shape']['rolle'], rollen['Dress_48788_Shape']['ordner']), ('kleid', 'dresses'))
        self.assertEqual((rollen['High_heels']['rolle'], rollen['High_heels']['ordner']), ('kleid', 'shoes'))
        self.assertEqual(rollen['CC_Base_Body']['rolle'], 'koerper')

    def test_4_mehrere_frisuren_tragen_ihren_netznamen_eine_bleibt_haar(self):
        rollen = self._rollen()
        arten = [r['art'] for r in rollen.values() if r['rolle'] == 'haar']
        self.assertEqual(len(arten), len(set(arten)), 'Name = Kennung des Stücks — jede Frisur braucht ihren eigenen')
        self.assertEqual(rollen['Bun']['art'], 'Haar Bun')
        inventar = _asian_cc()
        inventar['netze'] = [n for n in inventar['netze'] if n['name'] in ('CC_Base_Body', 'Bun')]
        einzeln = {r['name']: r for r in Blendimportrollen(inventar).zuordnen()}
        self.assertNotIn('art', einzeln['Bun'], 'EINE Frisur heißt wie bisher „<Figur> Haar"')

    def test_5_stuecknamen(self):
        bau = object.__new__(Blendimportstuecke)
        bau.figurname, bau.anatomie = 'Asian', 'scham'
        rollen = self._rollen()
        self.assertEqual(bau.anzeige(rollen['Bun']), 'Asian Haar Bun')
        self.assertEqual(bau.anzeige({'name': 'hair', 'rolle': 'haar'}), 'Asian Haar')
        self.assertEqual(bau.anzeige(rollen['Dress_48788_Shape']), 'Asian Kleid')

    def test_6_ein_netz_mit_alpha_aber_ohne_kopfgewicht_bleibt_kleidung(self):
        """Ein Kleid mit Alpha (Spitze) oder der BH ist kein Haar: Gewicht nicht am Kopf, Oberkante nicht am Kopf."""
        inventar = _asian_cc()
        inventar['netze'].append(_netz('Spitze', 1.2, 1.5, {'CC_Base_Spine02': 100.0, 'CC_Base_Head': 3.0}, alpha=True, breite=0.4))
        rollen = {r['name']: r['rolle'] for r in Blendimportrollen(inventar).zuordnen()}
        self.assertEqual(rollen['Spitze'], 'kleid')
