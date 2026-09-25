# SFTP — Criterios de éxito

Checklist para dar por cerrado el **módulo SFTP** (antes de pandas o polish UI).

- [ ] **S05** test_auth OK contra Transfer real (VPN)
- [ ] **S03** cambio de llave reconecta (L-01)
- [ ] **S06–S07** navegar `config/<profile>/scheduled` y `requested`
- [ ] **S08** preview CSV respeta R12; binario → PreviewNotSupported
- [ ] **S09** descarga a path local indicado por UI
- [ ] **S14** generar llave y usarla en S03
- [ ] **S17** perfil JSON persiste y recarga
- [ ] Mac y Windows: mismo contrato `ISftpBrowser`
- [ ] Mock mode sin VPN pasa tests de contrato
- [ ] **S18/S19** `PDE_DESKTOP_MOCK=1 ./scripts/run_sftp_job.sh` descarga `expect[]` y reporta PASS/FAIL
- [ ] Ninguna dependencia Postgres en carpeta `adapters/` SFTP
