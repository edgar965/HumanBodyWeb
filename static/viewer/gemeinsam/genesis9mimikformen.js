/**
 * Genesis9mimikformen — MB-Lab-Einheiten (Mimik-/Script-Spur, `Mimikbasis`)
 * als Genesis-9-Reglerstellungen (`Genesis9/mimik.py`, Gruppe `mimik`).
 *
 * ANLASS (22.09.2026, Edgar: „ich hatte das ALLES in Auftrag gegeben" — Mimik
 * UND Script sollten auf Genesis 9 wirken, nicht nur Lipsync): Bis dahin ging
 * nur `visemes` durch (`Mimikanwendung.anwenden` warf `gewichte` für
 * Genesis-9-Figuren weg). Diese Tabelle ist das Gegenstück zu
 * `Lipsyncformen.GENESIS9`, nur für die 42 MB-Lab-Einheiten statt der
 * Rhubarb-Mundformen.
 *
 * Wie bei `Lipsyncformen`: Augenmaß, keine Messung — ein plausibler Daz-Kanal
 * je Einheit, keine Eins-zu-eins-Übersetzung. Bewusst NICHT abgedeckt (kein
 * einigermaßen sicherer Daz-Kanal gefunden, oder nur ein BEIDSEITIGER
 * -1…1-Kanal, dessen negative Richtung `Genesis9/mimik.py` nicht bäckt —
 * siehe dort): `deglutition`, `pupilsDilatation`, `mouthChew`, `tongueOut`,
 * `tongueOutPressure`, `tongueTipUp`, `jawOut`, `jawHoriz`, `mouthHoriz`,
 * `eyesHoriz`, `eyesVert`. Diese Einheiten bleiben auf Genesis 9 wirkungslos
 * — nicht stumm falsch, sondern ehrlich nicht abgebildet.
 *
 * Struktur wie `Mimikbasis.basis`: `{einheit: {plus: {kanal: gewicht},
 * minus: {kanal: gewicht}}}` — `plus` bei positivem MB-Lab-Gewicht, `minus`
 * bei negativem (`uebersetzen()` mischt wie `Mimikbasis.bewegungen`).
 */
export class Genesis9mimikformen {
    static TABELLE = {
        mouthSmileL: { plus: { facs_ctrl_MouthSmile: 0.6, facs_ctrl_MouthDimple: 0.3 },
                       minus: { facs_ctrl_MouthFrown: 0.6 } },
        mouthSmileR: { plus: { facs_ctrl_MouthSmile: 0.6, facs_ctrl_MouthDimple: 0.3 },
                       minus: { facs_ctrl_MouthFrown: 0.6 } },
        mouthSmile: { plus: { facs_ctrl_MouthSmile: 1.0 }, minus: { facs_ctrl_MouthFrown: 1.0 } },
        mouthSmileOpen: { plus: { facs_ctrl_MouthSmile: 0.8, facs_ctrl_vAA: 0.3 } },
        mouthSmileOpen2: { plus: { facs_ctrl_MouthSmile: 1.0, facs_ctrl_vAA: 0.5,
                                    facs_ctrl_MouthSmileWiden: 0.4 } },
        mouthClosed: { plus: { facs_ctrl_MouthClose: 1.0 } },
        mouthOpen: { plus: { facs_ctrl_vAA: 0.7 } },
        mouthOpenHalf: { plus: { facs_ctrl_vAA: 0.4 } },
        mouthOpenLarge: { plus: { facs_ctrl_vAA: 0.9, facs_ctrl_MouthStretch: 0.3 } },
        mouthOpenAggr: { plus: { facs_ctrl_vAA: 1.0, facs_ctrl_MouthStretch: 0.5 } },
        mouthOpenO: { plus: { facs_ctrl_vOW: 0.8, facs_ctrl_MouthPucker: 0.3 } },
        mouthOpenTeethClosed: { plus: { facs_ctrl_vAA: 0.25, facs_ctrl_MouthClose: 0.2 } },
        mouthInflated: { plus: { facs_ctrl_CheekPuff: 1.0 } },
        mouthLowerOut: { plus: { facs_ctrl_MouthShrugLower: 0.7, facs_ctrl_MouthLowerDown: 0.3 } },
        mouthBite: { plus: { facs_ctrl_MouthPress: 0.6, facs_ctrl_JawClench: 0.4 } },

        browsMidVert: { plus: { facs_ctrl_BrowUp: 1.0 }, minus: { facs_ctrl_BrowDown: 1.0 } },
        browOutVertL: { plus: { facs_ctrl_BrowUp: 0.6 }, minus: { facs_ctrl_BrowDown: 0.6 } },
        browOutVertR: { plus: { facs_ctrl_BrowUp: 0.6 }, minus: { facs_ctrl_BrowDown: 0.6 } },
        browSqueezeL: { plus: { facs_ctrl_BrowSqueeze: 1.0 } },
        browSqueezeR: { plus: { facs_ctrl_BrowSqueeze: 1.0 } },

        eyeClosedL: { plus: { facs_ctrl_EyeFullCompressionLeft: 1.0 } },
        eyeClosedR: { plus: { facs_ctrl_EyeFullCompressionRight: 1.0 } },
        eyeClosedPressureL: { plus: { facs_ctrl_EyeFullCompressionLeft: 1.0 } },
        eyeClosedPressureR: { plus: { facs_ctrl_EyeFullCompressionRight: 1.0 } },
        eyeSquintL: { plus: { facs_ctrl_EyesSquint: 0.7 } },
        eyeSquintR: { plus: { facs_ctrl_EyesSquint: 0.7 } },

        cheekSneerL: { plus: { facs_ctrl_NoseSneer: 0.7, facs_ctrl_CheekSquint: 0.5 } },
        cheekSneerR: { plus: { facs_ctrl_NoseSneer: 0.7, facs_ctrl_CheekSquint: 0.5 } },
        nostrilsExpansion: { plus: { facs_ctrl_NasalFlare: 1.0 } },

        tongueVert: { plus: { facs_ctrl_TongueUp: 1.0 } },
        tongueHoriz: { plus: { facs_ctrl_TongueRight: 1.0 }, minus: { facs_ctrl_TongueLeft: 1.0 } },
    };

    /**
     * MB-Lab-Gewichte (`{einheit: -1…1}`) -> Genesis-9-Reglergewichte
     * (`{kanal: 0…1}`), analog zu `Mimikbasis.bewegungen`: positive Gewichte
     * nehmen `plus`, negative `minus`, mehrere Einheiten auf demselben Kanal
     * addieren sich (auf 1 geklemmt — Daz' Kanäle sind 0…1).
     */
    static uebersetzen(gewichte) {
        /** @type {Object<string, number>} */
        const aus = {};
        for (const [einheit, g] of Object.entries(gewichte || {})) {
            const eintrag = Genesis9mimikformen.TABELLE[einheit];
            if (!eintrag || !g) continue;
            const richtung = g > 0 ? eintrag.plus : eintrag.minus;
            if (!richtung) continue;
            const betrag = Math.min(1, Math.abs(g));
            for (const [kanal, w] of Object.entries(richtung)) {
                aus[kanal] = Math.min(1, (aus[kanal] || 0) + w * betrag);
            }
        }
        return aus;
    }
}
