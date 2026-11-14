/**
 * Meshgenesiskikleiderfeld — die Kleider aus der KI im Feld „Ergebnis“ einer Tripo-Jobseite (20.10.2026 nachts, Server `Meshgenesisergebniskleider`).
 * Die Stücke, die die Testseite wirksam gewählt hat (nur Zeilen aus der KI: k geschnitten, s Schnitt, h Frisur), aus ihrer Ruhelage mit der Haltung der KI gehäutet (`Meshgenesistestnetzbau`, dieselben
 * Matrizen wie die Testseite) und als EINE Gruppe auf das Rig der Probe ausgerichtet (`Meshgenesisausrichtung.starr` von den Gelenken der KI-Figur auf das gezeigte Rig) — wie die Figur daneben.
 */
import * as THREE from 'three';
import { Meshgenesisausrichtung } from './meshgenesisausrichtung.js';
import { Meshgenesisflaechennetz } from './meshgenesisflaechennetz.js';
import { Meshgenesishaeutung } from './meshgenesishaeutung.js';
import { Meshgenesistestnetzbau } from './meshgenesistestnetzbau.js';
import { Meshfighautstueck } from '../meshfigur/meshfighautstueck.js';

export class Meshgenesiskikleiderfeld {
    // z (12.11.2026, „Genesis zuerst“): Stück der Garderobe, Server `Meshgenesistestkikleider`
    static WEGE = new Set(['k', 's', 'h', 'f', 'g', 'z']);
    /** = `Kleiderverdeckung.TIEFE_KOSTUEM_M` auf dem Server (ProjektTemp/_wegwerf/meshgenesis_kleider_verdeckung.py) */
    static STOFF_TIEFE_M = 0.040;
    static TEXT = { k: 'aus dem Netz geschnitten', s: 'GarmentCode-Schnitt', f: 'Schnitt aus der Fläche', g: 'Schicht aus der KI', h: 'Frisur der Garderobe (Bibliothek)', z: 'Garderobe' };

    /** → {gruppe, rig, namen: [Text je Stück]} oder null (keine KI-Kleider gewählt). */
    static async laden(ki) {
        const antwort = await fetch(ki.liste);
        if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
        const daten = await antwort.json();
        const matrizen = Meshgenesishaeutung.ausDrehungen(ki.dreh, ki.rig, ki.ruhezentren);
        const gruppe = new THREE.Group();
        const namen = [], stuecke = [];
        // Alle Stücke zugleich holen (08.11.2026, Edgar: „alle modelle sollen innerhalb von max. 5 s angezeigt werden“): vorher wartete jedes Stück auf das vorige — im Log der Seite
        // „Zauberer Alle Textur“ lagen zwischen zwei Stücken 35–75 s, weil nach jeder Textur die Seite neu rechnete (`Fotogenesisseite.nachgeladen`). Gebaut wird weiter in der Reihenfolge der Liste.
        const wahl = (daten.stuecke || []).filter(st => st.quelle === 'ki' && Meshgenesiskikleiderfeld.WEGE.has(st.wahl) && st[st.wahl]?.netz);
        const netze = await Promise.all(wahl.map(st => Meshgenesisflaechennetz.holen(null, st[st.wahl].netz)
            .catch(fehler => { console.warn('Meshgenesiskikleiderfeld: %s nicht geladen (%s)', st.id, fehler.message); return null; })));
        for (const [i, st] of wahl.entries()) {
            const netz = netze[i];
            if (!netz) continue;
            try {
                const mesh = Meshgenesistestnetzbau.mesh(netz, matrizen);
                mesh.userData.art = st.art;
                gruppe.add(mesh);
                namen.push(`${st.name} (${Meshgenesiskikleiderfeld.TEXT[st.wahl]})`);
                const e = st[st.wahl];
                const kostuem = !!(e.kostuem || e.uebertrag?.art === 'rueckhaeutung');                  // Kostüm-Weg A (Stück aus dem Eingang ausgeschnitten)
                stuecke.push({ id: st.id, art: st.art, ruhe: netz.ruhe, dreiecke: netz.dreiecke, netz, kostuem });   // `netz`: die Animation bindet das Stück an das Skelett der Figur (`Meshgenesisbewegungskleid`)
            } catch (fehler) {
                console.warn('Meshgenesiskikleiderfeld: %s nicht geladen (%s)', st.id, fehler.message);
            }
        }
        if (!gruppe.children.length) return null;
        gruppe.userData.meshgenesisFremd = true;          // das Feld gibt die Gruppe beim Leeren nicht frei
        return { gruppe, rig: ki.rig, namen, stuecke, kleiderAn: true };
    }

    /**
     * Die Stücke in der RUHELAGE der KI-Figur als Stoffe der Hautverdeckung (`inst.hautStuecke`, wie `Meshfigurkleider._hautMelden`, 21.10.2026): die Haut und das Anatomie-Stück der
     * Genesis-Figur im Ergebnis fallen dort weg, wo ein Stück sie verdeckt (`Hautverdeckung`, `Anatomieverdeckung`) — Edgar an Mann1: „aus der Hose kommt Genital heraus“. Die Figur im
     * Ergebnis ist aus denselben Reglern gebaut wie die Figur, auf der die Stücke liegen; ihre Ruhelage ist dieselbe. Haar verdeckt keine Haut (`Hautverdeckung.zaehlt`).
     */
    static hautStuecke(ki) {
        const aus = {};
        for (const st of ki?.stuecke || []) {
            if (!st.ruhe || !st.dreiecke) continue;
            const index = st.dreiecke instanceof Uint32Array ? st.dreiecke : Uint32Array.from(st.dreiecke);
            // Kostümstücke (23.10.2026, Edgar an OlesiaWalk: Haut in Flecken auf Shirt und Jeans; an Edgar: „das Haar fehlt an der Schädeldecke“): dieselbe Regel wie der Server
            // (`Kleiderverdeckung.masken`, Fassung 2) — UV-Nähte verschweißt (sonst ist jede Naht ein „lockerer Rand“), Stoff bis `STOFF_TIEFE_M` hinter der Haut (der Körper der KI ragt dort
            // Zentimeter durch das Stück), und Haar verdeckt wie Stoff (die Haarschale aus dem Eingang; der KI-Kopf ragt sonst oben hindurch).
            const { punkte, dreiecke } = st.kostuem ? Meshfighautstueck.verschweissen(st.ruhe, index) : { punkte: st.ruhe, dreiecke: index };
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
            geo.setIndex(new THREE.BufferAttribute(dreiecke, 1));
            const netz = new THREE.Mesh(geo);
            netz.userData.art = st.art === 'haar' && !st.kostuem ? 'haar' : 'kleidung';
            netz.userData.haar = st.art === 'haar';
            if (st.kostuem) netz.userData.stoffTiefe = Meshgenesiskikleiderfeld.STOFF_TIEFE_M;
            aus[`ki_${st.id}`] = netz;
        }
        if (ki) ki.haut = aus;
        return aus;
    }

    /**
     * Schalter „Kleider“ der Jobseite (21.10.2026): alle Stücke ein- oder ausblenden — seit 30.10.2026 auch das Haar (Edgar: „die Haare werden nicht deaktiviert“) —, mit ihnen die Stoffe der
     * Hautverdeckung (`Hautverdeckung.zaehlt` übergeht ausgeblendete). → true, wenn sich etwas geändert hat (dann muss die Hautverdeckung neu planen).
     */
    static kleiderZeigen(ki, an) {
        if (!ki || ki.kleiderAn === an) return false;
        ki.kleiderAn = an;
        for (const kind of ki.gruppe.children) kind.visible = an;
        for (const netz of Object.values(ki.haut || {})) netz.visible = an;
        return true;
    }

    /** Die Gruppe auf das gezeigte Rig legen (gleiche Knochenfolge wie die Beschreibung der Seite) und in das Feld hängen. */
    static einhaengen(inhalt, ki, ziel, ausschnitt) {
        const gruppe = ki.gruppe;
        gruppe.position.set(0, 0, 0);
        gruppe.quaternion.identity();
        if (ziel?.length) {
            const a = [], b = [];
            ziel.forEach((p, i) => { if (p && ki.rig[i]) { a.push(ki.rig[i]); b.push(p); } });
            if (a.length >= 3) {
                const { quaternion, verschiebung } = Meshgenesisausrichtung.starr(a, b);
                gruppe.quaternion.copy(quaternion);
                gruppe.position.copy(verschiebung);
            }
        }
        if (ausschnitt) gruppe.position.add({ x: ausschnitt.ziel[0] - ausschnitt.mitte[0], y: ausschnitt.ziel[1] - ausschnitt.mitte[1], z: ausschnitt.ziel[2] - ausschnitt.mitte[2] });
        gruppe.traverse(o => { o.frustumCulled = false; o.layers.set(1); });
        gruppe.updateMatrixWorld(true);
        inhalt.add(gruppe);
    }
}
