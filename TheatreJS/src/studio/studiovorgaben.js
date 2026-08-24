import { PRESETS, applyPreset } from '../presets.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Studiovorgaben — was beim Öffnen des Theatre-Studios von selbst geladen wird.
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Drei Dinge kommen aus den
 * Einstellungen: die Beleuchtungsvorgabe, die Figur und ihre Animation. Die
 * Videowerte werden nur gemerkt (`window._theatreVideoSettings`) — der
 * Aufnahmedialog belegt seine Felder daraus vor.
 *
 * **Reihenfolge:** erst Licht, dann Figur, dann Animation. Und das Ganze erst,
 * wenn Theatre.js sein Studio aufgebaut hat — sonst überschreibt dessen Aufbau
 * die gerade gesetzten Werte wieder (`WARTEN_MS`).
 */
export class Studiovorgaben {

    static ENDPUNKT = '/api/settings/theatre/';
    /** So lange braucht Theatre.js, bis sein Studio steht. */
    static WARTEN_MS = 500;

    /**
     * @param {Object} buehne { camera, lights, controls }
     * @param {Object} lader  { figurenlader, animationslauf }
     */
    constructor(buehne, lader) {
        Object.assign(this, buehne, lader);
    }

    /** Nach der Wartezeit laden — der übliche Aufruf. */
    spaeterLaden() {
        setTimeout(() => this.laden(), Studiovorgaben.WARTEN_MS);
        return this;
    }

    async laden() {
        let stand;
        try {
            const antwort = await fetch(Studiovorgaben.ENDPUNKT);
            if (!antwort.ok) {
                Protokoll.debug('Theatre Studio',
                                `Vorgaben nicht abrufbar (HTTP ${antwort.status})`);
                return;
            }
            stand = await antwort.json();
        } catch (fehler) {
            Protokoll.warnung('main', 'Failed to load Theatre defaults:', fehler);
            return;
        }
        Studiovorgaben.videowerte(stand);
        this._beleuchtung(stand.preset);
        await this._figur(stand);
    }

    static videowerte(stand) {
        window._theatreVideoSettings = {
            format: stand.video_format || 'mp4',
            resolution: stand.video_resolution || '1080p',
            fps: stand.video_fps || 30,
            quality: stand.video_quality || 'high',
        };
    }

    _beleuchtung(name) {
        const vorgabe = name && PRESETS[name];
        if (!vorgabe) return;
        applyPreset(vorgabe, this.camera, this.lights, this.controls);
        Protokoll.debug('main', '✓ Auto-applied preset:', vorgabe.name);
    }

    async _figur(stand) {
        if (!stand.model) return;
        try {
            await this.figurenlader.modell(stand.model);
            Protokoll.debug('main', '✓ Auto-loaded model:', stand.model);
            await this._animation(stand.animation);
        } catch (fehler) {
            Protokoll.warnung('main', 'Auto-load model/animation failed:', fehler);
        }
    }

    /** `kategorie/name` — ohne Figur wäre die Animation ohne Wirkung. */
    async _animation(angabe) {
        if (!angabe) return;
        const [kategorie, name] = angabe.split('/');
        if (!kategorie || !name) return;
        await this.animationslauf.laden(kategorie, name);
        Protokoll.debug('main', '✓ Auto-loaded animation:', angabe);
    }
}
