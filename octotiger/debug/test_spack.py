import sys, os
import time
from io import StringIO
from subprocess import Popen, PIPE


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

class Shell:
    def __init__(self):
        self.proc = Popen(['bash'], stdin=PIPE, stdout=PIPE)
        with open('/tmp/output', 'w') as fp:
            pass

    def run(self, command, to_print=True):
        cmd = command + b" > /tmp/output 2>&1; echo done\n"
        self.proc.stdin.write(cmd)
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        with open("/tmp/output", "r") as output:
            lines = output.readlines()
            if to_print:
                print("".join(lines))
            return lines

def test_cmd2():
    shell = Shell()
    shell.run(b"echo $PATH")
    shell.run(b". /home/jiakuny/.bashrc")
    shell.run(b"spack env activate hpx-lci")
    shell.run(b"octotiger")

if __name__ == "__main__":
    ret = run("spack env activate {}".format("hpx-lci"))
    if "Error" in "\n".join(ret):
        for line in ret:
            if "setup-env.sh" in line:
                pshell.run(line.strip())
                ret = pshell.run("spack env activate {}".format(env))
                break
    assert "Error" not in "\n".join(ret)