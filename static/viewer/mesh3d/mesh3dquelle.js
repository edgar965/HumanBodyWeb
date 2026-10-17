/**
 * Mesh3dquelle — die Karte „Quelle und Einstellungen“ der Jobseite „Mesh-3D“ (11.10.2026).
 *
 * Oben die Quelle: was gelesen wird (Datei, Format, Weg, nicht gelesene Fassungen) und — änderbar (Edgar: „ich kann nicht mal das Modell ändern!!!“) — Pfad, Name der Figur und „Datei wählen …“ /
 * „Ordner wählen …“ zum Hochladen (`Mesh3dwahl`). „Quelle übernehmen“ (`POST /api/mesh3d/<kennung>/quelle/`, `Mesh3dquellwechsel`) ersetzt das Netz; ein anderes Netz verwirft die Ergebnisse des
 * Auftrags (Rückfrage), ein anderer Name nicht. Darunter die Einstellungen des Imports aus dem Katalog des Servers (`/api/character/blendimport/einstellungen/?format=…`): jede Eingabe wird sofort
 * gespeichert (`POST /api/mesh3d/<kennung>/einstellungen/`) und gilt ab dem nächsten Start; während eines Laufs ist alles gesperrt.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3danzeige } from './mesh3danzeige.js';
import { Mesh3dfelder } from './mesh3dfelder.js';
import { Mesh3dwahl } from './mesh3dwahl.js';

export class Mesh3dquelle {
    static QUELLFELDER = ['pfad', 'name', 'eigener_name'];
    /** Beim Weg „netz“ (ein verschmolzenes Netz) zählen nur diese Einstellungen — Kleider, Haut, Augen, Scham und Körperergänzung gehören zum Weg „teile“. */
    static NETZ_FELDER = ['basis', 'umfang', 'pose', 'pose_drehung', 'kleidung_zug', 'frisur', 'frisur_ziel', 'vergleichsvariante'];
    static FORMATE = { blend: 'Blender (.blend)', obj: 'OBJ', fbx: 'FBX', glb: 'GLB' };

    constructor(seite) {
        this.seite = seite;
        this.zahlen = document.getElementById('quelle-zahlen');
        this.felder = document.getElementById('mesh3d-optionen');
        this.meldung = document.getElementById('optionen-meldung');
        this.gesperrt = document.getElementById('optionen-gesperrt');
        this.pfad = document.getElementById('quelle-pfad');
        this.name = document.getElementById('quelle-name');
        this.format = document.getElementById('quelle-format');
        this.knopf = document.getElementById('quelle-uebernehmen');
        this.formmeldung = document.getElementById('quelle-meldung');
        this.optionen = null;
        this._gebaut = false;
        this._stand = '';
        this._frist = null;
        // Das Format der Auswahl steht im Dateidialog (`accept`) und im Upload; „Datei wählen“ trägt den Pfad der hochgeladenen Datei ein, übernommen wird erst mit „Quelle übernehmen“.
        this.format.innerHTML = Object.entries(Mesh3dquelle.FORMATE).map(([k, t]) => `<option value="${k}">${t}</option>`).join('');
        this.wahl = new Mesh3dwahl(document.getElementById('quelle-wahl'), antwort => {
            this.pfad.value = antwort.pfad;
            this.formmeldung.textContent = 'Datei hochgeladen — „Quelle übernehmen“ ersetzt das Netz (auch „Neu berechnen“ übernimmt sie zuerst).';
        });
        this.format.addEventListener('change', () => this.wahl.setzen(this.format.value));
        this.knopf.addEventListener('click', () => this.uebernehmen());
        this._pfadGeladen = '';
        this._nameGeladen = '';
    }

    async zeigen(z) {
        if (Mesh3danzeige.geaendert(this, '_stand', [z.quelle, z.name, z.format, z.weg, z.einstellungen?.pfad, z.einstellungen?.eigener_name])) {
            const q = z.quelle;
            Mesh3danzeige.zeilen(this.zahlen, [
                q.datei ? `Datei: ${q.datei}` : 'Datei: noch keine — „Datei wählen …“ lädt ein Netz hoch, „Quelle übernehmen“ setzt es.',
                `Format: ${Mesh3dquelle.FORMATE[z.format] || z.format} · Figur: „${z.name}“`,
                `Weg: ${z.weg === 'netz' ? 'Netz (ein verschmolzenes Netz, ohne Blender)' : 'Teile (getrennte Objekte, Blender liest)'}${z.weg_grund ? ` — ${z.weg_grund}` : ''}`,
                (q.kandidaten || []).length > 1 ? `Im Ordner nicht gelesen: ${q.kandidaten.slice(1).map(k => k.datei).join(', ')}` : null,
            ]);
            this._formfuellen(z);
        }
        if (!this._gebaut) await this.bauen(z);
        const laeuft = z.status === 'laeuft';
        for (const element of [this.pfad, this.name, this.format, this.knopf]) element.disabled = laeuft;
        if (this.optionen) {
            Mesh3dfelder.sperren(this.felder, this.optionen, laeuft);
            this.gesperrt.hidden = !laeuft;
        }
    }

    /** Pfad und Name aus dem Stand in die Felder — aber nicht über etwas, das gerade getippt wurde. */
    _formfuellen(z) {
        const pfad = z.einstellungen?.pfad || z.quelle.datei || '';
        const name = z.einstellungen?.eigener_name || '';
        if (this.pfad.value === this._pfadGeladen) this.pfad.value = pfad;
        if (this.name.value === this._nameGeladen) this.name.value = name;
        this._pfadGeladen = pfad;
        this._nameGeladen = name;
        this.format.value = z.format;
        this.wahl.setzen(z.format);
    }

    async bauen(z) {
        this._gebaut = true;
        try {
            const daten = await Serverabruf.json(`/api/character/blendimport/einstellungen/?format=${encodeURIComponent(z.format)}`);
            this.optionen = daten.optionen.filter(o => !Mesh3dquelle.QUELLFELDER.includes(o.schluessel)
                && (z.weg !== 'netz' || Mesh3dquelle.NETZ_FELDER.includes(o.schluessel)));
            Mesh3dfelder.bauen(this.felder, this.optionen, z.einstellungen, werte => this.speichern(werte));
        } catch (fehler) {
            this._gebaut = false;
            this.seite.fehlerband.lesefehler(`Einstellungen nicht lesbar: ${fehler.message}`);
        }
    }

    /** Steht im Feld ein anderer Pfad als im Auftrag — eine Datei ist hochgeladen oder getippt, aber noch nicht übernommen? */
    offen() {
        const z = this.seite.zustand;
        const pfad = this.pfad.value.trim();
        return Boolean(pfad) && pfad !== (z?.einstellungen?.pfad || z?.quelle?.datei || '');
    }

    /**
     * Vor „Neu berechnen“: eine hochgeladene, aber nicht übernommene Datei wird zuerst übernommen — sonst rechnet der Lauf das ALTE Netz (Edgar, 14.10.2026: „ich habe die glb geändert — du hast noch den alten Job
     * gerechnet“; beide Aufträge am 14.10.2026 liefen so mit `Edgar.glb`, obwohl `edgar2009.glb` und `edgar1970.glb` hochgeladen waren — der Pfad im Feld ging mit dem Neuladen der Seite verloren).
     * → `true` (nichts offen), die Antwort des Servers (übernommen) oder `false` (abgebrochen oder gescheitert: dann wird nicht gerechnet).
     */
    async vorStart() {
        if (!this.offen()) return true;
        return (await this.uebernehmen()) || false;
    }

    /** „Quelle übernehmen“: Pfad und Name an den Server; ein anderes Netz verwirft die Ergebnisse, davor fragt die Seite. → die Antwort des Servers, `false` bei Abbruch oder Fehler. */
    async uebernehmen() {
        const pfad = this.pfad.value.trim();
        const z = this.seite.zustand;
        this.formmeldung.classList.remove('fehlertext');
        if (!pfad) {
            this.formmeldung.classList.add('fehlertext');
            this.formmeldung.textContent = 'Pfad fehlt: eine Datei oder einen Ordner angeben, oder „Datei wählen …“.';
            return false;
        }
        const hatErgebnis = z && z.status !== 'neu';
        if (hatErgebnis && pfad !== (z.einstellungen?.pfad || z.quelle.datei)
            && !window.confirm('Ein anderes Netz verwirft die bisherigen Ergebnisse dieses Auftrags (Auftrag „Mesh to 3D“, Rollen, Pose, Bewegung). Das gespeicherte Modell der alten Datei bleibt, bis der Auftrag gelöscht wird. Fortfahren?')) return false;
        this.knopf.disabled = true;
        this.formmeldung.textContent = 'wird übernommen …';
        try {
            const antwort = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/quelle/`, { pfad, eigener_name: this.name.value.trim() });
            if (antwort.error) throw new Error(antwort.error);
            this.formmeldung.textContent = antwort.neues_netz
                ? 'Neues Netz übernommen — das alte ist aus der Mesh-Ansicht weg, „Neu berechnen“ startet den Lauf.' : 'Name übernommen — er gilt ab dem nächsten Lauf.';
            this._gebaut = false;
            await this.seite.aktualisieren();
            return antwort;
        } catch (fehler) {
            this.formmeldung.classList.add('fehlertext');
            this.formmeldung.textContent = `Nicht übernommen: ${fehler.daten?.error || fehler.message}`;
            return false;
        } finally {
            this.knopf.disabled = this.seite.zustand?.status === 'laeuft';
        }
    }

    /** Sofort speichern — Text erst beim Verlassen des Felds (`change`), Auswahl und Haken sofort. */
    async speichern(werte) {
        this.meldung.textContent = 'speichert …';
        try {
            const antwort = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/einstellungen/`, { werte });
            if (antwort.error) throw new Error(antwort.error);
            this.meldung.textContent = 'gespeichert';
            window.clearTimeout(this._frist);
            this._frist = window.setTimeout(() => { this.meldung.textContent = ''; }, 2500);
        } catch (fehler) {
            this.meldung.textContent = '';
            this.seite.fehlerband.meldung(`Einstellung nicht gespeichert: ${fehler.message}`);
        }
    }
}
