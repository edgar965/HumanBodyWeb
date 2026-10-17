/**
 * Mesh3dmodell — die Karte „Genesis-Modell“ (Schritt „Modell“) der Jobseite „Mesh-3D“ (11.10.2026): Name des gespeicherten Modells, wo man es findet, und der Knopf „Als Modell speichern“.
 *
 * Seit 15.10.2026 speichert ein Mesh-3D-Auftrag sein Modell NICHT mehr selbst (Edgar: „nur wenn ich das im jeweiligen Jobfenster anklicke“): der Knopf schickt `POST /api/mesh3d/<kennung>/modell/`
 * (`Mesh3dmodellspeichern`); solange nichts zu speichern ist (Lauf rechnet, keine Figur), nennt der Server den Grund, und er steht neben dem Knopf. Ein gespeichertes Modell lässt sich erneut speichern
 * (derselbe Name). Das Modell (`data/models/<Name>.json`) steht in der Szene unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dmodell {

    constructor(seite) {
        this.seite = seite;
        this.zahlen = document.getElementById('modell-zahlen');
        this._stand = '';
        this._meldung = null;
        this._sendet = false;
    }

    zeigen(z) {
        if (!Mesh3danzeige.geaendert(this, '_stand', [z.modell, z.status, this._meldung, this._sendet])) return;
        const m = z.modell;
        if (m?.name) {
            Mesh3danzeige.zeilen(this.zahlen, [
                `Gespeichert als „${m.name}“ — in der Szene: Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle.`,
                m.daz ? `Daz-Fassung: ${typeof m.daz === 'object' ? JSON.stringify(m.daz) : m.daz}` : null,
            ]);
        } else {
            Mesh3danzeige.leer(this.zahlen, z.status === 'fertig' || m?.bereit
                ? 'Nicht gespeichert — ein Modell entsteht erst mit „Als Modell speichern“.'
                : 'Noch keine Figur — nach dem Lauf lässt sie sich hier als Modell speichern.');
        }
        const zeile = document.createElement('div');
        zeile.className = 'mesh3d-modellzeile';
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn btn-primary btn-sm';
        knopf.id = 'modell-speichern';
        knopf.disabled = this._sendet;
        knopf.innerHTML = '<i class="fas fa-save"></i> ';
        knopf.append(this._sendet ? 'Speichert …' : m?.name ? 'Erneut speichern' : 'Als Modell speichern');
        knopf.title = 'Die Figur dieses Auftrags als Genesis-Modell in „Gespeicherte Modelle“ ablegen (eine fremde Figur gleichen Namens wird nie überschrieben).';
        knopf.addEventListener('click', () => this._speichern(z));
        zeile.appendChild(knopf);
        if (this._meldung) {
            const text = document.createElement('span');
            text.className = `hb-hinweis${this._meldung.fehler ? ' fehlertext' : ''}`;
            text.textContent = this._meldung.text;
            zeile.appendChild(text);
        }
        const verweis = document.createElement('a');
        verweis.href = '/Charakter/';
        verweis.target = '_blank';
        verweis.className = 'hb-hinweis';
        verweis.textContent = 'Charakter-Editor öffnen';
        zeile.appendChild(verweis);
        this.zahlen.appendChild(zeile);
    }

    async _speichern(z) {
        this._sendet = true;
        this._meldung = null;
        this.zeigen(z);
        try {
            const antwort = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/modell/`, {});
            this._meldung = { text: `Gespeichert als „${antwort.name}“.` };
        } catch (fehler) {
            this._meldung = { text: `Nicht gespeichert: ${fehler.daten?.error || fehler.message || fehler}`, fehler: true };
        }
        this._sendet = false;
        this.zeigen(z);
        this.seite.aktualisieren();
    }
}
