/**
 * Theatre.js Scene Presets
 * Vordefinierte Einstellungen für Lichter, Kameras, Szenen
 */

import { getTheatreObject } from './theatre-bridge.js';

export const PRESETS = {
    // ────────────────────────────────────────────────────────────
    // 1. Ballet Stage (Default) — Warm theatrical lighting
    // ────────────────────────────────────────────────────────────
    ballet_stage: {
        name: 'Ballet Stage',
        description: 'Warme Spotlights, theatralisch dunkel',
        camera: {
            position: { x: 0, y: 1.6, z: 5 },
            fov: 35
        },
        lights: {
            spotLeft: {
                intensity: 8,
                color: { r: 1, g: 0.933, b: 0.867 }, // Warm white
                position: { x: -3, y: 6, z: 3 }
            },
            spotRight: {
                intensity: 8,
                color: { r: 1, g: 0.933, b: 0.867 },
                position: { x: 3, y: 6, z: 3 }
            },
            backLight: {
                intensity: 6,
                color: { r: 0.4, g: 0.267, b: 0.667 }, // Blue-violet
                position: { x: 0, y: 5, z: -4 }
            }
        }
    },

    // ────────────────────────────────────────────────────────────
    // 2. Studio Bright — Helle, neutrale Beleuchtung
    // ────────────────────────────────────────────────────────────
    studio_bright: {
        name: 'Studio Bright',
        description: 'Helle, gleichmäßige Beleuchtung für Details',
        camera: {
            position: { x: 0, y: 1.6, z: 4 },
            fov: 40
        },
        lights: {
            spotLeft: {
                intensity: 12,
                color: { r: 1, g: 1, b: 1 }, // Pure white
                position: { x: -2, y: 5, z: 4 }
            },
            spotRight: {
                intensity: 12,
                color: { r: 1, g: 1, b: 1 },
                position: { x: 2, y: 5, z: 4 }
            },
            backLight: {
                intensity: 3,
                color: { r: 0.9, g: 0.95, b: 1 }, // Soft white
                position: { x: 0, y: 4, z: -3 }
            }
        }
    },

    // ────────────────────────────────────────────────────────────
    // 3. Cinematic Moody — Film noir, dramatisch
    // ────────────────────────────────────────────────────────────
    cinematic_moody: {
        name: 'Cinematic Moody',
        description: 'Dramatisches Film-noir-Licht, starke Schatten',
        camera: {
            position: { x: 2, y: 1.4, z: 4 },
            fov: 28 // Telephoto look
        },
        lights: {
            spotLeft: {
                intensity: 15,
                color: { r: 1, g: 0.8, b: 0.6 }, // Warm amber
                position: { x: -4, y: 7, z: 2 }
            },
            spotRight: {
                intensity: 2,
                color: { r: 0.6, g: 0.7, b: 0.9 }, // Cool fill
                position: { x: 4, y: 3, z: 3 }
            },
            backLight: {
                intensity: 10,
                color: { r: 0.3, g: 0.5, b: 1 }, // Strong blue rim
                position: { x: 1, y: 6, z: -5 }
            }
        }
    },

    // ────────────────────────────────────────────────────────────
    // 4. Fashion Show — Runway-Style
    // ────────────────────────────────────────────────────────────
    fashion_show: {
        name: 'Fashion Show',
        description: 'Laufsteg-Beleuchtung, kühles Weiß von oben',
        camera: {
            position: { x: 0, y: 1.2, z: 6 },
            fov: 50 // Wide for full-body
        },
        lights: {
            spotLeft: {
                intensity: 10,
                color: { r: 0.95, g: 0.97, b: 1 }, // Cool white
                position: { x: -2, y: 8, z: 2 }
            },
            spotRight: {
                intensity: 10,
                color: { r: 0.95, g: 0.97, b: 1 },
                position: { x: 2, y: 8, z: 2 }
            },
            backLight: {
                intensity: 5,
                color: { r: 1, g: 1, b: 1 },
                position: { x: 0, y: 3, z: -2 }
            }
        }
    },

    // ────────────────────────────────────────────────────────────
    // 5. Sunset Warm — Goldene Stunde
    // ────────────────────────────────────────────────────────────
    sunset_warm: {
        name: 'Sunset Warm',
        description: 'Goldene Stunde, warmes Orange-Gold',
        camera: {
            position: { x: -1, y: 1.5, z: 4.5 },
            fov: 42
        },
        lights: {
            spotLeft: {
                intensity: 14,
                color: { r: 1, g: 0.7, b: 0.4 }, // Orange-gold
                position: { x: -5, y: 4, z: 3 }
            },
            spotRight: {
                intensity: 6,
                color: { r: 1, g: 0.85, b: 0.7 }, // Soft peach
                position: { x: 3, y: 5, z: 2 }
            },
            backLight: {
                intensity: 8,
                color: { r: 0.8, g: 0.4, b: 0.6 }, // Purple-pink
                position: { x: 2, y: 5, z: -4 }
            }
        }
    }
};

/**
 * Apply a preset to the scene (lights + camera).
 * @param {Object} preset Preset object from PRESETS
 * @param {THREE.Camera} camera Three.js camera
 * @param {Object} lights { spotLeft, spotRight, backLight }
 * @param {OrbitControls} controls OrbitControls instance
 */
export function applyPreset(preset, camera, lights, controls) {
    console.log(`[Preset] Applying: ${preset.name}`);

    // Get Theatre objects
    const cameraObj = getTheatreObject('Camera');
    const spotLeftObj = getTheatreObject('Spot Left');
    const spotRightObj = getTheatreObject('Spot Right');
    const backLightObj = getTheatreObject('Back Light');

    // Apply via Theatre API (this ensures Theatre UI updates)
    if (cameraObj) {
        cameraObj.props.position.x = preset.camera.position.x;
        cameraObj.props.position.y = preset.camera.position.y;
        cameraObj.props.position.z = preset.camera.position.z;
        cameraObj.props.fov = preset.camera.fov;
    }

    // Reset orbit controls target
    if (controls) {
        controls.target.set(0, 0.9, 0);
        controls.update();
    }

    // Apply light settings via Theatre
    applyLightViaTheatre(spotLeftObj, preset.lights.spotLeft);
    applyLightViaTheatre(spotRightObj, preset.lights.spotRight);
    applyLightViaTheatre(backLightObj, preset.lights.backLight);

    console.log(`✓ Preset "${preset.name}" applied via Theatre API`);
}

function applyLightViaTheatre(theatreObj, settings) {
    if (!theatreObj) return;
    theatreObj.props.intensity = settings.intensity;
    theatreObj.props.color.r = settings.color.r;
    theatreObj.props.color.g = settings.color.g;
    theatreObj.props.color.b = settings.color.b;
    theatreObj.props.position.x = settings.position.x;
    theatreObj.props.position.y = settings.position.y;
    theatreObj.props.position.z = settings.position.z;
}
