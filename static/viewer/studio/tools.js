/**
 * BVH Studio — Anmeldung der Werkzeugleiste und der Werkzeuge.
 *
 * Die Leiste steckt in `Werkzeugleiste` (werkzeugleiste.js), die Hilfe in
 * `Hilfefenster`. Vorher standen hier 155 Zeilen in `setupToolbar()`.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { _gaussSmooth, _gaussFilter, applyGaussToAllClips,
         reloadAllClipAnimations, smoothSelectedClip } from './werkzeug_glaettung.js';
import { _fixedPos, applyFixedPositionAll,
         restoreFixedPositionAll } from './werkzeug_position.js';
import { groundFixSelectedClip } from './werkzeug_boden.js';
import { Werkzeugleiste } from './werkzeugleiste.js';
import { Hilfefenster } from './hilfefenster.js';

let leiste = null;

export function setupToolbar() {
    if (!leiste) leiste = new Werkzeugleiste();
    return leiste.aufbauen();
}

export function showHelp(thema) {
    return Hilfefenster.zeigen(thema);
}

fn.smoothSelectedClip = smoothSelectedClip;
fn.groundFixSelectedClip = groundFixSelectedClip;
fn.getGaussSmooth = () => _gaussSmooth;
fn.gaussFilter = _gaussFilter;
fn.getFixedPos = () => _fixedPos;
fn.applyFixedPositionAll = applyFixedPositionAll;
