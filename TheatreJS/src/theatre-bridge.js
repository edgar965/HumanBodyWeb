import { getProject, types } from '@theatre/core';

let _project = null;
let _sheet = null;

/**
 * Initialise Theatre project and main sheet.
 * @returns {{ project, sheet }}
 */
export function setupTheatre() {
    _project = getProject('HumanBody Theatre');
    _sheet = _project.sheet('Main');
    return { project: _project, sheet: _sheet };
}

/**
 * Get the current sheet (for registering objects after init).
 */
export function getSheet() {
    return _sheet;
}

/**
 * Register a Three.js camera as an animatable Theatre object.
 */
export function createCameraSheet(sheet, camera) {
    const obj = sheet.object('Camera', {
        position: types.compound({
            x: types.number(camera.position.x, { range: [-50, 50] }),
            y: types.number(camera.position.y, { range: [-10, 20] }),
            z: types.number(camera.position.z, { range: [-50, 50] }),
        }),
        fov: types.number(camera.fov, { range: [10, 120] }),
    });
    obj.onValuesChange((values) => {
        camera.position.set(values.position.x, values.position.y, values.position.z);
        camera.fov = values.fov;
        camera.updateProjectionMatrix();
    });
    return obj;
}

/**
 * Register a light as an animatable Theatre object.
 */
export function createLightSheet(sheet, name, light) {
    const props = {
        position: types.compound({
            x: types.number(light.position.x, { range: [-20, 20] }),
            y: types.number(light.position.y, { range: [0, 20] }),
            z: types.number(light.position.z, { range: [-20, 20] }),
        }),
        intensity: types.number(light.intensity, { range: [0, 5] }),
        color: types.rgba({
            r: light.color.r,
            g: light.color.g,
            b: light.color.b,
            a: 1,
        }),
    };
    const obj = sheet.object(name, props);
    obj.onValuesChange((values) => {
        light.position.set(values.position.x, values.position.y, values.position.z);
        light.intensity = values.intensity;
        light.color.setRGB(values.color.r, values.color.g, values.color.b);
    });
    return obj;
}

/**
 * Register a mesh/group as an animatable Theatre object.
 */
export function createMeshSheet(sheet, name, mesh) {
    const obj = sheet.object(name, {
        position: types.compound({
            x: types.number(mesh.position.x, { range: [-20, 20] }),
            y: types.number(mesh.position.y, { range: [-5, 10] }),
            z: types.number(mesh.position.z, { range: [-20, 20] }),
        }),
        rotation: types.compound({
            x: types.number(0, { range: [-180, 180] }),
            y: types.number(0, { range: [-180, 180] }),
            z: types.number(0, { range: [-180, 180] }),
        }),
        scale: types.number(1, { range: [0.01, 10] }),
    });
    obj.onValuesChange((values) => {
        mesh.position.set(values.position.x, values.position.y, values.position.z);
        mesh.rotation.set(
            values.rotation.x * Math.PI / 180,
            values.rotation.y * Math.PI / 180,
            values.rotation.z * Math.PI / 180
        );
        mesh.scale.setScalar(values.scale);
    });
    return obj;
}
