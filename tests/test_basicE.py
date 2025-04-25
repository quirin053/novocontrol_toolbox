import unittest
import basicE

# TODO use subtests

class TestCalculation(unittest.TestCase):
    def test_reihenleitwert(self):
        self.assertEqual(basicE.leitwert_reihe([1, 1, 1]), 1/3)
        self.assertEqual(basicE.leitwert_reihe([1, 1, 0]), 0)
        self.assertEqual(basicE.leitwert_reihe([1, 0, 1]), 0)
        self.assertEqual(basicE.leitwert_reihe([5, 0.1, 33]), 1/(1/5 + 1/0.1 + 1/33))


    def test_reihenleitfaehigkeit(self):
        # print(basicE.leitfaehigkeit_reihe([1, 5], [2, 1]))
        
        self.assertEqual(basicE.leitfaehigkeit_reihe([1, 1, 1], [1/3, 1/3, 1/3]), 1)
        self.assertEqual(basicE.leitfaehigkeit_reihe([1, 1], [1, 1]), 1)
        self.assertEqual(basicE.leitfaehigkeit_reihe([1, 5], [2, 1]), 3/2.2)

    def test_permittivity_series(self):
        self.assertEqual(basicE.permittivity_series([1, 2], [1, 1]), 4/3)
        self.assertEqual(basicE.permittivity_series([1, 2, 1], [1, 1, 2]), 8/7)


class TestExceptions(unittest.TestCase):

    def test_reihenleitwert(self):
        with self.assertRaises(TypeError):
            basicE.leitwert_reihe(1)


    def test_reihenleitfaehigkeit(self):
        with self.assertRaises(TypeError):
            basicE.leitfaehigkeit_reihe(1, [1, 1])
        # with self.assertRaises(ValueError):
        #     basicE.leitfaehigkeit_reihe([1, 1], [1, 0])
        with self.assertRaises(ValueError):
            basicE.leitfaehigkeit_reihe([1, 1], [1])

    def test_permittivity_series(self):
        with self.assertRaises(TypeError):
            basicE.permittivity_series(1, [1, 1])
        # with self.assertRaises(ValueError):
        #     basicE.permittivity_series([1, 1], [1, 0])
        with self.assertRaises(ValueError):
            basicE.permittivity_series([1, 1], [1])
        


if __name__ == '__main__':
    unittest.main()