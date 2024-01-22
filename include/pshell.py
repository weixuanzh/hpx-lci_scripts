from subprocess import Popen, PIPE
import os, sys
import threading
import random
import time


class ThreadReadio(threading.Thread):
    def __init__(self, io, outfile, term_words, command):
        threading.Thread.__init__(self)
        self.ret = None
        self.io = io
        self.outfile = outfile
        self.term_words = term_words
        self.command = command

    def run(self):
        content = ""
        while True:
            text = self.io.read1(8192).decode("utf-8")
            if text:
                content = content + text
                if content.endswith(self.term_words):
                    content = content[:-len(self.term_words)]
                    break
                if self.outfile:
                    print(text, file=self.outfile, end='')
                    self.outfile.flush()
        self.ret = content


class PShell:
    def __init__(self):
        self.proc = Popen(['bash'], stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    def run(self, command, to_print=True):
        if type(command) is list or type(command) is tuple:
            command = " ".join(command)
        secret = random.random()
        term_words = "\n{} done\n".format(secret)
        cmd = command + "; printf \"{}\"; >&2 printf \"{}\"\n".format(term_words, term_words)
        print("Execute: " + command)
        sys.stdout.flush()
        self.proc.stdin.write(cmd.encode('UTF-8'))
        self.proc.stdin.flush()

        if to_print:
            t1 = ThreadReadio(self.proc.stdout, sys.stdout, term_words, command)
            t2 = ThreadReadio(self.proc.stderr, sys.stderr, term_words, command)
        else:
            t1 = ThreadReadio(self.proc.stdout, None, term_words, command)
            t2 = ThreadReadio(self.proc.stderr, None, term_words, command)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        return t1.ret, t2.ret


pshell = PShell()


def run(command, to_print=True):
    return pshell.run(command, to_print)


def update_env(environs, to_print=True):
    for key, val in environs.items():
        pshell.run("export {}={}".format(key, val))


if __name__ == "__main__":
    run("echo hello")
    run("echo world")
    env = "/global/homes/j/jackyan/workspace/hpx-lci_scripts/spack_env/perlmutter/hpx-lci-debug"
    _, ret_stderr = pshell.run("spack env activate {}".format(env), to_print=False)
    if "Error" in ret_stderr:
        for line in ret_stderr.splitlines():
            if "setup-env.sh" in line:
                pshell.run(line.strip())
                _, ret_stderr = pshell.run("spack env activate {}".format(env))
                break
    print(ret_stderr)
    assert not ret_stderr
    run("octotiger")
