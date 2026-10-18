import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { closeDialog, openDialog } from './utils.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Modellexportinhalt, STATISCHE_FORMATE } from './modellexport_inhalt.js';
import { Modellexport } from './modellexport.js';
import { Modellexportordner } from './modellexport_ordner.js';
import { Szenenausgabe } from './szenenausgabe.js';
import { Figuraufbaustand } from '../gemeinsam/figuraufbaustand.js';

/**
 * Modellexportdialog — der Dialog hinter „Modell exportieren …" im Kontextmenü
 * der Modellzeile (`speichernmenue.js`) und der Figur in der 3D-Ansicht
 * (`figurkontextmenue.js`).
 *
 * WARNUNGEN LIVE (26.09.2026, `Docu/konzept_modellexport.md`): Jede Änderung
 * an einem Häkchen oder Format rechnet `Modellexportinhalt.warnungen` neu —
 * VOR dem Export, nicht erst in der Abschlussmeldung.
 *
 * SEIT 18.10.2026 (Edgar: „exportieren als glb, blender, fbx, und jpg", „auch in
 * json", „Per Default: json, glb und jpg aktiviert"): FBX, JPG (vier Ansichten)
 * und JSON (die Daten von „Modell speichern unter") dazu; Ordner und Dateiname
 * kommen aus `Modellexportordner` (`3DObjects/modelsExport/<Modellname>`), die
 * Pose ist die angezeigte. Formate und Pose werden NICHT mehr vom letzten Mal
 * übernommen — Edgar hat die Vorgabe festgelegt, eine gemerkte Wahl stünde ihr
 * bei jedem Öffnen im Weg.
 */
export class Modellexportdialog {

    static FORMATE = ['json', 'glb', 'blend', 'fbx', 'jpg', 'obj', 'ply', 'stl', 'dae'];
    static VORGABE_FORMATE = ['json', 'glb', 'jpg'];
    //: Inhalt (außer Animation — die richtet sich lieber nach der GERADE
    //: aktiven Animation als nach dem letzten Mal) und Auflösung — das sind
    //: echte Vorlieben, keine je-Figur-Werte wie Name.
    static EINSTELLUNGEN_SCHLUESSEL = 'modell_export_einstellungen';

    static _instId = null;
    static _ordner = null;

    /** An das Dialog-Markup binden — einmal beim Seitenaufbau. */
    static verdrahten() {
        const dialog = document.getElementById('modellexport-dialog');
        if (!dialog) return;
        Modellexportdialog._ordner = new Modellexportordner({
            ordner: document.getElementById('modellexport-ordner'),
            name: document.getElementById('modellexport-name'),
            knopf: document.getElementById('modellexport-suchen'),
            vorhanden: document.getElementById('modellexport-vorhanden'),
        }, () => Modellexportdialog._formate());
        for (const f of Modellexportdialog.FORMATE) {
            document.getElementById(`modellexport-fmt-${f}`)?.addEventListener('change', () => {
                Modellexportdialog._warnungenZeichnen();
                Modellexportdialog._ordner.pruefenBald();
            });
        }
        for (const id of ['modellexport-rig', 'modellexport-textur', 'modellexport-assets',
                          'modellexport-animation']) {
            document.getElementById(id)?.addEventListener('change', () => Modellexportdialog._warnungenZeichnen());
        }
        document.getElementById('modellexport-confirm')?.addEventListener('click', () => Modellexportdialog._exportieren());
        // Solange die Figur nachlädt, bleibt der Knopf zu — und geht von
        // selbst auf, sobald sie steht (Edgar, 26.09.2026: „aktiviere export
        // nur wenn die Figur ganz geladen ist").
        document.addEventListener(Figuraufbaustand.EREIGNIS, () => Modellexportdialog._sperreZeichnen());
    }

    /**
     * Knopf und Hinweis nach dem Aufbaustand der Figur. Getrennt von
     * `_warnungenZeichnen`, weil die Warnungen an den Häkchen hängen und
     * dieser Zustand an der Figur — sonst überschriebe eins das andere.
     */
    static _sperreZeichnen() {
        const inst = state.characters.get(Modellexportdialog._instId);
        const knopf = document.getElementById('modellexport-confirm');
        const hinweis = document.getElementById('modellexport-aufbau');
        if (!knopf || !hinweis) return;
        const laeuft = Figuraufbaustand.laeuft(inst);
        // Ein laufender Export hat den Knopf selbst gesperrt — nicht dazwischenfunken.
        if (knopf.textContent !== 'Exportiere …') knopf.disabled = laeuft;
        hinweis.hidden = !laeuft;
    }

    /** Den Dialog für eine Figur öffnen — Rechtsklick-Eintrag ruft das. */
    static async oeffnen(charId) {
        const dialog = document.getElementById('modellexport-dialog');
        const inst = state.characters.get(charId);
        if (!dialog || !inst) return;
        Modellexportdialog._instId = charId;

        const prefs = await Serverabruf.json('/api/ui-prefs/').catch(() => ({}));
        for (const f of Modellexportdialog.FORMATE) {
            const cb = document.getElementById(`modellexport-fmt-${f}`);
            if (cb) cb.checked = Modellexportdialog.VORGABE_FORMATE.includes(f);
        }
        const aktuell = document.querySelector('input[name="modellexport-pose"][value="aktuell"]');
        if (aktuell) aktuell.checked = true;
        Modellexportdialog._einstellungenAnwenden(prefs[Modellexportdialog.EINSTELLUNGEN_SCHLUESSEL]);

        const anim = Modellexportinhalt.animationsstand(inst);
        document.getElementById('modellexport-anim-name').textContent = anim.aktiv
            ? `(„${anim.clip.name || 'Clip'}")` : anim.fremd ? `(gehört zu „${anim.fremdname}")` : '(keine aktiv)';
        document.getElementById('modellexport-animation').checked = anim.aktiv;

        await Modellexportdialog._ordner.vorbelegen(inst.presetName || inst.presetKey || 'figur');

        openDialog(dialog);
        Modellexportdialog._warnungenZeichnen();
        Modellexportdialog._sperreZeichnen();
    }

    /** Zuletzt genutzten Inhalt und Auflösung ins Markup übernehmen (Formate und Pose nicht, siehe Klassenkopf). */
    static _einstellungenAnwenden(einstellungen) {
        if (!einstellungen) return;
        for (const feld of ['rig', 'textur', 'assets']) {
            const cb = document.getElementById(`modellexport-${feld}`);
            if (cb && feld in einstellungen) cb.checked = !!einstellungen[feld];
        }
        if (einstellungen.aufloesung !== undefined) {
            const sel = document.getElementById('modellexport-aufloesung');
            if (sel) sel.value = String(einstellungen.aufloesung);
        }
        if (einstellungen.polygone !== undefined) {
            const sel = document.getElementById('modellexport-polygone');
            if (sel) sel.value = String(einstellungen.polygone);
        }
        if (einstellungen.fps) {
            const feld = document.getElementById('modellexport-fps');
            if (feld) feld.value = String(einstellungen.fps);
        }
    }

    // ------------------------------------------------------------- Optionen

    static _formate() {
        return Modellexportdialog.FORMATE.filter((f) => document.getElementById(`modellexport-fmt-${f}`)?.checked);
    }

    static _optionen() {
        return {
            formate: Modellexportdialog._formate(),
            rig: !!document.getElementById('modellexport-rig')?.checked,
            textur: !!document.getElementById('modellexport-textur')?.checked,
            assets: !!document.getElementById('modellexport-assets')?.checked,
            animation: !!document.getElementById('modellexport-animation')?.checked,
            pose: document.querySelector('input[name="modellexport-pose"]:checked')?.value || 'aktuell',
            //: 0 = Original — `<select>`-Werte sind Strings, deshalb `Number(...)`.
            aufloesung: Number(document.getElementById('modellexport-aufloesung')?.value || 0),
            //: Anteil der Dreiecke, die im `.blend`-Export bleiben — 1 = Original,
            //: kleiner nur über Blenders Decimate-Modifier (`modellexportblend.py`).
            polygone: Number(document.getElementById('modellexport-polygone')?.value || 1),
            fps: Math.min(120, Math.max(1, Math.round(Number(document.getElementById('modellexport-fps')?.value) || 30))),
            ordner: document.getElementById('modellexport-ordner')?.value.trim(),
            name: document.getElementById('modellexport-name')?.value.trim(),
            // Genau in den angezeigten Ordner — er trägt schon den Modellnamen (`Modellexportordner`).
            direkt: true,
        };
    }

    /** Posenzeile nur, wenn eine Pose überhaupt zum Tragen kommt — DAE stellt seit 18.10.2026 auch mit Rig die Gelenke danach. */
    static _poseZeileZeigen(optionen) {
        const nutzt = !optionen.rig || optionen.formate.some((f) => STATISCHE_FORMATE.includes(f) || f === 'dae');
        document.getElementById('modellexport-pose-zeile').hidden = !nutzt;
    }

    static _warnungenZeichnen() {
        const inst = state.characters.get(Modellexportdialog._instId);
        if (!inst) return;
        const optionen = Modellexportdialog._optionen();
        Modellexportdialog._poseZeileZeigen(optionen);
        const feld = document.getElementById('modellexport-warnungen');
        const warnungen = optionen.formate.length
            ? Modellexportinhalt.warnungen(inst, optionen)
            : ['Kein Format gewählt.'];
        feld.innerHTML = warnungen.map((w) => `<div><i class="fas fa-triangle-exclamation"></i> ${_escapeHtml(w)}</div>`).join('');
    }

    // -------------------------------------------------------------- Export

    static async _exportieren() {
        const inst = state.characters.get(Modellexportdialog._instId);
        const optionen = Modellexportdialog._optionen();
        if (!inst || !optionen.formate.length || !optionen.ordner) {
            alert('Bitte mindestens ein Format und einen Ordner angeben.');
            return;
        }
        const knopf = document.getElementById('modellexport-confirm');
        knopf.disabled = true;
        knopf.textContent = 'Exportiere …';
        try {
            if (optionen.formate.includes('json')) optionen.modelldaten = Szenenausgabe.modelldaten(inst);
            const ergebnis = await Modellexport.exportieren(inst, optionen);
            Serverabruf.senden('/api/ui-prefs/', {
                [Modellexportdialog.EINSTELLUNGEN_SCHLUESSEL]: {
                    rig: optionen.rig, textur: optionen.textur, assets: optionen.assets,
                    aufloesung: optionen.aufloesung, fps: optionen.fps, polygone: optionen.polygone,
                },
            }).catch(() => {});
            closeDialog(document.getElementById('modellexport-dialog'));
            const dateiliste = (ergebnis.dateien || []).map((d) => `${d.name} (${d.bytes} Bytes)`).join('\n');
            const warnhinweis = ergebnis.warnungen?.length ? `\n\nWarnungen:\n${ergebnis.warnungen.join('\n')}` : '';
            alert(`Exportiert nach ${ergebnis.ordner}:\n${dateiliste}${warnhinweis}`);
        } catch (fehler) {
            alert(`Export fehlgeschlagen: ${fehler.message || fehler}`);
        } finally {
            knopf.disabled = false;
            knopf.textContent = 'Exportieren';
        }
    }
}

function _escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

fn.openModelExportDialog = (charId) => Modellexportdialog.oeffnen(charId);
fn.initModellexportDialog = () => Modellexportdialog.verdrahten();
