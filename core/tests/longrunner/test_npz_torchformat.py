# -*- coding: utf-8 -*-
"""torch-Format statt NPZ (13.11.2026, Edgar: „stelle doch alle npz um auf torch formate, mach einen testcase dazu der die alle überprüft und ändert“, „verschiebe alte npz damit das gleich
auffällt, behalte aber die backups“).

  * Code: kein eigener Code arbeitet an `Npztorch` vorbei mit `.npz`/`.npy` (`Npzpruefung`: numpy-Lesen/Schreiben, Dateinamen-Prüfungen, glob) — außer `AUSNAHMEN`. Sabotage: die
    Prüfung muss jedes Muster in einem Beispiel finden.
  * `Npztorch`: `.pt` schreiben, über den alten Namen lesen (gleiche Typen wie aus einer `.npz`), `datei`/`da`/`stat`/`glob`/`ersetzen`/`kopieren`/`loeschen`.
  * `Npzumstellung`: alte `.npz`/`.npy` → `.pt`, Inhalt verglichen, alte Datei in die Sicherung (an Kopien in einem eigenen Ordner unter `ProjektTemp`).
Das Umstellen der echten Dateien macht `Npzumstellung(wurzeln).aendern()` (Aufruf `ProjektTemp/_wegwerf/npz_umstellen/umstellen.py aendern <wurzel>`), nicht dieser Test — ein Test schreibt
nie in Produktivdaten (`tests-und-produktivdaten`). Er meldet aber jede alte Datei, die noch unter den Datenwurzeln liegt (`test_keine_alten_dateien`, nur Zählung).
"""
import shutil
import sys
import unittest
from pathlib import Path

import torch
from django.conf import settings

W = Path(settings.TOOLS_ROOT)
if str(W) not in sys.path:
    sys.path.insert(0, str(W))
from KoerperKI_alle.npzpruefung import Npzpruefung  # noqa: E402
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402
from KoerperKI_alle.npzumstellung import Npzumstellung  # noqa: E402

CODE = ['meshgenesis', 'KoerperKI_alle', 'KoerperKI_Fotos', 'KopfKI', 'HaarKI', 'Genesis9', 'HumanBodyWeb/core', 'HumanBodyWeb/ui', 'pshuman_port14', 'Kleidung', 'Sapiens2Torch',
        'Sam3Torch', 'VitposeTorch', 'Sam3dbodyTorch', 'MediapipeTorch', 'InsightfaceTorch', 'EconTorch', 'Sapiens2Normalen', 'fotogenesis', 'Figurfilm', 'koerper_eigen', 'meshto3d']
#: bewusst NPZ: Npztorch und seine Werkzeuge; Tests, die alte .npz als Eingang anlegen (Npztorch liest beide)
AUSNAHMEN = ('KoerperKI_alle/npztorch.py', '/tests/')
#: Wurzeln, deren Dateien umgestellt sein sollen (Zählung)
DATEN = ['3DObjects/meshgenesis', '3DObjects/fotogenesis', 'Genesis9', '3DObjects/models/Genesis9', '3DObjects/blendimport', '3DObjects/meshfigurauftraege']   # Welle 2: 13.11.2026 abends
ORDNER = W / 'ProjektTemp' / '_test_npz_torchformat'
N = 'n' + 'p'           # Beispielcode für die Sabotage, ohne dass der numpy-Hook ihn als eigenen Code liest


class NpzTorchformatTest(unittest.TestCase):
    def setUp(self):
        if ORDNER.exists():
            shutil.rmtree(ORDNER)
        ORDNER.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, ORDNER, ignore_errors=True)

    def test_kein_code_an_npztorch_vorbei(self):
        wurzeln = [str(W / c) for c in CODE]
        befunde = [b for b in Npzpruefung.pruefen(wurzeln) + Npzpruefung.parameter(wurzeln) if not any(a in b[0].replace('\\', '/') for a in AUSNAHMEN) and '_wegwerf' not in b[0]]
        self.assertEqual([], ['%s:%d [%s] %s' % b for b in befunde])

    def test_sabotage_parameter(self):
        (ORDNER / 'beispiel_parameter.py').write_text('from pathlib import Path\n\nclass Lager:\n    @staticmethod\n    def da(pfad):\n        return pfad.is_file()\n\n'
                                                      'Lager.da(Path("a") / "netz.npz")\n', encoding='utf-8')
        self.assertEqual([b[2] for b in Npzpruefung.parameter([str(ORDNER)])], ['parameter'])

    def test_sabotage_pruefung_findet_jedes_muster(self):
        beispiel = ORDNER / 'beispiel.py'
        beispiel.write_text('import os, shutil\nfrom pathlib import Path\nziel = Path("a") / "netz.npz"\n'
                            'x = %s.load(ziel)\nif ziel.is_file():\n    pass\nos.path.getmtime(ziel)\nshutil.copy2(ziel, "b.npz")\nlist(Path("a").glob("*.npz"))\n'
                            '%s.savez("c.npz", a=1)\n' % (N, N), encoding='utf-8')
        arten = sorted(art for _z, art, _t in Npzpruefung.datei(beispiel))
        self.assertEqual(arten, ['muster', 'numpy', 'numpy', 'pfad', 'pfad', 'pfad'])

    def test_sabotage_uebergabe(self):
        """Ein Pfad, den `Npztorch.speichern` schreibt und der in einen Auftrag geht (Wert, Argumentliste, Methode im Auftrag), braucht `fuer_numpy=True` oder einen Vermerk
        (13.11.2026: Blender- und Stoffsolver-Aufträge kamen als `.pt` an)."""
        kopf = 'from KoerperKI_alle.npztorch import Npztorch\n\nclass Auftrag:\n'
        roh = (kopf + '    def schreiben(self, stamm):\n        Npztorch.speichern(str(stamm) + "_k.npz", a=1%s)\n        return {"koerper": str(stamm) + "_k.npz"}\n\n'
               '    def lage(self):\n        Npztorch.speichern_npy(self.ablage.arbeit("l.npy"), 1%s)\n        return ["--lage", self.ablage.arbeit("l.npy")]\n\n'
               '    def haut(self):\n        pfad = self.ordner / "h.npz"\n        Npztorch.speichern(pfad, a=1%s)\n        return pfad\n\n'
               '    def brief(self):\n        auftrag = {}\n        auftrag["koerper"] = str(self.haut())\n        return auftrag\n')
        (ORDNER / 'ohne.py').write_text(roh % ('', '', ''), encoding='utf-8')
        (ORDNER / 'mit.py').write_text(roh % ((', fuer_numpy=True',) * 3), encoding='utf-8')
        self.assertEqual([art for _z, art, _t in Npzpruefung.datei(ORDNER / 'ohne.py')], ['uebergabe'] * 3)
        self.assertEqual(Npzpruefung.datei(ORDNER / 'mit.py'), [])
        # kein Auftrag: Formattupel, Entpacken, gleichnamige Variable in einer anderen Funktion
        (ORDNER / 'frei.py').write_text(kopf + '    def a(self, ziel):\n        Npztorch.speichern(ziel, a=1)\n        print("%s %s" % (ziel, 1))\n        x, y = ziel, 2\n\n'
                                        '    def b(self, ziel):\n        return [ziel]\n', encoding='utf-8')
        self.assertEqual(Npzpruefung.datei(ORDNER / 'frei.py'), [])

    def test_sabotage_fremdleser(self):
        """Ein .npz-Pfad, der an `humanbody_core` geht (liest numpy selbst), und ein Name aus einer Methode, die einen .npz-Text zurückgibt (13.11.2026: `G9unterteilung._laden` —
        die umgestellten Unterteiler griffen nicht mehr). Gegenprobe: derselbe Aufruf an ein Modul mit torch ist kein `fremd`; Daten aus einer .npz sind kein Pfad."""
        roh = ('from pathlib import Path\nfrom %s import Unterteilungsbau\n\nclass Ablage:\n    @staticmethod\n    def _dateiname(s):\n        return "unterteilung_s%%d.npz" %% s\n\n'
               '    def laden(self, s):\n        pfad = Path("a") / self._dateiname(s)\n        if not pfad.is_file():%s\n            return None\n'
               '        return Unterteilungsbau.laden(pfad)%s\n\n    def daten(self):\n        d = Unterteilungsbau.lesen(Path("a") / "x.npz")%s\n        return Unterteilungsbau.netz(d)\n')
        (ORDNER / 'fremd.py').write_text(roh % ('humanbody_core.unterteilungsbau', '', '', ''), encoding='utf-8')
        (ORDNER / 'vermerkt.py').write_text(roh % (('humanbody_core.unterteilungsbau',) + ('  # npz geprüft: humanbody_core',) * 3), encoding='utf-8')
        (ORDNER / 'mit_torch.py').write_text(roh % ('KoerperKI_alle.unterteilung', '', '', ''), encoding='utf-8')
        self.assertEqual(sorted(art for _z, art, _t in Npzpruefung.datei(ORDNER / 'fremd.py')), ['fremd', 'fremd', 'pfad'])
        self.assertEqual(Npzpruefung.datei(ORDNER / 'vermerkt.py'), [])
        self.assertEqual([art for _z, art, _t in Npzpruefung.datei(ORDNER / 'mit_torch.py')], ['pfad'])

    def test_fuer_numpy_schreibt_npz(self):
        alt = Npztorch.TORCH_SCHREIBEN
        Npztorch.TORCH_SCHREIBEN = True
        self.addCleanup(setattr, Npztorch, 'TORCH_SCHREIBEN', alt)
        punkte = torch.arange(6, dtype=torch.float32, device='cuda').reshape(2, 3)
        self.assertEqual(Npztorch.speichern(ORDNER / 'auftrag.npz', punkte=punkte, fuer_numpy=True), ORDNER / 'auftrag.npz')
        self.assertEqual(Npztorch.speichern_npy(ORDNER / 'lage.npy', punkte, fuer_numpy=True), ORDNER / 'lage.npy')
        self.assertEqual(sorted(p.name for p in ORDNER.iterdir()), ['auftrag.npz', 'lage.npy'])
        self.assertEqual((ORDNER / 'auftrag.npz').read_bytes()[:2], b'PK')                  # Zip wie numpys savez
        self.assertEqual((ORDNER / 'lage.npy').read_bytes()[:6], Npztorch.MAGIC)
        self.assertTrue(torch.equal(Npztorch.lesen(ORDNER / 'auftrag.npz')['punkte'], punkte))

    def test_npztorch_torchformat(self):
        alt = Npztorch.TORCH_SCHREIBEN
        Npztorch.TORCH_SCHREIBEN = True
        self.addCleanup(setattr, Npztorch, 'TORCH_SCHREIBEN', alt)
        name = ORDNER / 'netz.npz'
        punkte = torch.arange(12, dtype=torch.float32, device='cuda').reshape(4, 3)
        geschrieben = Npztorch.speichern(name, punkte=punkte, zahl=3, text='abc', namen=['a', 'b'])
        self.assertEqual(geschrieben, ORDNER / 'netz.pt')
        self.assertFalse(name.exists())
        d = Npztorch.lesen(name)
        self.assertTrue(torch.equal(d['punkte'], punkte))
        self.assertEqual((d['zahl'].dtype, int(d['zahl'])), (torch.int64, 3))
        self.assertEqual((d['text'], list(d['namen'])), ('abc', ['a', 'b']))
        self.assertTrue(Npztorch.da(name))
        self.assertEqual(Npztorch.datei(name), ORDNER / 'netz.pt')
        self.assertEqual(Npztorch.stat(name).st_size, (ORDNER / 'netz.pt').stat().st_size)
        self.assertEqual(list(Npztorch.glob(ORDNER, '*.npz')), [name])
        Npztorch.kopieren(name, ORDNER / 'kopie.npz')
        self.assertTrue((ORDNER / 'kopie.pt').is_file())
        Npztorch.ersetzen(ORDNER / 'kopie.npz', ORDNER / 'weg.npz')
        self.assertEqual(sorted(p.name for p in ORDNER.glob('*.pt')), ['netz.pt', 'weg.pt'])
        Npztorch.loeschen(ORDNER / 'weg.npz')
        self.assertFalse(Npztorch.da(ORDNER / 'weg.npz'))
        with self.assertRaises(FileNotFoundError):
            Npztorch.stat(ORDNER / 'weg.npz')

    def test_umstellung_mit_sicherung(self):
        alt = ORDNER / 'daten' / 'alt.npz'
        alt.parent.mkdir()
        schalter = Npztorch.TORCH_SCHREIBEN
        Npztorch.TORCH_SCHREIBEN = False
        try:
            Npztorch.speichern(alt, a=torch.arange(5, device='cuda'), b='text')
        finally:
            Npztorch.TORCH_SCHREIBEN = schalter
        self.assertTrue(alt.is_file())
        nur = ORDNER / 'daten' / 'nur_numpy.npz'          # Muster aus `NUR_NUMPY` je Datei (Unterteiler, die humanbody_core selbst liest) — bleibt, wie es ist
        shutil.copy2(alt, nur)

        class Umstellung(Npzumstellung):
            NUR_NUMPY = (ORDNER.relative_to(W).as_posix() + '/daten/nur_*',)
        u = Umstellung([ORDNER / 'daten'])
        u.SICHERUNG = ORDNER / 'sicherung'
        zaehler, befunde = u.aendern()
        self.assertEqual((zaehler['umgestellt'], befunde), (1, []))
        self.assertEqual((nur.is_file(), nur.with_suffix('.pt').exists()), (True, False))
        self.assertFalse(alt.exists())
        self.assertTrue((ORDNER / 'sicherung' / alt.relative_to(W)).is_file())
        d = Npztorch.lesen(alt)
        self.assertEqual((d['a'].tolist(), d['b']), ([0, 1, 2, 3, 4], 'text'))

    def test_keine_alten_dateien(self):
        """Nur Zählung: alte .npz/.npy unter den Datenwurzeln (nach `umstellen.py aendern` leer, außer Befunden der Umstellung)."""
        rest = [str(p) for p in Npzumstellung.dateien([W / d for d in DATEN])][:20]
        self.assertEqual([], rest)


if __name__ == '__main__':
    unittest.main()
