#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Das ist die Referenzimplementierung für die Verschlüsselung und Signatur
beim Export der Akte für den AS-Wechsel bei ePA-3.0.x und ePA-3.1.x.

Ziel ist es den Export-Paket-Mechanismus von ePA-2.6 so weit wie möglich zu
übernehmen. Da es bei ePA 3.x keine Kontext-Schlüssel mehr gibt, wird für den
Export der "Null-Schlüssel" (0...0 (256 Bit)) anstatt dessen verwendet. Es
gibt aus sicherheitstechnischer Perspektive also nur noch eine effektive
Verschlüsselungsschicht -- aus Implementierungssicht immer noch zwei
(Null-Schlüssel innere Verschlüsselungsschicht, VAU-ENC bei der äußeren
Verschlüsselungsschicht).

Für zukünftige ePA-AS-Versionen werden wir mit dem Export-Mechanismus auf eine
synchrone VAU-zu-VAU-Kommunikation über das VAU-Protokoll wechseln. Die "alte"
VAU (altes Aktensystem) wird dann die zu exportierten Daten (ZIP-File) über das
VAU-Protokoll an die "neue" VAU (also im neuen Aktensystem) senden. Das Ziel
dabei ist, bessere Sicherheitseigenschaften (Forward-Secrecy, Quantum
Computing Resistance) zu erreichen.

Die alte VAU-Instanz stellt das Export-Paket zunächst als ZIP-File zusammen.
Und dann wird es mit dem Kontextschlüssel der Akte via AES/GCM verschlüsselt.
Das Chiffrat wird zusammen mit der Exportzeit und der KVRN der Akte von der
alten VAU signiert. Das Ergebnis wird dann via ECIES-Verschlüsselung für die
neue VAU verschlüsselt.
"""

import cbor2, datetime, secrets
from binascii import unhexlify

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


if __name__ == "__main__":

    # Das Verschlüsselungszertifikat der neuen VAU bekommt die alte
    # VAU-Instanz im SuspendAccount-SOAP-Request als Eingabeparameter.
    # Das Zertifikat muss die alte VAU prüfen, so wie auch Zertifikate beim
    # VAU-Protokoll ...
    # im SOAP-Request ist das Zertifikat base64(der(cert))-kodiert
    neue_vau_enc_zertifikat_der = open("pki/neue_vau_enc_cert.der", "rb").read()

    # Bei ePA-3x. gibt es nun keinen Kontext-Schlüssel mehr. Dieser wird für die
    # innere Verschlüsselungsschicht jetzt immer auf Null gesetzt.
    # (Null-Schlüssel 0...0 (256-Bit)
    user_context_key = unhexlify("00"*32)
    assert len(user_context_key) == 32 # 256-Bit-Schlüssel

    # Der Name der Datei des Export-Paket im Download-Bereich des alten AS
    # soll keine Informationen über den Versicherten enthalten. Er wird
    # zufällig erzeugt (256 Bit).
    export_paket_name = secrets.token_hex(32)
    export_zeit = datetime.datetime.now().isoformat().encode()
    # Den KVNR die zur aktuell zu exportierenden Akten kennt die VAU-Instanz.
    aktueller_versicherter_kvrn = b"A123456789"

    zu_exportierende_daten = open("test-daten.bin", "rb").read()
    print('zu exportierenden Testdaten ("ZIP-Archiv"):',
        len(zu_exportierende_daten), "Bytes")
    sign_cert = open("pki/alte_vau_sign_cert.der", "rb").read()
    # der private Schlüssel würde dann in HSM liegen
    signing_key_pem = open("pki/alte_vau_sign_priv_key.pem", "rb").read()
    signing_key = serialization.load_pem_private_key(signing_key_pem,
                  password=None, backend=default_backend())

    # AES/GCM-Verschlüsselung der zu exportierenden Daten der Akte mittels
    # des Kontextschlüssels (also Metadaten (TOC) und verschlüsselte Dokumente
    # der Akte)
    iv = secrets.token_bytes(12)
    ciphertext_1 =  iv + AESGCM(user_context_key).encrypt(iv,
                     zu_exportierende_daten, associated_data=None)

    # Jetzt signiere ich das Chiffrat_1 zusammen mit der Exportzeit und
    # der KVNR der Akte
    signature = signing_key.sign(
                ciphertext_1 + export_zeit + aktueller_versicherter_kvrn,
                ec.ECDSA(hashes.SHA256()))

    # Array aus 6 Elementen: Version=1, Chiffrat_1 ...
    plaintext_2 = cbor2.dumps([1, ciphertext_1, export_zeit,
                   aktueller_versicherter_kvrn, sign_cert, signature])

    # Jetzt brauche ich den Schlüssel aus dem Neue-VAU-Zertifikat
    neue_vau_enc_zertifikat = x509.load_der_x509_certificate(
                              neue_vau_enc_zertifikat_der, default_backend())
    neue_vau_enc_public_key = neue_vau_enc_zertifikat.public_key()
    assert neue_vau_enc_public_key.curve.name == 'brainpoolP256r1'

    # ephemere Schlüsselpaar für die ECIES-Verschlüsselung erzeugen
    private_key = ec.generate_private_key(ec.BrainpoolP256R1(), default_backend())
    pn = private_key.public_key().public_numbers()
    x = "{:x}".format(pn.x).zfill(64).encode()
    y = "{:x}".format(pn.y).zfill(64).encode()
    shared_secret = private_key.exchange(ec.ECDH(), neue_vau_enc_public_key)
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
           info=b'ePA-Export-Paket', backend=default_backend())
    aes_key = hkdf.derive(shared_secret)
    iv = secrets.token_bytes(12)
    ciphertext_2 = b'\x01' + unhexlify(x) + unhexlify(y) + iv + \
                    AESGCM(aes_key).encrypt(iv, plaintext_2, associated_data=None)

    with open(export_paket_name, "wb") as f:
        f.write(ciphertext_2)
    print("Export-Paket für den Dowloadpunkt (Name, Größe)=(",
        export_paket_name, ", ", len(ciphertext_2),")", sep='')

