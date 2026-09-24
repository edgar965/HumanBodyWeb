import * as THREE from 'three';

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
 * Bild wird mit `createImageBitmap` außerhalb des Hauptfadens dekodiert
 * (`ImageBitmapLoader`, `imageOrientation: 'flipY'` ersetzt Threes `flipY`,
 * das für Bitmaps nicht gilt). Farbraum und Verwendung hängen an der Datei:
 * eine Albedo ist immer sRGB, eine Normalenkarte immer linear, darum darf
 * der Vorrat sie teilen.
 */
export class Genesis9texturen {

    static ADRESSE = '/api/character/genesis9-figur/textur/';
    /** Alle Bilder eines Netzes in EINER Anfrage (`core/api/g9texturbuendel.py`). */
    static BUENDEL = '/api/character/genesis9-figur/texturbuendel/';
    /** Adresse -> {textur, fertig: Promise<THREE.Texture|null>} */
    static _vorrat = new Map();
    static _lader = null;

    /** Die Adresse eines Bibliothekspfads. */
    static adresse(pfad) {
        return Genesis9texturen.ADRESSE + pfad.split('/').map(encodeURIComponent).join('/');
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
        const offen = new Map();
        for (const e of eintraege || []) {
            const pfad = e?.pfad;
            if (!pfad || offen.has(pfad)) continue;
            const adresse = Genesis9texturen.adresse(pfad);
            if (Genesis9texturen._vorrat.has(adresse)) continue;   // liegt schon oder lädt
            let loesen;
            const fertig = new Promise(r => { loesen = r; });
            const textur = Genesis9texturen._leereTextur(pfad, e.srgb);
            offen.set(pfad, { textur, loesen });
            Genesis9texturen._vorrat.set(adresse, { textur, fertig });
        }
        if (offen.size) Genesis9texturen._buendelHolen(offen);
    }

    static _leereTextur(pfad, srgb) {
        const textur = new THREE.Texture();
        textur.flipY = false;                    // die Bitmap kommt schon gewendet
        textur.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        textur.name = pfad.split('/').pop();
        return textur;
    }

    static async _buendelHolen(offen) {
        let puffer = null;
        let kopf = null;
        let versatz = 0;
        try {
            const antwort = await fetch(Genesis9texturen.BUENDEL, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pfade: [...offen.keys()] }),
            });
            if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
            puffer = await antwort.arrayBuffer();
            const kopflaenge = new DataView(puffer).getUint32(0);
            kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, kopflaenge)));
            versatz = 4 + kopflaenge;
        } catch (fehler) {
            // Kein Bündel: jedes Bild einzeln, wie vor dem 23.09.2026.
            for (const [pfad, eintrag] of offen) Genesis9texturen._einzeln(pfad, eintrag);
            return;
        }
        for (const teil of kopf.teile || []) {
            const eintrag = offen.get(teil.pfad);
            if (!eintrag) continue;
            offen.delete(teil.pfad);
            if (!teil.art || !teil.bytes) {       // war zu groß fürs Bündel
                Genesis9texturen._einzeln(teil.pfad, eintrag);
                continue;
            }
            const roh = new Uint8Array(puffer, versatz, teil.bytes);
            versatz += teil.bytes;
            Genesis9texturen._bitmap(new Blob([roh], { type: teil.art }))
                .then(bitmap => Genesis9texturen._fertig(eintrag, bitmap))
                .catch(() => Genesis9texturen._einzeln(teil.pfad, eintrag));
        }
        // Was der Kopf nicht nennt (dürfte nicht vorkommen): einzeln holen.
        for (const [pfad, eintrag] of offen) Genesis9texturen._einzeln(pfad, eintrag);
    }

    static _bitmap(blob) {
        return createImageBitmap(blob, { imageOrientation: 'flipY', premultiplyAlpha: 'none' });
    }

    static _fertig(eintrag, bitmap) {
        eintrag.textur.image = bitmap;
        eintrag.textur.needsUpdate = true;
        eintrag.loesen(eintrag.textur);
    }

    /** Ein Bild des Bündels einzeln nachladen — in DASSELBE Texturobjekt. */
    static _einzeln(pfad, eintrag) {
        return Genesis9texturen.lader().loadAsync(Genesis9texturen.adresse(pfad))
            .then(bitmap => Genesis9texturen._fertig(eintrag, bitmap))
            .catch(() => {
                Genesis9texturen._vorrat.delete(Genesis9texturen.adresse(pfad));
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
            if (material) material.needsUpdate = true;
        };
        if (eintrag.textur.image) anwenden(eintrag.textur);
        else eintrag.fertig.then(anwenden);
        return eintrag.textur;
    }

    /** Der Vorratseintrag einer Datei — beim ersten Mal wird geladen. */
    static eintrag(pfad, srgb) {
        const adresse = Genesis9texturen.adresse(pfad);
        let eintrag = Genesis9texturen._vorrat.get(adresse);
        if (eintrag) return eintrag;
        const textur = Genesis9texturen._leereTextur(pfad, srgb);
        const fertig = Genesis9texturen.lader().loadAsync(adresse).then(bitmap => {
            textur.image = bitmap;
            textur.needsUpdate = true;
            return textur;
        }).catch(() => {
            Genesis9texturen._vorrat.delete(adresse);
            return null;
        });
        eintrag = { textur, fertig };
        Genesis9texturen._vorrat.set(adresse, eintrag);
        return eintrag;
    }

    static lader() {
        if (!Genesis9texturen._lader) {
            Genesis9texturen._lader = new THREE.ImageBitmapLoader();
            Genesis9texturen._lader.setOptions({ imageOrientation: 'flipY', premultiplyAlpha: 'none' });
        }
        return Genesis9texturen._lader;
    }

    /** Für Proben: wie viele Bilder liegen im Vorrat, wie viele sind fertig. */
    static stand() {
        let fertig = 0;
        for (const e of Genesis9texturen._vorrat.values()) if (e.textur.image) fertig++;
        return { bilder: Genesis9texturen._vorrat.size, fertig };
    }

    /** Alles freigeben (Seitenwechsel, Proben). */
    static leeren() {
        for (const e of Genesis9texturen._vorrat.values()) e.textur.dispose();
        Genesis9texturen._vorrat.clear();
    }
}
