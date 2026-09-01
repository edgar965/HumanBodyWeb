# -*- coding: utf-8 -*-
u"""Das Blender-Addon laedt — und meldet an, was es anmelden soll.

DER ANLASS (01.09.2026)
=======================
`HumanBodyBlender` hatte keinen einzigen Test. Der Grund klingt
zwingend: Der Code braucht `bpy`, und Blender zu starten ist in diesem
Projekt unerwuenscht. Also blieben 11.788 eigene Zeilen ungeprueft —
darunter `cloth_builder.py` (2.254 Zeilen), `ui.py` (2.194) und
`animation.py` (1.745).

Der Schluss war falsch. Ein Addon laesst sich sehr wohl laden, wenn man
Blenders Module nachbildet (`blenderattrappe.py`), und dabei faellt
genau die Fehlerklasse auf, die ein Umbau erzeugt: ein Import, der ins
Leere zeigt, ein Name, den es auf Modulebene nicht mehr gibt, eine
Klasse, die beim Aufteilen aus einem `classes`-Tupel gefallen ist.

WAS DIESER TEST NICHT IST
=========================
Er ersetzt keinen Blender-Lauf. Ob ein Operator in einer echten Szene
das Richtige tut, sagt er nicht — er sagt, dass das Addon vollstaendig
und in sich stimmig ist.

FREMDCODE BLEIBT AUSSEN VOR
===========================
`convert/retarget_bvh` (Thomas Larsson, GPL-2.0-or-later) und
`kbs_retarget` (KBS DEV, GPL-3) sind fremde Addons, 25.143 der 36.931
Zeilen. Sie werden aktualisiert; ihre Befunde gehen dieses Projekt
nichts an.

BDD - GEGEBEN / DANN
====================
    JedesEigeneModul        ... laesst sich einzeln laden
    DieAnmeldung            ... meldet 93 Klassen an und wieder ab
    DieAttrappe             ... faellt auf, wenn ein Name fehlt
"""
import ast
import importlib
import sys
import unittest
from pathlib import Path

from .blenderattrappe import Blenderattrappe

#: Die Wurzel, unter der die vier Repos liegen.
TOOLS = Path(__file__).resolve().parents[4]
ADDON = TOOLS / 'HumanBodyBlender'

#: Fremde Addons — Urheber siehe Kopf.
FREMD = ('convert', 'kbs_retarget')

#: Kein Quelltext.
KEIN_CODE = ('data', 'cache', '__pycache__')

#: So viele Klassen meldet ``register()`` an. Die Zahl steht hier, damit
#: eine verschwundene Klasse auffaellt statt stillschweigend zu fehlen —
#: sie zu aendern ist eine bewusste Entscheidung, kein Nebeneffekt.
KLASSEN = 93


def eigene_module():
    u"""Die Modulnamen des eigenen Addon-Codes, ohne Fremdbestand."""
    namen = []
    for pfad in sorted(ADDON.rglob('*.py')):
        teile = pfad.relative_to(ADDON).parts
        if teile[0] in FREMD or set(teile) & set(KEIN_CODE):
            continue
        if pfad.name == '__init__.py':
            teile = teile[:-1]
        else:
            teile = teile[:-1] + (pfad.stem,)
        namen.append('.'.join(('HumanBodyBlender',) + teile))
    return namen


class AddonBasis(unittest.TestCase):
    u"""Legt die Pfade so, wie Blender sie dem Addon gibt."""

    databases = []

    @classmethod
    def setUpClass(cls):
        for pfad in (TOOLS, TOOLS / 'HumanBody'):
            if str(pfad) not in sys.path:
                sys.path.insert(0, str(pfad))


class JedesEigeneModul(AddonBasis):
    u"""Jede Datei des Addons laesst sich laden."""

    def test_alle_module_laden(self):
        with Blenderattrappe():
            schlecht = []
            for name in eigene_module():
                try:
                    importlib.import_module(name)
                except Exception as fehler:      # noqa: BLE001
                    schlecht.append('%s — %s: %s'
                                    % (name, type(fehler).__name__, fehler))
        self.assertEqual(schlecht, [], 'Module laden nicht: %s' % schlecht)

    def test_es_sind_ueberhaupt_welche_da(self):
        u"""Sabotageschutz: Eine leere Liste bestuende jeden Test."""
        self.assertGreaterEqual(len(eigene_module()), 15)


class DieAnmeldung(AddonBasis):
    u"""``register()`` meldet jede Klasse an, ``unregister()`` alle ab."""

    def anmelden(self):
        with Blenderattrappe() as attrappe:
            addon = importlib.import_module('HumanBodyBlender')
            addon.register()
            angemeldet = list(attrappe.angemeldet)
            addon.unregister()
            return angemeldet, list(attrappe.angemeldet)

    def test_die_erwartete_zahl(self):
        angemeldet, _uebrig = self.anmelden()
        self.assertEqual(len(angemeldet), KLASSEN)

    def test_nach_dem_abmelden_bleibt_nichts(self):
        _angemeldet, uebrig = self.anmelden()
        self.assertEqual(uebrig, [])

    def test_keine_klasse_doppelt(self):
        u"""Ein Name in zwei ``classes``-Tupeln ist ein Fehler.

        Blender wirft beim zweiten ``register_class`` desselben Namens;
        beim Aufteilen einer Datei passiert das schnell.
        """
        angemeldet, _uebrig = self.anmelden()
        doppelt = {n for n in angemeldet if angemeldet.count(n) > 1}
        self.assertEqual(doppelt, set())


class DieAttrappe(AddonBasis):
    u"""Die Gegenprobe: Der Test muss rot werden koennen."""

    def test_ein_fehlender_name_faellt_auf(self):
        u"""Sabotage — ein Modul, das einen Namen einfuehrt, den es nicht gibt."""
        with Blenderattrappe():
            with self.assertRaises(ImportError):
                exec('from HumanBodyBlender.morphing import GibtEsNicht',
                     {})

    def test_sie_raeumt_sys_modules_wieder_auf(self):
        u"""Sonst sieht der naechste Test im Lauf ein halbes Blender."""
        vorher = 'bpy' in sys.modules
        with Blenderattrappe():
            self.assertIn('bpy', sys.modules)
        self.assertEqual('bpy' in sys.modules, vorher)


class DerGeteilteZustand(AddonBasis):
    u"""Der Anzeigezustand ist EINER — ueber alle Bauteile hinweg.

    Beim Aufteilen von `ui.py` (2.194 Zeilen) wanderten dreizehn
    Modulvariablen in `ui_teile/zustand.py`. Sie wurden vorher mit
    `global` gesetzt, und genau das bricht beim Aufteilen STILL:
    `global` meint immer das eigene Modul. Ein Bauteil, das die
    Teilewahl einschaltet, haette eine eigene Variable angelegt; das
    andere haette weiter `False` gelesen. Kein Fehler, keine Meldung —
    die Teilewahl waere einfach nie an.
    """

    def test_was_ein_bauteil_setzt_sieht_das_andere(self):
        with Blenderattrappe():
            zustand = importlib.import_module(
                "HumanBodyBlender.ui_teile.zustand").Anzeigezustand
            teilewahl = importlib.import_module(
                "HumanBodyBlender.ui_teile.teilewahl")
            zeichnen = importlib.import_module(
                "HumanBodyBlender.ui_teile.zeichnen_koerper")
            vorher = zustand.wahl_laeuft
            try:
                zustand.wahl_laeuft = True
                self.assertIs(teilewahl.Anzeigezustand, zustand)
                self.assertIs(zeichnen.Anzeigezustand, zustand)
                self.assertTrue(teilewahl.Anzeigezustand.wahl_laeuft)
                self.assertTrue(zeichnen.Anzeigezustand.wahl_laeuft)
            finally:
                zustand.wahl_laeuft = vorher

    def test_kein_global_mehr_auf_den_umgezogenen_namen(self):
        u"""Sabotageschutz: Ein zurueckgekehrtes `global` faellt auf.

        UEBER DEN SYNTAXBAUM, NICHT UEBER ZEILEN: Der erste Wurf las
        Text und schlug in `zustand.py` an — dort stehen die alten
        `global`-Zeilen im Docstring, als Erklaerung, warum es sie nicht
        mehr gibt. Ein `ast.Global`-Knoten ist Code; eine Zeile, die so
        aussieht, muss keiner sein.
        """
        alt = {"_pick_mode_active", "_hovered_category", "_zone_tris",
               "_expanded_categories", "_draw_handler", "_updating"}
        gefunden = []
        for pfad in sorted((ADDON / "ui_teile").glob("*.py")):
            baum = ast.parse(pfad.read_text(encoding="utf-8"))
            for knoten in ast.walk(baum):
                if isinstance(knoten, ast.Global) and alt & set(knoten.names):
                    gefunden.append("%s:%d %s"
                                    % (pfad.name, knoten.lineno,
                                       ", ".join(knoten.names)))
        self.assertEqual(gefunden, [])


class DieProjektpfade(AddonBasis):
    u"""Die Datenwurzeln zeigen auf echte Verzeichnisse.

    DIESER TEST HAT EINEN GRUND (01.09.2026): Sechs Dateien im Addon
    berechneten ihre Wurzel selbst, als
    ``os.path.dirname(os.path.dirname(__file__))``. Beim Aufteilen
    rutschten zwei davon in ein Unterpaket — und dieselbe Zeile zeigte
    auf `HumanBodyBlender/` statt auf `A:/3DTools`.

    Das wirft NICHTS. Der BVH-Katalog waere leer gewesen, die
    Frisurenliste auch; die Panels haetten sich normal aufgebaut und
    nichts angeboten. Ein Import-Test findet so etwas nicht — er laedt
    das Modul ja erfolgreich.
    """

    def test_jede_wurzel_gibt_es(self):
        with Blenderattrappe():
            pfade = importlib.import_module(
                "HumanBodyBlender.pfade").Projektpfade
            fehlt = [name for name in ("tools", "humanbody", "daten",
                                       "bvh", "assets", "webapp")
                     if not Path(getattr(pfade, name)()).is_dir()]
        self.assertEqual(fehlt, [], "Wurzeln zeigen ins Leere: %s" % fehlt)

    def test_der_bvh_katalog_findet_dateien(self):
        u"""Die Probe aufs Exempel: Im BVH-Verzeichnis liegen Dateien."""
        with Blenderattrappe():
            katalog = importlib.import_module(
                "HumanBodyBlender.anim.katalog")
            ordner = Path(katalog._BVH_DIR)
            self.assertTrue(ordner.is_dir(), katalog._BVH_DIR)
            self.assertTrue(any(ordner.rglob("*.bvh")),
                            "keine BVH-Datei unter %s" % ordner)

    def test_niemand_rechnet_die_wurzel_selbst_aus(self):
        u"""Sabotageschutz: eine neue `dirname`-Kette faellt auf."""
        kette = "dirname(os.path.dirname("
        gefunden = []
        for name in eigene_module():
            teile = name.split(".")[1:]
            pfad = ADDON.joinpath(*teile)
            pfad = pfad.with_suffix(".py") if pfad.suffix != ".py" else pfad
            if not pfad.is_file():
                pfad = ADDON.joinpath(*teile) / "__init__.py"
            if not pfad.is_file() or pfad.name == "pfade.py":
                continue
            for nummer, zeile in enumerate(
                    pfad.read_text(encoding="utf-8").splitlines(), 1):
                if kette in zeile and not zeile.strip().startswith("#"):
                    gefunden.append("%s:%d" % (pfad.name, nummer))
        self.assertEqual(gefunden, [],
                         "Wurzel selbst gerechnet statt `pfade.py`: %s"
                         % gefunden)


class DieErzeugtenPanels(AddonBasis):
    u"""36 Panel-Klassen aus 18 Bereichen — vollstaendig und verschachtelt.

    `ui.py` schrieb sie einzeln aus: 540 Zeilen, in denen 54 Werte
    steckten, und zwei Saetze desselben (N-Leiste und
    Eigenschaften-Editor). Jetzt erzeugt sie `ui_teile/panelbau.py`.

    Der Test prueft die STRUKTUR, nicht eine abgespeicherte Liste:
    Jeder Satz hat dieselben Bereiche, jedes Kind zeigt auf ein Panel,
    das es gibt, und die Verschachtelung ist nicht flach — fuenf
    Panels haengen unter `wardrobe`. Genau die gingen beim ersten Wurf
    der Fabrik verloren.
    """

    #: 18 Bereiche an zwei Orten.
    ANZAHL = 36

    def panels(self):
        with Blenderattrappe():
            ui = importlib.import_module("HumanBodyBlender.ui")
            return {k.bl_idname: k for k in ui.PANELS}

    def test_die_erwartete_zahl(self):
        self.assertEqual(len(self.panels()), self.ANZAHL)

    def test_jedes_kind_findet_sein_elternpanel(self):
        panels = self.panels()
        verwaist = [n for n, k in panels.items()
                    if getattr(k, "bl_parent_id", None)
                    and k.bl_parent_id not in panels]
        self.assertEqual(verwaist, [])

    def test_genau_zwei_wurzeln(self):
        u"""Eine je Ort — alles andere haengt darunter."""
        wurzeln = sorted(n for n, k in self.panels().items()
                         if not getattr(k, "bl_parent_id", None))
        self.assertEqual(wurzeln, ["HUMANBODY_PT_main",
                                   "HUMANBODY_PT_props_main"])

    def test_die_verschachtelung_ist_nicht_flach(self):
        u"""Fuenf Panels haengen unter `wardrobe`, nicht unter `main`."""
        panels = self.panels()
        unter_garderobe = [n for n, k in panels.items()
                           if getattr(k, "bl_parent_id", "").endswith(
                               "_wardrobe")]
        self.assertEqual(len(unter_garderobe), 10, unter_garderobe)

    def test_beide_saetze_fuehren_dieselben_bereiche(self):
        panels = self.panels()
        leiste = {n[len("HUMANBODY_PT_"):] for n in panels
                  if not n.startswith("HUMANBODY_PT_props_")}
        eigen = {n[len("HUMANBODY_PT_props_"):] for n in panels
                 if n.startswith("HUMANBODY_PT_props_")}
        self.assertEqual(leiste, eigen)

    def test_jedes_panel_zeichnet_etwas(self):
        u"""Ein Panel ohne `draw` waere leer — und faellt sonst nicht auf."""
        ohne = [n for n, k in self.panels().items()
                if not callable(getattr(k, "draw", None))]
        self.assertEqual(ohne, [])
