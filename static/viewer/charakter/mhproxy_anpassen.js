/**
 * MakeHuman-Proxy an den Koerper anpassen.
 *
 * Aus mh_proxy.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 18.08.2026: 247 Zeilen. Das Netz-Bauen (Anfrage, Einheiten, Achsen,
 * Material, Textur) steht jetzt in `mhproxynetz.Mhproxynetz`; hier bleibt die
 * Bedienung — Werte aus den Reglern, Doppelläufe verhindern, die Spiegelung
 * zwischen Assets- und Eigenschaften-Reiter.
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _bindSlider, _selectedInst, _selectedMHMesh, _sliderVal } from './utils.js';
import { Materialregler } from './materialregler.js';
import { Mhverformung } from './mhproxy_verformung.js';
import { Mhproxynetz } from './mhproxynetz.js';

/**
 * EINE Anpassung zur Zeit (Review 15.08.2026).
 *
 * Der Serverteil des Proxy-Fits braucht gemessene 1,14 s (13.08.2026), und es
 * gibt ZWEI Auslöser: den Knopf und den entprellten Refit beim Schieben eines
 * Reglers (400 ms). Wer einen Regler bewegt und dann auf „Anpassen" klickt, hat
 * zwei Anfragen gleichzeitig unterwegs — und beide entfernen dasselbe Netz aus
 * `inst.clothMeshes`, geben Geometrie und Material frei und schreiben ihr
 * Ergebnis zurück. Der langsamere gewinnt, egal welche Werte er hatte.
 *
 * Statt zu sperren und den Klick zu verlieren, wird der letzte Wunsch gemerkt
 * und nach dem laufenden Fit EINMAL nachgezogen: Beim Schieben eines Reglers ist
 * „der letzte Stand gewinnt" die richtige Antwort.
 */
let _mhFitLaeuft = false;
let _mhFitNachziehen = false;

async function _doMHProxyFit() {
    if (_mhFitLaeuft) { _mhFitNachziehen = true; return; }
    _mhFitLaeuft = true;
    try {
        await _mhProxyFitAusfuehren();
    } finally {
        _mhFitLaeuft = false;
    }
    if (_mhFitNachziehen) {
        _mhFitNachziehen = false;
        await _doMHProxyFit();
    }
}

/** Die Reglerwerte des Assets-Reiters. */
function _reglerwerte() {
    return {
        color: document.getElementById('mh-color')?.value || '#4d5980',
        offset: _sliderVal('mh-offset'),
        stiffness: _sliderVal('mh-stiffness'),
        scale: _sliderVal('mh-scale'),
        y_offset: _sliderVal('mh-y-offset'),
        push_dist: _sliderVal('mh-push-dist') || 3,
        roughness: _sliderVal('mh-roughness'),
        metalness: _sliderVal('mh-metalness'),
        opacity: _sliderVal('mh-opacity'),
    };
}

async function _mhProxyFitAusfuehren() {
    // Die Kennung EINMAL lesen und festhalten. Der Fit dauert gemessene 1,14 s;
    // wer in dieser Zeit ein anderes Stück in der Liste anklickt, ändert
    // `state._selectedMHId`. Wurde sie danach ein zweites Mal gelesen, schrieb
    // der Fit die Farbe des ALTEN Stücks in die Felder des neuen.
    // (Befund aus dem Sparring mit Nemotron, 18.08.2026.)
    const kennung = state._selectedMHId;
    if (!kennung) return;
    const inst = _selectedInst();
    if (!inst) return;
    await _fitMHProxyOnInst(inst, kennung, _reglerwerte());
    _farbeSpiegeln(inst, kennung);
    fn.updateEquippedList?.(inst);
    fn.updateVertexCount?.();
}

/**
 * Die Farbe des angepassten Stücks in beide Farbfelder.
 *
 * Sie kann vom Server kommen (Material der Vorlage oder Textur) — dann müssen
 * beide Felder sie zeigen, sonst schreibt der nächste Fit die alte zurück.
 *
 * NUR, wenn die Auswahl noch dieselbe ist: Die Felder gehören immer dem
 * AKTUELL gewählten Stück. Wer während der 1,14 s ein anderes anklickt, bekäme
 * sonst die Farbe des vorigen ins Feld geschrieben — und beim nächsten Fit auf
 * sein neues Stück.
 */
function _farbeSpiegeln(inst, kennung) {
    if (state._selectedMHId !== kennung) return;
    const gemerkt = inst.mhProxies?.[kennung];
    if (!gemerkt) return;
    for (const feldname of ['mh-color', 'prop-mh-color']) {
        const feld = document.getElementById(feldname);
        if (feld) feld.value = gemerkt.color;
    }
}

async function _fitMHProxyOnInst(inst, garmentId, p) {
    return new Mhproxynetz(inst, garmentId, p).anpassen();
}

/** Die Materialregler im Eigenschaften-Reiter auf das gewählte Netz stellen. */
function _syncPropMHControls() {
    const wahl = _selectedMHMesh();
    if (!wahl) return;
    const werkstoff = wahl.mesh.material;
    const prozent = wert => (wert / 100).toFixed(2);
    for (const [feld, wert] of [['roughness', werkstoff.roughness],
                                ['metalness', werkstoff.metalness],
                                ['opacity', werkstoff.opacity]]) {
        _setzen(`prop-mh-${feld}`, Math.round(wert * 100), prozent);
    }
    const farbe = document.getElementById('prop-mh-color');
    if (farbe) farbe.value = '#' + werkstoff.color.getHexString();
    _spiegelnVomAssetsReiter();
    _anzeigenBinden();
}

/** Wert und Anzeige eines Reglers setzen (`<id>` und `<id>-val`). */
function _setzen(kennung, wert, formatieren) {
    const regler = document.getElementById(kennung);
    if (regler) regler.value = wert;
    const anzeige = document.getElementById(`${kennung}-val`);
    if (anzeige) anzeige.textContent = formatieren(wert);
}

/** Die vier Anpassregler: Assets-Reiter -> Eigenschaften-Reiter. */
const SPIEGEL = [['prop-mh-stiffness', 'mh-stiffness'],
                 ['prop-mh-offset', 'mh-offset'],
                 ['prop-mh-scale', 'mh-scale'],
                 ['prop-mh-y-offset', 'mh-y-offset']];

function _spiegelnVomAssetsReiter() {
    for (const [hier, dort] of SPIEGEL) {
        const quelle = document.getElementById(dort);
        const ziel = document.getElementById(hier);
        if (quelle && ziel) ziel.value = quelle.value;
    }
}

/** Anzeigeformate der Regler im Eigenschaften-Reiter. */
const ANZEIGEN = [
    ['prop-mh-stiffness', wert => (wert / 100).toFixed(2)],
    ['prop-mh-offset', wert => (wert / 1000).toFixed(3)],
    ['prop-mh-scale', wert => wert + '%'],
    ['prop-mh-y-offset', wert => wert + ' mm'],
    ['prop-mh-roughness', wert => (wert / 100).toFixed(2)],
    ['prop-mh-metalness', wert => (wert / 100).toFixed(2)],
    ['prop-mh-opacity', wert => (wert / 100).toFixed(2)],
];

function _anzeigenBinden() {
    for (const [kennung, formatieren] of ANZEIGEN) {
        _bindSlider(kennung, `${kennung}-val`, formatieren);
    }
}

/**
 * Bedienung im Eigenschaften-Reiter. Sie zeigt dieselben Werte wie der
 * Assets-Reiter, nur unter `prop-`-Kennungen — deshalb kommen Material und
 * Verformung aus denselben Klassen (`Materialregler`, `Mhverformung`). Vorher
 * standen hier 106 Zeilen, davon 60 als Zeile-fuer-Zeile-Kopie des
 * Herausdrueckens aus dem Assets-Reiter.
 */
function _initPropMHControls() {
    new Materialregler('prop-mh', _selectedMHMesh).grundwerte().deckkraft();
    // Die vier Anpassregler spiegeln auf den Assets-Reiter: dort haengt die
    // Neuanpassung am Server. Waehrend des Ziehens nur den Wert nachziehen,
    // beim Loslassen das `change`-Ereignis weitergeben.
    for (const [hier, dort] of SPIEGEL) {
        const regler = document.getElementById(hier);
        if (!regler) continue;
        const spiegeln = (weiter) => {
            const ziel = document.getElementById(dort);
            if (!ziel) return;
            ziel.value = regler.value;
            if (weiter) ziel.dispatchEvent(new Event('change'));
        };
        regler.addEventListener('input', () => spiegeln(false));
        regler.addEventListener('change', () => spiegeln(true));
    }
    _bindSlider('prop-mh-push-dist', 'prop-mh-push-dist-val', wert => wert + ' mm');
    const verformung = new Mhverformung('prop-mh');
    document.getElementById('prop-mh-push')
        ?.addEventListener('click', () => verformung.herausdruecken());
    document.getElementById('prop-mh-push-undo')
        ?.addEventListener('click', () => verformung.zuruecknehmen());
}

export { _doMHProxyFit, _fitMHProxyOnInst, _syncPropMHControls, _initPropMHControls };
