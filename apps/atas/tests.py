from rest_framework.test import APITestCase

from apps.tests_folder_mixin import FolderModuleMixin


class AtaTests(FolderModuleMixin, APITestCase):
    FOLDER_URL = "/api/atas/folders/"
    FILES_URL = "/api/atas/files/"
    FILES_DELETE_URL = "/api/atas/files-delete/"
    MODULO = "ATAS"
