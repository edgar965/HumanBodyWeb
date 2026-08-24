/**
 * Theatre-Studio — Aufbau der Bühne und Verdrahtung der Bedienung.
 *
 * UMBAU 18.08.2026: 788 Zeilen in einem einzigen `DOMContentLoaded`-Zuhoerer.
 * Herausgeloest wurden:
 *
 *     studio/studiostart.js          Theatre.js hochfahren, Oberflaeche ruecken
 *     studio/zeigerwahl.js           Klick auf Licht / Kleidung / Figur
 *     studio/studioknoepfe.js        Rig, Abspielen, Studio, Modelle-Reiter
 *     studio/zeitleistenwerkzeuge.js Timeline neu aufbauen / leeren
 *     studio/szenenspeicherung.js    Dialog „Szene speichern"
 *     studio/buehnenzugaben.js       GLB einfuegen, Vorgabe, Zusatzlicht
 *     studio/videoaufnahme.js        Dialog „Als MP4 exportieren"
 *     studio/studiovorgaben.js       Startvorgaben aus den Einstellungen
 *     studio/buehnenschleife.js      Bildschleife
 *     studio/exportreiter.js         Reiter „Export"
 *
 * Was hier bleibt, ist die Reihenfolge: Erst die Bühne, dann Theatre.js, dann
 * die Bedienung — und der Abspieler VOR dem Animationslauf.
 */
import studio from '@theatre/studio';
import { createScene } from './scene-setup.js';
import { setupTheatre, createCameraSheet, createLightSheet,
         getAllTheatreObjects } from './theatre-bridge.js';
import { VideoExporter } from './video-export.js';
import { KeyframeUI } from './keyframe-ui.js';
import { Skinner } from './studio/skinner.js';
import { Lichtpanel } from './studio/panels/lichtpanel.js';
import { Kleiderpanel } from './studio/panels/kleiderpanel.js';
import { Figurpanel } from './studio/panels/figurpanel.js';
import { Bildexport } from './studio/bildexport.js';
import { Auswahl } from './studio/auswahl.js';
import { Figurenlader } from './studio/figurenlader.js';
import { Seitenlisten } from './studio/seitenlisten.js';
import { Abspieler } from './studio/abspieler.js';
import { Kamerabahn } from './studio/kamerabahn.js';
import { Animationslauf } from './studio/animationslauf.js';
import { Bedienleiste } from './studio/bedienleiste.js';
import { Studiostart } from './studio/studiostart.js';
import { Zeigerwahl } from './studio/zeigerwahl.js';
import { Studioknoepfe } from './studio/studioknoepfe.js';
import { Zeitleistenwerkzeuge } from './studio/zeitleistenwerkzeuge.js';
import { Szenenspeicherung } from './studio/szenenspeicherung.js';
import { Buehnenzugaben } from './studio/buehnenzugaben.js';
import { Videoaufnahme } from './studio/videoaufnahme.js';
import { Studiovorgaben } from './studio/studiovorgaben.js';
import { Buehnenschleife } from './studio/buehnenschleife.js';
import { Exportreiter } from './studio/exportreiter.js';
import { PRESETS, applyPreset } from './presets.js';
import { Protokoll } from '../../static/viewer/gemeinsam/protokoll.js';

/** Nach `DOMContentLoaded` waere es zu spaet — siehe studio/studiostart.js. */
Studiostart.hochfahren(studio);

/** Wartezeit, bis die Buehne steht und der Autostart greifen darf. */
const AUTOSTART_MS = 3000;

window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('theatre-canvas');
    if (!canvas) {
        Protokoll.fehler('main', 'theatre-canvas nicht gefunden');
        return;
    }

    // 1. Bühne
    const { scene, camera, renderer, controls, lights, lightIcons,
            transformControls } = createScene(canvas);
    Object.assign(window, { scene, camera, lights, lightIcons,
                            transformControls,
                            activeMixer: null, isPlaying: false,
                            currentTime: 0, animDuration: 1 });

    // Auswahl (Figur / Licht / Kleidung) in einer Klasse — vorher zwei
    // Closure-Variablen, an fuenfzehn Stellen gesetzt und gelesen.
    const auswahl = new Auswahl(transformControls);
    window.auswahl = auswahl;
    const loadedCharacters = [];

    // Skelett, Gewichte und die Umwandlung zu SkinnedMesh: studio/skinner.js.
    const skinner = new Skinner(scene, loadedCharacters);
    skinner.laden();
    window.skinner = skinner;

    // Eigenschaften-Felder. Sie muessen VOR der Zeigerwahl stehen: `const` in
    // einem Block gilt erst ab seiner Zeile.
    const lichtpanel = new Lichtpanel(lights);
    const kleiderpanel = new Kleiderpanel();
    const figurpanel = new Figurpanel();
    Object.assign(window, { lichtpanel, kleiderpanel, figurpanel });

    // Figuren laden (Vorgabe, Szene) und Bühnenzustand speichern:
    // studio/figurenlader.js — der Kern stand vorher dreimal in dieser Datei.
    const figurenlader = new Figurenlader(scene, loadedCharacters, skinner,
                                          auswahl);
    window.figurenlader = figurenlader;

    new Zeigerwahl({ canvas, camera, lightIcons, figuren: loadedCharacters,
                     auswahl, lichtpanel, kleiderpanel,
                     figurpanel }).verdrahten();

    // 2. Theatre-Projekt und -Blatt
    const { project, sheet } = setupTheatre();
    window.theatreProject = project;
    window.theatreSheet = sheet;

    // 3. Kamera und die drei Bühnenlichter als animierbare Objekte anmelden
    const cameraObj = createCameraSheet(sheet, camera);
    createLightSheet(sheet, 'Spot Left', lights.spotLeft);
    createLightSheet(sheet, 'Spot Right', lights.spotRight);
    createLightSheet(sheet, 'Back Light', lights.backLight);

    // Kamerabewegung zurueck nach Theatre.js melden, damit das Detailfeld die
    // wirkliche Position zeigt. Waehrend des Abspielens NICHT — dann fuehrt die
    // Sequenz die Kamera, und das Zurueckschreiben wuerde sie ausbremsen.
    controls.addEventListener('change', () => {
        if (window.isPlaying) return;
        studio.transaction(({ set }) => {
            set(cameraObj.props.position.x, camera.position.x);
            set(cameraObj.props.position.y, camera.position.y);
            set(cameraObj.props.position.z, camera.position.z);
        });
    });

    // 4. Schlüsselbild-Oberfläche
    const theatreObjects = getAllTheatreObjects();
    window.theatreObjects = theatreObjects;   // Playwright und Konsole lesen es
    const keyframeUI = new KeyframeUI(project, sheet, theatreObjects, studio);
    window.keyframeUI = keyframeUI;
    // Den Sequenz-Editor aufklappen, indem das Blatt ausgewaehlt wird.
    project.ready.then(() => studio.setSelection([sheet]));

    // 5. Bedienung
    const exporter = new VideoExporter(renderer.domElement);
    const bedienleiste = new Bedienleiste(
        { scene, lightIcons, transformControls },
        { PRESETS, applyPreset, camera, lights, controls }).verdrahten();
    window.bedienleiste = bedienleiste;
    new Studioknoepfe(skinner, studio).verdrahten();

    // Kamera-Keyframes: studio/kamerabahn.js. Vorher 94 Zeilen in drei
    // Menue-Zuhoerern — dreimal derselbe Menue-Vorspann, zweimal dieselbe
    // Suche nach dem Theatre-Zustand im localStorage.
    const kamerabahn = new Kamerabahn(sheet.sequence, cameraObj, camera,
                                      studio).verdrahten();
    window.kamerabahn = kamerabahn;
    new Zeitleistenwerkzeuge(sheet, studio, theatreObjects).verdrahten();

    // Modalfenster, Szenen- und Modell-Listen: studio/seitenlisten.js.
    Seitenlisten.modalfensterVerdrahten();
    const listen = new Seitenlisten(
        figurenlader, (kategorie, name) => animationslauf.laden(kategorie, name));
    listen.modelle();
    document.getElementById('menu-scene-load')
        ?.addEventListener('click', () => listen.szenen());
    new Szenenspeicherung(figurenlader, { camera, controls, lights }).verdrahten();

    // REIHENFOLGE: Der Abspieler steht VOR dem Animationslauf, weil dessen
    // Konstruktor ihn als Wert bekommt. Umgekehrt greift der Abspieler auf den
    // Lauf nur ueber Pfeilfunktionen zu — die werden erst beim Abspielen
    // ausgefuehrt, da ist er längst da. Andere Reihenfolge =
    // "Cannot access 'animationslauf' before initialization".
    const abspieler = new Abspieler(sheet.sequence, {
        mixer: () => animationslauf.mixer,
        aktion: () => animationslauf.aktion,
        stoppen: () => animationslauf.anhalten(),
    }).verdrahten();
    window.abspieler = abspieler;

    const animationslauf = new Animationslauf(
        { scene, sheet, studio }, skinner, auswahl, abspieler);
    window.animationslauf = animationslauf;
    // Animationsbaum aufbauen — braucht `animationslauf` von der Zeile darueber.
    listen.animationen();

    new Buehnenzugaben({ scene, camera, lights, controls, sheet }).verdrahten();
    new Videoaufnahme(exporter, { renderer, camera }).verdrahten();
    new Studiovorgaben({ camera, lights, controls },
                       { figurenlader, animationslauf }).spaeterLaden();

    // 6. Bildschleife
    const schleife = new Buehnenschleife(
        { scene, camera, renderer, controls },
        { animationslauf, abspieler, auswahl }).starten();

    // 7. Schnittstelle fuer das Rendern auf dem Server (Playwright)
    window.__theatreSetTime = (zeit) => {
        abspieler.zeitSetzen(zeit);
        schleife.zeichnen();
    };
    window.__theatreGetDuration = () => abspieler.dauer || 0;
    window.__theatreReady = false;

    // Autostart ueber die Adresszeile (?autoplay=1) — erst, wenn die Buehne steht.
    if (new URLSearchParams(window.location.search).get('autoplay') === '1') {
        setTimeout(() => {
            const knopf = document.getElementById('btnPlayPause');
            if (knopf && !abspieler.laeuft) knopf.click();
            window.__theatreReady = true;
        }, AUTOSTART_MS);
    }

    new Exportreiter({ name: () => animationslauf.name,
                       dauer: () => abspieler.dauer }).verdrahten();

    // Video-Export: studio/bildexport.js (vorher 250 Zeilen hier). Er braucht
    // genau die Faehigkeiten des Abspielers — Dauer, Zeit setzen, pausieren,
    // fortsetzen — und bekommt ihn deshalb direkt.
    const bildexport = new Bildexport(
        { renderer, scene, camera, canvas },
        {
            dauer: () => abspieler.dauer || 10,
            zeitSetzen: (zeit) => abspieler.zeitSetzen(zeit),
            laeuft: () => abspieler.laeuft,
            pausieren: () => { if (abspieler.laeuft) abspieler.umschalten(); },
            fortsetzen: () => { if (!abspieler.laeuft) abspieler.umschalten(); },
        }).verdrahten();
    window.bildexport = bildexport;
});
