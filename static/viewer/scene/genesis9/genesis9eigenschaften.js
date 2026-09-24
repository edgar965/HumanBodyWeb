import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9garderobe } from './genesis9garderobe.js';
import { Eigenschaftenbereiche } from '../eigenschaftenbereiche.js';
import { Genesis9posen } from './genesis9posen.js';
import { Genesis9texturmischung } from './genesis9texturmischung.js';
import { Hoehengriff } from '../../gemeinsam/hoehengriff.js';

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
        // PARALLEL statt nacheinander (23.09.2026, Edgar: „mach das laden
        // parallel und asynchron wie auf BVH Studio"): Regler-Plan, Posenliste
        // und Garderobe sind DREI unabhaengige Serveranfragen in drei
        // getrennte Behaelter — nur `_haut`/`_regler`/Texturmischung brauchen
        // den Plan, Posen und Garderobe brauchen ihn nicht. Vorher liefen sie
        // als `await`-Kette hintereinander (Log: drei Anfragen ueber ~2 s
        // verteilt statt gleichzeitig).
        await Promise.all([
            Genesis9eigenschaften.plan().then(plan => {
                Genesis9eigenschaften._haut(inst, plan);
                Genesis9eigenschaften._regler(inst, plan);
                Genesis9eigenschaften._reglergriff();
                // Texturmischung ganz unten (21.09.2026): alle Hautsaetze mit Prozent.
                Genesis9texturmischung.fuellen(inst, plan);
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

    /**
     * Der Wert, den ein Regler zeigt: was der Nutzer gestellt hat, sonst der
     * WIRKSAME Wert aus dem Formelgraphen (`inst.morphwerte`, vom Server).
     *
     * Edgar (18.09.2026): „bei Ursula9 ist der Ursula Head gerade bei 0 %,
     * auch andere Ursula-Properties sind bei 0". Das Preset stellt nur den
     * Steuerregler `P3DUrsula_figure_ctrl_Character` auf 1; Kopf und Körper
     * (`P3DUrsula_head_bs_Head`, `_body_bs_Body`) bekommen ihre 100 % über
     * Formeln — im Regler-Wörterbuch stehen sie nicht, der Schieber zeigte 0.
     * Daz zeigt bei so einem Kanal die Summe. `gesteuert` = nicht selbst
     * gestellt, aber wirksam.
     */
    static wert(inst, regler) {
        const eigen = inst.regler?.[regler.name];
        const gestellt = eigen !== undefined && eigen !== null;
        const wirksam = inst.morphwerte?.[regler.name];
        // Ein Kanal mit Deltas zeigt seine SUMME (eigener Wert + Formeln, wie
        // Daz) — auch nach einem eigenen Zug: 50 % eigen + 100 % gesteuert
        // sind begrenzt 100 %, und das steht dann auch am Schieber.
        if (wirksam !== undefined && Math.abs(wirksam) > 1e-9) {
            return { wert: wirksam, gesteuert: !gestellt };
        }
        return { wert: gestellt ? eigen : (regler.vorgabe ?? 0), gesteuert: false };
    }

    /** Nach einem Lauf die gesteuerten Schieber auf den neuen wirksamen Wert. */
    static nachziehen(inst, plan) {
        const alle = (plan?.bereiche || []).flatMap(b => b.regler || []);
        for (const regler of alle) {
            const schieber = document.getElementById(`g9-${regler.name}`);
            if (!schieber || schieber === document.activeElement) continue;
            const { wert, gesteuert } = Genesis9eigenschaften.wert(inst, regler);
            if (Math.abs(parseFloat(schieber.value) - wert) < 1e-6) continue;
            schieber.value = wert;
            const anzeige = schieber.parentElement?.querySelector('.slider-value');
            if (anzeige) anzeige.textContent = Genesis9eigenschaften.text(wert, gesteuert);
        }
    }

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
        behaelter.appendChild(Genesis9eigenschaften._wahl('Haut',
            [{ id: '', name: 'Wie im Katalog' },
             ...(plan.haut || []).map(h => ({ id: h.id, name: `${h.name} (${h.geschlecht})` }))],
            inst.haut || '',
            wert => Genesis9lauf.planen(inst, () => inst.hautSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst))));
        behaelter.appendChild(Genesis9eigenschaften._wahl('Augen',
            (plan.augen || []).map(a => ({ id: a.id, name: a.name })),
            inst.augen || '01',
            wert => Genesis9lauf.planen(inst, () => inst.augenSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst))));
        Genesis9eigenschaften._brauen(inst, plan, behaelter);
        // Wimpern, Nagellack und Schminke (18.09.2026): je Kategorie ein Preset
        // aus den Charakterordnern und dem Daz-Makeup-System (`Genesis9/schminke.py`).
        for (const kategorie of plan.praesets || []) {
            behaelter.appendChild(Genesis9eigenschaften._wahl(kategorie.name,
                [{ id: '', name: '—' }, ...kategorie.eintraege],
                inst.praesets?.[kategorie.kategorie] || '',
                wert => Genesis9lauf.planen(inst,
                    () => inst.praesetSetzen(kategorie.kategorie, wert),
                    () => Genesis9eigenschaften._kopf(inst))));
        }
    }

    /**
     * Brauen (18.09.2026): 12 Kartenstile, 9 Faserstile (`Genesis9/brauen.py`),
     * die Farbliste hängt an der Art — beim Wechsel der Art fällt eine Farbe,
     * die es dort nicht gibt, auf die Vorgabe zurück.
     */
    static _brauen(inst, plan, behaelter) {
        const stile = plan.brauenstile || [];
        if (!stile.length) return;
        const artVon = stil => (stile.find(s => s.id === stil) || stile[0]).art;
        const farben = art => (plan.brauenfarben || {})[art] || plan.brauen || [];
        const farbwahl = () => Genesis9eigenschaften._wahl('Brauenfarbe',
            [{ id: '', name: 'Vorgabe (Brown)' }, ...farben(artVon(inst.brauenstil))],
            inst.brauen || '',
            wert => Genesis9lauf.planen(inst, () => inst.brauenSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst)));
        let farbzeile = farbwahl();
        behaelter.appendChild(Genesis9eigenschaften._wahl('Brauenstil',
            stile, inst.brauenstil || stile[0].id,
            wert => {
                const farbe = farben(artVon(wert)).some(f => f.id === inst.brauen) ? inst.brauen : '';
                inst.brauenstil = wert;
                inst.brauen = farbe;
                const neu = farbwahl();
                farbzeile.replaceWith(neu);
                farbzeile = neu;
                Genesis9lauf.planen(inst, () => inst.brauenstilSetzen(wert, farbe),
                                    () => Genesis9eigenschaften._kopf(inst));
            }));
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

    static _regler(inst, plan) {
        const behaelter = document.getElementById('prop-genesis9-regler');
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const bereiche = plan.bereiche || [];
        if (!bereiche.length) {
            behaelter.innerHTML = `<div class="gedaempft">${
                escapeHtml(plan.fehler || 'Keine Regler gefunden.')}</div>`;
            return;
        }
        for (const bereich of bereiche) {
            const kasten = document.createElement('details');
            kasten.className = 'uma-gruppe';
            kasten.open = bereich.schluessel === 'figur';
            kasten.innerHTML = `<summary>${escapeHtml(bereich.name)} `
                + `<span class="gedaempft">(${bereich.regler.length})</span></summary>`;
            for (const r of bereich.regler) {
                kasten.appendChild(Genesis9eigenschaften._zeile(inst, r));
            }
            behaelter.appendChild(kasten);
        }
    }

    /**
     * Der Griff unter der Reglerliste (Edgar, 20.09.2026: „mach unten an der
     * Stelle einen Griff, mit dem ich die Ansicht nach unten verschieben
     * kann, merke dir die Position"). Einmal verdrahtet — das Feld ist Teil
     * der Vorlage, `_regler` tauscht nur seinen Inhalt.
     */
    static _reglergriff() {
        if (Genesis9eigenschaften._griff) return;
        Genesis9eigenschaften._griff = new Hoehengriff({
            griff: document.getElementById('prop-genesis9-regler-griff'),
            bereich: document.getElementById('prop-genesis9-regler'),
            min: 120, max: 1600, vorgabe: 300,
            schluessel: 'scene_genesis9_regler_hoehe',
        }).verdrahten();
    }

    static _zeile(inst, regler) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const { wert, gesteuert } = Genesis9eigenschaften.wert(inst, regler);
        const kennung = `g9-${regler.name}`;
        const titel = gesteuert ? `${regler.name} — über Formeln gestellt` : regler.name;
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(titel)}">${
                escapeHtml(regler.anzeige)}</label>
            <input type="range" id="${kennung}" min="${regler.min}" max="${regler.max}"
                   step="0.01" value="${wert}" data-regler="${escapeHtml(regler.name)}">
            <span class="slider-value">${Genesis9eigenschaften.text(wert, gesteuert)}</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseFloat(schieber.value);
            anzeige.textContent = Genesis9eigenschaften.text(neu);
            Genesis9lauf.planen(inst, () => inst.reglerSetzen(regler.name, neu),
                                () => { Genesis9eigenschaften._kopf(inst);
                                        Genesis9eigenschaften.nachziehen(inst, Genesis9eigenschaften._plan); });
        });
        return zeile;
    }

    /** Daz zeigt die Kanäle als Prozent — hier auch; gesteuerte mit Stern. */
    static text(wert, gesteuert = false) {
        return `${Math.round(wert * 100)} %${gesteuert ? ' *' : ''}`;
    }
}
