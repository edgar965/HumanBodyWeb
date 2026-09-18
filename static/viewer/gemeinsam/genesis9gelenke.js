import { Dazachsen } from './dazachsen.js';
import { Gelenkformeln } from './gelenkformeln.js';
import { Genesis9felder } from './genesis9felder.js';

/**
 * Genesis9gelenke — Daz' Gelenkkorrekturen (JCMs) in der BEWEGUNG einer
 * Genesis-9-Figur (Edgar, 18.09.2026: „Mach Daz' JCMs").
 *
 * In Daz stellt eine Formel den Korrekturmorph aus der Knochendrehung:
 * `body_cbs_thigh_x35p_l = clamp(l_thigh?rotation/x / 35)` — der Oberschenkel
 * beugt sich, die Gesäßfalte kommt, das Knie bleibt rund. Posen-Presets
 * tragen die Werte gebacken mit; die BVH-Bewegung kannte sie bis heute nicht.
 *
 * JE BILD, nach dem Mischer: (1) die Daz-Winkel der 52 Eingabeknochen aus
 * ihren Quaternionen lesen (`Dazachsen.winkel`), (2) den Formelgraphen
 * rechnen (`Gelenkformeln`, 157 Kanäle), (3) die Felder der 117 Morphe mit
 * ihren Werten ins Netz summieren (`Genesis9felder.anwenden`) — Körper und
 * Mund-Anhang. Steht die Figur in Ruhe, sind alle Winkel 0 und die Felder
 * gehen wieder heraus; ein neues Skelett (`neuFormen`) verwirft den Stand.
 *
 * Läuft in der Szene (`szenenschleife.js`) und im Studio (`playback.js`),
 * beide rufen `takt(inst)` je Genesis-9-Figur.
 *
 * SEIT 18.09.2026 NACHTS (Edgar: „mach beide"): (a) Die KLEIDUNG folgt —
 * wie Daz' Auto-Follow — mit eigenen Feldern je Stück (`Genesis9felder.
 * holenStueck`, `Genesis9/stueckfelder.py`: die Körperdeltas auf die Teile
 * projiziert), Teil für Teil auf `clothMeshes[kennung/n]`; ein Stück wird
 * geholt, sobald es getragen wird. Ein dForce-Stück zeigt beim Abspielen
 * sein Simulationsnetz (`genesis9stoffschwung.js`), das die Felder nicht
 * sieht — lose Kleider, dort spielt es keine Rolle. (b) Die zwei SCHALTER
 * des Graphen (`Base Joint Correctives`, `Flexion Automatic Strength`)
 * kommen als `inst.gelenkregler` mit der Figurantwort — gestellt im
 * Bedienfeld oder über eine Charakterformel (Fabrice: Beugungen 1).
 */
export class Genesis9gelenke {

    static GRUPPE = 'gelenke';
    static SCHWELLE = 0.005;
    static _figuren = new WeakMap();          // inst -> {skelett, knochen, felder, stuecke}
    static _winkel = [0, 0, 0];

    /** Trifft die Figur zu — eine Genesis 9 mit Skelett und Körpernetz? */
    static passt(inst) {
        return !!(inst && inst.quelle === 'genesis9' && inst.skelett?.skeleton && inst.bodyMesh);
    }

    /**
     * Ein Bild: Winkel lesen, Graph rechnen, Felder schreiben. Die Felder
     * (7–30 MB je Stufe, dazu je Stück) werden erst geholt, wenn die Figur
     * ihre Ruhe verlässt (`Dazachsen.bewegt`) — eine stehende Figur kostet
     * nichts (18.09.2026 nachts: das Laden dauerte über eine Minute).
     */
    static takt(inst) {
        if (!Genesis9gelenke.passt(inst)) return null;
        const bekannt = Genesis9gelenke._figuren.get(inst);
        if (!(bekannt && bekannt.skelett === inst.skelett && bekannt.stufen === inst.stufen)
            && !Dazachsen.bewegt(inst.skelett)) return null;
        const eintrag = Genesis9gelenke._eintrag(inst);
        if (!eintrag?.felder) return null;
        const { felder, knochen } = eintrag;
        /** @type {Object<string, number[]>} */
        const winkel = {};
        for (const name of felder.graph.knochen) {
            const k = knochen[name];
            if (k) winkel[name] = Dazachsen.winkel(k, [0, 0, 0]);
        }
        const eingaben = { ...Gelenkformeln.eingaben(winkel), ...(inst.gelenkregler || {}) };
        const werte = Gelenkformeln.werte(felder.graph, eingaben);
        for (const name of Object.keys(werte)) {
            if (Math.abs(werte[name]) < Genesis9gelenke.SCHWELLE) delete werte[name];
        }
        Genesis9felder.anwenden(inst.bodyMesh, Genesis9gelenke.GRUPPE, felder.koerper, werte);
        for (const [schluessel, netz] of Object.entries(inst.anhangNetze || {})) {
            const eigene = felder.anhaenge[schluessel];
            if (eigene) Genesis9felder.anwenden(netz, Genesis9gelenke.GRUPPE, eigene, werte);
        }
        Genesis9gelenke._kleidung(inst, eintrag, werte);
        eintrag.werte = werte;
        return werte;
    }

    /** Die getragenen Stücke: Felder holen, sobald ein Stück neu ist, und Teil für Teil anwenden. */
    static _kleidung(inst, eintrag, werte) {
        const stuecke = eintrag.stuecke;
        for (const kennung of Object.keys(inst.kleidung || {})) {
            if (stuecke.has(kennung)) continue;
            stuecke.set(kennung, null);
            Genesis9felder.holenStueck(Genesis9gelenke.GRUPPE, kennung, inst.stufen).then(teile => {
                if (Genesis9gelenke._figuren.get(inst) === eintrag) stuecke.set(kennung, teile || []);
            });
        }
        for (const [schluessel, netz] of Object.entries(inst.clothMeshes || {})) {
            const [kennung, nummer] = schluessel.split('/');
            const eigene = stuecke.get(kennung)?.[Number(nummer)];
            if (eigene && Object.keys(eigene).length) {
                Genesis9felder.anwenden(netz, Genesis9gelenke.GRUPPE, eigene, werte);
            }
        }
    }

    /** Alle Figuren einer Seite (`state.characters.values()`, Studio-Modelle). */
    static alle(figuren) {
        for (const inst of figuren) {
            if (Genesis9gelenke.passt(inst)) Genesis9gelenke.takt(inst);
        }
    }

    /** Der zuletzt gerechnete Stand `{morph: wert}` — für Sichtproben. */
    static werte(inst) {
        return Genesis9gelenke._figuren.get(inst)?.werte || null;
    }

    /** Felder und Achsen je Figur; das Skelett entscheidet, ob neu vorbereitet wird. */
    static _eintrag(inst) {
        let eintrag = Genesis9gelenke._figuren.get(inst);
        if (eintrag && eintrag.skelett === inst.skelett && eintrag.stufen === inst.stufen) {
            return eintrag;
        }
        eintrag = { skelett: inst.skelett, stufen: inst.stufen, felder: null, knochen: null, werte: null,
                    stuecke: new Map() };          // kennung -> [{kanal: {n, d}}] je Teil (null = lädt)
        Genesis9gelenke._figuren.set(inst, eintrag);
        Genesis9felder.holen(Genesis9gelenke.GRUPPE, inst.stufen).then(felder => {
            if (!felder || Genesis9gelenke._figuren.get(inst) !== eintrag) return;
            const alle = Dazachsen.vorbereiten(inst.skelett, felder.achsen);
            eintrag.knochen = Object.fromEntries(
                felder.graph.knochen.filter(n => alle[n]).map(n => [n, alle[n]]));
            eintrag.felder = felder;
        });
        return eintrag;
    }

    /** Die Figur verlässt die Bewegung: Felder heraus, Stand vergessen. */
    static vergessen(inst) {
        if (!inst) return;
        if (inst.bodyMesh) Genesis9felder.entfernen(inst.bodyMesh, Genesis9gelenke.GRUPPE);
        for (const netz of [...Object.values(inst.anhangNetze || {}), ...Object.values(inst.clothMeshes || {})]) {
            Genesis9felder.entfernen(netz, Genesis9gelenke.GRUPPE);
        }
        Genesis9gelenke._figuren.delete(inst);
    }
}
