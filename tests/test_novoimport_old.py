import unittest
import pandas as pd
import pathlib
import novo_importer_old as ni

class TestBasicImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod_path = pathlib.Path(__file__).parent
        cls.messpath = mod_path / pathlib.PurePath('testdata/20250311-RT601-ST013+PE-ST049_20DEG_01.TXT')
    

    def test_read_novo(self):
        df, einheiten, metadata = ni.read_novo(self.messpath)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(einheiten, dict)
        self.assertIsInstance(metadata, dict)
        self.assertEqual(len(df.columns), len(einheiten))




# class TestNoEdgeCompensation(unittest.TestCase):


# class TestTemperatureSeries(unittest.TestCase):

if __name__ == '__main__':
    unittest.main()