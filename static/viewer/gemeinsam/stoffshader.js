import { Shaderpatch } from './shaderpatch.js';
import { StoffshaderGLSL } from './stoffshaderglsl.js';
import { Stoffarten } from './stoffarten.js';

/**
 * Stoffshader — Bindung (Fadenzahl, Webart), Glanz und Glanzsaum eines Stücks im Shader, ohne Neubau des Netzes (25.10.2026).
 *
 * WARUM (Edgar, 25.10.2026: „beim Regler: Stoff gibt es noch mehr Optionen … die Anzahl der Fäden, Glanz, stoffart usw.“): Glanz
 * (`specularIntensity`) gab es nur an Stücken mit Daz-Preset und am Physical-Material, den Glanzsaum nur an live gebauten GarmentCode-
 * Stücken (`Garmentstoff`), und das Gewebe ersetzte die Normalkarte des Stücks (`Stoffwerte.gewebe` bis heute) — die Daz-Normalen und
 * die gebackenen Falten waren dann weg. Hier liegt alles als EIN Eingriff (`Shaderpatch`, Schlüssel `stoffshader`) auf jedem Material,
 * ob Standard oder Physical; danach schalten nur noch Uniforms (Three hält je Material und Programm dessen Uniform-Objekte fest — dieselben
 * Objekte bleiben, wie bei `Umfaerbung`). Der Text der Shader-Stücke: `StoffshaderGLSL`.
 *
 * ZWEI NUTZER, EINE SCHNITTSTELLE:
 *   Daz-, GC- und MB-Stücke    `Stoffshader.setzen(material, stoff, uvMeter)` — hängt den Eingriff beim ersten Bedarf an (`Stoffwerte`).
 *   eigene Stücke (Schale)     haben ein eigenes `onBeforeCompile` (`Eigenkleid`) — dort `const u = Stoffshader.uniforms()`, im Eingriff
 *                              `Stoffshader.patchen(shader, u)`, `Stoffshader.SCHLUESSEL` in den Programmschlüssel, und bei jeder Änderung
 *                              `Stoffshader.werte(u, stoff, uvMeter)`. `stoff` hat dieselbe Form wie `werte.stoff` (`Stoffarten.werte`).
 *
 * DICHTE: Fäden je UV-Einheit = Meter Stoff je UV-Einheit (`uvMeter`, am Netz gemessen, `Stoffwerte.uvMeter`) × 100 × Fäden je cm. Ohne
 * Maß gilt 1 m je UV-Einheit — eine Annahme, keine Messung (`UV_METER_OHNE_MASS`).
 * Ohne Three.js: die Farben sind schlichte `{r, g, b}` (Threes Uniform-Setzer liest sie wie `Color`) — in Node prüfbar.
 */
export class Stoffshader {

    static SCHLUESSEL = 'stoffshader';
    static FASSUNG = '1';
    /** Bindung → Nummer im Shader (`StoffshaderGLSL.FUNKTIONEN`, `stoffHoehe`); 0 = keine. */
    static ARTEN = { glatt: 0, leinwand: 1, koeper: 2, jersey: 3, satin: 4, narbung: 5 };
    static UV_METER_OHNE_MASS = 1.0;

    /** Neue Uniforms in der Vorgabe: nichts verändert (keine Bindung, Glanz 1, kein Saum). */
    static uniforms() {
        return {
            stoffArt: { value: 0 }, stoffDichte: { value: 400 }, stoffStaerke: { value: 0 },
            stoffSpiegel: { value: 1 }, stoffSaum: { value: 0 }, stoffSaumStreuung: { value: 0.8 },
            stoffSaumEigen: { value: 0 }, stoffSaumFarbe: { value: { r: 1, g: 1, b: 1 } },
        };
    }

    /** Der Eingriff selbst: Uniforms anhängen, Text umschreiben (`StoffshaderGLSL.einsetzen`). */
    static patchen(shader, uniforms) {
        Object.assign(shader.uniforms, uniforms);
        return StoffshaderGLSL.einsetzen(shader);
    }

    /** Braucht `stoff` den Eingriff? Ein unberührtes Stück bekommt keinen (kein neues Programm). */
    static noetig(stoff) {
        if (!stoff || typeof stoff !== 'object') return false;
        const g = stoff.gewebe;
        const bindung = g && Stoffshader.ARTEN[g.art] > 0 && Number(g.staerke) > 0;
        const glanz = typeof stoff.glanz === 'number' && stoff.glanz !== 1;
        const saum = typeof stoff.saum === 'number' && stoff.saum > 0;
        return Boolean(bindung || glanz || saum);
    }

    /** Die Werte auf ein Material; false, wenn es keinen Eingriff braucht und noch keinen trägt, oder kein Standard-/Physical-Material ist. */
    static setzen(material, stoff, uvMeter = 0) {
        if (!material?.isMeshStandardMaterial) return false;
        let eingriff = Shaderpatch.eingriff(material, Stoffshader.SCHLUESSEL);
        if (!eingriff) {
            if (!Stoffshader.noetig(stoff)) return false;
            const uniforms = Stoffshader.uniforms();
            eingriff = (shader) => Stoffshader.patchen(shader, uniforms);
            eingriff.uniforms = uniforms;
            eingriff.kennung = () => Stoffshader.FASSUNG;
            Shaderpatch.anhaengen(material, Stoffshader.SCHLUESSEL, eingriff);
        }
        Stoffshader.werte(eingriff.uniforms, stoff, uvMeter);
        return true;
    }

    /** Die Uniforms des Materials — oder null, wenn es den Eingriff nicht trägt (für die Prüfung im Browser). */
    static stand(material) {
        return Shaderpatch.eingriff(material, Stoffshader.SCHLUESSEL)?.uniforms || null;
    }

    /** `stoff` → Uniforms. Fehlende Felder heißen Vorgabe (`Stoffarten.VORGABE`), „Wie geliefert“ beim Gewebe heißt Art 0. */
    static werte(u, stoff, uvMeter = 0) {
        const s = stoff || {};
        const v = Stoffarten.VORGABE;
        const zahl = (w, vorgabe, min, max) => (Number.isFinite(Number(w)) && w !== null && w !== '' ? Math.min(max, Math.max(min, Number(w))) : vorgabe);
        const g = s.gewebe || {};
        const art = Stoffshader.ARTEN[g.art] || 0;
        u.stoffArt.value = art;
        u.stoffStaerke.value = art ? zahl(g.staerke, 0, 0, 2) : 0;
        u.stoffDichte.value = Stoffshader.dichte(uvMeter, zahl(g.faeden, Stoffarten.gewebevorgabe(g.art).faeden, 0.1, 100));
        u.stoffSpiegel.value = zahl(s.glanz, v.glanz, 0, 2);
        u.stoffSaum.value = zahl(s.saum, v.saum, 0, 1);
        u.stoffSaumStreuung.value = zahl(s.saumstreuung, v.saumstreuung, 0, 1);
        const farbe = Stoffshader.linear(s.saumfarbe);
        u.stoffSaumEigen.value = farbe ? 1 : 0;
        if (farbe) Object.assign(u.stoffSaumFarbe.value, farbe);
        return u;
    }

    /** Fäden je UV-Einheit. */
    static dichte(uvMeter, faedenJeCm) {
        const m = uvMeter > 0 ? uvMeter : Stoffshader.UV_METER_OHNE_MASS;
        return m * 100 * faedenJeCm;
    }

    /** '#rrggbb' (sRGB, wie der Farbwähler) → linear `{r, g, b}`, wie Threes `Color.set` rechnet; sonst null. */
    static linear(hex) {
        const m = /^#([0-9a-f]{6})$/i.exec(String(hex || ''));
        if (!m) return null;
        const n = parseInt(m[1], 16);
        const lin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
        return { r: lin((n >> 16 & 255) / 255), g: lin((n >> 8 & 255) / 255), b: lin((n & 255) / 255) };
    }
}
