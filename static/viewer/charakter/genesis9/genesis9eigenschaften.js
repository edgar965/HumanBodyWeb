import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9garderobe } from './genesis9garderobe.js';
import { Eigenschaftenbereiche } from '../eigenschaftenbereiche.js';
import { Genesis9posen } from './genesis9posen.js';
import { Genesis9ersatz } from '../../gemeinsam/genesis9ersatz.js';
import { Genesis9materialdialog } from './genesis9materialdialog.js';
import { Genesis9texturmischung } from './genesis9texturmischung.js';
import { Genesis9hautebenenregler } from './genesis9hautebenenregler.js';
import { Genesis9eigenehaut } from '../../gemeinsam/genesis9eigenehaut.js';
import { Hoehengriff } from '../../gemeinsam/hoehengriff.js';
import { Kopfeigenlink } from './kopfeigenlink.js';
import { Genesis9koerpermorphformular } from './genesis9koerpermorphformular.js';
import { Genesis9reglerliste } from './genesis9reglerliste.js';
import { Genesis9reglerzeile } from './genesis9reglerzeile.js';
import { Genesis9genitalien } from './genesis9genitalien.js';

/**
 * Genesis9eigenschaften — der Eigenschaften-Reiter einer Genesis-9-Figur.
 *
 * Was diese Figur hat (18.09.2026): Daz' eigene Formregler in vier Bereichen
 * (Figur, Körper, Kopf, Mimik — `Genesis9/reglerplan.py`) und seit dem
 * 20.09.2026 die Posensteuerungen des Körpers in sechs weiteren (Rumpf mit
 * Brüsten und Taille, Hals, Arme, Hände, Beine, Füße — 480 von 1.512
 * Kanälen; der Rest ist Verstecktes und Unwirksames), Hautsätze
 * und Augen der Starter Essentials und der Charakterordner, Brauenstil,
 * Wimpern, Nagellack und Schminke je Kategorie (`praesets`) sowie Daz-Posen
 * und -Ausdrücke (`genesis9posen.js`). Die Daz-Garderobe
 * (`genesis9garderobe.js`) füllt den Assets-Reiter.
 *
 * Der Reglerplan kommt EINMAL vom Server und wird hier gemerkt: Er hängt
 * nicht an der Figur, sondern an der Bibliothek.
 *
 * BEIM ZIEHEN WIRD GERECHNET, ABER ENTPRELLT (`genesis9lauf.js`): Ein
 * Reglerzug baut Körper, Anhänge UND Kleidung neu — 0,1 s Server plus
 * Übertragung (27.087 Punkte); während ein Lauf unterwegs ist, wird nur
 * der Wunsch gemerkt, sonst überholten sich die Antworten.
 */
export class Genesis9eigenschaften {

    static BEREICH = 'prop-genesis9-section';
    static ADRESSE = '/api/character/genesis9-figur/regler/';
    static _plan = null;
    static _griff = null;

    static async fuellen(inst) {
        const bereich = document.getElementById(Genesis9eigenschaften.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        Genesis9eigenschaften._kopf(inst);
        // PARALLEL statt nacheinander (23.09.2026, Edgar: „mach das laden parallel und asynchron wie auf BVH Studio"):
        // Regler-Plan, Posenliste und Garderobe sind DREI unabhaengige Anfragen in getrennte Behaelter — nur `_haut`/`_regler`/
        // Texturmischung brauchen den Plan. Vorher eine `await`-Kette (Log: drei Anfragen ueber ~2 s verteilt).
        await Promise.all([
            Genesis9eigenschaften.plan().then(plan => {
                Genesis9eigenschaften._haut(inst, plan);
                Genesis9eigenschaften._regler(inst, plan);
                Genesis9eigenschaften._reglergriff();
                // Texturmischung ganz unten (21.09.2026): alle Hautsaetze mit Prozent.
                Genesis9texturmischung.fuellen(inst, plan);
                // Hautebenen (17.10.2026): Hautton, Flecken, Muskel-/Fettzeichnung, graue Haare — Uniform-Regler ohne Serverlauf.
                Genesis9hautebenenregler.fuellen(inst);
            }),
            Genesis9posen.fuellen(inst),
            // Die Garderobe steht im Assets-Reiter (`_genesis9_garderobe.html`,
            // Edgar 17.09.2026: „machst Du einen extra Reiter dafür bei Assets?").
            Genesis9garderobe.fuellen(inst,
                document.getElementById(Genesis9garderobe.BEREICH)),
        ]);
    }

    /** Für eine HumanBody-Figur nur die Daz-Garderobe: Bereich einblenden und füllen
     *  (`Dazkleidung`, 19.09.2026 — Edgar: „Genesis Kleider auf HumanBody?"). */
    static garderobeFuerHumanbody(inst) {
        Eigenschaftenbereiche.dazGarderobeDazu(true);
        return Genesis9garderobe.fuellen(inst, document.getElementById(Genesis9garderobe.BEREICH));
    }

    /** HEISST `leeren`, WEIL `properties.js` SO RUFT (siehe `umapythoneigenschaften.js`). */
    static leeren() {
        document.getElementById(Genesis9eigenschaften.BEREICH)
            ?.classList.add('hb-versteckt');
    }

    static async plan() {
        if (!Genesis9eigenschaften._plan) {
            Genesis9eigenschaften._plan = await Serverabruf.json(
                Genesis9eigenschaften.ADRESSE);
        }
        return Genesis9eigenschaften._plan;
    }

    // ------------------------------------------------------------- Anzeige
    // Wert, Bereich und Text eines Reglers stehen seit 18.10.2026 in `genesis9reglerzeile.js` (Aliasse und Paare der Gliederung).

    static _kopf(inst) {
        const feld = document.getElementById('prop-genesis9-kopf');
        if (!feld) return;
        const wirksam = Object.keys(inst.morphwerte || {}).length;
        feld.innerHTML = `<strong>${escapeHtml(inst.presetName)}</strong> · `
            + `${Number(inst.punktzahl || 0).toLocaleString()} Punkte · `
            + `SubD ${inst.stufen || 0} (${Number(inst.browserpunkte || 0).toLocaleString()}) · `
            + `${((inst.hoehe || 0) * 100).toFixed(1)} cm · ${wirksam} Morphs wirksam`;
    }

    // ---------------------------------------------------------------- Haut

    static _haut(inst, plan) {
        const behaelter = document.getElementById('prop-genesis9-haut');
        if (!behaelter) return;
        behaelter.innerHTML = '';
        // Neben jeder Auswahl mit Material ein Zahnrad: Glanz, Rauheit … im Popup (`Genesis9materialdialog`, 09.10.2026);
        // sein Block „Form" zeigt die Formregler des Teils (`Genesis9teilregler`) als Zeilen wie die Reglerliste (Kennung `g9d-`).
        // `hautNeu`: nach „Als eigene Haut speichern" steht die neue Haut in `plan.haut` — die Auswahl neu bauen (18.10.2026).
        Genesis9materialdialog.form = { inst, plan, zeile: r => Genesis9eigenschaften._zeile(inst, r, 'g9d-'), hautNeu: () => Genesis9eigenschaften._haut(inst, plan) };
        // Eigene Häute (`eigen:…`, `Genesis9eigenehaut`) legen beim Wählen ihre Regler auf; danach Schieber und offenes Popup nachziehen. Ohne Geschlecht keine leeren Klammern.
        behaelter.appendChild(Genesis9materialdialog.knopf(inst, 'haut', Genesis9eigenschaften._wahl('Haut',
            [{ id: '', name: 'Wie im Katalog' },
             ...(plan.haut || []).map(h => ({ id: h.id, name: h.geschlecht && h.geschlecht !== 'eigen' ? `${h.name} (${h.geschlecht})` : h.name }))],
            inst.haut || '',
            wert => Genesis9lauf.planen(inst, () => Genesis9eigenehaut.waehlen(inst, plan, wert),
                                        () => Genesis9eigenschaften._nachHaut(inst, plan), 'haut'))));
        behaelter.appendChild(Genesis9materialdialog.knopf(inst, 'augen', Genesis9eigenschaften._augenWahl(inst, plan)));
        Genesis9eigenschaften._brauen(inst, plan, behaelter);
        // Wimpern, Nagellack und Schminke (18.09.2026): je Kategorie ein Preset aus den Charakterordnern und dem Daz-Makeup-System.
        for (const kategorie of plan.praesets || []) {
            behaelter.appendChild(Genesis9materialdialog.fuerKategorie(inst, kategorie.kategorie, Genesis9eigenschaften._wahl(kategorie.name,
                [{ id: '', name: '—' }, ...kategorie.eintraege],
                inst.praesets?.[kategorie.kategorie] || '',
                wert => Genesis9lauf.planen(inst,
                    () => inst.praesetSetzen(kategorie.kategorie, wert),
                    () => Genesis9eigenschaften._kopf(inst), `praeset:${kategorie.kategorie}`))));
        }
    }

    /** Nach einem Hautwechsel: Kopfzeile, Schieber der Hautebenen, Texturmischung und ein offenes Popup auf den Stand der Figur — eine eigene Haut bringt ihre Werte mit. */
    static _nachHaut(inst, plan) {
        Genesis9eigenschaften._kopf(inst);
        Genesis9hautebenenregler.nachziehen(inst);
        Genesis9texturmischung.fuellen(inst, plan);
        Genesis9materialdialog.aktualisieren(inst);
    }

    /** Sentinel für „Original Augen vom Modell" — nie an den Server gesendet (`Genesis9Modell.augenOriginalSetzen`). */
    static AUGEN_ORIGINAL = '__original__';

    /** Der Brauenstil, den der Server bei leerem Wert zeichnet — gleich `G9brauen.VORGABE` (`Genesis9/brauen.py`; ein Test hält beide gegeneinander). */
    static BRAUENVORGABE = 'card06';

    /**
     * Das Augen-Dropdown. Trägt das Modell eigene Augen (Fotokachel `inst.fototextur.augen` aus Mesh-to-3D / Blender-Import
     * oder ein Ersatz-Stück, `Genesis9ersatz.hatAugen`), steht „Original Augen vom Modell" als ERSTER Eintrag da (Edgar,
     * 08.10.2026) — vorausgewählt, solange der Nutzer kein Preset gewählt hat (`!inst._augenGewaehlt`). Jedes Preset gilt
     * bei jedem Modell vor den eigenen Augen (09.10.2026: „alle Modelle sollen alle Augen kriegen können").
     */
    static _augenWahl(inst, plan) {
        const eintraege = (plan.augen || []).map(a => ({ id: a.id, name: a.name }));
        const hatKachel = !!inst.fototextur?.augen || Genesis9ersatz.hatAugen(inst);
        if (hatKachel) eintraege.unshift({ id: Genesis9eigenschaften.AUGEN_ORIGINAL, name: 'Original Augen vom Modell' });
        const gewaehlt = hatKachel && !inst._augenGewaehlt ? Genesis9eigenschaften.AUGEN_ORIGINAL : (inst.augen || '01');
        return Genesis9eigenschaften._wahl('Augen', eintraege, gewaehlt,
            wert => Genesis9lauf.planen(inst,
                () => wert === Genesis9eigenschaften.AUGEN_ORIGINAL ? inst.augenOriginalSetzen() : inst.augenSetzen(wert),
                () => Genesis9eigenschaften._kopf(inst), 'augen'));
    }

    /**
     * Brauen (18.09.2026): 12 Kartenstile, 9 Faserstile (`Genesis9/brauen.py`),
     * die Farbliste hängt an der Art — beim Wechsel der Art fällt eine Farbe,
     * die es dort nicht gibt, auf die Vorgabe zurück.
     */
    static _brauen(inst, plan, behaelter) {
        const stile = plan.brauenstile || [];
        if (!stile.length) return;
        // Leerer Zustand = der Server zeichnet Karte 06 (`G9brauen.VORGABE`). Die Auswahl zeigt GENAU das und nicht den ersten Eintrag der Liste
        // (Edgar, 10.10.2026, Asian: „ändern funktioniert nicht" — angezeigt „MB Olesia Brows Apply", gezeichnet Karte 06; wer den angezeigten
        // Eintrag wählt, löst kein `change` aus). Gilt auch für die Art, nach der die Farbliste gebaut wird.
        const vorgabe = stile.some(s => s.id === Genesis9eigenschaften.BRAUENVORGABE) ? Genesis9eigenschaften.BRAUENVORGABE : stile[0].id;
        const stilJetzt = () => inst.brauenstil || vorgabe;
        const artVon = stil => (stile.find(s => s.id === stil) || stile[0]).art;
        const farben = art => (plan.brauenfarben || {})[art] || plan.brauen || [];
        const farbwahl = () => Genesis9eigenschaften._wahl('Brauenfarbe',
            [{ id: '', name: 'Vorgabe (Brown)' }, ...farben(artVon(stilJetzt()))],
            inst.brauen || '',
            wert => Genesis9lauf.planen(inst, () => inst.brauenSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst), 'brauen'));
        let farbzeile = farbwahl();
        behaelter.appendChild(Genesis9materialdialog.knopf(inst, 'brauen', Genesis9eigenschaften._wahl('Brauenstil',
            stile, stilJetzt(),
            wert => {
                const farbe = farben(artVon(wert)).some(f => f.id === inst.brauen) ? inst.brauen : '';
                inst.brauenstil = wert;
                inst.brauen = farbe;
                const neu = farbwahl();
                farbzeile.replaceWith(neu);
                farbzeile = neu;
                Genesis9lauf.planen(inst, () => inst.brauenstilSetzen(wert, farbe),
                                    () => Genesis9eigenschaften._kopf(inst), 'brauenstil');
            })));
        behaelter.appendChild(farbzeile);
    }

    static _wahl(titel, eintraege, wert, beimAendern) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label>${escapeHtml(titel)}</label>`;
        const feld = document.createElement('select');
        feld.className = 'hb-dehnt';
        for (const e of eintraege) {
            const option = document.createElement('option');
            option.value = e.id;
            option.textContent = e.name;
            option.selected = e.id === wert;
            feld.appendChild(option);
        }
        feld.addEventListener('change', () => { beimAendern(feld.value); markDirty(); });
        zeile.appendChild(feld);
        return zeile;
    }

    // -------------------------------------------------------------- Regler

    /** Die Reglerliste nach Körperteil mit Suche (`genesis9reglerliste.js`, 18.10.2026). Alle Bereiche zu — welcher aufgeht, entscheidet `Modellklappung`. */
    static _regler(inst, plan) {
        const behaelter = document.getElementById('prop-genesis9-regler');
        if (!behaelter) return;
        const [liste, genitalien] = Genesis9genitalien.teilen(plan);     // „Genitalien": eigener Bereich unter Genesis, nicht in der Liste (18.10.2026)
        Genesis9genitalien.fuellen(document.getElementById('prop-genesis9-genitalien'), genitalien, inst, r => Genesis9eigenschaften._zeile(inst, r));
        Genesis9reglerliste.fuellen(behaelter, document.getElementById('prop-genesis9-reglerkopf'), liste,
            r => Genesis9eigenschaften._zeile(inst, r),
            (kasten, bereich) => {
                Kopfeigenlink.anhaengen(kasten, bereich, inst);   // „Kopf-Eigen": Link zur Seite „Gesichtsform"
                Genesis9koerpermorphformular.anhaengen(kasten, bereich, inst, r => Genesis9eigenschaften._zeile(inst, r));   // „Nachformung (Ort)": freies Morph-Formular
            });
    }

    /** Der Griff unter der Reglerliste (Edgar, 20.09.2026: „mach unten an der Stelle einen Griff …, merke dir die Position"). Einmal verdrahtet. */
    static _reglergriff() {
        if (Genesis9eigenschaften._griff) return;
        Genesis9eigenschaften._griff = new Hoehengriff({
            griff: document.getElementById('prop-genesis9-regler-griff'),
            bereich: document.getElementById('prop-genesis9-regler'),
            min: 120, max: 1600, vorgabe: 300,
            schluessel: 'scene_genesis9_regler_hoehe',
        }).verdrahten();
    }

    /** Eine Reglerzeile (`genesis9reglerzeile.js`); nach jedem Lauf Kopfzeile und gesteuerte Schieber nachziehen. */
    static _zeile(inst, regler, praefix = 'g9-') {
        return Genesis9reglerzeile.bauen(inst, regler, () => {
            Genesis9eigenschaften._kopf(inst);
            Genesis9reglerzeile.nachziehen(inst, Genesis9eigenschaften._plan);
        }, praefix);
    }
}
