from rest_framework.test import APITestCase

from apps.tests_folder_mixin import FolderModuleMixin


class RelatorioTests(FolderModuleMixin, APITestCase):
    FOLDER_URL = "/api/relatorios/folders/"
    FILES_URL = "/api/relatorios/files/"
    FILES_DELETE_URL = "/api/relatorios/files-delete/"
    MODULO = "RELATORIOS"
