import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Eigenkleidwerte } from '../../gemeinsam/eigenkleidwerte.js';
import { Eigenkleider } from '../../gemeinsam/eigenkleider.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Genesis9eigenkleidstoff } from './genesis9eigenkleidstoff.js';

/**
 * Genesis9eigenkleidkasten — EIN eigenes Stück (Oberteil, Hose) in Assets → Eigen (Stufe K2a, 25.10.2026, Edgar: „Die neuen Kleider-Regler sollen in den Tab Assets →
 * Eigen, darunter die Unterteilung wie bei Assets → Genesis“).
 *
 * Kopf mit Stand (angelegt/abgelegt), Knöpfe „Anlegen“ und „Ablegen“, darunter die Felder aus `Eigenkleidfelder` nach Blöcken (Säume · Kragen und Knopfleiste ·
 * Sitz · Stoff · Textur; ein Block ohne Felder entfällt). Im Block „Stoff“ stehen seit 25.10.2026 nachts dieselben Zeilen wie am Daz-Stück (`Genesis9eigenkleidstoff`).
 * Ein Zug am Schieber stellt NUR die Uniforms des Stücks (`Eigenkleider.vorschau`, kein Serveraufruf, kein Neubau); erst beim Loslassen (`change`) steht der Wert in
 * den Reglern der Figur (`Eigenkleidwerte.setzen`) und gilt als Teil der Figur (`markDirty`). Doppelklick: zurück auf die Vorgabe. Abgelegt sind die Felder gesperrt.
 */
export class Genesis9eigenkleidkasten {

    static kasten(inst, art) {
        const a = Eigenkleidwerte.ARTEN[art];
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe g9-untergruppe g9-eigenkleid-stueck g9-eigenkleid-eigen';
        kasten.dataset.eigenkleid = art;
        kasten.innerHTML = `<summary>${escapeHtml(a.titel)} <span class="gedaempft"></span></summary>`;
        const inhalt = document.createElement('div');
        inhalt.className = 'g9-eigenkleid-inhalt';
        inhalt.appendChild(Genesis9eigenkleidkasten._knoepfe(inst, art, kasten));
        for (const [block, titel] of Eigenkleidwerte.BLOECKE) {
            const felder = Eigenkleidwerte.FELDER[art].filter(feld => feld.block === block);
            if (!felder.length) continue;                     // die Hose hat keinen Kragen
            inhalt.insertAdjacentHTML('beforeend', `<div class="gedaempft g9-eigenregler-unter">${escapeHtml(titel)}</div>`);
            for (const f of felder) {
                if (Genesis9eigenkleidstoff.FELDER.has(f.feld)) continue;          // Stoffzeilen wie am Daz-Stück, unten
                const bauer = f.knopf ? '_knopf' : f.farbe ? '_farbe' : f.wahl ? '_wahl' : '_schieber';
                inhalt.appendChild(Genesis9eigenkleidkasten[bauer](inst, art, f));
            }
            if (block === 'stoff') inhalt.appendChild(Genesis9eigenkleidstoff.block(inst, art));
        }
        kasten.appendChild(inhalt);
        Genesis9eigenkleidkasten.stand(kasten, inst, art);
        // nach jeder Eingabe neu ausgrauen (die Felder rufen ihre Vorschau vorher, im Bubbling)
        for (const ereignis of ['input', 'change']) inhalt.addEventListener(ereignis, () => Genesis9eigenkleidkasten.ausgrauen(kasten, inst, art));
        return kasten;
    }

    static _knoepfe(inst, art, kasten) {
        const zeile = document.createElement('div');
        zeile.className = 'g9-eigenkleid-knoepfe';
        zeile.innerHTML = '<button type="button" class="btn-toggle primary" data-aktion="anlegen"><i class="fas fa-tshirt"></i> Anlegen</button>'
            + '<button type="button" class="btn-toggle" data-aktion="ablegen"><i class="fas fa-times"></i> Ablegen</button>'
            + '<span class="g9-eigenkleid-meldung gedaempft"></span>';
        zeile.addEventListener('click', (e) => {
            const knopf = e.target.closest('button[data-aktion]');
            if (knopf) Genesis9eigenkleidkasten.schalten(inst, art, knopf.dataset.aktion === 'anlegen', kasten);
        });
        return zeile;
    }

    /** Anlegen oder ablegen: Regler `an`, dann die Stücke der Figur nachführen; ein Fehler steht im Kasten und im Protokoll. */
    static async schalten(inst, art, an, kasten) {
        if (an) Eigenkleidwerte.anlegen(inst, art); else Eigenkleidwerte.ablegen(inst, art);
        markDirty();
        Genesis9eigenkleidkasten.stand(kasten, inst, art);
        const meldung = kasten.querySelector('.g9-eigenkleid-meldung');
        meldung.textContent = '';
        try {
            await Eigenkleider.anwenden(inst);
        } catch (fehler) {
            meldung.textContent = fehler.message;
            meldung.classList.add('fehlertext');
            Protokoll.fehler('Eigene Kleider', `${art} nicht angelegt`, fehler);
        }
    }

    /** Knopf „Drapieren“ und „Grundform“ (Rock, Kleid; `Eigenrock`): Stand und Dauer stehen daneben. */
    static _knopf(inst, art, f) {
        const zeile = document.createElement('div');
        zeile.className = 'g9-eigenkleid-knoepfe';
        zeile.dataset.eigenkleid = `${art}:${f.feld}`;
        zeile.title = f.hilfe || '';
        zeile.innerHTML = '<button type="button" class="btn-toggle primary" data-an="1"><i class="fas fa-wind"></i> Drapieren</button>'
            + '<button type="button" class="btn-toggle" data-an="0"><i class="fas fa-undo"></i> Grundform</button><span class="gedaempft"></span>';
        const meldung = zeile.querySelector('span');
        zeile.addEventListener('click', async (e) => {
            const knopf = e.target.closest('button[data-an]');
            if (!knopf) return;
            const an = knopf.dataset.an === '1';
            meldung.textContent = an ? 'fällt …' : '';
            markDirty();
            const stand = await Eigenkleider.drapieren(inst, art, an);
            meldung.textContent = stand === false ? 'erst anlegen' : stand ? `drapiert in ${stand.ms} ms (gerechnet ${stand.rechnen_ms} ms) · Saum ${stand.saum_mm} mm tiefer` : (an ? 'überholt' : 'Grundform');
        });
        return zeile;
    }

    /** Kopf, Knöpfe und Sperre der Felder nach dem Stand der Figur. */
    static stand(kasten, inst, art) {
        const an = Eigenkleidwerte.an(inst, art);
        kasten.querySelector(':scope > summary .gedaempft').textContent = an ? '(angelegt)' : '(abgelegt)';
        kasten.querySelector('[data-aktion="anlegen"]').disabled = an;
        kasten.querySelector('[data-aktion="ablegen"]').disabled = !an;
        Genesis9eigenkleidkasten.ausgrauen(kasten, inst, art);
    }

    /**
     * Felder sperren: abgelegt alle, angelegt die, die bei den jetzigen Werten nichts bewirken (`Eigenkleidwerte.aktiv`, 26.10.2026) — grau. Die Werte sind die des Stücks
     * (auch mitten im Zug, `Eigenkleider.vorschau`), ohne Stück die der Figur. Gerufen nach jeder Eingabe im Kasten.
     */
    static ausgrauen(kasten, inst, art) {
        const an = Eigenkleidwerte.an(inst, art);
        const werte = Eigenkleider.stueck(inst, art)?.werte || Eigenkleidwerte.alle(inst, art);
        for (const feld of kasten.querySelectorAll('[data-eigenkleid]:is(input, select)')) {
            const [, name] = feld.dataset.eigenkleid.split(':');
            const wirkt = Eigenkleidwerte.aktiv(art, name, werte);
            feld.disabled = !an || !wirkt;
            (feld.closest('.slider-row') || feld.parentElement)?.classList.toggle('g9-ausgegraut', an && !wirkt);
        }
    }

    static _zeile(inst, art, f, feld) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row g9-eigenkleid-zeile';
        const kennung = `g9-eigenkleid-${art}-${f.feld}`;
        zeile.innerHTML = `<label for="${kennung}" title="${escapeHtml(f.hilfe || '')}">${escapeHtml(f.titel)}</label>`;
        feld.id = kennung;
        feld.dataset.eigenkleid = `${art}:${f.feld}`;
        feld.title = `${f.hilfe || f.titel} · Doppelklick: Vorgabe`;
        zeile.appendChild(feld);
        return zeile;
    }

    static _schieber(inst, art, f) {
        const schieber = document.createElement('input');
        Object.assign(schieber, { type: 'range', min: f.min, max: f.max, step: f.schritt });
        schieber.value = Eigenkleidwerte.wert(inst, art, f.feld);
        const zeile = Genesis9eigenkleidkasten._zeile(inst, art, f, schieber);
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-value';
        anzeige.textContent = Eigenkleidwerte.anzeige(f, schieber.value);
        zeile.appendChild(anzeige);
        schieber.addEventListener('input', () => {
            anzeige.textContent = Eigenkleidwerte.anzeige(f, schieber.value);
            Eigenkleider.vorschau(inst, art, f.feld, Number(schieber.value));
        });
        schieber.addEventListener('change', () => {
            Eigenkleidwerte.setzen(inst, art, f.feld, Number(schieber.value));
            markDirty();
        });
        schieber.addEventListener('dblclick', () => {
            schieber.value = f.vorgabe;
            schieber.dispatchEvent(new Event('input'));
            Eigenkleidwerte.setzen(inst, art, f.feld, null);
            markDirty();
        });
        return zeile;
    }

    /** Eine Auswahl (Form des Ausschnitts): Wahl = Vorschau UND Wert der Figur in einem Schritt (es gibt keinen Zug). */
    static _wahl(inst, art, f) {
        const feld = document.createElement('select');
        feld.className = 'viewer-select hb-dehnt';
        f.wahl.forEach((name, i) => feld.add(new Option(name, String(i))));
        feld.value = String(Eigenkleidwerte.wert(inst, art, f.feld));
        const zeile = Genesis9eigenkleidkasten._zeile(inst, art, f, feld);
        feld.addEventListener('change', () => {
            Eigenkleider.vorschau(inst, art, f.feld, Number(feld.value));
            Eigenkleidwerte.setzen(inst, art, f.feld, Number(feld.value));
            markDirty();
        });
        return zeile;
    }

    static _farbe(inst, art, f) {
        const feld = document.createElement('input');
        feld.type = 'color';
        feld.className = 'g9-eigenkleid-farbe';
        feld.value = Eigenkleidwerte.hex(Eigenkleidwerte.wert(inst, art, f.feld));
        const zeile = Genesis9eigenkleidkasten._zeile(inst, art, f, feld);
        feld.addEventListener('input', () => Eigenkleider.vorschau(inst, art, f.feld, Eigenkleidwerte.ausHex(feld.value)));
        feld.addEventListener('change', () => {
            Eigenkleidwerte.setzen(inst, art, f.feld, Eigenkleidwerte.ausHex(feld.value));
            markDirty();
        });
        feld.addEventListener('dblclick', () => {
            feld.value = Eigenkleidwerte.hex(f.vorgabe);
            Eigenkleider.vorschau(inst, art, f.feld, f.vorgabe);
            Eigenkleidwerte.setzen(inst, art, f.feld, null);
            markDirty();
        });
        return zeile;
    }
}
