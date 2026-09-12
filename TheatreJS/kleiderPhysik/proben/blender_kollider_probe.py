# Probe: kollidiert Blenders Stoff mit einem Kollider, der sich BEWEGT und
# VERFORMT? Kugel mit animiertem Ort und animiertem Shape-Key, Tuch darueber.
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 30
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 0.5))
kugel = bpy.context.object
kugel.modifiers.new('koll', 'COLLISION')
kugel.collision.thickness_outer = 0.01
# Bewegung: die Kugel faehrt nach +x
kugel.location = (0, 0, 0.5)
kugel.keyframe_insert('location', frame=1)
kugel.location = (0.6, 0, 0.5)
kugel.keyframe_insert('location', frame=40)
# Verformung: Shape-Key streckt die Kugel in z
kugel.shape_key_add(name='Basis')
sk = kugel.shape_key_add(name='hoch')
for v in sk.data:
    v.co.z = v.co.z * 1.8
sk.value = 0.0
sk.keyframe_insert('value', frame=1)
sk.value = 1.0
sk.keyframe_insert('value', frame=40)
bpy.ops.mesh.primitive_grid_add(
    x_subdivisions=40, y_subdivisions=40, size=2.4, location=(0, 0, 1.3)
)
tuch = bpy.context.object
tuch.modifiers.new('stoff', 'CLOTH')
cs = tuch.modifiers['stoff'].settings
cs.quality = 5
cc = tuch.modifiers['stoff'].collision_settings
cc.use_self_collision = True
cc.distance_min = 0.005
dg = bpy.context.evaluated_depsgraph_get()


def tuch_z(frame):
    sc.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = tuch.evaluated_get(dg)
    zs = [(ev.matrix_world @ v.co) for v in ev.data.vertices]
    return zs


import time as _t  # noqa: E402 — Probe-Skript, laeuft in Blender von oben nach unten

_t0 = _t.perf_counter()
for f in range(1, 31):
    sc.frame_set(f)
print("PROBE zeit_30_bilder_s=%.1f" % (_t.perf_counter() - _t0))
p = tuch_z(30)
p = tuch_z(30)
kev = kugel.evaluated_get(bpy.context.evaluated_depsgraph_get())
kw = [kev.matrix_world @ v.co for v in kev.data.vertices]
kz = max(q.z for q in kw)
kx = sum(q.x for q in kw) / len(kw)
nah = [q.z for q in p if (q.x - kx) ** 2 + q.y**2 < 0.04]
weit = [q.z for q in p if (q.x - kx) ** 2 + q.y**2 > 0.81]
# Stoffpunkte INNERHALB der (gestreckten) Kugel: Ellipsoid-Test im Objektraum
innen = 0
for q in p:
    lokal = kugel.matrix_world.inverted() @ q
    sz = (kz - 0.5) / 0.5
    if (lokal.x / 0.5) ** 2 + (lokal.y / 0.5) ** 2 + (lokal.z / (0.5 * sz)) ** 2 < 1.0:
        innen += 1
print(
    'PROBE kugel_mitte_x=%.2f kugel_oben=%.3f tuch_ueber_kugel_min=%.3f (n=%d) '
    'tuch_am_rand_min=%.3f (n=%d) im_kollider=%d von %d'
    % (
        kx,
        kz,
        min(nah) if nah else -9,
        len(nah),
        min(weit) if weit else -9,
        len(weit),
        innen,
        len(p),
    )
)
