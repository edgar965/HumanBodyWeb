# -*- coding: utf-8 -*-
"""Testkern — die Testfassung von `humanbody_core`, getrennt vom Betrieb geladen.

Aus `core/test_character_api.py` herausgelöst (17.08.2026, 564 Zeilen — der
Spitzenbefund von `dateigroesse`). Dort standen sechs Modulvariablen

    _test_module = _test_morph_data = _test_char_defaults = None
    _test_mesh_data = _test_cc_subdivider = _test_propagated_skin_weights = None

und sechs Funktionen, die je eine davon füllten (`freie-funktionen`,
`modulzustand`). Sie gehören zusammen: Es ist EIN Zwischenstand — die Fassung
aus `TestCharakter/`, geladen und aufgebaut. Deshalb eine Klasse.

WARUM DAS ÜBERHAUPT SO GELADEN WIRD
===================================
Die Testseite vergleicht eine ANDERE Fassung von `humanbody_core` (ein
bestimmter Commit unter `TestCharakter/`) mit der laufenden. Beide gleichzeitig
im Prozess zu haben geht nur über `importlib` mit eigenem Modulnamen — und mit
sauber getrennten Zwischenständen, sonst zeigt die Konfigurationsseite plötzlich
die Testdaten.
"""

import importlib.util
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)


class Testkern:
    """Geladene Testfassung samt ihrer Daten — alles klassenweit gemerkt."""

    #: Wurzel der Testfassung (`HumanBodyWeb/../TestCharakter`).
    WURZEL = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))),
        'TestCharakter')

    #: Referenzdateien aus CharMorphPlugin, zum Vergleich daneben.
    CHARMORPH_REF = os.path.join(WURZEL, 'charmorph_ref')

    #: Unter diesem Namen liegt die Testfassung in `sys.modules` — nicht unter
    #: `humanbody_core`, sonst überschreibt sie die laufende.
    MODULNAME = 'humanbody_core_test'

    #: Körpertypen in der Reihenfolge, in der sie als Vorgabe taugen.
    BEVORZUGT = ('Caucasian', 'Male_Caucasian', 'Female_Caucasian')

    _modul = None
    _morphdaten = None
    _vorgaben = None
    _netzdaten = None
    _unterteiler = None
    _gewichte = None

    # ------------------------------------------------------------------- laden

    @classmethod
    def modul(cls):
        """Die Testfassung von `humanbody_core`, einmal geladen."""
        if cls._modul is not None:
            return cls._modul
        ordner = os.path.join(cls.WURZEL, 'humanbody_core')
        anfang = os.path.join(ordner, '__init__.py')
        if not os.path.isfile(anfang):
            raise FileNotFoundError(
                'TestCharakter/humanbody_core fehlt. Anlegen mit: '
                'python TestCharakter/download_version.py <commit>')
        if cls.WURZEL not in sys.path:
            sys.path.insert(0, cls.WURZEL)
        spec = importlib.util.spec_from_file_location(
            cls.MODULNAME, anfang, submodule_search_locations=[ordner])
        modul = importlib.util.module_from_spec(spec)
        sys.modules[cls.MODULNAME] = modul
        cls._laden_mit_ersatznamen(spec, modul)
        cls._modul = modul
        logger.info('Testfassung von humanbody_core geladen: %s', ordner)
        return modul

    @staticmethod
    def _laden_mit_ersatznamen(spec, modul):
        """Beim Ausführen muss `humanbody_core` auf die TESTfassung zeigen.

        Die Untermodule importieren sich gegenseitig unter ihrem echten Namen.
        Deshalb wird der Eintrag für die Dauer des Ladens getauscht — und danach
        zurückgesetzt, sonst rechnet der Betrieb mit der Testfassung weiter.
        """
        vorher = sys.modules.get('humanbody_core')
        sys.modules['humanbody_core'] = modul
        try:
            spec.loader.exec_module(modul)
        finally:
            if vorher is not None:
                sys.modules['humanbody_core'] = vorher
            else:
                sys.modules.pop('humanbody_core', None)

    # -------------------------------------------------------------------- Daten

    @classmethod
    def datenordner(cls):
        return os.path.join(cls.WURZEL, 'data', 'humanBody')

    @classmethod
    def datei(cls, *teile):
        """Pfad einer Datei im Datenordner der Testfassung."""
        return os.path.join(cls.datenordner(), *teile)

    @classmethod
    def morphdaten(cls):
        if cls._morphdaten is None:
            cls._morphdaten = cls.modul().MorphData(data_dir=cls.datenordner())
            cls._morphdaten.load()
        return cls._morphdaten

    @classmethod
    def vorgaben(cls):
        if cls._vorgaben is None:
            cls._vorgaben = cls.modul().CharacterDefaults()
            cls._vorgaben.load(os.path.join(cls.WURZEL, 'settings.yaml'))
        return cls._vorgaben

    @classmethod
    def netzdaten(cls):
        if cls._netzdaten is None:
            cls._netzdaten = cls.modul().MeshData(data_dir=cls.datenordner())
            cls._netzdaten.load()
        return cls._netzdaten

    @classmethod
    def zustand(cls, koerpertyp=None):
        """Ein `CharacterState` der Testfassung, auf einen Körpertyp gestellt."""
        zustand = cls.modul().CharacterState(cls.morphdaten(), cls.vorgaben())
        zustand.set_body_type(koerpertyp or cls.koerpertyp())
        return zustand

    @classmethod
    def koerpertyp(cls):
        """Der Vorgabe-Körpertyp: der erste bekannte, sonst irgendeiner."""
        morphs = cls.morphdaten()
        if not morphs.l1:
            return 'Caucasian'
        for name in cls.BEVORZUGT:
            if name in morphs.l1:
                return name
        return next(iter(morphs.l1))

    # ------------------------------------------------------------- Unterteilung

    @classmethod
    def unterteiler(cls):
        """Catmull-Clark-Unterteiler der Testfassung — oder None.

        None heißt: Das Netz besteht nicht aus Vierecken oder die Klasse fehlt
        in dieser Fassung. Die Antwort fällt dann auf das Grundnetz zurück.
        """
        if cls._unterteiler is not None:
            return cls._unterteiler
        netz = cls.netzdaten()
        if netz.faces is None or netz.faces.ndim != 2 or netz.faces.shape[1] != 4:
            return None
        klasse = cls._unterteiler_klasse()
        if klasse is None:
            return None
        cls._unterteiler = klasse(netz.faces, face_materials=netz.face_materials,
                                  uvs=netz.uvs, levels=1)
        logger.info('Test-Unterteiler: %d Grund- -> %d Unterpunkte',
                    netz.faces.max() + 1, cls._unterteiler.sub_vertex_count)
        cls._referenznormalen()
        return cls._unterteiler

    @classmethod
    def _unterteiler_klasse(cls):
        """`CatmullClarkSubdivider` — am Paket oder aus seiner eigenen Datei."""
        modul = cls.modul()
        if hasattr(modul, 'CatmullClarkSubdivider'):
            return modul.CatmullClarkSubdivider
        pfad = os.path.join(cls.WURZEL, 'humanbody_core', 'catmull_clark.py')
        if not os.path.isfile(pfad):
            logger.error('CatmullClarkSubdivider fehlt in der Testfassung')
            return None
        spec = importlib.util.spec_from_file_location(
            cls.MODULNAME + '.catmull_clark', pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul.CatmullClarkSubdivider

    @classmethod
    def _referenznormalen(cls):
        """Normalen aus dem ersten Körpertyp — sie halten die Glättung fest."""
        typ = next(iter(cls.morphdaten().l1), None)
        if not typ:
            return
        punkte = cls.zustand(typ).compute()
        if punkte is None:
            return
        cls._unterteiler.compute_quad_normals(cls._unterteiler.subdivide(punkte))
        logger.info('Test-Unterteiler: Referenznormalen aus %s', typ)

    # ---------------------------------------------------------------- Gewichte

    @classmethod
    def gewichte(cls):
        """Hautgewichte, durch die Unterteilung gereicht — oder None.

        Die Grundgewichte gelten für das Grundnetz (18k Punkte); die Anzeige
        braucht sie für das unterteilte (70k). Die Reihenfolge stimmt nur, wenn
        sie durch dieselbe Unterteilung laufen — siehe die Lehre „Skin Weights +
        CC Subdivision" im Projektgedächtnis.
        """
        if cls._gewichte is not None:
            return cls._gewichte
        pfad = cls.datei('skin_weights_base.json')
        unterteiler = cls.unterteiler()
        if not os.path.isfile(pfad) or unterteiler is None:
            return None
        with open(pfad, 'r', encoding='utf-8') as f:
            grund = json.load(f)
        logger.info('Test: Hautgewichte weitergereicht, %d Grund- -> %d Unterpunkte',
                    grund['vertex_count'], unterteiler.sub_vertex_count)
        cls._gewichte = unterteiler.propagate_skin_weights(
            grund['weights'], grund['bone_names'])
        return cls._gewichte

    # ---------------------------------------------------------------- vergessen

    @classmethod
    def vergessen(cls):
        """Alles fallen lassen — der nächste Zugriff lädt neu.

        Stand doppelt im Code (`test_reload` und `test_switch_character`, je
        zwölf Zeilen mit sechs `global`-Angaben). Beim Wechsel der Fassung MUSS
        auch `sys.modules` aufgeräumt werden, sonst liefert der Import die alte
        Fassung aus dem Zwischenspeicher.
        """
        for name in [k for k in sys.modules if k.startswith(cls.MODULNAME)]:
            del sys.modules[name]
        cls._modul = None
        cls._morphdaten = None
        cls._vorgaben = None
        cls._netzdaten = None
        cls._unterteiler = None
        cls._gewichte = None
        logger.info('Testfassung vergessen — wird beim nächsten Zugriff neu geladen')
