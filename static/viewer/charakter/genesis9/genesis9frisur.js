import { THREE, state } from '../state.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9netz } from '../../gemeinsam/genesis9netz.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { fn } from '../../gemeinsam/registrierung.js';

/**
 * Genesis9frisur — eine HumanBody-Frisur (GLB aus `hairstyles/`) auf einer
 * Genesis-9-Figur.
 *
 * WARUM (Edgar, 19.09.2026: „bei Genesis sehe ich nicht alle Assets die ich
 * bei HumanBody sehe, z.B. Haar"): Der Haar-Bereich war für Genesis-Figuren
 * versteckt, und `_loadHairForCharacter` hängt die GLB starr an den
 * HumanBody-Kopfknochen. Hier holt der Server die Frisur auf DIESEN Kopf
 * gelegt (`core/dienste/g9frisur.py`: achsweise auf den Kopfkasten skaliert,
 * aus der Kopfhaut gehoben, an `head` gebunden) — dieselbe Antwortform wie
 * ein Daz-Stück, also derselbe Weg ins Netz (`Genesis9netz.bauen`,
 * `inst._einhaengen`).
 *
 * DAS STÜCK LIEGT IN `clothMeshes` (`SCHLUESSEL`), nicht in `inst.hairMesh`:
 * Nur so bindet `_kleiderBinden` es nach einem Umbau an das neue Skelett
 * (`hautgewichte` in `userData`). `inst.hairStyle` bleibt gesetzt, damit
 * Auswahlfeld und Farbe wie bei HumanBody funktionieren (`hair.js`).
 */
export class Genesis9frisur {

    static ADRESSE = '/api/character/genesis9-figur/frisur/';
    static SCHLUESSEL = 'humanbody_frisur/0';

    /** Das Netz der Frisur an der Figur — oder null. */
    static netz(inst) {
        return inst?.clothMeshes?.[Genesis9frisur.SCHLUESSEL] || null;
    }

    /** Der Frisurname aus der Adresse des Auswahlfelds (`/api/character/hairstyle/<name>/`). */
    static name(url) {
        const treffer = /hairstyle\/([^/]+)\/?$/.exec(url || '');
        return treffer ? decodeURIComponent(treffer[1]) : (url || '').split('/').filter(Boolean).pop() || '';
    }

    /** Auswahl aus dem Haar-Bereich: leer = ausziehen, sonst anziehen. */
    static async waehlen(inst, url, farbe) {
        if (!url) return Genesis9frisur.ausziehen(inst);
        return Genesis9frisur.anziehen(inst, url, farbe);
    }

    static async anziehen(inst, url, farbe) {
        const name = Genesis9frisur.name(url);
        if (!inst || !name) return null;
        Genesis9frisur.ausziehen(inst);
        const stufen = inst.stufen ?? 1;
        let daten;
        try {
            daten = await Serverabruf.senden(
                `${Genesis9frisur.ADRESSE}${encodeURIComponent(name)}/?stufen=${stufen}`,
                { regler: inst.regler || {} });
        } catch (fehler) {
            Protokoll.warnung('Genesis 9', `Frisur ${name} nicht ladbar: ${fehler.message}`);
            return null;
        }
        if (daten?.fehler) { Protokoll.warnung('Genesis 9', `Frisur ${name}: ${daten.fehler}`); return null; }
        const teil = daten.teile?.[0];
        if (!teil) return null;
        const netz = Genesis9netz.bauen(teil, `genesis9_frisur_${name}`);
        netz.userData.beschriftung = `${name} (HumanBody-Frisur)`;
        Genesis9frisur.faerben(netz, farbe);
        inst.clothMeshes[Genesis9frisur.SCHLUESSEL] = inst._einhaengen(netz, teil.hautgewichte);
        inst.hairStyle = { url, name, color: farbe || '' };
        Protokoll.info('Genesis 9', `Frisur ${name}: ${teil.vertex_count} Punkte, `
            + `aus der Kopfhaut gehoben bis ${daten.hub_mm} mm`);
        fn.updateEquippedList?.(inst);
        fn.updateVertexCount?.();
        return netz;
    }

    static ausziehen(inst) {
        const alt = Genesis9frisur.netz(inst);
        if (alt) Netzentsorgung.ausAblage(inst.group, inst.clothMeshes, Genesis9frisur.SCHLUESSEL);
        inst.hairStyle = null;
        fn.updateEquippedList?.(inst);
        fn.updateVertexCount?.();
        return !!alt;
    }

    /** Die Farbe aus `hairColorData` auf alle Materialien des Netzes. */
    static faerben(netz, farbe) {
        const rgb = farbe ? state.hairColorData?.[farbe] : null;
        if (!rgb || !netz) return false;
        const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
        (Array.isArray(netz.material) ? netz.material : [netz.material])
            .forEach((m) => { if (m?.color) m.color.copy(color); });
        return true;
    }
}
