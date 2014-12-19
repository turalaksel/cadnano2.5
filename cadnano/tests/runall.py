
import glob
import os
import unittest
from .xmlrunner import XMLTestRunner
# from unittests import UnitTests
# from modeltests import ModelTests
from .functionaltests import FunctionalTests
# from recordedtests.template import RecordedTests

def main(useXMLRunner=True):
    # load hard-coded tests
    # unit_test_suite = unittest.makeSuite(UnitTests)
    # model_test_suite = unittest.makeSuite(ModelTests)
    functional_test_suite = unittest.makeSuite(FunctionalTests)

    # combine and run tests
    # alltests = unittest.TestSuite([unit_test_suite, model_test_suite, functional_test_suite])
    alltests = unittest.TestSuite([functional_test_suite])

    if useXMLRunner:
        stream = file("testresults.xml", "w")
        runner = XMLTestRunner(stream)
        result = runner.run(alltests)
        stream.close()
    else:
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(alltests)
    return result


if __name__ == "__main__":
    textRunner = os.environ.get('CADNANO_RUN_PLAINTEXT_TESTS', None) == "YES"
    main(not textRunner)
