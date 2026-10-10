# -*- coding: utf-8 -*-
"""Läuft IN Blender (importiert von `hautbacken_normalen_golden.py`): kleine künstliche Netze für die Golden-Daten der Blender-Normalen.

Jedes Netz prüft einen Zweig von Blenders `mesh_normals.cc` (v5.2.2): glatt/scharf/flach, n-Ecken, offene Ränder, nicht-mannigfaltige Kanten (drei Polygone, gegenläufiger Umlaufsinn),
lose Punkte, eigene Normalen je Ecke und je Punkt (zusammenbleibende Fächer), eine Spitze mit ungültigem Lnor-Raum. `zufallsnetz(seed)` mischt davon zufällig (Gegenprobe der Fächerlogik).
Bekannt und ausgespart: ein Polygon, das einen Punkt zweimal benutzt — Blender setzt die zweite Ecke nie (nicht initialisierter Speicher), das ist kein Vergleichswert.
"""

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np


def netz(name, punkte, flaechen, scharfe_kanten=(), flache_flaechen=(), eigene=None, eigene_punkte=None):
    """Netz aus Listen. `scharfe_kanten`: Punktpaare. `flache_flaechen`: Polygonindizes. `eigene`/`eigene_punkte`: Funktion(me) → Normalen je Ecke bzw. je Punkt."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, q)) for q in punkte], [], [tuple(f) for f in flaechen])
    me.update()
    glatt = np.ones(len(me.polygons), dtype=np.int8)
    if len(flache_flaechen):
        glatt[list(flache_flaechen)] = 0
    me.polygons.foreach_set('use_smooth', glatt)
    if len(scharfe_kanten):
        paare = {tuple(sorted(k)) for k in scharfe_kanten}
        for kante in me.edges:
            if tuple(sorted(kante.vertices)) in paare:
                kante.use_edge_sharp = True
    me.update()
    if eigene is not None:
        me.normals_split_custom_set(eigene(me))
        me.update()
    if eigene_punkte is not None:
        me.normals_split_custom_set_from_vertices(eigene_punkte(me))
        me.update()
    return me


def zufall_normalen(startwert):
    """Eigene Normalen je Ecke: die automatische Normale plus Rauschen (macht die Kanten dazwischen scharf)."""
    def f(me):
        rng = np.random.default_rng(startwert)
        auto = np.empty(len(me.loops) * 3, dtype=np.float32)
        me.corner_normals.foreach_get('vector', auto)
        n = auto.reshape(-1, 3) + 0.6 * rng.normal(size=(len(me.loops), 3))
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        return [tuple(float(x) for x in v) for v in n]
    return f


def punkt_normalen(startwert, streuung=0.5, hin=None):
    """Eine eigene Normale je PUNKT (alle Ecken des Punkts gleich → die Fächer bleiben zusammen). `hin`: feste Richtung statt Zufall."""
    def f(me):
        rng = np.random.default_rng(startwert)
        auto = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertex_normals.foreach_get('vector', auto)
        n = auto.reshape(-1, 3) + streuung * rng.normal(size=(len(me.vertices), 3))
        if hin is not None:
            n = np.tile(np.array(hin, dtype=np.float64), (len(me.vertices), 1))
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        return [tuple(float(x) for x in v) for v in n]
    return f


def wuerfel(a=1.0):
    p = [(-a, -a, -a), (a, -a, -a), (a, a, -a), (-a, a, -a), (-a, -a, a), (a, -a, a), (a, a, a), (-a, a, a)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return p, f


def kugel(u=12, v=8, r=1.0):
    p = [(0, 0, r)]
    for j in range(1, v):
        t = np.pi * j / v
        for i in range(u):
            a = 2 * np.pi * i / u
            p.append((r * np.sin(t) * np.cos(a), r * np.sin(t) * np.sin(a), r * np.cos(t)))
    p.append((0, 0, -r))
    f = [(0, 1 + (i + 1) % u, 1 + i) for i in range(u)]
    for j in range(v - 2):
        for i in range(u):
            a, b = 1 + j * u + i, 1 + j * u + (i + 1) % u
            f.append((a, b, b + u, a + u))
    letzte = 1 + (v - 2) * u
    f += [(len(p) - 1, letzte + i, letzte + (i + 1) % u) for i in range(u)]
    return p, f


def gitter(n=6, m=5, hoehe=0.3):
    rng = np.random.default_rng(3)
    p = [(i, j, hoehe * float(rng.normal())) for j in range(m + 1) for i in range(n + 1)]
    f = [(j * (n + 1) + i, j * (n + 1) + i + 1, j * (n + 1) + i + n + 2, j * (n + 1) + i + n + 1) for j in range(m) for i in range(n)]
    return p, f


def prisma(ecken=7):
    """Prisma mit n-Eck-Deckeln (Newell), oben leicht uneben."""
    rng = np.random.default_rng(5)
    unten = [(np.cos(2 * np.pi * i / ecken), np.sin(2 * np.pi * i / ecken), 0.0) for i in range(ecken)]
    oben = [(1.1 * np.cos(2 * np.pi * i / ecken), 0.9 * np.sin(2 * np.pi * i / ecken), 1.0 + 0.1 * float(rng.normal())) for i in range(ecken)]
    f = [tuple(reversed(range(ecken))), tuple(range(ecken, 2 * ecken))]
    f += [(i, (i + 1) % ecken, ecken + (i + 1) % ecken, ecken + i) for i in range(ecken)]
    return unten + oben, f


def spitze():
    """Dünne Pyramide: die Kanten an der Spitze liegen fast in Richtung der Fächernormalen → ungültiger Lnor-Raum."""
    p = [(0, 0, 0), (0.5, 0.5, -100), (-0.5, 0.5, -100), (-0.5, -0.5, -100), (0.5, -0.5, -100)]
    return p, [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)]


def kuenstlich(fall):
    """Alle künstlichen Fälle; `fall(me, name)` legt Netz und Blenders Normalen ab."""
    p, f = wuerfel()
    alle = [(f_[i], f_[(i + 1) % len(f_)]) for f_ in f for i in range(len(f_))]
    fall(netz('wuerfel_glatt', p, f), 'wuerfel_glatt')
    fall(netz('wuerfel_alle_scharf', p, f, scharfe_kanten=alle), 'wuerfel_alle_scharf')
    fall(netz('wuerfel_kanten', p, f, scharfe_kanten=[(0, 1), (1, 2), (4, 5), (0, 4), (2, 6)]), 'wuerfel_kanten')
    fall(netz('wuerfel_flach', p, f, flache_flaechen=[0, 3]), 'wuerfel_flach')
    fall(netz('wuerfel_alle_flach', p, f, flache_flaechen=range(6)), 'wuerfel_alle_flach')
    fall(netz('wuerfel_eigene', p, f, scharfe_kanten=[(0, 1), (1, 2)], eigene=zufall_normalen(1)), 'wuerfel_eigene')
    fall(netz('wuerfel_punkt', p, f, eigene_punkte=punkt_normalen(11)), 'wuerfel_punkt')
    p, f = kugel()
    kanten = [(f_[i], f_[(i + 1) % len(f_)]) for f_ in f[40:60] for i in range(len(f_))][::3]
    fall(netz('kugel_glatt', p, f), 'kugel_glatt')
    fall(netz('kugel_eigene', p, f, eigene=zufall_normalen(2)), 'kugel_eigene')
    fall(netz('kugel_scharf_flach', p, f, scharfe_kanten=kanten, flache_flaechen=[3, 11, 12, 30]), 'kugel_scharf_flach')
    fall(netz('kugel_scharf_eigene', p, f, scharfe_kanten=kanten, flache_flaechen=[11, 30], eigene=zufall_normalen(4)), 'kugel_scharf_eigene')
    fall(netz('kugel_punkt', p, f, eigene_punkte=punkt_normalen(12, 0.3)), 'kugel_punkt')
    fall(netz('kugel_punkt_scharf', p, f, scharfe_kanten=kanten, flache_flaechen=[5], eigene_punkte=punkt_normalen(13, 0.3)), 'kugel_punkt_scharf')
    p, f = gitter()
    fall(netz('gitter_offen', p, f), 'gitter_offen')
    fall(netz('gitter_offen_scharf', p, f, scharfe_kanten=[(8, 9), (9, 10), (10, 17), (12, 19), (19, 26)], flache_flaechen=[7]), 'gitter_offen_scharf')
    fall(netz('gitter_eigene', p, f, scharfe_kanten=[(8, 9), (9, 10)], eigene=zufall_normalen(6)), 'gitter_eigene')
    fall(netz('gitter_punkt', p, f, eigene_punkte=punkt_normalen(14, 0.4)), 'gitter_punkt')
    p, f = prisma()
    fall(netz('prisma_ngon', p, f), 'prisma_ngon')
    fall(netz('prisma_ngon_scharf', p, f, scharfe_kanten=[(0, 1), (1, 2), (7, 8)], flache_flaechen=[1]), 'prisma_ngon_scharf')
    fall(netz('prisma_ngon_eigene', p, f, scharfe_kanten=[(0, 1)], eigene=zufall_normalen(8)), 'prisma_ngon_eigene')
    fall(netz('prisma_punkt', p, f, eigene_punkte=punkt_normalen(15, 0.4)), 'prisma_punkt')
    # Nicht-mannigfaltig: drei Dreiecke an einer Kante, gegenläufiger Umlaufsinn, lose Punkte (5 und 8)
    p = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (2, 2, 2), (3, 0, 1), (4, 1, 1), (5, 5, 5)]
    f = [(0, 1, 2), (0, 3, 1), (0, 1, 4), (1, 6, 7), (1, 7, 6)]
    fall(netz('nichtmannig', p, f), 'nichtmannig')
    fall(netz('nichtmannig_scharf', p, f, scharfe_kanten=[(0, 1)], eigene=zufall_normalen(9)), 'nichtmannig_scharf')
    # Entartet: Punkte auf einer Geraden (Flächennormale unbestimmbar → (0, 0, 1)), ein Viereck mit doppeltem Punkt
    p = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (0, 1, 0), (1, 1, 0)]
    f = [(0, 1, 2), (1, 2, 3, 3), (0, 1, 5, 4)]
    fall(netz('entartet', p, f), 'entartet')
    p, f = spitze()
    fall(netz('spitze', p, f), 'spitze')
    fall(netz('spitze_eigene', p, f, eigene=zufall_normalen(10)), 'spitze_eigene')
    fall(netz('spitze_punkt', p, f, eigene_punkte=punkt_normalen(1, hin=(0, 0, 1))), 'spitze_punkt')
    fall(netz('spitze_punkt_zufall', p, f, eigene_punkte=punkt_normalen(2, 0.3)), 'spitze_punkt_zufall')


def zufallsnetz(seed):
    """Verformtes Gitter mit Löchern, Dreiecken, gedrehtem Umlaufsinn, doppelten Flächen, dritten Flächen an einer Kante, n-Ecken, scharfen Kanten/Polygonen, eigenen Normalen."""
    rng = np.random.default_rng(seed)
    n, m = int(rng.integers(3, 8)), int(rng.integers(3, 8))
    hoehe = float(rng.uniform(0.0, 0.8))
    p = [(i + rng.normal(0, 0.15), j + rng.normal(0, 0.15), hoehe * rng.normal()) for j in range(m + 1) for i in range(n + 1)]
    f = []
    for j in range(m):
        for i in range(n):
            a = j * (n + 1) + i
            q = [a, a + 1, a + n + 2, a + n + 1]
            r = rng.random()
            if r < 0.12:
                continue
            for t in ([q] if r > 0.4 else [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]):
                f.append(list(reversed(t)) if rng.random() < 0.1 else t)
    if not f:
        f = [[0, 1, n + 2, n + 1]]
    for _ in range(int(rng.integers(0, 3))):
        g = list(f[int(rng.integers(len(f)))])                      # doppelte Fläche
        f.append(list(reversed(g)) if rng.random() < 0.5 else g)
    for _ in range(int(rng.integers(0, 3))):
        g = f[int(rng.integers(len(f)))]                            # dritte Fläche an einer Kante
        p.append(tuple(float(x) * 2 for x in rng.normal(size=3)))
        f.append([g[0], g[1], len(p) - 1])
    if rng.random() < 0.5:                                          # n-Eck an einer Kante
        g = f[int(rng.integers(len(f)))]
        neu = []
        for _ in range(int(rng.integers(3, 6))):
            p.append(tuple(float(x) * 2 for x in rng.normal(size=3)))
            neu.append(len(p) - 1)
        f.append([g[0], g[1]] + neu)
    kanten = sorted({tuple(sorted((g[i], g[(i + 1) % len(g)]))) for g in f for i in range(len(g))})
    scharf = [k for k in kanten if rng.random() < 0.2] if seed % 3 else []
    flach = [i for i in range(len(f)) if rng.random() < 0.1] if seed % 4 == 1 else []
    return netz('fuzz%d' % seed, p, f, scharfe_kanten=scharf, flache_flaechen=flach,
                eigene=zufall_normalen(seed) if seed % 5 == 3 else None, eigene_punkte=punkt_normalen(seed, 0.4) if seed % 5 == 2 else None)
