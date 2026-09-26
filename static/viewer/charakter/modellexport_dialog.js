import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { closeDialog, openDialog } from './utils.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Modellexportinhalt, STATISCHE_FORMATE } from './modellexport_inhalt.js';
import { Modellexport } from './modellexport.js';

/**
 * Modellexportdialog — der Dialog hinter „Exportieren …" im Kontextmenü der
 * Modellzeile (`speichernmenue.js`).
 *
 * WARNUNGEN LIVE (26.09.2026, `Docu/konzept_modellexport.md`): Jede Änderung
 * an einem Häkchen oder Format rechnet `Modellexportinhalt.warnungen` neu —
 * VOR dem Export, nicht erst in der Abschlussmeldung.
 */
export class Modellexportdialog {

    static VORGABE_ENDPUNKT = '/api/character/modellexport/vorgabe/';
    static UI_PREF_SCHLUESSEL = 'modell_export_ordner';
    //: Format-Häkchen, Inhalt (außer Animation — die richtet sich lieber
    //: nach der GERADE aktiven Animation als nach dem letzten Mal), Pose und
    //: Auflösung — das sind echte Vorlieben, keine je-Figur-Werte wie Name.
    static EINSTELLUNGEN_SCHLUESSEL = 'modell_export_einstellungen';

    static _instId = null;

    /** An das Dialog-Markup binden — einmal beim Seitenaufbau. */
    static verdrahten() {
        const dialog = document.getElementById('modellexport-dialog');
        if (!dialog) return;
        for (const id of ['modellexport-fmt-glb', 'modellexport-fmt-obj', 'modellexport-fmt-ply',
                          'modellexport-fmt-stl', 'modellexport-fmt-dae', 'modellexport-fmt-blend',
                          'modellexport-rig', 'modellexport-textur', 'modellexport-assets',
                          'modellexport-animation']) {
            document.getElementById(id)?.addEventListener('change', () => Modellexportdialog._warnungenZeichnen());
        }
        document.getElementById('modellexport-confirm')?.addEventListener('click', () => Modellexportdialog._exportieren());
    }

    /** Den Dialog für eine Figur öffnen — Rechtsklick-Eintrag ruft das. */
    static async oeffnen(charId) {
        const dialog = document.getElementById('modellexport-dialog');
        const inst = state.characters.get(charId);
        if (!dialog || !inst) return;
        Modellexportdialog._instId = charId;

        const prefs = await Serverabruf.json('/api/ui-prefs/').catch(() => ({}));
        Modellexportdialog._einstellungenAnwenden(prefs[Modellexportdialog.EINSTELLUNGEN_SCHLUESSEL]);

        const anim = Modellexportinhalt.animationsstand(inst);
        document.getElementById('modellexport-anim-name').textContent = anim.aktiv
            ? `(„${anim.clip.name || 'Clip'}")` : anim.fremd ? `(gehört zu „${anim.fremdname}")` : '(keine aktiv)';
        document.getElementById('modellexport-animation').checked = anim.aktiv;

        document.getElementById('modellexport-name').value = inst.presetName || inst.presetKey || 'figur';

        const ordnerFeld = document.getElementById('modellexport-ordner');
        ordnerFeld.value = await Modellexportdialog._ordnerVorgabe(prefs);

        openDialog(dialog);
        Modellexportdialog._warnungenZeichnen();
    }

    /** Zuletzt genutzte Formate/Inhalt/Pose/Auflösung ins Markup übernehmen. */
    static _einstellungenAnwenden(einstellungen) {
        if (!einstellungen) return;
        for (const f of ['glb', 'obj', 'ply', 'stl', 'dae', 'blend']) {
            const cb = document.getElementById(`modellexport-fmt-${f}`);
            if (cb) cb.checked = einstellungen.formate?.includes(f) ?? cb.checked;
        }
        for (const feld of ['rig', 'textur', 'assets']) {
            const cb = document.getElementById(`modellexport-${feld}`);
            if (cb && feld in einstellungen) cb.checked = !!einstellungen[feld];
        }
        if (einstellungen.pose) {
            const radio = document.querySelector(`input[name="modellexport-pose"][value="${einstellungen.pose}"]`);
            if (radio) radio.checked = true;
        }
        if (einstellungen.aufloesung !== undefined) {
            const sel = document.getElementById('modellexport-aufloesung');
            if (sel) sel.value = String(einstellungen.aufloesung);
        }
    }

    static async _ordnerVorgabe(prefs) {
        if (prefs[Modellexportdialog.UI_PREF_SCHLUESSEL]) return prefs[Modellexportdialog.UI_PREF_SCHLUESSEL];
        try {
            const antwort = await Serverabruf.json(Modellexportdialog.VORGABE_ENDPUNKT);
            return antwort.ordner || '';
        } catch {
            return '';
        }
    }

    // ------------------------------------------------------------- Optionen

    static _formate() {
        const gewaehlt = ['glb', 'obj', 'ply', 'stl', 'dae', 'blend']
            .filter((f) => document.getElementById(`modellexport-fmt-${f}`)?.checked);
        return gewaehlt;
    }

    static _optionen() {
        return {
            formate: Modellexportdialog._formate(),
            rig: !!document.getElementById('modellexport-rig')?.checked,
            textur: !!document.getElementById('modellexport-textur')?.checked,
            assets: !!document.getElementById('modellexport-assets')?.checked,
            animation: !!document.getElementById('modellexport-animation')?.checked,
            pose: document.querySelector('input[name="modellexport-pose"]:checked')?.value || 'ruhelage',
            //: 0 = Original — `<select>`-Werte sind Strings, deshalb `Number(...)`.
            aufloesung: Number(document.getElementById('modellexport-aufloesung')?.value || 0),
            ordner: document.getElementById('modellexport-ordner')?.value.trim(),
            name: document.getElementById('modellexport-name')?.value.trim(),
        };
    }

    /** Posenzeile nur, wenn eine Pose überhaupt zum Tragen kommt. */
    static _poseZeileZeigen(optionen) {
        const nutzt = !optionen.rig || optionen.formate.some((f) => STATISCHE_FORMATE.includes(f));
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
            const ergebnis = await Modellexport.exportieren(inst, optionen);
            Serverabruf.senden('/api/ui-prefs/', {
                [Modellexportdialog.UI_PREF_SCHLUESSEL]: optionen.ordner,
                [Modellexportdialog.EINSTELLUNGEN_SCHLUESSEL]: {
                    formate: optionen.formate, rig: optionen.rig, textur: optionen.textur,
                    assets: optionen.assets, pose: optionen.pose, aufloesung: optionen.aufloesung,
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
