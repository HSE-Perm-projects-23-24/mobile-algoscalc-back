import os
import unittest
from core_tests.algorithm_collection_tests import AlgorithmCollectionTests
from core_tests.algorithm_builder_tests import AlgorithmBuilderTest
from core_tests.algorithm_tests import AlgorithmTests
from core_tests.data_element_tests import DataElementTests
from core_tests.data_type_tests import DataTypeTests
from core_tests.data_shape_tests import DataShapeTests
from app_tests.app_tests import AppTest

if __name__ == '__main__':
    if os.path.exists(os.path.basename(__file__)):
        os.chdir('..')
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([
        loader.loadTestsFromTestCase(DataShapeTests),
        loader.loadTestsFromTestCase(DataTypeTests),
        loader.loadTestsFromTestCase(DataElementTests),
        loader.loadTestsFromTestCase(AlgorithmTests),
        loader.loadTestsFromTestCase(AlgorithmBuilderTest),
        loader.loadTestsFromTestCase(AlgorithmCollectionTests),
        loader.loadTestsFromTestCase(AppTest),
    ])

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
