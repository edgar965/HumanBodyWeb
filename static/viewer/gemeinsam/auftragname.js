/**
 * Auftragname — den Namen eines Auftrags auf seiner Seite ändern (29.09.2026).
 *
 * Edgar: „die namen sollen in allen Jobs angegeben werden können … geänderte namen dann
 * auch in der Übersicht". Der Name stand in der Überschrift und war nur beim Anlegen
 * setzbar. Jetzt ist die Überschrift selbst das Eingabefeld: klicken (oder auf den Stift),
 * schreiben, Enter — Escape nimmt zurück.
 *
 * Wie `Auftragloeschen` kennt diese Klasse keinen Bereich; alles Bereichsspezifische steht
 * als `data-`Attribut am Namensfeld:
 *   data-adresse  Endpunkt `POST /api/modell-aus-dateien/<bereich>/<id>/name/` (Pflicht)
 *
 * Die Übersicht zeigt denselben Wert aus der Datenbank — sie braucht deshalb nichts
 * nachgezogen zu bekommen, sondern nur den nächsten Aufruf (`auftragsseiten.md`).
 */
import { Aktionsprotokoll } from './aktionsprotokoll.js';
import { Serverabruf } from './serverabruf.js';

export class Auftragname {

    static FELD = 'auftrag-name';
    static DIAGNOSE_ALERT = false;         // der Alert nimmt dem Feld den Fokus (siehe `bearbeiten`); die Diagnose steht weiter im Protokoll (`name_diagnose`)

    /** Bindet das Namensfeld, falls die Seite eines hat. */
    static binden(id = Auftragname.FELD) {
        const feld = document.getElementById(id);
        if (!feld || !feld.dataset.adresse) return null;
        return new Auftragname(feld).aufbauen();
    }

    constructor(feld) {
        this.feld = feld;
        this.adresse = feld.dataset.adresse;
        this.laeuft = false;
    }

    aufbauen() {
        this.feld.classList.add('auftrag-name-editierbar');
        this.feld.title = 'Namen ändern';
        this.feld.addEventListener('click', () => this.bearbeiten());
        const stift = document.createElement('button');
        stift.type = 'button';
        stift.className = 'btn btn-secondary btn-sm auftrag-name-stift';
        stift.title = 'Namen ändern';
        stift.innerHTML = '<i class="fas fa-pen"></i>';
        stift.addEventListener('click', (ereignis) => {
            ereignis.stopPropagation();
            this.klickZeigen();
            this.diagnose('Klick auf den Stift', ereignis);
            try {
                this.bearbeiten();
            } catch (fehler) {
                this.klickZeigen(`Klick – Fehler: ${fehler && fehler.message ? fehler.message : fehler}`, true);
                Aktionsprotokoll.melden('name_fehler', `bearbeiten() warf: ${fehler && fehler.message ? fehler.message : fehler}`, 'error');
            }
        });
        // Erfassungsphase: ein Druck IM Rechteck des Stifts, der ein anderes Element trifft (verdeckt), käme sonst nie beim Stift an.
        document.addEventListener('pointerdown', (ereignis) => {
            if (this.stift && !this.stift.contains(ereignis.target) && this.imStift(ereignis)) this.diagnose('Druck im Stift-Rechteck, getroffen hat ein anderes Element', ereignis);
        }, true);
        this.feld.after(' ', stift);
        this.stift = stift;
        return this;
    }

    /**
     * „Klick“ direkt neben dem Stift (Edgar, 14.10.2026, bei „Polstertänzer Kopie“: „schreibe direkt neben dem Stift auf die Seite ‚Klick‘“): Zeigt AUF DER SEITE, dass der Klick am Stift angekommen ist —
     * kein Alert (der nimmt dem Feld den Fokus). Erscheint der Text nicht, kam der Klick nie an; erscheint er und das Feld bleibt zu, steht der Grund im Text (`bleibt`) und im Protokoll.
     */
    klickZeigen(text = 'Klick', bleibt = false) {
        if (!this.stift) return;
        if (!this.klick) {
            this.klick = document.createElement('span');
            this.klick.className = 'auftrag-name-klick';
            this.klick.style.cssText = 'margin-left:0.6rem;font-size:0.9rem;font-weight:600;color:var(--warning,#e5a50a);';
            this.stift.after(this.klick);
        }
        this.klick.textContent = text;
        clearTimeout(this.klickUhr);
        if (!bleibt) this.klickUhr = setTimeout(() => { this.klick?.remove(); this.klick = null; }, 3000);
    }

    imStift(ereignis) {
        const r = this.stift.getBoundingClientRect();
        return r.width > 0 && ereignis.clientX >= r.left && ereignis.clientX <= r.right && ereignis.clientY >= r.top && ereignis.clientY <= r.bottom;
    }

    /**
     * Diagnose (14.10.2026, Edgar: „klicke ich auf den Editor stift …, es tut sich nichts. Mach einen Alert, damit du das loggern kannst!“): Im client.log stand von einem solchen Klick NICHTS — kein `klick`,
     * kein `druck_ohne_klick`; der Stift selbst funktionierte in einem frischen Tab. Der Alert nennt, wohin gedrückt wurde, wo der Stift liegt und was an seiner Stelle oben liegt; `Aktionsprotokoll`
     * schreibt den Text ins Protokoll. Abschalten, sobald die Ursache feststeht: `DIAGNOSE_ALERT = false` (das Protokollieren bleibt).
     */
    diagnose(wo, ereignis) {
        try {
            const r = this.stift.getBoundingClientRect();
            const oben = r.width > 0 ? document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2) : null;
            const name = (el) => el ? `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : ''}` : 'nichts';
            const text = `${wo}: Druck bei ${Math.round(ereignis.clientX)},${Math.round(ereignis.clientY)} auf ${name(ereignis.target)} · Stift ${Math.round(r.left)},${Math.round(r.top)} ${Math.round(r.width)}x${Math.round(r.height)} · oben auf dem Stift liegt ${name(oben)} · scrollY ${Math.round(scrollY)} · Feld offen ${!!this.eingabe} · Speicherung läuft ${this.laeuft} · Seite ${document.visibilityState}`;
            Aktionsprotokoll.melden('name_diagnose', text);
            if (Auftragname.DIAGNOSE_ALERT) window.alert(text);
        } catch (fehler) {
            Aktionsprotokoll.melden('name_diagnose_fehler', String(fehler && fehler.message ? fehler.message : fehler), 'error');
        }
    }

    /** Überschrift gegen ein Eingabefeld tauschen. */
    bearbeiten() {
        if (this.eingabe) { this.eingabe.focus(); return; }
        this.meldung('');
        const alt = this.feld.textContent.trim();
        Aktionsprotokoll.melden('name_bearbeiten', `Feld offen, alter Name ${JSON.stringify(alt)} → ${this.adresse}`);
        const eingabe = document.createElement('input');
        eingabe.type = 'text';
        eingabe.className = 'viewer-eingabe auftrag-name-eingabe';
        eingabe.maxLength = 200;
        eingabe.value = alt;
        eingabe.addEventListener('keydown', (ereignis) => {
            if (ereignis.key === 'Enter') { ereignis.preventDefault(); this.speichern(eingabe.value, alt); }
            if (ereignis.key === 'Escape') { ereignis.preventDefault(); this.beenden(alt); }
        });
        // Blur speichert ebenfalls — ein Klick daneben soll die Eingabe nicht verwerfen. Verliert das FENSTER den Fokus (ein `alert`, anderes Fenster, anderer Tab), bleibt das Feld offen:
        // Der Alert der Diagnose nahm dem frisch geöffneten Feld sofort den Fokus, `speichern` sah „unverändert“ und schloss es wieder (Edgar 14.10.2026: „alert kommt, aber Ändern … nicht möglich“).
        eingabe.addEventListener('blur', () => { if (this.eingabe === eingabe && document.hasFocus()) this.speichern(eingabe.value, alt); });
        this.feld.style.display = 'none';
        if (this.stift) this.stift.style.display = 'none';
        this.feld.after(eingabe);
        this.eingabe = eingabe;
        eingabe.focus();
        eingabe.select();
    }

    async speichern(neu, alt) {
        const name = (neu || '').trim();
        if (this.laeuft) { Aktionsprotokoll.melden('name_ignoriert', 'eine Speicherung läuft schon'); return; }
        if (!name || name === alt) {
            Aktionsprotokoll.melden('name_verworfen', `${name ? 'Name unverändert' : 'Name leer'} (${JSON.stringify(alt)}), nichts gesendet`);
            this.beenden(alt);
            return;
        }
        this.laeuft = true;
        Aktionsprotokoll.melden('name_senden', `${JSON.stringify(alt)} → ${JSON.stringify(name)} an ${this.adresse}`);
        try {
            const antwort = await Serverabruf.senden(this.adresse, { name });
            if (antwort && antwort.error) throw new Error(antwort.error);
            Aktionsprotokoll.melden('name_gespeichert', JSON.stringify(antwort.name || name));
            this.beenden(antwort.name || name);
            document.title = document.title.replace(alt, antwort.name || name);
            // Weitere Stellen derselben Seite, die den Namen zeigen (Mesh3D-AI: Karte „Job“, 19.10.2026), tragen `data-auftragname-kopie`.
            document.querySelectorAll('[data-auftragname-kopie]').forEach((el) => { el.textContent = antwort.name || name; });
        } catch (fehler) {
            Aktionsprotokoll.melden('name_fehler', `${fehler.status || '?'} ${fehler.daten?.error || fehler.message}`, 'error');
            this.beenden(alt);
            this.meldung(`Name konnte nicht gespeichert werden: ${fehler.daten?.error || fehler.message}`);
        } finally {
            this.laeuft = false;
        }
    }

    /**
     * Den Fehler NEBEN dem Namen zeigen, bis der nächste Versuch beginnt. Bis 12.10.2026 stand hier `window.alert`: Ein Server-Neustart (Autoreload) mitten im Speichern ließ den Dialog
     * sechs Minuten offen — die ganze Seite war so lange tot (kein Klick, kein Takt, kein Protokoll: `verbindung_unterbrochen` „360 s“ im client.log war dieser Dialog, nicht der Server).
     */
    meldung(text) {
        if (!text) { this.hinweis?.remove(); this.hinweis = null; return; }
        if (!this.hinweis) {
            this.hinweis = document.createElement('span');
            this.hinweis.className = 'auftrag-name-fehler';
            this.hinweis.setAttribute('role', 'alert');
            (this.stift || this.feld).after(this.hinweis);
        }
        this.hinweis.textContent = text;
    }

    beenden(text) {
        // Zuerst vergessen, dann entfernen: `remove()` löst synchron `blur` aus, und der Hörer sähe sonst noch ein offenes Feld, speicherte erneut und rief `beenden` verschachtelt
        // (`NotFoundError: … no longer a child`, js_fehler im client.log 14.10.2026).
        const eingabe = this.eingabe;
        this.eingabe = null;
        if (eingabe) eingabe.remove();
        this.feld.textContent = text;
        this.feld.style.display = '';
        if (this.stift) this.stift.style.display = '';
    }
}
