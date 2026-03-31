from rest_framework.test import APITestCase

from apps.tests_folder_mixin import FolderModuleMixin


class ParecerTests(FolderModuleMixin, APITestCase):
    FOLDER_URL = "/api/pareceres/folders/"
    FILES_URL = "/api/pareceres/files/"
    FILES_DELETE_URL = "/api/pareceres/files-delete/"
    MODULO = "PARECERES"
