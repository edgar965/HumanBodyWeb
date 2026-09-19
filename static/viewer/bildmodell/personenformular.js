/**
 * Personenformular — Alter, Größe, Gewicht, Tonus, Haar und „Neu berechnen".
 *
 * Edgar (19.09.2026): „mache mir ein paar Felder oben für die Eingaben
 * zusätzlicher Daten, und einen ‚Neu Berechnen'-Button." Die Werte gehen als
 * `optionen.person` mit dem Start; Größe und Gewicht formen das Zielnetz
 * (`G9koerpergewicht`: Beta 1 bis Volumen × Dichte stimmt), Haar wird ins
 * Modell und in die 3D-Ansicht übernommen. Alter und Tonus haben in den
 * Daz Starter Essentials keinen Regler — sie stehen am Modell, wirken nicht
 * auf die Form; das sagt das Formular selbst.
 *
 * „Neu berechnen" startet ab „Zielnetz": Schätzungen bleiben, nur Ziel,
 * Anpassung, Rest, Vorschau und Speichern laufen (Damira: ~40 s). Der
 * Balken unter dem Knopf zählt `zustand.lauf.prozent` — den Fortschritt ab
 * dem Startschritt (`Bildmodelllauf.relativ`), nicht den Gesamtbalken, der
 * bei einem Start ab Zielnetz schon auf 60 % stünde.
 */
import { Laufansicht } from './laufansicht.js';

export class Personenformular {

    static FELDER = ['alter', 'groesse_cm', 'gewicht_kg', 'tonus', 'haar'];

    constructor(auftrag, katalog, optionenformular, festgehalten) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.formular = optionenformular;
        this.festgehalten = festgehalten;
        this.feld = document.getElementById('personenformular');
        if (!this.feld) return;
        this._haare();
        this.fuellen((auftrag.zustand.optionen || {}).person || {});
        const tonus = this.feld.querySelector('[name=tonus]');
        tonus?.addEventListener('input', () => { this._tonusText(tonus.value); });
        this._tonusText(tonus?.value);
        document.getElementById('neu-berechnen')?.addEventListener('click', () => this.neuBerechnen());
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    _haare() {
        const wahl = this.feld.querySelector('[name=haar]');
        if (!wahl) return;
        for (const h of this.katalog.haare || []) {
            const o = document.createElement('option');
            o.value = h.id; o.textContent = h.name;
            wahl.appendChild(o);
        }
    }

    _tonusText(wert) {
        const t = document.getElementById('tonus-wert');
        if (t) t.textContent = `${Math.round(Number(wert || 0))} %`;
    }

    fuellen(person) {
        for (const name of Personenformular.FELDER) {
            const e = this.feld.querySelector(`[name=${name}]`);
            if (!e || person[name] === undefined || person[name] === null) continue;
            e.value = String(person[name]);
        }
    }

    werte() {
        const aus = {};
        for (const name of Personenformular.FELDER) {
            const e = this.feld.querySelector(`[name=${name}]`);
            if (!e) continue;
            if (e.type === 'number' || e.type === 'range') {
                if (e.value !== '') aus[name] = Number(e.value);
            } else if (e.value) aus[name] = e.value;
        }
        return aus;
    }

    zeigen(z) {
        const knopf = document.getElementById('neu-berechnen');
        const laeuft = z.status === 'laeuft';
        if (knopf) {
            knopf.disabled = laeuft;
            knopf.querySelector('span').textContent = laeuft ? 'Berechnet …' : 'Neu berechnen';
            knopf.querySelector('i')?.classList.toggle('fa-spin', laeuft);
        }
        this._lauf(z, laeuft);
        const beleg = ((z.ergebnis || {}).ziel || {}).gewicht;
        const t = document.getElementById('person-beleg');
        if (!t) return;
        if (beleg && beleg.gewicht_nachher !== undefined) {
            t.textContent = `Zielnetz: ${beleg.gewicht_vorher} kg aus den Bildern → ${beleg.gewicht_nachher} kg `
                + `(Beta 1 ${beleg.beta1_vorher} → ${beleg.beta1}, Dichte 1000 kg/m³)`;
        } else t.textContent = '';
    }

    _lauf(z, laeuft) {
        const feld = document.getElementById('person-lauf');
        if (!feld) return;
        feld.classList.toggle('hb-versteckt', !laeuft);
        if (!laeuft) return;
        const prozent = Math.max(0, Math.min(100, Number((z.lauf || {}).prozent || 0)));
        document.getElementById('person-fortschritt').style.width = `${prozent}%`;
        const schritt = this.auftrag.constructor.SCHRITTE;
        const ab = schritt.indexOf((z.lauf || {}).ab), jetzt = schritt.indexOf(z.schritt);
        const nummer = ab >= 0 && jetzt >= ab ? ` (${jetzt - ab + 1}/${schritt.length - ab})` : '';
        document.getElementById('person-lauf-text').textContent =
            `${prozent} % · ${Laufansicht.NAMEN[z.schritt] || z.schritt || ''}${nummer}`
            + `${z.progress_detail ? ' · ' + z.progress_detail : ''}`;
    }

    async neuBerechnen() {
        const proportionen = window.__bildmodell?.proportionen?.werte?.() || {};
        const optionen = { ...this.formular.werte(), person: this.werte(), proportionen };
        try {
            await this.auftrag.starten(optionen, 'ziel', this.festgehalten ? this.festgehalten() : {});
        } catch (fehler) {
            window.alert(`Neu berechnen fehlgeschlagen: ${fehler.message}`);
        }
    }
}
