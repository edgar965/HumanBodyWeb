# -*- coding: utf-8 -*-
"""Modell aus Bildern — die drei Boxen je Bild, Ersetzen/Löschen, Sichtung nur neuer Dateien, Lauf bis.

Edgar (19.09.2026): „Mach in jeder Zeile einen Button zum Bild hochladen …
und eines zum Bild löschen … Erste Combo Box: Hauptbild-Typ, zweite
Nebenbild-Typ, dritte nur Textur?"

Ohne Daz-Bibliothek und ohne Schätzer: Attrappen und Kunstdaten in
`ProjektTemp/pruefungen` (`Pruefablage`, nie auf C:).
"""

import io
import json
import unittest

from django.test import Client, TestCase, override_settings

from core.daten.bildmodellablage import Bildmodellablage
from core.dienste.bildmodellbildtypen import Bildmodellbildtypen as T
from core.dienste.bildmodelldateien import Bildmodelldateien
from core.dienste.bildmodellsichtung import Bildmodellsichtung
from core.dienste.bildmodelltextur import Bildmodelltextur
from core.models import Bildmodellauftrag

from ._pruefablage import Pruefablage


class BildtypenTest(unittest.TestCase):
    def test_hauptbild_setzt_kategorie_ansicht_und_gewicht(self):
        e = {'datei': 'a.jpg', 'kategorie': 'neben', 'teil': 'haende', 'gewicht': 0.0}
        self.assertTrue(T.stellen(e, {'haupt': 'kopf/seite'}))
        self.assertEqual((e['kategorie'], e['ansicht'], e['gewicht']), ('kopf', 'seite', 1.0))
        self.assertNotIn('teil', e, 'ein Hauptbild hat kein Nebenbild-Teil')
        self.assertTrue(e['manuell'])
        self.assertEqual(T.haupt(e), 'kopf/seite')
        self.assertEqual(T.neben(e), '')
        # „kein Hauptbild" macht aus dem Körperbild ein Nebenbild
        T.stellen(e, {'haupt': ''})
        self.assertEqual(e['kategorie'], 'neben')
        self.assertEqual(T.neben(e), 'neben')

    def test_nebenbild_mit_teil_und_ohne(self):
        e = {'datei': 'a.jpg', 'kategorie': 'koerper', 'ansicht': 'vorne', 'gewicht': 1.0}
        T.stellen(e, {'neben': 'neben/oberkoerper'})
        self.assertEqual((e['kategorie'], e['teil']), ('neben', 'oberkoerper'))
        self.assertEqual(T.neben(e), 'neben/oberkoerper')
        self.assertEqual(T.textur_teile(e), ('hals', 'rumpf', 'l_schulter', 'r_schulter'))
        T.stellen(e, {'neben': 'gruppe'})
        self.assertEqual(e['kategorie'], 'gruppe')
        self.assertNotIn('teil', e)
        T.stellen(e, {'neben': ''})
        self.assertEqual(e['kategorie'], 'leer', '„kein Nebenbild" = ohne Befund')
        self.assertFalse(T.stellen(e, {'neben': 'quatsch'}), 'Unbekanntes wird nicht gestellt')

    def test_nutzung_entscheidet_form_und_textur(self):
        e = {'kategorie': 'koerper', 'gewicht': 1.0, 'textur': {'hautton': [1, 2, 3], 'tauglich': True}}
        self.assertTrue(T.fuer_form(e) and T.fuer_textur(e) and Bildmodelltextur.gewaehlt(e))
        T.stellen(e, {'nutzung': 'textur'})
        self.assertFalse(T.fuer_form(e), '„nur Textur" zählt nicht für die Form')
        self.assertTrue(Bildmodelltextur.gewaehlt(e))
        T.stellen(e, {'nutzung': 'form'})
        self.assertTrue(T.fuer_form(e))
        self.assertFalse(Bildmodelltextur.gewaehlt(e), '„nur Form" liefert keine Haut')
        T.stellen(e, {'nutzung': 'aus'})
        self.assertFalse(T.fuer_form(e) or T.fuer_textur(e) or T.fuer_haende(e))
        # Sabotage-Gegenprobe: Gewicht 0 zählt nie für die Form.
        e2 = {'kategorie': 'koerper', 'gewicht': 0.0}
        self.assertFalse(T.fuer_form(e2))
        # Nebenbild mit Teil und Hautton gilt als gewählt, ohne Teil nur mit Häkchen.
        n = {'kategorie': 'neben', 'teil': 'ruecken', 'textur': {'hautton': [1, 2, 3], 'tauglich': False}}
        self.assertTrue(Bildmodelltextur.gewaehlt(n))
        self.assertFalse(Bildmodelltextur.gewaehlt({'kategorie': 'neben', 'textur': {'hautton': [1, 2, 3]}}))
        self.assertTrue(T.fuer_haende({'kategorie': 'neben', 'teil': 'haende'}))
        self.assertFalse(T.fuer_haende(n), 'ein Rückenbild liefert keine Finger')

    def test_katalog(self):
        k = T.katalog()
        self.assertEqual(set(k), {'haupt', 'neben', 'nutzung'})
        self.assertIn('koerper/dreiviertel', [e['wert'] for e in k['haupt']])
        self.assertIn('neben/fuesse', [e['wert'] for e in k['neben']])
        self.assertEqual([e['wert'] for e in k['nutzung']], ['form_textur', 'form', 'textur', 'aus'])
        from Genesis9.koerperteile import G9koerperteile

        for teile in T.TEILE.values():
            for t in teile:
                self.assertIn(t, G9koerperteile.TEILE, t)


class _Job:
    kennung = 'pruef'

    def __init__(self, bilder):
        self.bilder = bilder
        self.gespeichert = 0

    def bild(self, datei):
        return next((b for b in self.bilder if b.get('datei') == datei), None)

    def save(self, **_):
        self.gespeichert += 1


class _Upload:
    def __init__(self, name, inhalt=b'neu'):
        self.name = name
        self._inhalt = inhalt

    def chunks(self):
        yield self._inhalt


class DateienTest(unittest.TestCase):
    # `Bildmodellablage.wurzel()` liest OBJECTS_ROOT bei JEDEM Aufruf — der Block bleibt offen.
    @staticmethod
    def _ablage():
        a = Bildmodellablage('pruef')
        a.anlegen()
        return a

    def test_bild_loeschen_nimmt_original_nur_ohne_geschwister(self):
        with Pruefablage.ordner('bm_dateien_') as ordner, override_settings(OBJECTS_ROOT=ordner):
            a = self._ablage()
            (a.original() / 'foto.jpg').write_bytes(b'x')
            for n in ('foto_z1.jpg', 'foto_z2.jpg'):
                (a.zuschnitt() / n).write_bytes(b'x')
            (a.schaetzung() / 'foto_z1_posed.npy').write_bytes(b'x')
            job = _Job([
                {'datei': 'foto_z1.jpg', 'quelle': 'foto.jpg',
                 'schaetzung': {'posed_vertices_path': 'foto_z1_posed.npy'}},
                {'datei': 'foto_z2.jpg', 'quelle': 'foto.jpg'},
            ])
            d = Bildmodelldateien(job, a)
            self.assertFalse(d.bild_entfernen('foto_z1.jpg'), 'z2 braucht das Original noch')
            self.assertTrue((a.original() / 'foto.jpg').is_file())
            self.assertFalse((a.zuschnitt() / 'foto_z1.jpg').exists())
            self.assertFalse((a.schaetzung() / 'foto_z1_posed.npy').exists(), 'Schätzernetz geht mit')
            self.assertEqual([b['datei'] for b in job.bilder], ['foto_z2.jpg'])
            self.assertTrue(d.bild_entfernen('foto_z2.jpg'), 'der letzte Ausschnitt nimmt das Original mit')
            self.assertFalse((a.original() / 'foto.jpg').exists())
            self.assertEqual(job.bilder, [])
            self.assertFalse(d.bild_entfernen('gibtsnicht.jpg'))

    def test_original_ersetzen_und_ohne_befund(self):
        with Pruefablage.ordner('bm_dateien_') as ordner, override_settings(OBJECTS_ROOT=ordner):
            a = self._ablage()
            (a.original() / 'foto.jpg').write_bytes(b'alt')
            (a.original() / 'anderes.png').write_bytes(b'x')
            (a.zuschnitt() / 'foto_z1.jpg').write_bytes(b'x')
            job = _Job([{'datei': 'foto_z1.jpg', 'quelle': 'foto.jpg'}])
            d = Bildmodelldateien(job, a)
            self.assertEqual(d.ohne_befund(), ['anderes.png'])
            neu = d.original_ersetzen('foto.jpg', _Upload('Mein Bild.PNG', b'neu'))
            self.assertEqual(neu, 'foto.png', 'Stamm bleibt, Endung vom Upload')
            self.assertEqual((a.original() / 'foto.png').read_bytes(), b'neu')
            self.assertFalse((a.original() / 'foto.jpg').exists())
            self.assertFalse((a.zuschnitt() / 'foto_z1.jpg').exists())
            self.assertEqual(job.bilder, [], 'Einträge der alten Datei sind weg')
            self.assertEqual(sorted(d.ohne_befund()), ['anderes.png', 'foto.png'])
            self.assertEqual(d.original_entfernen('anderes.png'), 0)
            self.assertFalse((a.original() / 'anderes.png').exists())


class SichtungUmfangTest(unittest.TestCase):
    def test_nur_neue_dateien_oder_fehlendes_rig(self):
        with Pruefablage.ordner('bm_umfang_') as ordner, override_settings(OBJECTS_ROOT=ordner):
            a = Bildmodellablage('pruef')
            a.anlegen()
            for n in ('a.jpg', 'b.jpg', 'c.jpg', 'd.jpg'):
                (a.original() / n).write_bytes(b'x')
            job = _Job([
                {'datei': 'a_z1.jpg', 'quelle': 'a.jpg', 'kategorie': 'koerper', 'gewicht': 1.0,
                 'rigs': {'yolo': {}, 'openpifpaf': {}, 'vitpose': {}}, 'textur': {}},
                {'datei': 'b_z1.jpg', 'quelle': 'b.jpg', 'kategorie': 'kopf', 'gewicht': 1.0,
                 'rigs': {'yolo': {}}, 'textur': {}},
                {'datei': 'c.jpg', 'quelle': 'c.jpg', 'kategorie': 'neben', 'gewicht': 0.0,
                 'rigs': {'yolo': {}, 'openpifpaf': {}, 'vitpose': {}}},
            ])
            s = Bildmodellsichtung(job, a, {'rig': 'alle', 'umfang': 'neue'})
            dran = [p.name for p in s.zu_sichten(a.originale())]
            self.assertEqual(dran, ['b.jpg', 'c.jpg', 'd.jpg'], 'b: Rigs fehlen, c: Hautprobe fehlt, d: neu')
            s = Bildmodellsichtung(job, a, {'rig': 'yolo', 'umfang': 'neue'})
            self.assertEqual([p.name for p in s.zu_sichten(a.originale())], ['c.jpg', 'd.jpg'])
            # Sabotage-Gegenprobe: mit allen Rigs und Hautprobe bleibt nur die neue Datei.
            job.bilder[1]['rigs'] = dict(job.bilder[0]['rigs'])
            job.bilder[2]['textur'] = {}
            s = Bildmodellsichtung(job, a, {'rig': 'alle'})
            self.assertEqual([p.name for p in s.zu_sichten(a.originale())], ['d.jpg'])
            # Übernahme: die Einträge der nicht gesichteten Quellen bleiben, die Wahl der Boxen auch.
            job.bilder[0].update(nutzung='textur', teil='haende', manuell=True, kategorie='neben',
                                 gewicht=0.2)
            s._uebernehmen([{'datei': 'd_z1.jpg', 'quelle': 'd.jpg', 'kategorie': 'koerper', 'gewicht': 1.0},
                            {'datei': 'a_z1.jpg', 'quelle': 'a.jpg', 'kategorie': 'koerper', 'gewicht': 1.0}],
                           bleiben={'b.jpg', 'c.jpg'})
            nach = {b['datei']: b for b in job.bilder}
            self.assertEqual(set(nach), {'a_z1.jpg', 'b_z1.jpg', 'c.jpg', 'd_z1.jpg'})
            self.assertEqual((nach['a_z1.jpg']['nutzung'], nach['a_z1.jpg']['teil']), ('textur', 'haende'))
            self.assertEqual(nach['a_z1.jpg']['kategorie'], 'neben', 'von Hand gestellt bleibt')


def _png():
    from PIL import Image

    puffer = io.BytesIO()
    Image.new('RGB', (8, 8), (120, 90, 70)).save(puffer, 'PNG')
    return puffer.getvalue()


class EndpunkteTest(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')

    def test_stellen_ersetzen_loeschen_und_bis(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        with Pruefablage.ordner('bm_api_') as ordner, override_settings(OBJECTS_ROOT=ordner):
            antwort = self.client.post(
                '/api/bildmodell/anlegen/',
                {'name': 'ZZ Boxen', 'typ': 'genesis9',
                 'bilder': [SimpleUploadedFile('a.png', _png(), 'image/png')],
                 'optionen': json.dumps({'testfall': {'figur': 'gibtsnicht'}})},
            )
            self.assertEqual(antwort.status_code, 200, antwort.content[:200])
            job = Bildmodellauftrag.objects.get(pk=antwort.json()['id'])
            self.assertEqual(job.optionen['testfall'], {}, 'unbekannte Referenzfigur wird verworfen')
            ablage = Bildmodellablage(job.kennung)
            (ablage.zuschnitt() / 'a.jpg').write_bytes(b'x')
            job.bilder = [{'datei': 'a.jpg', 'quelle': 'a.png', 'kategorie': 'neben', 'gewicht': 0.0}]
            job.save()
            z = self.client.get('/api/bildmodell/%s/zustand/' % job.id).json()
            self.assertEqual(z['neue'], [], 'a.png hat einen Eintrag')
            r = self.client.post('/api/bildmodell/%s/bild/a.jpg/' % job.id,
                                 data=json.dumps({'haupt': 'koerper/hinten', 'nutzung': 'textur'}),
                                 content_type='application/json')
            self.assertEqual(r.status_code, 200)
            b = r.json()['bild']
            self.assertEqual((b['kategorie'], b['ansicht'], b['nutzung'], b['gewicht']),
                             ('koerper', 'hinten', 'textur', 1.0))
            # Ersetzen: neue Datei, Eintrag weg, Datei unter „neue"
            r = self.client.post('/api/bildmodell/%s/original/a.png/ersetzen/' % job.id,
                                 {'bild': SimpleUploadedFile('neu.jpg', _png(), 'image/jpeg')})
            self.assertEqual(r.status_code, 200, r.content[:200])
            self.assertEqual(r.json()['neue'], ['a.jpg'])
            self.assertEqual(r.json()['bilder'], [])
            self.assertTrue((ablage.original() / 'a.jpg').is_file())
            self.assertFalse((ablage.original() / 'a.png').exists())
            # Löschen des Originals
            r = self.client.post('/api/bildmodell/%s/original/a.jpg/loeschen/' % job.id)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json()['originale'], [])
            weg = self.client.post('/api/bildmodell/%s/bild/x.jpg/loeschen/' % job.id)
            self.assertEqual(weg.status_code, 404)
            # Start mit `bis`: der Arbeiter bekommt --bis; der Testfall bleibt, auch wenn
            # die Seite ihn nicht schickt.
            from unittest import mock

            job.optionen['testfall'] = {'figur': 'zz_referenz'}
            job.save()
            with mock.patch('core.api.bildmodell.Bildmodellarbeiter.starten', return_value=4711) as start:
                r = self.client.post('/api/bildmodell/%s/starten/' % job.id,
                                     data=json.dumps({'ab': 'sichtung', 'bis': 'sichtung',
                                                      'optionen': {'umfang': 'neue'}}),
                                     content_type='application/json')
            self.assertEqual(r.json()['bis'], 'sichtung')
            start.assert_called_once_with(mock.ANY, 'sichtung', 'sichtung', None)
            job.refresh_from_db()
            self.assertEqual(job.optionen['umfang'], 'neue')
            self.assertEqual(job.optionen['testfall'], {'figur': 'zz_referenz'})


class LaufBisTest(unittest.TestCase):
    def test_lauf_endet_nach_bis(self):
        from core.dienste.bildmodelllauf import Bildmodelllauf

        lauf = Bildmodelllauf.__new__(Bildmodelllauf)
        gelaufen = []

        class Job:
            kennung = 'pruef'
            status = 'angelegt'
            error_message = ''
            progress = 0
            progress_detail = ''
            schritt = ''
            started_at = finished_at = None

            def save(self, **_):
                pass

            def refresh_from_db(self, **_):
                pass

        lauf.job = Job()
        for s in ('sichtung', 'schaetzung', 'ziel', 'anpassung', 'rest', 'vorschau', 'textur', 'speichern'):
            setattr(lauf, '_' + s, (lambda name: (lambda: gelaufen.append(name)))(s))
        self.assertTrue(lauf.ausfuehren('sichtung', bis='sichtung'))
        self.assertEqual(gelaufen, ['sichtung'])
        self.assertEqual(lauf.job.status, 'fertig')
        self.assertEqual(lauf.job.progress, 15, 'Ende des Sichtungsbands, nicht 100')
        gelaufen.clear()
        self.assertTrue(lauf.ausfuehren('vorschau'))
        self.assertEqual(gelaufen, ['vorschau', 'textur', 'speichern'])
        self.assertEqual(lauf.job.progress, 100)
        # `schritte`: genau diese, in Reihenfolge — „Textur anpassen" mit neuen Dateien (19.09.2026).
        gelaufen.clear()
        self.assertTrue(lauf.ausfuehren('speichern', schritte=['textur', 'sichtung']))
        self.assertEqual(gelaufen, ['sichtung', 'textur'])
        self.assertEqual(lauf.job.progress, 98, 'Ende des Texturbands')
