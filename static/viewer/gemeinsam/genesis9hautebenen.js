import * as THREE from 'three';
import { Genesis9haut } from './genesis9haut.js';
import { Genesis9hautfalten } from './genesis9hautfalten.js';
import { Genesis9hautkarten } from './genesis9hautkarten.js';
import { Genesis9ergrauen } from './genesis9ergrauen.js';
import { Genesis9mimikfalten } from './genesis9mimikfalten.js';
import { Genesis9hautebenenwerte } from './genesis9hautebenenwerte.js';
import { Genesis9texturen } from './genesis9texturen.js';

/**
 * Genesis9hautebenen — Hautton, Rötung, Sommersprossen, Altersflecken, Muskel- und Fettzeichnung und graue Haare einer Genesis-9-Figur (17.10.2026).
 *
 * Edgar, 17.10.2026: „Baue noch Hautebenen: Hautton, Sommersprossen, Altersflecken, graue Haare, Muskel- und Fettzeichnung. Mach einen Vorschlag, wie die in den Shader
 * kommen" — und danach „wo sind die Regler Haut?". Keine Morphs: die Werte liegen je Figur in `inst.hautebenen = {name: Prozent}` (geht mit „Modell speichern" mit,
 * wie `teilmaterial` und `hautmischung`), im Shader sind sie Uniforms (`genesis9hautebenenglsl.js`) — ein Reglerzug baut weder Körper noch Programm.
 *
 * KARTEN vom Server (`Genesis9hautkarten`, je Geschlecht beim ersten Gebrauch im Hintergrund gebaut): die Gebiete für Sommersprossen und Altersflecken und die Muskel-/
 * Fettnormalen. Ohne Karten bleibt der Hautton wirksam; Punkte und Zeichnung warten.
 *
 * AN DAS ALTER GEKOPPELT (Setzung, Tabelle 5 und 7 in `genesis9-alter.md`): Altersflecken und graue Haare folgen `alter:gesamt`/`alter:jahre` (`Genesis9hautfalten.alter`),
 * der Regler addiert nichts, er hebt nur an (Maximum aus Regler und Alter). Altersflecken beginnen bei Alterswert 0,2 (rund 38 Jahre) und stehen bei 0,8 voll; graue Haare ab
 * 0,23 (40 Jahre) bis 1 (90 Jahre).
 *
 * Ein Material bekommt den Zusatz erst, wenn ein Wert von null abweicht — eine Figur ohne Hautebenen läuft mit dem Shader von vorher.
 *
 * ZWEITE WELLE (18.10.2026, Edgar: „möglichst viele Regler, damit ich möglichst komplexe Haut erstellen kann"): 18 weitere Regler (`Genesis9hautebenenwerte.FELDER`), Shader in
 * `Genesis9hautrauschenGLSL`. „Altersfalten" hebt die Faltenschicht des Alters an (`Genesis9hautfalten.anwenden`, Maximum aus Regler und Alter).
 */
export class Genesis9hautebenen {

    /** Die Regler (Titel, Bereich, Hilfe) und die Rechnung Prozent → Anteile stehen in `Genesis9hautebenenwerte` (ohne Three.js, in Node prüfbar). */
    static FELDER = Genesis9hautebenenwerte.FELDER;

    static HAUT = /^(Head|Body|Arms|Legs)$/;
    /** Steigung der Zeichnung bei Gewicht 1 (die Karte trägt Steigungen bis 0,3; wie `Genesis9hautfalten.STAERKE`, nach Augenmaß). */
    static STAERKE = 3.0;

    // ------------------------------------------------------------- Werte

    static standard(name) {
        return Genesis9hautebenenwerte.standard(name);
    }

    static wert(inst, name) {
        return Genesis9hautebenenwerte.wert(inst, name);
    }

    /** Die wirksamen Werte (−1…1 bzw. 0…1) samt der Kopplung ans Alter (`Genesis9hautebenenwerte.wirksam`). */
    static wirksam(inst) {
        return Genesis9hautebenenwerte.wirksam(inst, Genesis9hautfalten.alter(inst));
    }

    /** Die Materialien der Haut (Kopf, Körper, Arme, Beine) mit ihrer UDIM-Kachel. */
    static materialien(inst) {
        const material = inst.bodyMesh?.material;
        return (Array.isArray(material) ? material : [material])
            .filter(m => m?.userData?.kachel != null && Genesis9hautebenen.HAUT.test(m.userData.gruppe || ''));
    }

    // -------------------------------------------------------------- Shader

    /** Den Zusatz ankündigen (einmal je Material; `zeichnung` kommt dazu, bleibt dann). Liefert die Uniforms. */
    static einrichten(material, mitZeichnung, mitMimik = false) {
        const zusatz = Genesis9haut._zusatz(material);
        let neu = false;
        if (!zusatz.hautebenen) {
            zusatz.hautebenen = {
                zeichnung: false, gebietBild: false, zeichnungBild: false, mimik: false, mimikBild: false, mimikKanaele: [],
                uniforms: {
                    uHtTon: { value: 0 }, uHtRoetung: { value: 0 }, uHtSommer: { value: 0 }, uHtAlter: { value: 0 }, uHtGroesseS: { value: 1 },
                    uHtMeterUV: { value: 1 }, uHtGebietAn: { value: 0 }, uHtGebiet: { value: Genesis9haut.platzhalter(0, 0, 0, THREE.NoColorSpace, 0) },
                    // Zweite Welle (18.10.2026, `Genesis9hautrauschenGLSL`): je vier Werte in einem vec4.
                    uHtF1: { value: new THREE.Vector4() }, uHtF2: { value: new THREE.Vector4() }, uHtF3: { value: new THREE.Vector4(1, 0, 1, 0) },
                    uHtF4: { value: new THREE.Vector4(0, 0, 0, 0.8) }, uHtF5: { value: new THREE.Vector4(0, 0, 1.7, 0) }, uHtB1: { value: new THREE.Vector4() },
                },
            };
            neu = true;
        }
        const h = zusatz.hautebenen;
        if (mitZeichnung && !h.zeichnung) {
            h.zeichnung = true;
            Object.assign(h.uniforms, {
                uHtMuskel: { value: 0 }, uHtFett: { value: 0 }, uHtZStaerke: { value: Genesis9hautebenen.STAERKE },
                uHtZeichnung: { value: Genesis9haut.platzhalter(128, 128, 128, THREE.NoColorSpace, 128) },
            });
            // Ohne Grundnormale kennt der Shader keinen Tangentenraum: eine flache einsetzen (wie bei den Falten).
            if (!material.normalMap) material.normalMap = Genesis9haut.platzhalter(128, 128, 255);
            neu = true;
        }
        if (mitMimik && !h.mimik) {                       // Mimikfalten (`Genesis9mimikfalten`): nur am Kopf, bleibt dann
            h.mimik = true;
            Object.assign(h.uniforms, Genesis9mimikfalten.uniforms());
            if (!material.normalMap) material.normalMap = Genesis9haut.platzhalter(128, 128, 255);
            neu = true;
        }
        if (neu) {
            Genesis9haut._einhaengen(material);
            material.needsUpdate = true;
        }
        return h;
    }

    /**
     * STREUFARBE am Hautton (UMA-Palette, `genesis9-alter.md` Tabelle 6): dunklere Haut streut das Licht tiefer rot (UMA: #6A1C14 beim dunkelsten Ton), hellere heller und rosa (#FF9C91).
     * Das Durchlicht der Haut (`Genesis9haut.durchlicht`, Daz' Transmitted Color) wird je nach Ton von der Farbe des Presets zu diesen Enden gemischt; die Preset-Farbe bleibt am Material
     * gemerkt (`farbeGrund`). Das Farbobjekt ist dasselbe, das der Shader als Uniform hält — kein Neubau.
     */
    static streufarbe(material, ton) {
        const d = material.userData.genesis9?.durchlicht;
        if (!d?.farbe) return;
        d.farbeGrund ??= d.farbe.clone();
        const ziel = new THREE.Color().setRGB(...(ton > 0 ? Genesis9hautebenen.STREU_DUNKEL : Genesis9hautebenen.STREU_HELL), THREE.SRGBColorSpace);
        d.farbe.copy(d.farbeGrund).lerp(ziel, Math.min(1, Math.abs(ton)));
    }

    static STREU_DUNKEL = [0x6A / 255, 0x1C / 255, 0x14 / 255];
    static STREU_HELL = [1, 0x9C / 255, 0x91 / 255];

    // -------------------------------------------------------------- Anwenden

    /**
     * Die Werte der Figur auf die Materialien legen und die Karten holen, die gebraucht werden. Billig im Zug (Uniforms); die Karten kommen einmal je Material.
     * `lauf` verwirft eine überholte Antwort.
     */
    static async anwenden(inst) {
        const w = Genesis9hautebenen.wirksam(inst);
        const mitFarbe = Genesis9hautebenenwerte.mitFarbe(w) || Genesis9hautebenenwerte.mitBeulen(w);
        const mitZeichnung = w.muskel > 0 || w.fett > 0;
        const mitMimik = Genesis9hautebenenwerte.mimikAktiv(inst, w.mimik);
        const lauf = inst._hautebenenlauf = (inst._hautebenenlauf || 0) + 1;
        const betroffen = [];
        const kopf = [];
        const koerper = Genesis9hautebenen.koerpermass(inst);
        for (const m of Genesis9hautebenen.materialien(inst)) {
            Genesis9hautebenen.streufarbe(m, w.ton);           // auch zurück auf die Preset-Farbe, wenn der Ton wieder 0 ist
            const mimikHier = mitMimik && m.userData.gruppe === Genesis9mimikfalten.GRUPPE;
            if (!mitFarbe && !mitZeichnung && !mimikHier && !m.userData.genesis9?.hautebenen) continue;
            const h = Genesis9hautebenen.einrichten(m, mitZeichnung, mimikHier);
            const u = h.uniforms;
            u.uHtTon.value = w.ton; u.uHtRoetung.value = w.roetung; u.uHtSommer.value = w.sommer; u.uHtAlter.value = w.altersflecken; u.uHtGroesseS.value = w.groesse;
            Genesis9hautebenen._zweiteWelle(u, w, Genesis9hautebenen.TEIL[m.userData.gruppe] ?? 1, koerper);
            if (u.uHtMuskel) { u.uHtMuskel.value = w.muskel; u.uHtFett.value = w.fett; }
            if (u.uHtMimikW) kopf.push(m);
            betroffen.push(m);
        }
        Genesis9hautebenen._mimikgewichte(inst, kopf, w.mimik, mitMimik);
        Genesis9ergrauen.anwenden(inst, w.ergrauen);
        const geschlecht = Genesis9hautfalten.geschlecht(inst);
        const jobs = [];
        // Die Gebietskarte trägt auch `meter_je_uv` — die Punkte (Muttermale, Pickel, Aknenarben) brauchen es für ihre Größe in Millimetern.
        if (Genesis9hautebenenwerte.mitGebiet(w) || w.muttermale > 0 || w.pickel > 0) jobs.push(Genesis9hautebenen._karten(inst, lauf, betroffen, 'gebiet', geschlecht));
        if (mitZeichnung) jobs.push(Genesis9hautebenen._karten(inst, lauf, betroffen, 'zeichnung', geschlecht));
        if (mitMimik) jobs.push(Genesis9hautebenen._karten(inst, lauf, kopf, 'mimik', 'female').then(() => Genesis9hautebenen._mimikgewichte(inst, kopf, w.mimik, mitMimik)));
        await Promise.all(jobs);
    }

    /** Materialgruppe → Teil im Shader (`Genesis9hautrauschenGLSL.GEBIET`). */
    static TEIL = { Head: 0, Body: 1, Arms: 2, Legs: 3 };

    /** Höhe und Boden des Körpers in Ruhelage (Objektraum, aus der Geometrie) — für Gebiete nach Körperhöhe (Cellulite, Pickel an Brust und Rücken). */
    static koerpermass(inst) {
        const geometrie = inst.bodyMesh?.geometry;
        if (!geometrie?.attributes?.position) return { hoehe: 1.7, boden: 0 };
        if (!geometrie.boundingBox) geometrie.computeBoundingBox();
        const { min, max } = geometrie.boundingBox;
        return { hoehe: Math.max(0.5, max.y - min.y), boden: min.y };
    }

    /** Die Werte der zweiten Welle in die vier-Werte-Uniforms (Belegung: `Genesis9hautrauschenGLSL`). */
    static _zweiteWelle(u, w, teil, koerper) {
        u.uHtF1.value.set(w.farbton, w.oliv, w.saettigung, w.helligkeit);
        u.uHtF2.value.set(w.struktur, w.teint, w.pigment, w.vitiligo);
        u.uHtF3.value.set(w.flecken, w.muttermale, w.muttermaleGroesse, w.pickel);
        u.uHtF4.value.set(w.adern, w.wangen, w.augenringe, w.dichte);
        u.uHtF5.value.set(w.weite, teil, koerper.hoehe, koerper.boden);
        u.uHtB1.value.set(w.cellulite, w.narben, w.pickel, 0);
    }

    /** Die Gewichte der Mimikfalten auf die Kopfmaterialien — ohne Mimik (oder ohne Ausdruck) alle 0, dann ist die Schleife im Shader leer. */
    static _mimikgewichte(inst, kopf, regler, aktiv) {
        for (const m of kopf) {
            const h = m.userData.genesis9.hautebenen;
            Genesis9hautebenenwerte.mimikGewichte(inst, aktiv ? h.mimikKanaele : [], h.uniforms.uHtMimikW.value);
            h.uniforms.uHtMimikStaerke.value = aktiv ? regler * Genesis9mimikfalten.STAERKE : 0;
        }
    }

    static MERKER = { gebiet: 'gebietBild', zeichnung: 'zeichnungBild', mimik: 'mimikBild' };

    static async _karten(inst, lauf, materialien, produkt, geschlecht) {
        const merk = Genesis9hautebenen.MERKER[produkt];
        const offen = materialien.filter(m => !m.userData.genesis9.hautebenen[merk]);
        if (!offen.length) return;
        const karten = await Genesis9hautkarten.holen(produkt, geschlecht);
        if (!karten || lauf !== inst._hautebenenlauf) return;
        for (const m of offen) {
            const h = m.userData.genesis9.hautebenen;
            const adresse = karten.bilder[String(m.userData.kachel)];
            if (!adresse) continue;                      // Kachel ohne Karte (Nägel)
            const angaben = karten.kacheln[String(m.userData.kachel)] || {};
            if (angaben.meter_je_uv) h.uniforms.uHtMeterUV.value = angaben.meter_je_uv;
            if (produkt === 'mimik') h.mimikKanaele = angaben.kanaele || [];
            h[merk] = true;
            Genesis9texturen.holen(adresse, false, m, bild => Genesis9hautebenen._bild(m, produkt, bild));
        }
    }

    static _bild(material, produkt, bild) {
        const h = material.userData.genesis9?.hautebenen;
        if (!h || !bild) return;
        bild.wrapS = bild.wrapT = THREE.ClampToEdgeWrapping;
        if (produkt === 'gebiet') { h.uniforms.uHtGebiet.value = bild; h.uniforms.uHtGebietAn.value = 1; }
        else if (produkt === 'mimik' && h.uniforms.uHtMimikAtlas) {
            // Ein Atlas darf nicht gemipt werden: in der Ferne mischte das die Nachbarzellen (andere Kanäle) herein.
            bild.generateMipmaps = false;
            bild.minFilter = THREE.LinearFilter;
            bild.needsUpdate = true;
            h.uniforms.uHtMimikAtlas.value = bild;
        } else if (h.uniforms.uHtZeichnung) h.uniforms.uHtZeichnung.value = bild;
    }

    /** Nur das Haar (ein Stück kam dazu): graue Strähnen auf die frischen Netze legen. */
    static haar(inst) {
        Genesis9ergrauen.anwenden(inst, Genesis9hautebenen.wirksam(inst).ergrauen);
    }

    /** Einen Wert stellen (Prozent) und anwenden; `null` = zurück auf den Standard. Die Altersfalten liegen in einer eigenen Schicht (`Genesis9hautfalten`). */
    static setzen(inst, name, wert) {
        inst.hautebenen = { ...(inst.hautebenen || {}) };
        Genesis9hautebenen._eintragen(inst, name, wert);
        if (name === 'falten') Genesis9hautfalten.anwenden(inst);
        return Genesis9hautebenen.anwenden(inst);
    }

    /** Mehrere Werte auf einmal (`{name: Prozent|null}`) — ein Anwenden statt eines je Feld (Zurücksetzen, gespeicherte Haut). */
    static alleSetzen(inst, werte) {
        inst.hautebenen = { ...(inst.hautebenen || {}) };
        for (const [name, wert] of Object.entries(werte || {})) Genesis9hautebenen._eintragen(inst, name, wert);
        if ('falten' in (werte || {})) Genesis9hautfalten.anwenden(inst);
        return Genesis9hautebenen.anwenden(inst);
    }

    static _eintragen(inst, name, wert) {
        const zahl = Number(wert);
        if (wert === null || !Number.isFinite(zahl) || zahl === Genesis9hautebenen.standard(name)) delete inst.hautebenen[name];
        else inst.hautebenen[name] = Math.round(zahl);
    }
}
