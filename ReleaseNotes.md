<img align="right" width="250" height="47" src="images/Gematik_Logo_Flag_With_Background.png"/> <br/>    
 
# Release Notes ref-ePA-HealthRecordMigration
## Release 3.1.0-7
- require history-bundles for versioned fhir resources (C_12580)
- added resources of Patient Service (C_12479)
### changes
- remove isPrivateInsurance to indicate if GKV or PKV (C_12359)
## Release 3.1.0-6
- Health Record Relocation for ePA-3.1.3
### changes
- remove isPrivateInsurance to indicate if GKV or PKV (C_12359)
## Release 3.1.0-5
### changes
- clarify document link restrictions for attached xds documents
- editorial update regarding fhir resources used in export file 
## Release 3.1.0-4
### changes
- editorial correction ('secondaryDataUsage', 'data-submission') in export package definition (C_12322)
- add isPrivateInsurance to indicate if GKV or PKV (C_12328)
- integrate changes from Release 3.0.5-3
    - added User-specific Deny Policy Medication Service content (C_12333)
## Release 3.1.0-3
### changes
- integrate changes from Release 3.0.5-2, 3.0.5-1 and 3.0.0-3
    - handling for NCPeH entitlements explained (C_12218)
    - correction of type in insurantId of entitlement jwt (C_12216)
    - added insurance name to export package (C_12030)
    - removed ePA-2.X remains
    - update package requirements
    - fixed schema and example in E-Mails section in export package definition.
## Release 3.1.0-2
### changes
-  Added the changes for the ePA 3.1 Medication Service FHIR instances  
## Release 3.1.0-1
### changes
- integrate changes from Release 3.0.0-2 
    - added requirement for sequence of entries in export package zip file.
## Release 3.1.0
- Health Record Relocation for ePA-3.1
### changes
- integrate changes from Release 3.0.0-2 
    - fixed schema and example for emails section in export package definition
## Release 3.1.0-RC
- Health Record Relocation for ePA-3.1 and later versions
### changes
- added research data purpose consent decisions to export package.
- renamed the json schema $id to avoid any ambiguities with names for json data files. 
## Release 3.0.0-1
### changes
- changed E-Mails section in export package definition according to updated E-Mail Management.
## Release 3.0.0
- Health Record Relocation for ePA-3.0 and later versions
## Release 3.0 init
- initial setup for Release 3.0 'ePA fuer Alle'
