import { loadBVHAnimation } from './wiedergabe.js';

/**
 * Animationsverwaltung — Umbenennen, Verschieben, Löschen und Ordner der
 * Animationsliste, über Kontextmenü, Werkzeugknöpfe oder Tastatur.
 *
 * Aus animation/baum.js herausgeloest (Umbau 16.08.2026):
 * `setupAnimManagement()` hatte 151 Zeilen, und die drei Dateivorgänge standen
 * jeweils ZWEIMAL darin — einmal für das Kontextmenü (Ziel aus
 * `_animCtxTarget`) und einmal für die Werkzeugknöpfe (Ziel aus
 * `.anim-item.active`), mit denselben Fragen und denselben Aufrufen. "Ordner
 * anlegen" stand ebenfalls zweimal. Und `if (r?.ok) loadAnimationTree()` zehnmal.
 *
 * Jetzt beschreibt `VORGAENGE`, was ein Vorgang fragt und welchen Serveraufruf
 * er macht; `ausfuehren()` ist die einzige Stelle, die ihn durchführt.
 */
export class Animationsverwaltung {

    /**
     * Die sechs Vorgänge.
     *  frage/vorgabe  — Eingabefeld; ohne `frage` wird nur bestätigt
     *  bestaetigen    — Rückfrage vor dem Ausführen
     *  aktion/feld    — Serveraufruf und Name der Eingabe darin
     *  ordner         — true: braucht nur die Kategorie, nicht den Dateinamen
     *  ohneZiel       — true: braucht kein gewähltes Element
     */
    static VORGAENGE = {
        'play': { spielen: true },
        'rename': { frage: 'Neuer Name:', vorgabe: ziel => ziel.name,
                    aktion: 'rename', feld: 'new_name' },
        'move': { frage: 'In welchen Ordner verschieben?',
                  vorgabe: ziel => ziel.category,
                  aktion: 'move', feld: 'new_category' },
        'delete': { bestaetigen: ziel => `"${ziel.name}" wirklich löschen?`,
                    aktion: 'delete' },
        'rename-folder': { frage: 'Neuer Ordnername:',
                           vorgabe: ziel => ziel.category,
                           aktion: 'rename_folder', feld: 'new_name',
                           ordner: true },
        'new-folder': { frage: 'Name des neuen Unterordners:',
                        aktion: 'create_folder', feld: 'folder_name',
                        ohneZiel: true },
        'delete-folder': { bestaetigen: ziel =>
                               `Ordner "${ziel.category}" wirklich löschen?`
                               + '\n(Nur wenn leer)',
                           aktion: 'delete_folder', ordner: true },
    };

    /** Werkzeugknöpfe: Kennung und Vorgang. */
    static KNOEPFE = [
        ['anim-new-folder', 'new-folder'],
        ['anim-rename', 'rename'],
        ['anim-move', 'move'],
        ['anim-delete', 'delete'],
    ];

    /** Tastenkürzel: Taste und der Knopf, den sie drückt. */
    static TASTEN = { F2: 'anim-rename', Delete: 'anim-delete' };

    /**
     * @param ziel        () => das Kontextmenü-Ziel
     * @param neuLaden    () => Liste neu aufbauen
     * @param serverruf   (aktion, daten) => Antwort
     */
    constructor({ ziel, neuLaden, serverruf }) {
        this.ziel = ziel;
        this.neuLaden = neuLaden;
        this.serverruf = serverruf;
    }

    aufbauen() {
        this._kontextmenues();
        this._knoepfe();
        this._tasten();
        this._hilfe();
        // Ein Klick irgendwohin schließt die Kontextmenüs.
        document.addEventListener('click', () => Animationsverwaltung.menuesZu());
        return this;
    }

    static menuesZu() {
        for (const menue of document.querySelectorAll('.hb-kontextmenue')) {
            menue.style.display = 'none';
        }
    }

    // ------------------------------------------------------------ Ausführung

    /**
     * Einen Vorgang mit einem Ziel ausführen — von wo der Aufruf kommt, ist
     * hier gleichgültig.
     */
    async ausfuehren(kennung, ziel) {
        const vorgang = Animationsverwaltung.VORGAENGE[kennung];
        if (!vorgang) return;
        if (vorgang.spielen) {
            if (ziel) loadBVHAnimation(ziel.url, ziel.name, 0);
            return;
        }
        if (!ziel && !vorgang.ohneZiel) {
            alert('Bitte zuerst eine Animation auswählen.');
            return;
        }
        const eingabe = this._eingabe(vorgang, ziel);
        if (eingabe === null) return;
        const antwort = await this.serverruf(vorgang.aktion,
                                            this._nutzlast(vorgang, ziel, eingabe));
        if (antwort?.ok) this.neuLaden();
    }

    /**
     * Was der Benutzer eingibt oder bestätigt. `null` heißt abgebrochen,
     * `undefined` heißt: dieser Vorgang braucht keine Eingabe.
     */
    _eingabe(vorgang, ziel) {
        if (vorgang.bestaetigen) {
            return confirm(vorgang.bestaetigen(ziel)) ? undefined : null;
        }
        if (!vorgang.frage) return undefined;
        const vorher = vorgang.vorgabe ? vorgang.vorgabe(ziel) : '';
        const eingabe = prompt(vorgang.frage, vorher);
        if (!eingabe || eingabe === vorher) return null;
        return eingabe;
    }

    _nutzlast(vorgang, ziel, eingabe) {
        const daten = {};
        if (ziel && !vorgang.ohneZiel) {
            daten.category = ziel.category;
            if (!vorgang.ordner) daten.name = ziel.name;
        }
        if (vorgang.feld && eingabe !== undefined) daten[vorgang.feld] = eingabe;
        return daten;
    }

    // ------------------------------------------------------------- Anbindung

    /** Datei- und Ordner-Kontextmenü; der Vorgang steht in `data-action`. */
    _kontextmenues() {
        for (const eintrag of document.querySelectorAll(
                '#anim-ctx-file .hb-menueeintrag, #anim-ctx-folder .hb-menueeintrag')) {
            eintrag.addEventListener('click', () => {
                this.ausfuehren(eintrag.dataset.action, this.ziel());
            });
        }
    }

    /** Werkzeugknöpfe wirken auf die gewählte Zeile der Liste. */
    _knoepfe() {
        for (const [id, vorgang] of Animationsverwaltung.KNOEPFE) {
            document.getElementById(id)?.addEventListener('click', () => {
                this.ausfuehren(vorgang, Animationsverwaltung.gewaehlt());
            });
        }
        document.getElementById('anim-refresh')
            ?.addEventListener('click', () => this.neuLaden());
    }

    /** Die gewählte Zeile als Ziel — dieselbe Form wie das Kontextmenü-Ziel. */
    static gewaehlt() {
        const zeile = document.querySelector('.anim-item.active');
        if (!zeile) return null;
        return { type: 'file', category: zeile.dataset.category,
                 name: zeile.dataset.name, url: zeile.dataset.url };
    }

    _tasten() {
        document.addEventListener('keydown', ereignis => {
            // In Eingabefeldern gehören F2 und Entf dem Feld.
            if (ereignis.target.tagName === 'INPUT') return;
            const knopfId = Animationsverwaltung.TASTEN[ereignis.key];
            if (!knopfId) return;
            // Entf ohne Auswahl soll nichts fragen.
            if (ereignis.key === 'Delete' && !Animationsverwaltung.gewaehlt()) return;
            ereignis.preventDefault();
            document.getElementById(knopfId)?.click();
        });
    }

    _hilfe() {
        const menue = document.getElementById('anim-help-menu');
        const fenster = document.getElementById('anim-help-modal');
        document.getElementById('anim-help-btn')?.addEventListener('click', ereignis => {
            ereignis.stopPropagation();
            if (menue) {
                menue.style.display = menue.style.display === 'block' ? 'none' : 'block';
            }
        });
        document.addEventListener('click', () => {
            if (menue) menue.style.display = 'none';
        });
        document.getElementById('anim-help-animations')?.addEventListener('click', () => {
            if (menue) menue.style.display = 'none';
            fenster?.classList.add('open');
        });
        document.getElementById('anim-help-close')
            ?.addEventListener('click', () => fenster?.classList.remove('open'));
        fenster?.addEventListener('click', ereignis => {
            if (ereignis.target === ereignis.currentTarget) {
                ereignis.currentTarget.classList.remove('open');
            }
        });
    }
}
