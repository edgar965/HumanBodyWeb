/**
 * Keyframefeld — das Bedienfeld des Reiters „Keyframes".
 *
 * Herausgelöst aus `keyframe-ui.js` (319 Zeilen). Dort stand das Markup mit
 * rund 20 Inline-Stilen in einer Zeichenkette (Befund `jsstilfassungen`); die
 * Regeln heißen jetzt `.kf-*` und stehen in `templates/theatre.html`.
 *
 * Diese Klasse baut nur auf und liefert die Elemente zurück — wer sie
 * verdrahtet, entscheidet `KeyframeUI`.
 */
export class Keyframefeld {

    static REITER = 'tab-keyframes';
    static VORGABE_DAUER = 10;

    constructor(objektnamen) {
        this.objektnamen = objektnamen;
    }

    /** Aufbauen; liefert `false`, wenn es den Reiter nicht gibt. */
    aufbauen() {
        const reiter = document.getElementById(Keyframefeld.REITER);
        if (!reiter) return false;
        reiter.innerHTML = this._markup();
        return true;
    }

    _markup() {
        const wahl = this.objektnamen
            .map(name => `<option value="${name}">${name}</option>`).join('');
        return `
            <div class="keyframe-panel">
                <div class="kf-controls">
                    <h3 class="kf-titel">Animation Timeline</h3>
                    <div class="kf-knopfreihe">
                        <button id="kf-play" class="btn-secondary kf-dehnen">
                            <i class="fas fa-play"></i> Play
                        </button>
                        <button id="kf-stop" class="btn-secondary kf-dehnen">
                            <i class="fas fa-stop"></i> Stop
                        </button>
                    </div>
                    <div class="kf-feld">
                        <label class="kf-beschriftung">Duration (seconds)</label>
                        <input type="number" id="kf-duration" class="kf-eingabe"
                               value="${Keyframefeld.VORGABE_DAUER}" min="1" max="300">
                    </div>
                    <div class="kf-feld">
                        <label class="kf-beschriftung">Current Time:
                            <span id="kf-time-display">0.00s</span></label>
                        <input type="range" id="kf-timeline" class="kf-regler"
                               min="0" max="${Keyframefeld.VORGABE_DAUER}"
                               step="0.1" value="0">
                    </div>
                    <div class="kf-abschnitt">
                        <label class="kf-beschriftung kf-block">Add Keyframe</label>
                        <select id="kf-object-select" class="kf-eingabe">${wahl}</select>
                        <button id="kf-add" class="btn-primary kf-voll">
                            <i class="fas fa-plus"></i> Add Keyframe at Current Time
                        </button>
                    </div>
                </div>
                <div class="kf-list">
                    <h4 class="kf-untertitel">Keyframes</h4>
                    <div id="kf-keyframes" class="kf-liste">
                        <div class="kf-leer">
                            No keyframes yet. Add one to start animating!
                        </div>
                    </div>
                </div>
                <div class="kf-fussreihe">
                    <button id="kf-export" class="btn-secondary dehnen-klein">
                        <i class="fas fa-download"></i> Export
                    </button>
                    <button id="kf-import" class="btn-secondary dehnen-klein">
                        <i class="fas fa-upload"></i> Import
                    </button>
                    <button id="kf-clear" class="btn-secondary dehnen-klein">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                </div>
            </div>
        `;
    }
}
