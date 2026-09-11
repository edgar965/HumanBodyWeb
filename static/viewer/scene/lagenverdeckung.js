/**
 * Lagenverdeckung — Stoff unter einem anderen Stück wird nicht gezeichnet.
 *
 * Die Entscheidung steht in `gemeinsam/lagenmaske.js` (ohne Three.js, dort
 * der Befund: Bund der Leggings durch das T-Shirt, 11.09.2026). Hier die
 * Three.js-Seite, gebaut wie `hautverdeckung.js`: der volle Index jedes
 * Stücks bleibt in `geometry.userData.indexVoll`, gezeichnet wird ein Index
 * ohne die verdeckten Dreiecke, die verdeckten Ecken der Randdreiecke ziehen
 * sich im Shader zurück (`Hauteinzug`, hier entlang der Hautnormale, mit
 * der auch die Maske gerechnet ist).
 *
 * Jede Maske rechnet vom VOLLEN Index aller Stücke — auch die Haut
 * (`Hautverdeckung.stoffe` liest `indexVoll`), sonst hinge die Hautmaske
 * davon ab, welches Stück zuerst gekürzt wurde.
 *
 * WANN: bei jedem `Stueckereignis`, gebündelt je Figur und Umlauf, wie die
 * Hautverdeckung. Mit weniger als zwei Stücken werden alle Indizes
 * wiederhergestellt.
 */
import { THREE } from './state.js';
import { Lagenmaske } from '../gemeinsam/lagenmaske.js';
import { Hautmaske } from '../gemeinsam/hautmaske.js';
import { Hautmaskegeometrie } from '../gemeinsam/hautmaskegeometrie.js';
import { Hautverdeckung } from './hautverdeckung.js';
import { Hauteinzug } from '../gemeinsam/hauteinzug.js';
import { Stueckereignis } from './garmentcode_stueckereignis.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Lagenverdeckung {

    /** Alle Stücke der Figur gegeneinander maskieren. */
    static anwenden(inst) {
        const geo = inst?.bodyMesh?.geometry;
        if (!geo?.attributes?.position || !geo.index) return null;
        Hautverdeckung.merken(geo);
        const stoffe = Hautverdeckung.stoffe(inst);
        for (const s of stoffe) Hautverdeckung.merken(inst.clothMeshes[s.schluessel].geometry);
        if (stoffe.length < 2) return Lagenverdeckung.aufheben(inst);
        const t0 = performance.now();
        const koerper = { punkte: geo.attributes.position.array, dreiecke: geo.userData.indexVoll.index };
        const ergebnis = Lagenmaske.verdeckt(koerper, stoffe);
        const stand = { stuecke: [], ms: 0 };
        for (const s of stoffe) {
            const netz = inst.clothMeshes[s.schluessel];
            const { maske, ueber } = ergebnis.get(s.schluessel);
            const voll = netz.geometry.userData.indexVoll;
            const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, maske);
            Hautverdeckung.indexSetzen(netz.geometry, neu.index, neu.gruppen);
            netz.geometry.userData.lagenVerdeckt = ueber.length ? maske : null;
            Lagenverdeckung._einzug(netz, ueber.length ? maske : null, koerper);
            let verdeckt = 0;
            for (let i = 0; i < maske.length; i++) verdeckt += maske[i];
            if (ueber.length) stand.stuecke.push({ stueck: s.schluessel, unter: ueber, verdeckt, dreiecke: neu.entfernt });
        }
        stand.ms = Math.round(performance.now() - t0);
        for (const e of stand.stuecke) {
            Protokoll.debug('Lagenverdeckung', `${e.stueck}: ${e.verdeckt} Punkte unter ${e.unter.join(', ')}, `
                + `${e.dreiecke} Dreiecke ausgeblendet`);
        }
        return stand;
    }

    /** Alle Stücke wieder vollständig zeichnen. */
    static aufheben(inst) {
        for (const netz of Object.values(inst?.clothMeshes || {})) {
            const voll = netz?.geometry?.userData?.indexVoll;
            if (!voll) continue;
            Hautverdeckung.indexSetzen(netz.geometry, voll.index, voll.gruppen);
            delete netz.geometry.userData.lagenVerdeckt;
            Lagenverdeckung._einzug(netz, null, null);
        }
        return { stuecke: [], ms: 0 };
    }

    /**
     * Einzug der verdeckten Ecken entlang der HAUTnormale — die Normale des
     * Stoffnetzes taugt nicht (Wicklung eines Schnitts), und die Maske ist
     * mit derselben Hautnormale gerechnet.
     */
    static _einzug(netz, maske, koerper) {
        const geo = netz.geometry;
        const P = geo.attributes.position.array;
        const werte = new Float32Array(P.length);
        if (maske && koerper) {
            const N = Hautmaskegeometrie.normalen(koerper.punkte, koerper.dreiecke);
            const gitter = Hautmaskegeometrie.punktgitter(koerper.punkte, Hautmaskegeometrie.ZELLE_M);
            const NS = Lagenmaske.normalenVonHaut(P, koerper.punkte, N, gitter);
            for (let i = 0; i < maske.length; i++) {
                if (!maske[i]) continue;
                werte[3 * i] = -Hauteinzug.EINZUG_M * NS[3 * i];
                werte[3 * i + 1] = -Hauteinzug.EINZUG_M * NS[3 * i + 1];
                werte[3 * i + 2] = -Hauteinzug.EINZUG_M * NS[3 * i + 2];
            }
        }
        const bisher = geo.getAttribute('einzug');
        if (bisher && bisher.array.length === werte.length) { bisher.array.set(werte); bisher.needsUpdate = true; }
        else geo.setAttribute('einzug', new THREE.BufferAttribute(werte, 3));
        Hauteinzug.patchen(netz);
    }

    static _ausstehend = new Set();

    static einhaengen() {
        Stueckereignis.hoeren(({ inst }) => {
            if (!inst || Lagenverdeckung._ausstehend.has(inst)) return;
            Lagenverdeckung._ausstehend.add(inst);
            setTimeout(() => {
                Lagenverdeckung._ausstehend.delete(inst);
                try { Lagenverdeckung.anwenden(inst); }
                catch (fehler) { Protokoll.warnung('Lagenverdeckung', fehler.message); }
            }, 0);
        });
    }
}

Lagenverdeckung.einhaengen();
window.__lagenverdeckung = Lagenverdeckung;
