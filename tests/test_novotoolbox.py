import unittest
import pandas as pd
import pathlib
# from .. import novotoolbox as ni
from novocontrol_toolbox import novo_toolbox as ni
# TODO use pytest instead of unittest

class TestBasicImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod_path = pathlib.Path(__file__).parent
        cls.messpath = mod_path / pathlib.PurePath('testdata/20250311-RT601-ST013+PE-ST049_20DEG_01.TXT')
        cls.basepath = mod_path / pathlib.PurePath('testdata/RToben/')
        cls.filenames = ['20250303-RT601-ST013+PE-ST049_20DEG_01.TXT', '20250303-RT601-ST013+PE-ST049_20DEG_02.TXT', '20250303-RT601-ST013+PE-ST049_20DEG_03.TXT']

    def test_read_novo(self):
        df, einheiten, metadata = ni.read_novo(self.messpath)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(einheiten, dict)
        self.assertIsInstance(metadata, dict)
        self.assertEqual(len(df.columns), len(einheiten))

    def test_ClassMeasurement(self):
        m = ni.Measurement(self.messpath)
        self.assertIsInstance(m.df, pd.DataFrame)
        self.assertIsInstance(m.einheiten, dict)
        self.assertIsInstance(m.metadata, dict)

    def test_metadata(self):
        m = ni.Measurement(self.messpath)
        self.assertEqual(len(m.einheiten), 8)
        self.assertEqual(len(m.metadata), 9)
        # Einheiten
        self.assertEqual(m.einheiten["Freq."], 'Hz')
        self.assertEqual(m.einheiten["|Eps|"], '')
        self.assertEqual(m.einheiten["|Sig|"], 'S/cm')
        # Metadata
        self.assertEqual(m.metadata["Date"], '11.3.2025')
        self.assertEqual(m.metadata["Time"], '9:32')
        self.assertEqual(m.metadata["Sample"], 'RT601-ST013+PE-ST049')
        self.assertEqual(m.metadata["Diameter"], 40.0)
        self.assertEqual(m.metadata["Thickness"], 2.19)
        self.assertEqual(m.metadata["Spacer Capacity"], 0.0)
        self.assertEqual(m.metadata["Spacer Area"], 0.0)
        self.assertEqual(m.metadata["Edge Correction"], True)
        self.assertEqual(m.metadata["Electrode Thickness"], 2.0)

    def test_data(self):
        m = ni.Measurement(self.messpath)
        self.assertEqual(m.df.columns[0], 'Freq.')
        self.assertEqual(m.df.columns[3], '|Eps|' )
        self.assertEqual(len(m.df.columns), 8)
        self.assertEqual(len(m.df), 13)
        self.assertEqual(m.df['|Eps|'].iloc[2], 2.68987) #loc(4e4, '|Eps|') ?
        


    def test_filenameParser(self):
        self.assertEqual(ni._parse_filename(pathlib.PurePath('C:/examplePath/20250311-RT601-ST013+PE-ST049_20DEG_01.TXT')), 
                        {'Date': '20250311', 'Sample': 'RT601-ST013+PE-ST049', 'Temperature': '20', 'm_number': '01'})

    def test_groupImport(self):
        mg1 = ni.MeasurementGroup.from_files(basepath=self.basepath, filenames=self.filenames)
        m = ni.Measurement(self.messpath)
        mg2 = ni.MeasurementGroup(measurements=m)
        mg3 = ni.MeasurementGroup()
        self.assertTrue(mg3._empty)
        self.assertFalse(mg2._empty)
        self.assertFalse(mg1._empty)

class TestMeasurementGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod_path = pathlib.Path(__file__).parent
        cls.messpath = mod_path / pathlib.PurePath('testdata/20250311-RT601-ST013+PE-ST049_20DEG_01.TXT')
        cls.basepath = mod_path / pathlib.PurePath('testdata/RToben/')
        cls.filenames = ['20250303-RT601-ST013+PE-ST049_20DEG_01.TXT', '20250303-RT601-ST013+PE-ST049_20DEG_02.TXT', '20250303-RT601-ST013+PE-ST049_20DEG_03.TXT']
        cls.m = ni.Measurement(cls.messpath)
        cls.mg = ni.MeasurementGroup.from_files(basepath=cls.basepath, filenames=cls.filenames)

    def test_magicMethods(self):
        mg = ni.MeasurementGroup.from_files(basepath=self.basepath, filenames=self.filenames)
        self.assertEqual(len(mg), 3)

    def test_addMeasurement(self):
        mg = ni.MeasurementGroup.from_files(basepath=self.basepath, filenames=self.filenames)
        self.assertEqual(len(self.mg.measurements), 3)
        self.mg.append_measurement(self.m)
        self.assertEqual(len(self.mg.measurements), 4)
        self.mg.append_measurement(self.messpath) # already exists
        self.assertEqual(len(self.mg.measurements), 4)

    def test_mean_deviation(self):
        mg = ni.MeasurementGroup.from_files(basepath=self.basepath, filenames=self.filenames)
        mg[0].df = pd.DataFrame({
            "Freq.": [1, 4, 7],
            "B": [5, 3, 4],
            "C": [20, 16, 6],
            "D": [-14, -3, 17]
            })
        mg[1].df = pd.DataFrame({
            "Freq.": [1, 4, 7],
            "B": [5, 3, 4],
            "C": [20, 16, 6],
            "D": [-14, -3, 17]
            })
        mg[2].df = pd.DataFrame({
            "Freq.": [1, 4, 7],
            "B": [5, 3, 4],
            "C": [20, 16, 6],
            "D": [-14, -3, 17]
            })
        pd.testing.assert_frame_equal(mg.mean().df, mg[0].df, check_dtype=False) 
        deviation_series = mg.mean_deviation_series
        expected_index = pd.Index([1, 4, 7], name='Freq.')
        self.assertIsInstance(deviation_series, pd.DataFrame)
        pd.testing.assert_index_equal(deviation_series.index, expected_index)
        expected_df = pd.DataFrame({
            "B": [0.0, 0.0, 0.0],
            "C": [0.0, 0.0, 0.0],
            "D": [0.0, 0.0, 0.0]
        }, index=expected_index)
        pd.testing.assert_frame_equal(deviation_series, expected_df)
        mg[1].df = pd.DataFrame({
            "Freq.": [1, 4, 7],
            "B": [8, 2, -3],
            "C": [2, 160, 1],
            "D": [0, 0, -17]
            })
        # check new mean
        expected_df = pd.DataFrame({
            "Freq.": [1, 4, 7],
            "B": [6.0, 8/3, 5/3],
            "C": [14, 64, 13/3],
            "D": [-28/3, -2, 17/3]
        }) 
        pd.testing.assert_frame_equal(mg.mean().df, expected_df, check_dtype=False)
        deviation_series = mg.mean_deviation_series
        expected_df = pd.DataFrame({
            "B": [4/18, 1/6, 28/15],
            "C": [24/42, 1, 20/39],
            "D": [2/3, 2/3, 8/3]
        }, index=expected_index)
        pd.testing.assert_frame_equal(deviation_series, expected_df)

        mean_deviation = mg.mean_deviation
        print(mean_deviation)
        expected_mean_deviation = pd.Series([203/270, 569/819, 4/3], index=["B", "C", "D"])
        pd.testing.assert_series_equal(mean_deviation, expected_mean_deviation)




        
class TestMeasurement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod_path = pathlib.Path(__file__).parent
        cls.messpath = mod_path / pathlib.PurePath('testdata/20250311-RT601-ST013+PE-ST049_20DEG_01.TXT')
        cls.m1 = ni.Measurement(cls.messpath)
        cls.m2 = ni.Measurement()
        cls.m2.df = pd.DataFrame({
            "Freq.": [1, 4, 7],
            "B": [5, 3, 4],
            "C": [20, 16, 6],
            "D": [-14, -3, 17]
            })
    
    def test_mean(self):
        m2_mean = self.m2.mean()
        self.assertIsInstance(m2_mean, pd.Series)
        pd.testing.assert_series_equal(m2_mean, pd.Series([4.0, 4, 14, 0], index=["Freq.", "B", "C", "D"]))
        m2_mean = self.m2.mean(ignore_negatives=True)
        self.assertIsInstance(m2_mean, pd.Series)
        pd.testing.assert_series_equal(m2_mean, pd.Series([4.0, 4, 14, 17], index=["Freq.", "B", "C", "D"]))

# class TestNoEdgeCompensation(unittest.TestCase):

# class TestCalculations(unittest.TestCase):


# class TestTemperatureSeries(unittest.TestCase):

if __name__ == '__main__':
    unittest.main()