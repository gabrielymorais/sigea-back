from rest_framework.test import APITestCase

from apps.tests_folder_mixin import FolderModuleMixin


class ReaTests(FolderModuleMixin, APITestCase):
    FOLDER_URL = "/api/rea/folders/"
    FILES_URL = "/api/rea/files/"
    FILES_DELETE_URL = "/api/rea/files-delete/"
    MODULO = "REA"
