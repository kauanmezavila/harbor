import base64


ALFABETO = (
    '„ĈгŃç"´ш}=•œ†wzДª≅Dõ·⊆Ê0ΑAΓ₿Ųľё₱sè§oŗэSYłŷC›Å₦—i✓цČъĎa[↕ÇÐΨ³ůŀ№₺F≤j|xĘőΝ⁸,ŭ+ġŦΣИ/∈Œь9ĵÔÏđ.)₈β✔∫ЭNêfΠb₆ãřMĳø©ρūЮUÖÈl£ŏψKĔκ$ģĤ@чZēìŰħιôыı⇔♦ЛÓСtЯg∵ÌJщ∅īйĺhŵàÉЙ₉ŎyÒ↑āâ₫ór²₇¹Δĥ∂⁰ШP5Â7Ξ?ĐĉĨ6ΡQ]žĄV‰″Õé(ţÁ4čŻÚŜņğ₾ΕºŹŧχКcмÛ←т₄ñ―üź2–ăĝ3☆₵ųθŊ{úĶ¡…οö★&д⊃еÝ⁶Æ♫pЗΧÍγхĪňŌ¿ŘζėąnбĕÃęΟëįýУτ∑vH‹сśk1ćİΚ€Ф↔₅áλĹØνĴ^OĚφ฿íξōſ∝_8Τ✖ЫЬк%₡∪ŸŽ~р⁷Eл√ŪпОń⇑жЧî↓∞ŐŤяĭŋΜŠ»Ś¨ΒĽ×ĮŁ₽Ŵũ∉TХĞdĬŞĂ;‚G-Ţ®уНš⊇⇒Ň#вe⁵ķю∓≠!−Ġÿ′ΗĻþΦżŅĢùum⁴BĩАò⁹⇓ΛßŬĖqÄ⇕π₸εWΖηŝ₁МЪзR₩ďÀ÷«Ц∩ĿŕL¥Б₴Ē‡Ů¶₂₀σ∆υ∴♣ÑË∇ΥÜ*αи¢ŶП≥ĆÎĜIаŉωВ♥фû₼¬ΩXť₃<ðæΙ♪♠ĲåĦ∏⇐РТГĀЖ™>űä→₹ЕЁŨ✕ļċĊ₲нΘо℠:ïŖěÞμŔ≈ЩδşÙ⊂'
)


def chave_valida(chave, alfabeto):
    """Check whether every password character exists in the cipher alphabet."""
    if not chave:
        return False

    for c in chave:
        if c not in alfabeto:
            return False

    return True


def BCB_bytes_text(path):
    """Read a binary file and return its Base64 text representation."""
    with open(path, "rb") as arquivo:
        dados = arquivo.read()

    texto = base64.b64encode(dados).decode("ascii")
    return texto


def BCB_text_bytes(path):
    """Read Base64 text from a file and return decoded bytes."""
    with open(path, "r") as arquivo:
        texto = arquivo.read()

    dados = base64.b64decode(texto)
    return dados


def BCB_Cryptography_bytes_passwd(texto, chave, iv=7):
    """Encrypt text using the Harbor rolling alphabet cipher."""
    alphabet_size = len(ALFABETO)
    resultado = ""
    prev = iv

    i = 0
    for c in texto:
        if c in ALFABETO:
            p = ALFABETO.index(c)
            k = ALFABETO.index(chave[i % len(chave)])

            nova_pos = (p + k + prev) % alphabet_size
            resultado += ALFABETO[nova_pos]

            prev = nova_pos
            i += 1
        else:
            resultado += c

    return resultado


def BCB_Descryptography_bytes_passwd(texto, chave, iv=7):
    """Decrypt text produced by BCB_Cryptography_bytes_passwd."""
    alphabet_size = len(ALFABETO)
    resultado = ""
    prev = iv

    i = 0
    for c in texto:
        if c in ALFABETO:
            pos_c = ALFABETO.index(c)
            k = ALFABETO.index(chave[i % len(chave)])

            p = (pos_c - k - prev) % alphabet_size
            resultado += ALFABETO[p]

            prev = pos_c
            i += 1
        else:
            resultado += c

    return resultado
