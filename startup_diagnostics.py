"""Early, best-effort startup diagnostics. Works before importing Kivy/jnius."""
import os
import sys
import tempfile
import traceback

_path = None
_installed = False
_fault_file = None


def mark(stage):
    line = '[MinikStartup] ' + stage + '\n'
    try:
        sys.stderr.write(line)
        sys.stderr.flush()
    except Exception:
        pass
    if _path:
        try:
            with open(_path, 'a', encoding='utf8') as stream:
                stream.write(line)
        except OSError:
            pass


def install():
    global _path, _installed, _fault_file
    if _installed:
        return
    _installed = True
    directory = os.environ.get('ANDROID_PRIVATE') or tempfile.gettempdir()
    _path = os.path.join(directory, 'minik_startup.log')
    try:
        os.makedirs(directory, exist_ok=True)
        if os.path.exists(_path) and os.path.getsize(_path) > 65536:
            with open(_path, 'w', encoding='utf8'):
                pass
    except OSError:
        pass
    previous = sys.excepthook

    def report(kind, value, tb):
        mark('UNCAUGHT PYTHON EXCEPTION')
        try:
            with open(_path, 'a', encoding='utf8') as stream:
                traceback.print_exception(kind, value, tb, file=stream)
        except OSError:
            pass
        previous(kind, value, tb)

    sys.excepthook = report
    mark('START version=1.3.0 python=' + sys.version.split()[0])
    try:
        import faulthandler
        _fault_file = open(_path, 'a', encoding='utf8')
        faulthandler.enable(file=_fault_file, all_threads=True)
    except (OSError, RuntimeError, ImportError):
        pass
