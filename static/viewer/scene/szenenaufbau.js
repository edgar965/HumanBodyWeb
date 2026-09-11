import { state, SESSION_KEY } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { loadCharmorphHairUI } from './charmorph_hair.js';
import { initFinalizeTab } from './finalize.js';
import { Szenenbuehne } from './szenenbuehne.js';
import { Szenenschleife } from './szenenschleife.js';
import { Starteinstellungen } from './starteinstellungen.js';
import { Reitergedaechtnis } from './reitergedaechtnis.js';
import { Reiterfreigabe } from './reiterfreigabe.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Startmessung } from '../gemeinsam/startmessung.js';
import { Klappbereiche } from '../gemeinsam/klappbereiche.js';
import { Reiterinhalt } from './reiterinhalt.js';

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
        'greifenBeobachten',
        'initSubMeshInteraction', 'initTabs', 'bindVisibilityToggles',
        'initPropGarmentControls', '_initPropMHControls', 'initPropHairControls',
        'mhAnwendenVerdrahten',
        // ACHT WEITERE STANDEN HIER (bis 10.09.2026): `loadPoseUI`,
        // `loadMHProxyUI`, `loadGarmentUI`, `loadKleiderUI`, `loadHairUI`,
        // `loadClothUI`, `loadAnimationUI`, `loadCharmorphAssets`. Sie
        // fuellen Reiter, von denen einer offen ist, und kosteten zusammen
        // 4,5 Sekunden. Jetzt baut sie `Reiterinhalt`, wenn ihr Reiter
        // aufgeht — dort stehen die Messwerte.
    ];

    /** Vorgabe-Animation des Demo-Knopfs. */
    static DEMO_URL = '/api/character/bvh/Mixamo/Catwalk_Idle_02/';
    static DEMO_NAME = 'Catwalk Idle 02';
    /** Erst nach dieser Zeit wird Vorgabekleidung angezogen — nach dem Start. */
    static KLEIDUNG_VERZOEGERUNG_MS = 3000;

    async starten() {
        // JEDER SCHRITT EINZELN GEMESSEN (10.09.2026, Edgar: „mehr als 10 s
        // bis das UI ohne Modell aufgebaut wird"). Von aussen war nicht zu
        // sehen, welcher Schritt die Zeit verbraucht — Server, Module und
        // DOM-Aufbau waren alle gemessen schnell. Begruendung und
        // Messwerte in `gemeinsam/startmessung.js`.
        const M = Startmessung;
        M.um('Buehne bauen', () => new Szenenbuehne().bauen());
        M.um('Bereiche klappbar', () => this._bereicheKlappbar());
        // Die Einstellungen laufen parallel zum Verdrahten — sie werden erst
        // in der Startsequenz gebraucht.
        const einstellungen = Starteinstellungen.holen();
        this.verdrahten();
        // Der SICHTBARE Reiter bekommt seinen Inhalt sofort — die acht
        // uebrigen erst, wenn sie aufgehen. Vorgabe ist „Eigenschaften",
        // der keinen dieser Aufbauten braucht; kostet also nichts. Steht
        // ein anderer im Reitergedaechtnis, baut ihn `switchTab` am Ende
        // der Startsequenz.
        Reiterinhalt.offenen();
        M.um('Rigging-Reiter', () => fn.initRiggingTab(fn.toggleRigVisibility));
        M.um('Charmorph-Haare', () => loadCharmorphHairUI());
        M.um('Finalize-Reiter', () => initFinalizeTab());
        M.um('Demoknopf', () => this.demoknopf());
        M.um('Einstellungen lesen', () => fn.loadSettings());
        window.addEventListener('beforeunload', () => fn.saveSessionState());
        M.um('Renderschleife', () => new Szenenschleife().starten());
        await M.umAsync('Startsequenz (Figur, Pose, Kleidung)',
                        async () => this.startsequenz(await einstellungen));
        // NICHT hier berichten: Die `async`-Aufbauten laufen noch.
        M.berichtWennRuhig();
        return this;
    }

    verdrahten() {
        for (const name of Szenenaufbau.AUFBAUEN) {
            const aufruf = fn[name];
            if (typeof aufruf !== 'function') {
                Protokoll.warnung('Scene', 'Aufbau fehlt:', name);
                continue;
            }
            // Einzeln gemessen: Diese Schleife baut die Panels, darunter den
            // Animationsbaum mit 21.299 Elementen. Ohne Messung je Aufruf
            // waere nicht zu sehen, welcher davon teuer ist.
            Startmessung.um(name, aufruf);
        }
    }

    /** Abschnitte auf- und zuklappbar machen — siehe `Klappbereiche`. */
    _bereicheKlappbar() {
        Klappbereiche.verdrahten();
    }

    // ---------------------------------------------------------- Startsequenz

    /**
     * Sitzung wiederherstellen oder Vorgabefigur laden, Pose setzen,
     * Vorgabekleidung anziehen.
     */
    async startsequenz(einstellungen) {
        // JEDER TEIL EINZELN (10.09.2026): Als Block gemessen waren es 3.277
        // von 6.201 ms — welcher Teil davon, sagte die Zahl nicht.
        const M = Startmessung;
        // NUR DIE HAUTFARBEN HALTEN DIE FIGUR AUF (10.09.2026, Edgar: „Lade
        // asynchron, ich will ganz schnell das Modell sehen").
        //
        // Vorher wartete die Startsequenz auf alle vier, bevor die Figur
        // ueberhaupt begann. Einzeln gemessen: Hautfarben 69 ms (20 KB),
        // Haarfarben 41 ms (1 KB), Skelett 31 ms (28 KB), Hautgewichte
        // 71 ms (2.444 KB). Der Koerper braucht davon genau eines — die
        // Hautfarben, fuer `Charakterkoerper.hautfarbe`. Skelett und
        // Gewichte braucht erst das ZUBEHOER; es wartet in
        // `CharacterInstance.load` auf `state.grunddatenBereit`.
        const grunddaten = M.umAsync('  Haarfarben, Skelett, Gewichte', () =>
            Promise.all([this._haarfarben(), fn.loadRigifySkeleton(),
                         fn.loadSkinWeights()]));
        state.grunddatenBereit = grunddaten;
        await M.umAsync('  Hautfarben', () => this._hautfarben());
        const hatSitzung = !!sessionStorage.getItem(SESSION_KEY);
        if (hatSitzung) {
            await M.umAsync('  Sitzung wiederherstellen',
                            () => fn.restoreSessionState());
        }
        if (state.characters.size === 0) {
            try {
                await M.umAsync('  Vorgabefigur laden',
                                () => fn.loadDefaultCharacter());
            } catch (fehler) {
                Protokoll.warnung('Scene', 'Vorgabefigur nicht ladbar:', fehler);
            }
        }
        M.um('  Anfangszustand merken', () => fn.captureInitial?.());
        await M.umAsync('  Pose setzen', () => this._pose(einstellungen));
        M.um('  Vorgabekleidung anstossen',
             () => this._vorgabekleidung(einstellungen, hatSitzung));
        M.um('  Reitergedaechtnis', () => this._reitergedaechtnis());
        // Zum Schluss abwarten, damit ein Fehler in den Grunddaten gemeldet
        // wird und nicht als unbehandelte Ablehnung endet.
        await M.umAsync('  Grunddaten abschliessen', () => grunddaten);
    }

    /**
     * Die letzten Einstellungen der Reiter zurueckholen (09.09.2026).
     *
     * ZULETZT in der Startsequenz: Die Reiterfreigabe haengt daran, ob eine
     * Figur steht (`Reiterfreigabe.frei`), und ein Reiter, der beim Start
     * ausgegraut ist, darf auch nicht aufgehen. Die GarmentCode-Regler
     * bekommen ihre Werte NICHT hier, sondern wenn sie entstehen
     * (`Garmentcodegedaechtnis`) — zu diesem Zeitpunkt gibt es sie noch
     * nicht.
     */
    _reitergedaechtnis() {
        const gesetzt = Reitergedaechtnis.starten();
        const reiter = Reitergedaechtnis.letzterReiter();
        if (reiter && Reiterfreigabe.frei(reiter)) fn.switchTab?.(reiter);
        Protokoll.debug('Reiter', `${gesetzt} Einstellungen wiederhergestellt`,
                        reiter ? `zuletzt offen: ${reiter}` : '');
    }

    async _pose(einstellungen) {
        const pfad = einstellungen.posenpfad();
        if (!pfad || state.characters.size === 0) return;
        try {
            await fn.applyPoseFromServer(pfad);
        } catch (fehler) {
            Protokoll.warnung('Pose', 'Anfangspose fehlgeschlagen:', fehler);
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
                    Protokoll.warnung('MH Auto', 'fehlgeschlagen:', kennung, fehler);
                }
            }
        }, Szenenaufbau.KLEIDUNG_VERZOEGERUNG_MS);
    }

    async _hautfarben() {
        try {
            const daten = await fn.fetchMorphDefs();
            state.skinColors = daten.skin_colors || {};
        } catch (fehler) {
            Protokoll.warnung('Scene', 'Hautfarben nicht ladbar:', fehler);
        }
    }

    async _haarfarben() {
        const daten = await Serverabruf.jsonOderNull('/api/character/hairstyles/');
        state.hairColorData = daten?.colors || {};
    }

    // ------------------------------------------------------------ Demo-Knopf

    /**
     * Der Knopf in der Kopfleiste: Play für die AUSGEWÄHLTE Figur
     * (`Abspielsteuerung`, über `fn.abspielen`). Hat die Figur noch keine
     * Animation gewählt, läuft die Beispielanimation. Vorher schaltete er nur
     * die laufende Aktion um — egal, welche Figur ausgewählt war.
     */
    demoknopf() {
        const knopf = document.getElementById('play-demo-anim');
        if (!knopf) return;
        knopf.addEventListener('click', () => fn.abspielen(
            { url: Szenenaufbau.DEMO_URL, name: Szenenaufbau.DEMO_NAME }));
    }
}
