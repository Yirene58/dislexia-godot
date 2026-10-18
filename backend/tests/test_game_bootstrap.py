import unittest

from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.character import Character


class TestGameBootstrap(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_requires_authentication(self):
        response = self.client.get(
            "/api/game/characters/1/bootstrap"
        )

        self.assertEqual(response.status_code, 401)

    def test_rejects_unknown_character(self):
        with self.app.app_context():
            token = create_access_token(
                identity="999999999"
            )

        response = self.client.get(
            "/api/game/characters/999999999/bootstrap",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_rejects_another_users_character(self):
        with self.app.app_context():
            character = db.session.query(Character).first()

            if character is None:
                self.skipTest("No existen personajes para probar")

            character_id = character.id

            token = create_access_token(
                identity="999999999"
            )

        response = self.client.get(
            f"/api/game/characters/{character_id}/bootstrap",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
