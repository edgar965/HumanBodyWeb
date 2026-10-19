import * as THREE from 'three';
import { Genesis9texturblock } from './genesis9texturblock.js';
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
 * Bild wird mit `createImageBitmap` außerhalb des Hauptfadens dekodiert
 * (`ImageBitmapLoader`, `imageOrientation: 'flipY'` ersetzt Threes `flipY`,
 * das für Bitmaps nicht gilt). Farbraum und Verwendung hängen an der Datei:
 * eine Albedo ist immer sRGB, eine Normalenkarte immer linear, darum darf
 * der Vorrat sie teilen.
 *
 * Seit 19.10.2026 wählt die Seite, in welcher Fassung die Bilder der Bibliothek kommen (`Texturweg`: verkleinert, eines nach dem anderen hochgeladen oder als
 * S3TC-Block) — die Wahl steht in der Adresse, also auch im Schlüssel des Vorrats und gerechneter Karten.
 */
export class Genesis9texturen {

    static ADRESSE = '/api/character/genesis9-figur/textur/';
    /** Alle Bilder eines Netzes in EINER Anfrage (`core/api/g9texturbuendel.py`). */
    static BUENDEL = '/api/character/genesis9-figur/texturbuendel/';
    /** Adresse -> {textur, fertig: Promise<THREE.Texture|null>} */
    static _vorrat = new Map();
    static _lader = null;

    /** Die Adresse eines Bibliothekspfads — eine eigene Adresse (`/api/…`, die Fotokacheln eines
     *  gespeicherten Modells, `Genesis9fototextur`) geht unverändert durch. */
    static adresse(pfad) {
        if (pfad.startsWith('/')) return pfad;
        const abfrage = Texturweg.abfrage();
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
        const offen = new Map();
        for (const e of eintraege || []) {
            const pfad = e?.pfad;
            // Das Bündel kennt nur die Daz-Bibliothek; eigene Adressen lädt `holen` einzeln.
            if (!pfad || offen.has(pfad) || pfad.startsWith('/')) continue;
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
        const textur = Texturweg.komprimiert() && !pfad.startsWith('/') ? Genesis9texturblock.leer() : new THREE.Texture();
        textur.flipY = false;                    // die Bitmap kommt schon gewendet (der Block auch)
        textur.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        textur.name = pfad.split('?')[0].split('/').filter(Boolean).pop();
        textur.userData.adresse = Genesis9texturen.adresse(pfad);   // woher das Bild kommt: Teil des Schlüssels gerechneter Karten (`Anatomievorrat`)
        return textur;
    }

    /** Länger darf die Adresse des Bündels nicht werden (Daphnes Anfragezeile) — sonst POST, das der Browser nicht behält. */
    static ADRESSE_MAX = 12000;

    /**
     * Das Bündel holen und Stück für Stück lesen (19.10.2026): GET, damit der Browser es behält (ETag, ein unverändertes Bündel kommt als 304 aus seinem
     * Speicher — vorher übertrug jedes Laden alles neu, an Mann1 48,6 MB in 5,2 s); und jedes Bild wird dekodiert, sobald SEINE Bytes da sind, nicht erst
     * nach dem ganzen Bündel. Scheitert etwas, kommt jedes Bild, das noch fehlt, einzeln (wie vor dem 23.09.2026).
     */
    static async _buendelHolen(offen) {
        try {
            const pfade = [...offen.keys()], wahl = Texturweg.abfrage() ? `?${Texturweg.abfrage()}` : '';
            const adresse = `${Genesis9texturen.BUENDEL}${wahl || '?'}${wahl ? '&' : ''}${pfade.map(p => `p=${encodeURIComponent(p)}`).join('&')}`;
            const antwort = adresse.length <= Genesis9texturen.ADRESSE_MAX ? await fetch(adresse)
                : await fetch(Genesis9texturen.BUENDEL + wahl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pfade }) });
            if (!antwort.ok || !antwort.body) throw new Error(`HTTP ${antwort.status}`);
            await Genesis9texturen._buendelLesen(antwort.body.getReader(), offen);
        } catch (fehler) {
            // Was noch fehlt (kein Bündel, Strom abgerissen): einzeln.
        }
        for (const [pfad, eintrag] of offen) Genesis9texturen._einzeln(pfad, eintrag);
    }

    /** `[4 Byte Kopflänge][Kopf][Bild 1][Bild 2] …` aus dem Strom: jedes Bild an `_bitmap`, sobald es ganz da ist; erledigte fallen aus `offen`. */
    static async _buendelLesen(leser, offen) {
        const stuecke = [];                            // {start, daten}: empfangen, absolute Lage im Strom
        let da = 0, teile = null, naechster = 0, versatz = 0;
        const bereich = (von, bis) => stuecke.filter(s => s.start < bis && s.start + s.daten.length > von)
            .map(s => s.daten.subarray(Math.max(0, von - s.start), Math.min(s.daten.length, bis - s.start)));
        const kopie = (von, bis) => { const aus = new Uint8Array(bis - von); let p = 0; for (const t of bereich(von, bis)) { aus.set(t, p); p += t.length; } return aus; };
        for (;;) {
            const { done, value } = await leser.read();
            if (value?.length) { stuecke.push({ start: da, daten: value }); da += value.length; }
            if (!teile && da >= 4) {
                const laenge = new DataView(kopie(0, 4).buffer).getUint32(0);
                if (da >= 4 + laenge) { teile = JSON.parse(new TextDecoder().decode(kopie(4, 4 + laenge))).teile || []; versatz = 4 + laenge; }
            }
            while (teile && naechster < teile.length) {
                const teil = teile[naechster], eintrag = offen.get(teil.pfad);
                const groesse = teil.art && teil.bytes ? teil.bytes : 0;
                if (da < versatz + groesse) break;
                naechster += 1;
                if (!eintrag) { versatz += groesse; continue; }
                offen.delete(teil.pfad);
                if (!groesse) { Genesis9texturen._einzeln(teil.pfad, eintrag); continue; }       // war zu groß fürs Bündel
                const blob = new Blob(bereich(versatz, versatz + groesse), { type: teil.art });
                versatz += groesse;
                Genesis9texturen._bitmap(blob).then(bitmap => Genesis9texturen._fertig(eintrag, bitmap))
                    .catch(() => Genesis9texturen._einzeln(teil.pfad, eintrag));
            }
            while (stuecke.length && stuecke[0].start + stuecke[0].daten.length <= versatz) stuecke.shift();     // Gelesenes freigeben
            if (done) return;
        }
    }

    /** Blob → Bitmap, ein S3TC-Block (Weg C, `Genesis9texturblock`) → `{bild, stufen, …}`. */
    static _bitmap(blob) {
        if (blob.type === Genesis9texturblock.ART) return Genesis9texturblock.lesen(blob);
        return createImageBitmap(blob, { imageOrientation: 'flipY', premultiplyAlpha: 'none' });
    }

    /** Eine Adresse einzeln laden: der Block über `fetch` (der `ImageBitmapLoader` kennt ihn nicht), sonst wie bisher. */
    static _laden(adresse) {
        if (!adresse.includes('format=bc')) return Genesis9texturen.lader().loadAsync(adresse);
        return fetch(adresse).then(antwort => {
            if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
            return antwort.blob();
        }).then(blob => Genesis9texturen._bitmap(blob));
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
        return Genesis9texturen._laden(Genesis9texturen.adresse(pfad))
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
            if (material) { material.userData?.teilnach?.(); material.needsUpdate = true; }   // eigene Materialwerte nach dem Bild wieder auflegen (`Genesis9teilmaterial`)
        };
        if (eintrag.textur.image) anwenden(eintrag.textur);
        else {
            Genesis9texturen._zaehlen(material, 1);
            eintrag.fertig.then(textur => { Genesis9texturen._zaehlen(material, -1); anwenden(textur); });
        }
        return eintrag.textur;
    }

    /**
     * Material → Zahl der Bilder, die `holen` ihm noch einsetzt (19.10.2026). Das Material zeigt nicht, ob ein Bild unterwegs ist (`map` steht erst im
     * Rückruf): `Anatomiehaut` maß den Hautton am Körper ohne Karte — die Farbe vor den Bildern — und hielt die Scham für fertig; `Zeichenstand`
     * meldet „Texturen". Eine WeakMap, nicht `userData`: ein Klon des Materials (`Material.clone`, Weichgewebe) bekäme den Zähler mit und nie zurück.
     */
    static _offen = new WeakMap();

    static _zaehlen(material, schritt) {
        if (!material) return;
        const n = (Genesis9texturen._offen.get(material) || 0) + schritt;
        if (n > 0) Genesis9texturen._offen.set(material, n); else Genesis9texturen._offen.delete(material);
    }

    /** Wie viele Bilder `holen` diesem Material noch einsetzt. */
    static offen(material) {
        return Genesis9texturen._offen.get(material) || 0;
    }

    /** Der Vorratseintrag einer Datei — beim ersten Mal wird geladen. */
    static eintrag(pfad, srgb) {
        const adresse = Genesis9texturen.adresse(pfad);
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
