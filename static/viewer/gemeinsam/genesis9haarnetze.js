import * as THREE from 'three';
import { Eigenhaut } from './eigenhaut.js';
import { Protokoll } from './protokoll.js';
import { Skelettereignis } from './skelettereignis.js';

/**
 * Genesis9haarnetze — Haar und Bart der Haar-Engine an einem gespeicherten Genesis-Modell (23.11.2026, Server `Modellhaarnetze`).
 *
 * Edgar: „beim Speichern sollen zumindest Haare, Bart, Haut mitgehen“, zum Vorschlag, die Strähnen der Engine statt des Bibliotheksstücks zu speichern: „mach alles“. „Als Modell
 * speichern“ von Mesh-Genesis und Foto-Genesis legt das Anzeigenetz, das die Ergebniskarte zeigt, neben das Modell und schreibt `figur.haarnetze = {knochen, ruhezentren,
 * stuecke: [{id, name, art, adresse}]}`. Hier wird es mit DEMSELBEN Code wie die Abspielleiste der Testseite an das Skelett gebunden (`Meshgenesisbewegungskleid.binden`: Ruhelage,
 * Gewichte je Punkt, Knochen über ihre Namen, Materialien mit Deckkraftbild und Punktfarben) — als Nebenwirkung des Imports nach jedem neuen Skelett einer Figur (`Skelettereignis`:
 * erster Bau, Reglerzug, Stufenwechsel), auf jeder Seite mit einer Genesis-Figur (Charakter, Studio, Theatre).
 *
 * Rahmen: das Netz liegt in der Ruhelage der Figur, auf der die Engine gebaut hat (Ruhegelenke `ruhezentren`). Ein Unterschied zur gebauten Figur wird starr ausgeglichen wie auf der
 * Testseite (`Meshgenesisausrichtung.starr`), gemessen an den Ruhelagen der Knochen aus `boneInverses` (im Rahmen der Figurgruppe, `Knochenbau.ruhelagen`) — die Weltlagen, die die
 * Testseite nimmt (`Meshgenesisbewegungsfigur.knochenlagen`), stimmen hier nicht, sobald die Figur verschoben steht oder gerade spielt. Formregler, die den Kopf verändern, zieht das
 * Haar nicht nach (es ist kein Stück der Garderobe mit Morphen).
 *
 * Die Netze heißen `haarnetz_<id>`, tragen `userData.art = 'haar'` und `userData.haarnetz`; „Kleider aus“ blendet sie mit aus (`Kleidersichtbarkeit`), der Export nimmt sie wie
 * jedes sichtbare Netz der Figurgruppe (`Modellexportinhalt.objekte`). Die Module der Testseite kommen erst mit dem ersten Modell, das Haarnetze trägt (dynamischer Import).
 */
export class Genesis9haarnetze {

    static _je = new WeakMap();
    static WINKEL = 1e-6;
    static WEG_M = 1e-6;

    /** Netze der Figur nach `inst.haarnetze` anlegen, an das frische Skelett binden oder abnehmen. */
    static async anbringen(inst) {
        if (inst?.quelle !== 'genesis9') return;
        const stand = Genesis9haarnetze._je.get(inst) || { lauf: 0, netze: [] };
        Genesis9haarnetze._je.set(inst, stand);
        const daten = inst.haarnetze;
        const stuecke = Array.isArray(daten?.stuecke) ? daten.stuecke : [];
        const lauf = ++stand.lauf;
        const skelett = inst.skelett;
        if (!stuecke.length || !skelett?.skeleton) {
            Genesis9haarnetze._abnehmen(stand);
            return;
        }
        const [{ Meshgenesisflaechennetz }, { Meshgenesisbewegungskleid }, { Meshgenesisausrichtung }] = await Promise.all([
            import('../meshgenesis/meshgenesisflaechennetz.js'), import('../meshgenesis/meshgenesisbewegungskleid.js'), import('../meshgenesis/meshgenesisausrichtung.js')]);
        const netze = await Promise.all(stuecke.map(st => Meshgenesisflaechennetz.holen(null, st.adresse).catch((fehler) => {
            Protokoll.warnung('Genesis9haarnetze', `${st.name || st.id}: ${fehler.message}`);
            return null;
        })));
        if (lauf !== stand.lauf || inst.skelett !== skelett) return;          // überholt: ein neueres Skelett bindet selbst
        const abbildung = Genesis9haarnetze._rahmen(skelett, daten.knochen || [], daten.ruhezentren || [], Meshgenesisausrichtung);
        const spalte = Eigenhaut.spaltenNummern(daten.knochen || [], skelett);
        if (stand.spalte && spalte && Genesis9haarnetze._gleich(stand, spalte, abbildung, netze)) {
            for (const n of stand.netze) Eigenhaut.einhaengen(inst.group, n.mesh, skelett);     // dieselben Knochen am selben Platz: nur umbinden, keine neue Geometrie
            return;
        }
        Genesis9haarnetze._abnehmen(stand);
        stand.spalte = spalte; stand.abbildung = abbildung;
        stuecke.forEach((st, i) => {
            const mesh = netze[i] && Meshgenesisbewegungskleid.binden(netze[i], skelett, daten.knochen, abbildung);
            if (!mesh) return;
            mesh.name = `haarnetz_${st.id}`;
            mesh.userData.art = 'haar';
            mesh.userData.haarnetz = st.id;
            mesh.visible = inst.kleiderSichtbar !== false;
            Eigenhaut.einhaengen(inst.group, mesh, skelett);
            stand.netze.push({ mesh, netz: netze[i] });
        });
        Protokoll.debug('Genesis9haarnetze', `${inst.figur}: ${stand.netze.length} von ${stuecke.length} Haarnetzen gebunden${abbildung ? ' (Rahmen ausgeglichen)' : ''}`);
    }

    /** Rahmen der Engine-Figur → Rahmen dieser Figur, oder null, wenn sie aufeinander liegen (wie `Meshgenesisbewegungsfigur.rahmen`, Lagen aus `boneInverses`). */
    static _rahmen(skelett, knochen, ruhezentren, Meshgenesisausrichtung) {
        const sk = skelett.skeleton, je = new Map(), m = new THREE.Matrix4(), p = new THREE.Vector3();
        sk.bones.forEach((b, i) => { if (!je.has(b.name) && sk.boneInverses[i]) je.set(b.name, p.setFromMatrixPosition(m.copy(sk.boneInverses[i]).invert()).toArray()); });
        const a = [], b = [];
        knochen.forEach((name, i) => { if (je.has(name) && ruhezentren[i]) { a.push(ruhezentren[i]); b.push(je.get(name)); } });
        if (a.length < 3) return null;
        const r = Meshgenesisausrichtung.starr(a, b);
        const verschoben = r.verschiebung.length() > 1e-4 || 2 * Math.acos(Math.min(1, Math.abs(r.quaternion.w))) > 1e-3;
        return verschoben ? r : null;
    }

    /** Dieselben Netze, dieselben Knochenspalten, derselbe Rahmen? */
    static _gleich(stand, spalte, abbildung, netze) {
        if (stand.netze.length !== netze.filter(Boolean).length || stand.netze.some((n, i) => n.netz !== netze.filter(Boolean)[i])) return false;
        if (stand.spalte.length !== spalte.length || stand.spalte.some((s, i) => s !== spalte[i])) return false;
        const a = stand.abbildung, b = abbildung;
        if (!a || !b) return !a && !b;
        return a.verschiebung.distanceTo(b.verschiebung) < Genesis9haarnetze.WEG_M && a.quaternion.angleTo(b.quaternion) < Genesis9haarnetze.WINKEL;
    }

    static _abnehmen(stand) {
        for (const { mesh } of stand.netze) {
            mesh.parent?.remove(mesh);
            mesh.geometry.dispose();          // die Materialien gehören dem Netz (`Meshgenesisflaechennetz.materialien`, `userData.gemeinsam`)
        }
        stand.netze = [];
        stand.spalte = null; stand.abbildung = null;
    }
}

if (typeof document !== 'undefined') {
    Skelettereignis.hoeren(({ inst }) => {
        Genesis9haarnetze.anbringen(inst).catch(fehler => Protokoll.fehler('Genesis9haarnetze', 'Haar und Bart nicht angelegt', fehler));
    });
}
