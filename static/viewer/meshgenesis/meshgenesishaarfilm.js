/**
 * Meshgenesishaarfilm — Haar und Bart in der Animation mit der Bewegung aus der Kette statt eigener Pendel (20.11.2026, Edgar: „Weg 2“ — Physik überall mit demselben Code).
 *
 * Gerechnet ist sie auf dem Server (Schritt „haar“, `meshgenesis_kleiderhaar_lauf.py`: die Leitsträhnen mit der Stoffsolver-`Straehnenbahn` auf den Kernen, Sprünge der Bewegung
 * starr mitgetragen); abgelegt je Stück und Bewegung der Versatz NACH dem Häuten an den simulierten Punkten und je Leitpunkt der Punkt davor (`ab`) und der Anteil zum nächsten
 * (`Meshgenesistesthaar`). Hier je Bild Versatz je Leitpunkt = d[ab]·(1 − Anteil) + d[ab + 1]·Anteil, zwischen zwei abgelegten Bildern gemischt, mit der Drehung der `abbildung`
 * (für einen Versatz gilt nur sie) — in die Textur von `Meshgenesishaarschwung`, der Shader addiert ihn wie bisher. Ohne Ablage für die Bewegung (404) oder mit einem anderen Netz
 * (Leitsträhnen × Schritte, `kopf.netz`) bleiben die Pendel (`Lockenpendel`).
 */
import * as THREE from 'three';

export class Meshgenesishaarfilm {
    static FASSUNG = 2;
    static _filme = new Map();          // `${adresse}|${wahl}` → Promise<Film|null>, einmal je Seite

    static holen(adresse, wahl) {
        if (!adresse || !wahl) return Promise.resolve(null);
        const schluessel = `${adresse}|${wahl}`;
        if (!Meshgenesishaarfilm._filme.has(schluessel)) {
            Meshgenesishaarfilm._filme.set(schluessel, fetch(`${adresse}/haar/?bvh=${encodeURIComponent(wahl)}`).then(async antwort => {
                if (antwort.status === 404) return null;
                if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
                return Meshgenesishaarfilm.entpacken(await antwort.arrayBuffer(), wahl);
            }).catch(fehler => { console.warn(`Meshgenesishaarfilm: ${adresse} nicht geladen (${fehler.message})`); return null; }));
        }
        return Meshgenesishaarfilm._filme.get(schluessel);
    }

    /** Paket → Film `{...kopf, wahl, sa, sb, f, daten}`: je Leitpunkt die Spalten des Punkts davor/danach unter den bewegten (−1: ohne Versatz) und der Anteil. */
    static async entpacken(puffer, wahl) {
        const laenge = new DataView(puffer).getUint32(0, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        if (kopf.fassung !== Meshgenesishaarfilm.FASSUNG) throw new Error(`Fassung ${kopf.fassung} statt ${Meshgenesishaarfilm.FASSUNG}`);
        const l = kopf.leitpunkte;
        let o = 4 + laenge;
        const ab = new Int32Array(puffer, o, l); o += 4 * l;
        const anteil = new Uint8Array(puffer, o, l); o += l + ((4 - (l % 4)) % 4);
        const index = new Int32Array(puffer, o, kopf.punkte); o += 4 * kopf.punkte;
        const strom = new Blob([new Uint8Array(puffer, o)]).stream().pipeThrough(new DecompressionStream('deflate'));
        const daten = new Int16Array(await new Response(strom).arrayBuffer());
        const n = kopf.bewegt * 3;
        if (daten.length !== kopf.bilder * n) throw new Error(`${daten.length} Werte statt ${kopf.bilder * n}`);
        for (let i = n; i < daten.length; i++) daten[i] += daten[i - n];             // Differenzen von Bild zu Bild → Versatz je Bild
        const sa = new Int32Array(l), sb = new Int32Array(l), f = new Float32Array(l);
        for (let j = 0; j < l; j++) {
            const a = ab[j];
            sa[j] = a < 0 ? -1 : index[a];
            sb[j] = a < 0 ? -1 : index[a + 1];
            f[j] = anteil[j] / 255;
        }
        return { ...kopf, wahl, sa, sb, f, daten };
    }

    /** Für alle Haarstücke der Bewegung den Film holen; ein Film mit anderem Netz (Leitsträhnen × Schritte) wird nicht genommen. */
    static async anbringenAlle(bewegung) {
        const wahl = bewegung.wahl;
        await Promise.all((bewegung.kleider || []).map(async k => {
            const s = k.mesh?.userData.haarschwung;
            if (!s) return;
            if (s.film && s.film.wahl !== wahl) s.film = null;
            const film = await Meshgenesishaarfilm.holen(k.adresse, wahl);
            if (!film || bewegung.wahl !== wahl) return;
            if (film.netz?.leitstraehnen !== s.g || film.netz?.schritte !== s.k1 || film.leitpunkte !== s.g * s.k1) {
                console.warn(`Meshgenesishaarfilm: ${k.mesh.name} hat ${s.g} × ${s.k1} Leitpunkte, die Ablage ${film.netz?.leitstraehnen} × ${film.netz?.schritte} — Schritt „haar“ neu rechnen, bis dahin Pendel`);
                return;
            }
            s.film = film;
            s.filmStand = -1;
        }));
        bewegung._bild?.();
    }

    /** Je Bild: die Versätze zur Zeit `zeit` (s) in die Textur des Stücks (`s` = `mesh.userData.haarschwung`). */
    static stellen(s, zeit) {
        const fm = s.film;
        const t = Math.max(0, zeit || 0) * fm.fps / fm.jedes;
        const a = Math.min(Math.floor(t), fm.bilder - 1), b = Math.min(a + 1, fm.bilder - 1), u = Math.min(Math.max(t - a, 0), 1);
        if (a + u === s.filmStand) return;
        s.filmStand = a + u;
        const d = fm.daten, m = fm.bewegt * 3, da = a * m, db = b * m, ka = (1 - u) * fm.skala, kb = u * fm.skala;
        const v = new THREE.Vector3(), q = s.q, out = s.daten;
        for (let j = 0, n = fm.leitpunkte; j < n; j++) {
            const ca = 3 * fm.sa[j], cb = 3 * fm.sb[j], w = fm.f[j];
            let x = 0, y = 0, z = 0;
            if (ca >= 0) {
                x = (d[da + ca] * ka + d[db + ca] * kb) * (1 - w); y = (d[da + ca + 1] * ka + d[db + ca + 1] * kb) * (1 - w); z = (d[da + ca + 2] * ka + d[db + ca + 2] * kb) * (1 - w);
            }
            if (cb >= 0) {
                x += (d[da + cb] * ka + d[db + cb] * kb) * w; y += (d[da + cb + 1] * ka + d[db + cb + 1] * kb) * w; z += (d[da + cb + 2] * ka + d[db + cb + 2] * kb) * w;
            }
            if (q) { v.set(x, y, z).applyQuaternion(q); x = v.x; y = v.y; z = v.z; }
            out[j * 4] = x; out[j * 4 + 1] = y; out[j * 4 + 2] = z;
        }
        s.tex.needsUpdate = true;
    }
}
