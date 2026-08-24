import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { loadRigifySkeleton, loadSkinWeights, loadSkinColors,
         loadHairColors } from '../character_core.js?v=1';
import { loadLibrary, setupLibraryManagement, setupSidebarResize } from './library.js';
import { createSceneLightTracks } from './spur_lichter.js';
import { setupTimeline } from './timeline.js';
import { setupPlayback } from './playback.js';
import { setupToolbar } from './tools.js';
import { setupExportPanel } from './export_video.js';
import { bindClothExportButtons } from './export1.js';
import { Projektwiederherstellung } from './projekt_wiederherstellung.js';
import { Sitzung } from './sitzung.js';
import { createFloorTrack } from './spur_boden.js';
import { setupTheatreMenu } from './theatre_lichter.js';
import { setupSceneObjectImport } from './objektimport.js';
import { Anfasser } from './anfasser.js';
import { setupViewportContextMenu } from './szenenmenue.js';
import { Studiobuehne } from './studiobuehne.js';
import { Studioschleife } from './studioschleife.js';
import { Studioeinstellungen } from './studioeinstellungen.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Studiostart — der Start des BVH-Studios.
 *
 * Aus `index.js init()` herausgeloest (Umbau 16.08.2026): 146 Zeilen, in denen
 * Bühne, Vorgaben, Bibliothek, acht Aufbaurufe, das Laden des Vorgabeprojekts
 * und die Renderschleife hintereinander standen. Das Laden des Vorgabeprojekts
 * allein waren 40 Zeilen mit vier verschachtelten `try`-Blöcken.
 */
export class Studiostart {

    /** Reihenfolge des Aufbaus. */
    static AUFBAUEN = [setupTimeline, setupPlayback, setupToolbar,
                       setupExportPanel, bindClothExportButtons,
                       setupViewportContextMenu, setupTheatreMenu,
                       setupSceneObjectImport];

    /** Schlüssel, unter dem die verworfene Sitzung ihren Anzeigestand ablegt. */
    static UI_SCHLUESSEL = 'bvhStudio_sessionState__ui';

    async starten() {
        new Studiobuehne().bauen();
        await Promise.all([loadRigifySkeleton(), loadSkinWeights(),
                           loadSkinColors(), loadHairColors()]);
        const einstellungen = (await Studioeinstellungen.holen()).anwenden();
        this.bibliothek();
        for (const aufbau of Studiostart.AUFBAUEN) aufbau();
        Anfasser.aufbauen();

        const wiederhergestellt = await Sitzung.wiederherstellen();
        if (!wiederhergestellt && state.project.tracks.length === 0) {
            await this.vorgabeprojekt(einstellungen);
        }
        this.szenenspuren();
        new Studioschleife().starten();
        this.debugzugaenge();
        fn.updateStudioInfo?.();
        Protokoll.debug('BVH Studio', 'gestartet'
                    + (wiederhergestellt ? ' (Sitzung wiederhergestellt)' : ''));
        return this;
    }

    /**
     * Bibliothek: Verwaltung und Größenziehen sofort, das Einlesen der über
     * 7000 Dateien im Hintergrund — sonst wartet der Start darauf.
     */
    bibliothek() {
        setupLibraryManagement();
        setupSidebarResize();
        const baum = document.getElementById('lib-tree');
        if (baum) {
            baum.innerHTML = '<div class="lib-hinweis">'
                + '<i class="fas fa-spinner fa-spin"></i>'
                + 'BVH-Library wird geladen …</div>';
        }
        loadLibrary().catch(fehler => {
            Protokoll.warnung('BVH Studio', 'Library nicht ladbar:', fehler);
            if (!baum) return;
            baum.innerHTML = '<div class="lib-hinweis lib-fehler">'
                + 'Library-Load fehlgeschlagen. '
                + '<a href="#" id="lib-retry">Erneut versuchen</a></div>';
            document.getElementById('lib-retry')?.addEventListener('click', ereignis => {
                ereignis.preventDefault();
                loadLibrary();
            });
        });
    }

    // ------------------------------------------------------- Vorgabeprojekt

    /** Das in den Einstellungen genannte Projekt laden, wenn es noch existiert. */
    async vorgabeprojekt(einstellungen) {
        if (!einstellungen.vorgabeprojekt) return;
        try {
            const pfad = await this._projektpfad(einstellungen);
            if (!pfad) return;
            const daten = await this._projektdaten(pfad);
            if (!daten?.name) {
                Protokoll.warnung('BVH Studio', 'project-load ohne Projekt:', pfad);
                return;
            }
            await Projektwiederherstellung.uebernehmen(daten);
            Protokoll.debug('BVH Studio', 'Vorgabeprojekt geladen:',
                        einstellungen.vorgabeprojekt);
            this.anzeigestandUebernehmen();
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'Vorgabeprojekt nicht ladbar:', fehler);
        }
    }

    /** Pfad der Projektdatei zum Namen aus den Einstellungen. */
    async _projektpfad(einstellungen) {
        const adresse = '/api/studio/project-list/?dir='
            + encodeURIComponent(einstellungen.projektpfad);
        const liste = await Serverabruf.json(adresse);
        const treffer = (liste.files || []).find(datei =>
            datei.name.replace(/\.studio\.json$/i, '')
            === einstellungen.vorgabeprojekt);
        return treffer?.path || null;
    }

    async _projektdaten(pfad) {
        const inhalt = await Serverabruf.json(
            '/api/studio/project-load/?path=' + encodeURIComponent(pfad));
        // Die Schnittstelle liefert { ok, project, path } — das Projekt liegt
        // eine Ebene tiefer, ältere Antworten kamen flach.
        return inhalt.project || inhalt;
    }

    /**
     * Abspielkopf, Zoom und Auswahl aus einer verworfenen Sitzung übernehmen.
     * Der Stand wird dabei gelöscht: Er gehört zum Projekt, das gerade geladen
     * wurde, und passt beim nächsten Start nicht mehr.
     */
    anzeigestandUebernehmen() {
        let stand = null;
        try {
            const roh = sessionStorage.getItem(Studiostart.UI_SCHLUESSEL);
            if (!roh) return;
            stand = JSON.parse(roh);
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'Anzeigestand unlesbar:', fehler);
            return;
        }
        state.playheadFrame = stand.playheadFrame ?? 0;
        state.timelineZoom = stand.timelineZoom ?? 100;
        state.timelineScrollX = stand.timelineScrollX ?? 0;
        state.selectedTrackIdx = stand.selectedTrackIdx ?? -1;
        state.selectedClipIdx = stand.selectedClipIdx ?? -1;
        sessionStorage.removeItem(Studiostart.UI_SCHLUESSEL);
        const zoom = document.getElementById('tl-zoom');
        if (zoom) zoom.value = state.timelineZoom;
        fn.applyPlayhead?.();
    }

    /**
     * Boden und Licht als Spuren anmelden — NACH dem Wiederherstellen, damit
     * die Indizes der Benutzerspuren stabil bleiben (`_linkedAnimIdx` zeigt
     * sonst auf die falsche Spur).
     */
    szenenspuren() {
        createFloorTrack();
        createSceneLightTracks();
        delete state.project._pendingSceneOverrides;
        fn.updateTrackHeaders?.();
        fn.renderTimeline?.();
        fn.updateProperties?.();
    }

    /** Zugänge für die Fehlersuche in der Konsole. */
    debugzugaenge() {
        window.__studioProject = state.project;
        window.__studioState = state;
        window.__studioFn = fn;
    }
}
