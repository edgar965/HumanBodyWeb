import * as THREE from 'three';
import { sharedState } from '../character_core.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';
import { UmaModell } from '../gemeinsam/umamodell.js';
import { MakehumanModell } from '../gemeinsam/makehumanmodell.js';
import { SmplModell } from '../gemeinsam/smplmodell.js';
import { UmapythonModell } from '../gemeinsam/umapythonmodell.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';

/**
 * Spurfigurarten — welche Modellklasse die Figur einer Spur baut.
 *
 * Edgar, 15.09.2026: „bei Modell hinzufügen, mach das unterteilt, in
 * HumanBody, UMA, MakeHuman usw". Bis dahin baute das Studio nur das
 * HumanBody-Netz (`Spurfigur` → `HumanbodyModell`). Jetzt trägt die
 * Bewegungsspur neben `preset` eine `quelle`, und hier steht je Quelle, wie
 * das Modell entsteht — dieselben Klassen wie in der Szene
 * (`gemeinsam/modell.js`: „EINE Klasse mit bauen()").
 *
 * Was dem Studio je Art wichtig ist:
 * - `mischerWurzel`: HumanBody hängt sein Skelett am Netz, die anderen an der
 *   Figurgruppe (`Knochenbau`, GLB-Szene) — dort muss der Mischer laufen.
 * - `ruhelage`: UMA darf NICHT `skeleton.pose()` (Bindpose der GLB, A-Pose
 *   entlang −Z); es hat `ruhelageHerstellen()`.
 * - `hoehe`: über die Knochen, nicht über die Box des Netzes — ein
 *   SkinnedMesh meldet die Ruhe-Box, nicht die Figur.
 */
export class Spurfigurarten {

    static VORGABE = 'modell';

    /** Quelle → Modell bauen. Jede liefert das gebaute Modell. */
    static BAUER = {
        async modell(spur, beiKoerper) {
            const vorgabe = await Serverabruf.json('/api/character/model/'
                + encodeURIComponent(spur.preset) + '/');
            spur.modelData = vorgabe;             // Export1 liest `bone_parts` von hier
            spur.bodyType = vorgabe.body_type || spur.bodyType || HumanbodyModell.VORGABE_KOERPERART;
            const modell = new HumanbodyModell(spur.name, { ...vorgabe, body_type: spur.bodyType });
            await modell.bauen({
                skelettdaten: sharedState.rigifySkeletonData,
                gewichte: sharedState.skinWeightData,
                hautfarben: sharedState.skinColors,
                haarfarben: sharedState.hairColorData,
                beiKoerper,
            });
            return modell;
        },
        async uma(spur, beiKoerper) {
            const modell = new UmaModell(spur.name, { datei: spur.preset });
            await modell.bauen();
            beiKoerper(modell);
            return modell;
        },
        async makehuman(spur, beiKoerper) {
            const modell = new MakehumanModell(spur.name, { modell: spur.preset });
            await modell.bauen();
            beiKoerper(modell);
            return modell;
        },
        async smpl(spur, beiKoerper) {
            const modell = new SmplModell(spur.name, { koerper: spur.preset });
            await modell.bauen();
            beiKoerper(modell);
            return modell;
        },
        async umapython(spur, beiKoerper) {
            const modell = new UmapythonModell(spur.name, { rasse: spur.preset });
            await modell.bauen();
            beiKoerper(modell);
            return modell;
        },
        async genesis9(spur, beiKoerper) {
            const modell = new Genesis9Modell(spur.name, { figur: spur.preset });
            await modell.bauen();
            beiKoerper(modell);
            return modell;
        },
    };

    static quelle(spur) {
        return Spurfigurarten.BAUER[spur.quelle] ? spur.quelle : Spurfigurarten.VORGABE;
    }

    /** Das Modell der Spur bauen; `beiKoerper(modell)` setzt es in die Spur. */
    static async bauen(spur, beiKoerper) {
        spur.modelData = null;
        return Spurfigurarten.BAUER[Spurfigurarten.quelle(spur)](spur, beiKoerper);
    }

    /** Worauf der Mischer läuft: HumanBody auf dem Netz, alle anderen auf der Gruppe. */
    static mischerWurzel(spur) {
        return Spurfigurarten.quelle(spur) === 'modell' ? spur.mesh : spur.group;
    }

    /** Zurück in die Ruhelage — je Art anders. */
    static ruhelage(spur) {
        if (spur.modell?.ruhelageHerstellen) spur.modell.ruhelageHerstellen();
        else if (spur.skeleton?.skeleton) spur.skeleton.skeleton.pose();
    }

    /** Körperhöhe über die Knochen (m) — 0, wenn es keine gibt. */
    static hoehe(skelett) {
        const bones = skelett?.bones || skelett?.skeleton?.bones || [];
        const punkt = new THREE.Vector3();
        let unten = Infinity, oben = -Infinity;
        for (const bone of bones) {
            bone.getWorldPosition(punkt);
            unten = Math.min(unten, punkt.y);
            oben = Math.max(oben, punkt.y);
        }
        return oben > unten ? oben - unten : 0;
    }
}
