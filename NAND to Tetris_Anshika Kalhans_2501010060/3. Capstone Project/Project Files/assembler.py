
import sys
from pathlib import Path

# Predefined Hack symbols
symbols = {
    "SP": 0, "LCL": 1, "ARG": 2,
    "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576
}

for i in range(16):
    symbols[f"R{i}"] = i

dest_table = {
    "": "000", "M": "001", "D": "010",
    "MD": "011", "A": "100", "AM": "101",
    "AD": "110", "AMD": "111"
}

comp_table = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101",
    "!A": "0110001", "-D": "0001111", "-A": "0110011",
    "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010",
    "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011",
    "M+1": "1110111", "M-1": "1110010",
    "D+M": "1000010", "D-M": "1010011",
    "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101"
}

jump_table = {
    "": "000", "JGT": "001", "JEQ": "010",
    "JGE": "011", "JLT": "100", "JNE": "101",
    "JLE": "110", "JMP": "111"
}


def clean_line(line):
    return line.split("//")[0].strip().replace(" ", "").replace("\t", "")


def valid_symbol(value):
    import re
    return bool(re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", value))

def first_pass(lines):
    rom_address = 0
    user_symbols = {}

    for line_number, line in lines:
        if not line:
            continue

        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]

            if not valid_symbol(label):
                raise ValueError(f"Line {line_number}: invalid label")

            if label in symbols or label in user_symbols:
                raise ValueError(
                    f"Line {line_number}: duplicate or reserved label '{label}'"
                )

            user_symbols[label] = rom_address
        else:
            rom_address += 1

    symbols.update(user_symbols)
    return user_symbols


def second_pass(lines):
    binary_code = []
    user_symbols = {}
    next_variable_address = 16

    for line_number, line in lines:
        if not line or (line.startswith("(") and line.endswith(")")):
            continue

        try:
            if line.startswith("@"):
                value = line[1:]

                if not value:
                    raise ValueError("empty A-instruction")

                if value.isdigit():
                    address = int(value)
                    if address > 32767:
                        raise ValueError("address exceeds 32767")
                else:
                    if not valid_symbol(value):
                        raise ValueError("invalid symbol")

                    if value not in symbols:
                        symbols[value] = next_variable_address
                        user_symbols[value] = next_variable_address
                        next_variable_address += 1

                    address = symbols[value]

                binary_code.append(format(address, "016b"))

            else:
                if line.count("=") > 1 or line.count(";") > 1:
                    raise ValueError("invalid C-instruction")

                if "=" in line:
                    dest, remainder = line.split("=")
                else:
                    dest, remainder = "", line

                if ";" in remainder:
                    comp, jump = remainder.split(";")
                else:
                    comp, jump = remainder, ""

                if dest not in dest_table:
                    raise ValueError("invalid destination")

                if comp not in comp_table:
                    raise ValueError("invalid computation")

                if jump not in jump_table:
                    raise ValueError("invalid jump")

                binary_code.append(
                    "111" + comp_table[comp]
                    + dest_table[dest] + jump_table[jump]
                )

        except ValueError as error:
            raise ValueError(f"Line {line_number}: {error}")

    return binary_code, user_symbols


def assemble(filename):
    input_path = Path(filename)

    if not input_path.is_file():
        print("Error: Input file not found.")
        return

    raw_lines = input_path.read_text(encoding="utf-8").splitlines()

    lines = [
        (number, clean_line(line))
        for number, line in enumerate(raw_lines, start=1)
    ]

    label_symbols = first_pass(lines)
    machine_code, variable_symbols = second_pass(lines)

    output_path = input_path.with_suffix(".hack")
    output_path.write_text(
        "\n".join(machine_code) + "\n",
        encoding="utf-8"
    )

    symbols_path = input_path.parent / "symbols.txt"

    with symbols_path.open("w", encoding="utf-8") as file:
        file.write("SYMBOL\tADDRESS\tTYPE\n")

        for name, address in label_symbols.items():
            file.write(f"{name}\t{address}\tLABEL\n")

        for name, address in variable_symbols.items():
            file.write(f"{name}\t{address}\tVARIABLE\n")

    print("Assembly completed successfully!")
    print(f"Hack file: {output_path}")
    print(f"Symbols file: {symbols_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = input("Enter ASM file path: ").strip().strip('"')

    try:
        assemble(filename)
    except ValueError as error:
        print("Assembly failed:", error)
