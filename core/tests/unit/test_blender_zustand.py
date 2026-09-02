# -*- coding: utf-8 -*-
u"""Was das Addon nach dem Laden TUT: Zustand, Pfade, Panels.

Drei Fehlerklassen, die ein Import-Test NICHT findet — er laedt das
Modul ja erfolgreich:

* **`global` nach dem Aufteilen.** Beim Zerlegen von `ui.py` (2.194
  Zeilen) wanderten dreizehn Modulvariablen in `ui_teile/zustand.py`.
  `global` meint immer das EIGENE Modul: Ein Bauteil haette eine eigene
  Variable angelegt, das andere weiter `False` gelesen. Kein Fehler,
  keine Meldung — die Teilewahl waere einfach nie an.
* **Eine Wurzel, die selbst gerechnet wird.** Sechs Dateien bildeten
  `os.path.dirname(os.path.dirname(__file__))`; beim Aufteilen zeigten
  zwei davon auf `HumanBodyBlender/` statt auf `3DTools/`. Der
  BVH-Katalog waere leer gewesen, die Panels haetten sich normal
  aufgebaut und nichts angeboten.
* **Panels, die aus der Liste fallen.** 36 Klassen aus 18 Bereichen,
  zwei Saetze desselben — frueher 540 Zeilen von Hand.

Das Laden und die Anmeldung stehen in `test_blender_addon.py`.

BDD - GEGEBEN / DANN
====================
    DerGeteilteZustand ... eine Variable, nicht je Bauteil eine
    DieProjektpfade    ... jede Wurzel zeigt auf ein echtes Verzeichnis
    DieErzeugtenPanels ... 36 Panels, verschachtelt, jedes zeichnet
"""
import ast
import importlib
import unittest
from pathlib import Path

from ._addonbasis import Addonbasis, ADDON
from .blenderattrappe import Blenderattrappe


class DerGeteilteZustand(Addonbasis):
    u"""Der Anzeigezustand ist EINER — ueber alle Bauteile hinweg.

    Beim Aufteilen von `ui.py` (2.194 Zeilen) wanderten dreizehn
    Modulvariablen in `ui_teile/zustand.py`. Sie wurden vorher mit
    `global` gesetzt, und genau das bricht beim Aufteilen STILL:
    `global` meint immer das eigene Modul. Ein Bauteil, das die
    Teilewahl einschaltet, haette eine eigene Variable angelegt; das
    andere haette weiter `False` gelesen. Kein Fehler, keine Meldung —
    die Teilewahl waere einfach nie an.
    """

    #: Module, die den Anzeigezustand halten. `zeichnen_koerper` stand
    #: hier bis zum 01.09.2026; seither zeichnet `wahlknopf` den
    #: Umschalter fuer BEIDE Panels, und nur der liest den Zustand.
    HALTER = ("HumanBodyBlender.ui_teile.teilewahl",
              "HumanBodyBlender.ui_teile.wahlknopf")

    def test_was_ein_bauteil_setzt_sieht_das_andere(self):
        with Blenderattrappe():
            zustand = importlib.import_module(
                "HumanBodyBlender.ui_teile.zustand").Anzeigezustand
            halter = [importlib.import_module(n)
                      for n in DerGeteilteZustand.HALTER]
            self.assertTrue(halter, "kein Modul haelt den Zustand mehr")
            vorher = zustand.wahl_laeuft
            try:
                zustand.wahl_laeuft = True
                for modul in halter:
                    self.assertIs(modul.Anzeigezustand, zustand,
                                  "%s hat eine EIGENE Kopie" % modul.__name__)
                    self.assertTrue(modul.Anzeigezustand.wahl_laeuft,
                                    "%s sieht die Aenderung nicht"
                                    % modul.__name__)
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


class DieProjektpfade(Addonbasis):
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
        for name in self.eigene_module():
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


class DieErzeugtenPanels(Addonbasis):
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
        u"""Ein Panel ohne `draw` waere leer — und faellt sonst nicht auf.

        Gefragt wird `vars(k)`, nicht `getattr(k, 'draw', None)`: Der
        Erzeuger MUSS jedem Panel ein eigenes `draw` mitgeben. Ein von
        `bpy.types.Panel` geerbtes wuerde die schwaechere Frage bestehen
        und zeichnete doch nichts.
        """
        ohne = [n for n, k in self.panels().items()
                if not callable(vars(k).get('draw'))]
        self.assertEqual(ohne, [])
