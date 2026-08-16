# -*- coding: utf-8 -*-
"""BVH-Bewegung in 2D-Bildpunkte projizieren.

Aus core/dienste/keypoints.py herausgeloest (Umbau 16.08.2026): 180 Zeilen
Vorwaertskinematik und orthographische Projektion — eine Rechnung, kein Dienst.
"""


def _parse_bvh_to_2d(bvh_path, video_w, video_h):
    """Parse BVH file, compute forward kinematics, project to 2D.

    Returns (keypoints_list, connections) where:
    - keypoints_list: [{joint_name: (x_px, y_px, 1.0), ...}, ...] per frame
    - connections: [(parent, child), ...] from BVH hierarchy
    """
    import numpy as np

    with open(bvh_path) as f:
        lines = [l.rstrip() for l in f.readlines()]

    # --- Parse HIERARCHY ---
    joints = []
    parent_map = {}
    offset_map = {}
    channels_map = {}
    channel_list = []  # flat ordered (joint, channel_type) for MOTION parsing

    parent_stack = []
    current_joint = None
    in_end_site = False
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line == 'MOTION':
            i += 1
            break

        tokens = line.split()
        if not tokens:
            i += 1
            continue

        if tokens[0] in ('ROOT', 'JOINT'):
            name = tokens[1]
            joints.append(name)
            parent_map[name] = parent_stack[-1] if parent_stack else None
            current_joint = name
            in_end_site = False
        elif tokens[0] == 'End' and len(tokens) > 1 and tokens[1] == 'Site':
            in_end_site = True
            current_joint = None
        elif tokens[0] == '{':
            if in_end_site:
                parent_stack.append('__endsite__')
            elif current_joint:
                parent_stack.append(current_joint)
                current_joint = None
        elif tokens[0] == '}':
            if parent_stack:
                parent_stack.pop()
            in_end_site = False
        elif tokens[0] == 'OFFSET' and not in_end_site and joints:
            offset_map[joints[-1]] = np.array([
                float(tokens[1]), float(tokens[2]), float(tokens[3])])
        elif tokens[0] == 'CHANNELS' and not in_end_site and joints:
            n = int(tokens[1])
            chs = tokens[2:2 + n]
            channels_map[joints[-1]] = chs
            for ch in chs:
                channel_list.append((joints[-1], ch))

        i += 1

    # --- Parse MOTION ---
    while i < len(lines) and not lines[i].strip().startswith('Frames:'):
        i += 1
    i += 1  # skip "Frames: N"
    i += 1  # skip "Frame Time: ..."

    frame_data = []
    while i < len(lines):
        line = lines[i].strip()
        if line:
            frame_data.append([float(v) for v in line.split()])
        i += 1

    if not frame_data or not joints:
        return [], []

    # --- Rotation helper ---
    def rot_mat(axis, angle_deg):
        a = np.radians(angle_deg)
        c, s = np.cos(a), np.sin(a)
        if axis == 'X':
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'Y':
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        else:
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    # --- Forward Kinematics per frame ---
    all_positions = []

    for values in frame_data:
        # Map channel values
        val_idx = 0
        ch_values = {}
        for jnt, ch in channel_list:
            ch_values[(jnt, ch)] = values[val_idx] if val_idx < len(values) else 0
            val_idx += 1

        world_matrices = {}
        world_pos = {}

        for jnt in joints:
            parent = parent_map.get(jnt)
            parent_mat = world_matrices.get(parent, np.eye(4))

            offset = offset_map.get(jnt, np.zeros(3))
            chs = channels_map.get(jnt, [])

            # Translation: offset for children, position channels for root
            tx, ty, tz = offset[0], offset[1], offset[2]
            for ch in chs:
                if ch == 'Xposition':
                    tx = ch_values.get((jnt, ch), 0)
                elif ch == 'Yposition':
                    ty = ch_values.get((jnt, ch), 0)
                elif ch == 'Zposition':
                    tz = ch_values.get((jnt, ch), 0)

            # Rotation: apply in BVH channel order
            R = np.eye(3)
            for ch in chs:
                if ch.endswith('rotation'):
                    angle = ch_values.get((jnt, ch), 0)
                    R = R @ rot_mat(ch[0], angle)

            local = np.eye(4)
            local[:3, :3] = R
            local[:3, 3] = [tx, ty, tz]

            world = parent_mat @ local
            world_matrices[jnt] = world
            world_pos[jnt] = world[:3, 3].copy()

        all_positions.append(world_pos)

    # --- Connections from hierarchy ---
    connections = [(parent_map[j], j) for j in joints if parent_map.get(j)]

    # --- Project to 2D (match Three.js fitOverlayCamera exactly) ---
    # Use first frame bounds, same as Three.js which calls fitOverlayCamera once
    first = all_positions[0]
    fx = [p[0] for p in first.values()]
    fy = [p[1] for p in first.values()]

    cx = (min(fx) + max(fx)) / 2
    cy = (min(fy) + max(fy)) / 2
    size_x = max(fx) - min(fx) or 1
    size_y = max(fy) - min(fy) or 1

    # Three.js uses padding multiplier of 1.5 on skeleton size
    skel_pad = 1.5
    half_w = (size_x * skel_pad) / 2
    half_h = (size_y * skel_pad) / 2

    # Adjust for video aspect ratio (same logic as Three.js fitOverlayCamera)
    video_aspect = video_w / video_h
    skel_aspect = half_w / max(half_h, 0.001)
    if video_aspect > skel_aspect:
        half_w = half_h * video_aspect
    else:
        half_h = half_w / video_aspect

    # Map from camera space [cx-half_w..cx+half_w] x [cy-half_h..cy+half_h]
    # to video pixels [0..video_w] x [0..video_h]
    keypoints_list = []
    for frame_pos in all_positions:
        kp = {}
        for jnt, pos in frame_pos.items():
            sx = (pos[0] - cx + half_w) / (2 * half_w) * video_w
            sy = (cy + half_h - pos[1]) / (2 * half_h) * video_h  # flip Y
            kp[jnt] = (sx, sy, 1.0)
        keypoints_list.append(kp)

    return keypoints_list, connections
