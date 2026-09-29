/**
 * Blendermodellrunde — eine Karte je Runde im Reiter „Iterationen" (29.09.2026).
 *
 * Zwei Arten Einträge in `ergebnis.iterationen`: die von Hand abgelegten Runden (`runde_ablegen.py`: Notiz, Kachel der
 * vier Ansichten, .blend) und die des Kreislaufs (`Kostuemrunde.ablegen`: Art, Note, Vergleichstafel, Änderungen,
 * Bericht der Prüf-KI). Die Karte zeigt, was da ist.
 */
export class Blendermodellrunde {

    static ARTEN = {
        ausgang: 'Ausgangslage', optimierer: 'Optimierer', ki: 'Prüf-KI übernommen', ki_verworfen: 'Prüf-KI verworfen',
    };

    constructor(dateiAdresse) {
        this.datei = dateiAdresse;
    }

    static zahl(wert, stellen = 3) {
        return wert == null ? '—' : Number(wert).toLocaleString('de-DE', { maximumFractionDigits: stellen });
    }

    karte(r) {
        const karte = document.createElement('div');
        karte.className = 'blendermodell-runde' + (r.uebernommen === false ? ' blendermodell-runde-verworfen' : '');
        const kopf = document.createElement('h3');
        const art = Blendermodellrunde.ARTEN[r.art] ? ` · ${Blendermodellrunde.ARTEN[r.art]}` : '';
        const note = r.note ? ` · Abweichung ${Blendermodellrunde.zahl(r.note.abweichung, 4)} (Umriss-IoU `
            + `${Blendermodellrunde.zahl(r.note.iou)}, Farbe ${Blendermodellrunde.zahl(r.note.farbe)})` : '';
        kopf.textContent = `Runde ${r.runde} · ${r.zeit || ''}${art}${note}`;
        karte.appendChild(kopf);
        if (r.notiz) karte.appendChild(this._text('p', r.notiz));
        if (r.kritik?.fehler) karte.appendChild(this._text('p', `Prüf-KI ${r.kritik.modell}: ${r.kritik.fehler}`, 'hb-schlecht'));
        const d = r.dateien || {};
        for (const [schluessel, alt] of [['vergleich', 'oben Vorlage, unten Render je Blickwinkel'],
                                         ['ansichten', 'vorn, rechts, hinten, links']]) {
            if (!d[schluessel]) continue;
            const bild = document.createElement('img');
            bild.src = this.datei(d[schluessel]);
            bild.alt = `Runde ${r.runde}: ${alt}`;
            bild.loading = 'lazy';
            karte.appendChild(bild);
        }
        const aenderungen = Object.entries(r.aenderungen || {});
        if (aenderungen.length) {
            const liste = aenderungen.map(([k, [a, b]]) =>
                `${k}: ${Blendermodellrunde.zahl(a)} → ${Blendermodellrunde.zahl(b)}`).join(' · ');
            karte.appendChild(this._text('p', `Geändert: ${liste}`, 'hb-hinweis'));
        }
        karte.appendChild(this._links(r, d));
        return karte;
    }

    _text(tag, text, klasse = '') {
        const el = document.createElement(tag);
        el.textContent = text;
        if (klasse) el.className = klasse;
        return el;
    }

    _links(r, d) {
        const links = document.createElement('div');
        links.className = 'mesh-downloads';
        for (const [schluessel, text] of [['kostuem', 'Kostüm als GLB'], ['zauberer', 'Blender-Datei (.blend)'],
                                          ['bericht', 'Bericht (JSON)']]) {
            if (!d[schluessel]) continue;
            const a = document.createElement('a');
            a.href = this.datei(d[schluessel]);
            a.textContent = text;
            a.download = d[schluessel];
            links.appendChild(a);
        }
        if (r.teile && Object.keys(r.teile).length) {
            links.appendChild(this._text('span', `Teile: ${Object.keys(r.teile).join(', ')}`, 'hb-hinweis'));
        }
        return links;
    }
}
