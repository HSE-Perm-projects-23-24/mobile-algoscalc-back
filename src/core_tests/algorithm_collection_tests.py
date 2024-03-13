import unittest
import os
import json
from shutil import rmtree

from src.core_tests import COLLECTION_FOLDER_PATH, PATH_CONFIG,\
    ALGORITHM_CONFIG, DEFINITION_FILE_NAME, FUNCTION_FILE_NAME, TEST_FILE_NAME,\
    FIB_DEF, FIB_FUNC, FIB_FILE_PATH, FIB_TESTS, FIB_TITLE, LOG_CONFIG_STUB, \
    ALG_FILE_PATH_TEMPL
from src.core.algorithm_collection import AlgorithmCollection, \
    NO_ALGORITHMS_MSG, ALGORITHM_NOT_EXISTS_TEMPL
from src.core.algorithm import Algorithm


class AlgorithmCollectionTests(unittest.TestCase):
    path_config = PATH_CONFIG
    path_config['algorithms_catalog_path'] = COLLECTION_FOLDER_PATH

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(os.path.basename(__file__)):
            os.chdir('../..')
        if not os.path.exists(COLLECTION_FOLDER_PATH):
            os.mkdir(COLLECTION_FOLDER_PATH)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(COLLECTION_FOLDER_PATH):
            os.removedirs(COLLECTION_FOLDER_PATH)

    def tearDown(self) -> None:
        if os.path.exists(COLLECTION_FOLDER_PATH):
            for file in os.listdir(COLLECTION_FOLDER_PATH):
                path = COLLECTION_FOLDER_PATH + '/' + file
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    rmtree(path)

    def test_empty_catalog(self):
        with self.assertRaises(RuntimeError) as error:
            AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                LOG_CONFIG_STUB)
        self.assertEqual(str(error.exception), NO_ALGORITHMS_MSG)

    def test_single_algorithm(self):
        name = 'test_single'
        self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertEqual(algorithms.get_name_title_dict(),
                         {'test_single': FIB_TITLE})
        alg = algorithms.get_algorithm(name)
        self.assertIsInstance(alg, Algorithm)
        self.assertEqual(alg.name, name)
        self.assertEqual(algorithms.get_algorithm_result(name, {'n': 20}),
                         {'result': 6765})
        self.assertTrue(algorithms.has_algorithm(name))

    def test_double_algorithms(self):
        names = ['test1', 'test2']
        for name in names:
            self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertEqual(algorithms.get_name_title_dict(),
                         {'test1': FIB_TITLE,
                          'test2': FIB_TITLE})

    def test_triple_algorithms(self):
        names = ['test1', 'test2', 'test3']
        for name in names:
            self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertEqual(algorithms.get_name_title_dict(),
                         {'test1': FIB_TITLE,
                          'test2': FIB_TITLE,
                          'test3': FIB_TITLE})

    def test_algorithm_not_exists(self):
        name = 'test_single'
        wrong_name = 'wrong_name'
        self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertFalse(algorithms.has_algorithm(wrong_name))
        self.assertRaisesRegex(ValueError,
                               ALGORITHM_NOT_EXISTS_TEMPL.format(wrong_name),
                               algorithms.get_algorithm, wrong_name)
        self.assertRaisesRegex(ValueError,
                               ALGORITHM_NOT_EXISTS_TEMPL.format(wrong_name),
                               algorithms.get_algorithm_result, wrong_name,
                               {'n': 20})

    def test_has_algorithm(self):
        name = 'name'
        wrong_name = 'wrong_name'
        self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertFalse(algorithms.has_algorithm(wrong_name))
        self.assertTrue(algorithms.has_algorithm(name))

    def test_get_algorithm_file_path(self):
        name = 'name'
        self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertEqual(
            os.path.abspath(algorithms.get_algorithm_file_path(name)),
            os.path.abspath(ALG_FILE_PATH_TEMPL.format(COLLECTION_FOLDER_PATH,
                                                       name))
        )

    def test_get_algorithm_file_path_wrong(self):
        name = 'name'
        wrong_name = 'wrong_name'
        self.create_files(name)
        algorithms = AlgorithmCollection(self.path_config, ALGORITHM_CONFIG,
                                         LOG_CONFIG_STUB)
        self.assertRaisesRegex(ValueError,
                               ALGORITHM_NOT_EXISTS_TEMPL.format(wrong_name),
                               algorithms.get_algorithm, wrong_name)

    def create_files(self, name: str) -> None:
        path = COLLECTION_FOLDER_PATH + '/' + name
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + '/' + DEFINITION_FILE_NAME, 'w') as def_file:
            json.dump(FIB_DEF, def_file)
        with open(path + '/' + FUNCTION_FILE_NAME, 'w') as func_file:
            func_file.write(FIB_FUNC)
        with open(path + '/' + TEST_FILE_NAME, 'w') as test_file:
            test_file.write(FIB_TESTS)


if __name__ == '__main__':
    unittest.main()
