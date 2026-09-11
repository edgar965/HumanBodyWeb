import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Posenabsatz — der Absatzschuh als Teil der Pose einer Figur.
 *
 * WARUM (Edgar, 11.09.2026: „der Betrachter soll bei einem Absatzschuh gar
 * nichts tun, sondern das Programm soll die Pose ändern!"): Die Beugung
 * rechnet der Server in jede Pose hinein (`core/dienste/absatzpose.py`,
 * `GET /api/character/pose/<id>/?winkel_grad=…`). Hier steht nur, WAS die
 * Figur gerade trägt (`figur.absatz`), damit jede Pose — auch die
 * Ruhelage — mit diesen Zahlen geholt wird, und der Hub, den eine Pose
 * nicht ausdrücken kann: `hebung_m` hebt die Figurgruppe, damit die Zehen
 * auf dem Boden bleiben. `Character._lage` zieht ihn beim Speichern ab.
 *
 * `figur.absatz` = `{winkel_grad, sprengung_grad, hebung_cm, plateau_cm,
 * quelle}` oder null; `quelle` sagt, ob die Zahlen vom getragenen Schuh
 * (`schuh:<stueck>`) oder von den Reglern (`regler`) kommen.
 */
export class Posenabsatz {

    static FELDER = ['winkel_grad', 'sprengung_grad', 'hebung_cm', 'plateau_cm'];

    /** Trägt diese Figur einen Absatz? */
    static aktiv(figur) {
        const a = figur?.absatz;
        return !!a && (a.winkel_grad > 0 || a.sprengung_grad > 0);
    }

    /** Die Abfrage für `/api/character/pose/<id>/` — Absatz und Skelett. */
    static abfrage(figur) {
        const teile = [];
        const koerpertyp = figur?.bodyType || figur?.body_type;
        if (koerpertyp) teile.push(`body_type=${encodeURIComponent(koerpertyp)}`);
        if (Posenabsatz.aktiv(figur)) {
            for (const feld of Posenabsatz.FELDER) {
                teile.push(`${feld}=${encodeURIComponent(figur.absatz[feld] || 0)}`);
            }
        }
        return teile.length ? `?${teile.join('&')}` : '';
    }

    /** Die Figur um den Hub der Pose heben (oder wieder senken). */
    static heben(figur, hebungM) {
        const bisher = figur.group.userData.absatzHub || 0;
        const hub = Number(hebungM) || 0;
        figur.group.position.y += hub - bisher;
        figur.group.userData.absatzHub = hub;
        if (hub !== bisher) {
            Protokoll.info('Pose', hub
                ? `Absatz: Figur steht ${(hub * 100).toFixed(1)} cm höher`
                : 'Absatz abgesetzt: Figur steht wieder flach');
        }
    }

    /**
     * Den Absatz einer Figur setzen (oder mit null nehmen) und ihre Pose
     * neu vom Server holen — die trägt die Beugung dann mit. `stellen` ist
     * `Posenanwendung.vomServer`, hereingereicht, damit die beiden Module
     * einander nicht im Kreis importieren.
     */
    static async setzen(figur, info, stellen) {
        const neu = info ? { ...info } : null;
        const gleich = JSON.stringify(Posenabsatz._zahlen(figur.absatz))
            === JSON.stringify(Posenabsatz._zahlen(neu));
        figur.absatz = neu;
        if (gleich && !figur.absatzOffen) return { ok: true, unveraendert: true };
        figur.absatzOffen = true;
        const ergebnis = await stellen(figur.poseId || 'ruhelage', figur);
        if (ergebnis.ok) figur.absatzOffen = false;
        else Protokoll.warnung('Pose', `Absatz nicht gestellt: ${ergebnis.grund}`);
        return ergebnis;
    }

    static _zahlen(info) {
        if (!info || !(info.winkel_grad > 0 || info.sprengung_grad > 0)) return null;
        return Posenabsatz.FELDER.map((f) => Number(info[f] || 0).toFixed(3));
    }
}
