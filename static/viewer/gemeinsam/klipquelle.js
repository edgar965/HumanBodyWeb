/**
 * Klipquelle — EIN umgezielter Clip für alle Ansichten der Ergebnisseite.
 *
 * Die 3D-Figur (`result_character/bvh_animation.js`) holt den Retarget vom
 * Server und meldet den fertigen Clip hier; das Skelettfenster des
 * BVH-Spielers (`bvh_player/humanbodyrig.js`) und die Videoüberlagerung
 * nehmen DENSELBEN Clip, statt ein zweites Mal zu laden.
 *
 * WARUM (12.09.2026, Edgar: „schon wieder unterschiedliche Rigs oben und
 * unten"): Vorher holte das Skelettfenster seinen eigenen Retarget — mit
 * der Höhe des nackten Skeletts (1,601 m) statt der des Netzes (1,678 m).
 * Zwei Abrufe, zwei Ablagen, zwei Maßstäbe, 3,5 s nebeneinander — und oben
 * ein anderes Rig als unten. Jetzt gibt es einen Abruf, und wer den Clip
 * braucht, wartet auf denselben.
 *
 * Modulzustand, bewusst: Die beiden Ansichten sind getrennte Modulgraphen
 * aus zwei `<script type="module">`-Blöcken. Sie treffen sich nur hier —
 * der Browser lädt ein Modul je Adresse genau einmal, beide erhalten also
 * dieselbe Klasse.
 */
export class Klipquelle {
    /** @type {import('three').AnimationClip|null} */
    static #klip = null;
    /** Wer auf den ersten Clip wartet: [{erfuellen, ablehnen}]. */
    static #warter = [];
    /** Wer jeden weiteren Clip sehen will (Modellwechsel, Fußkorrektur). */
    static #zuhoerer = [];

    /** Ist schon ein Clip gemeldet? */
    static get gemeldet() {
        return Klipquelle.#klip !== null;
    }

    /** Die Figur meldet ihren Clip — beim ersten Laden und bei jedem Neuladen. */
    static melden(klip) {
        Klipquelle.#klip = klip;
        const warter = Klipquelle.#warter;
        Klipquelle.#warter = [];
        for (const { erfuellen } of warter) erfuellen(klip);
        for (const tun of Klipquelle.#zuhoerer) tun(klip);
    }

    /** Der Abruf ist gescheitert — wer noch auf den ersten Clip wartet, erfährt es. */
    static scheitern(fehler) {
        const warter = Klipquelle.#warter;
        Klipquelle.#warter = [];
        for (const { ablehnen } of warter) ablehnen(fehler);
    }

    /** Versprechen auf den aktuellen Clip; ohne Clip wartet es auf `melden`. */
    static holen() {
        if (Klipquelle.#klip) return Promise.resolve(Klipquelle.#klip);
        return new Promise((erfuellen, ablehnen) => {
            Klipquelle.#warter.push({ erfuellen, ablehnen });
        });
    }

    /** Bei jedem weiteren Clip gerufen — nicht für den, der schon da ist. */
    static beiWechsel(tun) {
        Klipquelle.#zuhoerer.push(tun);
    }

    /** Für Prüfungen: alles vergessen. */
    static leeren() {
        Klipquelle.#klip = null;
        Klipquelle.#warter = [];
        Klipquelle.#zuhoerer = [];
    }
}
