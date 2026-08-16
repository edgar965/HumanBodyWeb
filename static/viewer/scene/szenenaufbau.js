import { state, SESSION_KEY } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { loadCharmorphHairUI } from './charmorph_hair.js';
import { initFinalizeTab } from './finalize.js';
import { Szenenbuehne } from './szenenbuehne.js';
import { Szenenschleife } from './szenenschleife.js';
import { Starteinstellungen } from './starteinstellungen.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Szenenaufbau — der Start der Szene-Seite: Bühne, Bedienung verdrahten,
 * Einstellungen anwenden, Figur laden.
 *
 * Aus `boot.js init()` herausgeloest (Umbau 16.08.2026): 169 Zeilen, in denen
 * Bühnenbau, 25 Verdrahtungsaufrufe, der Demo-Knopf und die gesamte
 * Startsequenz hintereinander standen. Die 25 Aufrufe sind jetzt eine Liste —
 * dort sieht man auf einen Blick, was die Seite alles aufsetzt, und ein
 * fehlender Aufruf fällt auf (genau so ein Fehler ist beim Umbau der
 * Animationsseite entstanden).
 */
export class Szenenaufbau {

    /**
     * Was beim Start verdrahtet wird, in dieser Reihenfolge. Namen aus der
     * Registrierung `fn`; ein fehlender Eintrag wird gemeldet, statt die
     * ganze Seite mit einem TypeError abzubrechen.
     */
    static AUFBAUEN = [
        'bindLightingUI', 'bindRendererUI', 'bindCameraUI', 'bindActions',
        'bindMenubar', 'initCharacterDialog', 'initSceneDialogs',
        '_initSaveAnimDialog', 'bindKeyboardShortcuts', 'bindCanvasClick',
        'initSubMeshInteraction', 'initTabs', 'bindVisibilityToggles',
        'initPropGarmentControls', '_initPropMHControls', 'initPropHairControls',
        'loadPoseUI', 'loadMHProxyUI', 'loadGarmentUI', 'loadKleiderUI',
        'loadHairUI', 'loadClothUI', 'loadAnimationUI', 'loadCharmorphAssets',
    ];

    /** Vorgabe-Animation des Demo-Knopfs. */
    static DEMO_URL = '/api/character/bvh/Mixamo/Catwalk_Idle_02/';
    static DEMO_NAME = 'Catwalk Idle 02';
    /** Erst nach dieser Zeit wird Vorgabekleidung angezogen — nach dem Start. */
    static KLEIDUNG_VERZOEGERUNG_MS = 3000;

    async starten() {
        new Szenenbuehne().bauen();
        this._bereicheKlappbar();
        // Die Einstellungen laufen parallel zum Verdrahten — sie werden erst
        // in der Startsequenz gebraucht.
        const einstellungen = Starteinstellungen.holen();
        this.verdrahten();
        fn.initRiggingTab(fn.toggleRigVisibility);
        loadCharmorphHairUI();
        initFinalizeTab();
        this.demoknopf();
        fn.loadSettings();
        window.addEventListener('beforeunload', () => fn.saveSessionState());
        new Szenenschleife().starten();
        await this.startsequenz(await einstellungen);
        return this;
    }

    verdrahten() {
        for (const name of Szenenaufbau.AUFBAUEN) {
            const aufruf = fn[name];
            if (typeof aufruf !== 'function') {
                console.warn('[Scene] Aufbau fehlt:', name);
                continue;
            }
            aufruf();
        }
    }

    _bereicheKlappbar() {
        for (const kopf of document.querySelectorAll('.panel-section h3')) {
            kopf.addEventListener('click', () => {
                kopf.closest('.panel-section').classList.toggle('collapsed');
            });
        }
    }

    // ---------------------------------------------------------- Startsequenz

    /**
     * Sitzung wiederherstellen oder Vorgabefigur laden, Pose setzen,
     * Vorgabekleidung anziehen.
     */
    async startsequenz(einstellungen) {
        await Promise.all([this._hautfarben(), this._haarfarben(),
                           fn.loadRigifySkeleton(), fn.loadSkinWeights()]);
        const hatSitzung = !!sessionStorage.getItem(SESSION_KEY);
        if (hatSitzung) await fn.restoreSessionState();
        if (state.characters.size === 0) {
            try {
                await fn.loadDefaultCharacter();
            } catch (fehler) {
                console.warn('[Scene] Vorgabefigur nicht ladbar:', fehler);
            }
        }
        fn.captureInitial?.();
        await this._pose(einstellungen);
        this._vorgabekleidung(einstellungen, hatSitzung);
    }

    async _pose(einstellungen) {
        const pfad = einstellungen.posenpfad();
        if (!pfad || state.characters.size === 0) return;
        try {
            await fn.applyPoseFromServer(pfad);
        } catch (fehler) {
            console.warn('[Pose] Anfangspose fehlgeschlagen:', fehler);
        }
    }

    /**
     * MakeHuman-Vorgabekleidung anziehen — nur bei einer frischen Seite ohne
     * Sitzung und wenn keine Figur schon eigene Stücke trägt. Verzögert, damit
     * der Start nicht auf die Anpassung wartet.
     */
    _vorgabekleidung(einstellungen, hatSitzung) {
        if (hatSitzung || !einstellungen.mhKleidung.length) return;
        if (state.characters.size === 0) return;
        const eigene = [...state.characters.values()]
            .some(figur => Object.keys(figur.mhProxies || {}).length > 0);
        if (eigene) return;
        setTimeout(async () => {
            for (const kennung of einstellungen.mhKleidung) {
                try {
                    state._selectedMHId = kennung;
                    await fn._doMHProxyFit();
                    Protokoll.debug('MH Auto', 'angezogen:', kennung);
                } catch (fehler) {
                    console.warn('[MH Auto] fehlgeschlagen:', kennung, fehler);
                }
            }
        }, Szenenaufbau.KLEIDUNG_VERZOEGERUNG_MS);
    }

    async _hautfarben() {
        try {
            const daten = await fn.fetchMorphDefs();
            state.skinColors = daten.skin_colors || {};
        } catch (fehler) {
            console.warn('[Scene] Hautfarben nicht ladbar:', fehler);
        }
    }

    async _haarfarben() {
        const daten = await Serverabruf.jsonOderNull('/api/character/hairstyles/');
        state.hairColorData = daten?.colors || {};
    }

    // ------------------------------------------------------------ Demo-Knopf

    /** Der Knopf spielt eine Beispielanimation und hält sie wieder an. */
    demoknopf() {
        const knopf = document.getElementById('play-demo-anim');
        if (!knopf) return;
        knopf.addEventListener('click', () => {
            if (!state.currentAction) {
                if (!fn._selectedInst() && !state.bodyMesh) return;
                fn.loadBVHAnimation(Szenenaufbau.DEMO_URL,
                                    Szenenaufbau.DEMO_NAME, 0);
                return;
            }
            this._umschalten(knopf);
        });
    }

    _umschalten(knopf) {
        const laeuft = state.playing;
        if (!laeuft && !state.currentAction.isRunning()) state.currentAction.play();
        state.currentAction.paused = laeuft;
        state.playing = !laeuft;
        knopf.innerHTML = laeuft ? '<i class="fas fa-play"></i>'
                                 : '<i class="fas fa-pause"></i>';
        knopf.classList.toggle('active', !laeuft);
    }
}
