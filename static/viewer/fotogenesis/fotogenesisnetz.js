/**
 * Fotogenesisnetz — Feld 2 „Netz“ der Seite „Foto-Genesis“ (24.10.2026): das Netz aus den Fotos (Hunyuan3D-2mv oder Tripo3D) als GLB, Zeichner für `Meshgenesisansicht`.
 *
 * Die Ansichtsarten wie bei Mesh-Genesis (`Meshgenesismaterial.MODI`, Materialien `Meshgenesisechtmaterial`): „Textur“ zeigt die Materialien der Datei, alle anderen Arten zeichnet das Feld mit EINEM Ersatzmaterial
 * über Ebene 1 (`inhalt.userData.genesisErsatz`, derselbe Weg wie die Genesis-Figur in `Meshgenesisgenesisfigur`). Ein Netz wird je Adresse einmal geladen; die Tripo-Dateien haben 61–69 MB
 * und ~1,9 Mio. Dreiecke (gelesen 24.10.2026, `_wegwerf/fotogenesis/glb_kopf.py`) — der Ladestand steht im Feld.
 */
import { LoaderUtils } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Pufferabruf } from '../gemeinsam/pufferabruf.js';
import { Meshgenesisechtmaterial } from '../meshgenesis/meshgenesisechtmaterial.js';

export class Fotogenesisnetz {
    /** @param {(text: string) => void} melden Ladestand ins Feld @param {() => void} fertig das Feld neu zeigen */
    constructor(melden, fertig) {
        Object.assign(this, { melden, fertig, _netze: new Map() });
    }

    /** Ersatzmaterial der Ansichtsart; `null` = die eigenen Materialien („Textur“). */
    static ersatz(modus) {
        if (modus === 'textur') return null;
        const art = modus === 'punkte' || modus === 'oberflaeche_draht' ? 'oberflaeche' : modus;
        const netz = Meshgenesisechtmaterial.netz(undefined, art);
        return netz.material ?? netz.children?.[0]?.material ?? null;
    }

    /**
     * Je Adresse EINE geladene Datei für alle Felder: `{szene: Promise, hoerer: Set}` (21.11.2026, Ladezeit /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/: das PSHuman-Netz,
     * 71 MB, 1,27 Mio. Punkte, wurde vom Feld „Netz“ und vom Feld „PSHuman“ je einmal geladen und geparst — zweimal 68 MB Geometrie im Speicher, zweimal die Parsezeit auf dem Hauptfaden).
     * Jedes Feld bekommt einen eigenen Klon der Szene (ein Objekt hängt nur in einem Feld); Geometrie und Materialien teilen die Klone (`Object3D.clone`).
     */
    static _dateien = new Map();

    /** Die Szene für EIN Feld: ein Klon der einmal geladenen Datei — ein gehäutetes Netz (Klon bräuchte `SkeletonUtils`, fehlt im Vendor) bekommt nur das erste Feld, jedes weitere lädt selbst. */
    static _datei(adresse, fortschritt) {
        let d = Fotogenesisnetz._dateien.get(adresse);
        if (!d) {
            d = { hoerer: new Set(), vergeben: false };
            d.szene = Fotogenesisnetz._einzeln(adresse, f => { for (const h of d.hoerer) h(f); });
            d.szene.catch(() => Fotogenesisnetz._dateien.delete(adresse));       // ein Fehlschlag bleibt nicht liegen: das nächste Feld lädt neu
            Fotogenesisnetz._dateien.set(adresse, d);
        }
        const weg = () => d.hoerer.delete(fortschritt);
        d.hoerer.add(fortschritt), d.szene.then(weg, weg);
        return d.szene.then(szene => {
            if (!szene.getObjectsByProperty('isSkinnedMesh', true).length) return szene.clone();
            if (!d.vergeben) { d.vergeben = true; return szene; }
            return Fotogenesisnetz._einzeln(adresse, fortschritt);
        });
    }

    /** Die Datei im Worker holen (23.11.2026, `Pufferabruf`: 60 MB kamen im Seitenaufbau nach 1,1–3,5 s statt 0,6 s), dann wie `GLTFLoader.load` zerlegen. Die Bilder hat der Worker schon dekodiert
     *  (PNG 4096², 331–367 ms); der Loader bekommt sie über seinen eigenen `loadImageSource` mit einem Lader, der das fertige Bitmap gibt — ohne Bitmap sein `ImageBitmapLoader`, dieselben Optionen. */
    static _einzeln(adresse, fortschritt) {
        return Pufferabruf.holen(adresse, fortschritt, { bilder: true }).then(puffer => new Promise((fertig, fehler) => new GLTFLoader().register(parser => {
            const bilder = Pufferabruf.glbBilder.get(puffer) ?? {}, eigen = parser.loadImageSource.bind(parser);
            parser.loadImageSource = (i, lader) => eigen(i, bilder[i] ? { isImageBitmapLoader: true, load: (_a, gut) => gut(bilder[i]) } : lader);
            return { name: 'fotogenesis_bilder' };
        }).parse(puffer, LoaderUtils.extractUrlBase(new URL(adresse, location.href).href), gltf => fertig(gltf.scene), fehler)));
    }

    _laden(netz) {
        const e = { stand: 'laedt', szene: null, text: `${netz.name} wird geladen … (${netz.mb} MB)` };
        this._netze.set(netz.adresse, e);
        const anfang = performance.now();
        Fotogenesisnetz._datei(netz.adresse, fortschritt => {
            if (fortschritt.total) this.melden(`${netz.name} wird geladen … ${Math.round(100 * fortschritt.loaded / fortschritt.total)} % von ${netz.mb} MB`);
        }).then(szene => {
            Object.assign(e, { szene, stand: 'fertig', text: '', dauer: Math.round(performance.now() - anfang) });
            performance.mark(`fotogenesis-netz:${netz.name}`), this.fertig();      // Marke: Ladezeit im Tab messbar (der Abruf im Worker steht nicht in der Zeitleiste der Seite)
        }, fehler => {
            Object.assign(e, { stand: 'fehler', text: `${netz.name} nicht geladen: ${fehler?.message ?? fehler}` });
            console.warn(`Fotogenesisnetz: ${e.text}`);
            this.fertig();
        });
        return e;
    }

    /** Zeichner von `Meshgenesisansicht`: `d = {netz: {name, mb, adresse}, modus}`. */
    zeichnen(inhalt, _art, d) {
        if (!d.netz) {
            inhalt.userData.hinweis = 'Für diesen Job liegt kein Netz aus den Fotos vor.';
            return;
        }
        const e = this._netze.get(d.netz.adresse) ?? this._laden(d.netz);
        if (e.stand !== 'fertig') {
            inhalt.userData.hinweis = e.text;
            return;
        }
        e.szene.traverse(o => { o.layers.set(1); o.frustumCulled = false; });
        // Gehört nicht dem Feld (`Meshgenesisansicht._leeren` gibt es dann nicht frei) — beim nächsten Zeigen hängt es wieder ein.
        e.szene.userData.meshgenesisFremd = true;
        inhalt.add(e.szene);
        inhalt.userData.genesisErsatz = Fotogenesisnetz.ersatz(d.modus);
        this.dauer = e.dauer;
    }
}
