import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Genesis9modellvorrat } from '../gemeinsam/genesis9modellvorrat.js';

/**
 * Exportleistemodell — „Als Modell speichern“ JEDER Exportleiste (23.11.2026, Edgar: „nutze gemeinsamen Code für alle, was soll das???“, „eine einzige Speicherart!“).
 *
 * Bis dahin band jede Seite den Knopf selbst — Mesh-Genesis-Test (`Meshgenesistestkleider`), Foto-Genesis (`Fotogenesismodellspeichern`, dazu die Karte „Genesis-Ergebnis“ mit einer eigenen
 * Adresse), 2D3D Kleider (`Meshfigurspeicher`): drei Klassen, drei Adressen, drei Prüfungen; Edgar 1 scheiterte in der Ergebniskarte an der Prüfung der Testseite. Jetzt bindet
 * `Exportleiste` diese Klasse für ihre Leiste, und es gibt EINE Adresse: `<Leiste>/modell/` (`Exportleistequelle.modell_stand` / `modell_speichern`). Was gespeichert wird, weiß der
 * Bereich auf dem Server; hier nur Name, Start, Stand (alle 2 s, solange es läuft) und die Meldung unter dem Knopf.
 *
 * Seit 23.11.2026 dazu Häkchen je Methode der Kleider (Edgar: „beim Speichern sollen zumindest Haare, Bart, Haut mitgehen, Toggles welche Kleider (Bibliothek usw)“): Der Server
 * schickt mit dem Stand ein `angebot` (`Meshgenesistestkleidmethoden.angebot`), angehakt ist zuerst die Methode, die die Seite zeigt (Ereignis `METHODE`). Haut, Haar, Bart, Schuhe,
 * Hut und Requisiten gehen immer mit; das entscheidet der Server.
 * Ist das Modell gespeichert, rechnet der Server gleich seine Anzeigen vorab (`Genesis9modellvorrat`, 24.11.2026) — die erste Ladung im Charakter kommt dann aus dem Vorrat.
 */
export class Exportleistemodell {

    static TAKT_MS = 2000;
    /** Ereignis am `document`, mit dem eine Seite sagt, welche Methode der Kleider sie zeigt (`detail` = 'bibliothek' | 'drapieren' | 'eigen' | 'passend';
     *  `Fotogenesiskleidermethode`). Die Häkchen folgen ihm, bis jemand selbst eins setzt. */
    static METHODE = 'hb:kleidermethode';

    constructor(leiste) {
        this.leiste = leiste;
        const w = leiste.wurzel;
        this.knopf = w.querySelector('#exportleiste-modell-speichern');
        this.name = w.querySelector('#exportleiste-modell-name');
        this.meldung = w.querySelector('#exportleiste-modell-meldung');
        this.methodenZeile = w.querySelector('#exportleiste-modell-methoden');
        this.haken = w.querySelector('#exportleiste-modell-haken');
        this.hinweis = this.meldung?.textContent.trim() || '';      // Text der Vorlage (`speichern_hinweis`): steht da, solange nie gespeichert wurde
        this._geholt = false;
        this._angebot = null;            // die Methoden, die es für dieses Modell gibt (`…/modell/` → `angebot`)
        this._lief = false;              // läuft seit dieser Seite ein Speichern? Dann gehört nach dem Ende das Vorab-Füllen dazu.
        this._selbst = false;            // hat jemand selbst einen Haken gesetzt? Dann folgen die Haken der Seite nicht mehr.
        this.gezeigt = 'bibliothek';
        this.knopf?.addEventListener('click', () => this.speichern());
        document.addEventListener(Exportleistemodell.METHODE, (e) => this._gezeigt(e.detail));
    }

    /** Die Seite zeigt jetzt diese Methode: als Vorgabe der Haken, solange niemand selbst einen gesetzt hat. */
    _gezeigt(methode) {
        this.gezeigt = methode || 'bibliothek';
        if (!this._selbst) this._hakenSetzen([this.gezeigt]);
    }

    /** Die Häkchen je Methode einmal bauen (Edgar, 23.11.2026: „Toggles welche Kleider (Bibliothek usw)“) — nur wo der Server ein Angebot schickt. */
    _hakenBauen(angebot) {
        if (this._angebot || !this.haken || !Array.isArray(angebot) || !angebot.length) return;
        this._angebot = angebot;
        this.haken.innerHTML = '';
        for (const m of angebot) {
            const label = document.createElement('label');
            label.className = 'exportleiste-haken-eintrag';
            label.title = m.wert === 'bibliothek' ? 'Die Kleidung, wie die Kleiderbibliothek sie zeigt' : `${m.anzahl} Kleidungsstück${m.anzahl === 1 ? '' : 'e'} mit „${m.text}“`;
            const kasten = Object.assign(document.createElement('input'), { type: 'checkbox', value: m.wert });
            kasten.addEventListener('change', () => { this._selbst = true; });
            label.append(kasten, ` ${m.text}`);
            this.haken.appendChild(label);
        }
        this.methodenZeile?.classList.remove('hb-versteckt');
        this._hakenSetzen([this.gezeigt]);
    }

    _hakenSetzen(werte) {
        const kaesten = [...(this.haken?.querySelectorAll('input[type="checkbox"]') || [])];
        if (!kaesten.length) return;
        const da = werte.filter(w => kaesten.some(k => k.value === w));
        for (const k of kaesten) k.checked = (da.length ? da : ['bibliothek']).includes(k.value);
    }

    /** Die angehakten Methoden — null, wenn es keine Häkchen gibt (dann entscheidet der Server, `Meshgenesistestkleidmethoden.VORGABE`). */
    _methoden() {
        if (!this._angebot) return null;
        return [...this.haken.querySelectorAll('input[type="checkbox"]:checked')].map(k => k.value);
    }

    /** Einmal nach dem ersten Zustand der Leiste: Stand und Vorgabe des Namens holen. */
    zeigen() {
        if (!this.knopf || this._geholt) return;
        this._geholt = true;
        this._standHolen();
    }

    async speichern() {
        const name = this.name?.value.trim() || '';
        if (!name) {
            this._melden('Bitte einen Namen für das Modell eingeben.', true);
            return;
        }
        this.knopf.disabled = true;
        this._melden(`„${name}“ wird gespeichert …`);
        let antwort;
        try {
            const methoden = this._methoden();
            antwort = await Serverabruf.senden(this.leiste.adresse('modell/'), methoden ? { name, methoden } : { name });
        } catch (fehler) {
            this._melden(`Nicht gespeichert: ${fehler.daten?.error || fehler.message}`, true);
            this.knopf.disabled = false;
            return;
        }
        this._stand(antwort?.stand || { status: 'laeuft', name });
    }

    async _standHolen() {
        clearTimeout(this._takt);
        try {
            const s = await Serverabruf.json(this.leiste.adresse('modell/'));
            if (this.name && !this.name.value) this.name.value = s.vorgabe || '';
            this._hakenBauen(s.angebot);
            this._stand(s);
        } catch (fehler) {
            this._melden(`Stand nicht lesbar: ${fehler.daten?.error || fehler.message}`, true);
            this.knopf.disabled = false;
        }
    }

    _stand(s) {
        const text = {
            nie: this.hinweis,
            laeuft: `Speichern läuft (${s.name || ''}): ${s.meldung || 'startet'}`,
            fertig: `${s.meldung || `Modell „${s.name}“ gespeichert`} — unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.`,
            fehler: `Speichern gescheitert: ${s.fehler || s.meldung || ''}`,
            kein: this.hinweis || s.meldung || '',          // Einpassung: der Hinweis der Vorlage sagt, was stattdessen geht
        }[s.status] ?? '';
        this._melden(text, s.status === 'fehler');
        if (s.status === 'laeuft') this._lief = true;
        else if (this._lief) {
            this._lief = false;
            if (s.status === 'fertig') Genesis9modellvorrat.fuellen(s.modell || s.name).catch(fehler => console.warn(`Exportleistemodell: Vorab-Anzeigen — ${fehler.message}`));
        }
        this.knopf.disabled = s.status === 'laeuft';          // nur während des Laufs (Bedienelemente nicht sperren)
        if (s.status === 'laeuft') this._takt = setTimeout(() => this._standHolen(), Exportleistemodell.TAKT_MS);
    }

    _melden(text, fehler = false) {
        if (!this.meldung) return;
        this.meldung.textContent = text;
        this.meldung.classList.toggle('hb-schlecht', fehler);
    }
}
