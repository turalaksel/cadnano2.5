
import cadnano
import cadnano.tests.guitestcase as guitestcase
from cadnano.proxyconfigure import proxyConfigure
proxyConfigure('PyQt')

main = guitestcase.main

class CadnanoGuiTestCase(guitestcase.GUITestCase):
    """
    SEE: http://docs.python.org/library/unittest.html
    """
    def setUp(self):
        """
        The setUp method is called before running any test. It is used
        to set the general conditions for the tests to run correctly.
        For GUI Tests, you always have to call setWidget to tell the
        framework what you will be testing.
        """
        import sys
        
        self.app = cadnano.initAppWithGui() # kick off a Gui style app
        self.document_controller = list(self.app.document_controllers)[0]
        self.main_window = self.document_controller.win

        # Include this or the automatic build will hang
        self.app.dontAskAndJustDiscardUnsavedChanges = True

        # By setting the widget to the main window we can traverse and
        # interact with any part of it. Also, tearDown will close
        # the application so we don't need to worry about that.
        self.setWidget(self.main_window, False, None)

    def tearDown(self):
        """
        The tearDown method is called at the end of running each test,
        generally used to clean up any objects created in setUp
        """
        guitestcase.GUITestCase.tearDown(self)

if __name__ == '__main__':
    guitestcase.main()
