"""Pruebas del progreso del niño: tabla Intento, IA adaptativa (RF4), niveles (RF13),
logros (RF6/RF38) y estado del jugador (RF16/RF43). Usa una base de datos en memoria,
así no toca dislexia.db.
"""
import unittest

from flask_jwt_extended import create_access_token

from app.config import Config
from app.services.adaptacion import EstadoAdaptativo, aplicar_resultado
from app.services.silabas import dificultades, silabear


class TestModuloAdaptativo(unittest.TestCase):
    def test_cinco_aciertos_suben_un_nivel(self):
        e = EstadoAdaptativo()
        for _ in range(4):
            e, cambio, _m = aplicar_resultado(e, True)
            self.assertIsNone(cambio)
        e, cambio, _m = aplicar_resultado(e, True)
        self.assertEqual((e.dificultad, cambio), (2, "sube"))

    def test_tres_fallos_bajan_un_nivel(self):
        e = EstadoAdaptativo(dificultad=3)
        aplicar_resultado(e, False)
        aplicar_resultado(e, False)
        e, cambio, _m = aplicar_resultado(e, False)
        self.assertEqual((e.dificultad, cambio), (2, "baja"))

    def test_un_acierto_corta_la_racha_de_fallos(self):
        e = EstadoAdaptativo(dificultad=2)
        aplicar_resultado(e, False)
        aplicar_resultado(e, False)
        aplicar_resultado(e, True)
        e, cambio, _m = aplicar_resultado(e, False)
        self.assertEqual((e.dificultad, cambio), (2, None))

    def test_no_pasa_de_los_limites(self):
        e = EstadoAdaptativo(dificultad=1)
        for _ in range(6):
            e, _c, _m = aplicar_resultado(e, False)
        self.assertEqual(e.dificultad, 1)
        e = EstadoAdaptativo(dificultad=3)
        for _ in range(10):
            e, _c, _m = aplicar_resultado(e, True)
        self.assertEqual(e.dificultad, 3)


class TestRutasProgreso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._uri_original = Config.SQLALCHEMY_DATABASE_URI
        Config.SQLALCHEMY_DATABASE_URI = "sqlite://"
        from app import create_app
        from app.extensions import db
        from app.models.character import Character
        from app.models.user import User
        cls.app = create_app()
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()
            u1 = User(username="nina", email="nina@x.com")
            u1.set_password("12345678")
            u2 = User(username="otro", email="otro@x.com")
            u2.set_password("12345678")
            db.session.add_all([u1, u2])
            db.session.commit()
            c = Character(user_id=u1.id, name="Leo", character_class="mage")
            db.session.add(c)
            db.session.commit()
            cls.cid = c.id
            cls.token = create_access_token(identity=str(u1.id))
            cls.token_otro = create_access_token(identity=str(u2.id))

    @classmethod
    def tearDownClass(cls):
        Config.SQLALCHEMY_DATABASE_URI = cls._uri_original

    def _h(self, token=None):
        return {"Authorization": f"Bearer {token or self.token}"}

    def _intento(self, correcto, **extra):
        cuerpo = {"world_id": "mundo_1", "nivel": 1, "ejercicio": "pelota",
                  "correcto": correcto, "tiempo_ms": 1500}
        cuerpo.update(extra)
        return self.client.post(f"/api/characters/{self.cid}/intentos",
                                json=cuerpo, headers=self._h())

    def test_1_flujo_completo(self):
        # Niveles: solo el 1 abierto y recomendado
        r = self.client.get(f"/api/characters/{self.cid}/mundos/mundo_1", headers=self._h())
        niveles = r.get_json()["data"]["niveles"]
        self.assertEqual([n["desbloqueado"] for n in niveles], [True, False, False])
        self.assertTrue(niveles[0]["recomendado"])

        # RF4: 5 aciertos seguidos suben la dificultad
        for i in range(5):
            r = self._intento(True)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["data"]["dificultad"], 2)
        self.assertEqual(r.get_json()["data"]["cambio"], "sube")

        # RF39: la inactividad no cuenta como error
        for _ in range(3):
            r = self._intento(False, por_inactividad=True)
        self.assertEqual(r.get_json()["data"]["dificultad"], 2)

        # RF4: 3 fallos seguidos bajan la dificultad
        for _ in range(3):
            r = self._intento(False, tipo_error="inversion", respuesta=["et"])
        self.assertEqual(r.get_json()["data"]["dificultad"], 1)
        self.assertEqual(r.get_json()["data"]["cambio"], "baja")

        # RF13: no se puede completar un nivel bloqueado
        r = self.client.post(f"/api/characters/{self.cid}/mundos/mundo_1/niveles/3/completar",
                             headers=self._h())
        self.assertEqual(r.status_code, 409)

        # RF6: completar niveles da insignias y desbloquea el siguiente
        r = self.client.post(f"/api/characters/{self.cid}/mundos/mundo_1/niveles/1/completar",
                             headers=self._h())
        d = r.get_json()["data"]
        self.assertEqual(d["nuevos_logros"], ["mundo_1:nivel_1"])
        self.assertTrue(d["niveles"][1]["desbloqueado"])
        self.assertTrue(d["niveles"][1]["recomendado"])
        self.client.post(f"/api/characters/{self.cid}/mundos/mundo_1/niveles/2/completar",
                         headers=self._h())
        r = self.client.post(f"/api/characters/{self.cid}/mundos/mundo_1/niveles/3/completar",
                             headers=self._h())
        d = r.get_json()["data"]
        self.assertTrue(d["mundo_completado"])
        self.assertIn("mundo_1:completado", d["nuevos_logros"])

        # Repetir un nivel ya completado no duplica la insignia (RF12)
        r = self.client.post(f"/api/characters/{self.cid}/mundos/mundo_1/niveles/1/completar",
                             headers=self._h())
        self.assertEqual(r.get_json()["data"]["nuevos_logros"], [])

        # "Mis logros": obtenidos y pendientes
        r = self.client.get(f"/api/characters/{self.cid}/logros", headers=self._h())
        mundo1 = r.get_json()["data"][0]
        self.assertTrue(all(i["obtenido"] for i in mundo1["insignias"]))
        mundo2 = r.get_json()["data"][1]
        self.assertFalse(any(i["obtenido"] for i in mundo2["insignias"]))

    def test_2_estado_del_jugador(self):
        r = self.client.put(f"/api/characters/{self.cid}/estado-juego", headers=self._h(),
                            json={"mundo_actual": "mundo_1",
                                  "ejercicio_pendiente": {"nivel": 2, "palabra": "tomate"}})
        self.assertEqual(r.status_code, 200)
        r = self.client.get(f"/api/characters/{self.cid}/estado-juego", headers=self._h())
        self.assertEqual(r.get_json()["data"]["ejercicio_pendiente"]["palabra"], "tomate")

    def test_3_otro_usuario_no_ve_ni_modifica(self):
        r = self.client.get(f"/api/characters/{self.cid}/mundos/mundo_1",
                            headers=self._h(self.token_otro))
        self.assertEqual(r.status_code, 404)
        r = self.client.post(f"/api/characters/{self.cid}/intentos",
                             headers=self._h(self.token_otro),
                             json={"world_id": "mundo_1", "ejercicio": "x", "correcto": True})
        self.assertEqual(r.status_code, 404)

    def test_4_validaciones(self):
        r = self._intento("si")
        self.assertEqual(r.status_code, 400)
        r = self._intento(True, world_id="mundo_9")
        self.assertEqual(r.status_code, 400)

    def test_5_palabras_por_nivel_y_dificultad(self):
        for nivel, (mi, ma) in {1: (2, 2), 2: (3, 3), 3: (2, 3)}.items():
            r = self.client.post("/api/ia/silabas", headers=self._h(), json={
                "nivel": nivel, "cantidad": 4, "character_id": self.cid, "world_id": "mundo_1"})
            d = r.get_json()["data"]
            self.assertEqual(len(d["palabras"]), 4)
            for p in d["palabras"]:
                self.assertTrue(mi <= len(p["silabas"]) <= ma, p)
                self.assertEqual(p["silabas"], silabear(p["palabra"]))
                # opciones = sílabas correctas + tantas trampas como la dificultad
                self.assertEqual(len(p["opciones"]), len(p["silabas"]) + d["dificultad"])
                if nivel == 3:
                    self.assertTrue({"grupo_consonantico", "diptongo", "silaba_trabada"}
                                    & dificultades(p["palabra"]), p)


if __name__ == "__main__":
    unittest.main()
