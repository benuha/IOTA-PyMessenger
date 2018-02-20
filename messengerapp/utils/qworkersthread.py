"""
Implement multi-threading processes and callback signals
"""
import logging
import traceback

import sys
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """
    Defines signals available from running Worker thread. These are:

    finished
        no data
    error
        `tuple` (exception_type, value, traceback.format_exc())
    result
        `object` data returned from processing
    progress
        `int` indicating % progress
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread, inherits from QRunnable to handle thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            logger.exception("Worker processes failed!")
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            # Done
            self.signals.finished.emit()
