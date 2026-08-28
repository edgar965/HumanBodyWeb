# -*- coding: utf-8 -*-
"""Charakterdaten — die geteilten, langlebigen Ressourcen an EINER Stelle.

WARUM (Umbau 15.08.2026): In `character_api.py` standen acht Modulfunktionen mit
vier `global`-Variablen als Zwischenspeicher — `_get_morph_data`,
`_get_char_defaults`, `_get_mesh_data`, `_get_cc_subdivider`,
`_gender_from_body_type`, `_build_body_state`, `_get_smpl_library`,
`_get_smpl_body_gen`. Der Aufrufgraph zeigt sie als die einzigen Helfer, die von
MEHREREN Themen benutzt werden (Kleidung, Netz, Morph, Skelett, Rest): genau die
Stellen, an denen ein Schnitt durch die Datei entweder Kopien erzeugt oder
Luecken hinterlaesst. Deshalb kommen sie zuerst und als Klasse.

Die Zwischenspeicher sind bewusst Klassenattribute: Es gibt einen Prozess und
eine Datenlage; zwei Instanzen wuerden dieselben 70.000 Vertices doppelt laden.

FEHLER 16.08.2026: Die Zwischenspeicher wurden VOR dem Laden gesetzt —
`cls._morph_data = MorphData(...)`, danach `load()`. Daphne beantwortet Anfragen
parallel: Ein zweiter Aufruf sah das Attribut schon gesetzt und arbeitete mit
den noch LEEREN Daten weiter. `MorphData.get_l2_for_type()` merkt sich sein
Ergebnis in `_l2_cache` — die leere Morph-Liste blieb also fuer die Lebensdauer
des Prozesses stehen, und `/api/character/morphs/` lieferte dauerhaft
`morphs: []`. Alle Seiten zeigten dann eine leere Morph-Liste; ein Neustart
half nur, solange kein Rennen auftrat, was den Fehler zufaellig erscheinen
liess. Jetzt: erst laden, dann zuweisen, und das Ganze unter einem Schloss.
"""
import logging

import numpy as np
from django.conf import settings

from humanbody_core import CharacterDefaults, CharacterState, MeshData, MorphData
from humanbody_core.catmull_clark import CatmullClarkSubdivider

from ..daten.koerperzustand import Koerperzustand
from ..daten.ladeschloss import Ladeschloss

logger = logging.getLogger('core')


class Charakterdaten:
    """Zugriff auf Morph-Daten, Netze, Voreinstellungen und Unterteiler."""

    _morph_data = None
    _char_defaults = None
    _mesh_data = {}          # {'female': MeshData, 'male': MeshData}
    _cc_subdivider = {}      # {'female': CatmullClarkSubdivider, ...}
    _smpl_library = None
    _smpl_body_gen = None

    #: Schuetzt das Fuellen der Zwischenspeicher — EIN Schloss JE Wert
    #: (18.08.2026). Vorher hielt ein einziges Schloss waehrend der
    #: Catmull-Clark-Unterteilung **gemessene 1,21 s**, und in dieser Zeit
    #: warteten auch Anfragen, die nur die Morphdaten brauchten. Warum
    #: wiedereintretend: siehe `daten/ladeschloss.py`.
    _schloesser = Ladeschloss()

    VORGABE_KOERPERTYP = 'Female_Caucasian'

    # ------------------------------------------------------------ Grunddaten

    @staticmethod
    def geschlecht_zu(koerpertyp):
        """'Male_Caucasian' -> 'male'. Alles andere gilt als weiblich."""
        return 'male' if str(koerpertyp).startswith('Male_') else 'female'

    @classmethod
    def morphdaten(cls):
        def bauen():
            daten = MorphData(data_dir=str(settings.HUMANBODY_DATA_DIR))
            daten.load()
            # Erst nach dem Laden sichtbar machen — sonst sieht eine parallele
            # Anfrage leere Morph-Packs (siehe Modulkopf).
            cls._morph_data = daten
            return daten
        return cls._schloesser.einmal('morph', lambda: cls._morph_data, bauen)

    @classmethod
    def voreinstellungen(cls):
        def bauen():
            werte = CharacterDefaults()
            werte.load(str(settings.HUMANBODY_ROOT / 'settings.yaml'))
            cls._char_defaults = werte
            return werte
        return cls._schloesser.einmal('vorgaben', lambda: cls._char_defaults,
                                      bauen)

    #: Felder von `MeshData`, die als NumPy-Feld im Zwischenspeicher liegen.
    NETZFELDER = ('faces', 'face_materials', 'normals', 'uvs')

    @classmethod
    def netzdaten(cls, geschlecht='female'):
        """MeshData je Geschlecht — die maennlichen Daten liegen in `_male`."""
        def bauen():
            verzeichnis = str(settings.HUMANBODY_DATA_DIR)
            if geschlecht == 'male':
                verzeichnis += '_male'
            netz = MeshData(data_dir=verzeichnis)
            netz.load()
            cls._schreibschutz(netz)
            cls._mesh_data[geschlecht] = netz
            return netz
        return cls._schloesser.einmal('netz:' + geschlecht,
                                      lambda: cls._mesh_data.get(geschlecht),
                                      bauen)

    @classmethod
    def _schreibschutz(cls, netz):
        """Die Felder im Zwischenspeicher gegen Schreibzugriff sperren.

        WARUM (Review-Befund „mutable Rückgabe gecachter NumPy-Arrays", von
        Nemotron als Rückfrage gestellt und am 28.08.2026 nachgeprüft):
        `netzdaten()` gibt das GEMERKTE Objekt heraus, nicht eine Kopie —
        18.210 Punkte, 17.288 Flächen. Wer eines der Felder an Ort und Stelle
        ändert, ändert es für JEDE weitere Anfrage dieses Prozesses. Das ist
        die unangenehmste Sorte Fehler: Die erste Anfrage ist richtig, die
        zweite falsch, und ein Serverneustart „behebt" es.

        Heute schreibt niemand hinein — nachgezählt am 28.08.2026, alle acht
        Aufrufer lesen nur (`netz.faces[…]`, nie `netz.faces[…] =`). Der
        Schutz kostet nichts und macht aus einem stillen Schaden eine
        Ausnahme an der Stelle, an der er entsteht.

        Kopieren wäre die Alternative und ist die schlechtere: 18.210 Punkte
        je Anfrage kopieren, damit niemand schreibt, der ohnehin nicht schreibt.
        """
        for name in cls.NETZFELDER:
            feld = getattr(netz, name, None)
            if isinstance(feld, np.ndarray):
                feld.flags.writeable = False

    # ---------------------------------------------------------- Unterteilung

    @classmethod
    def unterteiler(cls, geschlecht='female'):
        """Catmull-Clark-Unterteiler mit vorbereiteten Referenznormalen.

        Die Normalen werden EINMAL aus dem Basiskoerper gerechnet: Andere
        Koerpertypen haben zusammenfallende Vertices, aus denen sich keine
        brauchbare Richtung ergibt — ohne diese Referenz zeigen dort Flaechen
        nach innen."""
        return cls._schloesser.einmal(
            'unterteiler:' + geschlecht,
            lambda: cls._cc_subdivider.get(geschlecht),
            lambda: cls._unterteiler_bauen(geschlecht))

    @classmethod
    def _unterteiler_bauen(cls, geschlecht):
        """Der teure Teil — laeuft unter dem Schloss NUR dieses Namens.

        Gemessen 1,21 s beim ersten Aufruf. Vorher blockierte er ueber das
        gemeinsame Schloss auch Anfragen, die nur Morph- oder Netzdaten
        brauchten (Befund aus dem Sparring, 18.08.2026).
        """
        mesh = cls.netzdaten(geschlecht)
        if mesh.faces is None or mesh.faces.ndim != 2 or mesh.faces.shape[1] != 4:
            return None
        cc = CatmullClarkSubdivider(mesh.faces,
                                    face_materials=mesh.face_materials,
                                    uvs=mesh.uvs, levels=1)
        logger.info('CC-Unterteiler (%s): %d Basis- -> %d Untervertices, '
                    '%d Dreiecke', geschlecht, mesh.faces.max() + 1,
                    cc.sub_vertex_count, len(cc.triangles))
        cls._referenznormalen(cc, geschlecht)
        # Erst mit fertigen Referenznormalen sichtbar machen.
        cls._cc_subdivider[geschlecht] = cc
        return cc

    @classmethod
    def _referenznormalen(cls, cc, geschlecht):
        basistyp = 'Male_Caucasian' if geschlecht == 'male' else 'Female_Caucasian'
        zustand = CharacterState(cls.morphdaten(), cls.voreinstellungen())
        zustand.set_body_type(basistyp)
        verts = zustand.compute()
        if verts is None:
            return
        cc.compute_quad_normals(cc.subdivide(verts))
        logger.info('CC-Unterteiler (%s): Referenznormalen aus %s',
                    geschlecht, basistyp)

    # ------------------------------------------------------------ SMPL-Teile

    @classmethod
    def smpl_bibliothek(cls):
        def bauen():
            from GarmentFitter.smpl_library import SmplGarmentLibrary
            bibliothek = SmplGarmentLibrary(
                str(settings.HUMANBODY_SMPL_GARMENT_DIR))
            bibliothek.scan()
            # Erst nach dem Einlesen sichtbar — sonst sieht eine parallele
            # Anfrage eine leere Kleiderliste.
            cls._smpl_library = bibliothek
            return bibliothek
        return cls._schloesser.einmal('smpl_bibliothek',
                                      lambda: cls._smpl_library, bauen)

    @classmethod
    def smpl_koerpergenerator(cls):
        def bauen():
            from GarmentFitter.smpl_library import SmplBodyGenerator
            cls._smpl_body_gen = SmplBodyGenerator(str(settings.SMPL_MODELS_DIR))
            return cls._smpl_body_gen
        return cls._schloesser.einmal('smpl_generator',
                                      lambda: cls._smpl_body_gen, bauen)

    # ------------------------------------------------------------- Koerper bauen

    @classmethod
    def koerper_aus(cls, parameter):
        """Morph-Parameter (dict-artig) -> Koerperzustand.

        Erwartet die flache Form aus der Anfrage: `body_type`, `morph_<name>`
        und `meta_<name>`. Ein unbrauchbarer Wert wird uebergangen und
        protokolliert — eine halb gesetzte Figur ist besser als eine Fehlerseite
        wegen eines Reglers."""
        koerpertyp = parameter.get('body_type') or cls.VORGABE_KOERPERTYP
        geschlecht = cls.geschlecht_zu(koerpertyp)

        zustand = CharacterState(cls.morphdaten(), cls.voreinstellungen())
        zustand.set_body_type(koerpertyp)
        for schluessel, wert in parameter.items():
            cls._regler_setzen(zustand, schluessel, wert)

        mesh = cls.netzdaten(geschlecht)
        faces = mesh.faces if (mesh.faces is not None and mesh.faces.ndim == 2) else None
        return Koerperzustand(zustand, geschlecht, zustand.compute(), faces,
                              koerpertyp)

    @staticmethod
    def _regler_setzen(zustand, schluessel, wert):
        if schluessel.startswith('morph_'):
            try:
                zustand.set_morph(schluessel[len('morph_'):], float(wert))
            except (TypeError, ValueError):
                logger.debug('Morphwert %r=%r uebergangen', schluessel, wert)
        elif schluessel.startswith('meta_'):
            try:
                zustand.set_meta(schluessel[len('meta_'):], float(wert))
            except (TypeError, ValueError, AttributeError):
                logger.debug('Metawert %r=%r uebergangen', schluessel, wert)
