from hashlib import sha256


def hashear(entry):
    """Return the SHA-256 hex digest for a text value."""
    codificado = sha256(entry.encode("utf-8"))
    return codificado.hexdigest()


def ultra_hash(entry):
    """Hash each character first, then hash the joined result."""
    hashs = []
    entry_chars = list(entry)

    for char in entry_chars:
        output = hashear(char)
        hashs.append(output)

    final_output = hashear("".join(hashs))
    return final_output
