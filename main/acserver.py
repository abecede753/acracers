import pathlib
import psutil
import subprocess
import time

from django.conf import settings


def pause():
    time.sleep(1)


def ac_run():
    """Starts and waits for the end of acServer(wrapper) in
    settings.ACWRAPPEREXE directory."""
    proc = subprocess.Popen(
        [settings.ACWRAPPEREXE, ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=pathlib.Path(settings.ACWRAPPEREXE).parent,
        encoding="utf-8"
    )
    pidfile = pathlib.Path(settings.ACWRAPPEREXE).parent / 'pidfile'
    with pidfile.open(mode="w", encoding="utf-8") as f:
        f.write(str(proc.pid))
    panictimeout = 0
    while proc.poll() is None:
        pause()
        if 'acServer' not in [x.name() for x in psutil.process_iter()]:
            panictimeout += 1
        else:
            panictimeout = 0
        if panictimeout > 2:
            print("panic! killing acwrapper.")
            try:
                subprocess.Popen.kill(proc)
            except Exception:
                print("EXTRAPANIC?")
            pause()
    pidfile.unlink()
    print("server ended.")
