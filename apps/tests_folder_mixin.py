"""
Mixin com testes comuns para todos os módulos de pasta
(ATAS, Relatórios, Pareceres, Ofícios, REA).

Uso:
    class AtaTests(FolderModuleMixin, APITestCase):
        FOLDER_URL = '/api/atas/folders/'
        FILES_URL  = '/api/atas/files/'
        FILES_DELETE_URL = '/api/atas/files-delete/'
        MODULO = 'ATAS'
"""
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.historico.models import HistoricoAcao
from apps.tests_helpers import make_user


class FolderModuleMixin:
    FOLDER_URL = ""
    FILES_URL = ""
    FILES_DELETE_URL = ""
    MODULO = ""

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)

    def _file(self, name="arquivo.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 conteudo fake", content_type="application/pdf")

    def _create_folder(self, name="Pasta Teste"):
        r = self.client.post(self.FOLDER_URL, {"name": name})
        self.assertEqual(r.status_code, 201)
        return r.data["id"]

    def _upload_file(self, folder_id, filename="arquivo.pdf"):
        r = self.client.post(
            f"{self.FOLDER_URL}{folder_id}/files/",
            {"files": self._file(filename)},
            format="multipart",
        )
        self.assertEqual(r.status_code, 201)
        return r.data[0]["id"]

    # Autenticação

    def test_unauthenticated_list_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.FOLDER_URL)
        self.assertEqual(response.status_code, 401)

    # Pastas

    def test_list_folders_empty(self):
        response = self.client.get(self.FOLDER_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_create_folder(self):
        response = self.client.post(self.FOLDER_URL, {"name": "Reunião Março"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Reunião Março")

    def test_create_folder_registra_historico(self):
        self.client.post(self.FOLDER_URL, {"name": "Nova Pasta"})
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="CRIAR", modulo=self.MODULO
            ).exists()
        )

    def test_rename_folder(self):
        folder_id = self._create_folder("Original")
        response = self.client.patch(f"{self.FOLDER_URL}{folder_id}/", {"name": "Renomeada"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Renomeada")

    def test_rename_folder_registra_historico(self):
        folder_id = self._create_folder()
        self.client.patch(f"{self.FOLDER_URL}{folder_id}/", {"name": "Renomeada"})
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="EDITAR", modulo=self.MODULO
            ).exists()
        )

    def test_delete_folder(self):
        folder_id = self._create_folder("Para Deletar")
        response = self.client.delete(f"{self.FOLDER_URL}{folder_id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_folder_registra_historico(self):
        folder_id = self._create_folder()
        self.client.delete(f"{self.FOLDER_URL}{folder_id}/")
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="EXCLUIR", modulo=self.MODULO
            ).exists()
        )

    def test_nao_ve_pastas_de_outro_usuario(self):
        outro = make_user()
        self.client.force_authenticate(user=outro)
        self.client.post(self.FOLDER_URL, {"name": "Pasta do Outro"})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.FOLDER_URL)
        self.assertEqual(len(response.data), 0)

    def test_filtro_por_nome(self):
        self._create_folder("Reunião")
        self._create_folder("Outro")
        response = self.client.get(self.FOLDER_URL, {"q": "Reunião"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Reunião")

    # Upload de arquivos

    def test_upload_arquivo(self):
        folder_id = self._create_folder()
        response = self.client.post(
            f"{self.FOLDER_URL}{folder_id}/files/",
            {"files": self._file()},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 1)

    def test_upload_registra_historico(self):
        folder_id = self._create_folder()
        self.client.post(
            f"{self.FOLDER_URL}{folder_id}/files/",
            {"files": self._file()},
            format="multipart",
        )
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="UPLOAD", modulo=self.MODULO
            ).exists()
        )

    def test_upload_sem_arquivo_retorna_400(self):
        folder_id = self._create_folder()
        response = self.client.post(
            f"{self.FOLDER_URL}{folder_id}/files/", {}, format="multipart"
        )
        self.assertEqual(response.status_code, 400)

    # Arquivos

    def test_list_arquivos(self):
        folder_id = self._create_folder()
        self._upload_file(folder_id)
        response = self.client.get(self.FILES_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_arquivos_filtro_por_pasta(self):
        folder_a = self._create_folder("Pasta A")
        folder_b = self._create_folder("Pasta B")
        self._upload_file(folder_a, "arq_a.pdf")
        self._upload_file(folder_b, "arq_b.pdf")
        response = self.client.get(self.FILES_URL, {"folder_id": folder_a})
        self.assertEqual(len(response.data), 1)

    def test_renomear_arquivo(self):
        folder_id = self._create_folder()
        file_id = self._upload_file(folder_id)
        response = self.client.patch(
            f"{self.FILES_URL}{file_id}/", {"original_name": "novo_nome.pdf"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["original_name"], "novo_nome.pdf")

    def test_delete_arquivo(self):
        folder_id = self._create_folder()
        file_id = self._upload_file(folder_id)
        response = self.client.delete(f"{self.FILES_DELETE_URL}{file_id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_arquivo_registra_historico(self):
        folder_id = self._create_folder()
        file_id = self._upload_file(folder_id)
        self.client.delete(f"{self.FILES_DELETE_URL}{file_id}/")
        excluir_count = HistoricoAcao.objects.filter(
            usuario=self.user, acao="EXCLUIR", modulo=self.MODULO
        ).count()
        self.assertGreaterEqual(excluir_count, 1)

    def test_nao_deleta_arquivo_de_outro_usuario(self):
        outro = make_user()
        self.client.force_authenticate(user=outro)
        folder_id = self._create_folder()
        file_id = self._upload_file(folder_id)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"{self.FILES_DELETE_URL}{file_id}/")
        self.assertEqual(response.status_code, 404)

    # Download ZIP

    def test_download_zip_pasta_vazia_retorna_400(self):
        folder_id = self._create_folder("Vazia")
        response = self.client.get(f"{self.FOLDER_URL}{folder_id}/download/")
        self.assertEqual(response.status_code, 400)

    def test_download_zip(self):
        folder_id = self._create_folder()
        self._upload_file(folder_id)
        response = self.client.get(f"{self.FOLDER_URL}{folder_id}/download/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

    def test_download_zip_registra_historico(self):
        folder_id = self._create_folder()
        self._upload_file(folder_id)
        self.client.get(f"{self.FOLDER_URL}{folder_id}/download/")
        self.assertTrue(
            HistoricoAcao.objects.filter(
                usuario=self.user, acao="DOWNLOAD", modulo=self.MODULO
            ).exists()
        )
