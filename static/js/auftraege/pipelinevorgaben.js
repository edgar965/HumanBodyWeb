import { Pipelinefelder } from './pipelinefelder.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Pipelinevorgaben — die drei Qualitaetsstufen (Schnell, Standard, Maximum)
 * je Pipeline in die Formularfelder schreiben.
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026): Tabelle mit
 * 85 Zeilen plus `applyPreset` mit 38 Zeilen inline.
 */
export class Pipelinevorgaben {

    /** Beschriftung der Knoepfe je Stufe — fuer die Hervorhebung. */
    static BESCHRIFTUNG = { fast: 'schnell', standard: 'standard',
                            max: 'maximum' };

    static WERTE = {
        v4: {
            fast: {
                v4_hcd_iterations: 3, v4_hcd_epochs: 10,
                v4_hcd_learning_rate: 0.01, v4_smoothing_cutoff: 10.0,
                v4_smoothing_sampling: 30, v4_mp_detection: 0.3,
                v4_mp_tracking: 0.1,
                v4_parts: { body: true, hands: false, face: false,
                            mouth: false, eyes: false },
            },
            standard: {
                v4_hcd_iterations: 10, v4_hcd_epochs: 30,
                v4_hcd_learning_rate: 0.001, v4_smoothing_cutoff: 5.0,
                v4_smoothing_sampling: 30, v4_mp_detection: 0.5,
                v4_mp_tracking: 0.2,
                v4_parts: { body: true, hands: true, face: true,
                            mouth: true, eyes: false },
            },
            max: {
                v4_hcd_iterations: 50, v4_hcd_epochs: 100,
                v4_hcd_learning_rate: 0.0005, v4_smoothing_cutoff: 2.5,
                v4_smoothing_sampling: 60, v4_mp_detection: 0.7,
                v4_mp_tracking: 0.5,
                v4_parts: { body: true, hands: true, face: true,
                            mouth: true, eyes: true },
            },
        },
        gvhmr: {
            fast: { gvhmr_static_cam: true, gvhmr_focal_length_mm: 0,
                    gvhmr_device: 'cuda', gvhmr_smooth_sigma: 4.0,
                    gvhmr_joint_limits: true },
            standard: { gvhmr_static_cam: true, gvhmr_focal_length_mm: 0,
                        gvhmr_device: 'cuda', gvhmr_smooth_sigma: 2.0,
                        gvhmr_joint_limits: true },
            max: { gvhmr_static_cam: false, gvhmr_focal_length_mm: 0,
                   gvhmr_device: 'cuda', gvhmr_smooth_sigma: 1.0,
                   gvhmr_joint_limits: true },
        },
        wham: {
            fast: { wham_local_only: true, wham_smplify: false,
                    wham_device: 'cuda' },
            standard: { wham_local_only: false, wham_smplify: false,
                        wham_device: 'cuda' },
            max: { wham_local_only: false, wham_smplify: true,
                   wham_device: 'cuda' },
        },
        prompthmr: {
            fast: { prompthmr_static_cam: true, prompthmr_device: 'cuda' },
            standard: { prompthmr_static_cam: true, prompthmr_device: 'cuda' },
            max: { prompthmr_static_cam: false, prompthmr_device: 'cuda' },
        },
        hybrid: {
            fast: {
                hybrid_body_device: 'cuda', hybrid_gvhmr_static_cam: true,
                hybrid_gvhmr_focal_length_mm: 0,
                hybrid_prompthmr_static_cam: true,
                hybrid_hands_source: 'v4', hybrid_face_source: 'smplest_x',
                hybrid_v4_hcd_iterations: 3, hybrid_v4_hcd_epochs: 10,
                hybrid_v4_mp_detection: 0.3, hybrid_v4_mp_tracking: 0.1,
                hybrid_v4_parts: { face: true, hands: true, mouth: false,
                                   eyes: false },
            },
            standard: {
                hybrid_body_device: 'cuda', hybrid_gvhmr_static_cam: true,
                hybrid_gvhmr_focal_length_mm: 0,
                hybrid_prompthmr_static_cam: true,
                hybrid_hands_source: 'v4', hybrid_face_source: 'smplest_x',
                hybrid_v4_hcd_iterations: 10, hybrid_v4_hcd_epochs: 30,
                hybrid_v4_mp_detection: 0.5, hybrid_v4_mp_tracking: 0.2,
                hybrid_v4_parts: { face: true, hands: true, mouth: true,
                                   eyes: false },
            },
            max: {
                hybrid_body_device: 'cuda', hybrid_gvhmr_static_cam: false,
                hybrid_gvhmr_focal_length_mm: 0,
                hybrid_prompthmr_static_cam: false,
                hybrid_hands_source: 'v4', hybrid_face_source: 'smplest_x',
                hybrid_v4_hcd_iterations: 30, hybrid_v4_hcd_epochs: 80,
                hybrid_v4_mp_detection: 0.7, hybrid_v4_mp_tracking: 0.5,
                hybrid_v4_parts: { face: true, hands: true, mouth: true,
                                   eyes: true },
            },
        },
    };

    /**
     * Eine Stufe anwenden.
     * @param {string} pipeline  Schluessel in WERTE
     * @param {string} stufe     'fast' | 'standard' | 'max'
     * @param {Function} danach  wird nach dem Setzen gerufen (Hybrid-Umschalter)
     */
    static anwenden(pipeline, stufe, danach = null) {
        const vorgabe = Pipelinevorgaben.WERTE[pipeline]?.[stufe];
        if (!vorgabe) return false;
        Pipelinevorgaben._knopfHervorheben(pipeline, stufe);
        for (const [name, wert] of Object.entries(vorgabe)) {
            if (name.endsWith('_parts')) Pipelinevorgaben._teile(name, wert);
            else Pipelinevorgaben._feld(name, wert);
        }
        if (danach) danach();
        return true;
    }

    static _feld(name, wert) {
        const feld = document.querySelector(`[name="${name}"]`);
        if (!feld) { Protokoll.debug('pipelinevorgaben', `kein Feld für "${name}"`); return; }
        if (feld.type === 'checkbox') feld.checked = wert;
        else feld.value = wert;
    }

    /** Ankreuzgruppe: Der Name im Formular ist der Schluessel selbst. */
    static _teile(name, werte) {
        document.querySelectorAll(`[name="${name}"]`).forEach(feld => {
            feld.checked = !!werte[feld.value];
        });
    }

    static _knopfHervorheben(pipeline, stufe) {
        const karte = document.getElementById('settings-' + pipeline);
        if (!karte) return;
        const gesucht = Pipelinevorgaben.BESCHRIFTUNG[stufe];
        karte.querySelectorAll('.preset-btn').forEach(knopf => {
            knopf.classList.toggle(
                'active', knopf.textContent.trim().toLowerCase() === gesucht);
        });
    }

    /** Aktuelle Werte der gewaehlten Pipeline (fuer den Start). */
    static werteLesen(pipeline) {
        return Pipelinefelder.sammeln(pipeline);
    }
}
