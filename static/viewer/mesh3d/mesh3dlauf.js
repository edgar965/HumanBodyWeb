/**
 * Mesh3dlauf — die Laufkarte oben auf der Jobseite „Mesh-3D“ (11.10.2026): Schritte mit Dauer, Fortschritt, „ab Schritt“, Neu berechnen, Anhalten.
 *
 * Wie `Engine2d3dKleiderseite.schritte` auf der Seite von „2D3D Kleider“ (dieselben Klassen `meshfigur-schritt-*`). Start und Anhalten laufen über die
 * Endpunkte des Modell-Imports; „Neu berechnen“ beginnt beim gewählten Schritt und rechnet bis zum Modell (der Import kennt kein „bis“).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Mesh3danzeige } from './mesh3danzeige.js';

export class Mesh3dlauf {
    static ART = { fertig: 'fertig', laeuft: 'laeuft', gescheitert: 'fehler', angehalten: 'angehalten', uebersprungen: 'uebersprungen', offen: 'offen' };
    static STATUS = {
        neu: 'Angelegt — noch nicht gerechnet', laeuft: 'Läuft', fertig: 'Fertig', gescheitert: 'Fehlgeschlagen', angehalten: 'Angehalten',
    };

    constructor(seite) {
        this.seite = seite;
        this.liste = document.getElementById('schritte');
        this.balken = document.getElementById('fortschritt');
        this.text = document.getElementById('fortschritt-text');
        this.ab = document.getElementById('ab-schritt');
        this.starten = document.getElementById('starten');
        this.anhalten = document.getElementById('anhalten');
        this.status = document.getElementById('auftrag-status');
        this._schritte = '';
        this.starten.addEventListener('click', () => this.neu(this.ab.value || null, this.starten));
        this.anhalten.addEventListener('click', () => this.stoppen());
    }

    zeigen(z) {
        const laeuft = z.status === 'laeuft';
        this.liste.replaceChildren();
        for (const s of z.schritte) {
            const punkt = document.createElement('li');
            const art = Mesh3dlauf.ART[s.zustand] || 'offen';
            punkt.className = `meshfigur-schritt meshfigur-schritt-${art}${['angehalten', 'uebersprungen'].includes(art) ? ` mesh3d-schritt-${art}` : ''}`;
            punkt.title = s.hinweis || '';
            punkt.textContent = s.titel;
            if (s.dauer_s) {
                const zeit = document.createElement('small');
                zeit.textContent = ` ${Mesh3danzeige.dauer(s.dauer_s)}`;
                punkt.appendChild(zeit);
            }
            this.liste.appendChild(punkt);
        }
        this.balken.style.width = `${laeuft || z.status === 'fertig' ? z.fortschritt : (z.status === 'neu' ? 0 : z.fortschritt)}%`;
        const klar = z.wartet ? 'In der Warteschlange' : (Mesh3dlauf.STATUS[z.status] || z.status);
        // Eingereiht (ein anderer Import rechnet): eine normale Auskunft statt eines Fehlers, der Auftrag startet von selbst.
        this.text.textContent = z.wartet ? (z.detail || 'In der Warteschlange') : laeuft ? `${z.fortschritt} % — ${z.detail || z.schritt || ''}` : `${klar}${z.dauer_s ? ` · ${Mesh3danzeige.dauer(z.dauer_s)}` : ''}`;
        this.status.textContent = klar;
        this._abwahl(z);
        this.starten.disabled = laeuft;
        this.starten.querySelector('span').textContent = z.wartet ? 'Eingereiht …' : laeuft ? 'Berechnet …' : 'Neu berechnen';
        this.anhalten.disabled = !laeuft;
        this.ab.disabled = laeuft;
    }

    /** Die Wahl „ab Schritt“: erster Eintrag = von vorn; die gewählte bleibt über Abfragetakte stehen. */
    _abwahl(z) {
        const schluessel = JSON.stringify(z.moegliche.map(s => s.schluessel));
        if (schluessel === this._schritte) return;
        this._schritte = schluessel;
        const vorher = this.ab.value;
        this.ab.replaceChildren();
        z.moegliche.forEach((s, i) => this.ab.appendChild(new Option(i === 0 ? `${s.titel} (von vorn)` : s.titel, s.schluessel)));
        if (vorher && z.moegliche.some(s => s.schluessel === vorher)) this.ab.value = vorher;
    }

    /** Rechnet ab einem Schritt neu — auch für die Knöpfe der Karten („Pose rechnen“). */
    async neu(ab, knopf = null) {
        const tat = async () => {
            try {
                // Eine hochgeladene, nicht übernommene Datei kommt zuerst ins Netz des Auftrags (`Mesh3dquelle.vorStart`); ein neues Netz rechnet immer von vorn (die Ergebnisse des alten sind weg).
                const quelle = await this.seite.quelle.vorStart();
                if (quelle === false) return;
                if (quelle?.neues_netz) ab = null;
                const antwort = await Serverabruf.senden(`/api/character/blendimport/${this.seite.kennung}/neu/`, { ab });
                if (antwort.error) throw new Error(antwort.error);
                await this.seite.aktualisieren();
                if (antwort.wartet && antwort.meldung) this.text.textContent = antwort.meldung;      // sofort sagen, dass der Auftrag eingereiht ist (der nächste Takt bringt denselben Text vom Stand)
            } catch (fehler) {
                this.seite.fehlerband.meldung(`Start fehlgeschlagen: ${fehler.message}`);
                throw fehler;
            }
        };
        if (knopf) return Knopfsperre.waehrend(knopf, tat, 'Startet …').catch(() => {});
        return tat().catch(() => {});
    }

    async stoppen() {
        this.anhalten.disabled = true;
        try {
            await Serverabruf.senden(`/api/character/blendimport/${this.seite.kennung}/anhalten/`, {});
            await this.seite.aktualisieren();
        } catch (fehler) {
            this.seite.fehlerband.meldung(`Anhalten fehlgeschlagen: ${fehler.message}`);
        }
    }
}
