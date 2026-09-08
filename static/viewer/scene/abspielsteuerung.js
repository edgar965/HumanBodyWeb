import { Figurmerker } from './figurmerker.js';

/**
 * Abspielsteuerung — Play, Stop, Zeitleiste und Tempo im Animation-Reiter,
 * dazu der Play-Knopf in der Kopfleiste (`play-demo-anim`).
 *
 * WARUM (06.09.2026, Edgar: „Animationen funktionieren nicht auf die
 * ausgewählte Person"): Beide Play-Knöpfe schalteten nur `state.currentAction`
 * um — die Aktion der Figur, die gerade lief. Wer HumanBody animierte, dann UMA
 * auswählte und Play drückte, hielt HumanBody an; UMA rührte sich nicht, und
 * nichts sagte warum. Dazu band `loadAnimationUI` die Knöpfe bei JEDEM Aufruf
 * neu (auch nach „Animation speichern"): zwei Zuhörer, zwei Umschaltungen,
 * kein sichtbarer Effekt — „der Button reagiert nicht".
 *
 * Jetzt gilt: Play meint die AUSGEWÄHLTE Figur.
 *  * Läuft ihre Animation, wird pausiert oder fortgesetzt.
 *  * Ist eine andere Figur animiert oder keine, holt Play die für diese Figur
 *    gemerkte Animation (`Figurmerker`) auf sie — ersatzweise die zuletzt in
 *    der Bibliothek angeklickte, ersatzweise `ersatz` (die Beispielanimation
 *    des Kopfleisten-Knopfs).
 *  * Ohne Figur schaltet Play die laufende Animation um, wie früher.
 *
 * `state` und `fn` kommen als Parameter — kein Import von `state.js`, damit
 * die Klasse in Node ohne Three.js prüfbar ist (`test_js_abspielsteuerung`).
 */
export class Abspielsteuerung {

    static PAUSE = '<i class="fas fa-pause"></i>';
    static PLAY = '<i class="fas fa-play"></i>';
    static LAEDT = '<i class="fas fa-spinner fa-spin"></i>';
    static KNOEPFE = ['anim-play', 'play-demo-anim'];

    constructor(state, fn) {
        this.state = state;
        this.fn = fn;
        this.verdrahtet = false;
    }

    // ------------------------------------------------------------------ Play

    /** Play im Sinn der ausgewählten Figur (siehe Klassendoku). `ersatz` = {url, name}. */
    abspielen(ersatz = null) {
        const { state } = this;
        const inst = state.selectedCharacterId
            ? state.characters.get(state.selectedCharacterId) : null;
        if (!inst) {
            if (state.currentAction) { this.umschalten(); return 'umgeschaltet'; }
            this.meldung('Keine Figur ausgewählt — erst eine Figur anklicken.');
            return 'keine-figur';
        }
        if (state.currentAction && state._animatedCharId === inst.id) {
            this.umschalten();
            return 'umgeschaltet';
        }
        const wahl = this.wahlFuer(inst.id) || ersatz;
        if (!wahl) {
            this.meldung('Keine Animation gewählt — eine aus der Bibliothek anklicken.');
            return 'keine-animation';
        }
        // Ab jetzt ist das die Animation DIESER Figur — wie nach einem Klick
        // in der Bibliothek: gemerkt und dort hervorgehoben.
        Figurmerker.animationMerken(inst.id, wahl);
        this.fn.animationMarkieren?.(wahl.name || null);
        state.currentAnimName = wahl.name || '';
        this.fn.loadBVHAnimation(wahl.url, wahl.name, 0);
        return 'geladen';
    }

    /** Die Animation, die Play auf dieser Figur starten soll — oder null. */
    wahlFuer(id) {
        const gemerkt = Figurmerker.animation(id);
        if (gemerkt && gemerkt.url) return gemerkt;
        if (this.state.currentAnimUrl) {
            return { url: this.state.currentAnimUrl, name: this.state.currentAnimName || '' };
        }
        const aktiv = document.querySelector('#anim-tree .anim-item.active');
        if (aktiv && aktiv.dataset.url) return { url: aktiv.dataset.url, name: aktiv.dataset.name || '' };
        return null;
    }

    /** Laufende Aktion anhalten oder fortsetzen. */
    umschalten() {
        const { state } = this;
        const laeuft = !!state.playing;
        if (!laeuft && !state.currentAction.isRunning()) state.currentAction.play();
        state.currentAction.paused = laeuft;
        state.playing = !laeuft;
        this.knoepfeAngleichen();
    }

    /** Beide Knöpfe zeigen denselben Stand: Pause, solange etwas läuft. */
    knoepfeAngleichen() {
        const laeuft = !!this.state.playing;
        for (const kennung of Abspielsteuerung.KNOEPFE) {
            const knopf = document.getElementById(kennung);
            if (!knopf) continue;
            knopf.innerHTML = laeuft ? Abspielsteuerung.PAUSE : Abspielsteuerung.PLAY;
            if (kennung === 'play-demo-anim') knopf.classList.toggle('active', laeuft);
        }
    }

    /**
     * Der Knopf zeigt, dass geladen wird.
     *
     * Edgar, 08.09.2026: „bei klicke auf eine Animation im Tab soll die
     * gleich anfangen zu animieren (und der Play button soll zum Pause
     * mutieren)". Das Abspielen und die Umschaltung auf Pause standen
     * schon — was fehlte, war die Zeit dazwischen: Ein Retarget kostet
     * gemessen 5,5 bis 7,0 s (`/api/retarget/` im Serverlog), und solange
     * blieb der Knopf unverändert auf Play. Wer klickt und nichts sieht,
     * klickt noch einmal.
     *
     * Der Spinner wird von `knoepfeAngleichen` überschrieben, sobald das
     * Laden fertig ist — der Aufruf steht am Ende von `loadBVHAnimation`,
     * auch im Fehlerfall.
     */
    ladeanzeige() {
        for (const kennung of Abspielsteuerung.KNOEPFE) {
            const knopf = document.getElementById(kennung);
            if (knopf) knopf.innerHTML = Abspielsteuerung.LAEDT;
        }
    }

    /**
     * Die Zeile unter der Leiste: was lädt, was läuft, was scheiterte. Ein
     * Retarget dauert bei 2.500 Bildern 9–13 s — ohne diese Zeile sah das wie
     * ein toter Knopf aus (Edgar, 05.09.2026).
     */
    meldung(text) {
        const feld = document.getElementById('anim-info');
        if (feld) feld.textContent = text;
    }

    // ------------------------------------------------------------ Verdrahten

    /** Einmal — ein zweiter Aufruf hängt keine zweiten Zuhörer an. */
    verdrahten() {
        if (this.verdrahtet) return false;
        this.verdrahtet = true;
        const { state, fn } = this;
        const knopf = (kennung) => document.getElementById(kennung);
        knopf('anim-play')?.addEventListener('click', () => this.abspielen());
        knopf('anim-stop')?.addEventListener('click', () => {
            fn.stopAnimation(false);
            state.currentAnimName = '';
        });
        const zeitleiste = knopf('anim-timeline');
        zeitleiste?.addEventListener('input', () => {
            const clip = state.currentAction?.getClip();
            if (!clip) return;
            state.currentAction.time = (parseInt(zeitleiste.value, 10) / 100) * clip.duration;
            if (state.mixer) state.mixer.update(0);
        });
        const tempo = knopf('anim-speed');
        const tempoText = knopf('speed-label');
        tempo?.addEventListener('input', () => {
            const faktor = parseInt(tempo.value, 10) / 100;
            if (tempoText) tempoText.textContent = `Speed: ${faktor.toFixed(1)}x`;
            if (state.mixer) state.mixer.timeScale = faktor;
        });
        const delta = knopf('scene-delta-norm');
        delta?.addEventListener('change', () => {
            state._sceneDeltaNorm = delta.value === 'auto' ? undefined : delta.value === '1';
            if (state.currentAnimUrl) {
                fn.loadBVHAnimation(state.currentAnimUrl, state.currentAnimName, 0,
                                    state.currentAnimBvhText || null);
            }
        });
        const boden = knopf('scene-ground-fix');
        boden?.addEventListener('change', () => { state.currentAnimGroundFixed = boden.checked; });
        knopf('anim-save-btn')?.addEventListener('click', () => {
            if (!state.currentAnimBvhText && !state.currentAnimUrl) { alert('Keine Animation geladen.'); return; }
            fn.openSaveAnimDialog();
        });
        return true;
    }
}
