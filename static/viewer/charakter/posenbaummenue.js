import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Kontextmenue } from '../gemeinsam/kontextmenue.js';
import { Ordnerwahl } from '../gemeinsam/ordnerwahl.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenbaumansicht } from './posenbaumansicht.js';

/**
 * Posenbaummenue — Kontextmenüs im Reiter „Posen": auf einer Pose Anwenden,
 * Umbenennen, Verschieben nach …, Löschen; auf einem Ordner Neuer Unterordner,
 * Umbenennen, Löschen; auf einem Bestand Neuer Ordner (17.10.2026).
 *
 * Edgar, 17.10.2026: „Mach Funktionen zum Verschieben, Löschen der Poses in
 * andere Ordner als Kontextmenü, so wie bei Animationen, Löschen, Umbenennen der
 * Ordner auch". Der Kasten ist `Kontextmenue`, das Fenster „Verschieben nach …"
 * `Ordnerwahl` — dieselben wie bei den Animationen.
 *
 * ZWEI BESTÄNDE, ZWEI BEDEUTUNGEN VON „LÖSCHEN" — deshalb nennt jede Rückfrage,
 * was geschieht:
 * - HumanBody: Datei bzw. Ordner wandern nach `HumanBody/data/poseData/.trash/`.
 * - Genesis 9: Die Daz-Bibliothek wird nie beschrieben (`G9pfade`); die Pose
 *   wird ausgeblendet (`3DObjects/models/Genesis9/posen_einteilung.json`).
 * Feste Einträge (die T-Pose des Hauptmenüs und ihr Ordner) bekommen keine
 * ändernden Einträge — der Server lehnt sie ohnehin ab (`Posenordner`).
 */
export class Posenbaummenue {

    static ENDPUNKT = '/api/character/posenbaum/verwalten/';
    static POSE_ENDPUNKT = '/api/character/pose-manage/';

    /**
     * @param umfeld `{ansicht, anwenden(pose, bestand), neuLaden(waehle), meldung(text, ok),
     *                 geaendert(bestand)}` — `geaendert` nach jeder gelungenen Aktion am Baum
     */
    constructor(umfeld) {
        this.umfeld = umfeld;
    }

    // --------------------------------------------------------------- Menüs

    pose(ereignis, pose, bestand) {
        const fest = (bestand.feste_posen || []).includes(pose.id);
        const eintraege = [{ symbol: 'fa-play', text: 'Anwenden', tun: () => this.umfeld.anwenden(pose, bestand) }];
        if (!fest) {
            eintraege.push(null);
            if (bestand.umbenennbar) {
                eintraege.push({ symbol: 'fa-pen', text: 'Umbenennen (F2)', tun: () => this.umbenennen(pose, bestand) });
            }
            eintraege.push({ symbol: 'fa-arrows-alt', text: 'Verschieben nach …',
                             tun: () => this.verschieben(pose, bestand) },
                           { symbol: 'fa-trash', text: 'Löschen (Entf)', tun: () => this.loeschen(pose, bestand) });
        }
        Kontextmenue.zeigen(ereignis.clientX, ereignis.clientY, eintraege);
    }

    ordner(ereignis, knoten, bestand) {
        const eintraege = [{ symbol: 'fa-folder-plus', text: knoten.pfad ? 'Neuer Unterordner …' : 'Neuer Ordner …',
                             tun: () => this.ordnerAnlegen(knoten, bestand) }];
        const fest = (bestand.feste_ordner || []).some((f) => f === knoten.pfad || f.startsWith(`${knoten.pfad}/`));
        if (knoten.pfad && !fest) {
            eintraege.push({ symbol: 'fa-pen', text: 'Ordner umbenennen', tun: () => this.ordnerUmbenennen(knoten, bestand) },
                           { symbol: 'fa-trash', text: 'Ordner löschen', tun: () => this.ordnerLoeschen(knoten, bestand) });
        }
        Kontextmenue.zeigen(ereignis.clientX, ereignis.clientY, eintraege);
    }

    // ------------------------------------------------------------- Posen

    async umbenennen(pose, bestand) {
        if (!bestand.umbenennbar || (bestand.feste_posen || []).includes(pose.id)) return false;
        const neu = (prompt(`Neuer Name für „${pose.name}":`, pose.name) || '').trim();
        if (!neu || neu === pose.name) return false;
        const antwort = await this._senden(Posenbaummenue.POSE_ENDPUNKT,
            { action: 'rename', category: pose.ordner, name: pose.name, new_name: neu });
        if (!antwort) return false;
        await this.umfeld.neuLaden({ bestand: bestand.kennung, id: `${pose.ordner}/${neu}` });
        this.umfeld.meldung(`„${pose.name}" heißt jetzt „${neu}".`);
        return true;
    }

    async verschieben(pose, bestand) {
        const ordner = this.umfeld.ansicht.ordnerpfade(bestand.kennung)
            .map((p) => ({ wert: p, text: p.replaceAll('/', ' › '), aktuell: p === pose.ordner }));
        const ort = pose.ordner ? pose.ordner.replaceAll('/', ' › ') : bestand.titel;
        const ziel = await Ordnerwahl.waehlen(`„${pose.name}" liegt in „${ort}"`, ordner,
                                              { neuHinweis: 'Name des neuen Ordners (Unterordner mit /)' });
        if (!ziel || ziel === pose.ordner) return false;
        const antwort = await this._aktion(bestand, 'move', { id: pose.id, target: ziel });
        if (!antwort) return false;
        await this.umfeld.neuLaden({ bestand: bestand.kennung, id: antwort.id || pose.id });
        this.umfeld.meldung(`„${pose.name}" liegt jetzt in „${antwort.ordner || ziel}".`);
        return true;
    }

    async loeschen(pose, bestand) {
        const daz = bestand.quelle === 'genesis9';
        const was = daz
            ? 'Die Pose wird ausgeblendet — die Daz-Bibliothek bleibt unverändert '
              + '(zurückholen: 3DObjects/models/Genesis9/posen_einteilung.json, „ausgeblendet").'
            : 'Die Datei wandert in den Papierkorb (HumanBody/data/poseData/.trash/).';
        if (!confirm(`„${pose.name}" aus „${pose.ordner || bestand.titel}" löschen?\n\n${was}`)) return false;
        const antwort = await this._aktion(bestand, 'delete', { id: pose.id });
        if (!antwort) return false;
        await this.umfeld.neuLaden(null);
        this.umfeld.meldung(daz ? `„${pose.name}" ausgeblendet.` : `„${pose.name}" liegt im Papierkorb (${antwort.papierkorb}).`);
        return true;
    }

    // ------------------------------------------------------------ Ordner

    async ordnerAnlegen(knoten, bestand) {
        const ort = knoten.pfad ? `in „${knoten.pfad}"` : `in ${bestand.titel}`;
        const name = (prompt(`Name des neuen Ordners ${ort}:`, '') || '').trim();
        if (!name) return false;
        const antwort = await this._aktion(bestand, 'new_folder', { parent: knoten.pfad, name });
        if (!antwort) return false;
        this.umfeld.ansicht.offen.add(`${bestand.kennung}:${knoten.pfad}`);
        await this.umfeld.neuLaden(null);
        this.umfeld.meldung(`Ordner „${antwort.pfad}" angelegt.`);
        return true;
    }

    async ordnerUmbenennen(knoten, bestand) {
        const neu = (prompt(`Neuer Name für den Ordner „${knoten.name}":`, knoten.name) || '').trim();
        if (!neu || neu === knoten.name) return false;
        const antwort = await this._aktion(bestand, 'rename_folder', { folder: knoten.pfad, new_name: neu });
        if (!antwort) return false;
        // Offen bleibt er unter dem neuen Namen — samt den offenen Ordnern darunter.
        const ansicht = this.umfeld.ansicht;
        for (const schluessel of [...ansicht.offen]) {
            const vorn = `${bestand.kennung}:${knoten.pfad}`;
            if (schluessel === vorn || schluessel.startsWith(`${vorn}/`)) {
                ansicht.offen.add(`${bestand.kennung}:${antwort.pfad}${schluessel.slice(vorn.length)}`);
            }
        }
        await this.umfeld.neuLaden(null);
        this.umfeld.meldung(`Ordner „${knoten.name}" heißt jetzt „${neu}".`);
        return true;
    }

    async ordnerLoeschen(knoten, bestand) {
        const anzahl = Posenbaumansicht.anzahl(knoten);
        const was = bestand.quelle === 'genesis9'
            ? 'Die Posen darin werden ausgeblendet — die Daz-Bibliothek bleibt unverändert.'
            : 'Der Ordner wandert in den Papierkorb (HumanBody/data/poseData/.trash/), nicht von der Platte.';
        const posen = (n) => `${n} ${n === 1 ? 'Pose' : 'Posen'}`;
        if (!confirm(`Ordner „${knoten.pfad}" mit ${posen(anzahl)} löschen?\n\n${was}`)) return false;
        const antwort = await this._aktion(bestand, 'delete_folder', { folder: knoten.pfad });
        if (!antwort) return false;
        await this.umfeld.neuLaden(null);
        this.umfeld.meldung(`Ordner „${knoten.pfad}" gelöscht (${posen(antwort.posen ?? anzahl)}).`);
        return true;
    }

    // ------------------------------------------------------------ Server

    async _aktion(bestand, aktion, daten) {
        const antwort = await this._senden(Posenbaummenue.ENDPUNKT,
                                           { bestand: bestand.kennung, action: aktion, ...daten });
        if (antwort) this.umfeld.geaendert?.(bestand);
        return antwort;
    }

    async _senden(adresse, nutzlast) {
        try {
            return (await Serverabruf.senden(adresse, nutzlast)) || {};
        } catch (fehler) {
            Protokoll.fehler('Posen', nutzlast.action, fehler);
            alert(`Fehler: ${fehler.message || fehler}`);
            return null;
        }
    }
}
