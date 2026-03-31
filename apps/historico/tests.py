from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.historico.models import HistoricoAcao, TipoAcao, Modulo
from apps.historico.utils import registrar_acao
from apps.tests_helpers import make_user

HISTORICO_URL = "/api/historico/"


class HistoricoTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="histuser")
        self.client.force_authenticate(user=self.user)

    def _registrar(self, acao=TipoAcao.CRIAR, modulo=Modulo.ATAS, descricao="Ação teste", **kwargs):
        registrar_acao(self.user, acao, modulo, descricao, **kwargs)

    # ------------------------------------------------------------------ #
    # Autenticação
    # ------------------------------------------------------------------ #

    def test_nao_autenticado_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(response.status_code, 401)

    # ------------------------------------------------------------------ #
    # Listagem
    # ------------------------------------------------------------------ #

    def test_list_vazio(self):
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_retorna_proprias_acoes(self):
        self._registrar(descricao="Criou pasta")
        self._registrar(acao=TipoAcao.EXCLUIR, modulo=Modulo.DOCUMENTOS, descricao="Deletou doc")
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(len(response.data), 2)

    def test_nao_ve_acoes_de_outro_usuario(self):
        outro = make_user(username="outro_hist")
        registrar_acao(outro, TipoAcao.CRIAR, Modulo.ATAS, "Ação do outro")
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(response.data, [])

    def test_ordenado_mais_recente_primeiro(self):
        self._registrar(descricao="Primeira")
        self._registrar(descricao="Segunda")
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(response.data[0]["descricao"], "Segunda")
        self.assertEqual(response.data[1]["descricao"], "Primeira")

    # ------------------------------------------------------------------ #
    # Campos retornados
    # ------------------------------------------------------------------ #

    def test_campos_retornados(self):
        self._registrar(descricao="Criou pasta", objeto_id=1, objeto_nome="Pasta A")
        response = self.client.get(HISTORICO_URL)
        item = response.data[0]
        campos = {"id", "acao", "acao_display", "modulo", "modulo_display", "descricao", "objeto_id", "objeto_nome", "created_at"}
        self.assertTrue(campos.issubset(item.keys()))

    def test_campo_acao_display_legivel(self):
        self._registrar(acao=TipoAcao.CRIAR)
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(response.data[0]["acao_display"], "Criar")

    def test_campo_modulo_display_legivel(self):
        self._registrar(modulo=Modulo.RELATORIOS)
        response = self.client.get(HISTORICO_URL)
        self.assertEqual(response.data[0]["modulo_display"], "Relatórios")

    # ------------------------------------------------------------------ #
    # Filtros
    # ------------------------------------------------------------------ #

    def test_filtro_por_modulo(self):
        self._registrar(modulo=Modulo.ATAS, descricao="Ação em ATAS")
        self._registrar(modulo=Modulo.DOCUMENTOS, descricao="Ação em DOCUMENTOS")
        response = self.client.get(HISTORICO_URL, {"modulo": "ATAS"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["modulo"], "ATAS")

    def test_filtro_por_acao(self):
        self._registrar(acao=TipoAcao.CRIAR, descricao="Criou algo")
        self._registrar(acao=TipoAcao.EXCLUIR, descricao="Deletou algo")
        response = self.client.get(HISTORICO_URL, {"acao": "EXCLUIR"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["acao"], "EXCLUIR")

    def test_filtro_modulo_e_acao_combinados(self):
        self._registrar(acao=TipoAcao.CRIAR, modulo=Modulo.ATAS)
        self._registrar(acao=TipoAcao.UPLOAD, modulo=Modulo.ATAS)
        self._registrar(acao=TipoAcao.CRIAR, modulo=Modulo.DOCUMENTOS)
        response = self.client.get(HISTORICO_URL, {"modulo": "ATAS", "acao": "CRIAR"})
        self.assertEqual(len(response.data), 1)

    def test_filtro_modulo_invalido_retorna_vazio(self):
        self._registrar(modulo=Modulo.ATAS)
        response = self.client.get(HISTORICO_URL, {"modulo": "MODULO_INEXISTENTE"})
        self.assertEqual(response.data, [])

    # ------------------------------------------------------------------ #
    # Integração via API real (criação de pasta no módulo ATAS)
    # ------------------------------------------------------------------ #

    def test_criacao_de_pasta_atas_registra_no_historico(self):
        self.client.post("/api/atas/folders/", {"name": "Pasta via API"})
        response = self.client.get(HISTORICO_URL)
        acoes = [item["acao"] for item in response.data]
        self.assertIn("CRIAR", acoes)

    def test_upload_de_arquivo_registra_no_historico(self):
        r = self.client.post("/api/atas/folders/", {"name": "Pasta Upload"})
        folder_id = r.data["id"]
        f = SimpleUploadedFile("arquivo.pdf", b"%PDF fake", content_type="application/pdf")
        self.client.post(f"/api/atas/folders/{folder_id}/files/", {"files": f}, format="multipart")
        response = self.client.get(HISTORICO_URL)
        acoes = [item["acao"] for item in response.data]
        self.assertIn("UPLOAD", acoes)
