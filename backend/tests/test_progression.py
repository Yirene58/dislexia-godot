import unittest
from types import SimpleNamespace

from app.services.progression_service import (
    experience_required,
    calculate_level,
    add_experience,
)


class TestProgression(unittest.TestCase):

    def test_initial_level(self):
        self.assertEqual(calculate_level(0), 1)

    def test_level_two(self):
        self.assertEqual(calculate_level(100), 2)

    def test_level_three(self):
        self.assertEqual(calculate_level(400), 3)

    def test_experience_required(self):
        self.assertEqual(experience_required(4), 900)

    def test_add_experience(self):
        character = SimpleNamespace(
            experience=80,
            level=1,
        )

        add_experience(character, 50)

        self.assertEqual(character.experience, 130)
        self.assertEqual(character.level, 2)

    def test_invalid_experience(self):
        character = SimpleNamespace(
            experience=0,
            level=1,
        )

        with self.assertRaises(ValueError):
            add_experience(character, -10)


if __name__ == "__main__":
    unittest.main()
