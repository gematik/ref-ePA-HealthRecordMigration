<img align="right" width="200" height="37" src="images/Gematik_Logo_Flag_With_Background.png"/> <br/>
  
# Electronic Health Record System (Health Record Relocation)


---

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-health-record-relocation">About Health Record Relocation </a></li>
    <li><a href="#release-notes">Release Notes</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contributions">Contributions</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About Health Record Relocation
This repository provides technical information for the Electronic Health Record (ePA) application as part of the Telematic Infrastructure (TI).

Health Record Relocation applies when a particular health record shall be moved from one health record system to another ("Relocation"). The process itself is defined in chapter "Health Record Relocation Service" of specification 'gemSpec_Aktensystem_ePAfuerall" and involves the ePA-Basic interfaces I_Health_Record_Relocation_Service and I_Information_Service_Accounts.

One step of the relocation is the exchange of encrypted health record content, collected in a single Zip-file - the export package. The structure of the export package and its enryption is defined here: [Package-Exchange encryption](./as-wechsel/Readme.md) and [Export-Package](./docs/Healthrecord%20relocation%20export%20package.adoc).

This branch relates to **ePA version 3.1** (3.1.X)</br>
See [Branchinformation.md](./Branchinformation.md) for links to specification and further repositories.


## Release Notes
See [ReleaseNotes.md](./ReleaseNotes.md) for all information regarding the releases.

## License
 
Copyright 2024 gematik GmbH
 
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
 
See the [LICENSE](./LICENSE) for the specific language governing permissions and limitations under the License.
 
Unless required by applicable law the software is provided "as is" without warranty of any kind, either express or implied, including, but not limited to, the warranties of fitness for a particular purpose, merchantability, and/or non-infringement. The authors or copyright holders shall not be liable in any manner whatsoever for any damages or other claims arising from, out of or in connection with the software or the use or other dealings with the software, whether in an action of contract, tort, or otherwise.
 
The software is the result of research and development activities, therefore not necessarily quality assured and without the character of a liable product. For this reason, gematik does not provide any support or other user assistance (unless otherwise stated in individual cases and without justification of a legal obligation). Furthermore, there is no claim to further development and adaptation of the results to a more current state of the art.
 
gematik may remove published results temporarily or permanently from the place of publication at any time without prior notice or justification.


## Contributions

This repository is for publication of approved artefacts in context of a specific ePA release. Changes to normative content may be applied in rare exceptional cases but is not intended. Such changes will be covered by follow-up releases in different branches.
Therefor submission of issues and pull requests are not rejected by default but the preferred channel is a contact via gematik website (see <a href="#contact">Contact</a> below) 

## Contact

Please use the contact sheet https://fachportal.gematik.de/kontaktformular and choose "elektronische Patientenakte (ePA)" as request category in drop-down list "Thema der Anfrage/Kategorien".
