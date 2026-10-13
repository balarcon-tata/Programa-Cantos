# TATA | OEE Cantos — instalación e integración
Dashboard aislado en `oee/index.html`. La aplicación `Programa-Cantos/index.html` no se altera.

## Estado
- Frontend publicado como código en GitHub, acceso a datos mediante correo corporativo Supabase Auth (OTP). Verifica que el proveedor Email de Supabase esté habilitado y que su política de cuentas permita a los usuarios autorizados.
- Tablas del proyecto existente `Balances_ingenieria`: `oc_admins`, `oc_machine_config`, `oc_machine_hourly`, todas con RLS.
- Administrador inicial: `balarcon@tata.com.gt`. Personal autorizado con dominio `@tata.com.gt` puede consultar, pero no editar metas.
- Sincronización con INTEQ **pendiente de instalar en red interna**. El dashboard no debe mostrar datos inventados.
- Contador `cinchos` **aún requiere validación física** como acumulativo; las filas incompletas no deben considerarse producción confirmada.
- El indicador denominado OEE no representa OEE integral hasta disponer de calidad + rendimiento + disponibilidad reales; por ahora se visualiza eficiencia horaria y ocupación.

## Pasos siguientes
1. Abrir `https://balarcon-tata.github.io/Programa-Cantos/oee/` después de confirmar GitHub Pages habilitado en Settings > Pages para rama main / raíz.
2. Autenticarse con correo corporativo y comprobar lectura de metas (inicialmente sin datos). Si el correo no llega, revisar Supabase Auth > Providers / URL Configuration y Site URL / Redirect URLs.
3. Descargar la V3 del agente, instalarlo en máquina interna con Python. Verificar consulta a `http://172.16.3.127:3000` con credenciales de servicio, por un canal autorizado por TI.
4. Confirmar el significado de `cinchos`, la zona horaria y metas. No publicar alertas basadas en contadores no validados.
5. Configurar la ingesta autorizada a Supabase. Se recomienda un endpoint Edge Function con credencial limitada de ingestión y registros de auditoría; **no colocar service_role key ni token de Grafana ni URL privada del webhook en GitHub Pages**.
6. Adaptar Power Automate: el disparador de webhook de Teams admite tarjetas Adaptive Card. Añadir transformación para Outlook de la misma carga, probar con datos claramente marcados.
7. Programar el proceso en equipo o servidor interno que permanezca encendido, con comprobación de ejecuciones y reintentos idempotentes.

## SQL/seguridad
- `oc_machine_hourly`: clave compuesta `machine,slot` para escrituras idempotentes.
- Lecturas RLS limitadas al dominio TATA, escrituras de configuración a admins autorizados.
- No modificar tablas de otros proyectos ni exponer datos en archivos estáticos.
- **Aviso ajeno a Cantos:** la inspección de Supabase encontró 4 tablas `engineering_balance_*` con RLS desactivado. No se tocaron; evaluar políticas antes de habilitarlo (puede afectar aplicaciones en uso).

## Prueba rápida
Comprobar el acceso al dashboard, luego revisar en Supabase Table Editor las 11 filas de `oc_machine_config`. `oc_machine_hourly` debe permanecer vacía hasta que el sincronizador lea INTEQ.
