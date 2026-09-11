import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Startmessung } from '../gemeinsam/startmessung.js';

/**
 * Der Inhalt eines Reiters entsteht, wenn der Reiter aufgeht — nicht vorher.
 *
 * BEFUND (Edgar, 10.09.2026): „die ladezeit http://127.0.0.1:8081/humanbody/
 * scene/ ist bei mehr als 15 Sekunden, alleine mehr als 10 s bis das UI ohne
 * modell aufgebaut wird" — und dazu der Weg: „Die Leiste links kann z.B.
 * asynchron aufgebaut werden."
 *
 * WAS GEMESSEN WURDE (Vordergrund-Fenster, kalter Cache, 10.09.2026)
 * ==================================================================
 * Der Szeneaufbau rief acht Panel-Aufbauten beim Start auf, für Reiter, von
 * denen genau EINER offen ist. Ihre Kosten, jeder einzeln gemessen:
 *
 *     loadAnimationUI      1.343 ms      Reiter „Animation"
 *     loadKleiderUI        1.119 ms      Reiter „Kleider"
 *     loadGarmentUI          523 ms      Reiter „Assets"
 *     loadCharmorphAssets    364 ms      Reiter „Assets"
 *     loadHairUI             335 ms      Reiter „Assets"
 *     loadClothUI            333 ms      Reiter „Assets"
 *     loadPoseUI             269 ms      Reiter „Modell"
 *     loadMHProxyUI          195 ms      Reiter „Assets"
 *
 * Sie standen vorher alle mit „1 ms" im Bericht: `Startmessung.um` ist
 * synchron und endete beim ersten `await` — gemessen war nur der Anlauf.
 *
 * Am schwersten wiegt der Animationsbaum. Im DOM gezählt:
 *
 *     tab-animation   21.334 Elemente        tab-eigenschaften  1.434
 *     Seite gesamt    26.688 Elemente        tab-assets         1.471
 *
 * Also 80 % des gesamten Dokuments für einen Reiter, der zu ist — 7.067
 * Animationen aus einer 978-KB-Antwort, von denen man zwanzig sieht.
 * Isoliert nachgemessen: 130 ms bauen, 504 ms einhängen und Layout.
 *
 * WARUM DAS SICHER IST
 * ====================
 * Nachgesehen, nicht angenommen: Von den acht schreibt nur `loadHairUI`
 * gemeinsamen Zustand (`state.hairColorData`) — und den setzt `_haarfarben()`
 * in der Startsequenz ohnehin aus derselben Quelle. Von außen ruft die
 * Aufbauten niemand ausser ihnen selbst (`loadAnimationUI` nach dem
 * Umbenennen, `loadPoseUI` nach dem Speichern einer Pose); die
 * Sitzungswiederherstellung fasst sie nicht an.
 *
 * Der Bau hängt an `switchTab`, nicht am Klick: Das Reitergedächtnis schaltet
 * beim Start programmatisch um, und ein Reiter, der so aufgeht, muss genauso
 * gefüllt werden wie einer, den jemand anklickt.
 */
export class Reiterinhalt {

    /**
     * Welcher Reiter was braucht — Namen aus der Registrierung `fn`.
     *
     * Die Zuordnung ist im laufenden DOM gemessen (`closest('.tab-pane')`
     * auf dem Ziel-Element jedes Aufbaus), nicht aus den Namen geraten:
     * `loadMHProxyUI` etwa füllt `#mh-list` und sitzt damit in „Assets",
     * obwohl seine Geschwister `_initPropMHControls` heißen.
     */
    static AUFBAUTEN = {
        animation: ['loadAnimationUI', 'initFigurvideo'],
        assets: ['loadGarmentUI', 'loadHairUI', 'loadClothUI',
                 'loadCharmorphAssets', 'loadMHProxyUI'],
        kleider: ['loadKleiderUI'],
        modell: ['loadPoseUI'],
    };

    /** Was schon gebaut ist. Jeder Reiter wird genau einmal gefüllt. */
    static _gebaut = new Set();

    /**
     * `?alleReiter=1` baut wieder alles beim Start — der alte Zustand.
     *
     * Nur zum Messen: Ein Vorher/Nachher ist sonst nicht fair zu belegen,
     * weil zwischen zwei Ladevorgaengen der Modul-Zwischenspeicher, die
     * Serverlast und der gemerkte Reiter wechseln. Mit dem Schalter laufen
     * beide Faelle in derselben Minute auf derselben Maschine.
     */
    static alleSofort() {
        return new URLSearchParams(location.search).has('alleReiter');
    }

    /**
     * Den Inhalt eines Reiters herstellen, falls das noch nicht geschah.
     *
     * Gibt das Versprechen zurück, damit ein Aufrufer darauf warten KANN —
     * `switchTab` tut es bewusst nicht: Der Reiter soll sofort umschalten,
     * auch wenn seine Liste eine halbe Sekunde später steht.
     */
    static bauen(reiter) {
        const namen = Reiterinhalt.AUFBAUTEN[reiter];
        if (!namen || Reiterinhalt._gebaut.has(reiter)) return Promise.resolve();
        // VOR dem Bauen vermerken: Zwei Klicks kurz hintereinander wuerden
        // sonst zwei Laeufe ausloesen, und die haengen ihre Zuhoerer doppelt an.
        Reiterinhalt._gebaut.add(reiter);
        const laeufe = [];
        for (const name of namen) {
            const aufruf = fn[name];
            if (typeof aufruf !== 'function') {
                Protokoll.warnung('Reiter', 'Aufbau fehlt:', name);
                continue;
            }
            try {
                laeufe.push(Startmessung.um(`Reiter „${reiter}": ${name}`, aufruf));
            } catch (fehler) {
                // Ein Aufbau, der wirft, darf die anderen des Reiters nicht
                // mitnehmen — sonst bleibt ein halber Reiter ohne Meldung.
                Protokoll.warnung('Reiter', `${name} fehlgeschlagen:`, fehler);
            }
        }
        return Promise.allSettled(laeufe);
    }

    /**
     * Den beim Start offenen Reiter füllen.
     *
     * Ohne das bliebe genau der eine Reiter leer, den der Nutzer ansieht.
     */
    static offenen() {
        if (Reiterinhalt.alleSofort()) {
            return Promise.all(Object.keys(Reiterinhalt.AUFBAUTEN)
                .map(reiter => Reiterinhalt.bauen(reiter)));
        }
        const aktiv = document.querySelector('.panel-tab.active')?.dataset.tab;
        if (!aktiv) return Promise.resolve();
        return Reiterinhalt.bauen(aktiv);
    }

    /** Für Tests und die Konsole: den Merker zurücksetzen. */
    static vergessen() {
        Reiterinhalt._gebaut.clear();
    }
}
