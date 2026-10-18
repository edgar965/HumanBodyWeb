import * as THREE from 'three';
import { Genesis9haut } from './genesis9haut.js';
import { Genesis9texturen } from './genesis9texturen.js';
import { Protokoll } from './protokoll.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Genesis9hautfalten — die Falten des Alters auf der Haut (17.10.2026).
 *
 * Edgar: „altersregler funktioniert nicht, das Gesicht wenn der am Anschlag ist, ist noch immer das gleiche … schau dir das bei HumanBody an, da wird es ein
 * alter Mann". HumanBody zeichnet zur Altersform die Falten des MB-Lab-Verschiebungsbilds (Augenlinien, Halsringe, Kinnlinie); die Morphs allein sind dort
 * wenige Millimeter. Der Server rechnet dieses Bild je UDIM-Kachel in eine Normalenkarte um (`core/dienste/g9hautfalten.py`, einmal je Geschlecht, 46 s, dann aus
 * der Ablage), hier liegt sie als weitere Normalenschicht über der Hautnormale (`Genesis9haut.falten`, `Genesis9hautGLSL.FALTEN`).
 *
 * Das Gewicht ist der Wert des Reglers `alter:gesamt` (nur 0 … +1; jünger = keine Falten) mal `STAERKE`. Ohne Alter wird nichts geholt: weder der Bau noch
 * ein Bild. Nach jedem Körperbau (`koerperAufbauen`) frisch aufgelegt, wie die Texturmischung.
 */
export class Genesis9hautfalten {

    static ADRESSE = '/api/character/genesis9-figur/hautfalten/';
    static REGLER = 'alter:gesamt';
    static MAENNLICH = 'BaseMasculine_figure_ctrl_Character';
    static WEIBLICH = 'BaseFeminine_figure_ctrl_Character';
    /** Streckung der Steigung bei Alter +1 (1 = so tief wie HumanBodys Verschiebung); die Falten sind ein Licht-, kein Formeffekt. Nach Augenmaß (Chrome, Mann1). */
    static STAERKE = 4.0;
    /** Abdunklung der Albedo in der tiefsten Furche bei Alter +1 (Alpha der Karte = Furchentiefe, `g9hautfalten.py` Fassung 2). Nach Augenmaß. */
    static DUNKEL = 0.6;
    /** Der Bau auf dem Server dauert ~50 s: so oft fragen wir im Abstand von `PAUSE_MS` nach. */
    static VERSUCHE = 60;
    static PAUSE_MS = 3000;
    /** Geschlecht → Promise<{kachel: Adresse}|null> */
    static _stand = new Map();

    /**
     * Der Alterswert 0 … 1 (nur „älter" zeichnet Falten): das EINE Aussehen, das der Server aus „Alter“ (`alter:jahre`) und „Wirkt älter / jünger“ (`alter:gesamt`) rechnet und in der
     * Netzantwort als `alter_aussehen` schickt (`G9alterung`, 17.10.2026, Vorschlag A). Vorher las diese Stelle das MAXIMUM der rohen Schieber, während der Körper SUMMIERTE — Lebensalter −1
     * (Baby) mit Alter +1 bekam Falten und graue Haare. Ohne das Feld (eine Antwort ohne `alter_aussehen`, ältere Server) gilt die alte Regel.
     */
    static alter(inst) {
        if (Number.isFinite(inst.alterAussehen)) return Math.min(1, Math.max(0, inst.alterAussehen));
        const r = inst.regler || {};
        return Math.min(1, Math.max(0, Number(r[Genesis9hautfalten.REGLER]) || 0, Number(r['alter:jahre']) || 0));
    }

    /** `male`, wenn die männliche Grundfigur im Rumpf stärker steht — wie `G9alter.maennlich`. */
    static geschlecht(inst) {
        const r = inst.regler || {};
        return (Number(r[Genesis9hautfalten.MAENNLICH]) || 0) > (Number(r[Genesis9hautfalten.WEIBLICH]) || 0) ? 'male' : 'female';
    }

    /** Die Materialien des Körpers, die zu einer UDIM-Kachel gehören. */
    static materialien(inst) {
        const material = inst.bodyMesh?.material;
        return (Array.isArray(material) ? material : [material]).filter(m => m?.userData?.kachel != null);
    }

    /** Die Adressen der Faltenkarten je Kachel — einmal je Geschlecht; wartet auf den Bau; null bei Fehler. */
    static bilder(geschlecht) {
        if (!Genesis9hautfalten._stand.has(geschlecht)) {
            Genesis9hautfalten._stand.set(geschlecht, Genesis9hautfalten._abwarten(geschlecht).catch(fehler => {
                Protokoll.warnung('Hautfalten', `Faltenkarten (${geschlecht}) nicht verfügbar: ${fehler.message}`);
                Genesis9hautfalten._stand.delete(geschlecht);
                return null;
            }));
        }
        return Genesis9hautfalten._stand.get(geschlecht);
    }

    static async _abwarten(geschlecht) {
        for (let i = 0; i < Genesis9hautfalten.VERSUCHE; i++) {
            const antwort = await Serverabruf.json(`${Genesis9hautfalten.ADRESSE}${geschlecht}/`);
            if (antwort.stand === 'fertig') return antwort.bilder || {};
            if (antwort.stand === 'fehler') throw new Error(antwort.fehler || 'Bau fehlgeschlagen');
            await new Promise(weiter => setTimeout(weiter, Genesis9hautfalten.PAUSE_MS));
        }
        throw new Error('Bau dauert zu lange');
    }

    /**
     * Gewicht und Bilder auf die Materialien der Figur legen. Ohne Alter: nur die schon eingerichteten Schichten auf 0 stellen — kein Abruf.
     * `lauf` verwirft die Antwort eines überholten Aufrufs (der Schieber löst viele Körperbauten aus).
     */
    static async anwenden(inst) {
        // `lauf` zählt JEDEN Aufruf, auch den ohne Alter: sonst setzt ein überholter Aufruf mit Alter (er wartet noch auf die Karten) seine Falten NACH der Rückstellung auf 0 wieder ein —
        // der Schieber stünde auf 0 und die Haut bliebe gealtert (17.10.2026, Edgar: „Altersregler hinterlässt Müll").
        const lauf = inst._faltenlauf = (inst._faltenlauf || 0) + 1;
        const alter = Genesis9hautfalten.alter(inst);
        const gewicht = alter * Genesis9hautfalten.STAERKE;
        const materialien = Genesis9hautfalten.materialien(inst);
        if (gewicht <= 0) {
            for (const m of materialien) Genesis9hautfalten.gewichtSetzen(m, 0, 0);
            return;
        }
        const bilder = await Genesis9hautfalten.bilder(Genesis9hautfalten.geschlecht(inst));
        if (!bilder || lauf !== inst._faltenlauf) return;
        for (const material of materialien) {
            const adresse = bilder[String(material.userData.kachel)];
            if (!adresse) continue;                      // Kachel ohne Falten (Nägel)
            Genesis9hautfalten.einrichten(material);
            Genesis9hautfalten.gewichtSetzen(material, gewicht, alter * Genesis9hautfalten.DUNKEL);
            Genesis9texturen.holen(adresse, false, material, bild => Genesis9hautfalten.bildSetzen(material, bild));
        }
    }

    /** Die Schicht ankündigen: Uniforms und Platzhalter; das Programm bekommt `-f` im Schlüssel. */
    static einrichten(material) {
        const zusatz = Genesis9haut._zusatz(material);
        if (zusatz.falten) return;
        zusatz.falten = {
            uFaltenAn: { value: 0 },
            uFaltenGewicht: { value: 0 },
            uFaltenDunkel: { value: 0 },
            uFaltenNormalen: { value: Genesis9haut.platzhalter(128, 128, 255) },
        };
        // Ohne Grundnormale kennt der Shader keinen Tangentenraum: eine flache einsetzen.
        if (!material.normalMap) material.normalMap = Genesis9haut.platzhalter(128, 128, 255);
        Genesis9haut._einhaengen(material);
        material.needsUpdate = true;
    }

    static bildSetzen(material, bild) {
        const falten = material.userData.genesis9?.falten;
        if (!falten || !bild) return;
        bild.wrapS = bild.wrapT = THREE.ClampToEdgeWrapping;
        falten.uFaltenNormalen.value = bild;
        falten.uFaltenAn.value = 1;
    }

    static gewichtSetzen(material, gewicht, dunkel) {
        const falten = material.userData.genesis9?.falten;
        if (!falten) return;
        falten.uFaltenGewicht.value = gewicht;
        falten.uFaltenDunkel.value = dunkel;
    }
}
