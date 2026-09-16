/**
 * Modellmenue — das Kontextmenue einer Modellspur mit der Vorlagenliste.
 *
 * Aus timeline.js herausgeloest (Umbau 16.08.2026), zusammen mit dem uebrigen
 * Kontextmenue; von zeitleiste_menue.js abgetrennt, weil die Vorlagenwahl eine
 * eigene Aufgabe mit eigenem Zwischenspeicher ist.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { Clip } from './models.js';
import { Zeitleistenziehen } from './zeitleiste_ziehen.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Modellhinzufuegen } from './zeitleiste_modellhinzufuegen.js';

/** Kleinste Laenge eines neu angelegten Modellclips in Bildern. */
const MINDESTLAENGE = 300;

export class Modellmenue {
    /** Maus-X des Rechtsklicks, von Zeitleistenmenue gesetzt. */
    static mausX = 0;
    /** Bild unter der Maus beim Rechtsklick — dort landen Mimik und Script. */
    static klickbild = 0;

    /** Die Vorlagen werden nur einmal vom Server geholt. */
    static geholt = false;

    static get menue() {
        return document.getElementById('model-context-menu');
    }

    /** Menue fuer eine Modellspur aufbauen und zeigen. */
    static zeigen(e, spur, spurNr, treffer, klickbild, anzeigen) {
        const menue = Modellmenue.menue;
        Modellmenue.klickbild = klickbild;
        // „Hinzufügen" zweigeteilt (Edgar, 15.09.2026): Modell — und Animation
        // mit normaler Animation (BVH-Bibliothek), Mimik und Script.
        Modellhinzufuegen.fuellen(spur, spurNr, menue, klickbild,
                                 { modell: 'model-ctx-add-submenu', bvh: 'model-ctx-bvh-submenu' });
        Modellmenue._vorlagenListe(spurNr);
        Modellmenue._aktuelleHervorheben(
            menue, treffer ? spur.clips[treffer.clipIdx]?.data?.preset : null);
        // „Länge“ gilt dem getroffenen Clip (Edgar, 13.09.2026: „Länge einstellen
        // soll auch beim Modell-Eintrag als Kontextmenü kommen“).
        menue.querySelector('#model-ctx-laenge')?.classList.toggle('hb-versteckt', !treffer);
        // Split und Löschen gelten dem getroffenen Clip — ohne Clip nicht anbieten.
        for (const aktion of ['ctx-split', 'ctx-delete']) {
            menue.querySelector(`[data-action="${aktion}"]`)?.classList.toggle('hb-versteckt', !treffer);
        }
        Modellmenue._befehleBinden(menue);
        anzeigen(menue, e);
    }

    static _aktuelleHervorheben(menue, aktuell) {
        menue.querySelectorAll('#model-preset-list .ctx-item').forEach(eintrag => {
            const gewaehlt = eintrag.dataset.preset === aktuell;
            eintrag.style.fontWeight = gewaehlt ? 'bold' : '';
            eintrag.style.color = gewaehlt ? '#e91e63' : '';
        });
    }

    static _befehleBinden(menue) {
        menue.querySelectorAll('.ctx-item[data-action]').forEach(eintrag => {
            eintrag.onclick = () => {
                if (eintrag.dataset.action === 'ctx-laenge') return;   // öffnet nur das Untermenü
                menue.style.display = 'none';
                const aktion = eintrag.dataset.action;
                if (aktion === 'ctx-playhead') {
                    Zeitleistenziehen.abspielkopfSetzen(Modellmenue.mausX);
                } else if (aktion === 'ctx-split') {
                    fn.splitClipAtPlayhead();
                } else if (aktion === 'ctx-delete') {
                    fn.deleteSelectedClip();
                } else if (aktion === 'ctx-laenge-prozent') {
                    fn.clipLaenge('prozent', Number(eintrag.dataset.wert) || null);
                } else if (aktion === 'ctx-laenge-sekunden') {
                    fn.clipLaenge('sekunden');
                }
            };
        });
        // Mimik und Script — dieselben Befehle wie im Spurkopfmenü.
        Modellhinzufuegen.binden(menue, state.selectedTrackIdx, Modellmenue.klickbild);
    }

    static _vorlagenListe(spurNr) {
        if (Modellmenue.geholt) return;
        Modellmenue.geholt = true;
        fetch('/api/character/models/').then(r => r.json()).then(daten => {
            const liste = document.getElementById('model-preset-list');
            liste.innerHTML = '';
            for (const p of (daten.presets || [])) {
                const eintrag = document.createElement('div');
                eintrag.className = 'ctx-item';
                eintrag.dataset.action = 'ctx-model-preset';
                eintrag.dataset.preset = p.name;
                eintrag.innerHTML = '<i class="fas fa-user symbol-modell">'
                    + `</i> ${p.label || p.name}`;
                liste.appendChild(eintrag);
            }
            liste.querySelectorAll('.ctx-item').forEach(eintrag => {
                eintrag.addEventListener('click', () => {
                    Modellmenue.menue.style.display = 'none';
                    Modellmenue.vorlageSetzen(spurNr, eintrag.dataset.preset);
                });
            });
        });
    }

    /**
     * Modellvorlage einer Spur setzen.
     *
     * BEFUND 16.08.2026: Hier stand `const Clip = track.clips[0]?.constructor;`
     * — der importierte `Clip` wurde also von einer oertlichen Variablen
     * verdeckt, und bei einer LEEREN Modellspur brach die Funktion mit
     * `if (!Clip) return;` ab. Genau dann braucht man sie aber: Es gibt noch
     * keinen Clip, der eine Vorlage tragen koennte.
     */
    static vorlageSetzen(spurNr, vorlage, quelle = 'modell') {
        const spur = state.project.tracks[spurNr];
        if (!spur || spur.type !== 'model') return;
        pushUndo('Preset ändern');
        const clip = Modellmenue._clipAmAbspielkopf(spur, spurNr);
        if (clip) {
            clip.data = clip.data || {};
            clip.data.preset = vorlage;
            clip.data.quelle = quelle;
            clip.name = vorlage;
        } else {
            const laenge = Math.max(MINDESTLAENGE,
                                    state.project.duration * state.project.fps);
            const neu = new Clip(null, vorlage, laenge, state.project.fps);
            neu.type = 'model';
            neu.startFrame = 0;
            neu.data = { preset: vorlage, quelle, bodyType: 'Female_Caucasian' };
            spur.clips.push(neu);
        }
        spur._currentPreset = null;          // erzwingt das Neuladen des Modells
        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updateProperties();
        Protokoll.debug('BVH Studio', `Model preset changed to: ${vorlage}`);
    }

    static _clipAmAbspielkopf(spur, spurNr) {
        if (state.selectedClipIdx >= 0 && state.selectedTrackIdx === spurNr) {
            return spur.clips[state.selectedClipIdx];
        }
        const t = state.playheadFrame / state.project.fps;
        for (const c of spur.clips) {
            const anfang = c.startFrame / state.project.fps;
            if (t >= anfang && t < anfang + c.duration) return c;
        }
        return null;
    }
}
