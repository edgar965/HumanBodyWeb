import { Modellexport } from '../charakter/modellexport.js';
import { Anatomiehaut } from '../gemeinsam/anatomiehaut.js';
import { Figuraufbaustand } from '../gemeinsam/figuraufbaustand.js';
import { Genesis9haeppchen } from '../gemeinsam/genesis9haeppchen.js';
import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';
import { Netzstufenstand } from '../gemeinsam/netzstufenstand.js';

/**
 * Exportleistefigur — die Figur der Seite als Datei für die Exportleiste (31.10.2026).
 *
 * GLB mit Rig, Textur und allen Stücken, ohne Animation (`Modellexport.glbBytes` — derselbe Schreiber wie „Exportieren …" der Charakter-Seite): Die Animation baut der Server aus der
 * BVH ein, damit Export und Render dieselbe Bewegung tragen. OBJ schreibt der Browser ganz (`Modellexport`, Format `obj`, aktuelle Pose — gestoppt ist das die Ruhelage) und legt sie
 * über den Endpunkt `obj/` der Leiste in ihren Ordner, je Export ein Unterordner (OBJ bringt MTL und ein Bild je Materialzone mit).
 */
export class Exportleistefigur {

    static OPTIONEN = { rig: true, textur: true, assets: true, aufloesung: 0 };

    /**
     * @param vorgabe `() => 'Kategorie/Name'` — die BVH-Vorgabe des Bereichs (`zustand.bvh_vorgabe`), für Quellen, deren Figur eine Bewegung braucht, um ganz zu stehen
     * @param eigen `() => bool` — der Bereich hat sein eigenes Modell (`zustand.eigenes_modell`, 2D3D Kleider): GLB und Blender nimmt der Server von dort, nur OBJ kommt aus der Seite
     */
    constructor(quelle, vorgabe = () => '', eigen = () => false) {
        this.quelle = quelle;
        this.vorgabe = vorgabe;
        this.eigen = eigen;
    }

    /** Was der Server zur Figur braucht: `{blob, stellung}` — beim eigenen Modell des Bereichs nichts (`blob` null), er nimmt sein Modell und seine Stellung. */
    async fuerServer() {
        if (this.eigen()) return { blob: null, stellung: {} };
        const { blob, modell } = await this.glb();
        return { blob, stellung: Exportleistefigur.stellung(modell) };
    }

    /** Das Formular für Export und Render: `modell` (nur mit GLB) und `angaben` als JSON. */
    static formular(blob, angaben) {
        const daten = new FormData();
        if (blob) daten.append('modell', blob, 'modell.glb');
        daten.append('angaben', JSON.stringify(angaben));
        return daten;
    }

    /**
     * Die Figur ganz gebaut, in der feinen Stufe. Auf Seiten mit Schnellanzeige (Mesh3D-AI) ist „grob" gewählt und die Figur bleibt im Käfig — gemessen am ersten Export
     * (31.10.2026, Test edgar): Körper 50.312 Dreiecke statt der feinen Stufe. Dann holt diese Figur allein die feine Stufe nach (`Genesis9haeppchen`, wie Strg+Alt+H), die Wahl der
     * Seite bleibt danach „grob". Die Quelle ruft das, bevor sie ihre Stücke an das Skelett der neuen Stufe bindet.
     */
    static async vollBauen(inst) {
        await Figuraufbaustand.warten(inst);
        if (inst?.quelle !== 'genesis9' || Netzstufenstand.wahl !== 'grob' || ['fein', 'ultrafein'].includes(Netzstufenstand.stufeVon(inst))) return;
        const vorher = Netzstufenstand.wahl;
        Netzstufenstand.wahl = 'fein';
        try {
            inst.fein = Genesis9haeppchen.zug(inst, false);
            await inst.fein;
        } finally {
            Netzstufenstand.wahl = vorher;
        }
    }

    /** Die Angaben zur Figur für den Server (Figur, Regler, Höhe — derselbe Retarget wie im Browser, `Exportleistebewegung`; `haut_deckt`: `hautDeckt`). */
    static stellung(m) {
        return { figur: m.figur || '', regler: m.regler || {}, hoehe_m: m.hoehe_m || 0, haut_deckt: Exportleistefigur.hautDeckt(m.inst) };
    }

    /**
     * Die Namen der Stücke, unter denen die Szene die Haut ausblendet (`Hautverdeckung.zaehlt`: kein Haar ohne Kostüm, keine ersetzenden Augen, nichts Ausgeblendetes) — so heißen sie
     * als Knoten in der GLB. Der Server nimmt nur unter diesen die Haut aus dem Körper (`Exportleistehautmaske`); unter Haar bliebe sonst ein Loch im Kopf, wo die Frisur Lücken hat.
     */
    static hautDeckt(inst) {
        return Object.entries(Hautverdeckung.stuecke(inst)).filter(([, netz]) => Hautverdeckung.zaehlt(netz)).map(([schluessel, netz]) => netz.name || schluessel);
    }

    async _modell() {
        const m = await this.quelle.modell({ bvh: this.vorgabe() });
        if (!m?.inst) throw new Error('Die Seite hat keine Figur für den Export');
        await Exportleistefigur.anatomieAbwarten(m.inst);
        return m;
    }

    static ANATOMIE_MS = 60000;

    /**
     * Bis das Anatomie-Stück die Haut des Körpers trägt (`Anatomiehaut`: Bilder abwarten, Karten backen) — die feine Stufe aus `vollBauen` baut es neu, und der Export lief
     * bisher sofort weiter (31.10.2026, Venus). Nach `ANATOMIE_MS` geht es ohne weiter, mit Warnung in der Konsole.
     */
    static async anatomieAbwarten(inst) {
        const ende = performance.now() + Exportleistefigur.ANATOMIE_MS;
        while (Anatomiehaut.stuecke(inst).length && performance.now() < ende) {
            await (Anatomiehaut.nachziehen(inst) || inst._anatomieWartet || null);
            if (!Anatomiehaut.offen(inst).length) return;
            await new Promise(r => setTimeout(r, 300));
        }
        if (Anatomiehaut.offen(inst).length) console.warn('Exportleistefigur: Anatomie-Stück nach %d s noch nicht in der Haut', Exportleistefigur.ANATOMIE_MS / 1000);
    }

    /**
     * → `{blob, modell}`: die GLB und die Angaben der Figur (`figur`, `regler`, `hoehe_m`). Der Körper OHNE die Haut unter den Stücken, wie die Szene ihn zeigt
     * (`hautWieSzene`, Edgar 31.10.2026: GLB und .blend werden bewegt, mit der ganzen Haut stach sie in der Bewegung durch den Stoff). Die Maske wird vorher für genau
     * diesen Körper gerechnet: nach `vollBauen` ist er neu, und die Rechnung der Szene kommt erst nach ihrer Ruhezeit (`Hautverdeckung.planen`).
     */
    async glb() {
        const modell = await this._modell();
        await Hautverdeckung.anwendenAsync(modell.inst);
        const bytes = await Modellexport.glbBytes(modell.inst, { ...Exportleistefigur.OPTIONEN, hautWieSzene: true });
        return { blob: new Blob([bytes], { type: 'model/gltf-binary' }), modell };
    }

    /**
     * OBJ + MTL + Bilder nach `<ordner>/<name>/` → Antwort des Servers `{ordner, dateien, warnungen, hautverdeckung}`. Über `endpunkt` (die Leiste, `obj/`) nimmt der Server
     * vorher die Haut unter den deckenden Stücken heraus, wie bei GLB und .blend (`Exportleisteobjmaske`).
     */
    async obj(ordner, name, endpunkt) {
        const modell = await this._modell();
        const felder = { haut_deckt: JSON.stringify(Exportleistefigur.hautDeckt(modell.inst)) };
        return Modellexport.exportieren(modell.inst, { ...Exportleistefigur.OPTIONEN, formate: ['obj'], animation: false, pose: 'aktuell', ordner, name, endpunkt, felder });
    }
}
