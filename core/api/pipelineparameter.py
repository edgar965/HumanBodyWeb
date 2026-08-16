# -*- coding: utf-8 -*-
"""Pipelineparameter: Formulardaten der Uploadseite lesen, Vorgaben liefern.

Aus core/api/auftraege.py herausgeloest (Umbau 16.08.2026).

Beide Woerterbuecher bleiben Woerterbuecher (Anforderung 11): `lesen()` liefert
genau das, was als JSON-Feld `BVHJob.pipeline_params` in der Datenbank landet,
`vorgaben()` genau das, was die Vorlage einsetzt. Beide verlassen das Programm
sofort und werden nirgends durch mehrere Funktionen gereicht.
"""


class Pipelineparameter:
    @staticmethod
    def lesen(post, pipeline):
        """Einstellungen der gewaehlten Pipeline aus dem Formular holen."""
        if pipeline == 'v4':
            return Pipelineparameter._v4(post)
        if pipeline == 'gvhmr':
            return Pipelineparameter._gvhmr(post)
        if pipeline == 'wham':
            return {
                'local_only': post.get('wham_local_only') == 'on',
                'smplify': post.get('wham_smplify') == 'on',
                'device': post.get('wham_device', 'cuda'),
            }
        if pipeline == 'prompthmr':
            return {
                'static_cam': post.get('prompthmr_static_cam') == 'on',
                'device': post.get('prompthmr_device', 'cuda'),
            }
        if pipeline.startswith('hybrid_'):
            return Pipelineparameter._hybrid(post)
        return {}

    @staticmethod
    def _teile(post, feld, namen):
        """Angekreuzte Koerperteile als einzelne Wahrheitswerte."""
        gewaehlt = post.getlist(feld)
        return {name: name in gewaehlt for name in namen}

    @staticmethod
    def _v4(post):
        p = {
            'hcd_iterations': int(post.get('v4_hcd_iterations', 10)),
            'hcd_epochs': int(post.get('v4_hcd_epochs', 30)),
            'hcd_learning_rate': float(post.get('v4_hcd_learning_rate', 0.001)),
            'smoothing_cutoff': float(post.get('v4_smoothing_cutoff', 5.0)),
            'smoothing_sampling': float(post.get('v4_smoothing_sampling', 30.0)),
            'mp_detection': float(post.get('v4_mp_detection', 0.5)),
            'mp_tracking': float(post.get('v4_mp_tracking', 0.2)),
        }
        p.update(Pipelineparameter._teile(
            post, 'v4_parts', ('body', 'face', 'hands', 'mouth', 'eyes')))
        return p

    @staticmethod
    def _gvhmr(post):
        p = {
            'static_cam': post.get('gvhmr_static_cam') == 'on',
            'focal_length_mm': float(post.get('gvhmr_focal_length_mm', 0)),
            'device': post.get('gvhmr_device', 'cuda'),
        }
        ordner = post.get('gvhmr_video_output_dir', '').strip()
        if ordner:
            p['video_output_dir'] = ordner
        return p

    @staticmethod
    def _hybrid(post):
        koerper = post.get('hybrid_body_backend', 'gvhmr')
        p = {
            'body_backend': koerper,
            'body_device': post.get('hybrid_body_device', 'cuda'),
            'hands_source': post.get('hybrid_hands_source', 'v4'),
            'face_source': post.get('hybrid_face_source', 'smplest_x'),
            'v4_hcd_iterations': int(post.get('hybrid_v4_hcd_iterations', 10)),
            'v4_hcd_epochs': int(post.get('hybrid_v4_hcd_epochs', 30)),
            'v4_mp_detection': float(post.get('hybrid_v4_mp_detection', 0.5)),
            'v4_mp_tracking': float(post.get('hybrid_v4_mp_tracking', 0.2)),
        }
        if koerper == 'gvhmr':
            p['static_cam'] = post.get('hybrid_gvhmr_static_cam') == 'on'
            p['focal_length_mm'] = float(post.get('hybrid_gvhmr_focal_length_mm', 0))
        else:
            p['static_cam'] = post.get('hybrid_prompthmr_static_cam') == 'on'
        for teil, an in Pipelineparameter._teile(
                post, 'hybrid_v4_parts', ('face', 'hands', 'mouth', 'eyes')).items():
            p['v4_' + teil] = an
        return p

    @staticmethod
    def vorgaben(s):
        """Vorbelegung der Formularfelder aus den Anwendungseinstellungen."""
        return {
            'v4_hcd_iterations': s.v4_hcd_iterations,
            'v4_hcd_epochs': s.v4_hcd_epochs,
            'v4_hcd_learning_rate': s.v4_hcd_learning_rate,
            'v4_smoothing_cutoff': s.v4_smoothing_cutoff,
            'v4_smoothing_sampling': s.v4_smoothing_sampling,
            'v4_mp_detection': s.mp_min_detection_confidence,
            'v4_mp_tracking': s.mp_min_tracking_confidence,
            'v4_body': s.v4_enable_body,
            'v4_face': s.v4_enable_face,
            'v4_hands': s.v4_enable_hands,
            'v4_mouth': s.v4_enable_mouth,
            'v4_eyes': s.v4_enable_eyes,
            'gvhmr_static_cam': s.gvhmr_static_cam,
            'gvhmr_focal_length_mm': s.gvhmr_focal_length_mm,
            'gvhmr_device': s.smpl_device,
            'gvhmr_video_output_dir': s.video_output_dir,
            'wham_local_only': s.wham_estimate_local_only,
            'wham_smplify': s.wham_run_smplify,
            'wham_device': s.smpl_device,
            'prompthmr_static_cam': s.prompthmr_static_camera,
            'prompthmr_device': s.smpl_device,
            # Hybrid greift auf dieselben Einstellungen zurueck
            'hybrid_body_device': s.smpl_device,
            'hybrid_gvhmr_static_cam': s.gvhmr_static_cam,
            'hybrid_gvhmr_focal_length_mm': s.gvhmr_focal_length_mm,
            'hybrid_prompthmr_static_cam': s.prompthmr_static_camera,
            'hybrid_v4_face': s.v4_enable_face,
            'hybrid_v4_hands': s.v4_enable_hands,
            'hybrid_v4_mouth': s.v4_enable_mouth,
            'hybrid_v4_eyes': s.v4_enable_eyes,
            'hybrid_v4_hcd_iterations': s.v4_hcd_iterations,
            'hybrid_v4_hcd_epochs': s.v4_hcd_epochs,
            'hybrid_v4_mp_detection': s.mp_min_detection_confidence,
            'hybrid_v4_mp_tracking': s.mp_min_tracking_confidence,
        }
