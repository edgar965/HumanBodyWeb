import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Studioanzeige } from './studioanzeige.js';
import { Mimikbasis } from './mimikbasis.js';
import { Mimikanwendung } from './mimikanwendung.js';

/**
 * Mimikeinrechnen — die Mimikspur in die Bewegungsclips der Figur einrechnen.
 *
 * Edgar, 13.09.2026: „per Klick zusammengerechnet in dann eine BVH-Datei."
 * Für jeden Bewegungsclip der verknüpften Animation werden die Gewichte je
 * QUELLBILD (Bildrate des Clips) für das Modell gerechnet — Schlüsselbilder,
 * Übergänge, Scripts der Script-Spur, alles wie beim Abspielen — und an
 * `save-bvh-effects` geschickt. Der Server legt `<name>_mimik.json` neben
 * die BVH; beim nächsten Retarget trägt die Animation die Mimik auf jeder
 * Seite (`core/dienste/mimikspuren.py`). Die BVH-Datei selbst bleibt.
 */
export class Mimikeinrechnen {

    static ADRESSE = '/api/retarget/save-bvh-effects/';
    static NACHKOMMA = 3;

    /** `spur` ist die Mimik- oder die Script-Spur — beide kennen ihr Modell. */
    static async einrechnen(spur) {
        await Mimikbasis.laden();
        const modell = state.project.tracks[spur._modellIdx];
        const animation = modell ? state.project.getLinkedAnimation(modell) : null;
        const clips = (animation?.clips || []).filter(c => c.type === 'bvh' && c.category && c.name);
        if (!clips.length) {
            Studioanzeige.melden('Mimik einrechnen: keine Bewegungsclips an der Modellspur');
            return [];
        }
        const ergebnisse = [];
        for (const clip of clips) {
            const mimik = Mimikeinrechnen.gewichteJeQuellbild(spur, clip);
            try {
                const antwort = await Serverabruf.senden(Mimikeinrechnen.ADRESSE,
                    { category: clip.category, name: clip.name, mimik });
                ergebnisse.push({ clip: clip.name, ...antwort });
            } catch (fehler) {
                Protokoll.warnung('Mimik', `Einrechnen fehlgeschlagen: ${clip.name}`, fehler);
                ergebnisse.push({ clip: clip.name, error: String(fehler) });
            }
        }
        const gut = ergebnisse.filter(e => e.ok).length;
        Studioanzeige.melden(`Mimik eingerechnet: ${gut} von ${clips.length} Clips `
                             + `(${clips.map(c => c.name).join(', ')})`);
        return ergebnisse;
    }

    /**
     * `{fps, einheiten, bilder}` — je Quellbild i des Clips die Gewichte an der
     * Projektzeit `start + (i − trimIn) / (fps · speed)`; vor dem Clipanfang
     * gilt der Anfang.
     */
    static gewichteJeQuellbild(spur, clip) {
        const fps = clip.fps || 30;
        const start = clip.startFrame / state.project.fps;
        const einheiten = Object.keys(Mimikbasis.basis || {}).sort();
        const stelle = Object.fromEntries(einheiten.map((e, i) => [e, i]));
        const bilder = [];
        for (let i = 0; i < clip.totalFrames; i++) {
            const t = Math.max(start, start + (i - (clip.trimIn || 0)) / (fps * (clip.speed || 1)));
            const { gewichte } = Mimikanwendung.gewichteModell(spur._modellIdx, t);
            const zeile = new Array(einheiten.length).fill(0);
            for (const [e, g] of Object.entries(gewichte)) {
                if (e in stelle) zeile[stelle[e]] = Number(g.toFixed(Mimikeinrechnen.NACHKOMMA));
            }
            bilder.push(zeile);
        }
        return { fps, einheiten, bilder };
    }
}

fn.mimikEinrechnen = (spur) => Mimikeinrechnen.einrechnen(spur);
