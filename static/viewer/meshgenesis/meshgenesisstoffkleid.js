/**
 * Meshgenesisstoffkleid — ein Stück der Kleiderbibliothek in der Animation als Stoff statt als zweite Haut (19.11.2026, Edgar über websites-ab: „in Bewegung als Stoff simuliert, mit Falten“).
 *
 * Gerechnet ist der Stoff vorab auf dem Server, je Stück und Bewegung (Schritt „stoff“ der Kette, `meshgenesis_kleiderstoff_lauf.py`, Stoffsolver mit Kernmotor) — wie dForce in Daz. Abgelegt ist
 * je Bild der Versatz jedes Punkts gegen die reine Häutung, in die RUHELAGE zurückgerechnet (die lineare Hautmischung ist dort linear). Hier wird je Bild die Bindelage des `SkinnedMesh` auf
 * Ruhe + Versatz gesetzt (zwischen zwei abgelegten Bildern gemischt) und die Normalen daraus neu gerechnet; die Karte häutet wie bisher — Wurzel, Ausrichtung (`abbildung`, nur die Drehung gilt
 * für einen Versatz) und Bodenstand bleiben die der Seite. Der Kapselschub (`Meshgenesiskollision`) ist für ein Stoffstück aus (Radien 0): den Körper hält der Stoff selbst fern.
 *
 * Ohne Stoff für diese Bewegung (404) bleibt das Stück gehäutet. Paket Fassung 2 (`Meshgenesisteststoff`): uint32 Kopflänge, JSON-Kopf `{fassung, fps, jedes, bilder, punkte, bewegt, skala}`,
 * int32 `index` (Punkte; Spalte unter den bewegten oder −1), dann deflate der int16-Versätze (Bilder, bewegt, 3), von Bild zu Bild differenziert — hier einmal aufsummiert.
 * Nur Punkte, die sich bewegen, und die Dreiecke um sie werden je Bild angefasst (`_teilnetz`): am eng anliegenden gk_anzug 192 von 29.847 Punkten.
 */
import * as THREE from 'three';

export class Meshgenesisstoffkleid {
    static FASSUNG = 2;
    static _filme = new Map();          // `${adresse}|${wahl}` → Promise<Film|null>, einmal je Seite

    /** Der Film eines Stücks für die Bewegung `wahl` ('Kategorie/Name') oder null. */
    static holen(adresse, wahl) {
        if (!adresse || !wahl) return Promise.resolve(null);
        const schluessel = `${adresse}|${wahl}`;
        if (!Meshgenesisstoffkleid._filme.has(schluessel)) {
            Meshgenesisstoffkleid._filme.set(schluessel, fetch(`${adresse}/stoff/?bvh=${encodeURIComponent(wahl)}`).then(async antwort => {
                if (antwort.status === 404) return null;
                if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
                return Meshgenesisstoffkleid.entpacken(await antwort.arrayBuffer(), wahl);
            }).catch(fehler => { console.warn(`Meshgenesisstoffkleid: ${adresse} nicht geladen (${fehler.message})`); return null; }));
        }
        return Meshgenesisstoffkleid._filme.get(schluessel);
    }

    /** Paket → Film `{...kopf, wahl, index: Int32Array(punkte), daten: Int16Array(bilder · bewegt · 3)}` mit aufsummierten Versätzen. */
    static async entpacken(puffer, wahl) {
        const laenge = new DataView(puffer).getUint32(0, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        if (kopf.fassung !== Meshgenesisstoffkleid.FASSUNG) throw new Error(`Fassung ${kopf.fassung} statt ${Meshgenesisstoffkleid.FASSUNG}`);
        const index = new Int32Array(puffer, 4 + laenge, kopf.punkte);
        const strom = new Blob([new Uint8Array(puffer, 4 + laenge + 4 * kopf.punkte)]).stream().pipeThrough(new DecompressionStream('deflate'));
        const daten = new Int16Array(await new Response(strom).arrayBuffer());
        const n = kopf.bewegt * 3;
        if (daten.length !== kopf.bilder * n) throw new Error(`${daten.length} Werte statt ${kopf.bilder * n}`);
        for (let i = n; i < daten.length; i++) daten[i] += daten[i - n];             // Differenzen von Bild zu Bild → Versatz je Bild (bleibt in int16, ±3,3 m)
        return { ...kopf, wahl, index, daten };
    }

    /** Für alle gebundenen Stücke der Bewegung den Film der gewählten Bewegung holen und anhängen (ein Stück mit dem Film einer anderen Bewegung wird erst abgenommen). */
    static async anbringenAlle(bewegung) {
        const wahl = bewegung.wahl;
        await Promise.all((bewegung.kleider || []).map(async k => {
            if (k.mesh.userData.stoff && k.mesh.userData.stoff.film.wahl !== wahl) Meshgenesisstoffkleid.abnehmen(k.mesh);
            const film = await Meshgenesisstoffkleid.holen(k.adresse, wahl);
            if (film && bewegung.wahl === wahl && !k.mesh.userData.stoff) Meshgenesisstoffkleid.anbringen(k.mesh, film, bewegung._abbildung);
        }));
        bewegung._bild?.();
    }

    /** → true, wenn der Film zum Stück passt (gleiche Punktzahl). */
    static anbringen(mesh, film, abbildung) {
        const pos = mesh.geometry.getAttribute('position');
        if (pos.count !== film.punkte) {
            console.warn(`Meshgenesisstoffkleid: ${mesh.name} hat ${pos.count} Punkte, der Stoff ${film.punkte} — bleibt gehäutet`);
            return false;
        }
        const q = abbildung?.quaternion && !abbildung.quaternion.equals(new THREE.Quaternion()) ? abbildung.quaternion : null;
        const ecken = [], spalten = [];
        for (let j = 0; j < film.index.length; j++) if (film.index[j] >= 0) { ecken.push(j); spalten.push(film.index[j]); }
        const s = { film, ruhe: Float32Array.from(pos.array), q, stand: -1, ecken: Int32Array.from(ecken), spalten: Int32Array.from(spalten), ...Meshgenesisstoffkleid._gruppen(pos.array) };
        Object.assign(s, Meshgenesisstoffkleid._teilnetz(mesh.geometry.index?.array, s));
        mesh.userData.stoff = s;
        for (const r of mesh.userData.kollision?.u.kollisionR.value || []) r.set(0, 0);
        return true;
    }

    static abnehmen(mesh) {
        const s = mesh.userData.stoff;
        if (!s) return;
        const pos = mesh.geometry.getAttribute('position');
        pos.array.set(s.ruhe);
        pos.needsUpdate = true;
        mesh.geometry.computeVertexNormals();
        delete mesh.userData.stoff;
    }

    /**
     * Für einen Export (`Meshgenesisexportquelle`, 20.11.2026): alle Stoffstücke in die Ruhelage, bis die zurückgegebene Funktion sie wieder freigibt. `stellen` schreibt Ruhe + Versatz in die
     * Punkte — die GLB trug sonst das Stück im gerade gezeigten Bild (zauberer_23: Robe bis 265 mm neben der Ruhe, der Render-Abgleich `Kettenfilm` wies sie ab).
     */
    static ruhen(kleider) {
        const gehalten = [];
        for (const { mesh } of kleider || []) {
            const s = mesh.userData.stoff;
            if (!s) continue;
            const pos = mesh.geometry.getAttribute('position');
            pos.array.set(s.ruhe);
            pos.needsUpdate = true;
            Meshgenesisstoffkleid.normalen(mesh.geometry, s);
            s.halt = true;
            gehalten.push(s);
        }
        return () => { for (const s of gehalten) { s.halt = false; s.stand = -1; } };
    }

    /** Je Bild (nach dem Mischer): `zeit` in Sekunden der Bewegung. */
    static stellen(kleider, zeit) {
        const v = new THREE.Vector3();
        for (const { mesh } of kleider || []) {
            const s = mesh.userData.stoff;
            if (!s || s.halt || !mesh.visible || !s.ecken.length) continue;
            const f = s.film;
            const t = Math.max(0, zeit || 0) * f.fps / f.jedes;
            const a = Math.min(Math.floor(t), f.bilder - 1), b = Math.min(a + 1, f.bilder - 1), u = Math.min(Math.max(t - a, 0), 1);
            if (a + u === s.stand) continue;
            s.stand = a + u;
            const pos = mesh.geometry.getAttribute('position'), p = pos.array, d = f.daten, r = s.ruhe, ecken = s.ecken, spalten = s.spalten;
            const m = f.bewegt * 3, da = a * m, db = b * m, ka = (1 - u) * f.skala, kb = u * f.skala;
            for (let e = 0; e < ecken.length; e++) {
                const j = 3 * ecken[e], ca = da + 3 * spalten[e], cb = db + 3 * spalten[e];
                let x = d[ca] * ka + d[cb] * kb, y = d[ca + 1] * ka + d[cb + 1] * kb, z = d[ca + 2] * ka + d[cb + 2] * kb;
                if (s.q) { v.set(x, y, z).applyQuaternion(s.q); x = v.x; y = v.y; z = v.z; }
                p[j] = r[j] + x; p[j + 1] = r[j + 1] + y; p[j + 2] = r[j + 2] + z;
            }
            pos.needsUpdate = true;
            Meshgenesisstoffkleid.normalen(mesh.geometry, s);
        }
    }

    /**
     * Punkte gleicher Lage in der Ruhe (auf 1e-5 m, wie `Meshgenesisflaechennormalen.geschweisst`) → Gruppe je Punkt: die Seite mittelt dort die Normalen, damit die UV-Nähte nicht knicken.
     * Der Stoff wurde verschweißt gerechnet — gleich liegende Punkte bekommen denselben Versatz und bleiben beisammen, die Gruppen gelten in jedem Bild.
     */
    static _gruppen(p) {
        const gruppe = new Int32Array(p.length / 3), nummer = new Map();
        for (let i = 0; i < gruppe.length; i++) {
            const k = `${Math.round(p[3 * i] * 1e5)},${Math.round(p[3 * i + 1] * 1e5)},${Math.round(p[3 * i + 2] * 1e5)}`;
            let g = nummer.get(k);
            if (g === undefined) nummer.set(k, g = nummer.size);
            gruppe[i] = g;
        }
        return { gruppe, summen: new Float32Array(nummer.size * 3) };
    }

    /**
     * Was sich je Bild ändern kann: Gruppen bewegter Punkte → Dreiecke daran → deren Gruppen sind „betroffen“ (ihre Normale ändert sich); summiert werden alle Dreiecke an betroffenen Gruppen,
     * geschrieben die Normalen der Punkte betroffener Gruppen. → `{dreiecke: Uint32Array (Anfang je Dreieck im Index), punkte: Int32Array}`.
     */
    static _teilnetz(idx, s) {
        if (!idx) return { dreiecke: null, punkte: null };
        const g = s.gruppe, n = s.summen.length / 3, bewegt = new Uint8Array(n), betroffen = new Uint8Array(n);
        for (const e of s.ecken) bewegt[g[e]] = 1;
        for (let i = 0; i < idx.length; i += 3) {
            if (bewegt[g[idx[i]]] || bewegt[g[idx[i + 1]]] || bewegt[g[idx[i + 2]]]) { betroffen[g[idx[i]]] = 1; betroffen[g[idx[i + 1]]] = 1; betroffen[g[idx[i + 2]]] = 1; }
        }
        const dreiecke = [], punkte = [];
        for (let i = 0; i < idx.length; i += 3) if (betroffen[g[idx[i]]] || betroffen[g[idx[i + 1]]] || betroffen[g[idx[i + 2]]]) dreiecke.push(i);
        for (let i = 0; i < g.length; i++) if (betroffen[g[i]]) punkte.push(i);
        return { dreiecke: Uint32Array.from(dreiecke), punkte: Int32Array.from(punkte) };
    }

    /**
     * Punktnormalen wie die Seite (`computeVertexNormals`, dann über gleich liegende Punkte gemittelt — `Meshgenesisflaechennormalen.geschweisst`): Flächennormale (B−A)×(C−A), nach Fläche
     * gewichtet in die Gruppe des Punkts summiert, normiert — nur über `_teilnetz`. Auf den Feldern statt mit einem `Vector3` je Ecke: gemessen 19.11.2026 kostete die Aktualisierung zweier
     * Stücke (71.668 Punkte, 124.664 Dreiecke) mit `computeVertexNormals` 49–132 ms je Bild.
     */
    static normalen(geo, s) {
        const p = geo.getAttribute('position').array, attr = geo.getAttribute('normal'), n = attr.array, idx = geo.index?.array;
        if (!idx || !s.dreiecke) { geo.computeVertexNormals(); return; }
        const g = s.gruppe, summe = s.summen, dreiecke = s.dreiecke, punkte = s.punkte;
        summe.fill(0);
        for (let k = 0; k < dreiecke.length; k++) {
            const i = dreiecke[k], ia = idx[i], ib = idx[i + 1], ic = idx[i + 2], a = 3 * ia, b = 3 * ib, c = 3 * ic;
            const ux = p[b] - p[a], uy = p[b + 1] - p[a + 1], uz = p[b + 2] - p[a + 2];
            const wx = p[c] - p[a], wy = p[c + 1] - p[a + 1], wz = p[c + 2] - p[a + 2];
            const nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
            const qa = 3 * g[ia], qb = 3 * g[ib], qc = 3 * g[ic];      // ohne Feld je Dreieck (keine Anlage in der Schleife)
            summe[qa] += nx; summe[qa + 1] += ny; summe[qa + 2] += nz;
            summe[qb] += nx; summe[qb + 1] += ny; summe[qb + 2] += nz;
            summe[qc] += nx; summe[qc + 1] += ny; summe[qc + 2] += nz;
        }
        for (let k = 0; k < punkte.length; k++) {
            const i = punkte[k], q = 3 * g[i], x = summe[q], y = summe[q + 1], z = summe[q + 2];
            const l = Math.sqrt(x * x + y * y + z * z) || 1;
            n[3 * i] = x / l; n[3 * i + 1] = y / l; n[3 * i + 2] = z / l;
        }
        attr.needsUpdate = true;
    }
}
