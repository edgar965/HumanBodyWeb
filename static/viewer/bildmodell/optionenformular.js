/**
 * Optionenformular — die Wahl je Schritt, aus dem Katalog gebaut.
 *
 * Edgar (19.09.2026): „auf der Seite soll man die verschiedenen Optionen /
 * Alternativen für einzelne Schritte einstellen können." Der Katalog
 * (`Bildmodelloptionen.katalog()`) nennt je Schritt seine Felder mit
 * Alternativen und Verfügbarkeit; hier wird je Feld eine Auswahl gebaut,
 * nicht verfügbare Einträge ausgegraut mit Grund im Titel, dazu das
 * Zahlenfeld „Größe cm". `werte()` liefert das Wörterbuch für den Start.
 *
 * Die Blöcke „Kopf" (`kopfBlock`) und „Textur" (`texturBlock`) werden NICHT unter `#optionen`
 * gehängt, sondern nur gebaut und gehalten — `Kopfpipelineansicht` (22.09.2026, Edgar: „ich
 * brauche Auswahlboxen für Fotos, daneben Auswahl für die Pipeline, daneben das Ergebnis in
 * 3D"; 23.09.2026: „die Texturberechnung in dem gleiche Workflow, unter den Combo boxen für
 * Flame usw" — die Kette „Kopf berechnen" läuft ja bis „textur" durch) hängt beide direkt an
 * die Kopf-Fotos. `stellen()`/`werte()` finden sie trotzdem — egal wo sie im Dokument hängen.
 */
export class Optionenformular {

    constructor(katalog, optionen) {
        this.katalog = katalog;
        this.optionen = optionen || {};
        this.feld = document.getElementById('optionen');
        this.kopfBlock = null;
        this.texturBlock = null;
        this.bauen();
    }

    bauen() {
        if (!this.feld) return;
        this.feld.innerHTML = '';
        this.kopfBlock = null;
        this.texturBlock = null;
        for (const schritt of this.katalog.schritte) {
            if (!schritt.felder.length) continue;
            const block = document.createElement('fieldset');
            block.className = 'bildmodell-schrittoptionen';
            block.dataset.schritt = schritt.schluessel;
            const titel = document.createElement('legend');
            titel.textContent = schritt.name;
            block.appendChild(titel);
            for (const f of schritt.felder) block.appendChild(this.zeile(f));
            if (schritt.schluessel === 'ziel') block.appendChild(this.groesse());
            if (schritt.schluessel === 'kopf') { this.kopfBlock = block; continue; }
            if (schritt.schluessel === 'textur') { this.texturBlock = block; continue; }
            this.feld.appendChild(block);
        }
        this.stellen(this.optionen);
    }

    zeile(f) {
        const zeile = document.createElement('label');
        zeile.className = 'bildmodell-option';
        const name = document.createElement('span');
        name.textContent = f.anzeige;
        const wahl = document.createElement('select');
        wahl.name = f.feld;
        for (const a of f.alternativen) {
            const o = document.createElement('option');
            o.value = a.wert;
            o.textContent = a.anzeige + (a.verfuegbar ? '' : ' — nicht bereit');
            o.title = a.verfuegbar ? a.erklaerung : `${a.erklaerung}${a.erklaerung ? ' — ' : ''}${a.grund}`;
            o.disabled = !a.verfuegbar;
            wahl.appendChild(o);
        }
        wahl.value = f.vorgabe;
        const erklaerung = document.createElement('small');
        erklaerung.className = 'hb-hinweis';
        const nachziehen = () => {
            const a = f.alternativen.find(x => x.wert === wahl.value);
            erklaerung.textContent = a ? (a.verfuegbar ? a.erklaerung : `${a.grund}`) : '';
        };
        wahl.addEventListener('change', nachziehen);
        nachziehen();
        zeile.append(name, wahl, erklaerung);
        return zeile;
    }

    groesse() {
        const zeile = document.createElement('label');
        zeile.className = 'bildmodell-option';
        const name = document.createElement('span');
        name.textContent = 'Größe cm';
        const eingabe = document.createElement('input');
        eingabe.type = 'number'; eingabe.name = 'groesse_cm'; eingabe.min = '100'; eingabe.max = '250';
        eingabe.step = '0.5'; eingabe.placeholder = 'nur bei „Angabe in cm"';
        const erklaerung = document.createElement('small');
        erklaerung.className = 'hb-hinweis';
        erklaerung.textContent = 'Aus Bildern ist keine absolute Größe ablesbar';
        zeile.append(name, eingabe, erklaerung);
        return zeile;
    }

    stellen(optionen) {
        if (!this.feld) return;
        for (const [feld, wert] of Object.entries(optionen || {})) {
            const e = this.feld.querySelector(`[name="${feld}"]`) || this.kopfBlock?.querySelector(`[name="${feld}"]`)
                || this.texturBlock?.querySelector(`[name="${feld}"]`);
            if (!e || wert === null || wert === undefined) continue;
            const alt = e.value;
            e.value = String(wert);
            if (e.tagName === 'SELECT' && e.value !== String(wert)) e.value = alt;
            e.dispatchEvent(new Event('change'));
        }
    }

    werte() {
        const aus = {};
        if (!this.feld) return aus;
        const felder = [...this.feld.querySelectorAll('select[name], input[name]')];
        if (this.kopfBlock) felder.push(...this.kopfBlock.querySelectorAll('select[name], input[name]'));
        if (this.texturBlock) felder.push(...this.texturBlock.querySelectorAll('select[name], input[name]'));
        for (const e of felder) {
            aus[e.name] = e.type === 'number' ? (e.value === '' ? null : Number(e.value)) : e.value;
        }
        return aus;
    }
}
