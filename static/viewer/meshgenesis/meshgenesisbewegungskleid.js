/**
 * Meshgenesisbewegungskleid — ein Stück der Ergebnisfigur (Anzeigenetz `Meshgenesisflaechennetz`: Ruhelage, Knochen und Gewichte je Punkt) an das Skelett der Genesis-Figur binden, damit es der
 * Standardanimation folgt (22.10.2026, `Meshgenesisfigurbewegung`).
 *
 * Still gezeigt wird ein Stück auf der CPU mit den Matrizen der KI-Haltung gehäutet (`Meshgenesistestnetzbau`). Für die Bewegung braucht es ein `SkinnedMesh` an den Knochen der Figur, die three.js
 * je Bild stellt: dieselben Gewichte, die Knochen über ihre NAMEN aufgelöst (die Gewichte zählen in der Reihenfolge der `kinematik.json` der Figur, das Skelett in der des Bauplans — wie `Eigenhaut`),
 * höchstens vier je Punkt (die stärksten, neu auf Summe 1).
 *
 * Die Ruhelage des Stücks und die des Skeletts liegen im selben Rahmen, wenn beide aus denselben Reglern gebaut sind; `abbildung` (`{quaternion, verschiebung}`, `Meshgenesisausrichtung.starr` von den
 * Ruhegelenken der Kinematik auf die Knochen der gebauten Figur) nimmt einen Unterschied der Rahmen heraus — gemessen wird er von `Meshgenesisfigurbewegung` und steht in deren Text.
 */
import * as THREE from 'three';
import { Eigenhaut } from '../gemeinsam/eigenhaut.js';
import { Meshgenesishaarschwung } from './meshgenesishaarschwung.js';
import { Meshgenesiskollision } from './meshgenesiskollision.js';
import { Meshgenesisstoffkleid } from './meshgenesisstoffkleid.js';
import { Meshgenesishaarfilm } from './meshgenesishaarfilm.js';
import { Meshgenesiskartenhaut } from './meshgenesiskartenhaut.js';
import { Meshgenesisflaechen } from './meshgenesisflaechen.js';
import { Meshgenesisflaechennormalen } from './meshgenesisflaechennormalen.js';

export class Meshgenesisbewegungskleid {
    /** Die Ruhelage eines Netzes im Rahmen der Figur (Float32Array, V·3). */
    static ruhe(netz, abbildung) {
        const aus = new Float32Array(netz.ruhe);
        if (!abbildung) return aus;
        const v = new THREE.Vector3();
        for (let i = 0; i < aus.length; i += 3) {
            v.set(aus[i], aus[i + 1], aus[i + 2]).applyQuaternion(abbildung.quaternion).add(abbildung.verschiebung);
            aus[i] = v.x; aus[i + 1] = v.y; aus[i + 2] = v.z;
        }
        return aus;
    }

    /**
     * @param netz Anzeigenetz mit `ruhe`, `knochen`, `gewicht`, `kopf.haut` @param skelett `{skeleton, bones}` der Genesis-Figur @param namen Knochennamen in der Reihenfolge der Gewichte
     * @param abbildung Rahmen der Kinematik → Rahmen der Figur (oder null) @returns {THREE.SkinnedMesh|null} null, wenn ein Knochen fehlt (dann bleibt das Stück weg — nie halb gebunden)
     *
     * 22.11.2026 (Edgar zur Ladezeit des Zauberers, „2 OK“: die Animation häutete Haar und Bart beim Start noch auf der CPU): Bis dahin entstand die Geometrie über
     * `Meshgenesistestnetzbau.mesh` mit Einheitsmatrizen — das häutete jedes Stück einmal ganz auf der CPU (Punkte und Normalen), die Lage wurde danach ohnehin ersetzt. Jetzt direkt:
     * dieselbe Lage, dieselben Gruppen und Materialien, derselbe Index (`Meshgenesiskartenhaut.index`: der des Pakets, wo er schon nach Material liegt), dieselben Gewichte (`_vier`, Knochen als
     * Uint16 statt Float32). Ohne Abbildung sind Lage und Normalen Sichten aufs Paket (`userData.lageGeteilt`; wer sie schreibt, macht sie erst zu eigenen — `Meshgenesisstoffkleid.anbringen`).
     */
    static binden(netz, skelett, namen, abbildung) {
        if (!netz?.ruhe || !netz.knochen || !netz.gewicht || !skelett?.skeleton) return null;
        const spalte = Eigenhaut.spaltenNummern(namen, skelett);
        if (!spalte) return null;
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(abbildung ? Meshgenesisbewegungskleid.ruhe(netz, abbildung) : netz.ruhe, 3));
        geo.setAttribute('uv', netz.uvAttribut);
        netz.farbe ??= Meshgenesisflaechen.farben(netz.kopf, netz.dreiecke, netz.etikett);
        geo.setAttribute('color', netz.farbe);
        const materialien = netz.materialien();
        geo.setIndex(new THREE.BufferAttribute(Meshgenesiskartenhaut.index(netz, materialien.length, (ab, n, m) => geo.addGroup(ab, n, m)), 1));
        Meshgenesisbewegungskleid._normalen(geo, netz, abbildung);
        const { index, gewicht } = Meshgenesisbewegungskleid._vier(netz, spalte);
        geo.setAttribute('skinIndex', new THREE.BufferAttribute(index, 4));
        geo.setAttribute('skinWeight', new THREE.BufferAttribute(gewicht, 4, !(gewicht instanceof Float32Array)));
        geo.userData.gemeinsam = false;         // gehört der Bewegung, nicht dem Feld: `Meshgenesisfigurbewegung.verwerfen` gibt sie frei
        geo.userData.lageGeteilt = !abbildung;
        for (const m of materialien) m.userData.gemeinsam = true;
        const mesh = new THREE.SkinnedMesh(geo, materialien);
        mesh.frustumCulled = false;
        return mesh;
    }

    /**
     * Normalen wie bis zum 22.11.2026 (mitgelieferte auf Länge 1 gebracht, sonst `Meshgenesisflaechennormalen.geschweisst` an der Ruhelage; mit der Abbildung gedreht). Ohne Abbildung die
     * mitgelieferten Int8-Werte selbst (die Karte liest c / 127; der Shader normiert nach dem Häuten — dieselbe Richtung).
     */
    static _normalen(geo, netz, abbildung) {
        const roh = netz.normalenRoh?.length === netz.ruhe.length ? netz.normalenRoh : null;
        if (roh && !abbildung) {
            geo.setAttribute('normal', new THREE.BufferAttribute(roh, 3, true));
            return;
        }
        let n;
        if (roh) {
            n = new Float32Array(roh.length);
            for (let i = 0; i < roh.length; i += 3) {
                const x = roh[i] / 127, y = roh[i + 1] / 127, z = roh[i + 2] / 127, l = Math.hypot(x, y, z);
                if (l > 1e-12) { n[i] = x / l; n[i + 1] = y / l; n[i + 2] = z / l; }
            }
        } else {
            const ruhe = new THREE.BufferGeometry();
            ruhe.setAttribute('position', new THREE.BufferAttribute(netz.ruhe, 3));
            ruhe.setIndex(geo.index);
            Meshgenesisflaechennormalen.geschweisst(ruhe);
            n = ruhe.getAttribute('normal').array;
        }
        if (abbildung) {
            const v = new THREE.Vector3();
            for (let i = 0; i < n.length; i += 3) {
                v.set(n[i], n[i + 1], n[i + 2]).applyQuaternion(abbildung.quaternion);
                n[i] = v.x; n[i + 1] = v.y; n[i + 2] = v.z;
            }
        }
        geo.setAttribute('normal', new THREE.BufferAttribute(n, 3));
    }

    /**
     * Die vier stärksten Knochen je Punkt (Gewichte ×255 im Netz), auf Summe 1 — bei Gleichstand in der Reihenfolge des Netzes. Ohne Gewicht am ersten Knochen (der Wurzel): der Punkt bleibt
     * in Ruhe am Körper, statt zum Ursprung zu fallen. 22.11.2026: Einfügen in feste Felder statt einer Liste aus Paaren je Punkt (Haar 2,19 Mio. Punkte: 8,8 Mio. Felder und eine Sortierung je
     * Punkt) — dieselbe Auswahl, dieselben Werte.
     *
     * Vier Knochen je Punkt und jede Summe genau 255 (Zauberer: alle Stücke außer der Robe): die Gewichte des Pakets selbst, normiert Uint8 (w / 255 = w / Summe — dieselben Werte, nur in der
     * Reihenfolge des Netzes statt nach Stärke; `Koerpertiefe` und `Meshgenesiskollision.stand` teilen normierte Gewichte), die Knochen des Pakets, wenn das Skelett sie in derselben Folge
     * führt (Zauberer: Spalte j = Knochen j), sonst umgeschrieben. Im Tab 22.11.2026: `_vier` am Haar 212–280 ms, so 0 ms und 52 MB weniger (Bart 36 MB).
     */
    static _vier(netz, spalte) {
        const k = netz.kopf.haut, kn = netz.knochen, g = netz.gewicht;
        const v = netz.ruhe.length / 3;
        if (k === 4 && Meshgenesisbewegungskleid._summe255(g, v)) return { index: Meshgenesisbewegungskleid._knochen(kn, spalte), gewicht: g };
        const index = new Uint16Array(v * 4);
        const gewicht = new Float32Array(v * 4);
        const w = new Int32Array(k), j = new Int32Array(k);
        for (let i = 0; i < v; i++) {
            let n = 0;
            for (let h = 0; h < k; h++) {
                const wert = g[i * k + h];
                if (!wert) continue;
                let p = n++;
                while (p > 0 && w[p - 1] < wert) { w[p] = w[p - 1]; j[p] = j[p - 1]; p--; }      // stabil absteigend wie `sort((a, b) => b[0] - a[0])`
                w[p] = wert;
                j[p] = spalte[kn[i * k + h]] ?? 0;
            }
            if (!n) {
                gewicht[i * 4] = 1;
                continue;
            }
            const m = Math.min(4, n);
            let summe = 0;
            for (let h = 0; h < m; h++) summe += w[h];
            for (let h = 0; h < m; h++) {
                index[i * 4 + h] = j[h];
                gewicht[i * 4 + h] = w[h] / summe;
            }
        }
        return { index, gewicht };
    }

    static _summe255(g, v) {
        for (let i = 0; i < v; i++) if (g[4 * i] + g[4 * i + 1] + g[4 * i + 2] + g[4 * i + 3] !== 255) return false;
        return true;
    }

    /** Knochen des Pakets → Knochen des Skeletts (`spalte`; ein Knochen jenseits der Spalten → 0 wie in `_vier`): das Paket selbst, wenn das nichts ändert. */
    static _knochen(kn, spalte) {
        let gleich = true;
        for (let j = 0; gleich && j < spalte.length; j++) gleich = spalte[j] === j;
        for (let i = 0; gleich && i < kn.length; i++) gleich = kn[i] < spalte.length;
        if (gleich) return kn;
        const aus = new Uint16Array(kn.length);
        for (let i = 0; i < kn.length; i++) aus[i] = spalte[kn[i]] ?? 0;
        return aus;
    }

    /**
     * Alle Stücke der Quelle an das Skelett der bewegten Figur binden (`bewegung`: `Meshgenesisfigurbewegung`; bis 19.11.2026 dort `_kleiderBinden`): je Stück das `SkinnedMesh`, der Kapselschub
     * aus fremden Gliedern (31.10.2026 nachts), die Bewegung je Locke (16.11.2026) und der Stoff der gewählten Bewegung, wo einer gerechnet ist (`Meshgenesisstoffkleid`, 19.11.2026).
     */
    static alleBinden(bewegung) {
        for (const k of bewegung.kleider) {
            k.mesh.parent?.remove(k.mesh);
            k.mesh.geometry.dispose();
        }
        bewegung.kleider = [];
        const q = bewegung._q;
        for (const st of q?.stuecke || []) {
            const mesh = Meshgenesisbewegungskleid.binden(st.netz, bewegung.modell.skelett, q.knochen, bewegung._abbildung);
            if (!mesh) continue;
            mesh.userData.art = st.art; mesh.name = `ki_${st.id}`;      // Name = Schlüssel in `hautStuecke` (Exportleiste: `Exportleistefigur.hautDeckt`, Knotenname in GLB und .blend)
            mesh.visible = bewegung._kleiderAn;
            Eigenhaut.einhaengen(bewegung.modell.group, mesh, bewegung.modell.skelett);
            Meshgenesiskollision.anbringen(mesh, q.kapseln, bewegung.modell.skelett, bewegung._abbildung, q.knochen);
            Meshgenesishaarschwung.anbringen(mesh, st.netz, bewegung._abbildung);
            bewegung.kleider.push({ mesh, art: st.art, adresse: st.adresse });
        }
        bewegung._kleiderWurzel = bewegung.modell.skelett?.rootBone || null;
        Meshgenesisstoffkleid.anbringenAlle(bewegung);
        Meshgenesishaarfilm.anbringenAlle(bewegung);              // Haar und Bart aus der Kette (Schritt „haar“, 20.11.2026)
    }
}
