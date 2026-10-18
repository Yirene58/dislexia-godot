import unittest

from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.character import Character


class TestSaveSecurity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_save_requires_authentication(self):
        response = self.client.get(
            "/api/characters/1/save"
        )

        self.assertEqual(response.status_code, 401)

    def test_cannot_access_another_users_save(self):
        with self.app.app_context():
            character = db.session.query(Character).first()

            if character is None:
                self.skipTest(
                    "No hay personajes disponibles para esta prueba"
                )

            character_id = character.id

            token = create_access_token(
                identity="999999999"
            )

        response = self.client.get(
            f"/api/characters/{character_id}/save",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_modify_another_users_save(self):
        with self.app.app_context():
            character = db.session.query(Character).first()

            if character is None:
                self.skipTest(
                    "No hay personajes disponibles para esta prueba"
                )

            character_id = character.id

            token = create_access_token(
                identity="999999999"
            )

        response = self.client.put(
            f"/api/characters/{character_id}/save",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "world_id": "mundo_no_autorizado",
                "checkpoint_id": "checkpoint_falso",
                "progress_data": {},
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_users_save(self):
        with self.app.app_context():
            character = db.session.query(Character).first()

            if character is None:
                self.skipTest(
                    "No hay personajes disponibles para esta prueba"
                )

            character_id = character.id

            token = create_access_token(
                identity="999999999"
            )

        response = self.client.delete(
            f"/api/characters/{character_id}/save",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
