from rest_framework.test import APITestCase

from apps.tests_folder_mixin import FolderModuleMixin


class OficioTests(FolderModuleMixin, APITestCase):
    FOLDER_URL = "/api/oficios/folders/"
    FILES_URL = "/api/oficios/files/"
    FILES_DELETE_URL = "/api/oficios/files-delete/"
    MODULO = "OFICIOS"
