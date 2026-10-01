import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Haarengineanimexport — Knopf „Modell mit Animation exportieren (GLB + Blender)" (Edgar, 01.10.2026: „Export als
 * glb / blender inkl. animation").
 *
 * Der Server nimmt das Modell der besten Runde (Körper mit Rig, Kleider, Haar) und die Bewegung des Schritts „film" und
 * schreibt `ergebnis/modell_animiert.glb` und `.blend` (`core/dienste/haarengineanimexport.py`). Bereit ist der Knopf,
 * sobald es beides gibt; sonst sagt sein Titel, was fehlt.
 */
export class Haarengineanimexport {

    constructor(seite) {
        this.seite = seite;
        this.knopf = document.getElementById('animexport');
        this.meldung = document.getElementById('animexport-meldung');
        this._laeuft = false;
        this.knopf.addEventListener('click', () => this.exportieren());
    }

    static fehlt(z) {
        const e = (z || {}).ergebnis || {};
        if (z?.laeuft) return 'Der Auftrag rechnet gerade';
        if (!((e.iterationen || []).length)) return 'Erst die Iterationen rechnen — es gibt noch kein Modell';
        if (!(e.film || {}).bewegung) return 'Erst den Schritt „film" rechnen (BVH in den Optionen, Vorgabe: Tanz)';
        return null;
    }

    zeigen(z) {
        const fehlt = Haarengineanimexport.fehlt(z);
        this.knopf.disabled = !!fehlt || this._laeuft;
        this.knopf.title = fehlt || 'Bestes Modell + Bewegung → modell_animiert.glb und modell_animiert.blend';
    }

    _melden(html, fehler = false) {
        this.meldung.innerHTML = html;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }

    async exportieren() {
        this._laeuft = true;
        this.zeigen(this.seite.zustand);
        this._melden('Modell mit Animation wird geschrieben (Blender ~10 s) …');
        try {
            const b = await Serverabruf.senden(this.seite.adresse('animexport/'), {});
            if (b.error) throw new Error(b.error);
            const mb = t => (t.bytes / 1048576).toFixed(1);
            const link = t => (t && t.adresse ? `<a href="${t.adresse}" download>${t.datei}</a> (${mb(t)} MB)`
                : (t && t.fehler) || '—');
            const fehlend = b.fehlend && b.fehlend.length ? ` · ohne Knoten: ${b.fehlend.join(', ')}` : '';
            this._melden(`Runde ${b.runde ?? '–'}, ${b.bilder} Bilder (${b.sekunden} s), ${b.kanaele} Knochen`
                + `${fehlend}<br>${link(b.glb)} · ${link(b.blend)}`, !!(b.blend && b.blend.fehler));
        } catch (fehler) {
            this._melden(`Export fehlgeschlagen: ${fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
