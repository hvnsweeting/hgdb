print(sys.executable)
print(sys.version)
print("Hello world, from python")
gdb.write("Hello world by gdb\n")


class HelloWorld(gdb.Command):
    def __init__(self):
        super (HelloWorld, self).__init__("hello", gdb.COMMAND_USER)


    def invoke(self, arg, from_tty):
        if arg.strip():
            name = arg.strip()
        else:
            name = "World"
        print(f"Chào, {name}!")


import tempfile
class Arch(gdb.Command):
    def __init__(self):
        super (Arch, self).__init__("arch", gdb.COMMAND_USER)


    def invoke(self, arg, from_tty):
        tmpfile = tempfile.mktemp()
        with open(tmpfile, 'w+') as f:
            gdb.execute("set logging off")
            gdb.execute("set height 0")
            gdb.execute(f"set logging file {tmpfile}")
            gdb.execute("set logging overwrite on")
            gdb.execute("set logging redirect on")
            gdb.execute("set logging on")
            gdb.execute("maintenance info sections ?")
            gdb.flush()
            gdb.execute("set logging off")
            output = f.read()
            for line in output.splitlines():
                if 'file type' in line:
                    print(line.split()[-1].strip('.'))
                    break


Arch()
HelloWorld()


class Context(gdb.Command):
    def __init__(self):
        super (Context, self).__init__("context", gdb.COMMAND_USER)

    def run_command(self, cmd):
        tmpfile = tempfile.mktemp()
        with open(tmpfile, 'w+') as f:
            gdb.execute("set logging off")
            gdb.execute("set height 0")
            gdb.execute(f"set logging file {tmpfile}")
            gdb.execute("set logging overwrite on")
            gdb.execute("set logging redirect on")
            gdb.execute("set logging on")
            try:
                gdb.execute(cmd)
                gdb.flush()
                output = f.read()
            except gdb.MemoryError:
                # gdb.MemoryError: Cannot access memory at address 0x0
                output = ""

            gdb.execute("set logging off")
        return output


    def invoke(self, arg, from_tty):
        for line in self.run_command("info registers").splitlines():
            if not line.startswith("r"):
                continue
            register, _address, *contents = line.split()
            r = self.run_command(f"x/i ${register}").strip(" =>\n")
            if '<' in r and '>' in r:
                print("{:<15}{}".format(register, r))
            else:
                print(line)


        print("="*20 + "DISASM" + "="*20)
        print(self.run_command("x/10i $pc"))
        print("="*20 + "STACK" + "="*20)
        # $4 = 10
        word_to_print = int(self.run_command("print ($rbp -$rsp)/4").split()[-1])
        print(self.run_command(f"x/{word_to_print}w $rsp"))

Context()

gdb.execute("""define hook-stop
context
end""")
