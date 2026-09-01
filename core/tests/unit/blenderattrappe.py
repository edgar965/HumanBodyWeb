# -*- coding: utf-8 -*-
u"""Blenders Module nachbilden, so weit ein Import sie braucht.

WOZU (01.09.2026)
=================
`HumanBodyBlender` ist ein Addon: Sein Code laeuft in Blenders eigenem
Python und importiert `bpy`, `mathutils`, `bmesh`, `gpu`. Ausserhalb von
Blender gibt es diese Module nicht, und Blender zu starten ist in diesem
Projekt ausdruecklich unerwuenscht.

Damit war der gesamte Addon-Code — 11.788 eigene Zeilen, darunter drei
Dateien ueber 1.700 Zeilen — von jeder Pruefung ausgenommen. Ein
Tippfehler in einem Klassennamen, ein Import, der nach einer Aufteilung
ins Leere zeigt, ein Name, den es auf Modulebene nicht mehr gibt: All
das faellt sonst erst auf, wenn jemand das Addon in Blender laedt.

WAS DIE ATTRAPPE KANN UND WAS NICHT
===================================
Sie traegt genau so weit, wie ein `import` reicht: Klassen zum Erben,
Eigenschaftsfabriken, die etwas zurueckgeben, ein `Vector`, der rechnen
kann. Sie fuehrt KEINEN Operator aus und ersetzt keinen Blender-Test —
was `execute()` in einer echten Szene tut, sagt sie nicht.

Das genuegt fuer die Frage, die hier zaehlt: Laedt jedes Modul, und
findet jeder Import sein Ziel?
"""
import math
import sys
import types


class Platzhalter:
    u"""Nimmt jeden Zugriff hin und gibt wieder einen Platzhalter.

    Blender-Code greift beim Import gelegentlich tief in `bpy.app` oder
    `bpy.utils.previews`. Ein Platzhalter, der alles beantwortet, ist
    hier richtig: Die Frage ist, OB das Modul laedt — nicht, was
    Blender zurueckgaebe.
    """

    def __getattr__(self, _name):
        return Platzhalter()

    def __call__(self, *_a, **_k):
        return Platzhalter()

    def __getitem__(self, _schluessel):
        return Platzhalter()

    def __iter__(self):
        return iter(())

    def __bool__(self):
        return False


class Vektor(tuple):
    u"""So viel Vektor, wie Code auf Modulebene braucht."""

    def __new__(cls, werte=(0.0, 0.0, 0.0)):
        return super().__new__(cls, tuple(float(w) for w in werte))

    def __add__(self, anderer):
        return Vektor(x + y for x, y in zip(self, anderer))

    def __sub__(self, anderer):
        return Vektor(x - y for x, y in zip(self, anderer))

    def __mul__(self, faktor):
        return Vektor(x * faktor for x in self)

    __rmul__ = __mul__

    @property
    def length(self):
        return math.sqrt(sum(x * x for x in self))

    def copy(self):
        return Vektor(self)

    def normalized(self):
        laenge = self.length
        if laenge == 0:
            return Vektor(self)
        return Vektor(x / laenge for x in self)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]


class Blenderattrappe:
    u"""Setzt Blenders Module in ``sys.modules`` und raeumt wieder auf."""

    #: Basisklassen, von denen Addon-Klassen erben. Blender gibt ihnen
    #: zur Laufzeit viel mit; zum Erben genuegt der nackte Typ.
    TYPEN = ('Operator', 'Panel', 'PropertyGroup', 'AddonPreferences',
             'UIList', 'Menu', 'Header', 'Object', 'Mesh', 'Armature',
             'Scene', 'Bone', 'PoseBone', 'EditBone', 'Material', 'Image',
             'Action', 'NodeTree', 'ShaderNodeTree', 'Node', 'Context',
             'Event', 'Modifier', 'Collection', 'ID', 'bpy_struct',
             'WindowManager', 'SpaceView3D', 'Object_OT_dummy')

    #: Die Fabriken aus ``bpy.props``. Im Addon stehen sie als Annotation
    #: (``x: IntProperty(...)``) — beim Import wird die Fabrik also
    #: WIRKLICH aufgerufen und muss etwas zurueckgeben.
    EIGENSCHAFTEN = ('BoolProperty', 'BoolVectorProperty', 'IntProperty',
                     'IntVectorProperty', 'FloatProperty',
                     'FloatVectorProperty', 'StringProperty',
                     'EnumProperty', 'PointerProperty',
                     'CollectionProperty', 'RemoveProperty')

    #: Die Fassung, gegen die dieses Addon gebaut ist. Mancher Code
    #: verzweigt schon beim Import danach (``if bpy.app.version < …``).
    FASSUNG = (5, 0, 0)

    def __init__(self):
        self.vorher = {}
        #: Die Klassen, die ``register()`` angemeldet hat — in der
        #: Reihenfolge der Anmeldung. Das ist die Zahl, die ein Umbau
        #: nicht veraendern darf: Faellt eine Klasse beim Aufteilen aus
        #: einem ``classes``-Tupel, faellt sie hier auf.
        self.angemeldet = []

    def __enter__(self):
        for name, modul in self.module().items():
            self.vorher[name] = sys.modules.get(name)
            sys.modules[name] = modul
        return self

    def __exit__(self, *_fehler):
        self._addon_entladen()
        for name, alt in self.vorher.items():
            if alt is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = alt
        return False

    @staticmethod
    def _addon_entladen():
        u"""Das Addon aus ``sys.modules`` nehmen — sonst haelt es Leichen.

        DAS WAR EIN ECHTER FEHLER (01.09.2026): Beim zweiten Durchlauf
        meldete ``register()`` NULL Klassen statt 93. Der Grund: Beim
        ersten Mal band sich der Addon-Code an DIESE Attrappe
        (``bpy.utils.register_class`` ist eine gebundene Methode). Blieb
        das Modul geladen, rief der zweite Lauf weiter die Methode der
        ERSTEN Attrappe — die Anmeldung lief also, nur zaehlte sie in ein
        Objekt, das niemand mehr ansieht.

        Ein Test, der so danebengreift, wird gruen, wenn man ihn allein
        laufen laesst, und rot in der Suite — oder umgekehrt. Deshalb
        beginnt jeder Kontext mit einem frisch geladenen Addon.
        """
        for name in [n for n in sys.modules
                     if n == 'HumanBodyBlender'
                     or n.startswith('HumanBodyBlender.')]:
            del sys.modules[name]

    def _anmelden(self, klasse):
        u"""Was ``bpy.utils.register_class`` bekommt, kommt hierher."""
        self.angemeldet.append(getattr(klasse, '__name__', repr(klasse)))

    def _abmelden(self, klasse):
        name = getattr(klasse, '__name__', repr(klasse))
        if name in self.angemeldet:
            self.angemeldet.remove(name)

    def module(self):
        u"""``{Modulname: Modul}`` — alles, was das Addon einfuehrt."""
        bpy = self.bpy()
        mathutils = self.mathutils()
        extras, batch = self.gpu_extras()
        return {
            'bpy': bpy,
            'bpy.types': bpy.types,
            'bpy.props': bpy.props,
            'bpy.utils': bpy.utils,
            'bpy.app': bpy.app,
            'mathutils': mathutils,
            'mathutils.kdtree': mathutils.kdtree,
            'mathutils.bvhtree': mathutils.bvhtree,
            'mathutils.geometry': mathutils.geometry,
            'bmesh': self.bmesh(),
            'gpu': self.gpu(),
            'gpu_extras': extras,
            'gpu_extras.batch': batch,
        }

    def bpy(self):
        bpy = types.ModuleType('bpy')

        typen = types.ModuleType('bpy.types')
        for name in self.TYPEN:
            setattr(typen, name, type(name, (), {}))
        bpy.types = typen

        props = types.ModuleType('bpy.props')
        for name in self.EIGENSCHAFTEN:
            # Die Vorgabe zurueckgeben, wo es eine gibt: Mancher Code
            # liest sie auf Modulebene wieder aus.
            setattr(props, name, lambda *a, default=None, **k: default)
        bpy.props = props

        utils = types.ModuleType('bpy.utils')
        utils.register_class = self._anmelden
        utils.unregister_class = self._abmelden
        utils.previews = Platzhalter()
        utils.resource_path = lambda *a, **k: ''
        utils.user_resource = lambda *a, **k: ''
        bpy.utils = utils

        app = types.ModuleType('bpy.app')
        app.version = self.FASSUNG
        app.version_string = '.'.join(str(t) for t in self.FASSUNG)
        app.handlers = Platzhalter()
        app.timers = Platzhalter()
        app.background = True
        bpy.app = app

        bpy.data = Platzhalter()
        bpy.context = Platzhalter()
        bpy.ops = Platzhalter()
        bpy.path = Platzhalter()
        return bpy

    def mathutils(self):
        m = types.ModuleType('mathutils')
        m.Vector = Vektor
        m.Matrix = type('Matrix', (), {
            'Identity': staticmethod(lambda n=4: Platzhalter()),
            'Rotation': staticmethod(lambda *a, **k: Platzhalter()),
            'Translation': staticmethod(lambda *a, **k: Platzhalter()),
        })
        m.Quaternion = type('Quaternion', (), {})
        m.Euler = type('Euler', (), {})
        m.Color = type('Color', (), {})

        for name in ('kdtree', 'bvhtree', 'geometry', 'noise', 'interpolate'):
            setattr(m, name, types.ModuleType('mathutils.' + name))
        m.kdtree.KDTree = type('KDTree', (), {})
        m.bvhtree.BVHTree = type('BVHTree', (), {})
        return m

    def bmesh(self):
        m = types.ModuleType('bmesh')
        m.new = lambda *a, **k: Platzhalter()
        m.from_edit_mesh = lambda *a, **k: Platzhalter()
        m.update_edit_mesh = lambda *a, **k: None
        m.ops = Platzhalter()
        m.types = Platzhalter()
        return m

    def gpu(self):
        m = types.ModuleType('gpu')
        m.state = Platzhalter()
        m.matrix = Platzhalter()
        m.shader = Platzhalter()
        m.types = Platzhalter()
        return m

    def gpu_extras(self):
        extras = types.ModuleType('gpu_extras')
        batch = types.ModuleType('gpu_extras.batch')
        batch.batch_for_shader = lambda *a, **k: Platzhalter()
        extras.batch = batch
        return extras, batch
