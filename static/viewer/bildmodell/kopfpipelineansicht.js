import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Proportionen3dbuehne } from './proportionen3dbuehne.js';
import { Laufansicht } from './laufansicht.js';

/**
 * Kopfpipelineansicht — EIN Panel direkt an den Kopf-Fotos: Fotoauswahl, Pipeline, 3D-Ergebnis
 * (22.09.2026, mehrfach erweitert).
 *
 * Der Weg hierher, Zitat für Zitat: „Mach eine eigene Pipeline für den Kopf, wo ich FLAME und
 * KeenTools FaceBuilder auswählen kann … und mehrere Fotos auswählen kann für den Kopf" — „mach
 * FaceBuilder OHNE Handarbeit im Blender, automatisch" — „wo ist der neue Workflow??? ich
 * brauch einen Button bei den Kopf bildern" — „mach mir eine extra Ausgabe NUR mit dem Kopf …
 * eine neue Zeile + das Ausgabefenster" — „warum ein Foto?? du hast nun 3 unterschiedliche
 * Pipelines für Kopf Foto, wo sind diese???" — und zuletzt, die Antwort auf die Rückfrage nach
 * einem Vergleich aller drei: „ich brauche Auswahlboxen für Fotos (ein oder mehrere), daneben
 * Auswahl für die Pipeline, daneben das Ergebnis in 3D". GENAU DAS baut diese Klasse, als EIN
 * Panel unter der Überschrift des Kopf-Fotobereichs (`#bereich-kopf`), drei Spalten:
 *
 *   Fotos     Häkchen mit Vorschaubild je Kopf-Foto (`kopf_an`) — grün umrandet, was die letzte
 *             Rechnung verwendet hat, rot umrandet, was scheiterte (kein Gesicht erkannt).
 *   Pipeline  Der Options-Block „Kopf (FLAME-Pipeline)" (`Optionenformular.kopfBlock`) — NICHT
 *             mehr unter „Optionen je Schritt" (dort war er für Edgar nicht auffindbar), sondern
 *             hierher verschoben (derselbe `<select>`, `Optionenformular.werte()`/`stellen()`
 *             finden ihn über die Referenz `kopfBlock`, unabhängig davon, wo er im Dokument
 *             hängt) — Kopfverfahren, Mischung, „Kopf berechnen", Statustext.
 *   3D        Der FLAME-Kopf des letzten Laufs, live (`kopf3d/`, `Bildmodellkopf.netz3d`).
 *
 * Ohne Häkchen an irgendeinem Foto: ALLE Kopffotos außer der Rückansicht zählen automatisch
 * (`Bildmodellkopf.bilder`, seit dem „warum ein Foto??"-Fund korrigiert — vorher griff da
 * fälschlich nur das eine Kopf-Hauptbild). Ein Klick auf „Kopf berechnen" läuft die Kette „kopf"
 * bis „speichern" durch (`KETTE`) — überspringt nur Sichtung/Schätzung (die hängen nicht am
 * Kopf), baut aber Zielnetz, Anpassung, Vorschau, Textur und Speichern aus dem neuen Kopf neu.
 */
export class Kopfpipelineansicht {

    static KETTE = ['kopf', 'ziel', 'anpassung', 'rest', 'vorschau', 'textur', 'speichern'];
    static FARBE = 0xd9c6b9;
    //: Größe des 3D-Kastens und Kamera-Zoom/-Blick — job-übergreifend gemerkt wie `Dialoggroesse`
    //: (23.09.2026, Edgar: „anpassbar in Höhe/Breite … merke dir die Zoom Position und die
    //: Fensterpositionen"). Unter `MINDESTENS` gilt der Merker als kaputt und wird ignoriert.
    static GROESSE_SCHLUESSEL = 'bildmodell_kopf3d_groesse';
    static KAMERA_SCHLUESSEL = 'bildmodell_kopf3d_kamera';
    static MINDESTENS = { b: 220, h: 180 };

    constructor(auftrag, formular) {
        this.auftrag = auftrag;
        this.formular = formular;
        this.knopf = null;
        this.texturKnopf = null;
        this.abbrechenKnopf = null;
        this.laufFeld = null;
        this.balken = null;
        this.laufText = null;
        this.status = null;
        this.fotosFeld = null;
        this.buehne = null;
        this._3dtext = null;
        this._fotosStand = null;
        this._standNetz = null;
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    /** Das Panel unter die Überschrift der Kopf-Fotos hängen — einmal, nach `bauen()`. */
    einhaengen() {
        const bereich = document.getElementById('bereich-kopf');
        const titel = bereich?.querySelector('h3');
        if (!bereich || !titel) return;

        const panel = document.createElement('div');
        panel.className = 'bildmodell-kopfpanel';

        this.fotosFeld = document.createElement('div');
        this.fotosFeld.className = 'bildmodell-kopfpanel-fotos';

        const mitte = document.createElement('div');
        mitte.className = 'bildmodell-kopfpanel-mitte';
        if (this.formular?.kopfBlock) {
            mitte.appendChild(this.formular.kopfBlock);
            this.status = document.createElement('div');
            this.status.className = 'hb-hinweis bildmodell-kopfstatus';
            this.formular.kopfBlock.appendChild(this.status);
        }
        // 23.09.2026, Edgar: „die Texturberechnung in dem gleiche Workflow, unter den Combo
        // boxen für Flame usw" — die Kette „Kopf berechnen" läuft ja schon bis „textur" durch.
        if (this.formular?.texturBlock) mitte.appendChild(this.formular.texturBlock);
        this.knopf = document.createElement('button');
        this.knopf.type = 'button';
        this.knopf.className = 'btn btn-primary btn-sm bildmodell-kopfknopf';
        this.knopf.title = 'Die per Häkchen links gewählten Fotos (ohne Häkchen: alle Kopffotos außer '
            + 'Rückansicht) mit dem Verfahren oben rechnen; danach Zielnetz, Anpassung, Vorschau, Textur '
            + 'und Speichern neu (ohne Sichtung/Schätzung — die hängen nicht am Kopf)';
        this.knopf.addEventListener('click', () => this.berechnen());

        // 23.09.2026, Edgar: „mach Fortschritts-leiste, das dauert ewig!! Und abbrechen button" —
        // die Kette rechnet nicht nur den Kopf, sondern bis „speichern" durch (Textur-Fotobake
        // allein ~1–3 min); ohne Rückmeldung sah das aus wie ein hängender Lauf. Balken/Text/
        // Abbrechen wie bei „Person" (`personenformular.js`), nur hier im Kopf-Panel.
        const knopfzeile = document.createElement('div');
        knopfzeile.className = 'bildmodell-kopfknopfzeile';
        this.abbrechenKnopf = document.createElement('button');
        this.abbrechenKnopf.type = 'button';
        this.abbrechenKnopf.className = 'btn btn-secondary btn-sm';
        this.abbrechenKnopf.disabled = true;
        this.abbrechenKnopf.title = 'Den laufenden Lauf beenden (Prozess samt Kindern)';
        this.abbrechenKnopf.innerHTML = '<i class="fas fa-stop"></i> Abbrechen';
        this.abbrechenKnopf.addEventListener('click', () => this.abbrechen());
        // 23.09.2026, Edgar: „ich will hier auch die textur berechnen können in einem Schritt" —
        // nur der Schritt „textur" (mit der Wahl aus dem Textur-Block direkt darüber), ohne den
        // ganzen Kopf neu zu rechnen. Dasselbe tut „Textur anpassen" weiter unten auf der Seite
        // (`texturansicht.js`), hier nur bequemer erreichbar.
        this.texturKnopf = document.createElement('button');
        this.texturKnopf.type = 'button';
        this.texturKnopf.className = 'btn btn-secondary btn-sm';
        this.texturKnopf.title = 'Nur die Textur mit der Wahl oben neu backen, ohne den Kopf neu zu rechnen';
        this.texturKnopf.innerHTML = '<i class="fas fa-paint-roller"></i> Textur berechnen';
        this.texturKnopf.addEventListener('click', () => this.texturBerechnen());
        knopfzeile.append(this.knopf, this.texturKnopf, this.abbrechenKnopf);
        mitte.appendChild(knopfzeile);

        this.laufFeld = document.createElement('div');
        this.laufFeld.className = 'bildmodell-personlauf hb-versteckt';
        const balkenRahmen = document.createElement('div');
        balkenRahmen.className = 'bildmodell-balken';
        this.balken = document.createElement('div');
        this.balken.className = 'bildmodell-fuellung';
        this.balken.style.width = '0%';
        balkenRahmen.appendChild(this.balken);
        this.laufText = document.createElement('span');
        this.laufText.className = 'hb-hinweis';
        this.laufFeld.append(balkenRahmen, this.laufText);
        mitte.appendChild(this.laufFeld);

        const drei = document.createElement('div');
        drei.className = 'bildmodell-kopfpanel-3d';
        const canvas = document.createElement('canvas');
        canvas.className = 'bildmodell-3dcanvas';
        drei.appendChild(canvas);
        this._3dtext = document.createElement('div');
        this._3dtext.className = 'hb-hinweis bildmodell-kopfpanel-3dtext';
        drei.appendChild(this._3dtext);

        panel.append(this.fotosFeld, mitte, drei);
        titel.insertAdjacentElement('afterend', panel);

        this._groesseWiederherstellen(drei);
        this._groesseMerkenEinrichten(drei);

        try {
            this.buehne = new Proportionen3dbuehne(canvas, { gitter: false });
            this.buehne.starten();
            this._kameraMerkenEinrichten();
        } catch (fehler) {
            this._3dtext.textContent = `Keine 3D-Ansicht: ${fehler.message}`;
        }

        this.zeigen(this.auftrag.zustand);
    }

    /** Zieh-Größe des 3D-Kastens aus dem letzten Mal (wie `Dialoggroesse`, aber auf einem
     *  Grid-Feld statt einem `<dialog>` — kein `.open`-Zustand zu prüfen). */
    _groesseWiederherstellen(drei) {
        let g = null;
        try { g = JSON.parse(localStorage.getItem(Kopfpipelineansicht.GROESSE_SCHLUESSEL) || 'null'); }
        catch (fehler) { g = null; }
        const min = Kopfpipelineansicht.MINDESTENS;
        if (g && g.b >= min.b && g.h >= min.h) {
            // 23.09.2026: `window.innerWidth - 16` kann kleiner als `min.b` werden (sehr schmales
            // Fenster) — dann war die Breite bisher ein ungültiges negatives „px" und der Browser
            // verwarf sie still (kein Fehler, einfach kein Effekt). Nach unten auf `min.b` geklemmt.
            drei.style.width = `${Math.max(min.b, Math.min(g.b, window.innerWidth - 16))}px`;
            drei.style.height = `${g.h}px`;
        }
    }

    _groesseMerkenEinrichten(drei) {
        if (typeof ResizeObserver === 'undefined') return;
        const min = Kopfpipelineansicht.MINDESTENS;
        new ResizeObserver(() => {
            const b = Math.round(drei.offsetWidth), h = Math.round(drei.offsetHeight);
            if (b < min.b || h < min.h) return;
            try { localStorage.setItem(Kopfpipelineansicht.GROESSE_SCHLUESSEL, JSON.stringify({ b, h })); }
            catch (fehler) { /* ohne Merker */ }
        }).observe(drei);
    }

    /** Kamera-Position/-Blick (Zoom) aus dem letzten Mal — angewendet, sobald ein Netz da ist
     *  (`_laden`), sonst überschreibt `Proportionen3dbuehne.setzen`s Erstansicht sie sofort wieder. */
    _kameraWiederherstellen() {
        let k = null;
        try { k = JSON.parse(localStorage.getItem(Kopfpipelineansicht.KAMERA_SCHLUESSEL) || 'null'); }
        catch (fehler) { k = null; }
        if (!k || !this.buehne) return;
        this.buehne.kamera.position.set(k.px, k.py, k.pz);
        this.buehne.steuerung.target.set(k.tx, k.ty, k.tz);
        this.buehne.steuerung.update();
    }

    _kameraSpeichern() {
        const p = this.buehne.kamera.position, t = this.buehne.steuerung.target;
        try {
            localStorage.setItem(Kopfpipelineansicht.KAMERA_SCHLUESSEL, JSON.stringify(
                { px: p.x, py: p.y, pz: p.z, tx: t.x, ty: t.y, tz: t.z }));
        } catch (fehler) { /* ohne Merker */ }
    }

    _kameraMerkenEinrichten() {
        if (!this.buehne) return;
        let zeitstempel = null;
        // Entprellt über `change` (deckt Damping/Trägheit nach dem Loslassen ab) UND zusätzlich
        // sofort bei `pointerup`/`wheel` auf der Leinwand selbst — direkt am DOM-Ereignis, nicht
        // über OrbitControls' eigene Änderungserkennung, falls die (Damping, Epsilon-Vergleich)
        // einen Zug mal nicht als „change" zählt.
        this.buehne.steuerung.addEventListener('change', () => {
            clearTimeout(zeitstempel);
            zeitstempel = setTimeout(() => this._kameraSpeichern(), 400);
        });
        this.buehne.canvas.addEventListener('pointerup', () => this._kameraSpeichern());
        this.buehne.canvas.addEventListener('wheel', () => {
            clearTimeout(zeitstempel);
            zeitstempel = setTimeout(() => this._kameraSpeichern(), 400);
        }, { passive: true });
    }

    /** Die Kette ab „kopf" starten — mit dem gerade im Panel gewählten Verfahren. */
    async berechnen() {
        try {
            const optionen = this.formular ? this.formular.werte() : undefined;
            await this.auftrag.starten(optionen, 'kopf', {}, null, Kopfpipelineansicht.KETTE);
        } catch (fehler) {
            window.alert(`Kopf nicht gestartet: ${fehler.message}`);
        }
    }

    async abbrechen() {
        try { await this.auftrag.anhalten(); }
        catch (fehler) { window.alert(`Abbrechen fehlgeschlagen: ${fehler.message}`); }
    }

    /** Nur der Schritt „textur" — mit neuen Dateien vorher die Sichtung (wie `Texturansicht.anpassen`). */
    async texturBerechnen() {
        try {
            const neue = (this.auftrag.zustand.neue || []).length;
            const schritte = neue ? ['sichtung', 'textur'] : ['textur'];
            const optionen = this.formular ? this.formular.werte() : undefined;
            await this.auftrag.starten(optionen, schritte[0], {}, null, schritte);
        } catch (fehler) {
            window.alert(`Textur nicht gestartet: ${fehler.message}`);
        }
    }

    /** Balken + Text während der Kette (wie `Personenformular._lauf`) — die Kette rechnet den
     *  Kopf UND Zielnetz/Anpassung/Vorschau/Textur/Speichern; ohne diese Anzeige sah die
     *  Textur-Fotobake (~1–3 min) wie ein hängender Lauf aus. */
    _laufZeigen(zustand, laeuftHier) {
        if (!this.laufFeld) return;
        this.laufFeld.classList.toggle('hb-versteckt', !laeuftHier);
        if (!laeuftHier) return;
        const prozent = Math.max(0, Math.min(100, Number((zustand.lauf || {}).prozent || 0)));
        this.balken.style.width = `${prozent}%`;
        const schritte = this.auftrag.constructor.SCHRITTE;
        const jetzt = schritte.indexOf(zustand.schritt);
        const ab = schritte.indexOf((zustand.optionen || {}).ab);
        const nummer = ab >= 0 && jetzt >= ab ? ` (${jetzt - ab + 1}/${schritte.length - ab})` : '';
        this.laufText.textContent = `${prozent} % · ${Laufansicht.NAMEN[zustand.schritt] || zustand.schritt || ''}${nummer}`
            + `${zustand.progress_detail ? ' · ' + zustand.progress_detail : ''}`;
    }

    zeigen(zustand) {
        this._fotosZeichnen(zustand);
        const k = (zustand?.ergebnis || {}).kopf;

        if (this.knopf) {
            const laeuft = zustand?.status === 'laeuft';
            // Über die ganze Kette hinweg „läuft" — `ab` bleibt 'kopf'/'textur', auch wenn
            // `schritt` längst weiter steht (`Bildmodellstart.starten` schreibt `optionen.ab`).
            const ab = (zustand?.optionen || {}).ab;
            const kopfLaeuft = laeuft && ab === 'kopf';
            const texturLaeuft = laeuft && ab === 'textur';
            this.knopf.disabled = laeuft;
            this.knopf.innerHTML = kopfLaeuft
                ? '<i class="fas fa-spinner fa-spin"></i> Kopf läuft …'
                : k?.netz ? '<i class="fas fa-sync"></i> Kopf neu berechnen' : '<i class="fas fa-cube"></i> Kopf berechnen';
            if (this.texturKnopf) {
                this.texturKnopf.disabled = laeuft;
                this.texturKnopf.innerHTML = texturLaeuft
                    ? '<i class="fas fa-spinner fa-spin"></i> Textur läuft …'
                    : '<i class="fas fa-paint-roller"></i> Textur berechnen';
            }
            if (this.abbrechenKnopf) this.abbrechenKnopf.disabled = !(kopfLaeuft || texturLaeuft);
            this._laufZeigen(zustand, kopfLaeuft || texturLaeuft);
        }

        if (this.status) {
            if (!k) { this.status.textContent = ''; }
            else {
                const teile = [`Verfahren: ${k.verfahren}`];
                if (k.fehler) teile.push(`Fehler: ${k.fehler}`);
                else if (k.hinweis) teile.push(k.hinweis);
                else if (k.netz) teile.push(`Kopf: ${k.punkte} Punkte, ${k.hoehe_cm} cm`);
                const fehlgeschlagen = (k.bilder || []).filter(b => !b.ok);
                const ok = (k.bilder || []).length - fehlgeschlagen.length;
                if (k.bilder && k.bilder.length) teile.push(`${ok} / ${k.bilder.length} Foto(s) ausgewertet`);
                if (k.anpassung && k.anpassung.fehler_prozent != null) {
                    teile.push(`Restfehler der Mehrbild-Anpassung: ${k.anpassung.fehler_prozent} %`);
                }
                this.status.textContent = teile.join(' · ');
            }
        }

        // `auftrag.zuhoeren` ruft `zeigen` schon beim Registrieren auf (im Konstruktor, vor
        // `einhaengen()`) — `_3dtext` gibt es da noch nicht. Ohne dieses Wächter-`if` würde
        // `_standNetz` schon hier gesetzt, und der echte Ladeversuch danach hielte sich fälschlich
        // für aktuell (kein Netz käme je an — genau der Fund vom 22.09.2026: leerer Text trotz
        // vorhandenem Ergebnis).
        if (this._3dtext && k && k.netz && k.stand !== this._standNetz) {
            this._standNetz = k.stand;
            this._laden();
        } else if (this._3dtext && !k?.netz && this._standNetz !== null) {
            this._standNetz = null;
            this._3dtext.textContent = k?.fehler || k?.hinweis || '';
        }
    }

    /** Vorschaubild + Häkchen je Kopf-Foto — grün/rot nach dem letzten Ergebnis. */
    _fotosZeichnen(zustand) {
        if (!this.fotosFeld) return;
        const bilder = (zustand?.bilder || []).filter(b => b.kategorie === 'kopf' && !b.video);
        const stand = JSON.stringify(bilder.map(b => [b.datei, b.kopf_an]));
        if (stand !== this._fotosStand) {
            this._fotosStand = stand;
            this.fotosFeld.innerHTML = '';
            for (const b of bilder) {
                const zeile = document.createElement('label');
                zeile.className = 'bildmodell-kopffoto';
                zeile.dataset.datei = b.datei;
                const kasten = document.createElement('input');
                kasten.type = 'checkbox';
                kasten.checked = !!b.kopf_an;
                kasten.addEventListener('change', async () => {
                    try { await this.auftrag.bildStellen(b.datei, { kopf_an: kasten.checked ? true : null }); }
                    catch (fehler) { kasten.checked = !kasten.checked; window.alert(fehler.message); }
                });
                const bild = document.createElement('img');
                bild.src = this.auftrag.dateiAdresse('zuschnitt', b.datei);
                bild.alt = b.datei;
                bild.loading = 'lazy';
                zeile.append(kasten, bild);
                this.fotosFeld.appendChild(zeile);
            }
        }
        const je = new Map(((zustand?.ergebnis || {}).kopf?.bilder || []).map(b => [b.datei, b]));
        for (const zeile of this.fotosFeld.children) {
            const info = je.get(zeile.dataset.datei);
            zeile.classList.toggle('bildmodell-kopffoto-ok', !!(info && info.ok));
            zeile.classList.toggle('bildmodell-kopffoto-fehler', !!(info && !info.ok));
            zeile.title = info && !info.ok ? `${zeile.dataset.datei}: ${info.fehler || 'nicht verwendbar'}` : zeile.dataset.datei;
        }
    }

    async _laden() {
        if (!this._3dtext) return;
        this._3dtext.textContent = 'Netz wird geladen …';
        try {
            const antwort = await Serverabruf.json(this.auftrag.adresse('kopf3d/'));
            if (!antwort || antwort.error) throw new Error((antwort || {}).error || 'keine Antwort');
            if (this.buehne) {
                this.buehne.netzSetzen(antwort);
                if (this.buehne.netz) {
                    // Echte Fototextur gibt es hier nicht (andere UV-Lage als FLAME, siehe
                    // `Bildmodellkopf.netz3d`) — der gemessene Hautton ist der ehrliche
                    // Zwischenstand statt der festen Platzhalterfarbe.
                    const farbe = antwort.hautton
                        ? (antwort.hautton[0] << 16) | (antwort.hautton[1] << 8) | antwort.hautton[2]
                        : Kopfpipelineansicht.FARBE;
                    this.buehne.netz.material.color.set(farbe);
                }
                this.buehne.fotokamera(null, 2.0);
                this._kameraWiederherstellen();
            }
            this._3dtext.textContent = `${(antwort.anzahl || 0).toLocaleString('de-DE')} Punkte, ${antwort.hoehe_cm} cm`;
        } catch (fehler) {
            this._3dtext.textContent = `Kein Netz geladen: ${fehler.message}`;
        }
    }
}
