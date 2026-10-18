import { Anatomieton } from './anatomieton.js';
import { Anatomiezuordnung } from './anatomiezuordnung.js';
import { Anatomiehash } from './anatomiehash.js';
import { Anatomiearbeit } from './anatomiearbeit.js';
import { Anatomiefenster } from './anatomiefenster.js';
import { Anatomierechnung } from './anatomierechnung.js';
import { Anatomietextur } from './anatomietextur.js';

/**
 * Anatomiebacken — die Karten des Scham-Stücks aus den Karten der gewählten Haut rechnen (11.10.2026).
 *
 * Edgar: „Skin änderung funktioniert nicht bei der Scham, die neue skin Textur erscheint da nicht, nur die farbe." Das Stück hat einen eigenen UV-Atlas;
 * die Karten der Haut gehören zu UV der Haut. Hier entsteht für das Stück eine NEUE Karte im Atlas des Stücks (Farbe, Normalen, Rauheit, je Texel von
 * der Stelle der Haut darunter, `Anatomiezuordnung` + `Anatomiebild`) — keine neue UV am Netz, keine Doppelpunkte an den Nähten der Haut-Inseln.
 * Die Zuordnung rechnet auf dem Hauptfaden in Häppchen (`atmen`), Bild und Füllen im Worker (`Anatomiearbeit`, seit 12.10.2026; ohne Worker ebenfalls auf dem
 * Hauptfaden). Ein Lauf je Stück und Haut, das Ergebnis liegt am Netz (`Anatomiekarten.merken`).
 *
 * Die Haut wird mit ihrem VOLLEN Index gelesen (`geometry.userData.indexVoll`): unter dem Stück hat die Hautverdeckung ihre Dreiecke aus dem Index
 * genommen, und genau die liegen dem Stück am nächsten.
 */
export class Anatomiebacken {

    /** Die Karte des Stücks ist so groß wie ihr Vorbild, aber nicht kleiner/größer als dies (Pixel je Kante). */
    static KANTE_MIN = 512;
    static KANTE_MAX = 2048;

    /** Lässt den Hauptfaden zwischen zwei Häppchen Luft (eine Nachricht, nicht der Zeitgeber: im Hintergrund-Tab auf 1 s gedrosselt). */
    static atmen() {
        return new Promise((fertig) => {
            const kanal = new MessageChannel();
            kanal.port1.onmessage = () => { kanal.port1.close(); fertig(); };
            kanal.port2.postMessage(0);
        });
    }

    /**
     * Einen Lauf anstoßen (je Stück und Schlüssel nur einen) — das Ergebnis oder ein Fehlschlag wird am Netz gemerkt, danach `fertig()`.
     * @param original  `Anatomiekarten.original(m)`: die eigenen Karten des Stücks (Vorlage für Größe und Einstellungen der neuen)
     */
    static anstossen(inst, netz, original, schluessel, haut, fertig) {
        if (netz.userData.anatomieBackt === schluessel) return;
        netz.userData.anatomieBackt = schluessel;
        const ablegen = (neu) => {
            if (netz.userData.anatomieBackt !== schluessel) return false;       // ein neuerer Lauf (andere Haut) hat übernommen
            const alt = netz.userData.anatomieGebacken;
            for (const t of [alt?.map, alt?.normalMap, alt?.roughnessMap]) t?.dispose?.();     // GPU-Speicher des alten Stands
            netz.userData.anatomieGebacken = { ...neu, schluessel };
            return true;
        };
        Anatomiebacken.backen(inst, netz, original, haut)
            .then((gebacken) => { if (ablegen(gebacken || { leer: true })) fertig(); })
            .catch((fehler) => { console.warn(`Anatomiebacken: ${fehler.message}`); ablegen({ leer: true }); })     // leer: nicht bei jedem Anwenden neu versuchen
            .finally(() => { if (netz.userData.anatomieBackt === schluessel) netz.userData.anatomieBackt = null; });
    }

    /**
     * Die Karten rechnen: `{map, normalMap, roughnessMap, farbe}` oder null (keine Karte der Haut in der Nähe, kein Index).
     * @param haut  Namen der Gruppen des Körpers, die Haut sind (`Anatomiehaut.HAUT`)
     */
    static async backen(inst, netz, original, haut) {
        const e = Anatomiebacken.eingabe(inst, netz, original, haut);
        if (!e) return null;
        const { quelle, breite, hoehe, stueck, vorlage } = e;
        const zu = await Anatomiebacken.zuordnung(netz, stueck, quelle.haut, breite, hoehe);
        if (!zu.anzahl) return null;
        const bild = await Anatomiebacken.bild(netz, zu, e);
        if (!bild) return null;                                        // überholt: eine neuere Haut hat den Auftrag abgelöst
        const vorN = original.normalen || quelle.texturen.find(t => t.normalMap)?.normalMap, vorR = original.rauheit || quelle.texturen.find(t => t.roughnessMap)?.roughnessMap;
        return {
            map: Anatomietextur.aus(vorlage, bild.farbe, breite, hoehe),
            normalMap: bild.normal && vorN ? Anatomietextur.aus(vorN, bild.normal, breite, hoehe) : null,
            roughnessMap: bild.rauheit && vorR ? Anatomietextur.aus(vorR, bild.rauheit, breite, hoehe) : null,
            farbe: quelle.texturen[Anatomiebacken.haeufigste(zu, quelle.gruppe, quelle.texturen.length)].color,
        };
    }

    /**
     * Bild und Füllen (`Anatomierechnung`): im Worker (`Anatomiearbeit`), solange einer zu haben ist, sonst auf dem Hauptfaden in Häppchen — dasselbe Ergebnis.
     * Der Worker bekommt die Pixel der Fenster und lässt sie leer zurück; nach einem Ausfall werden sie für den Hauptfaden neu gelesen.
     * @param e  `eingabe(…)`
     * @returns `{farbe, normal, rauheit}` oder null: der Lauf ist überholt (für dieses Stück kam ein neuerer Auftrag)
     */
    static async bild(netz, zu, e) {
        const { quelle, breite, hoehe, uv, uvKarte, stueck } = e;
        const auftrag = () => ({
            zu, st: { pos: stueck.pos, uv, normal: stueck.normal, index: stueck.index }, ha: quelle.haut, gruppe: quelle.gruppe,
            fenster: Anatomiefenster.lesen(zu, quelle.haut, quelle.gruppe, quelle.texturen), breite, hoehe, uvKarte,
        });
        let a = auftrag();
        if (Anatomiearbeit.verfuegbar()) {
            const aus = await Anatomiearbeit.rechnen(a, netz);
            if (aus === Anatomiearbeit.VERALTET) return null;
            if (aus) return aus;
            a = auftrag();                                             // der Worker ist ausgefallen; seine Fenster sind übertragen, also leer
        }
        return Anatomierechnung.rechnen(a, Anatomiebacken.atmen);
    }

    /**
     * Was die Rechnung liest: die Hautdreiecke in der Nähe (`quelle`), die Größe der Karte, die UV des Stücks (`uvKarte`: in Zeilen der Karte) und das Stück als
     * `{pos, uv, index, normal}` für die Zuordnung — oder null (keine Karte der Haut in der Nähe, kein Index, keine Vorlage mit Bild).
     * Vorlage (Größe, Farbraum, `flipY`) ist die eigene Farbkarte des Stücks; ohne eine („Daz Anatomie Mann" hat nur eine Farbe, 18.10.2026 an Matt0) die Farbkarte
     * der Haut — wie bei Normalen und Rauheit in `backen`. UV der Rechnung und neue Textur folgen derselben Vorlage, also passt `flipY` in beiden Fällen.
     */
    static eingabe(inst, netz, original, haut) {
        const quelle = Anatomiebacken.quelle(inst, netz, haut);
        const geo = netz.geometry, vorlage = original.karte || quelle?.texturen[0]?.map;
        if (!quelle || !geo.index || !vorlage?.image?.width) return null;
        const breite = Math.max(Anatomiebacken.KANTE_MIN, Math.min(Anatomiebacken.KANTE_MAX, vorlage.image.width));
        const hoehe = Math.max(Anatomiebacken.KANTE_MIN, Math.min(Anatomiebacken.KANTE_MAX, vorlage.image.height));
        const uv = geo.attributes.uv.array, uvKarte = vorlage.flipY ? Float32Array.from(uv, (w, i) => (i & 1 ? 1 - w : w)) : uv;
        const stueck = { pos: geo.attributes.position.array, uv: uvKarte, index: geo.index.array, normal: geo.attributes.normal?.array || null };
        return { quelle, breite, hoehe, uv, uvKarte, stueck, vorlage };
    }

    /**
     * Die Zuordnung (Texel des Stücks → Stelle der Haut), je Stück einmal je Geometrie (`Anatomiehash`): Sie hängt nicht an der Textur der Haut, ein Hautwechsel
     * braucht sie nicht neu (gemessen 12.10.2026: 5,6 von 8,2 s der Rechnung). Abgelegt wird das VERSPRECHEN: ein zweiter Aufruf, während der erste noch rechnet, wartet auf
     * denselben Lauf; ein gescheiterter Lauf bleibt nicht liegen.
     */
    static zuordnung(netz, stueck, haut, breite, hoehe) {
        // Die Normalen des Stücks ändert die Naht nach dem ersten Lauf an den Ringpunkten (`Hautloch.normalenAngleichen`, rechnet von `nahtRuhe` aus): im Schlüssel zählen die RUHE-Normalen,
        // sonst fand der erste Hautwechsel nach dem Laden nie einen Treffer (gemessen 12.10.2026: erster Wechsel 15 s, danach 3 s).
        const ruhe = netz.geometry?.userData?.nahtRuhe;
        const schluessel = Anatomiehash.schluessel({ ...stueck, normal: ruhe || stueck.normal }, haut, breite, hoehe);
        const alt = netz.userData.anatomieZuordnung;
        if (alt?.schluessel === schluessel) return alt.zu;
        const zu = Anatomiezuordnung.rechnen(stueck, haut, breite, hoehe, Anatomiebacken.atmen);
        netz.userData.anatomieZuordnung = { schluessel, zu };
        zu.catch(() => { if (netz.userData.anatomieZuordnung?.zu === zu) delete netz.userData.anatomieZuordnung; });
        return zu;
    }

    /**
     * Die Zuordnung schon rechnen, bevor jemand die Haut wechselt (Katalog-Haut, `Anatomiehaut.anwenden`): der erste Wechsel backt dann nur noch die Karten. Ein Lauf je
     * Stück zugleich; Fehler stehen im Log und brechen nichts ab.
     */
    static async vorrechnen(inst, netz, original, haut) {
        const ablage = netz.userData;
        if (ablage.anatomieVorrechnet) return;
        ablage.anatomieVorrechnet = true;
        try {
            const e = Anatomiebacken.eingabe(inst, netz, original, haut);
            if (e) await Anatomiebacken.zuordnung(netz, e.stueck, e.quelle.haut, e.breite, e.hoehe);
        } catch (fehler) {
            console.warn(`Anatomiebacken: Vorrechnen: ${fehler.message}`);
        } finally {
            ablage.anatomieVorrechnet = false;
        }
    }

    /** Die Gruppe der Haut, auf der die meisten Texel liegen (ihre Farbe gilt für das Stück). */
    static haeufigste(zu, gruppe, anzahl) {
        const zaehler = new Array(anzahl).fill(0);
        for (let k = 0; k < zu.anzahl; k++) zaehler[gruppe[zu.btri[k]]]++;
        return zaehler.indexOf(Math.max(...zaehler));
    }

    /**
     * Die Hautdreiecke in der Nähe des Stücks, mit ihren Karten: `{haut: {pos, uv, normal, ecken}, gruppe, texturen}` oder null.
     * `gruppe`: je Dreieck der Eintrag in `texturen` (eine Gruppe der Haut mit Farbkarte je Eintrag).
     */
    static quelle(inst, netz, haut) {
        const koerper = inst?.bodyMesh, geo = koerper?.geometry, stueck = netz?.geometry;
        if (!geo?.attributes?.uv || !geo.index || !stueck?.attributes?.position) return null;
        const voll = geo.userData?.indexVoll, index = voll ? voll.index : geo.index.array, gruppen = voll ? voll.gruppen : geo.groups;
        const material = [koerper.material].flat(), pos = geo.attributes.position.array;
        const kasten = Anatomieton.kasten(stueck, Anatomiezuordnung.REICHWEITE);
        const drin = (i) => [0, 1, 2].every(k => pos[3 * i + k] >= kasten.lo[k] && pos[3 * i + k] <= kasten.hi[k]);
        const texturen = [], ecken = [], gruppe = [];
        for (const gr of gruppen || []) {
            const m = material[gr.materialIndex];
            if (!haut.includes(m?.userData?.gruppe) || !m.map?.isTexture) continue;
            const nr = texturen.push({ map: m.map, normalMap: m.normalMap || null, roughnessMap: m.roughnessMap || null, color: m.color }) - 1;
            for (let n = 0; n + 2 < gr.count; n += 3) {
                const a = index[gr.start + n], b = index[gr.start + n + 1], c = index[gr.start + n + 2];
                if (drin(a) || drin(b) || drin(c)) { ecken.push(a, b, c); gruppe.push(nr); }
            }
        }
        if (!ecken.length) return null;
        return { haut: { pos, uv: geo.attributes.uv.array, normal: geo.attributes.normal?.array || null, ecken: Uint32Array.from(ecken) }, gruppe: Uint8Array.from(gruppe), texturen };
    }
}
