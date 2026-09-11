import os, numpy as np, warp as wp
wp.config.kernel_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warp_cache')
import newton
wp.init()
v = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=np.float32); f = np.array([0,1,2, 0,1,3, 0,2,3, 1,2,3], dtype=np.int32)
b = newton.ModelBuilder(); b.add_cloth_grid(pos=wp.vec3(0,0,2), rot=wp.quat_identity(), vel=wp.vec3(0), dim_x=4, dim_y=4, cell_x=0.1, cell_y=0.1, mass=0.1, fix_left=False, tri_ke=1e3, tri_ka=1e3, tri_kd=1e1, edge_ke=1e-1, edge_kd=0, particle_radius=0.01)
m = newton.Mesh(v, f); s = b.add_shape_mesh(-1, mesh=m); b.color(); model = b.finalize()
src = model.shape_source[s]
print('Mesh.mesh.id            ', src.mesh.id)
print('finalized keys/ids      ', [(k, mm.id) for k, mm in src._finalized_meshes.items()])
for name in ('shape_geo', 'shape_geo_src', 'shape_source_ptr', 'shape_mesh_id'):
    if hasattr(model, name):
        obj = getattr(model, name)
        val = getattr(obj, 'source', obj)
        try: print(name, '->', np.asarray(val.numpy() if hasattr(val, 'numpy') else val)[s])
        except Exception as e: print(name, 'nicht lesbar:', e)
