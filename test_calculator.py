import unittest
from calculator import addition


class TestAddition(unittest.TestCase):

    def test_positive_numbers(self):
        self.assertEqual(addition(2, 3), 5)

    def test_negative_numbers(self):
        self.assertEqual(addition(-1, -4), -5)

    def test_zero(self):
        self.assertEqual(addition(0, 7), 7)


if __name__ == "__main__":
    unittest.main()
