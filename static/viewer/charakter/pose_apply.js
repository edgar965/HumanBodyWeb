/**
 * Scene Editor -- Reiter „Posen": Ordnerbaum aller Modelle, Anwenden, Tastatur.
 *
 * UMBAU 18.08.2026: 236 Zeilen. Die Rechnung (Ruhelage, Deltas, Gliedmaßen,
 * T-Pose-Beine) steht jetzt in `posenanwendung.Posenanwendung`; hier bleibt die
 * Liste mit Auswahl, Kontextmenü und Tastaturkürzeln.
 *
 * UMBAU 17.10.2026 (Edgar: „mache alle vorhandenen Poses aus allen Modellen in
 * Ordner bei Poses (auch valkyrie, HumanBody usw)"): Die flache Liste der
 * HumanBody-Kategorien ist ein Baum über alle Bestände — HumanBody und die
 * Daz-Posen von Genesis 9 (`/api/character/posenbaum/`). Gezeichnet wird in
 * `Posenbaumansicht`, das Menü ist `Kontextmenue` (`Posenbaummenue`; das feste
 * `#pose-ctx-menu` der Vorlage ist weg), angewendet wird je Bestand (`Posenwahl`).
 */
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenanwendung } from './posenanwendung.js';
import { Posenspeichern } from './posenspeichern.js';
import { Posenbaumansicht } from './posenbaumansicht.js';
import { Posenbaummenue } from './posenbaummenue.js';
import { Posenwahl } from './posenwahl.js';

/** Ausgewählte Zeile und ihre Pose samt Bestand (`{pose, bestand}`). */
let _zeile = null;
let _auswahl = null;
let _ansicht = null;
let _menue = null;

function _auswaehlen(zeile, pose, bestand) {
    _zeile?.classList.remove('pose-gewaehlt');
    _zeile = zeile;
    _auswahl = { pose, bestand };
    zeile.classList.add('pose-gewaehlt');
}

/**
 * Die Statuszeile unter der Liste.
 *
 * WARUM (Edgar, 09.09.2026: „wenn ich da auf eine Pose klicke, wird die nicht
 * angewandt"): Ein Klick, der nichts bewirkt, muss SAGEN warum. Die
 * Rechenklasse liefert dazu `{ok, grund}`; hier steht der Text.
 */
function _status(text, ok = true) {
    const zeile = document.getElementById('pose-status');
    if (!zeile) {
        (ok ? Protokoll.info : Protokoll.fehler)('pose_apply', text || '');
        return;
    }
    zeile.textContent = text || '';
    zeile.classList.toggle('fehlertext', !ok);
}

/** Eine Pose anwenden und das Ergebnis melden. */
async function _anwenden(pose, bestand) {
    if (!pose) return;
    const befund = await Posenwahl.anwenden(pose, bestand);
    _status(befund.ok ? befund.text : befund.grund, befund.ok);
}

/* ── Baum, Menü und Tastatur: je einmal einrichten ── */

function _einrichten(liste) {
    if (_ansicht) return;
    _ansicht = new Posenbaumansicht(liste, {
        // Ein Klick wählt UND wendet an (seit 09.09.2026 — wie die Animationsbäume).
        klick: (pose, bestand, zeile) => { _auswaehlen(zeile, pose, bestand); _anwenden(pose, bestand); },
        menuePose: (ereignis, pose, bestand, zeile) => {
            _auswaehlen(zeile, pose, bestand);
            _menue.pose(ereignis, pose, bestand);
        },
        menueOrdner: (ereignis, knoten, bestand) => _menue.ordner(ereignis, knoten, bestand),
    });
    _menue = new Posenbaummenue({
        ansicht: _ansicht,
        anwenden: _anwenden,
        neuLaden: loadPoseUI,
        meldung: _status,
        geaendert: (bestand) => { if (bestand.quelle === 'genesis9') Posenwahl.genesis9Vergessen(); },
    });
    // `tabindex`: Ohne ihn bekommt die Liste keinen Fokus und keine Tasten.
    liste.setAttribute('tabindex', '0');
    liste.addEventListener('keydown', (ereignis) => {
        if (!_auswahl) return;
        if (ereignis.key === 'F2') {
            ereignis.preventDefault();
            _menue.umbenennen(_auswahl.pose, _auswahl.bestand);
        } else if (ereignis.key === 'Delete') {
            ereignis.preventDefault();
            if (!(_auswahl.bestand.feste_posen || []).includes(_auswahl.pose.id)) {
                _menue.loeschen(_auswahl.pose, _auswahl.bestand);
            }
        }
    });
    // Einmal binden: Bis zum 17.10.2026 hängte JEDES `loadPoseUI` (auch das nach
    // Umbenennen und Speichern) einen weiteren Hörer an (im Code gelesen).
    document.getElementById('pose-reset')?.addEventListener('click', () => {
        const befund = Posenanwendung.zuruecksetzen();
        _status(befund.ok ? 'Ruhelage hergestellt.' : befund.grund, befund.ok);
    });
}

/* ── Liste ── */

/**
 * @param waehle  die Pose, die nach dem Aufbau gewählt dastehen soll: `{bestand, id}`,
 *                oder als Text eine HumanBody-Kennung (`eigene/name`, die gerade gespeicherte)
 */
export async function loadPoseUI(waehle = null) {
    const liste = document.getElementById('pose-list');
    if (!liste) return;
    if (typeof waehle === 'string') waehle = { bestand: 'humanbody', id: waehle };
    else if (!waehle?.id || !waehle?.bestand) waehle = null;   // z. B. ein Ereignis als Argument
    _einrichten(liste);
    Posenspeichern.binden({ status: _status, neuLaden: loadPoseUI });
    try {
        const daten = await Serverabruf.json('/api/character/posenbaum/');
        // Auswahl fallen lassen: Die Zeile, auf die sie zeigt, wird neu gebaut.
        _zeile = null;
        _auswahl = null;
        const zeile = _ansicht.zeichnen(daten, waehle);
        if (zeile) {
            _auswaehlen(zeile, _ansicht.angabe(zeile), _ansicht.bestand(waehle.bestand));
            zeile.scrollIntoView({ block: 'nearest' });
        }
    } catch (fehler) {
        Protokoll.fehler('Pose', 'Baum nicht ladbar', fehler);
        liste.innerHTML = '<div class="leer-hinweis">Poses nicht verfügbar</div>';
    }
}

/** Der Weg aus dem Hauptmenü (T-Pose/A-Pose) und aus dem Szenenaufbau. */
export async function applyPoseFromServer(poseId) {
    const befund = await Posenanwendung.vomServer(poseId);
    _status(befund.ok ? `Pose liegt an (${befund.gesetzt} Knochen).`
                      : befund.grund, befund.ok);
    return befund;
}

// Register
fn.loadPoseUI = loadPoseUI;
fn.applyPoseFromServer = applyPoseFromServer;
window.__applyPoseRuntime = applyPoseFromServer;
window.__characters = state.characters;
