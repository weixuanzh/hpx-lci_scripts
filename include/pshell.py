from subprocess import Popen, PIPE
import os, sys

class PShell:
    def __init__(self):
        self.proc = Popen(['bash'], stdin=PIPE, stdout=PIPE)
        self.tmp_output_name = os.path.join("/tmp", "persistent_shell_output-p{}".format(self.proc.pid))
        with open(self.tmp_output_name, 'w') as fp:
            pass

    def run(self, command, to_print = True):
        cmd = command + " > {} 2>&1; printf \"{} done\n\"\n".format(self.tmp_output_name, self.tmp_output_name, command)
        print("Execute: " + cmd)
        sys.stdout.flush()
        self.proc.stdin.write(cmd.encode('UTF-8'))
        self.proc.stdin.flush()
        while True:
            tmp = self.proc.stdout.readline()
            print("readline: " + tmp.decode('UTF-8'))
            if "done" in tmp.decode('UTF-8'):
                break
        sys.stdout.flush()
        with open(self.tmp_output_name, "r") as output:
            lines = output.read().splitlines()
            if to_print and lines:
                print("\n".join(lines))
            return lines

pshell = PShell()

def run(command, to_print = True):
    pshell.run(command, to_print)

if __name__ == "__main__":
    run("echo hello")
    run("echo world")
    env = "hpx-lci"
    ret = pshell.run("spack env activate {}".format(env), to_print=False)
    if "Error" in "\n".join(ret):
        for line in ret:
            if "setup-env.sh" in line:
                pshell.run(line.strip())
                ret = pshell.run("spack env activate {}".format(env))
                break
    assert "Error" not in "\n".join(ret)
    run("octotiger")