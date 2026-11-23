/**
 * Pufferabruf — große Binärantworten (Anzeigenetze, GLB) in einem Worker holen; der Puffer kommt ohne Kopie in den Hauptfaden (23.11.2026, Edgar: „alles schneller, max 2. s“).
 *
 * Gemessen an /foto-genesis/test/iphone_mit_lidar_dycheck_space_out/ (Chrome-Tab, 23.11.2026): das Haarnetz (106 MB) kam allein in 0,63–1,1 s, im Seitenaufbau in 2,9–4,9 s —
 * Chrome nimmt den Rumpf einer `fetch`-Antwort im Hauptfaden entgegen, und der war in den ersten 8 s zu 3,5 s blockiert (Long Animation Frames, größte 1,0/1,3/1,2 s). Solange er
 * blockiert, liest niemand die Leitung leer, der Server wartet. Im Worker läuft das Lesen weiter, egal was der Hauptfaden tut.
 *
 *     const puffer = await Pufferabruf.holen(adresse, ({ loaded, total }) => …);   // wirft bei HTTP-Fehler einen Error mit `status`
 *
 * Ein Worker für alle Abrufe der Seite (aus einer Blob-Adresse: keine Vorlage braucht einen Pfad); ohne Worker der Abruf im Hauptfaden wie bisher.
 * Antworten mit ETag (Server `Netzpackung`) legt der Worker im CacheStorage ab und fragt beim nächsten Mal mit `If-None-Match` nach; bei 304 liest er von der Platte
 * (Haar 106 MB: 189–209 ms statt 0,85–1,8 s übers Netz). Chromes HTTP-Zwischenspeicher nimmt so große Antworten nicht (60 MB mit ETag: nie nachgefragt, 23.11.2026).
 */
export class Pufferabruf {
    /** Code des Workers: liest den Rumpf stückweise (Fortschritt höchstens alle 100 ms), setzt ihn zusammen und gibt den Puffer ab. */
    static CODE = `
const melden = (id, geladen, gesamt) => postMessage({ id, geladen, gesamt });
// Eingebettete Bilder eines GLB gleich hier dekodieren, mit den Optionen von threes ImageBitmapLoader (den nimmt der GLTFLoader), und die übrigen Pufferansichten herausschneiden:
// der GLTFLoader kopierte im Hauptfaden den ganzen BIN-Block und daraus jede Ansicht (PSHuman 60 MB, Parsen 47–52 ms; mit JSON und fertigen Ansichten 1,3–2,2 ms, 24.11.2026)
// — {bilder: {Bildnummer: ImageBitmap}, ansichten: [ArrayBuffer oder null für Bild und fremde Puffer], json} oder null
const glbTeile = async ganz => {
    const dv = new DataView(ganz.buffer);
    if (ganz.byteLength < 28 || dv.getUint32(0, true) !== 0x46546C67) return null;
    const jl = dv.getUint32(12, true), json = JSON.parse(new TextDecoder().decode(ganz.subarray(20, 20 + jl))), bin = 28 + jl, bilder = {};
    if (dv.getUint32(24 + jl, true) !== 0x004E4942) return null;
    for (const [i, b] of (json.images || []).entries()) {
        const v = b.bufferView !== undefined ? json.bufferViews[b.bufferView] : null;
        if (!v || (v.buffer ?? 0) !== 0) continue;
        const ab = bin + (v.byteOffset || 0);
        bilder[i] = await createImageBitmap(new Blob([ganz.subarray(ab, ab + v.byteLength)], { type: b.mimeType }), { premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
    }
    const bildAnsicht = new Set((json.images || []).map(b => b.bufferView));
    const ansichten = (json.bufferViews || []).map((v, i) => bildAnsicht.has(i) || (v.buffer ?? 0) !== 0 ? null
        : ganz.slice(bin + (v.byteOffset || 0), bin + (v.byteOffset || 0) + v.byteLength).buffer);
    return { bilder, ansichten, json };
};
// Antworten mit ETag (Server \`Netzpackung\`) bleiben im CacheStorage, höchstens GRENZE Bytes, die ältesten fallen weg; nachgefragt wird jedes Mal, 304 = unverändert
const KASTEN = 'pufferabruf-1', GRENZE = 1536 * 1048576;
const aufraeumen = async k => {
    const schluessel = await k.keys(), groessen = [];
    for (const s of schluessel) groessen.push(Number((await k.match(s))?.headers.get('X-Bytes')) || 0);
    for (let i = schluessel.length - 1, summe = 0; i >= 0; i--) if ((summe += groessen[i]) > GRENZE) await k.delete(schluessel[i]);
};
const lesen = async (id, antwort) => {
    // Content-Length ist bei gepacktem Rumpf (Content-Encoding) die gepackte Größe — dann nur „geladen“ melden
    const gesamt = antwort.headers.get('Content-Encoding') ? 0 : Number(antwort.headers.get('Content-Length')) || 0;
    const leser = antwort.body.getReader(), teile = [];
    let geladen = 0, zuletzt = 0;
    for (;;) {
        const { done, value } = await leser.read();
        if (done) break;
        teile.push(value);
        geladen += value.byteLength;
        const jetzt = performance.now();
        if (jetzt - zuletzt > 100) { zuletzt = jetzt; melden(id, geladen, gesamt); }
    }
    const ganz = new Uint8Array(geladen);
    let ab = 0;
    for (const t of teile) { ganz.set(t, ab); ab += t.byteLength; }
    return ganz;
};
// Ein einzelnes Bild (23.11.2026, \`Pufferabruf.bild\`): createImageBitmap HIER, mit den Optionen des Aufrufers — Spiegeln (flipY) und Vormultiplikation rechnet Chrome beim Auflösen
// im Faden des Aufrufers; im Hauptfaden waren das die unbeschrifteten 5–13-ms-Aufgaben beim Laden (ETW + CPU-Abtastung: 233 von 255 Proben in ImageBitmap::ImageBitmap)
const bildLesen = async (id, blob, optionen) => {
    try {
        const bitmap = await createImageBitmap(blob, optionen || {});
        postMessage({ id, bitmap }, [bitmap]);
    } catch (fehler) {
        postMessage({ id, fehler: String(fehler?.message ?? fehler) });
    }
};
onmessage = async ({ data: { id, adresse, bilder: mitBildern, blob, optionen } }) => {
    if (blob) { bildLesen(id, blob, optionen); return; }
    try {
        const k = await caches.open(KASTEN).catch(() => null), alt = k ? await k.match(adresse) : null, marke = alt?.headers.get('ETag');
        const antwort = await fetch(adresse, { credentials: 'same-origin', headers: marke ? { 'If-None-Match': marke } : {} });
        const kasten = antwort.status === 304 && !!alt;
        if (!kasten && !antwort.ok) { postMessage({ id, status: antwort.status }); return; }
        const ganz = kasten ? new Uint8Array(await alt.arrayBuffer()) : await lesen(id, antwort);
        const neu = kasten ? null : antwort.headers.get('ETag');
        // \`new Response\` kopiert die Bytes sofort — der Puffer darf danach in den Hauptfaden
        if (k && neu) k.put(adresse, new Response(ganz, { headers: { ETag: neu, 'X-Bytes': String(ganz.byteLength) } })).then(() => aufraeumen(k)).catch(() => {});
        const glb = mitBildern ? await glbTeile(ganz).catch(() => null) : null;
        postMessage({ id, status: 200, puffer: ganz.buffer, glb, kasten }, [ganz.buffer, ...Object.values(glb?.bilder || {}), ...(glb?.ansichten || []).filter(Boolean)]);
    } catch (fehler) {
        postMessage({ id, fehler: String(fehler?.message ?? fehler) });
    }
};`;

    static _arbeiter = null;
    static _offen = new Map();
    static _zaehler = 0;
    static ausgefallen = false;
    /** Puffer eines GLB → {Bildnummer: ImageBitmap}, im Worker dekodiert (`holen(…, {bilder: true})`, `Fotogenesisnetz`); fehlt ohne Worker. */
    static glbBilder = new WeakMap();
    /** Puffer eines GLB → {json, ansichten}: das gelesene JSON und jede Pufferansicht als eigener Puffer (Bilder: null), im Worker geschnitten; fehlt ohne Worker. */
    static glbTeile = new WeakMap();

    /**
     * @param {string} adresse  relativ zur Seite oder absolut
     * @param {(f: {loaded: number, total: number}) => void} [fortschritt]  wie `onProgress` von three (`total` 0, wenn unbekannt)
     * @param {{bilder?: boolean}} [wahl]  `bilder`: die eingebetteten Bilder eines GLB gleich im Worker dekodieren (23.11.2026: PSHuman-Textur 4096², 8,1 MB PNG, 331–367 ms) → `glbBilder`,
     *   dazu JSON und Pufferansichten → `glbTeile` (24.11.2026)
     * @returns {Promise<ArrayBuffer>}
     */
    static holen(adresse, fortschritt, wahl = {}) {
        const absolut = new URL(adresse, location.href).href;      // ein Worker aus einer Blob-Adresse löst keine relativen Adressen auf
        const arbeiter = Pufferabruf._worker();
        if (!arbeiter) return Pufferabruf._direkt(absolut, fortschritt);
        const id = ++Pufferabruf._zaehler;
        return new Promise((fertig, fehler) => {
            Pufferabruf._offen.set(id, { fertig, fehler, fortschritt, adresse: absolut });
            arbeiter.postMessage({ id, adresse: absolut, bilder: !!wahl.bilder });
        });
    }

    /**
     * Ein Bild dekodieren wie `createImageBitmap(blob, optionen)`, aber im Worker: Chrome dekodiert zwar immer außerhalb, wendet die Optionen (`imageOrientation: 'flipY'`,
     * `premultiplyAlpha: 'none'`) aber beim Auflösen im Faden des Aufrufers an — 2048² kostete dort 6–13 ms je Bild ohne jede Spur in LoAF oder Profiler (23.11.2026, ETW + WPR an
     * /foto-genesis/test/iphone_mit_lidar_dycheck_space_out/: 30 leere Aufgaben, 270 ms; 233 von 255 CPU-Proben in `ImageBitmap::ImageBitmap → SkImage::readPixels`). Das Bitmap kommt
     * ohne Kopie zurück. Ohne Worker im Hauptfaden wie bisher.
     * @returns {Promise<ImageBitmap>}
     */
    static bild(blob, optionen = {}) {
        const arbeiter = Pufferabruf._worker('_bildarbeiter');      // eigener Worker: die Umrechnung soll das Lesen großer Netze im ersten nicht aufhalten
        if (!arbeiter) return createImageBitmap(blob, optionen);
        const id = ++Pufferabruf._zaehler;
        return new Promise((fertig, fehler) => {
            Pufferabruf._offen.set(id, { fertig, fehler, blob, optionen });
            arbeiter.postMessage({ id, blob, optionen });
        });
    }

    static _bildarbeiter = null;

    /** `feld`: `_arbeiter` (Abrufe) oder `_bildarbeiter` (Bilder) — derselbe Code, zwei Instanzen. */
    static _worker(feld = '_arbeiter') {
        if (Pufferabruf[feld] || Pufferabruf.ausgefallen) return Pufferabruf[feld];
        try {
            Pufferabruf._url ??= URL.createObjectURL(new Blob([Pufferabruf.CODE], { type: 'text/javascript' }));
            const arbeiter = new Worker(Pufferabruf._url);
            arbeiter.onmessage = ({ data }) => Pufferabruf._angekommen(data);
            arbeiter.onerror = ereignis => Pufferabruf._ausfall(ereignis.message || 'Worker abgebrochen');
            Pufferabruf[feld] = arbeiter;
        } catch (fehler) {
            Pufferabruf._ausfall(fehler.message);
        }
        return Pufferabruf[feld];
    }

    static _angekommen(d) {
        const offen = Pufferabruf._offen.get(d.id);
        if (!offen) return;
        if ('geladen' in d) {                                       // nur Fortschritt; die letzte Nachricht trägt `puffer`, `status` oder `fehler`
            offen.fortschritt?.({ loaded: d.geladen, total: d.gesamt });
            return;
        }
        Pufferabruf._offen.delete(d.id);
        if (d.bitmap) { offen.fertig(d.bitmap); return; }
        if (offen.blob && d.fehler) { offen.fehler(new Error(d.fehler)); return; }
        // Marke: der Abruf im Worker steht nicht in der Zeitleiste der Seite (`performance.getEntriesByType('mark')`)
        if (d.puffer && d.glb) Pufferabruf.glbBilder.set(d.puffer, d.glb.bilder), Pufferabruf.glbTeile.set(d.puffer, d.glb);
        if (d.puffer) performance.mark(`pufferabruf:${offen.adresse}`, { detail: { bytes: d.puffer.byteLength, kasten: d.kasten } }), offen.fertig(d.puffer);
        else offen.fehler(Object.assign(new Error(d.fehler ?? `HTTP ${d.status}`), { status: d.status ?? 0 }));
    }

    /** Fällt der Worker aus, laufen die offenen und alle weiteren Abrufe im Hauptfaden. */
    static _ausfall(grund) {
        console.warn('Pufferabruf: Worker ausgefallen (%s) — Abrufe im Hauptfaden', grund);
        Pufferabruf.ausgefallen = true;
        Pufferabruf._arbeiter?.terminate();
        Pufferabruf._bildarbeiter?.terminate();
        Pufferabruf._arbeiter = Pufferabruf._bildarbeiter = null;
        const offen = [...Pufferabruf._offen.values()];
        Pufferabruf._offen.clear();
        for (const o of offen) (o.blob ? createImageBitmap(o.blob, o.optionen) : Pufferabruf._direkt(o.adresse, o.fortschritt)).then(o.fertig, o.fehler);
    }

    static async _direkt(adresse, fortschritt) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw Object.assign(new Error(`HTTP ${antwort.status}`), { status: antwort.status });
        const puffer = await antwort.arrayBuffer();
        fortschritt?.({ loaded: puffer.byteLength, total: puffer.byteLength });
        return puffer;
    }
}
