/**
 * Blendermodellleertaste — die Leertaste ist Abspielen / Pause der Animationsleiste (Edgar, 30.09.2026: „mach bei der
 * Animations-Play-Seite den Shortcut Leertaste für Play / Pause").
 *
 * Sie ruft dasselbe wie der Knopf `#anim-play` (`Blendermodellanimation.umschalten`): Ist der Blender-Film über der Bühne
 * zu sehen, steuert das den Film, sonst die Bewegung auf der Figur. Nicht abgefangen wird sie in Eingabefeldern, im
 * Video selbst (dessen eigene Steuerung reagiert auf die Leertaste), bei offenem Bildfenster, im Reiter „Iterationen"
 * und wenn es nichts abzuspielen gibt — dann behält die Leertaste ihre Aufgabe (Seite blättern, Knopf drücken).
 */
export class Blendermodellleertaste {

    static AUSGENOMMEN = 'input:not([type="range"]), select, textarea, video, [contenteditable="true"]';

    constructor(seite) {
        this.seite = seite;
        this._gefangen = false;
        document.addEventListener('keydown', ereignis => this._unten(ereignis), true);
        document.addEventListener('keyup', ereignis => this._oben(ereignis), true);
    }

    _gilt(ereignis) {
        if (ereignis.code !== 'Space' || ereignis.ctrlKey || ereignis.metaKey || ereignis.altKey || ereignis.shiftKey) return false;
        if (document.querySelector('dialog[open]')) return false;
        if (document.getElementById('reiter-auftrag').hidden) return false;
        if (ereignis.target.closest?.(Blendermodellleertaste.AUSGENOMMEN)) return false;
        const animation = this.seite.animation;
        return this.seite.blenderfilm.sichtbar() || (!animation.karte.hidden && !!animation.action);
    }

    _unten(ereignis) {
        if (!this._gilt(ereignis)) return;
        // Auch ein fokussierter Knopf soll nicht „gedrückt" werden: Die Leertaste gehört hier dem Abspielen.
        ereignis.preventDefault();
        ereignis.stopPropagation();
        this._gefangen = true;
        if (!ereignis.repeat) this.seite.animation.umschalten();
    }

    _oben(ereignis) {
        if (ereignis.code !== 'Space' || !this._gefangen) return;
        this._gefangen = false;
        ereignis.preventDefault();
        ereignis.stopPropagation();
    }
}
