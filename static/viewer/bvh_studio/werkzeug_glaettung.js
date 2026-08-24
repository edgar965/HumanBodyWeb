/**
 * Gauss-Glaettung der Bewegungsdaten (sitzungsweiter Schalter).
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026). Geglaettet werden
 * QUATERNIONEN, nicht Eulerwinkel — die springen bei jedem Umlauf.
 *
 * UMBAU 18.08.2026: 250 Zeilen, und der Filter stand ZWEIMAL darin. Jetzt:
 *
 *     gaussfilter.js        Kernel, Faltung, Quaternionen-Normierung (einmal)
 *     glaettungszustand.js  Schalter, Sigma, gesicherte Rohwerte
 *
 * Hier bleiben die vier Befehle: alles glätten, zurücknehmen, dauerhaft
 * speichern, einen ausgewählten Clip glätten.
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { applyFixedPositionAll, _fixedPos } from './werkzeug_position.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Gaussfilter } from './gaussfilter.js';
import { Glaettungszustand } from './glaettungszustand.js';

/**
 * EIN Zustand je Sitzung. Der Name bleibt `_gaussSmooth`, weil `tools.js`,
 * `vorschau.js` und `vorschau_fenster.js` ihn so importieren.
 */
export const _gaussSmooth = new Glaettungszustand();

/** Der alte Name des Filters — Aufrufer in `vorschau.js` und `fn.gaussFilter`. */
export function _gaussFilter(values, stride, sigma) {
    return Gaussfilter.glaetten(values, stride, sigma);
}

/** Anzeige im Werkzeugmenü: Sigma, Schalterfarben, Knopfbeschriftung. */
export function _updateGaussUI() {
    const sigmafeld = document.getElementById('dd-gauss-sigma-input');
    if (sigmafeld) sigmafeld.value = _gaussSmooth.sigma;
    // Klassen statt Inline-Farben (Befund `jsstilfassungen`): Ein Inline-Stil
    // schlägt jede Regel im Stylesheet, auch die des Themes.
    const an = document.getElementById('dd-gauss-on');
    const aus = document.getElementById('dd-gauss-off');
    an?.classList.toggle('gauss-gedaempft', _gaussSmooth.active);
    an?.classList.toggle('gauss-an', !_gaussSmooth.active);
    aus?.classList.toggle('gauss-aus', _gaussSmooth.active);
    aus?.classList.toggle('gauss-gedaempft', !_gaussSmooth.active);
    const knopf = document.getElementById('btn-tools');
    if (!knopf) return;
    const marke = _gaussSmooth.active
        ? `<span class="gauss-marke">●σ=${_gaussSmooth.sigma}</span> ` : '';
    knopf.innerHTML = `<i class="fas fa-wrench"></i> Tools ${marke}`
        + '<i class="fas fa-caret-down gauss-pfeil"></i>';
}

/** Alle Bewegungsclips glätten (Schalter EIN). */
export function applyGaussToAllClips() {
    const filter = new Gaussfilter(_gaussSmooth.sigma);
    const clips = Glaettungszustand.clips();
    let geglaettet = 0;
    for (const { spur, clip } of clips) {
        const sicherung = _gaussSmooth.sichern(clip);
        // Erst zurücksetzen, dann glätten — sonst faltet der zweite Lauf über
        // das Ergebnis des ersten (siehe Glaettungszustand).
        for (const bewegung of clip.animClip.tracks) {
            if (sicherung[bewegung.name]) {
                bewegung.values.set(sicherung[bewegung.name]);
            }
            filter.anwenden(bewegung.values, bewegung.getValueSize());
        }
        Glaettungszustand.mixerLoesen(spur, clip);
        geglaettet++;
    }
    for (const spur of state.project.tracks) {
        Glaettungszustand.spurZuruecksetzen(spur);
    }
    _nachziehen();
    fn.serverLog('gauss_smooth_on',
                 `sigma=${_gaussSmooth.sigma} clips=${geglaettet}/${clips.length}`);
    if (geglaettet === 0) {
        Protokoll.warnung('BVH Studio',
                          'Kein Clip geglättet — keine BVH-Spur mit Animation.');
    }
}

/** Rohwerte zurückschreiben (Schalter AUS). */
export function reloadAllClipAnimations() {
    for (const { spur, clip } of Glaettungszustand.clips()) {
        _gaussSmooth.zuruecksetzen(clip);
        Glaettungszustand.mixerLoesen(spur, clip);
        Glaettungszustand.spurZuruecksetzen(spur);
    }
    _gaussSmooth.vergessen();
    _nachziehen();
    fn.serverLog('gauss_smooth_off');
}

/**
 * Nach jeder Änderung an den Werten: feste Position neu anwenden und den
 * Abspielkopf auffrischen.
 *
 * Die feste Position arbeitet auf denselben Werten. Ohne das Leeren ihrer
 * Sicherung hält sie die Lage von VOR der Glättung fest.
 */
function _nachziehen() {
    if (_fixedPos.active) {
        _fixedPos.origData.clear();
        applyFixedPositionAll();
    }
    fn.applyPlayhead();
}

/** Die geglätteten Clips dauerhaft auf dem Server speichern. */
export async function saveSmoothedBVH() {
    if (!_gaussSmooth.active) {
        alert('Gaussian Smooth ist nicht aktiv.\nBitte erst EINSCHALTEN.');
        return;
    }
    const clips = _zuSpeichern();
    if (clips.length === 0) {
        alert('Keine Animation geladen.\nBitte erst eine Animation per '
              + 'Doppelklick zum Track hinzufügen\noder per A-Taste in der '
              + 'Vorschau öffnen.');
        return;
    }
    const sigma = _gaussSmooth.sigma;
    let gespeichert = 0;
    for (const clip of clips) {
        if (await _speichern(clip, sigma)) gespeichert++;
    }
    _gaussSmooth.vergessen();
    alert(`Smooth (σ=${sigma}) permanent gespeichert auf ${gespeichert} von `
          + `${clips.length} Clip(s).`);
    Protokoll.info('BVH Studio', `${gespeichert} geglaettete Clips gespeichert`);
}

/**
 * Die Clips, die gespeichert werden — aus der Zeitleiste oder aus der Vorschau.
 *
 * Der Rückfall auf die Vorschau ist wichtig: Wer eine Animation nur mit der
 * A-Taste ansieht, hat keinen Clip in der Zeitleiste und bekäme sonst „Keine
 * Animation geladen", obwohl eine vor ihm läuft.
 */
function _zuSpeichern() {
    const clips = Glaettungszustand.clips()
        .map(({ clip }) => clip)
        .filter(clip => clip.category && clip.name);
    if (clips.length > 0) return clips;
    const vorschau = fn.getPreviewInfo ? fn.getPreviewInfo() : null;
    if (vorschau?.category && vorschau?.name) {
        return [{ category: vorschau.category, name: vorschau.name }];
    }
    return [];
}

async function _speichern(clip, sigma) {
    try {
        const ergebnis = await Serverabruf.senden('/api/retarget/smooth-bvh/', {
            category: clip.category, name: clip.name, sigma,
        });
        if (!ergebnis.ok) {
            Protokoll.fehler('BVH Studio',
                             `Speichern fehlgeschlagen für ${clip.name}`,
                             ergebnis.error);
            return false;
        }
        fn.serverLog('gauss_saved', `${clip.category}/${clip.name} sigma=${sigma}`);
        return true;
    } catch (fehler) {
        Protokoll.fehler('BVH Studio',
                         `Speichern fehlgeschlagen für ${clip.name}`, fehler);
        return false;
    }
}

/** Nur den ausgewählten Clip glätten — mit Auswahl der Knochengruppe. */
export function smoothSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) {
        alert('Clip auswählen.');
        return;
    }
    pushUndo('Smooth');
    const clip = state.project.tracks[state.selectedTrackIdx]
        .clips[state.selectedClipIdx];
    if (!clip.animClip) {
        alert('Clip hat keine Animation.');
        return;
    }
    const sigma = _sigmaAusDemFeld(clip);
    if (sigma === null) return;
    const art = document.getElementById('tool-smooth-mode')?.value || 'all';
    const filter = new Gaussfilter(sigma);
    let geglaettet = 0;
    for (const bewegung of clip.animClip.tracks) {
        if (!_gemeint(bewegung.name, art)) continue;
        filter.anwenden(bewegung.values, bewegung.getValueSize());
        geglaettet++;
    }
    clip.smoothSigma = sigma;
    fn.updateProperties();
    Protokoll.info('BVH Studio',
                   `${clip.name} geglaettet: sigma=${sigma}, ${art}, `
                   + `${geglaettet} Spuren`);
}

function _sigmaAusDemFeld(clip) {
    const feld = document.getElementById('tool-smooth-sigma');
    const sigma = feld ? parseFloat(feld.value) || 2 : (clip.smoothSigma || 2);
    if (sigma <= 0) {
        alert('Sigma muss > 0 sein.');
        return null;
    }
    return sigma;
}

/** Knochen der Hände heißen so — daran hängt die Auswahl `body`/`hands`. */
const HANDKNOCHEN = ['hand', 'finger', 'thumb', 'palm'];

function _gemeint(spurname, art) {
    const name = spurname.toLowerCase();
    const istHand = HANDKNOCHEN.some(teil => name.includes(teil));
    if (art === 'body') return !istHand;
    if (art === 'hands') return istHand;
    return true;
}
