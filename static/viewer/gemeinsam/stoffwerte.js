import { Umfaerbung } from './umfaerbung.js';
import { Stoffshader } from './stoffshader.js';

/**
 * Stoffwerte — die Stoffwerte eines Genesis-Stücks (Daz, GC, MB) auf seine Materialien.
 *
 * WARUM (Edgar, 25.09.2026: „auch die Material-Einstellungen fehlen"): Die aus
 * GarmentCode gebackenen Stücke (`G9gcstuecke`) hatten nur noch die Farbe
 * (`Umfaerbung`), der GarmentCode-Reiter dagegen Roughness, Metalness und das
 * Gewebe (`garmentcode_material.js`, `garmentcode_gewebe.js`). Die Werte liegen
 * in den Werten des getragenen Stücks (`werte.stoff`) und gehen damit wie Farbe,
 * Variante und Regler mit der Figur in die Szene.
 *
 * `werte.stoff` (Form: `Stoffarten.werte`):
 *   rauheit, metall      am Material (`roughness`, `metalness`)
 *   relief               Stärke der EIGENEN Normalkarte des Stücks (Daz' Normalen, gebackene Falten) — `normalScale`, wie „Relief“ der
 *                        Körperteile (`Genesis9teilmaterial`); 1 = wie geliefert
 *   glanz, saum, saumstreuung, saumfarbe, gewebe {art, faeden, staerke}
 *                        im Shader (`Stoffshader`, seit 25.10.2026) — ohne Neubau, ohne neue Normalkarte
 *   stoffart             nur die Vorwahl, von der man ausging (`Stoffarten`)
 *
 * BIS 25.10.2026 WAR DAS GEWEBE EINE NORMALKARTE und ersetzte die des Stücks (Kachel aus `Gewebe.normalfeld`, `userData.eigeneNormalen`).
 * Damit verschwanden mit dem Gewebe auch die gebackenen Falten (`G9faltenkarte`, `bild.falten_*`) — sie stehen in derselben Karte. Jetzt
 * liegt die Bindung im Shader über der Normalkarte. Das Stoffmaß (Meter je UV-Einheit) wird wie bisher am Netz gemessen (`uvMeter`).
 *
 * SPÄTE BILDER: `Genesis9netz.texturen` setzt beim Eintreffen der Rauheitskarte `roughness = 1` und bei DirectX-Normalen `normalScale.y = −1`
 * — nach dem ersten Anziehen kommen die Bilder oft erst nach `stueck`. `userData.stoffnach` legt die Werte danach wieder auf
 * (`Genesis9texturen.holen` ruft es nach jedem Bild, wie `teilnach` bei den Körperteilen).
 */
export class Stoffwerte {

    /** Bis zu so vielen Kanten misst `uvMeter` (jede n-te). */
    static STICHPROBE = 20000;

    /** Die Werte eines getragenen Stücks auf seine Netze; liefert die Zahl der Materialien. */
    static stueck(inst, kennung, werte) {
        const stoff = werte?.stoff;
        if (!stoff || typeof stoff !== 'object') return 0;
        let gesetzt = 0;
        for (const { netz } of Umfaerbung.netze(inst, kennung)) {
            for (const { netz: kind, material } of Umfaerbung.materialien(netz)) {
                if (!Umfaerbung.faerbbar(material)) continue;
                gesetzt += Stoffwerte.material(material, stoff, kind.geometry);
            }
        }
        return gesetzt;
    }

    static material(material, stoff, geometrie = null) {
        const daten = material.userData;
        if (typeof stoff.rauheit === 'number' && 'roughness' in material) {
            material.roughness = stoff.rauheit;
        }
        if (typeof stoff.metall === 'number' && 'metalness' in material) {
            material.metalness = stoff.metall;
        }
        if (typeof stoff.relief === 'number') Stoffwerte.relief(material, stoff.relief);
        if (!(daten.uvMeter > 0) && geometrie?.attributes?.uv) daten.uvMeter = Stoffwerte.uvMeter(geometrie);
        Stoffshader.setzen(material, stoff, daten.uvMeter);
        daten.stoffnach = () => Stoffwerte.nach(material, stoff);
        material.needsUpdate = true;
        return 1;
    }

    /** Nach einem spät geladenen Bild nur das wieder auflegen, was das Bild überschreibt (Rauheit, Relief); der Shader hält den Rest. */
    static nach(material, stoff) {
        if (typeof stoff.rauheit === 'number' && 'roughness' in material) material.roughness = stoff.rauheit;
        if (typeof stoff.relief === 'number') Stoffwerte.relief(material, stoff.relief);
    }

    /**
     * Stärke der eigenen Normalkarte. Das Vorzeichen von y gehört der Karte (DirectX-Normalen: −1, `Genesis9netz.texturen`) und wird
     * gemerkt, solange y nicht 0 ist — bei Relief 0 wäre es sonst verloren.
     */
    static relief(material, wert) {
        const skala = material.normalScale;
        if (!skala) return;
        const daten = material.userData;
        if (skala.y !== 0) daten.reliefZeichen = Math.sign(skala.y);
        const w = Math.max(0, Math.min(2, wert));
        skala.set(w, w * (daten.reliefZeichen || 1));
    }

    /** Meter Stoff je UV-Einheit: Summe der 3D-Kantenlängen durch die der UV-Kanten. */
    static uvMeter(geometrie) {
        const pos = geometrie?.attributes?.position;
        const uv = geometrie?.attributes?.uv;
        if (!pos || !uv) return 0;
        const index = geometrie.index ? geometrie.index.array : null;
        const n = index ? index.length : pos.count;
        const schritt = Math.max(3, Math.floor(n / Stoffwerte.STICHPROBE / 3) * 3);
        let raum = 0;
        let flaeche = 0;
        for (let i = 0; i + 2 < n; i += schritt) {
            const a = index ? index[i] : i;
            const b = index ? index[i + 1] : i + 1;
            raum += Math.hypot(pos.getX(a) - pos.getX(b), pos.getY(a) - pos.getY(b),
                               pos.getZ(a) - pos.getZ(b));
            flaeche += Math.hypot(uv.getX(a) - uv.getX(b), uv.getY(a) - uv.getY(b));
        }
        return flaeche > 0 ? raum / flaeche : 0;
    }
}
