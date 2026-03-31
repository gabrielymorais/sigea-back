from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.historico.models import HistoricoAcao
from apps.tests_helpers import make_user

User = get_user_model()

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
ME_URL = "/api/auth/me/"
USUARIOS_URL = "/api/auth/usuarios/"

PAYLOAD_BASE = {
    "username": "novousuario",
    "email": "novo@test.com",
    "full_name": "Novo Usuário",
    "cpf": "500.500.500-50",
    "telefone": "(85) 98888-8888",
    "tipo_profissional": "Gestor",
    "escola_lotacao": "IFCE Fortaleza",
    "portaria": "Portaria 010/2026",
    "password": "senha@Segura1",
}


# Registro

class RegisterTests(APITestCase):
    def test_registro_valido(self):
        response = self.client.post(REGISTER_URL, PAYLOAD_BASE)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "novousuario")

    def test_registro_email_duplicado(self):
        self.client.post(REGISTER_URL, PAYLOAD_BASE)
        payload = {**PAYLOAD_BASE, "username": "outro", "cpf": "600.600.600-60"}
        response = self.client.post(REGISTER_URL, payload)
        self.assertEqual(response.status_code, 400)

    def test_registro_cpf_duplicado(self):
        self.client.post(REGISTER_URL, PAYLOAD_BASE)
        payload = {**PAYLOAD_BASE, "username": "outro2", "email": "outro2@test.com"}
        response = self.client.post(REGISTER_URL, payload)
        self.assertEqual(response.status_code, 400)

    def test_registro_username_duplicado(self):
        self.client.post(REGISTER_URL, PAYLOAD_BASE)
        payload = {**PAYLOAD_BASE, "email": "outro3@test.com", "cpf": "700.700.700-70"}
        response = self.client.post(REGISTER_URL, payload)
        self.assertEqual(response.status_code, 400)

    def test_registro_campos_obrigatorios(self):
        response = self.client.post(REGISTER_URL, {"username": "incompleto"})
        self.assertEqual(response.status_code, 400)


# ------------------------------------------------------------------ #
# Login
# ------------------------------------------------------------------ #

class LoginTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="loginuser", password="senha@Login1")

    def test_login_valido_retorna_tokens(self):
        response = self.client.post(LOGIN_URL, {"username": "loginuser", "password": "senha@Login1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_senha_errada(self):
        response = self.client.post(LOGIN_URL, {"username": "loginuser", "password": "errada"})
        self.assertEqual(response.status_code, 401)

    def test_login_usuario_inexistente(self):
        response = self.client.post(LOGIN_URL, {"username": "naoexiste", "password": "qualquer"})
        self.assertEqual(response.status_code, 401)


# ------------------------------------------------------------------ #
# Me (perfil)
# ------------------------------------------------------------------ #

class MeTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="meuser", password="senha@Me1")
        self.client.force_authenticate(user=self.user)

    def test_get_me_retorna_dados(self):
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "meuser")

    def test_get_me_nao_autenticado_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, 401)

    def test_atualizar_perfil(self):
        response = self.client.patch(ME_URL, {"full_name": "Nome Atualizado"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Nome Atualizado")

    def test_trocar_senha_correta(self):
        response = self.client.patch(ME_URL, {
            "current_password": "senha@Me1",
            "new_password": "novaSenha@2",
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("novaSenha@2"))

    def test_trocar_senha_errada_retorna_400(self):
        response = self.client.patch(ME_URL, {
            "current_password": "senhaErrada",
            "new_password": "novaSenha@2",
        })
        self.assertEqual(response.status_code, 400)


# ------------------------------------------------------------------ #
# Admin: gestão de usuários
# ------------------------------------------------------------------ #

class UsersAdminTests(APITestCase):
    def setUp(self):
        self.admin = make_user(username="admintest", is_staff=True)
        self.client.force_authenticate(user=self.admin)

    def _payload_novo_usuario(self):
        return {
            "username": "criado_pelo_admin",
            "email": "criadoadmin@test.com",
            "full_name": "Criado Admin",
            "cpf": "800.800.800-80",
            "telefone": "(85) 97777-7777",
            "tipo_profissional": "Técnico",
            "escola_lotacao": "IFCE Maracanaú",
            "portaria": "Portaria 020/2026",
            "password": "senha@Admin1",
        }

    def test_listar_usuarios_como_admin(self):
        response = self.client.get(USUARIOS_URL)
        self.assertEqual(response.status_code, 200)

    def test_listar_usuarios_como_nao_admin_retorna_403(self):
        comum = make_user(username="comum_noadmin")
        self.client.force_authenticate(user=comum)
        response = self.client.get(USUARIOS_URL)
        self.assertEqual(response.status_code, 403)

    def test_criar_usuario_como_admin(self):
        response = self.client.post(USUARIOS_URL, self._payload_novo_usuario())
        self.assertEqual(response.status_code, 201)

    def test_criar_usuario_registra_historico(self):
        self.client.post(USUARIOS_URL, self._payload_novo_usuario())
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.admin, acao="CRIAR", modulo="USUARIOS"
            ).exists()
        )

    def test_arquivar_usuario(self):
        user = make_user(username="paraarquivar")
        response = self.client.delete(f"{USUARIOS_URL}{user.pk}/")
        self.assertEqual(response.status_code, 204)
        user.refresh_from_db()
        self.assertTrue(user.is_archived)
        self.assertFalse(user.is_active)

    def test_arquivar_usuario_registra_historico(self):
        user = make_user(username="paraarquivar2")
        self.client.delete(f"{USUARIOS_URL}{user.pk}/")
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.admin, acao="EXCLUIR", modulo="USUARIOS"
            ).exists()
        )

    def test_desarquivar_usuario(self):
        user = make_user(username="paraderarquivar")
        self.client.delete(f"{USUARIOS_URL}{user.pk}/")
        response = self.client.post(f"{USUARIOS_URL}{user.pk}/desarquivar/")
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_archived)
        self.assertTrue(user.is_active)

    def test_desarquivar_usuario_registra_historico(self):
        user = make_user(username="paraderarquivar2")
        self.client.delete(f"{USUARIOS_URL}{user.pk}/")
        self.client.post(f"{USUARIOS_URL}{user.pk}/desarquivar/")
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.admin, acao="EDITAR", modulo="USUARIOS"
            ).exists()
        )

    def test_listar_somente_arquivados(self):
        user = make_user(username="arquivado_list")
        self.client.delete(f"{USUARIOS_URL}{user.pk}/")
        response = self.client.get(USUARIOS_URL, {"arquivados": "true"})
        self.assertEqual(response.status_code, 200)
        ids = [u["id"] for u in response.data["results"]]
        self.assertIn(user.pk, ids)
