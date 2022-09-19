import subprocess
import sys
from pathlib import Path


def shell(cmd, env=None, cwd=None):
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        cmd = ['/bin/bash', '-c', "".join(cmd)]
    else:
        cmd = "".join(cmd)
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    return p.returncode, stdout.decode(), stderr.decode()


def all_xmls(directory: Path):
    return sorted([f for f in list(directory.rglob("*.xml"))])


def get_all_xmls(argv):
    script_name = argv[0]
    usage = "usage: {} path/to/irs/directory,path/to/another/irs/directory".format(script_name)
    if len(sys.argv) != 2:
        raise Exception(usage)
    directories = argv[1].split(",")
    all_models = []
    for directory in directories:
        directory = Path(directory)
        assert directory.is_dir(), "Script expects directories. " + usage
        all_models.extend(all_xmls(directory))
    return set(all_models)
