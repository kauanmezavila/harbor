from hashlib import sha256


def hash_text(entry):
    """Return the SHA-256 hex digest for a text value."""
    encoded = sha256(entry.encode("utf-8"))
    return encoded.hexdigest()


def ultra_hash(entry):
    """Hash each character first, then hash the joined result."""
    hashes = []
    entry_chars = list(entry)

    for char in entry_chars:
        output = hash_text(char)
        hashes.append(output)

    final_output = hash_text("".join(hashes))
    return final_output
