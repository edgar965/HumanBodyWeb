/**
 * Mesh3daitestkleider — Karte „Kleider und Bestandteile“ der Testseite (17.10.2026 nachts, Server `Mesh3daitestkleider`, `Mesh3daitestmodell`).
 * Edgar: „Nach dem Bauen müsste ich im Ergebnis View festlegen können, ob ich ein Kleidungsstück in der ersten Option oder zweiten Option haben möchte. Also Toggle für jedes Kleidungsstück
 * für beide Optionen und Button zum übernehmen von Option a oder b in das End-Modell, mit speichern des Modells“.
 * Je Stück drei Schaltknöpfe (a Katalog · b aus dem Netz · aus); „Alle: a / b“ stellt die Vorgabe und nimmt die eigenen Wahlen zurück. Die gewählten Stücke stehen im Feld „Ausgabe“ an der Figur,
 * gehäutet mit denselben Matrizen (`Mesh3daitestnetzbau`). „Übernehmen und speichern“ startet den Prozess auf dem Server und fragt alle 2 s nach seinem Stand.
 */
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daitestnetzbau } from './mesh3daitestnetzbau.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const WEGTEXT = { a: 'Katalog', b: 'aus dem Netz', aus: 'aus' };

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
        this.info.textContent = daten.stuecke.length
            ? `${daten.stuecke.length} Stücke. b = aus dem Netz geschnitten (Mesh-3D-Lauf „${q?.name}“, Mesh to 3D ${q?.figur}) und auf die vorhergesagte Figur übertragen; `
              + 'a = Stück der Garderobe auf dieser Figur gebaut, umgefärbt in der Farbe aus dem Netz — gewählt durch Messung (Überdeckung der bedeckten Körperstellen; '
              + 'Haar: die Frisur, die „Mesh to 3D“ am Netzhaar gewählt hat). Haut: a = die Haut der Figur, b = die gebackene Haut des Mesh-3D-Laufs (gleiche Genesis-UV; '
              + 'ein kurzer Bart steht dort in der Haut, nicht im Haar). Das Netz von Mesh3D-AI sagt Kleider noch nicht selbst voraus.'
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

    _zeile(st) {
        const tr = document.createElement('tr');
        const a = st.a && !st.a.fehler ? st.a : null;
        const b = st.b && !st.b.fehler ? st.b : null;
        const haut = st.art === 'haut';
        tr.append(this._zelle(st.name, haut ? 'die Haut der Figur' : `${st.art}, Region ${st.region}${st.bewegung === 'starr' ? ', starr' : ''}`));
        if (haut) {
            tr.append(this._zelle(a ? a.anzeige_name : `— ${st.a?.fehler || 'nicht gerechnet'}`));
            tr.append(this._zelle(b ? `${b.anzeige_name}: Kacheln ${Object.keys(b.kacheln || {}).join(', ')}` : `— ${st.b?.fehler || 'nicht gerechnet'}`));
        } else {
            tr.append(this._zelle(a ? `${a.anzeige_name} (${a.kategorie}${a.ueberdeckung != null ? `, Überdeckung ${de(a.ueberdeckung, 2)}` : ''})` : `— ${st.a?.fehler || 'nicht gerechnet'}`,
                a?.kandidaten ? `nächste: ${a.kandidaten.slice(1).map(k => `${k.kennung} ${de(k.ueberdeckung, 2)}`).join(' · ')}` : ''));
            tr.append(this._zelle(b ? `${de(b.dreiecke)} Dreiecke (${b.uebertrag?.art === 'starr' ? 'starr übertragen' : `Abstand zur Haut Median ${de(b.uebertrag?.abstand_mm_median ?? 0, 1)} mm`})`
                : `— ${st.b?.fehler || 'nicht gerechnet'}`));
        }
        const wahl = document.createElement('td');
        const leiste = document.createElement('div');
        leiste.className = 'schalterleiste mesh3dai-kleider-wahl';
        // Haut: kein „aus“ — eine Figur ohne Haut gibt es nicht.
        for (const w of haut ? ['a', 'b'] : ['a', 'b', 'aus']) {
            const k = document.createElement('button');
            k.type = 'button';
            k.className = 'schaltknopf' + (st.wahl === w ? ' active' : '');
            k.textContent = w === 'aus' ? 'aus' : `${w} · ${haut && w === 'a' ? 'Haut der Figur' : WEGTEXT[w]}`;
            k.disabled = (w === 'a' && !a) || (w === 'b' && !b);
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
