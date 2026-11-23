/**
 * Genesis9texturzaehler — wie viele Bilder `Genesis9texturen.holen` einem Material noch einsetzt (19.10.2026), und die Bilder eines Materials gemeinsam einsetzen (23.11.2026).
 *
 * Zählen: Das Material zeigt nicht, ob ein Bild unterwegs ist (`map` steht erst im Rückruf): `Anatomiehaut` maß den Hautton am Körper ohne Karte — die Farbe vor den Bildern — und hielt
 * die Scham für fertig; `Zeichenstand` meldet „Texturen“. Eine WeakMap, nicht `userData`: ein Klon des Materials (`Material.clone`, Weichgewebe) bekäme den Zähler mit und nie zurück.
 *
 * Gemeinsam einsetzen (23.11.2026, Edgar: „löse das“ — lange Bilder beim Laden der Foto-Genesis-Testseite): Jedes Bild, das einen leeren Platz füllt (Farb-, Normal-, Rauheits-,
 * Glanzkarte …), gibt dem Material ein neues Shaderprogramm. Kamen die Bilder einzeln, übersetzte three je Material mehrere Programme nacheinander, die meisten nur für ein paar
 * Bilder gebraucht (gemessen an iphone_mit_lidar: 48 Programme beim Laden, im Zeichnen 64–208 ms Warten auf das Übersetzen). Jetzt wartet ein angekommenes Bild, bis keins dieses
 * Materials mehr fehlt — höchstens `SAMMELN_MS`, damit ein langsames Bild die übrigen nicht aufhält —, dann setzen alle in einer Aufgabe ein: ein Programmwechsel je Material.
 */
export class Genesis9texturzaehler {
    static SAMMELN_MS = 300;
    static _offen = new WeakMap();
    /** Material → {liste: [Einsetzen je angekommenem Bild], uhr} */
    static _wartend = new WeakMap();

    /** Ein Bild ist für `material` unterwegs. */
    static unterwegs(material) {
        if (material) Genesis9texturzaehler._offen.set(material, Genesis9texturzaehler.offen(material) + 1);
    }

    /** Wie viele Bilder `holen` diesem Material noch einsetzt. */
    static offen(material) {
        return Genesis9texturzaehler._offen.get(material) || 0;
    }

    /** Ein Bild ist angekommen (oder gescheitert — `einsetzen` tut dann nichts): mit den übrigen dieses Materials einsetzen, sobald keins mehr fehlt, spätestens nach `SAMMELN_MS`. */
    static angekommen(material, einsetzen) {
        if (!material) { einsetzen(); return; }
        const n = Genesis9texturzaehler.offen(material) - 1;
        if (n > 0) Genesis9texturzaehler._offen.set(material, n); else Genesis9texturzaehler._offen.delete(material);
        let w = Genesis9texturzaehler._wartend.get(material);
        if (!w) Genesis9texturzaehler._wartend.set(material, w = { liste: [], uhr: 0 });
        w.liste.push(einsetzen);
        if (n <= 0) Genesis9texturzaehler._einsetzen(material);
        else if (!w.uhr) w.uhr = setTimeout(() => Genesis9texturzaehler._einsetzen(material), Genesis9texturzaehler.SAMMELN_MS);
    }

    static _einsetzen(material) {
        const w = Genesis9texturzaehler._wartend.get(material);
        if (!w) return;
        Genesis9texturzaehler._wartend.delete(material);
        clearTimeout(w.uhr);
        for (const einsetzen of w.liste) einsetzen();
    }
}
