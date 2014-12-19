
import os, sys, time
import random
import unittest

import cadnano.tests.cadnanoguitestcase as cadnanoguitestcase

sys.path.insert(0, '.')
seed = random.Random().randint(0,1<<32)
enviroseed = os.environ.get('UNITTESTS_PRNG_SEED', False)
if enviroseed != False:
    seed = int(enviroseed)
del enviroseed
print("Seeding tests.unittests; use setenv UNITTESTS_PRNG_SEED=%i to replay." % seed)


class UnitTests(cadnanoguitestcase.CadnanoGuiTestCase):
    """
    Unit tests should test individual modules, and do not necessarily need
    to simulate user interaction.

    Create new tests by adding methods to this class that begin with "test".
    See for more detail: http://docs.python.org/library/unittest.html

    Run unit tests by calling "python -m test.unittests" from cadnano2 root
    directory.
    """
    def setUp(self):
        """
        The setUp method is called before running any test. It is used
        to set the general conditions for the tests to run correctly.
        """
        cadnanoguitestcase.CadnanoGuiTestCase.setUp(self)
        self.prng = random.Random(seed)
        # Add extra unit-test-specific initialization here

    def tearDown(self):
        """
        The tearDown method is called at the end of running each test,
        generally used to clean up any objects created in setUp
        """
        cadnanoguitestcase.CadnanoGuiTestCase.tearDown(self)
        # Add unit-test-specific cleanup here

    def testUnit1(self):
        """docstring for testUnit1"""
        pass

if __name__ == '__main__':
    tc = UnitTests()
    tc.setUp()
    cadnanoguitestcase.main()
