import json, tempfile, unittest
from pathlib import Path
from local_rag_desk import RagError, build_index, format_context, load_index, search, tokenize
from local_rag_desk.cli import main

class LocalRagTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)/"docs"; self.root.mkdir()
        (self.root/"water.md").write_text("Water treatment\n"+("Coagulation filtration improve drinking water quality. "*12),encoding="utf-8")
        (self.root/"arabic.txt").write_text("معالجة المياه\n"+("تساعد المرشحات في تحسين جودة المياه وإزالة الشوائب. "*12),encoding="utf-8")
        self.index_path=Path(self.tmp.name)/"index.json"
    def tearDown(self): self.tmp.cleanup()
    def test_unicode_tokenization(self): self.assertIn("المياه",tokenize("جودة المياه ممتازة"))
    def test_build_save_load_and_search(self):
        idx=build_index(self.root,self.index_path,chunk_size=30,overlap=5); self.assertGreaterEqual(idx["file_count"],2)
        loaded=load_index(self.index_path); hits=search(loaded,"filtration water",limit=2)
        self.assertTrue(hits); self.assertEqual("water.md",hits[0].source); self.assertGreater(hits[0].score,0)
    def test_arabic_search_and_context_citation(self):
        idx=build_index(self.root,chunk_size=30,overlap=5); hits=search(idx,"جودة المياه")
        self.assertTrue(hits); self.assertIn("arabic.txt",format_context(hits))
    def test_ignores_other_extensions(self):
        (self.root/"ignore.csv").write_text("water,water",encoding="utf-8"); idx=build_index(self.root,chunk_size=30,overlap=5); self.assertEqual(2,idx["file_count"])
    def test_bad_chunk_config(self):
        with self.assertRaises(RagError): build_index(self.root,chunk_size=10)
        with self.assertRaises(RagError): build_index(self.root,chunk_size=30,overlap=30)
    def test_empty_query_and_limit_validation(self):
        idx=build_index(self.root,chunk_size=30,overlap=5)
        with self.assertRaises(RagError): search(idx,"---")
        with self.assertRaises(RagError): search(idx,"water",limit=0)
    def test_corrupt_index_rejected(self):
        self.index_path.write_text(json.dumps({"format":1,"chunks":[]}),encoding="utf-8")
        with self.assertRaises(RagError): load_index(self.index_path)
    def test_cli_roundtrip(self):
        self.assertEqual(0,main(["index",str(self.root),"-o",str(self.index_path),"--chunk-size","30","--overlap","5"]))
        self.assertEqual(0,main(["search","معالجة المياه","-i",str(self.index_path),"--json"]))
        self.assertEqual(0,main(["validate","-i",str(self.index_path)]))

if __name__=="__main__": unittest.main()
