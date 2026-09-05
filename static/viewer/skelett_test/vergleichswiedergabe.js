import * as THREE from 'three';
import { Testzustand } from './testzustand.js';
import { removeBoneViz } from './knochenbild.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl }
    from '../retarget_hybrid.js';
import { placeBvhSkeleton } from '../skeleton_test.js';
import { Animationsbaum } from './animationsbaum.js';
import { Mischerbund } from './mischerbund.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Vergleichswiedergabe — dieselbe BVH-Datei auf Original- und DEF-Skelett.
 *
 * Herausgelöst aus `animationsliste.js` (232 Zeilen). Der Ablauf hat eine
 * Reihenfolge, die nicht beliebig ist:
 *
 * 1. **Erst das alte Skelett abräumen** (Hülle, Knochenbild, Beschriftungen),
 *    dann das neue setzen. Wer nur `placeBvhSkeleton` aufruft, bekommt zwei
 *    Skelette übereinander und Beschriftungen, die niemand mehr entfernt.
 * 2. **Die Zielskelette müssen vor dem Retarget in die Ruhelage** (`skeleton.pose()`).
 *    Sonst rechnet der Retarget-Lauf auf einer schon verdrehten Ausgangslage.
 * 3. **Ein Retarget-Fehler darf die BVH-Wiedergabe nicht mitnehmen** — deshalb der
 *    eigene Fänger: Das Original läuft dann allein, statt dass die Seite steht.
 *
 * Seit 05.09.2026 gibt es ZWEI Ziele: DEF und die UMA-Figur aus dem Figurkatalog
 * (`ZIELE`). Beide werden mit derselben BVH angefragt und laufen nebeneinander —
 * so sieht man, ob die Bewegungsbibliothek auf UMA genauso ankommt wie auf DEF.
 */
export class Vergleichswiedergabe {

    /** Die Zielskelette: Platz und Server-Kennung (`target=`); DEF ist die Vorgabe. */
    static ZIELE = [['def', null], ['uma', 'uma']];

    /** Der Platz für ein Format; ohne eigenen Platz der Ersatzplatz. */
    static platz(format) {
        return Animationsbaum.platz(format) || Animationsbaum.ERSATZPLATZ;
    }

    /** Eine Animation laden und auf allen Skeletten starten. */
    static laden(url, name, bilder, kategorie) {
        Vergleichswiedergabe.anhalten();
        Vergleichswiedergabe._melden(`Lade ${name}...`);
        Testzustand.bvhLoader.load(
            url,
            ergebnis => Vergleichswiedergabe._starten(ergebnis, url, name, bilder),
            undefined,
            fehler => {
                Protokoll.fehler('skelett_test', `BVH nicht ladbar: ${name}`, fehler);
                Vergleichswiedergabe._melden(`Fehler: ${name}`);
            });
    }

    static async _starten(ergebnis, url, name, bilder) {
        const knochen = ergebnis.skeleton.bones;
        if (knochen.length === 0) return;
        const format = detectBVHFormat(knochen);
        Testzustand.currentBvhResult = ergebnis;
        Testzustand.currentFormat = format;

        const mischer = [Vergleichswiedergabe._bvhMischer(ergebnis, format)];
        // Beide Ziele gleichzeitig anfragen — jedes ist ein eigener Serverlauf.
        const ziele = await Promise.all(Vergleichswiedergabe.ZIELE.map(
            ([platz, ziel]) => Vergleichswiedergabe._zielMischer(url, platz, ziel)));
        mischer.push(...ziele.filter(Boolean));

        Testzustand.mixer = new Mischerbund(mischer);
        Testzustand.currentAction = { clip: ergebnis.clip, paused: false };
        Testzustand.playing = true;
        Vergleichswiedergabe._knopf('<i class="fas fa-pause"></i>');
        Vergleichswiedergabe._melden(
            `${name} — ${bilder}f — ${ergebnis.clip.duration.toFixed(1)}s — ${format}`);
    }

    /** Das Original-Skelett neu setzen und die Bewegung darauf starten. */
    static _bvhMischer(ergebnis, format) {
        const platz = Vergleichswiedergabe.platz(format);
        Vergleichswiedergabe._abraeumen(platz);
        placeBvhSkeleton(ergebnis, platz);
        const mischer = new THREE.AnimationMixer(Testzustand.skeletons[platz].rootBone);
        mischer.clipAction(ergebnis.clip).play();
        return mischer;
    }

    /** Hülle, Knochenbild und Beschriftungen eines Platzes entfernen. */
    static _abraeumen(platz) {
        const eintrag = Testzustand.skeletons[platz];
        if (eintrag.wrapper) {
            eintrag.group.remove(eintrag.wrapper);
            eintrag.wrapper = null;
        }
        removeBoneViz(platz);
        eintrag.labels.forEach(schild => schild.parent && schild.parent.remove(schild));
        eintrag.labels = [];
    }

    /** Die retargetierte Fassung auf einem Zielskelett (DEF, UMA) — `null`, wenn es fehlt. */
    static async _zielMischer(url, platz, ziel) {
        const eintrag = Testzustand.skeletons[platz];
        if (!eintrag.skeleton) return null;      // Skelett (noch) nicht geladen
        try {
            eintrag.skeleton.skeleton.pose();      // Ruhelage vor dem Retarget
            const clip = await fetchRetargetedClipFromUrl(
                url, eintrag.skeleton, ziel ? { target: ziel } : {});
            const mischer = new THREE.AnimationMixer(eintrag.rootBone);
            mischer.clipAction(clip).play();
            return mischer;
        } catch (fehler) {
            Protokoll.fehler('skelett_test',
                             `${platz.toUpperCase()}-Retarget fehlgeschlagen`, fehler);
            return null;
        }
    }

    // ------------------------------------------------------------------ Stoppen

    static anhalten() {
        if (Testzustand.mixer) {
            Testzustand.mixer.stopAllAction();
            Testzustand.mixer = null;
        }
        Testzustand.currentAction = null;
        Testzustand.currentBvhResult = null;
        // Die Zielskelette zurück in die Ruhelage: Sie behielten sonst die
        // letzte Haltung der abgebrochenen Bewegung.
        for (const [platz] of Vergleichswiedergabe.ZIELE) {
            const eintrag = Testzustand.skeletons[platz];
            if (eintrag.skeleton) eintrag.skeleton.skeleton.pose();
        }
        Testzustand.playing = false;
    }

    // ----------------------------------------------------------------- Bedienung

    static bedienungBinden() {
        const abspielen = document.getElementById('anim-play');
        const stoppen = document.getElementById('anim-stop');
        const leiste = document.getElementById('anim-timeline');
        abspielen?.addEventListener('click', () => {
            if (!Testzustand.currentAction) return;
            Testzustand.playing = !Testzustand.playing;
            Testzustand.currentAction.paused = !Testzustand.playing;
            Vergleichswiedergabe._knopf(Testzustand.playing
                ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>');
        });
        stoppen?.addEventListener('click', () => {
            Vergleichswiedergabe.anhalten();
            Vergleichswiedergabe._knopf('<i class="fas fa-play"></i>');
            if (leiste) leiste.value = 0;
            Vergleichswiedergabe._melden('—');
            document.querySelectorAll('.anim-item.active')
                .forEach(el => el.classList.remove('active'));
        });
        leiste?.addEventListener('input', () => {
            if (!Testzustand.currentAction || !Testzustand.mixer) return;
            const dauer = Testzustand.currentAction.clip.duration;
            Testzustand.mixer.setTime((parseInt(leiste.value) / 100) * dauer);
        });
    }

    static _knopf(inhalt) {
        const knopf = document.getElementById('anim-play');
        if (knopf) knopf.innerHTML = inhalt;
    }

    static _melden(text) {
        const feld = document.getElementById('anim-info');
        if (feld) feld.textContent = text;
    }
}
