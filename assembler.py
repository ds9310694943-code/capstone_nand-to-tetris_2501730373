"""
assembler.py - Two-pass Hack assembler (Nand to Tetris capstone)
Roll No : 2501730373        K = 73

Extra feature (K mod 3 = 73 mod 3 = 1):
    A bad instruction does not crash the assembler. It prints a clear message
    such as   "Line 7: invalid instruction 'D=Q+1'"   and carries on, so that
    every mistake in the file is reported in one run. No .hack file is written
    if any error was found.

Usage:  python assembler.py Prog.asm        ->  Prog.hack
"""
import re
import sys

# ----------------------------------------------------------------- tables
SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
SYMBOLS.update({f"R{i}": i for i in range(16)})

# comp: a c1 c2 c3 c4 c5 c6
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
}
# every "A" form has an "M" twin with the a-bit set to 1
for _k, _v in list(COMP.items()):
    if "A" in _k:
        COMP[_k.replace("A", "M")] = "1" + _v[1:]

# destination: d1(A) d2(D) d3(M) - letters may come in any order
DEST = {"": "000"}
for _d in ["M", "D", "MD", "A", "AM", "AD", "AMD"]:
    _bits = "".join("1" if ch in _d else "0" for ch in "ADM")
    DEST[_d] = _bits
    DEST["".join(sorted(_d))] = _bits

JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

# commutative forms (A+D, M&D ...) are accepted too
for _k, _v in list(COMP.items()):
    for _op in "+&|":
        if _op in _k:
            _l, _r = _k.split(_op)
            COMP.setdefault(_r + _op + _l, _v)

SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


class AsmError(Exception):
    """Raised for one bad line; carries a readable message."""


def strip_line(raw):
    """Remove the comment and every space/tab from a source line."""
    return "".join(raw.split("//", 1)[0].split())


# ------------------------------------------------------------- first pass
def first_pass(lines, errors):
    """Build the label table and the list of real instructions.
    Returns (instructions, labels); instructions = [(line_no, text), ...]"""
    instructions, labels = [], {}
    for line_no, raw in enumerate(lines, start=1):
        text = strip_line(raw)
        if text == "":
            continue
        if text.startswith("("):
            if not text.endswith(")") or not SYMBOL_RE.match(text[1:-1] or " "):
                errors.append(f"Line {line_no}: invalid label '{text}'")
            else:
                name = text[1:-1]
                if name in labels:
                    errors.append(f"Line {line_no}: label '{name}' already defined")
                else:
                    labels[name] = len(instructions)   # address of next instruction
            continue
        instructions.append((line_no, text))
    return instructions, labels


# ------------------------------------------------------------ second pass
def encode_a(text, table, state):
    sym = text[1:]
    if sym == "":
        raise AsmError("invalid instruction: '@' has no value or symbol")
    if sym.isdigit():
        value = int(sym)
        if value > 32767:
            raise AsmError(f"invalid instruction: '{text}' value exceeds 32767")
    elif SYMBOL_RE.match(sym):
        if sym not in table:                 # new variable
            table[sym] = state["next_ram"]
            state["next_ram"] += 1
        value = table[sym]
    else:
        raise AsmError(f"invalid instruction '{text}'")
    return format(value, "016b")


def encode_c(text):
    dest, comp, jump = "", text, ""
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if dest not in DEST:
        raise AsmError(f"invalid instruction '{text}' (bad destination '{dest}')")
    if comp not in COMP:
        raise AsmError(f"invalid instruction '{text}' (bad computation '{comp}')")
    if jump not in JUMP:
        raise AsmError(f"invalid instruction '{text}' (bad jump '{jump}')")
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(instructions, labels, errors):
    table = dict(SYMBOLS)
    table.update(labels)
    state = {"next_ram": 16}                 # first variable -> RAM[16]
    binary = []
    for line_no, text in instructions:
        try:
            binary.append(encode_a(text, table, state) if text[0] == "@"
                          else encode_c(text))
        except AsmError as err:
            errors.append(f"Line {line_no}: {err}")
    return binary


# ------------------------------------------------------------------ main
def assemble(path):
    with open(path) as f:
        lines = f.readlines()
    errors = []
    instructions, labels = first_pass(lines, errors)
    binary = second_pass(instructions, labels, errors)
    if errors:
        for e in sorted(errors, key=lambda m: int(m.split(":")[0][5:])):
            print(e)
        print(f"{path}: {len(errors)} error(s) found - no .hack file written")
        return 1
    out = path[:-4] + ".hack"
    with open(out, "w") as f:
        f.write("\n".join(binary) + "\n")
    print(f"{path} -> {out}: {len(binary)} instructions")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(2)
    try:
        sys.exit(assemble(sys.argv[1]))
    except FileNotFoundError:
        print(f"Cannot open '{sys.argv[1]}'")
        sys.exit(2)
