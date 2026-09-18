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
    /** Adresse -> {textur, fertig: Promise<THREE.Texture|null>} */
    static _vorrat = new Map();
    static _lader = null;

    /** Die Adresse eines Bibliothekspfads. */
    static adresse(pfad) {
        return Genesis9texturen.ADRESSE + pfad.split('/').map(encodeURIComponent).join('/');
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
        const textur = new THREE.Texture();
        textur.flipY = false;                    // die Bitmap kommt schon gewendet
        textur.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        textur.name = pfad.split('/').pop();
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
