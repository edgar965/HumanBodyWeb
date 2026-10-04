import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleideranimexport — „Figur als GLB exportieren" und „In Blender exportieren" (Edgar, 01.10.2026: „Export als glb / blender inkl.
 * animation"; 03.10.2026: „rechts soll neben dem Export als glb auch erscheinen: export in blender und als Option (per default aktiviert):
 * Audio (mit Pfad), ausgewählte BVH (Pfad)").
 *
 * Der Server nimmt das Modell, das die Bühne zeigt (Stand-Modell mit Körper, Kleidern, Haar und Zubehör am Rig), legt die Bewegung der
 * gewählten BVH als Animation hinein und schreibt GLB bzw. `.blend` (`core/dienste/engine2d3dkleideranimexport.py`); das Audio liegt als
 * Datei daneben und läuft in der `.blend` als Tonstreifen. Die Dateien liegen im Exportordner des Auftrags und unter `ergebnis/`.
 *
 * BVH und Audio sind vorgewählt; ihre Pfade kommen aus den Optionen unter „Film" (`bvh`, `ton` — Vorgabe: der Tanz und die Audiospur des
 * aktuellen Studio-Projekts) und lassen sich hier für diesen Export ändern. Haken und Pfade merkt sich der Browser je Seite.
 */
export class Engine2d3dKleideranimexport {

    static MERKEN = 'engine2d3dkleider.export.';

    constructor(seite) {
        this.seite = seite;
        const $ = id => document.getElementById(id);
        this.glb = $('export-glb');
        this.blend = $('export-blend');
        this.meldung = $('export-meldung');
        this.bvh = $('export-bvh');
        this.bvhPfad = $('export-bvh-pfad');
        this.audio = $('export-audio');
        this.audioPfad = $('export-audio-pfad');
        this.name = $('export-name');
        this._laeuft = false;
        this._gefuellt = false;
        this._handname = false;
        for (const feld of [this.bvh, this.audio]) feld.checked = this._gemerkt(feld.id, 'an') !== '0';
        for (const feld of [this.bvh, this.audio, this.bvhPfad, this.audioPfad]) {
            feld.addEventListener('change', () => this._merken());
        }
        this.name.addEventListener('input', () => { this._handname = !!this.name.value.trim(); });
        this.glb.addEventListener('click', () => this.exportieren('glb'));
        this.blend.addEventListener('click', () => this.exportieren('blend'));
    }

    _gemerkt(id, art) {
        try { return localStorage.getItem(`${Engine2d3dKleideranimexport.MERKEN}${id}.${art}`); } catch { return null; }
    }

    _merken() {
        try {
            for (const feld of [this.bvh, this.audio]) {
                localStorage.setItem(`${Engine2d3dKleideranimexport.MERKEN}${feld.id}.an`, feld.checked ? '1' : '0');
            }
            for (const feld of [this.bvhPfad, this.audioPfad]) {
                localStorage.setItem(`${Engine2d3dKleideranimexport.MERKEN}${feld.id}.pfad`, feld.value);
            }
        } catch { /* ohne Speicher: nur diese Sitzung */ }
    }

    /** Was dem Export fehlt (Text für den Titel der Knöpfe) — oder null. */
    static fehlt(z) {
        if (z?.laeuft) return 'Der Auftrag rechnet gerade';
        if (!z?.standmodell && !(((z || {}).ergebnis || {}).iterationen || []).length) return 'Erst die Iterationen rechnen — es gibt noch kein Modell';
        return null;
    }

    /** Pfade vorbelegen: gemerkter Wert, sonst Option „Film" des Auftrags — einmal, danach gehören sie dem Nutzer. */
    _fuellen(z) {
        if (this._gefuellt) return;
        const film = ((z.optionen || {}).film) || {};
        this.bvhPfad.value = this._gemerkt(this.bvhPfad.id, 'pfad') || film.bvh || ((z.ergebnis || {}).film || {}).bvh || '';
        this.audioPfad.value = this._gemerkt(this.audioPfad.id, 'pfad') || film.ton || '';
        this._gefuellt = true;
    }

    zeigen(z) {
        this._fuellen(z);
        if (!this._handname && !this.name.value) this.name.value = z.name || 'modell';
        const fehlt = Engine2d3dKleideranimexport.fehlt(z);
        for (const knopf of [this.glb, this.blend]) knopf.disabled = !!fehlt || this._laeuft;
        this.glb.title = fehlt || 'Das Modell der Bühne mit der BVH-Animation als GLB';
        this.blend.title = fehlt || 'Das Modell der Bühne mit der BVH-Animation und dem Ton als Blender-Datei (~10 s)';
    }

    _melden(html, fehler = false) {
        this.meldung.innerHTML = html;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }

    static _link(teil) {
        const mb = t => (t.bytes / 1048576).toFixed(1);
        return teil && teil.adresse ? `<a href="${teil.adresse}" download>${teil.datei}</a> (${mb(teil)} MB)` : (teil && teil.fehler) || '';
    }

    async exportieren(format) {
        this._laeuft = true;
        this.zeigen(this.seite.zustand);
        const bvh = this.bvh.checked;
        const audio = this.audio.checked && !!this.audioPfad.value.trim();
        this._melden(`${format === 'blend' ? 'Blender-Datei' : 'GLB'} wird geschrieben${format === 'blend' ? ' (~10 s)' : ''} …`);
        try {
            const b = await Serverabruf.senden(this.seite.adresse('animexport/'), {
                glb: format === 'glb', blend: format === 'blend', bvh, bvh_pfad: this.bvhPfad.value.trim(),
                audio, audio_pfad: this.audioPfad.value.trim(), name: this.name.value.trim(),
            });
            if (b.error) throw new Error(b.error);
            const fehlend = b.fehlend && b.fehlend.length ? ` · ohne Knoten: ${b.fehlend.join(', ')}` : '';
            const teile = [format === 'blend' ? b.blend : b.glb].map(Engine2d3dKleideranimexport._link).filter(Boolean).join(' · ');
            const inhalt = [bvh ? `${b.bilder} Bilder (${b.sekunden} s)` : 'ohne Animation', audio ? 'mit Audio' : 'ohne Audio'].join(', ');
            this._melden(`Runde ${b.runde ?? '–'}, ${inhalt}${fehlend}<br>${teile}<br>Abgelegt in ${b.ablage.ordner}: ${b.ablage.dateien.join(', ')}`,
                !!(b.blend && b.blend.fehler));
        } catch (fehler) {
            this._melden(`Export fehlgeschlagen: ${fehler.daten?.error || fehler.message}`, true);
        } finally {
            this._laeuft = false;
            this.zeigen(this.seite.zustand);
        }
    }
}
