from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.historico.models import HistoricoAcao
from apps.tests_helpers import make_user

DOCS_URL = "/api/documents/"


def make_file(name="doc.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 conteudo fake", content_type="application/pdf")


class DocumentTests(APITestCase):
    def setUp(self):
        self.user = make_user(username="docuser")
        self.client.force_authenticate(user=self.user)

    def _create_doc(self, name="Documento Teste"):
        return self.client.post(
            DOCS_URL,
            {"name": name, "doc_type": "RELATORIO", "file": make_file()},
            format="multipart",
        )

    # ------------------------------------------------------------------ #
    # Autenticação
    # ------------------------------------------------------------------ #

    def test_nao_autenticado_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(DOCS_URL)
        self.assertEqual(response.status_code, 401)

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #

    def test_list_vazio(self):
        response = self.client.get(DOCS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_criar_documento(self):
        response = self._create_doc("Relatório Março")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Relatório Março")

    def test_criar_documento_registra_historico(self):
        self._create_doc()
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="UPLOAD", modulo="DOCUMENTOS"
            ).exists()
        )

    def test_list_retorna_proprio_documento(self):
        self._create_doc()
        response = self.client.get(DOCS_URL)
        self.assertEqual(len(response.data), 1)

    def test_atualizar_documento(self):
        r = self._create_doc()
        doc_id = r.data["id"]
        response = self.client.patch(f"{DOCS_URL}{doc_id}/", {"name": "Nome Novo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Nome Novo")

    def test_atualizar_documento_registra_historico(self):
        r = self._create_doc()
        doc_id = r.data["id"]
        self.client.patch(f"{DOCS_URL}{doc_id}/", {"name": "Editado"})
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="EDITAR", modulo="DOCUMENTOS"
            ).exists()
        )

    def test_deletar_documento(self):
        r = self._create_doc()
        doc_id = r.data["id"]
        response = self.client.delete(f"{DOCS_URL}{doc_id}/")
        self.assertEqual(response.status_code, 204)

    def test_deletar_documento_registra_historico(self):
        r = self._create_doc()
        doc_id = r.data["id"]
        self.client.delete(f"{DOCS_URL}{doc_id}/")
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="EXCLUIR", modulo="DOCUMENTOS"
            ).exists()
        )

    def test_download_documento(self):
        r = self._create_doc()
        doc_id = r.data["id"]
        response = self.client.get(f"{DOCS_URL}{doc_id}/download/")
        self.assertEqual(response.status_code, 200)

    def test_download_documento_registra_historico(self):
        r = self._create_doc()
        doc_id = r.data["id"]
        self.client.get(f"{DOCS_URL}{doc_id}/download/")
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="DOWNLOAD", modulo="DOCUMENTOS"
            ).exists()
        )

    # ------------------------------------------------------------------ #
    # Isolamento entre usuários
    # ------------------------------------------------------------------ #

    def test_nao_ve_documento_de_outro_usuario(self):
        outro = make_user(username="outro_doc")
        self.client.force_authenticate(user=outro)
        self._create_doc("Doc do Outro")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(DOCS_URL)
        self.assertEqual(len(response.data), 0)

    def test_nao_deleta_documento_de_outro_usuario(self):
        outro = make_user(username="outro_doc2")
        self.client.force_authenticate(user=outro)
        r = self._create_doc("Doc do Outro 2")
        doc_id = r.data["id"]
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"{DOCS_URL}{doc_id}/")
        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------ #
    # Busca e ordenação
    # ------------------------------------------------------------------ #

    def test_busca_por_nome(self):
        self._create_doc("Relatório Anual")
        self._create_doc("Ofício Especial")
        response = self.client.get(DOCS_URL, {"search": "Relatório"})
        self.assertEqual(len(response.data), 1)
