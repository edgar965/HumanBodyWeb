import { Testzustand } from './testzustand.js';
import { detectBVHFormat } from '../retarget_hybrid.js';
import { placeBvhSkeleton } from '../skeleton_test.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';

/**
 * Animationsbaum — die Kategorien der Vergleichsseite als aufklappbare Liste.
 *
 * Herausgelöst aus `animationsliste.js` (232 Zeilen). Zwei Dinge, die man
 * wissen muss:
 *
 * 1. **Die Zuordnung Format -> Skelettplatz steht nur hier** (`FORMAT_ZU_SKELETT`).
 *    Vorher gab es sie zweimal mit unterschiedlichem Inhalt: die Ruhelagen kannten
 *    `AIST` nicht, die Wiedergabe schon — ein AIST-Lauf legte also ein Skelett an,
 *    das beim Seitenaufbau leer geblieben war.
 * 2. **Die Ruhelagen laden die ERSTE Animation jeder Kategorie**, nur um das
 *    Skelett zu setzen. Ein Platz, der schon ein `bvhResult` hat, bleibt
 *    unberührt — sonst überschreibt der letzte Ladevorgang die Anzeige.
 */
export class Animationsbaum {

    /** BVH-Format -> Schlüssel in `Testzustand.skeletons`. */
    static FORMAT_ZU_SKELETT = {
        CMU: 'cmu', MIXAMO: 'mixamo', MOCAPNET: 'mocapnet',
        OPENPOSE: 'openpose', BANDAI: 'bandai', SMPL: 'smpl', AIST: 'smpl',
    };

    /** Platz, wenn das Format keinen eigenen hat. */
    static ERSATZPLATZ = 'mocapnet';

    /**
     * @param {HTMLElement} behaelter Ziel für die Liste (`#anim-tree`).
     * @param {Function} beimWaehlen (url, name, bilder, kategorie)
     */
    constructor(behaelter, beimWaehlen) {
        this.behaelter = behaelter;
        this.beimWaehlen = beimWaehlen;
    }

    /** Der Platz für ein Format — `null`, wenn es keinen eigenen gibt. */
    static platz(format) {
        return Animationsbaum.FORMAT_ZU_SKELETT[format] || null;
    }

    // ------------------------------------------------------------------ Liste

    async laden() {
        if (!this.behaelter) return;
        try {
            const daten = await Serverabruf.json('/api/character/animations/');
            Testzustand.allAnimations = daten.categories || {};
        } catch (fehler) {
            Protokoll.fehler('skelett_test', 'Animationen nicht ladbar', fehler);
            return;
        }
        this.zeichnen();
        this.ruhelagenLaden();
    }

    zeichnen() {
        const namen = Object.keys(Testzustand.allAnimations).sort();
        this.behaelter.innerHTML = '';
        if (namen.length === 0) {
            this.behaelter.innerHTML =
                '<div class="leer-hinweis-gross">Keine Animationen gefunden</div>';
            return;
        }
        for (const name of namen) {
            this.behaelter.appendChild(
                this._kategorie(name, Testzustand.allAnimations[name]));
        }
    }

    _kategorie(name, animationen) {
        const {kasten, koerper} = Kategoriekasten.bauen(
            name, animationen.length);
        for (const anim of animationen) {
            koerper.appendChild(this._zeile(name, anim));
        }
        return kasten;
    }

    _zeile(kategorie, anim) {
        const zeile = document.createElement('div');
        zeile.className = 'anim-item';
        zeile.dataset.url = anim.url;
        zeile.dataset.category = kategorie;
        zeile.innerHTML =
            `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
        zeile.addEventListener('click', () => {
            this.behaelter.querySelectorAll('.anim-item.active')
                .forEach(el => el.classList.remove('active'));
            zeile.classList.add('active');
            this.beimWaehlen(anim.url, anim.name, anim.frames, kategorie);
        });
        return zeile;
    }

    // --------------------------------------------------------------- Ruhelagen

    /** Je Kategorie die erste Datei laden und ihr Skelett in Ruhelage zeigen. */
    ruhelagenLaden() {
        const gesetzt = new Set();
        for (const kategorie of Object.keys(Testzustand.allAnimations).sort()) {
            const animationen = Testzustand.allAnimations[kategorie];
            if (!animationen || animationen.length === 0) continue;
            Testzustand.bvhLoader.load(animationen[0].url,
                                       ergebnis => this._ruhelage(ergebnis, gesetzt));
        }
    }

    _ruhelage(ergebnis, gesetzt) {
        const platz = Animationsbaum.platz(
            detectBVHFormat(ergebnis.skeleton.bones));
        if (!platz || gesetzt.has(platz)) return;
        if (Testzustand.skeletons[platz].bvhResult) return;
        gesetzt.add(platz);
        placeBvhSkeleton(ergebnis, platz);
        Testzustand.skeletons[platz].bvhResult = ergebnis;
    }
}
