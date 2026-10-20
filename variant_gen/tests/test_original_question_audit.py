"""Audit-only safeguards: content identity must never hide material changes."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from audit_original_questions import normalize, full_identity, split_revisions, WordNumbering


class AuditSafeguards(unittest.TestCase):
    def test_display_only(self):
        self.assertEqual(normalize(' x  +  2\n cm '), normalize('x + 2 cm'))
        self.assertEqual(normalize(r'$\sqrt{5}$'), normalize('sqrt(5)'))
        self.assertEqual(normalize(r'${x}^{2}$'), normalize('x^2'))
        self.assertNotEqual(normalize('sqrt(16)'), normalize('4'))

    def test_all_components_required(self):
        a = dict(stem='Nilai -2 cm?', options=['1', '2'], key=['B'], explanation='Alasan 2.')
        self.assertTrue(full_identity(a, dict(a)))
        for field, changed in [('stem','Nilai 2 cm?'), ('stem','Nilai -2 m?'),
                               ('options',['2','1']), ('key',['A']), ('explanation','Alasan 3.')]:
            b = dict(a, **{field: changed})
            self.assertFalse(full_identity(a,b), (field,changed))
        self.assertFalse(full_identity(a, dict(a, explanation=None)))

    def test_revision_kept_separate(self):
        parts=split_revisions([{'text':'Soal 8'}, {'text':'lama'},
                               {'text':'Revisi Soal 8'}, {'text':'baru'}])
        self.assertEqual([x[0] for x in parts], ['original','revision'])
        self.assertEqual(parts[0][1][-1]['text'],'lama')

    def test_numbering_restart_and_inheritance(self):
        n=WordNumbering.from_xml('''<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="upperLetter"/><w:lvlText w:val="%1."/></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="0"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="3"/></w:lvlOverride></w:num></w:numbering>''')
        self.assertEqual(n.label('1',0), 'A.')
        self.assertEqual(n.label('1',0), 'B.')
        self.assertEqual(n.label('2',0), 'C.')


if __name__=='__main__': unittest.main()
