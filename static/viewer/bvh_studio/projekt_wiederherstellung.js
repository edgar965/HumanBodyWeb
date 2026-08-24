/**
 * Projektwiederherstellung — eine gespeicherte .studio.json zurueck in den
 * Studiozustand bringen.
 *
 * Aus project.js herausgeloest (Umbau 16.08.2026): `restoreProjectData` war eine
 * einzige Funktion mit 191 Zeilen und vier Verschachtelungsebenen (Spuren →
 * Clips → zwei eingebettete async-Funktionen). Jetzt ein Schritt je Methode.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { Studioanzeige } from './studioanzeige.js';
import { Projektnachladen } from './projekt_nachladen.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Projektwiederherstellung {
    static async uebernehmen(data) {
        Protokoll.debug('Restore', `Starting. Input tracks: ${data.tracks?.length}, `
                    + `clips: ${data.tracks?.map(t => t.clips?.length)}`);
        // Rueckgaengig-Aufzeichnung fuer den GESAMTEN Vorgang aussetzen.
        state._undoSuppressed = true;

        // Alte Saves koennen _sceneLight-/_sceneItem-Spuren enthalten — die filtern
        // wir raus, damit createSceneLightTracks/createFloorTrack die Szenenelemente
        // frisch anlegen.
        const eingang = (data.tracks || [])
            .filter(td => !(td._sceneLight || td._sceneItem));

        for (let i = state.project.tracks.length - 1; i >= 0; i--) fn.removeTrack(i);

        state.project.name = data.name || 'Untitled';
        state.project.fps = data.fps || 30;

        // Szenen-Vorgaben zwischenlegen — createSceneLightTracks/createFloorTrack
        // wenden sie an. WICHTIG: undefined (Legacy-Save ohne Feld) → Vorgaben
        // erzeugen; {} (Save mit ausdruecklich leerem Licht-Dict) → nichts erzeugen.
        state.project._pendingSceneOverrides = {
            sceneLights: data.sceneLights,   // undefined bleibt undefined
            sceneFloor: data.sceneFloor || null,
        };

        const neueNummer = Projektwiederherstellung._indexTabelle(data.tracks || []);
        const wartend = [];
        for (const td of eingang) {
            const track = Projektwiederherstellung._spurAnlegen(td, neueNummer);
            for (const cd of (td.clips || [])) {
                Projektwiederherstellung._klipAnlegen(track, td, cd, wartend);
            }
        }
        await Promise.all(wartend);

        Projektwiederherstellung._modellspurenVerlinken();
        state._undoSuppressed = false;

        fn.updateDuration();
        fn.renderTimeline();
        fn.updateTrackHeaders();
        fn.applyPlayhead();  // Modellspuren aktivieren + Netze zeigen
        Protokoll.debug('BVH Studio', `Project restored: ${state.project.name} `
                    + `(${state.project.tracks.length} tracks)`);
        Studioanzeige.aktualisieren();
    }

    /**
     * Alte Save-Nummern → neue Nummern nach dem Filtern.
     * Wird auf `_linkedAnimIdx` angewandt; -1 heisst "rausgefiltert".
     */
    static _indexTabelle(gespeichert) {
        const tabelle = {};
        let neu = 0;
        gespeichert.forEach((td, alt) => {
            tabelle[alt] = (td._sceneLight || td._sceneItem) ? -1 : neu++;
        });
        return tabelle;
    }

    static _spurAnlegen(td, neueNummer) {
        const art = td.type || 'bvh';
        let track;
        if (art === 'bvh') {
            // Alte Namen "Track X" heissen heute "Animation X".
            let name = td.name;
            if (name && /^Track \d+$/.test(name)) name = name.replace('Track', 'Animation');
            track = fn.addTrack(name, true);  // Automodellspur beim Laden ueberspringen
            track.preset = td.preset || 'FemaleGarment';
            track.bodyType = td.bodyType || 'Female_Caucasian';
        } else if (art === 'model') {
            track = fn.addModelTrack(td.name);
            const gespeichert = td._linkedAnimIdx ?? -1;
            track._linkedAnimIdx = (gespeichert >= 0 && neueNummer[gespeichert] != null)
                ? neueNummer[gespeichert] : -1;
            track._currentPreset = td._currentPreset || null;
        } else {
            track = fn.addSpecialTrack(art, td.name);
        }
        track.color = td.color || track.color;
        track.muted = td.muted || false;
        track.position = td.position || [0, 0, 0];
        if (track.group) track.group.position.set(track.position[0], 0, track.position[2]);
        if (art === 'camera') track.cameraActive = td.cameraActive ?? true;
        if (art === 'light' && track.light && td.lightPosition) {
            Projektwiederherstellung._lichtUebernehmen(track, td);
        }
        return track;
    }

    static _lichtUebernehmen(track, td) {
        const licht = track.light;
        licht.color.set(td.lightColor || '#ffffff');
        licht.intensity = td.lightIntensity ?? 2;
        licht.position.set(td.lightPosition.x, td.lightPosition.y, td.lightPosition.z);
        if (licht.target && td.lightTarget) {
            licht.target.position.set(td.lightTarget.x, td.lightTarget.y, td.lightTarget.z);
            licht.target.updateMatrixWorld();
        }
        if (td.lightAngle != null) licht.angle = td.lightAngle;
        if (td.lightPenumbra != null) licht.penumbra = td.lightPenumbra;
        if (td.lightDistance != null) licht.distance = td.lightDistance;
        // Helferlinien beim Laden IMMER aus — der gespeicherte Wert wird bewusst
        // ignoriert, weil sie sonst bei jedem Projektstart die Szene zustellen.
        track.lightVisible = false;
        track.coneVisible = td.coneVisible ?? true;    // Lichtkegel: Vorgabe an
        if (track.lightHelper?.update) track.lightHelper.update();
    }

    static _klipAnlegen(track, td, cd, wartend) {
        const clip = new Clip(cd.category, cd.name, cd.totalFrames || 100, cd.fps || 30);
        clip.type = cd.type || 'bvh';
        // Kaputte Clips aus alten Teilungen: auf Modellspuren muss der Typ 'model' sein.
        if (track.type === 'model' && clip.type === 'bvh') {
            clip.type = 'model';
            if (!clip.data?.preset) {
                clip.data = { preset: td.preset || 'Rig1',
                              bodyType: td.bodyType || 'Female_Caucasian' };
            }
        }
        clip.startFrame = cd.startFrame || 0;
        clip.trimIn = cd.trimIn || 0;
        clip.trimOut = cd.trimOut || 0;
        clip.speed = cd.speed || 1;
        clip.smoothSigma = cd.smoothSigma || 0;
        clip.groundFix = cd.groundFix || false;
        clip.blendIn = cd.blendIn || 0;
        clip.blendOut = cd.blendOut || 0;
        if (cd.data) clip.data = cd.data;
        track.clips.push(clip);

        if (clip.type === 'bvh') {
            wartend.push(fn.loadClipAnimation(track, clip));
        } else if (clip.type === 'object_clip' && clip.data?.url
                   && track.type === 'scene_object') {
            wartend.push(Projektnachladen.objekt(track, td, clip));
        } else if (clip.type === 'audio' && clip.data?.audioUrl) {
            // Doppelten Schraegstrich aus alten Saves richten
            if (clip.data.audioUrl.startsWith('//')) {
                clip.data.audioUrl = clip.data.audioUrl.substring(1);
            }
            wartend.push(Projektnachladen.ton(track, clip));
        } else if (clip.type === 'audio') {
            clip._needsReload = true;
            Protokoll.warnung('Restore', `Audio "${clip.data?.fileName}" has no server URL `
                         + '— needs manual reload');
        }
        return clip;
    }

    /**
     * Modellspuren mit ungueltigem `_linkedAnimIdx` auf die erste BVH-Spur legen
     * (alte Saves, bei denen die Verknuepfung durch eingefuegte Szenenlichter
     * verrutscht ist).
     */
    static _modellspurenVerlinken() {
        const erste = state.project.tracks.findIndex(t => t.type === 'bvh');
        if (erste < 0) return;
        for (const t of state.project.tracks) {
            if (t.type !== 'model') continue;
            const verbunden = state.project.tracks[t._linkedAnimIdx];
            if (verbunden && verbunden.type === 'bvh') continue;
            Protokoll.debug('Restore', `Model-Track "${t.name}" neu verlinkt `
                        + `(war ${t._linkedAnimIdx}) → ${erste}`);
            t._linkedAnimIdx = erste;
        }
    }
}

fn.restoreProjectData = Projektwiederherstellung.uebernehmen;
