/**
 * Modellimportdialog — „Datei → Modell importieren…": ein Modell-JSON wie bisher ODER ein Modell aus Blender (.blend), OBJ oder FBX.
 *
 * Vier Reiter (Edgar, 10.10.2026: „json, blender, obj, fbx"). JSON ist ein Knopf (`importJsonModell`); die drei anderen sind
 * `Modellimportformular` — dieselbe Klasse, vom Server mit dem Katalog des Formats gefüttert — und starten denselben Import
 * (`/api/character/blendimport/starten/`, Feld `format`). Den Lauf zeigt `Blendimportfortschritt` unter den Reitern; es rechnet immer
 * nur ein Import, gleich aus welchem Reiter er kam.
 *
 * Edgar (08.10.2026): „Mach dafür den Import im UI, beim nächsten Mal soll das mit diesen Einstellungen im UI gehen." Die Einstellungen
 * (Ordner oder Datei, Name, Augen, Kachelgrößen, Grundfigur, Stücke) kommen vom Server samt den zuletzt benutzten Werten; „Importieren"
 * merkt sie dort (je Format). Ein Pfad statt Hochladen, weil die Texturen oft NEBEN der Datei liegen (bei „cute girl" nicht gepackt).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Blendimportfortschritt } from './blendimportfortschritt.js';
import { Blendimportleiste } from './blendimportleiste.js';
import { Blendimportzustand } from './blendimportzustand.js';
import { Modellimportformular } from './modellimportformular.js';
import { Modellimportstil } from './modellimportstil.js';

export class Modellimportdialog {

    static ID = 'modellimport-dialog';
    static MERKER = 'modellimport_reiter';
    /** Die Reiter in ihrer Reihenfolge; `abschnitt` ist die Überschrift über den Feldern eines Formats. */
    static REITER = [
        { id: 'json', titel: 'JSON' },
        { id: 'blend', titel: 'Blender', abschnitt: 'Blender-Modell (.blend) → Genesis-Figur mit eigenen Stücken' },
        { id: 'obj', titel: 'OBJ', abschnitt: 'OBJ-Modell (.obj) → Genesis-Figur mit eigenen Stücken' },
        { id: 'fbx', titel: 'FBX', abschnitt: 'FBX-Modell (.fbx) → Genesis-Figur mit eigenen Stücken' },
    ];

    /** Den Dialog öffnen (einmal bauen, danach wiederverwenden); die Felder des aktiven Reiters werden neu geladen. */
    static async oeffnen() {
        const dialog = Modellimportdialog.dialog();
        dialog.classList.add('visible');
        await Modellimportdialog.laden(dialog);
    }

    static dialog() {
        let dialog = document.getElementById(Modellimportdialog.ID);
        if (dialog) return dialog;
        const stil = document.createElement('style');
        stil.textContent = Modellimportstil.CSS;
        document.head.appendChild(stil);
        dialog = document.createElement('div');
        dialog.className = 'scene-modal-overlay';
        dialog.id = Modellimportdialog.ID;
        const reiter = Modellimportdialog.REITER;
        dialog.innerHTML = `<div class="scene-modal">
  <div class="scene-modal-header"><h4><i class="fas fa-file-import"></i> Modell importieren</h4>
    <button class="scene-modal-close" data-aktion="schliessen">&times;</button></div>
  <div class="scene-modal-body">
    <div class="mi-reiter" role="tablist">${reiter.map(r =>
        `<button role="tab" data-reiter="${r.id}">${r.titel}</button>`).join('')}</div>
    <div class="mi-tafel" data-tafel="json" role="tabpanel" hidden>
      <div class="mi-abschnitt">Modell-JSON</div>
      <button data-aktion="json">JSON-Datei wählen …</button>
    </div>
    ${reiter.filter(r => r.abschnitt).map(r => `<div class="mi-tafel" data-tafel="${r.id}" role="tabpanel" hidden>
      <div class="mi-abschnitt">${r.abschnitt}</div>
      <div class="mi-felder"></div>
      <div class="mi-quelle"></div>
    </div>`).join('')}
    <div class="mi-lauf" hidden></div>
  </div>
  <div class="scene-modal-footer">
    <span class="dialoghinweis mi-meldung"></span>
    <button data-aktion="schliessen">Schließen</button>
    <button class="primary" data-aktion="starten">Importieren</button>
  </div></div>`;
        document.body.appendChild(dialog);
        dialog._formulare = {};
        for (const r of reiter.filter(r => r.abschnitt)) {
            dialog._formulare[r.id] = new Modellimportformular(r.id, dialog.querySelector(`[data-tafel="${r.id}"]`));
        }
        Blendimportleiste.einrichten();            // die Leiste oben neben „HumanBody" hört auf denselben Stand wie der Dialog
        // Der Import wurde über „Abbrechen" in der Leiste gelöscht: kein Lauf mehr im Dialog, „Importieren" wieder frei.
        document.addEventListener('blendimport-geloescht', ereignis => {
            if (dialog._fortschritt?.kennung !== ereignis.detail.kennung) return;
            dialog._fortschritt.beenden();
            dialog._fortschritt = null;
            dialog.querySelector('.mi-lauf').hidden = true;
            Modellimportdialog.sperren(dialog, false);
        });
        dialog.addEventListener('click', ereignis => Modellimportdialog.klick(dialog, ereignis));
        return dialog;
    }

    static async klick(dialog, ereignis) {
        if (ereignis.target === dialog) { dialog.classList.remove('visible'); return; }
        const reiter = ereignis.target.closest('[data-reiter]')?.dataset.reiter;
        if (reiter) { await Modellimportdialog.wechseln(dialog, reiter); return; }
        const aktion = ereignis.target.closest('[data-aktion]')?.dataset.aktion;
        if (aktion === 'schliessen') dialog.classList.remove('visible');
        if (aktion === 'json') {
            dialog.classList.remove('visible');
            const { importJsonModell } = await import('./szene_dialoge.js');
            await importJsonModell();
        }
        if (aktion === 'starten') await Modellimportdialog.starten(dialog);
    }

    static meldung(dialog, text, fehler = false) {
        const feld = dialog.querySelector('.mi-meldung');
        feld.textContent = text || '';
        feld.classList.toggle('fehlertext', !!fehler);
    }

    /** Der zuletzt benutzte Reiter (nur eine Bequemlichkeit: ohne Speicher gilt der erste). */
    static gemerkt() {
        try {
            const id = localStorage.getItem(Modellimportdialog.MERKER);
            return Modellimportdialog.REITER.some(r => r.id === id) ? id : Modellimportdialog.REITER[0].id;
        } catch {
            return Modellimportdialog.REITER[0].id;
        }
    }

    static async laden(dialog) {
        Object.values(dialog._formulare).forEach(f => { f.geladen = false; });   // gemerkte Werte können sich geändert haben
        await Modellimportdialog.wechseln(dialog, dialog._aktiv || Modellimportdialog.gemerkt());
        try {
            // Rechnet schon ein Import (gestartet vor dem Neuladen der Seite oder vorher in diesem Dialog), zeigt der Dialog ihn.
            const laufend = await Blendimportzustand.laufend();
            if (laufend && dialog._fortschritt?.kennung !== laufend) await Modellimportdialog.anzeigen(dialog, laufend);
        } catch (fehler) {
            Modellimportdialog.meldung(dialog, `Lauf nicht abgefragt: ${fehler.message}`, true);
        }
    }

    /** Einen Reiter zeigen; die Felder eines Formats werden beim ersten Zeigen geladen. */
    static async wechseln(dialog, id) {
        dialog._aktiv = id;
        try { localStorage.setItem(Modellimportdialog.MERKER, id); } catch { /* ohne Speicher gilt beim nächsten Mal der erste Reiter */ }
        dialog.querySelectorAll('[data-reiter]').forEach(k => {
            const aktiv = k.dataset.reiter === id;
            k.classList.toggle('aktiv', aktiv);
            k.setAttribute('aria-selected', String(aktiv));
        });
        dialog.querySelectorAll('[data-tafel]').forEach(t => { t.hidden = t.dataset.tafel !== id; });
        dialog.querySelector('[data-aktion="starten"]').hidden = id === 'json';       // JSON hat seinen eigenen Knopf
        Modellimportdialog.meldung(dialog, '');
        const formular = dialog._formulare[id];
        if (!formular || formular.geladen) return;
        try {
            await formular.laden();
        } catch (fehler) {
            Modellimportdialog.meldung(dialog, `Einstellungen nicht geladen: ${fehler.message}`, true);
        }
    }

    /** „Importieren" sperren, solange ein Import rechnet — ein zweiter Klick startete sonst einen zweiten Import. */
    static sperren(dialog, gesperrt) {
        const knopf = dialog.querySelector('[data-aktion="starten"]');
        knopf.disabled = gesperrt;
        knopf.textContent = gesperrt ? 'Import läuft …' : 'Importieren';
        knopf.title = gesperrt ? 'Ein Import rechnet gerade — der nächste kann danach starten' : '';
    }

    /** Den Lauf dieses Imports im Dialog zeigen; „Importieren" bleibt gesperrt, bis er nicht mehr rechnet. */
    static anzeigen(dialog, kennung) {
        dialog._fortschritt?.beenden();
        Modellimportdialog.sperren(dialog, true);
        // Die Schritte nennt der Stand selbst (`schritte`, ein .blend-Import hat kein „umwandeln"); die des Formulars gelten für ältere Stände.
        const schritte = Object.values(dialog._formulare).find(f => f.schritte.length)?.schritte || [];
        dialog._fortschritt = new Blendimportfortschritt(dialog.querySelector('.mi-lauf'), kennung, schritte,
                                                         z => Modellimportdialog.sperren(dialog, Blendimportzustand.laeuft(z)));
        return dialog._fortschritt.starten();
    }

    static async starten(dialog) {
        const knopf = dialog.querySelector('[data-aktion="starten"]');
        const formular = dialog._formulare[dialog._aktiv];
        if (knopf.disabled || !formular) return;
        Modellimportdialog.sperren(dialog, true);       // sofort, vor dem ersten await: ein zweiter Klick findet ihn schon gesperrt
        try {
            if (!(await formular.pruefen())) {
                Modellimportdialog.meldung(dialog, 'Angaben prüfen — die Meldung steht über dem Knopf', true);
                Modellimportdialog.sperren(dialog, false);
                return;
            }
            const antwort = await Serverabruf.senden('/api/character/blendimport/starten/',
                                                     { werte: formular.werte(), format: formular.format });
            Modellimportdialog.meldung(dialog, `Import ${antwort.kennung} läuft — Einstellungen gemerkt.`);
            await Modellimportdialog.anzeigen(dialog, antwort.kennung);
        } catch (fehler) {
            Modellimportdialog.meldung(dialog, `Nicht gestartet: ${fehler.message}`, true);
            Modellimportdialog.sperren(dialog, false);
        }
    }
}
