# UI — Restricciones

| ID | Restricción |
|----|-------------|
| **U-R1** | Sin lógica SFTP/pandas en widgets — delegar a `core` |
| **U-R2** | Operaciones largas async; UI responsive |
| **U-R3** | Mensajes de error legibles; origen técnico en sftp/errores.md |
| **U-R4** | Reinicio app Windows: subprocess (no os.execv solo) |
| **U-R5** | Paridad visual Mac/Windows (mismas Uxx; nativos OS pickers) |
| **U-R6** | Lottie/motion opcional; spinners nativos en v1 |
| **U-R9** | **Sin auto-conexión:** al arrancar no invocar S01/S05/S06; red solo tras U-02 |
| **U-R10** | Fallo de conexión (timeout, auth, red): mostrar error y **continuar**; no cerrar app |
| **U-R11–U-R13** | Asistente metadata — ver [asistente-metadata.md](./asistente-metadata.md) |
| **U-R14** | Menú U-SB **desacoplado** del layout T — posición configurable; sin lógica en chrome |

No repetir R1–R27 de SFTP aquí — enlazar.
