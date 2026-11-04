import * as THREE from 'three';
import { Eigenkleidbacken } from './eigenkleidbacken.js';
import { Genesis9kleidung } from './genesis9kleidung.js';
import { Gezeichneterpunkt } from './gezeichneterpunkt.js';
import { Modellpruefungbild } from './modellpruefungbild.js';
import { Modellpruefungdeckung } from './modellpruefungdeckung.js';
import { Modellpruefungdurchstoss } from './modellpruefungdurchstoss.js';
import { Modellpruefunggelenke } from './modellpruefunggelenke.js';
import { Modellpruefunghaar } from './modellpruefunghaar.js';
import { Modellpruefungsaum } from './modellpruefungsaum.js';

/**
 * Modellpruefung — Fehler eines Genesis-9-Modells finden (02.11.2026; vorher `ProjektTemp/_wegwerf/tripo_wahrheit/wahrheit_pruefung.js`, dort vor jedem Export des
 * Wahrheitsdatensatzes). Edgar: „Kaputte Finger, schuhe nicht auf den Füssen, weisse haare!“, „Zacken beim Ärmel (kein Saum)“; Menü Werkzeuge → Modell Check
 * (`charakter/modellcheck.js`). Klassen, die Bilder zeichnet `Modellpruefungbild` (rot = Befund):
 *   deckung    Körper rot, wo Stoff sein muss (`Modellpruefungdeckung.muss`); das Daz-Anatomie-Stück nur, wo Stoff sein muss oder Kleidung anliegt. Neun Ansichten.
 *   schuhe     Füße von unten, Fußhaut rot — ein getragener Schuh deckt die Sohle.
 *   haare      die Frisur allein unter weißem Licht — fast weiß und grau = ohne Textur; dazu Haarkarten ohne Deckkraft (Material mit Bild, aber ohne Alpha, Schnitt,
 *              Alpha-to-Coverage oder Linien) — dann steht der Kartengrund als Blöcke im Haar; nur auf Karten, nicht auf geschlossenen Netzen (`Modellpruefunghaar`).
 *   finger     Punkte einer Hand, die > 3 mm in der anderen stecken (Lot auf die nach außen gerichtete Normale des nächsten Punkts).
 *   handstoff  Stoff der Oberteil-/Kleid-Schale, der höchstens 2 cm vor der Handhaut liegt (sechs Nahbilder je Hand, Tiefe getrennt) — Fetzen am Bündchen (Amala).
 *   gelenke, durchstoss, saeume  Klassen der Sitzung roomguest-f0 (`Modellpruefunggelenke`, `Modellpruefungdurchstoss`, `Modellpruefungsaum`).
 * Grenzen GESETZT, geeicht am Fehlerbild vom 02.11.2026 (Tagebuch `2026-11-02_eigenkleider-in-gebackener-pose.md`): Deckung 10 px (bis 02.11.2026 abends 60 — die ließ
 * Damiras Hautspalt am Rücken mit 48 px durch; Olesia mit Anatomie-Stück 125), Fußsohle 1 % (Afrikanerin 4,6, Laura 3,6, Kat 0), Haar 200 (charm_hair ohne Variante 231),
 * Finger 20 (Pose 29: 77/47, Laura 0).
 * Verworfen: Finger gegen den ganzen Körper (Hand außen auf der Hüfte zählte 5.600), umgeklappte Fläche als Lochmaß (verdeckte Falten) — nur Auskunft.
 * Mit `marken` gibt die Prüfung je Klasse die Punkte zurück, die im Prüfbild rot zu sehen sind (`Map` Netz → Uint8Array) — für die 3D-Ansicht (`Modellcheck3d`).
 */
export class Modellpruefung {

    static DECKUNG_PX_MAX = 10;
    static HAND_STOFF_M = 0.02;
    static HAND_STOFF_PX_MAX = 50;          // Nahbild je Hand 600 × 800, Kiste füllt das Bild; Amala Langarm vor dem Fix 639/353 px (Ring am Handgelenk, 0,3 % der Handhaut)
    static HAND_KONTAKT_M = 0.02;           // Handhaut so nah an Rumpf, Bein oder Kopf liegt am Stoff an (Laura: Hand auf der Hüfte, 10.228 px) — zählt nicht
    static HAAR_OHNE_DECKKRAFT_MAX = 0.5;
    static FUSS_ANTEIL_MAX = 0.01;
    static HAAR_WEISS = 200;
    static HAND_TIEFE_M = 0.003;
    static HAND_PUNKTE_MAX = 20;
    static FUSS = /^(l|r)_(foot|metatarsals|toes|bigtoe|indextoe|midtoe|ringtoe|pinkytoe)/;
    static HAND = /^(l|r)_(hand|carpal\d*|thumb\d|index\d|mid\d|ring\d|pinky\d|(index|mid|ring|pinky)metacarpal)$/;     // ohne `l_indextoe1` u. a. (bis 02.11.2026 abends mitgezählt)
    static ARM = /^(l|r)_(forearm|upperarm|shoulder)/;
    static KOPF = /head|neck|eye|jaw|tongue|teeth|lip|brow|ear|nose|cheek|squint|nasolabial|mouth/i;
    static SCHUH = /schuh|stiefel|shoe|boot|sneaker|sandal|heel|pump/i;

    /**
     * → `{ok, fehler, pruefungen: [{schluessel, titel, ok, text}], deckung, fuesse, haare, haende, handstoff, gelenke, durchstoss, saeume, gefaltet, bilder?, marken?}`.
     * `gebacken`: schon gebackene Netze (`Eigenkleidbacken`), sonst backt die Prüfung selbst und gibt sie danach frei.
     */
    static async pruefen(inst, { bilder = false, gebacken = null, marken = false } = {}) {
        if (inst?.quelle !== 'genesis9' || !inst.bodyMesh?.skeleton) throw new Error('Der Modell-Check prüft nur Genesis-9-Figuren.');
        const katalog = await Genesis9kleidung.stuecke();
        const eigene = gebacken || await Eigenkleidbacken.backen(inst);
        try {
            return Modellpruefung._rechnen(inst, katalog, eigene, bilder, marken);
        } finally {
            if (!gebacken) Eigenkleidbacken.weg(eigene);
        }
    }

    static _rechnen(inst, katalog, gebacken, mitBildern, mitMarken) {
        const M = Modellpruefung, D = Modellpruefungdeckung, koerper = inst.bodyMesh;
        inst.group.updateMatrixWorld(true);
        const n = koerper.geometry.attributes.position.count, p = new THREE.Vector3();
        const objekt = new Float32Array(3 * n), lage = new Float32Array(3 * n);
        for (let i = 0; i < n; i++) {
            Gezeichneterpunkt.lage(koerper, i, p); objekt.set([p.x, p.y, p.z], 3 * i);         // mit dem Hauteinzug unter der Kleidung, wie gezeichnet
            p.applyMatrix4(koerper.matrixWorld); lage.set([p.x, p.y, p.z], 3 * i);
        }
        const kn = M.knochenJe(koerper), glied = Uint8Array.from(kn, (k) => (M.ARM.test(k) || M.HAND.test(k) || M.FUSS.test(k) || M.KOPF.test(k) ? 1 : 0));
        const netze = [];
        inst.group.traverseVisible((o) => { if (o.isMesh && o !== koerper && o.geometry?.attributes?.position) netze.push(o); });
        const stueckVon = (o) => { const m = /^genesis9_kleid_(.+?)(_\d+)?$/.exec(o.name || ''); return m ? katalog.find((s) => s.id === m[1]) || { id: m[1] } : null; };
        const muss = D.muss(gebacken, objekt, lage, glied, netze);
        const anatomie = netze.filter((o) => /^daz_anatomie/.test(stueckVon(o)?.id || ''));
        // Kleidung für Anatomie, Durchstoß und Säume: die gebackenen Eigenschalen statt der lebenden (deren Punkte liegen ohne den Shader auf der Haut), ohne das
        // Anatomie-Stück (Katalogart „kleidung“, aber Haut: sein Rand ist kein Saum, der Körper darunter kein Durchstoß). Hängen die gebackenen schon in der Gruppe
        // (Exportlauf `wahrheit_eigen.js`), nur einmal — sonst stand jeder Saum doppelt im Befund (Olesia, 02.11.2026)
        const stoffe = netze.filter((o) => !o.userData?.eigenkleid && !anatomie.includes(o) && !gebacken.includes(o)).concat(gebacken);
        const scham = D.anatomieUnterStoff(anatomie, lage, muss, Modellpruefungdurchstoss.kleider(stoffe));
        const schuhe = netze.filter((o) => { const e = stueckVon(o); return e && M.SCHUH.test(`${e.kategorie || ''} ${e.id}`); });
        const frisuren = netze.filter((o) => stueckVon(o)?.art === 'haar');
        const fehler = [], pruefungen = [];
        const box = new THREE.Box3();
        for (let i = 0; i < n; i++) box.expandByPoint(p.set(lage[3 * i], lage[3 * i + 1], lage[3 * i + 2]));
        const bild = new Modellpruefungbild(inst, mitBildern, mitMarken), farbe = new Float32Array(3 * n);
        const deckung = { muss_punkte: muss.reduce((a, b) => a + b, 0), anatomie: scham.reduce((a, s) => a + s.zahl, 0), ansichten: [], rote_px_max: 0 };
        const marken = mitMarken ? { deckung: new Map(), schuhe: new Map(), handstoff: new Map(), finger: new Map(), durchstoss: new Map(), saeume: new Map() } : null;
        const wo = (a) => { const r = []; for (let i = 0; i < a.length; i++) if (a[i]) r.push(i); return r; };
        // Prüfpunkte einer Klasse für `Modellpruefungbild`: dort markiert, was im Prüfbild rot zu sehen ist (`stoff`: Tiefe gegen die Schalen statt den Körper)
        const kandidaten = (klasse, netz, ort, idx, stoff = false) => {
            if (!marken) return [];
            if (!marken[klasse].has(netz)) marken[klasse].set(netz, new Uint8Array(ort.length / 3));
            return [{ lage: ort, idx, marke: marken[klasse].get(netz), stoff }];
        };
        let fuesse = null, haare = null, handstoff = null;
        try {
            for (let i = 0; i < n; i++) farbe[3 * i] = muss[i];
            bild.anfangen(farbe, gebacken);
            bild.punktfarben(anatomie, scham.map((s) => s.unter));
            if (deckung.muss_punkte || deckung.anatomie) {
                const k = [...kandidaten('deckung', koerper, lage, wo(muss)), ...anatomie.flatMap((o, j) => kandidaten('deckung', o, scham[j].lage, wo(scham[j].unter)))];
                deckung.ansichten = bild.rundum(box.getCenter(new THREE.Vector3()), box.max.y - box.min.y, k);
                deckung.rote_px_max = Math.max(...deckung.ansichten.map((a) => a.rote_px));
            }
            const schalen = netze.filter((o) => ['oberteil', 'kleid'].includes(o.userData?.eigenkleid));
            if (schalen.length) {
                farbe.fill(0);
                const kisten = { l: new THREE.Box3(), r: new THREE.Box3() }, kontakt = M.kontakt(lage, kn, M.HAND_KONTAKT_M), frei = { l: [], r: [] };
                for (let i = 0; i < n; i++) {
                    if (!M.HAND.test(kn[i])) continue;
                    if (!kontakt[i]) { farbe[3 * i + 1] = 1; frei[kn[i][0]].push(i); }
                    kisten[kn[i][0]].expandByPoint(p.set(lage[3 * i], lage[3 * i + 1], lage[3 * i + 2]));
                }
                bild.farbe.needsUpdate = true;
                const aermel = gebacken.filter((b) => ['oberteil', 'kleid'].includes(b.userData.eigenGebacken));
                const k = (s) => [...kandidaten('handstoff', koerper, lage, frei[s]), ...aermel.flatMap((b) => {
                    const ort = b.geometry.attributes.position.array;
                    return kandidaten('handstoff', b, ort, Array.from({ length: ort.length / 3 }, (_, i) => i), true);
                })];
                handstoff = { l: bild.stoffAuf(kisten.l, koerper, schalen, 'hand_links', M.HAND_STOFF_M, k('l')),
                              r: bild.stoffAuf(kisten.r, koerper, schalen, 'hand_rechts', M.HAND_STOFF_M, k('r')) };
            }
            if (schuhe.length) {
                farbe.fill(0);
                const kiste = new THREE.Box3(), fuss = [];
                for (let i = 0; i < n; i++) if (M.FUSS.test(kn[i])) { farbe[3 * i] = 1; fuss.push(i); kiste.expandByPoint(p.set(lage[3 * i], lage[3 * i + 1], lage[3 * i + 2])); }
                bild.farbe.needsUpdate = true;
                const z = bild.vonUnten(kiste, kandidaten('schuhe', koerper, lage, fuss));
                fuesse = { schuhe: schuhe.map((o) => stueckVon(o).id), fuss_px: z.rot, anteil: +(z.rot / Math.max(z.rot + z.schwarz + z.hell, 1)).toFixed(3) };
            }
            if (frisuren.length) {
                const z = bild.allein(frisuren, 'haare');
                haare = { frisuren: [...new Set(frisuren.map((o) => stueckVon(o).id))], mittel: z.mittel, ohne_deckkraft: Modellpruefunghaar.ohneDeckkraft(frisuren) };
            }
        } finally {
            bild.ende();
        }
        const nrm = M.normalen(koerper, lage), fingerPunkte = [];
        const haende = M.finger(lage, nrm, kn, fingerPunkte);
        const gelenke = Modellpruefunggelenke.pruefen(koerper, lage);          // Klassen der Sitzung roomguest-f0 (2d-3d-AI)
        const durchstoss = Modellpruefungdurchstoss.pruefen(koerper, lage, stoffe, nrm);
        const saeume = Modellpruefungsaum.pruefen(koerper, lage, stoffe);
        const gefaltet = Object.fromEntries(gebacken.map((b) => [b.userData.eigenGebacken, b.userData.gefaltet]).filter(([, v]) => v));

        const eintragen = (schluessel, titel, ok, text) => { pruefungen.push({ schluessel, titel, ok, text }); if (ok === false) fehler.push(`${titel}: ${text}`); };
        const zu = deckung.ansichten.filter((a) => a.rote_px > M.DECKUNG_PX_MAX);
        eintragen('deckung', 'Haut, wo Stoff sein muss', deckung.ansichten.length ? !zu.length : null, !deckung.ansichten.length ? 'keine eigenen Stücke, kein Rock, kein Anatomie-Stück unter Stoff'
            : (zu.length ? `${zu.map((a) => `${a.rolle} ${a.rote_px} px`).join(', ')} (Grenze ${M.DECKUNG_PX_MAX} px je Ansicht)` : `höchstens ${deckung.rote_px_max} px je Ansicht`));
        eintragen('schuhe', 'Fuß im Schuh', fuesse ? fuesse.anteil <= M.FUSS_ANTEIL_MAX : null, fuesse
            ? `${fuesse.schuhe.join(', ')}: Fußsohle von unten zu ${(100 * fuesse.anteil).toFixed(1)} % sichtbar (Grenze ${100 * M.FUSS_ANTEIL_MAX} %)` : 'keine Schuhe');
        const weiss = haare && Math.min(...haare.mittel) > M.HAAR_WEISS && Math.max(...haare.mittel) - Math.min(...haare.mittel) < 25;
        const karten = haare && haare.ohne_deckkraft > M.HAAR_OHNE_DECKKRAFT_MAX;
        eintragen('haare', 'Frisur mit Textur', haare ? !weiss && !karten : null, haare ? `${haare.frisuren.join(', ')}: Mittel ${haare.mittel.join('/')}${weiss ? ' — fast weiß, ohne Textur' : ''}`
            + `, ${Math.round(100 * haare.ohne_deckkraft)} % der Dreiecke auf Haarkarten ohne Deckkraft${karten ? ` (Grenze ${100 * M.HAAR_OHNE_DECKKRAFT_MAX} %) — Kartengrund als Blöcke im Haar` : ''}` : 'keine Frisur');
        const fingerZu = haende.l > M.HAND_PUNKTE_MAX || haende.r > M.HAND_PUNKTE_MAX;
        eintragen('finger', 'Finger frei', !fingerZu, `${haende.l} Punkte links, ${haende.r} rechts in der anderen Hand (Grenze ${M.HAND_PUNKTE_MAX}, jeder zweite gezählt)`);
        const handZu = handstoff && Object.values(handstoff).filter((h) => h.auf_px > M.HAND_STOFF_PX_MAX);
        eintragen('handstoff', 'Kein Stoff auf den Händen', handstoff ? !handZu.length : null, handstoff
            ? Object.entries(handstoff).map(([s, h]) => `${s === 'l' ? 'links' : 'rechts'} ${h.auf_px} px (${h.rolle})`).join(', ')
                + ` — Stoff ≤ ${100 * M.HAND_STOFF_M} cm vor der Handhaut (Grenze ${M.HAND_STOFF_PX_MAX} px je Nahbild)` : 'kein eigenes Oberteil oder Kleid');
        eintragen('gelenke', 'Gelenke im Körper', !gelenke.aussen.length, gelenke.aussen.length
            ? gelenke.aussen.map((g) => `${g.name} ${g.abstand_mm} mm außen`).join(', ') : `${gelenke.geprueft} Knochen innen`);
        eintragen('durchstoss', 'Körper unter der Kleidung', durchstoss.geprueft ? !durchstoss.zu.length : null, durchstoss.stuecke.length
            ? durchstoss.stuecke.map((s) => `${s.name} ${s.zahl} Punkte bis ${s.tief_mm} mm außen`).join(', ') + ` (Grenze ${Modellpruefungdurchstoss.PUNKTE_MAX})`
            : (durchstoss.geprueft ? 'kein Punkt außerhalb' : 'keine Kleidung'));
        eintragen('saeume', 'Säume glatt', saeume.geprueft ? !saeume.zu.length : null, saeume.zu.length
            ? saeume.zu.slice(0, 6).map((x) => `${x.name} ${x.laenge_mm} mm: Zacken ${x.zacken_mm} mm, Überlänge ${Math.round(100 * x.ueberlaenge)} %`).join(', ')
                + (saeume.zu.length > 6 ? ` … (${saeume.zu.length})` : '') : (saeume.geprueft ? `${saeume.saeume.length} Säume glatt` : 'keine Kleidung'));
        const aus = { ok: !fehler.length, fehler, pruefungen, deckung, fuesse, haare, haende, handstoff, gelenke, durchstoss, saeume, gefaltet };
        if (mitBildern) aus.bilder = bild.bilder;
        if (marken) {
            const setzen = (klasse, netz, liste) => {
                const m = netz.geometry.attributes.position.count, a = marken[klasse].get(netz) || new Uint8Array(m);
                for (const i of liste) a[i] = 1;
                marken[klasse].set(netz, a);
            };
            setzen('finger', koerper, fingerPunkte);
            setzen('durchstoss', koerper, durchstoss.zu.flatMap((s) => s.punkte));
            for (const s of saeume.zu) { const o = stoffe.find((x) => (x.name || x.uuid) === s.name); if (o) setzen('saeume', o, s.punkte); }
            aus.marken = { ...marken, haare: frisuren, gelenke: gelenke.aussen.map((g) => g.name) };
        }
        return aus;
    }

    /** Je Punkt 1, wenn ein Handpunkt näher als `r` an einem Punkt außerhalb von Hand und Arm liegt (Hand liegt am Körper an). */
    static kontakt(lage, kn, r) {
        const M = Modellpruefung, zellen = new Map(), schl = (x, y, z) => `${Math.floor(x / r)},${Math.floor(y / r)},${Math.floor(z / r)}`, aus = new Uint8Array(kn.length);
        for (let j = 0; j < kn.length; j++) {
            if (M.HAND.test(kn[j]) || M.ARM.test(kn[j])) continue;
            const k = schl(lage[3 * j], lage[3 * j + 1], lage[3 * j + 2]);
            if (!zellen.has(k)) zellen.set(k, []);
            zellen.get(k).push(j);
        }
        for (let i = 0; i < kn.length; i++) {
            if (!M.HAND.test(kn[i])) continue;
            const x = lage[3 * i], y = lage[3 * i + 1], z = lage[3 * i + 2], cx = Math.floor(x / r), cy = Math.floor(y / r), cz = Math.floor(z / r);
            suche: for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
                for (const j of zellen.get(`${cx + a},${cy + b},${cz + c}`) || []) {
                    if ((lage[3 * j] - x) ** 2 + (lage[3 * j + 1] - y) ** 2 + (lage[3 * j + 2] - z) ** 2 < r * r) { aus[i] = 1; break suche; }
                }
            }
        }
        return aus;
    }

    /** Punkte je Hand, die > `HAND_TIEFE_M` in der anderen Hand stecken (jeder zweite Punkt); ihre Nummern dazu in `punkte`. */
    static finger(lage, nrm, kn, punkte = []) {
        const M = Modellpruefung, haende = { l: [], r: [] }, aus = { l: 0, r: 0 }, z = 0.03;
        for (let i = 0; i < kn.length; i++) if (M.HAND.test(kn[i])) haende[kn[i][0]].push(i);
        for (const s of ['l', 'r']) {
            const zellen = new Map(), schl = (x, y, w) => `${Math.floor(x / z)},${Math.floor(y / z)},${Math.floor(w / z)}`;
            for (const j of haende[s === 'l' ? 'r' : 'l']) { const k = schl(lage[3 * j], lage[3 * j + 1], lage[3 * j + 2]); if (!zellen.has(k)) zellen.set(k, []); zellen.get(k).push(j); }
            for (let k = 0; k < haende[s].length; k += 2) {
                const i = haende[s][k], x = lage[3 * i], y = lage[3 * i + 1], w = lage[3 * i + 2];
                const cx = Math.floor(x / z), cy = Math.floor(y / z), cw = Math.floor(w / z);
                let j = -1, bd = z * z;
                for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
                    for (const m of zellen.get(`${cx + a},${cy + b},${cw + c}`) || []) {
                        const d = (lage[3 * m] - x) ** 2 + (lage[3 * m + 1] - y) ** 2 + (lage[3 * m + 2] - w) ** 2;
                        if (d < bd) { bd = d; j = m; }
                    }
                }
                if (j >= 0 && (x - lage[3 * j]) * nrm[3 * j] + (y - lage[3 * j + 1]) * nrm[3 * j + 1] + (w - lage[3 * j + 2]) * nrm[3 * j + 2] < -M.HAND_TIEFE_M) { aus[s]++; punkte.push(i); }
            }
        }
        return aus;
    }

    /** Normalen der Haltung, nach außen: Vorzeichen gegen die Normalen des Netzes ausgerichtet. */
    static normalen(netz, lage) {
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        if (netz.geometry.index) g.setIndex(netz.geometry.index.clone());
        g.computeVertexNormals();
        const n = g.attributes.normal.array.slice(), alt = netz.geometry.attributes.normal?.array;
        g.dispose();
        if (alt) { let s = 0; for (let i = 0; i < n.length; i++) s += n[i] * alt[i]; if (s < 0) for (let i = 0; i < n.length; i++) n[i] = -n[i]; }
        return n;
    }

    /** Vorherrschender Knochen je Punkt. */
    static knochenJe(netz) {
        const si = netz.geometry.attributes.skinIndex, sw = netz.geometry.attributes.skinWeight, bones = netz.skeleton.bones, aus = new Array(si.count);
        for (let i = 0; i < si.count; i++) {
            let best = 0, bw = -1;
            for (let k = 0; k < 4; k++) { const w = sw.getComponent(i, k); if (w > bw) { bw = w; best = si.getComponent(i, k); } }
            aus[i] = bones[best]?.name || '';
        }
        return aus;
    }
}
