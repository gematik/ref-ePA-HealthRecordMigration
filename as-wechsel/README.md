# Schutz des Export-Pakets bei AS-Anbieterwechsel

Wechselt ein Versicherter seinen ePA-Anbieter, werden die Daten seiner Akte vom
alten Anbieter zum neuen Anbieter übertragen. Hierzu wird im Aktensystem des
alten Anbieters ein Export-Paket mit den Daten der Akte erstellt, d. h. von den 
Meta-Daten und Dokumenten (Daten) in einer Akte.
Diese Export-Paket wird vom alten Anbieter dem neuen Anbieter zum Download zur
Verfügung gestellt. Der neue Anbieter kann das Export-Paket laden und die im
Export-Paket befindlichen Daten in das Konto des Versicherten beim neuen
Anbieter importieren.

Das Export-Paket wird innerhalb Vertrauenswürdiger Ausführungsumgebungen (VAU)
erstellt bzw. entpackt, jedoch außerhalb der VAU zum Download zur Verfügung
gestellt. Das Export-Paket wird daher vor unautorisierten Zugriff (insbesondere
auch durch Innentäter beim Betreiber des Aktensystems) durch die folgenden 
hier beschriebenen Maßnahmen zusätzlich geschützt.

## Unterschied von ePA-2.6 zu ePA-3.0.x. (ePA-3.1.x) 

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

## Schlüsselmaterial zum Schutz des Export-Paketes

Zum Schutz des Export-Pakets ist folgendes Schlüsselmaterial erforderlich:

- Kontextschlüssel welcher hier konstant 0...0 Bits (256 Bit) ist.
  Alle zu exportierenden Daten werden mittels des Kontextschlüssel symmetrisch
  verschlüsselt.

- Schlüsselmaterial der VAU zur Content-Signatur beim Betreiber
  (VAU-SIG-Zertifikat C.VAU-SIG mit öffentlichem Schlüssel Pub-VAU-SIG, privatem
  Schlüssel Priv-VAU-SIG)). 
  Der private Schlüssel kann nur durch eine VAU verwendet werden.

- Schlüsselmaterial der VAU zur Ver- und Entschlüsselung beim Betreiber
  (VAU-ENC-Zertifikat C.VAU-ENC mit öffentlichem Schlüssel Pub-VAU-ENC, privatem
  Schlüssel Priv-VAU-ENC)). Der private Schlüssel kann nur durch eine VAU 
  verwendet werden.

## Grundsätzlicher Ablauf der Verschlüsselung des Export-Pakets beim alten Anbieter
(vollständige Kommunikation der Aktensysteme bei Aktensystemwechsel: siehe gemSpec_Aktensystem_ePAfueralle#3.2 Health Record Relocation Service)

Der Kostenträger initiert die Erstellung des Exportpakets durch den Aufruf der Operation startPackageCreation der Schnittstelle I_Health_Record_Relocation_Service.

Gemäß [Exportpaket](../docs/Healthrecord%20relocation%20export%20package.adoc) werden die zu übertragenden Inhalte des Aktenkontos in einer einzelnen ZIP-Datei zusammengefasst.

Für den Schutz der ZIP-Datei sind folgende Schritte durchzuführen:

1. Das ENC-Zertifikat des empfangenden Aktensystems wird von HSM unter Verwendung der Regel hsm-r7 abgerufen. 

2. Der Verarbeitungskontext bildet einen 256-Bit-Zufallswert und kodiert diesen
   hexadezimal. Das Ergebnis wird als `export_paket_name` bezeichnet und muss
   der Dateiname des Exportpakets sein. Der Rückgabewert von startPackageCreation ist die downloadurl, wobei der Dateiname in dieser URL 
   `export_paket_name` sein muss. Weiterhin darf der Pfadname in der URL
   keine personenbeziehbaren Daten enthalten.

3. Der Verarbeitungskontext verschlüsselt die ZIP-Datei symmetrisch (wie sonst
   auch bei ePA üblich AES/GCM, IV=96-Bit zufällig erzeugt, 128-Bit Auth-Tag)
   mit dem Kontextschlüssel KS (Null-Schüssel) und erhält `ciphertext_1`.

4. Der Verarbeitungskontext signiert mit dem privaten VAU-Signaturschlüssel
   Priv-VAU-SIG den Wert `ciphertext_1 ||  export_zeit || KVNR` und erhält als
   Ergebnis die Signatur `signature`. Hierbei ist `export_zeit` die aktuelle
   Zeit (ISO-Format) und `KVNR` die Krankenversichertennummer des Versicherten,
   der seinen Anbieter wechselt.

5. Der Verarbeitungskontext verschlüsselt das Array `plaintext_2 =
   [1, ciphertext_1, export_zeit, KVNR, C.VAU-SIG, signature]` (s.u. für genaues
   Format) hybrid mittels ECIES-Verschlüsselungsverfahren unter Nutzung des
   öffentlichem Schlüssels Pub-VAU-ENC aus dem VAU-ENC-Zertifikats des neuen
   Aktensystems und erhält `ciphertext_2`.

6. Der Verarbeitungskontext stellt `ciphertext_2` unter der erzeugten
   downloadurl (siehe Schritt 2) außerhalb der VAU zum Download für den neuen
   Anbieter bereit. 

## Grundsätzlicher Ablauf der Entschlüsselung des Export-Pakets beim neuen Anbieter
(vollständige Kommunikation der Aktensysteme bei Aktensystemwechsel: siehe gemSpec_Aktensystem_ePAfueralle#3.2 Health Record Relocation Service)

Der neue Kostenträger initiert den Import eines bereitgestellten Exportpaket eines anderen Aktensystems nach Erhalt der downloadurl durch den Aufruf der Operation startPackageImport der Schnittstelle I_Health_Record_Relocation_Service.

Für die Entschlüsselung der erhaltenen ZIP-Datei sind folgende Schritte durchzuführen:

1. Der Verarbeitungskontext entschlüsselt `ciphertext_2` mittels
   ECIES-Verschlüsselungsverfahren unter Nutzung des privaten Schlüssels
   Priv-VAU-ENC und erhält das Array 
   `plaintext_2 = [1, ciphertext_1, export_zeit, KVNR, C.VAU-SIG, signature]`.

2. Der Verarbeitungskontext prüft die Signatur signature mittels des
   mitgelieferten Zertifikats C.VAU-SIG des alten Anbieters.

3. Der Verarbeitungskontext prüft, dass KVNR mit der KVNR des angemeldeten
   Versicherten übereinstimmt und die `export_zeit` nicht mehr als x abweicht.
   Die `export_zeit` soll nicht älter als 30 Tage sein.

4. Der Verarbeitungskontext entschlüsselt `ciphertext_1` mit dem Kontextschlüssel
   KS und erhält die unverschlüsselte ZIP-Datei für den Import.

5. Der erfolgreich Import der Daten wird an das bereitstellende Aktensystem durch Verwendung der Operation deleteExportPackage der Schnittstelle I_Information_Service_Accouts gemeldet. 


## Formate
### Chiffrat\_2 (äußere Verschlüsselungsschicht)

Eine '\x01' plus das normale ECIES-Chiffrat:

1. ein Byte \x01
2. 32-Byte X-Wert ephemerer Schlüssel 
   (bzw. wenn der Schlüssel in Verschlüsselungszertifikat der neuen VAU
   eine größere Kurve (brainpoolP384R1 etc.) dann sind dies analog viele
   Byte. Soll heissen: die pro-Nachricht-ephemeren Schlüssel hängen natürlich
   von den Verschlüsselungsschlüsseln der VAU aus dem Zertifikat ab.)
3. 32-Byte Y-Wert ephemerer Schlüssel 
4. 12 Byte IV für die AES/GCM-Entschlüsselung zufällig erzeugt
5. AES/GCM Chiffrat plus 16 Byte (= 128 Bit) Authentication-Tag

### Plaintext nach der ersten Entschlüsselung (also von Chiffrat\_2)

Ein [CBOR](https://www.rfc-editor.org/rfc/rfc8949.html)-Array der mit folgenden
sechs Elementen

1. eine 1 (integer) als Versionsnummer (Aufwärtskompatibilität)
2. das chiffrat\_1 als binary string
3. die Exportzeit im ISO-Format als ASCII-String der als binary string in CBOR
   kodiert ist (Beispiel: `2021-06-18T15:56:09.340643`)
4. die KVNR des Versicherten, dem die ePA zugehörig ist, als ASCII-String der als
   binary string in CBOR kodiert ist (Beispiel: `A123456789`)
5. das Signatur-Zertifikat der exportierenden -- also damit hier signierenden
   -- VAU-Instanz (binary string)
6. eine ECDSA-Signatur wie üblich nach TR-3111 kodiert (binary string)

Designüberlegung:

(1) 
Parsing/Deserialisierung ist nie angenehm. Wer lange genug sich mit ASN.1/CMS
geschlagen hat, wird sich etwas einfaches wünschen. CBOR wird u. A. bei
FIDO2/Webauthentication verwendet.

(2)
Das Datenformat soll so einfach wie möglich sein, deshalb wurde ein simples
array verwendet und keine verschachtelten Datenstrukturen.

(3)
Bei Datenformaten gibt es zwei Designrichtungen:

1. Daten nach dem was sie vom Daten-Typ sind zu kodieren, oder
2. Daten passend für die nächst folgenden Verarbeitungsschritte zu
   kodieren.

Bei Erhalt eines `plaintext_2` muss die neue VAU-Instanz zunächst die Signatur
prüfen. Signaturen können nur auf binär-Daten geprüft werden. Deshalb sind die
Exportzeit und die KVNR ebenfalls als binary string kodiert.


### Chiffrat\_1 (innere Verschlüsselungsschicht)

Das ein AES/GCM-Chiffrat, verschlüsselt mit dem Kontext-Schlüssel und wie
üblich ein Binärstring beginnend:

- mit 12 Byte (= 96 Bit) IV zufällig pro Verschlüsselung erzeugt,
- dem (aus kryptographischer Sicht) eigentlichen AES/GCM-Chiffrat gefolgt von
  16 Byte (= 128 Bit) Authentication Tag.

## Ready-to-Run Docker-Container

Auf einem System, auf dem Docker installiert ist, kann man den Beispiel-Code
in wenigen Sekunden zum Starten bekommen:

    $ docker pull andreashallof/as-wechsel:3.0
    $ docker run -it andreashallof/as-wechsel:3.0 /bin/bash

    root@3f324c6446c3:/as-wechsel# ./gen-test-daten.sh 10MiB
    10240+0 records in
    10240+0 records out
    10485760 bytes (10 MB, 10 MiB) copied, 0.0758072 s, 138 MB/s

    root@3f324c6446c3:/as-wechsel# ./alte_vau_instanz.py
    zu exportierenden Testdaten ("ZIP-Archiv"): 10485760 Bytes
    Export-Paket für den Dowloadpunkt (Name, Größe)=(a2decb106689b187a3475b86a0d32b5f2a472fbed75bec7ca7f0f2cbbe3af785, 10486586)
    root@3f324c6446c3:/as-wechsel# ./neue_vau_instanz.py a2decb106689b187a3475b86a0d32b5f2a472fbed75bec7ca7f0f2cbbe3af785
    Die Export-Daten (ZIP-File) haben die Größe 10485760 und den Hashwert e5b844cc57f57094ea4585e235f36c78c1cd222262bb89d53c94dcb4d6b3e55d.

    root@3f324c6446c3:/as-wechsel# sha256sum test-daten.bin
    e5b844cc57f57094ea4585e235f36c78c1cd222262bb89d53c94dcb4d6b3e55d  test-daten.bin

    root@3f324c6446c3:/as-wechsel#

## Dependencies

Wer nicht den Docker-Container verwenden möchte, muss darauf achten die
notwendigen python-Libraries installiert zu haben. Dies kann man über den für
die verwendete Linux-Distribution üblichen Paket-Manager tun (apt-get, pacman,
emerge etc.) oder über `pip` -- siehe folgend.

### via Linux-Paket-Manager

Die python-Programm benötigen python3 mit den Bibliotheken `cryptography` und
`cbor`. Diese sind bei quasi allen Linux-Distributionen dabei.

Beispiel: 

- Ubuntu `apt install python-cryptography python3-cbor2`
- Arch Linux `pacman -S extra/python-cryptography community/python-cbor2`

### via pip

Alternativ `pip install -r requirements.txt` starten.


