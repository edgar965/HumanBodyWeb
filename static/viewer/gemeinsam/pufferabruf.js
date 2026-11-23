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
// Eingebettete Bilder eines GLB gleich hier dekodieren, mit den Optionen von threes ImageBitmapLoader (den nimmt der GLTFLoader) — {Bildnummer: ImageBitmap} oder null
const glbBilder = async ganz => {
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
    return bilder;
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
onmessage = async ({ data: { id, adresse, bilder: mitBildern } }) => {
    try {
        const k = await caches.open(KASTEN).catch(() => null), alt = k ? await k.match(adresse) : null, marke = alt?.headers.get('ETag');
        const antwort = await fetch(adresse, { credentials: 'same-origin', headers: marke ? { 'If-None-Match': marke } : {} });
        const kasten = antwort.status === 304 && !!alt;
        if (!kasten && !antwort.ok) { postMessage({ id, status: antwort.status }); return; }
        const ganz = kasten ? new Uint8Array(await alt.arrayBuffer()) : await lesen(id, antwort);
        const neu = kasten ? null : antwort.headers.get('ETag');
        // \`new Response\` kopiert die Bytes sofort — der Puffer darf danach in den Hauptfaden
        if (k && neu) k.put(adresse, new Response(ganz, { headers: { ETag: neu, 'X-Bytes': String(ganz.byteLength) } })).then(() => aufraeumen(k)).catch(() => {});
        const bilder = mitBildern ? await glbBilder(ganz).catch(() => null) : null;
        postMessage({ id, status: 200, puffer: ganz.buffer, bilder, kasten }, [ganz.buffer, ...Object.values(bilder || {})]);
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

    /**
     * @param {string} adresse  relativ zur Seite oder absolut
     * @param {(f: {loaded: number, total: number}) => void} [fortschritt]  wie `onProgress` von three (`total` 0, wenn unbekannt)
     * @param {{bilder?: boolean}} [wahl]  `bilder`: die eingebetteten Bilder eines GLB gleich im Worker dekodieren (23.11.2026: PSHuman-Textur 4096², 8,1 MB PNG, 331–367 ms) → `glbBilder`
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

    static _worker() {
        if (Pufferabruf._arbeiter || Pufferabruf.ausgefallen) return Pufferabruf._arbeiter;
        try {
            const url = URL.createObjectURL(new Blob([Pufferabruf.CODE], { type: 'text/javascript' }));
            const arbeiter = new Worker(url);
            arbeiter.onmessage = ({ data }) => Pufferabruf._angekommen(data);
            arbeiter.onerror = ereignis => Pufferabruf._ausfall(ereignis.message || 'Worker abgebrochen');
            Pufferabruf._arbeiter = arbeiter;
        } catch (fehler) {
            Pufferabruf._ausfall(fehler.message);
        }
        return Pufferabruf._arbeiter;
    }

    static _angekommen(d) {
        const offen = Pufferabruf._offen.get(d.id);
        if (!offen) return;
        if ('geladen' in d) {                                       // nur Fortschritt; die letzte Nachricht trägt `puffer`, `status` oder `fehler`
            offen.fortschritt?.({ loaded: d.geladen, total: d.gesamt });
            return;
        }
        Pufferabruf._offen.delete(d.id);
        // Marke: der Abruf im Worker steht nicht in der Zeitleiste der Seite (`performance.getEntriesByType('mark')`)
        if (d.puffer && d.bilder) Pufferabruf.glbBilder.set(d.puffer, d.bilder);
        if (d.puffer) performance.mark(`pufferabruf:${offen.adresse}`, { detail: { bytes: d.puffer.byteLength, kasten: d.kasten } }), offen.fertig(d.puffer);
        else offen.fehler(Object.assign(new Error(d.fehler ?? `HTTP ${d.status}`), { status: d.status ?? 0 }));
    }

    /** Fällt der Worker aus, laufen die offenen und alle weiteren Abrufe im Hauptfaden. */
    static _ausfall(grund) {
        console.warn('Pufferabruf: Worker ausgefallen (%s) — Abrufe im Hauptfaden', grund);
        Pufferabruf.ausgefallen = true;
        Pufferabruf._arbeiter?.terminate();
        Pufferabruf._arbeiter = null;
        const offen = [...Pufferabruf._offen.values()];
        Pufferabruf._offen.clear();
        for (const o of offen) Pufferabruf._direkt(o.adresse, o.fortschritt).then(o.fertig, o.fehler);
    }

    static async _direkt(adresse, fortschritt) {
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw Object.assign(new Error(`HTTP ${antwort.status}`), { status: antwort.status });
        const puffer = await antwort.arrayBuffer();
        fortschritt?.({ loaded: puffer.byteLength, total: puffer.byteLength });
        return puffer;
    }
}
