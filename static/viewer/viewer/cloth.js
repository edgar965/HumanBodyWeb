/**
 * Viewer — Cloth UI (template/builder/primitive cloth generation).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { bindSlider, sliderVal } from './utils.js';
import { ensureSkinned } from './skinning.js';
import { Stoffvorlagen } from './cloth/stoffvorlagen.js';
import { Stoffbauer } from './cloth/stoffbauer.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Hautnetz } from '../gemeinsam/hautnetz.js';
import { Stoffabruf } from '../gemeinsam/stoffabruf.js';

/**
 * Kleidungs-Bedienfeld aufbauen.
 *
 * Der Inhalt steckt in cloth/stoffvorlagen.js und cloth/stoffbauer.js — vorher
 * 245 Zeilen in dieser einen Funktion, mit vier Bereichen und verschachtelten
 * Hilfsfunktionen dazwischen.
 */
export async function loadClothUI() {
    try {
        const daten = await Serverabruf.json('/api/character/cloth/regions/');
        const dienste = {
            reglerBinden: bindSlider,
            reglerWert: sliderVal,
            stoffLaden: (key, params, farbe) => loadCloth(key, params, farbe),
            bereichEntfernen: removeClothRegion,
            stoffNetze: () => state.clothMeshes,
        };
        new Stoffvorlagen(daten, dienste).verdrahten();
        new Stoffbauer(daten, dienste).verdrahten();
        document.getElementById('cloth-remove-all')
            ?.addEventListener('click', () => removeAllCloth());
    } catch (fehler) {
        Protokoll.warnung('cloth', 'Kleidungs-Bedienfeld nicht verfuegbar:', fehler);
    }
}

export async function loadCloth(key, params, color) {
    const createBtns = document.querySelectorAll('#cloth-tpl-create, #cloth-bld-create, #cloth-prim-create');
    createBtns.forEach(b => b.disabled = true);

    ensureSkinned();

    try {
        const stoff = await Stoffabruf.netz(params, () => removeClothRegion(key));
        if (!stoff) return;
        const { daten: data, geometrie: geo } = stoff;

        const mat = Stoffabruf.material(
            Stoffabruf.farbe(data, { wunsch: color, farbfeld: 'cloth-color' }));

        const mesh = Hautnetz.bauen(geo, mat, state, data);

        state.clothMeshes[key] = mesh;
        state.clothParams[key] = { params, color: '#' + mesh.material.color.getHexString() };
        state.scene.add(mesh);

        Protokoll.debug('Viewer',
            `Cloth ${key}: ${data.vertex_count} verts, ${data.face_count} tris, skinned=${mesh.isSkinnedMesh || false}`);
        fn.updateEquippedList();
    } catch (e) {
        console.error('Failed to load cloth:', e);
    } finally {
        // `finally`, NICHT hinter dem try (Befund 30.08.2026): Der frueher
        // dort stehende Aufruf wurde bei `return` im Fehlerfall uebersprungen.
        // Antwortete der Server einmal mit `error`, blieben die drei
        // Erzeugen-Knoepfe bis zum Neuladen der Seite grau — ohne Meldung, ohne
        // erkennbaren Grund.
        createBtns.forEach(b => b.disabled = false);
    }
}

export function removeClothRegion(key) {
    if (!Netzentsorgung.ausAblage(state.scene, state.clothMeshes, key)) return;
    delete state.clothParams[key];
    fn.updateEquippedList();
}

export function removeAllCloth() {
    for (const key of Object.keys(state.clothMeshes)) {
        removeClothRegion(key);
    }
}

// Register
fn.loadClothUI = loadClothUI;
fn.loadCloth = loadCloth;
fn.removeClothRegion = removeClothRegion;
fn.removeAllCloth = removeAllCloth;
