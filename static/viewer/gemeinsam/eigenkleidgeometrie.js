import * as THREE from 'three';
import { Koerperkoordinatenpunkte } from './koerperkoordinatenpunkte.js';
import { Eigenkleidbruecke } from './eigenkleidbruecke.js';
import { Stoffwerte } from './stoffwerte.js';
import { Protokoll } from './protokoll.js';

/**
 * Eigenkleidgeometrie — die Geometrie einer Schale auf dem Körper (Stufe K2a, 25.10.2026).
 *
 * Eine eigene `BufferGeometry` mit DENSELBEN Attributobjekten wie der Körper (Three lädt sie einmal hoch, keine Kopie der Punkte) und dem VOLLEN Index. Der Körper
 * bekommt unter einem angesetzten Stück (Daz-Anatomie) ein Loch: `Figurhaut` legt den vollen Index in `userData.indexVoll` und setzt einen gekürzten (im Chrome
 * gemessen an DamiraAlt: 599.424 statt 603.744 Indizes) — oft erst NACH dem Binden. Die Schale behält deshalb den Index, der beim Binden voll war.
 *
 * Dazu die Attribute `kkKoord` (Körperkoordinaten je Punkt, an UV-Nähten verschweißt — `Koerperkoordinatenpunkte.ausKarte`), `kkBruecke` und `kkBrueckeB`
 * (`Eigenkleidbruecke`, aus denselben Körperkoordinaten) und die Längen dieser Figur
 * (Rumpf aus der Brücke, Arm und Bein im Verhältnis der Grundfigur). Beides hängt nur an der Körpergeometrie und wird je Geometrie EINMAL gerechnet (`_gemerkt`),
 * Oberteil und Hose teilen es.
 */
export class Eigenkleidgeometrie {

    static _gemerkt = new WeakMap();

    /** → `{geo, laengen: [Rumpf, Arm, Bein] m, bruecke: {punkte, maxHuelleM, maxFallM, ms}, uvMeter}` — `uvMeter` = Meter Haut je UV-Einheit (für die Bindung,
     *  `Stoffshader`; am Körper gemessen wie an einem Daz-Stück, `Stoffwerte.uvMeter`). */
    static bauen(quelle, materialien, karte) {
        const voll = quelle.userData?.indexVoll;
        const index = voll?.index || quelle.index?.array;
        const gruppen = voll?.gruppen || quelle.groups;
        const extra = Eigenkleidgeometrie._extra(quelle, index, gruppen, materialien, karte);
        const geo = new THREE.BufferGeometry();
        for (const [name, attribut] of Object.entries(quelle.attributes)) geo.setAttribute(name, attribut);
        geo.setAttribute('kkKoord', extra.koord);
        geo.setAttribute('kkAnsatz', extra.ansatz);
        geo.setAttribute('kkNormal', extra.normal);
        geo.setAttribute('kkBruecke', extra.attribut);
        geo.setAttribute('kkBrueckeB', extra.attributB);
        geo.setAttribute('kkBrueckeC', extra.attributC);
        geo.setIndex(voll?.index ? new THREE.BufferAttribute(voll.index, 1) : quelle.index);
        for (const g of gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
        geo.userData.quelle = quelle;
        geo.userData.indexGeteilt = !voll?.index;
        geo.userData.stand = extra.bruecke;                         // zum Nachsehen im Browser (Messung), keine Logik hängt daran
        return { geo, laengen: extra.laengen, bruecke: extra.bruecke, uvMeter: extra.uvMeter };
    }

    static _extra(quelle, index, gruppen, materialien, karte) {
        let extra = Eigenkleidgeometrie._gemerkt.get(quelle);
        if (extra) return extra;
        const t0 = performance.now();
        const koord = Koerperkoordinatenpunkte.ausKarte(karte, quelle.attributes.position.array, quelle.attributes.uv.array, index, gruppen, materialien);
        const msKoord = Math.round(performance.now() - t0);
        const b = Eigenkleidbruecke.rechnen(quelle.attributes.position.array, koord);
        const skala = b.rumpfLaenge > 0.2 && b.rumpfLaenge < 1.5 ? b.rumpfLaenge / karte.laengen[0] : 1;
        extra = {
            koord: new THREE.BufferAttribute(Koerperkoordinatenpunkte.alsFeld(koord), 4),
            ansatz: new THREE.BufferAttribute(Koerperkoordinatenpunkte.ansatz(koord), 1),
            normal: new THREE.BufferAttribute(Koerperkoordinatenpunkte.normalen(quelle.attributes.position.array, quelle.attributes.normal.array), 3),
            attribut: new THREE.BufferAttribute(b.feld, 4),
            attributB: new THREE.BufferAttribute(b.feldB, 4),
            attributC: new THREE.BufferAttribute(b.feldC, 4),
            laengen: karte.laengen.map(l => l * skala),
            uvMeter: Stoffwerte.uvMeter(quelle),
            bruecke: { punkte: b.punkte, maxHuelleM: b.maxHuelleM, maxFallM: b.maxFallM, ms: b.ms, rumpfM: b.rumpfLaenge, msKoord, verschweisst: koord.verschweisst },
            koordRoh: koord, faelle: new Map(),
        };
        extra.faelle.set(Eigenkleidgeometrie.schluessel(Eigenkleidbruecke.FALL), { attribut: extra.attribut, attributB: extra.attributB, attributC: extra.attributC });
        Eigenkleidgeometrie._gemerkt.set(quelle, extra);
        Protokoll.debug('Eigene Kleider', `Brücke ${b.punkte} Punkte, Hülle bis ${(1000 * b.maxHuelleM).toFixed(1)} mm, Fall bis ${(1000 * b.maxFallM).toFixed(1)} mm, `
            + `Rumpf ${b.rumpfLaenge?.toFixed(3)} m (${b.ms} ms)`);
        return extra;
    }

    /**
     * Brücke mit einem anderen Fall (Regler „Fall unter Wölbungen“, m je m) und Saum (Rumpfhöhe, nur Haut darüber trägt; auf 0,05 gerundet, sonst rechnete jeder
     * Schritt am Saumschieber neu) an DIESE Schale hängen — je Körpergeometrie, Fall und Saum einmal gerechnet (an DamiraAlt 54–99 ms für die ganze Brücke), die
     * letzten `FAELLE` gemerkt. Andere Schalen auf demselben Körper behalten ihre.
     */
    static FAELLE = 4;

    static schluessel(fall, saum = Infinity) {
        return `${Math.round(1000 * fall) / 1000}|${Number.isFinite(saum) ? Math.round(20 * saum) / 20 : 'alles'}`;
    }

    /** Liegt die Brücke für Fall und Saum schon an oder gemerkt bereit (dann kostet `fallen` nichts)? */
    static gerechnet(geo, fall, saum = Infinity) {
        const k = Eigenkleidgeometrie.schluessel(fall, saum);
        return geo?.userData.fall === k || Boolean(Eigenkleidgeometrie._gemerkt.get(geo?.userData.quelle)?.faelle.has(k));
    }

    static fallen(geo, fall, saum = Infinity) {
        const extra = Eigenkleidgeometrie._gemerkt.get(geo?.userData.quelle);
        const k = Eigenkleidgeometrie.schluessel(fall, saum), grund = Eigenkleidgeometrie.schluessel(Eigenkleidbruecke.FALL);
        if (!extra || geo.userData.fall === k) return;
        let paar = extra.faelle.get(k);
        if (!paar) {
            const [f, s] = k.split('|');
            const b = Eigenkleidbruecke.rechnen(geo.userData.quelle.attributes.position.array, extra.koordRoh, Number(f), s === 'alles' ? Infinity : Number(s));
            paar = { attribut: new THREE.BufferAttribute(b.feld, 4), attributB: new THREE.BufferAttribute(b.feldB, 4), attributC: new THREE.BufferAttribute(b.feldC, 4) };
            extra.faelle.set(k, paar);
            const alt = [...extra.faelle.keys()].filter(x => x !== grund && x !== k);
            if (alt.length > Eigenkleidgeometrie.FAELLE) extra.faelle.delete(alt[0]);
        }
        geo.setAttribute('kkBruecke', paar.attribut);
        geo.setAttribute('kkBrueckeB', paar.attributB);
        geo.setAttribute('kkBrueckeC', paar.attributC);
        geo.userData.fall = k;
    }

    /** Freigeben — VORHER die geteilten Attribute (und einen geteilten Index) abhängen, sonst gäbe `dispose` die Puffer des Körpers mit frei
     *  (`WebGLGeometries.onGeometryDispose`); `kkBruecke` teilen Oberteil und Hose. */
    static weg(geo) {
        if (!geo) return;
        for (const name of Object.keys(geo.attributes)) geo.deleteAttribute(name);
        if (geo.userData.indexGeteilt) geo.setIndex(null);
        geo.dispose();
    }
}
