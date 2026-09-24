import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';
import { Bildmittel } from './bildmittel.js';

/**
 * Umfaerbung — ein Daz-Stück (Haar, Kleidung, Requisit) in einer frei
 * gewählten Farbe, ohne dass die Struktur des Bildes verloren geht.
 *
 * WARUM (Edgar, 24.09.2026: „kann die Farbe der Haare auch angepasst werden?
 * z.B. Kin Hair? Evtl. auch die der anderen Assets?"): Daz liefert Farben als
 * Varianten — bei Kin Hair ist jede ein EIGENES Bild (`diffuse/image_file`),
 * die Farbzahl steht bei allen auf demselben Hellgrau 0,82. `material.color`
 * zu setzen reicht darum nicht: Three rechnet Farbe × Bild, ein braunes
 * Haarbild mal Pink wird Dunkelviolett.
 *
 * DIE RECHNUNG (im Fragment-Shader, hinter `color_fragment`, wo
 * `diffuseColor` schon Farbe × Bild × Punktfarbe ist):
 *
 *     Ergebnis = Wahlfarbe × Helligkeit(Texel) ÷ Helligkeit(Mittel)
 *
 * Das Bild liefert nur noch Hell und Dunkel (Strähnen, Glanz, Falten), der
 * Farbton kommt aus der Wahl. Das Mittel ist die Grundfarbe (`diffuse`, im
 * Shader gelesen — sie steht erst nach dem Bildladen fest) mal dem Mittel
 * der BELEGTEN Texel des Bildes (`Bildmittel`, einmal je Bild auf der CPU
 * gemessen, sobald es da ist — `onBeforeRender`). Bis dahin die oberste
 * Mip-Stufe (`textureLod(map, …, 16)`); die zählt die leeren Flächen des
 * UV-Atlas mit, und die Angie-Jeans stand damit fast weiß da (im Chrome,
 * 24.09.2026). Ohne die Teilung wäre Pink auf dunkelbraunem Haar fast
 * schwarz; mit ihr landet jedes Ausgangsbild im Mittel auf der gewählten
 * Farbe. Das Verhältnis ist bei 4 gedeckelt (Glanzlichter auf dunklem Bild).
 *
 * Stranghaar (`Genesis9strang`, Linien mit Punktfarben, ohne Bild): Das
 * Mittel ist der Durchschnitt der Punktfarben (`farbmittel`), NICHT mal der
 * Grundfarbe — die hebt die Auswahl-Hervorhebung an (`teilnetz_auswahl.js`),
 * und die soll sichtbar bleiben.
 *
 * Eingebaut wird EINMAL je Material (`Shaderpatch`), danach schalten nur
 * noch Uniforms: Three ruft `onBeforeCompile` je Programm nur einmal und hält
 * dessen Uniforms fest (`genesis9haut.js`, 19.09.2026) — neue Objekte sähe
 * das gemerkte Programm nie.
 */
export class Umfaerbung {

    static SCHLUESSEL = 'umfaerbung';
    static DECKEL = 4.0;
    /** Rec. 709 — linear, wie Three rechnet. */
    static LUMA = [0.2126, 0.7152, 0.0722];

    /**
     * Die Farbe eines Materials setzen (`'#rrggbb'`) oder abschalten (leer).
     * `mittel`: eigenes Mittel (Stranghaar) — sonst die Grundfarbe.
     */
    static setzen(material, hex, mittel = null) {
        if (!material) return false;
        let eingriff = Shaderpatch.eingriff(material, Umfaerbung.SCHLUESSEL);
        if (!hex && !eingriff) return false;
        if (!eingriff) eingriff = Umfaerbung._einbauen(material);
        const u = eingriff.uniforms;
        u.umfAn.value = hex ? 1 : 0;
        if (hex) u.umfFarbe.value.set(hex);
        // Die Grundfarbe liest der Shader selbst (`diffuse`): `material.color`
        // steht erst fest, wenn das Bild geladen ist (`Genesis9netz.texturen`).
        u.umfMitGrund.value = mittel ? 0 : 1;
        u.umfMittel.value.copy(mittel || new THREE.Color(1, 1, 1));
        return true;
    }

    /** Die gerade gesetzte Farbe eines Materials (`'#rrggbb'`) — oder ''. */
    static farbe(material) {
        const u = Shaderpatch.eingriff(material, Umfaerbung.SCHLUESSEL)?.uniforms;
        return u && u.umfAn.value > 0.5 ? `#${u.umfFarbe.value.getHexString()}` : '';
    }

    /**
     * Beschläge — Gruppennamen, die die Farbe des ganzen Stücks NICHT
     * bekommen. Nicht `metalness`: das G9-Base-Shirt trägt eine Metallkarte
     * (Wert 1, die Karte entscheidet je Texel) und blieb so ungefärbt, die
     * Nieten der Angie-Jeans (`SmallRivet`, `Snap`) haben gar keine
     * (im Chrome gemessen, 24.09.2026).
     */
    static BESCHLAG = /rivet|snap|button|knopf|zip|buckle|schnalle|eyelet|grommet|metal|chain|clasp|hook|stud/i;

    /**
     * Färbt die Farbe fürs ganze Stück dieses Material? Nicht Beschläge
     * und nicht die fast durchsichtigen Glanzschichten. Eine Gruppenfarbe
     * gilt trotzdem: die hat jemand für genau diese Gruppe gewählt.
     */
    static faerbbar(material) {
        if (!material) return false;
        if (Umfaerbung.BESCHLAG.test(material.userData?.gruppe || '')) return false;
        return !(material.transparent && (material.opacity ?? 1) < 0.5);
    }

    /** Alle Materialien eines Netzes (auch unter einer Gruppe) mit ihrem Netz. */
    static materialien(netz) {
        const aus = [];
        netz?.traverse?.((kind) => {
            if (!kind.material) return;
            for (const m of Array.isArray(kind.material) ? kind.material : [kind.material]) {
                if (m) aus.push({ netz: kind, material: m });
            }
        });
        return aus;
    }

    /** Die Netze eines Stücks: Genesis 9 `kennung/n`, HumanBody `daz_kennung/n`. */
    static netze(inst, kennung) {
        return Object.entries(inst?.clothMeshes || {})
            .filter(([schluessel, netz]) => netz && Umfaerbung.gehoert(schluessel, kennung))
            .map(([schluessel, netz]) => ({ schluessel, netz }));
    }

    static gehoert(schluessel, kennung) {
        const kopf = String(schluessel).split('/')[0];
        return kopf === kennung || kopf === `daz_${kennung}`;
    }

    /**
     * Die Werte eines getragenen Stücks (`farbe`, `gruppenfarben`) auf seine
     * Netze legen — nach jedem Anziehen/Neubau und bei jeder Änderung.
     */
    static stueck(inst, kennung, werte) {
        let gesetzt = 0;
        for (const { netz } of Umfaerbung.netze(inst, kennung)) {
            gesetzt += Umfaerbung.netz(netz, werte?.farbe || '', werte?.gruppenfarben || {});
        }
        return gesetzt;
    }

    static netz(netz, farbe, gruppenfarben = {}) {
        let gesetzt = 0;
        for (const { netz: kind, material } of Umfaerbung.materialien(netz)) {
            const eigene = gruppenfarben[material.userData?.gruppe] || '';
            const hex = eigene || (farbe && Umfaerbung.faerbbar(material) ? farbe : '');
            const mittel = material.vertexColors ? Umfaerbung.farbmittel(kind.geometry) : null;
            if (Umfaerbung.setzen(material, hex, mittel) && hex) gesetzt += 1;
        }
        return gesetzt;
    }

    /** Der Durchschnitt der Punktfarben (linear) — einmal je Geometrie gemessen. */
    static farbmittel(geometrie) {
        const farben = geometrie?.attributes?.color;
        if (!farben) return null;
        if (geometrie.userData.umfFarbmittel) return geometrie.userData.umfFarbmittel;
        const summe = [0, 0, 0];
        const n = farben.count;
        for (let i = 0; i < n; i++) {
            summe[0] += farben.getX(i); summe[1] += farben.getY(i); summe[2] += farben.getZ(i);
        }
        const mittel = n ? new THREE.Color(summe[0] / n, summe[1] / n, summe[2] / n)
            : new THREE.Color(1, 1, 1);
        geometrie.userData.umfFarbmittel = mittel;
        return mittel;
    }

    static _einbauen(material) {
        const uniforms = {
            umfAn: { value: 0 },
            umfFarbe: { value: new THREE.Color(1, 1, 1) },
            umfMittel: { value: new THREE.Color(1, 1, 1) },
            umfMitGrund: { value: 1 },
            umfBild: { value: new THREE.Color(1, 1, 1) },
            umfBildDa: { value: 0 },
        };
        const eingriff = (shader) => {
            Object.assign(shader.uniforms, uniforms);
            shader.fragmentShader = Umfaerbung.fragment(shader.fragmentShader);
        };
        eingriff.uniforms = uniforms;
        Shaderpatch.anhaengen(material, Umfaerbung.SCHLUESSEL, eingriff);
        // Das Bild kommt oft erst nach dem Färben (`Genesis9netz.texturen`) —
        // gemessen wird beim Zeichnen, einmal je Bild (`Bildmittel` merkt es).
        const vorher = material.onBeforeRender;
        material.onBeforeRender = function (...args) {
            if (typeof vorher === 'function') vorher.apply(this, args);
            Umfaerbung.bildNachziehen(this, eingriff);
        };
        return eingriff;
    }

    /** Das Mittel des aktuellen Bildes in die Uniforms — sobald es da ist. */
    static bildNachziehen(material, eingriff) {
        const uniforms = eingriff.uniforms;
        if (uniforms.umfAn.value < 0.5) return;
        const bild = material.map?.image || null;
        if (eingriff.bild === bild) return;
        // Nicht messbar (kein Canvas): einmal versucht, dann bleibt das GPU-Mittel.
        const mittel = Bildmittel.von(material.map);
        eingriff.bild = bild;
        uniforms.umfBildDa.value = mittel ? 1 : 0;
        if (mittel) uniforms.umfBild.value.setRGB(mittel[0], mittel[1], mittel[2]);
    }

    /** Den Fragment-Shader umschreiben — rein über Text, in Node prüfbar. */
    static fragment(quelle) {
        const [r, g, b] = Umfaerbung.LUMA;
        const luma = `vec3(${r}, ${g}, ${b})`;
        const kopf = 'uniform float umfAn;\nuniform vec3 umfFarbe;\nuniform vec3 umfMittel;\n'
            + 'uniform float umfMitGrund;\nuniform vec3 umfBild;\nuniform float umfBildDa;\n';
        const rechnung = `
if (umfAn > 0.5) {
    vec3 umfSchnitt = mix(vec3(1.0), diffuse, umfMitGrund) * umfMittel;
    #ifdef USE_MAP
        umfSchnitt *= umfBildDa > 0.5 ? umfBild : textureLod(map, vec2(0.5), 16.0).rgb;
    #endif
    float umfH = dot(diffuseColor.rgb, ${luma});
    float umfM = max(dot(umfSchnitt, ${luma}), 1e-4);
    diffuseColor.rgb = umfFarbe * min(umfH / umfM, ${Umfaerbung.DECKEL.toFixed(1)});
}`;
        return quelle
            .replace('#include <common>', `#include <common>\n${kopf}`)
            .replace('#include <color_fragment>', `#include <color_fragment>${rechnung}`);
    }
}
