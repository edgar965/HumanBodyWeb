import * as THREE from 'three';
import { Genesis9texturbasis } from './genesis9texturbasis.js';
import { Genesis9texturblock } from './genesis9texturblock.js';
import { Genesis9texturbuendel } from './genesis9texturbuendel.js';
import { Genesis9texturzaehler } from './genesis9texturzaehler.js';
import { Pufferabruf } from './pufferabruf.js';
import { Texturweg } from './texturweg.js';

/**
 * Genesis9texturen — jede Bilddatei einer Genesis-9-Figur EINMAL im Browser.
 *
 * BEFUND (Edgar, 18.09.2026 abends: „laden Ursula dauert lange, offenbar
 * lädt die Figur 2 Mal, nach dem ersten Laden sind Artefakte zu sehen …
 * performance beim rotieren schlecht, ruckelt"): `Genesis9netz.texturen`
 * rief bei JEDEM Netzbau `TextureLoader.load` für jedes Bild — beim Käfig-
 * Zug, beim feinen Zug, bei jedem Reglerzug. Der Browser holte die Datei
 * zwar aus seinem Cache, dekodierte sie aber neu (8K-JPEG: Sekunden) und lud
 * sie neu auf die GPU (8192² RGBA = 268 MB je Kachel, fünf Kacheln mit
 * Strg+Alt+H); die alten Texturen blieben auf der GPU liegen, weil
 * `Material.dispose()` sie nicht freigibt. Sichtbar: nach dem Käfig stand
 * der feine Körper sekundenlang WEISS (Sichtprobe `ProjektTemp/g9_p9_
 * gemischt_koerper2_kleid0.jpg`), und jeder Upload hielt die Zeichenschleife
 * an.
 *
 * Jetzt: ein Vorrat je Adresse. Ein zweites Netz mit demselben Bild bekommt
 * dasselbe `THREE.Texture`-Objekt — schon dekodiert, schon auf der GPU. Das
 * Bild wird mit `createImageBitmap` im Worker dekodiert (`Pufferabruf.bild`, seit
 * 23.11.2026 — vorher im Hauptfaden, dort rechnete Chrome Spiegeln und Umrechnen;
 * `imageOrientation: 'flipY'` ersetzt Threes `flipY`, das für Bitmaps nicht gilt). Farbraum und Verwendung hängen an der Datei:
 * eine Albedo ist immer sRGB, eine Normalenkarte immer linear, darum darf
 * der Vorrat sie teilen.
 *
 * Seit 19.10.2026 wählt die Seite, in welcher Fassung die Bilder der Bibliothek kommen (`Texturweg`: verkleinert, eines nach dem anderen hochgeladen oder als
 * S3TC-Block) — die Wahl steht in der Adresse, also auch im Schlüssel des Vorrats und gerechneter Karten.
 */
export class Genesis9texturen {

    static ADRESSE = '/api/character/genesis9-figur/textur/';
    /** Adresse -> {textur, fertig: Promise<THREE.Texture|null>} */
    static _vorrat = new Map();

    /** Die Adresse eines Bibliothekspfads — eine eigene Adresse (`/api/…`, die Fotokacheln eines
     *  gespeicherten Modells, `Genesis9fototextur`) geht unverändert durch. `srgb`: Farbbild — nur bei UASTC Teil der Adresse (`Texturweg.abfrage`). */
    static adresse(pfad, srgb = true) {
        if (pfad.startsWith('/')) return pfad;
        const abfrage = Texturweg.abfrage(srgb);
        return Genesis9texturen.ADRESSE + pfad.split('/').map(encodeURIComponent).join('/') + (abfrage ? `?${abfrage}` : '');
    }

    /**
     * Die Bilder EINES Netzes in EINER Anfrage vorladen (23.09.2026, Edgar:
     * „weniger einzelne Texturanfragen (Bündelung/Sprite)").
     *
     * Chrome hält je Herkunft nur SECHS Verbindungen offen (HTTP/1.1, und
     * Daphne kann kein HTTP/2): die rund vierzig Bilder einer angezogenen
     * Figur liefen in sieben Wellen, jede Welle so langsam wie ihr langsamstes
     * Bild. Hier kommen sie als ein Datenstrom (`g9texturbuendel.py`).
     *
     * NICHT AWAITEN: Die Platzhalter stehen VOR dem ersten `await` im Vorrat —
     * `Genesis9netz.bauen` läuft gleich danach synchron weiter, findet sie und
     * startet deshalb KEINE Einzelanfragen. Wer schon eine Textur in der Hand
     * hat, behält sie: scheitert das Bündel (oder lässt der Server ein zu
     * großes Bild draußen), wird DASSELBE Texturobjekt einzeln nachgeladen —
     * nie gelöscht, sonst bliebe ein ausgegebenes Material für immer weiß.
     *
     * @param eintraege [{pfad, srgb}] — `srgb` nur für Farbbilder (Albedo).
     */
    static vorladen(eintraege) {
        const gruppen = new Map();               // Abfrage → (Pfad → Eintrag): bei UASTC je eine Anfrage für Farb- und Datenbilder, sonst eine
        for (const e of eintraege || []) {
            const pfad = e?.pfad;
            // Das Bündel kennt nur die Daz-Bibliothek; eigene Adressen lädt `holen` einzeln.
            if (!pfad || pfad.startsWith('/')) continue;
            const srgb = !!e.srgb, wahl = Texturweg.abfrage(srgb);
            const offen = gruppen.get(wahl) || new Map();
            if (offen.has(pfad)) continue;
            const adresse = Genesis9texturen.adresse(pfad, srgb);
            if (Genesis9texturen._vorrat.has(adresse)) continue;   // liegt schon oder lädt
            let loesen;
            const fertig = new Promise(r => { loesen = r; });
            const textur = Genesis9texturen._leereTextur(pfad, srgb);
            offen.set(pfad, { textur, loesen, srgb });
            gruppen.set(wahl, offen);
            Genesis9texturen._vorrat.set(adresse, { textur, fertig });
        }
        for (const [wahl, offen] of gruppen) Genesis9texturbuendel.holen(offen, wahl, { bild: Genesis9texturen._ausBuendel, einzeln: Genesis9texturen._einzeln });
    }

    static _leereTextur(pfad, srgb) {
        const textur = Texturweg.komprimiert() && !pfad.startsWith('/') ? Genesis9texturblock.leer() : new THREE.Texture();
        textur.flipY = false;                    // die Bitmap kommt schon gewendet (der Block auch)
        textur.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        textur.name = pfad.split('?')[0].split('/').filter(Boolean).pop();
        textur.userData.adresse = Genesis9texturen.adresse(pfad, srgb);   // woher das Bild kommt: Teil des Schlüssels gerechneter Karten (`Anatomievorrat`)
        return textur;
    }

    /** Ein Bild des Bündels einsetzen (`Genesis9texturbuendel`): Blob oder Ausschnitt des Puffers; scheitert es, kommt es einzeln. */
    static _ausBuendel(pfad, quelle, eintrag) {
        Genesis9texturen._bitmap(quelle, Genesis9texturen.adresse(pfad, eintrag.srgb)).then(bild => Genesis9texturen._fertig(eintrag, bild))
            .catch(() => Genesis9texturen._einzeln(pfad, eintrag));
    }

    /** Blob → Bitmap, ein S3TC-Block (Weg C, `Genesis9texturblock`) oder UASTC (`Genesis9texturbasis`) → `{bild, stufen, …}`. Scheitert UASTC im Browser (Wandler
     *  nicht geladen), kommt derselbe Pfad als S3TC-Block (`adresse` ohne Abfrage + `format=bc`). */
    static _bitmap(blob, adresse = '') {
        if (blob.type === Genesis9texturblock.ART) return Genesis9texturblock.lesen(blob);
        if (blob.puffer) blob = new Blob([new Uint8Array(blob.puffer, blob.ab, blob.bytes)], { type: blob.type });      // Ausschnitt eines Bündels, kein Block
        if (blob.type === Genesis9texturbasis.ART) {
            return Genesis9texturbasis.lesen(blob).catch(fehler => {
                console.warn(`Genesis9texturen: UASTC nicht lesbar (${fehler?.message || fehler}) — S3TC-Block für ${adresse.split('?')[0].split('/').pop()}`);
                return Genesis9texturen._laden(`${adresse.split('?')[0]}?format=bc`);
            });
        }
        // im Worker (`Pufferabruf.bild`, 23.11.2026): Spiegeln und Umrechnen beim Auflösen kosteten im Hauptfaden 6–13 ms je 2048²-Bild, unsichtbar für LoAF und Profiler
        return Pufferabruf.bild(blob, Genesis9texturen.OPTIONEN);
    }

    /** Wie bis 23.11.2026 der `ImageBitmapLoader`: `imageOrientation: 'flipY'` ersetzt Threes `flipY`, ohne Vormultiplikation. */
    static OPTIONEN = { imageOrientation: 'flipY', premultiplyAlpha: 'none' };

    /** Eine Adresse einzeln laden — jedes Format über `fetch`, das Bild im Worker (`_bitmap`; bis 23.11.2026 Bilder über threes `ImageBitmapLoader` im Hauptfaden). */
    static _laden(adresse) {
        if (Genesis9texturbuendel.perWorker() && adresse.includes('format=')) {          // GPU-Block der Bibliothek (11 MB je 4096er): über den Worker, erkannt am Inhalt
            return Pufferabruf.holen(adresse, null, { kasten: Genesis9texturbuendel.KASTEN }).then(puffer => Genesis9texturen._bitmap(
                Genesis9texturblock.erkannt(puffer) ? { puffer, ab: 0, bytes: puffer.byteLength, type: Genesis9texturblock.ART }
                    : new Blob([puffer], { type: adresse.includes('format=uastc') ? Genesis9texturbasis.ART : '' }), adresse));
        }
        return fetch(adresse, { credentials: 'same-origin' }).then(antwort => {
            if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
            return antwort.blob();
        }).then(blob => Genesis9texturen._bitmap(blob, adresse));
    }

    /** Das Bild an die Textur hängen — bei Weg B in der Reihe, je Aufgabe eines, gleich auf die Karte (`Texturweg.einreihen`). */
    static _setzen(textur, inhalt) {
        return Texturweg.einreihen(textur, () => {
            if (Genesis9texturblock.ist(inhalt)) Genesis9texturblock.setzen(textur, inhalt);
            else textur.image = inhalt;
            textur.needsUpdate = true;
        });
    }

    static _fertig(eintrag, bitmap) {
        return Genesis9texturen._setzen(eintrag.textur, bitmap).then(() => eintrag.loesen(eintrag.textur));
    }

    /** Ein Bild des Bündels einzeln nachladen — in DASSELBE Texturobjekt. */
    static _einzeln(pfad, eintrag) {
        const adresse = Genesis9texturen.adresse(pfad, eintrag.srgb);
        return Genesis9texturen._laden(adresse)
            .then(bitmap => Genesis9texturen._fertig(eintrag, bitmap))
            .catch(() => {
                Genesis9texturen._vorrat.delete(adresse);
                eintrag.loesen(null);
            });
    }

    /**
     * Ein Bild holen — `danach(textur)` läuft, sobald das Bild da ist (bei
     * einem Treffer im Vorrat sofort), und danach `material.needsUpdate`.
     * `srgb`: Farbbild (Albedo), sonst lineare Daten (Normalen, Rauheit …).
     */
    static holen(pfad, srgb, material, danach) {
        const eintrag = Genesis9texturen.eintrag(pfad, srgb);
        const anwenden = textur => {
            if (!textur) return;
            danach(textur);
            if (material) { material.userData?.teilnach?.(); material.userData?.stoffnach?.(); material.needsUpdate = true; }   // eigene Materialwerte nach dem Bild wieder auflegen (`Genesis9teilmaterial`, `Stoffwerte`)
        };
        if (eintrag.textur.image) anwenden(eintrag.textur);
        else {
            // die Bilder eines Materials setzen gemeinsam ein — ein Programmwechsel statt einer je Bild (23.11.2026, `Genesis9texturzaehler`)
            Genesis9texturzaehler.unterwegs(material);
            eintrag.fertig.then(textur => Genesis9texturzaehler.angekommen(material, () => anwenden(textur)));
        }
        return eintrag.textur;
    }

    /** Wie viele Bilder `holen` diesem Material noch einsetzt (`Genesis9texturzaehler`). */
    static offen(material) {
        return Genesis9texturzaehler.offen(material);
    }

    /** Der Vorratseintrag einer Datei — beim ersten Mal wird geladen. */
    static eintrag(pfad, srgb) {
        const adresse = Genesis9texturen.adresse(pfad, srgb);
        let eintrag = Genesis9texturen._vorrat.get(adresse);
        if (eintrag) return eintrag;
        const textur = Genesis9texturen._leereTextur(pfad, srgb);
        const fertig = Genesis9texturen._laden(adresse).then(bild => Genesis9texturen._setzen(textur, bild)).then(() => textur).catch(() => {
            Genesis9texturen._vorrat.delete(adresse);
            return null;
        });
        eintrag = { textur, fertig };
        Genesis9texturen._vorrat.set(adresse, eintrag);
        return eintrag;
    }

    /** Für Proben: wie viele Bilder liegen im Vorrat, wie viele sind fertig. */
    static stand() {
        let fertig = 0;
        for (const e of Genesis9texturen._vorrat.values()) if (e.textur.image) fertig++;
        return { bilder: Genesis9texturen._vorrat.size, fertig };
    }

    /**
     * Warten, bis JEDES Bild im Vorrat entweder da ist oder endgültig
     * gescheitert ist (Fund 26.09.2026: ein Export direkt nach dem Laden
     * einer Figur traf `material.map.image === undefined`, weil `vorladen()`
     * bewusst NICHT wartet — `GLTFExporter`/`ObjMtl` lassen ein Bild ohne
     * `.image` einfach weg, still, ohne Fehler). Bereits fertige Einträge
     * kosten nichts (Promise ist schon aufgelöst).
     */
    static wartenAufAlle() {
        return Promise.all([...Genesis9texturen._vorrat.values()].map(e => e.fertig));
    }

    /** Alles freigeben (Seitenwechsel, Proben). */
    static leeren() {
        for (const e of Genesis9texturen._vorrat.values()) e.textur.dispose();
        Genesis9texturen._vorrat.clear();
    }
}
