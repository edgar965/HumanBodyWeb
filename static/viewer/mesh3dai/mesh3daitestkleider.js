/**
 * Mesh3daitestkleider — Karte „Kleider und Bestandteile“ der Testseite (17.10.2026 nachts, Server `Mesh3daitestkleider`, `Mesh3daitestmodell`).
 * Edgar: „Nach dem Bauen müsste ich im Ergebnis View festlegen können, ob ich ein Kleidungsstück in der ersten Option oder zweiten Option haben möchte. Also Toggle für jedes Kleidungsstück
 * für beide Optionen und Button zum übernehmen von Option a oder b in das End-Modell, mit speichern des Modells“.
 * Je Stück drei Schaltknöpfe (a Katalog · b aus dem Netz · aus); „Alle: a / b“ stellt die Vorgabe und nimmt die eigenen Wahlen zurück. Die gewählten Stücke stehen im Feld „Ausgabe“ an der Figur,
 * gehäutet mit denselben Matrizen (`Mesh3daitestnetzbau`). „Übernehmen und speichern“ startet den Prozess auf dem Server und fragt alle 2 s nach seinem Stand.
 */
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daitestkleidname } from './mesh3daitestkleidname.js';
import { Mesh3daitestnetzbau } from './mesh3daitestnetzbau.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
// k/s/h (20.10.2026): Kleider aus der KI von Mesh3D-AI (Server `Mesh3daitestkikleider`); a/b kommen aus dem Mesh-3D-Lauf, nicht aus der KI
// d und n sind Vergleichslinien zum Schnitt s (20.10.2026): wählbar, nie Vorgabe, nie im Ergebnis der Jobseite
// f (21.10.2026): Schnitt aus der Fläche — Nähte vom Körper, flachgelegt, GarmentCode näht und drapiert; Vorgabe vor s
// g (21.10.2026): Schicht aus der KI — der Schichtkopf gibt die Form des Stücks je Punkt des Genesis-Käfigs aus, gegen die Zielstücke trainiert
const WEGTEXT = { a: 'Katalog', b: 'Mesh-3D-Lauf', k: 'KI geschnitten', s: 'KI Schnitt', f: 'KI Schnitt aus der Fläche', g: 'KI Schicht', h: 'Bibliothek Frisur', d: 'Vergleich Schnittdeutung', n: 'Vergleich NeuralTailor', aus: 'aus' };
const WEGE = ['g', 'k', 'f', 's', 'h', 'd', 'n', 'a', 'b'];

export class Mesh3daitestkleider {
    constructor(karte, seite) {
        this.karte = karte;
        this.seite = seite;
        this.kennung = seite.kennung;
        this.geschlecht = null;
        this.liste = null;
        this.netze = new Map();          // `${weg}/${id}` → Promise<Mesh3daiflaechennetz>
        this.objekte = new Map();        // `${weg}/${id}` → THREE.Mesh (gehäutet mit `this.matrizen`)
        this.matrizen = null;
        this.tabelle = karte.querySelector('[data-kleider="tabelle"]');
        this.info = karte.querySelector('[data-kleider="info"]');
        this.stand = karte.querySelector('[data-kleider="stand"]');
        this.name = karte.querySelector('#mesh3dai-kleider-name');
        this.knopf = karte.querySelector('#mesh3dai-kleider-speichern');
        karte.querySelectorAll('[data-kleider-alle]').forEach(k => k.addEventListener('click', () => this.alle(k.dataset.kleiderAlle)));
        this.knopf?.addEventListener('click', () => this.speichern());
    }

    _adresse(teil = '') {
        return `/api/mesh3dai/test/${encodeURIComponent(this.kennung)}/${teil}`;
    }

    /** Liste holen und zeigen; `matrizen` = Haltung der Figur (ohne: nur die Tabelle). */
    async laden(geschlecht, matrizen, standardname) {
        if (geschlecht !== this.geschlecht) {
            this.netze.clear();
            this.objekte.clear();
        }
        this.geschlecht = geschlecht;
        if (matrizen) this.matrizen = matrizen;
        if (this.name && !this.name.value) this.name.value = standardname || '';
        try {
            const antwort = await fetch(this._adresse(`kleider/${geschlecht}/`));
            const daten = await antwort.json();
            if (!antwort.ok) throw new Error(daten.error || `HTTP ${antwort.status}`);
            this._setzen(daten);
        } catch (fehler) {
            this.info.textContent = `Kleider nicht lesbar: ${fehler.message}`;
            return;
        }
        this._standHolen();
        await this._objekteBauen();
    }

    _setzen(daten) {
        this.liste = daten;
        const q = daten.quelle;
        const ki = daten.ki;
        const zahlKi = daten.stuecke.filter(st => st.quelle === 'ki').length;
        this.info.textContent = daten.stuecke.length
            ? `${daten.stuecke.length} Stücke, davon ${zahlKi} aus der KI. `
              + (ki ? `KI (Zerlegung ${ki.zerlegung?.lauf ?? '?'}${ki.schnitt_lauf ? `, Schnitt ${ki.schnitt_lauf}` : ''}): k = die KI zieht die Grenze im Netz, Geometrie und Textur aus dem Netz, auf die vorhergesagte Figur übertragen; `
                    + 's = GarmentCode-Schnitt, Katalogstück, Form und Regler vom Schnittkopf aus dem geschnittenen Stück; h = Frisur der Garderobe (Bibliothek) mit den nächsten Haarmaßen der KI, nur auf eigene Wahl. '
                  : 'Kleider aus der KI sind für diesen Test noch nicht gerechnet. ')
              + (q ? `Nicht aus der KI: b = vom Mesh-3D-Lauf „${q.name}“ geschnitten, a = Garderobe-Stück nach Messung gegen b; Haut a = Haut der Figur, b = gebackene Haut des Mesh-3D-Laufs.` : '')
            : (daten.grund || 'Keine Stücke.');
        this.karte.querySelectorAll('[data-kleider-alle]').forEach(k => {
            const an = k.dataset.kleiderAlle === daten.vorgabe;
            k.classList.toggle('active', an);
            k.setAttribute('aria-pressed', String(an));
        });
        this.tabelle.replaceChildren(...daten.stuecke.map(st => this._zeile(st)));
        if (this.knopf) this.knopf.disabled = !daten.stuecke.length;
    }

    _zelle(text, titel) {
        const td = document.createElement('td');
        td.textContent = text;
        if (titel) td.title = titel;
        return td;
    }

    /** Ein Satz je Weg: was dieser Weg für das Stück gebaut hat (oder warum nicht). */
    _beschreibung(st, w) {
        const e = st[w];
        if (!e || e.fehler) return `${w} · ${WEGTEXT[w]}: — ${e?.fehler || 'nicht gerechnet'}`;
        const haut = st.art === 'haut';
        const abstand = u => u?.art === 'starr' ? 'starr übertragen' : `Abstand zur Haut Median ${de(u?.abstand_mm_median ?? 0, 1)} mm`;
        const text = {
            a: () => haut ? e.anzeige_name : `${e.anzeige_name} (${e.kategorie}${e.ueberdeckung != null ? `, Überdeckung ${de(e.ueberdeckung, 2)}` : ''})`,
            b: () => haut ? `${e.anzeige_name}: Kacheln ${Object.keys(e.kacheln || {}).join(', ')}` : `${de(e.dreiecke)} Dreiecke (${abstand(e.uebertrag)})`,
            k: () => `${de(e.dreiecke)} Dreiecke aus dem Netz (${abstand(e.uebertrag)})`,
            s: () => `GarmentCode ${e.schnitt?.stueck} · ${e.schnitt?.form} (Sicherheit ${de(e.schnitt?.sicherheit ?? 0, 2)}), Abstand zum geschnittenen Stück ${de(e.abstand_mm?.netz_zum_schnitt ?? 0, 1)} mm`,
            h: () => `${e.anzeige_name} (Abstand der Haarmaße ${de(e.abstand ?? 0, 2)}${e.farbe ? `, Farbe ${e.farbe}` : ''})`,
            d: () => `Deutung „${e.schnitt?.deutung}“ → GarmentCode ${e.schnitt?.stueck} · ${e.schnitt?.form}, Abstand zum geschnittenen Stück ${de(e.abstand_mm?.netz_zum_schnitt ?? 0, 1)} mm`,
            n: () => `${de(e.schnitt?.teile ?? 0)} Schnittteile, ${de(e.schnitt?.naehte ?? 0)} Nähte, Abstand zum geschnittenen Stück ${de(e.abstand_mm?.netz_zum_schnitt ?? 0, 1)} mm`,
            f: () => `${de(e.schnitt?.flaeche?.teile?.length ?? 0)} Schnittteile, ${de(e.schnitt?.flaeche?.schnitt?.naehte ?? 0)} Nähte, Abstand zum geschnittenen Stück ${de(e.abstand_mm?.netz_zum_schnitt ?? 0, 1)} mm`,
            g: () => `${de(e.dreiecke ?? 0)} Dreiecke aus dem Schichtkopf (${abstand(e.uebertrag)})${e.stufe2?.lauf ? `, Stufe 2 ${e.stufe2.lauf}` : ''}`,
        }[w];
        // Ein Weg ohne eigenen Satz darf die Karte nicht abbrechen (22.10.2026: g fehlte hier, „Kleider nicht lesbar“ — die Testseite zeigte seit Weg g keine Kleider)
        return `${w} · ${haut && w === 'a' ? 'Haut der Figur' : WEGTEXT[w]}: ${text ? text() : (e.grund || 'gerechnet')}`;
    }

    _zeile(st) {
        const tr = document.createElement('tr');
        const haut = st.art === 'haut';
        const wege = WEGE.filter(w => st[w]);
        tr.append(this._zelle(st.name, haut ? 'die Haut der Figur' : `${st.art}, Region ${st.region}${st.bewegung === 'starr' ? ', starr' : ''}${st.quelle === 'ki' ? ' — aus der KI' : ' — aus dem Mesh-3D-Lauf'}`));
        // Name und Kategorie in der Garderobe (22.10.2026, `Mesh3daitestkleidname`)
        tr.append(...Mesh3daitestkleidname.zellen(st, this.liste?.kategorien, this.name?.value?.trim(), rumpf => this.stueckSpeichern(rumpf)));
        const td = document.createElement('td');
        for (const w of wege) {
            const zeile = document.createElement('div');
            zeile.textContent = this._beschreibung(st, w);
            if (w === 'a' && st.a?.kandidaten) zeile.title = `nächste: ${st.a.kandidaten.slice(1).map(k => `${k.kennung} ${de(k.ueberdeckung, 2)}`).join(' · ')}`;
            if (w === 'h' && st.h?.kandidaten) zeile.title = `nächste: ${st.h.kandidaten.slice(1).map(k => `${k.kennung} ${de(k.abstand, 2)}`).join(' · ')}`;
            td.append(zeile);
        }
        tr.append(td);
        const wahl = document.createElement('td');
        const leiste = document.createElement('div');
        leiste.className = 'schalterleiste mesh3dai-kleider-wahl';
        // Haut: kein „aus“ — eine Figur ohne Haut gibt es nicht.
        for (const w of haut ? wege : [...wege, 'aus']) {
            const k = document.createElement('button');
            k.type = 'button';
            k.className = 'schaltknopf' + (st.wahl === w ? ' active' : '');
            k.textContent = w === 'aus' ? 'aus' : `${w} · ${haut && w === 'a' ? 'Haut der Figur' : WEGTEXT[w]}`;
            k.disabled = w !== 'aus' && (!st[w] || !!st[w].fehler);
            k.setAttribute('aria-pressed', String(st.wahl === w));
            k.addEventListener('click', () => this.waehlen(st.id, w));
            leiste.append(k);
        }
        wahl.append(leiste);
        tr.append(wahl);
        return tr;
    }

    async waehlen(id, wahl) {
        await this._senden('wahl/', { stueck: id, wahl });
    }

    /** Name oder Kategorie eines Stücks speichern — nur die Tabelle neu, die Figur bleibt (`Mesh3daitestkleidname`). */
    async stueckSpeichern(rumpf) {
        try {
            this._setzen(await Serverabruf.senden(this._adresse(`kleider/${this.geschlecht}/speichern/`), rumpf));
        } catch (fehler) {
            alert(`Nicht gespeichert: ${fehler.daten?.error || fehler.message}`);
        }
    }

    async alle(weg) {
        await this._senden('wahl/', { alle: weg });
    }

    async _senden(teil, rumpf) {
        try {
            this._setzen(await Serverabruf.senden(this._adresse(`kleider/${this.geschlecht}/${teil}`), rumpf));
        } catch (fehler) {
            alert(`Wahl nicht gespeichert: ${fehler.message}`);
            return;
        }
        await this._objekteBauen();
    }

    /** Die Netze der gewählten Stücke holen (einmal je Stück und Weg) und mit den Matrizen der Figur häuten. */
    async _objekteBauen() {
        if (!this.liste || !this.matrizen) return;
        // Die Haut ist kein eigenes Objekt: sie ersetzt das Anzeigenetz der Figur (`hautNetz`, `Mesh3daitestseite.figurNeu`).
        const auftraege = this.liste.stuecke.filter(st => st.art !== 'haut' && st.wahl !== 'aus' && st[st.wahl]?.netz).map(async st => {
            const schluessel = `${st.wahl}/${st.id}`;
            if (this.objekte.has(schluessel)) return;
            if (!this.netze.has(schluessel)) this.netze.set(schluessel, Mesh3daiflaechennetz.holen(null, st[st.wahl].netz));
            try {
                const netz = await this.netze.get(schluessel);
                this.objekte.set(schluessel, Mesh3daitestnetzbau.mesh(netz, this.matrizen));
            } catch (fehler) {
                this.netze.delete(schluessel);
                console.warn('Mesh3daitestkleider: %s nicht geladen (%s)', schluessel, fehler.message);
            }
        });
        await Promise.all(auftraege);
        await this.seite.figurNeu();    // Haut a/b, und die Haut unter den gewählten Stücken fällt weg (`verdeckt`)
    }

    /** Neue Haltung (anderes Geschlecht, neue Figur): alle geladenen Stücke neu häuten. */
    neuHaeuten(matrizen) {
        this.matrizen = matrizen;
        this.objekte.clear();
        return this._objekteBauen();
    }

    /**
     * Die Dreiecke der Figur, die die gewählten Stücke verdecken (Server: `verdeckt` = Bits je Dreieck, base64, little-endian) — die Figur lässt sie weg, sonst sticht die Haut durch den Stoff.
     * @returns {Uint8Array|null}
     */
    verdeckt(anzahl) {
        if (!this.liste) return null;
        let aus = null;
        for (const st of this.liste.stuecke) {
            const bits = st.wahl !== 'aus' ? st[st.wahl]?.verdeckt : null;
            if (!bits) continue;
            aus ??= new Uint8Array(anzahl);
            const bytes = Uint8Array.from(atob(bits), c => c.charCodeAt(0));
            for (let t = 0; t < anzahl; t++) if (bytes[t >> 3] & (1 << (t & 7))) aus[t] = 1;
        }
        return aus;
    }

    /** Das Anzeigenetz der Figur mit der Haut aus dem Netz (Wahl „b“ der Zeile „Haut“: dieselben Dreiecke, die Kacheln des Mesh-3D-Laufs) — oder null (Haut der Figur). */
    async hautNetz() {
        const st = this.liste?.stuecke.find(s => s.art === 'haut');
        const adresse = st?.wahl === 'b' ? st.b?.netz : null;
        if (!adresse) return null;
        if (!this.netze.has('b/haut')) this.netze.set('b/haut', Mesh3daiflaechennetz.holen(null, adresse));
        try {
            return await this.netze.get('b/haut');
        } catch (fehler) {
            this.netze.delete('b/haut');
            console.warn('Mesh3daitestkleider: Haut aus dem Netz nicht geladen (%s)', fehler.message);
            return null;
        }
    }

    /** Die Objekte der wirksamen Wahl (für das Feld „Ausgabe“). */
    sichtbare() {
        if (!this.liste) return [];
        return this.liste.stuecke.filter(st => st.art !== 'haut' && st.wahl !== 'aus').map(st => this.objekte.get(`${st.wahl}/${st.id}`)).filter(Boolean);
    }

    async speichern() {
        const name = (this.name?.value || '').trim();
        if (!name) {
            alert('Bitte einen Namen für das Modell eingeben.');
            return;
        }
        this.knopf.disabled = true;
        try {
            await Serverabruf.senden(this._adresse(`modell/${this.geschlecht}/`), { name });
        } catch (fehler) {
            this.stand.textContent = `Nicht gestartet: ${fehler.message}`;
            this.knopf.disabled = false;
            return;
        }
        this._standHolen();
    }

    async _standHolen() {
        clearTimeout(this._takt);
        try {
            const antwort = await fetch(this._adresse(`modell/${this.geschlecht}/`));
            const s = await antwort.json();
            const text = { nie: '', laeuft: `Übernahme läuft (${s.name}): ${s.meldung || ''}`, fertig: `${s.meldung} — unter „Charakter hinzufügen → Genesis 9 → Gespeicherte Modelle“.`,
                fehler: `Übernahme gescheitert: ${s.fehler || s.meldung}` }[s.status] ?? '';
            this.stand.textContent = text;
            if (this.knopf) this.knopf.disabled = s.status === 'laeuft' || !this.liste?.stuecke?.length;
            if (s.status === 'laeuft') this._takt = setTimeout(() => this._standHolen(), 2000);
        } catch (fehler) {
            this.stand.textContent = `Stand nicht lesbar: ${fehler.message}`;
        }
    }
}
