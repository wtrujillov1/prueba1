# Informe técnico · Proyecta

**Universidad Politécnica Salesiana · 18 de octubre de 2026 · Modalidad remota**

## Objetivo y decisiones

Promocionar una feria de proyectos estudiantiles mediante cinco secciones: inicio, presentación, proyectos, programa y participación. La información de la institución, fecha y modalidad corresponde a los datos facilitados; los equipos, proyectos y horarios son ejemplos editables. El programa usa la hora de Ecuador (UTC−5).

Se eligió una aplicación estática de HTML5, CSS y JavaScript nativos, sin dependencias de ejecución ni recursos remotos. Los SVG originales son fluidos y la fuente Space Grotesk se distribuye localmente con licencia SIL OFL. La paleta combina fondo claro, azul para las acciones y verde para los acentos; las tarjetas y los espacios facilitan la exploración.

HTML utiliza `header`, `nav`, `main`, `section`, `article`, `aside` y `footer`, un solo `h1` y una jerarquía sin saltos. La navegación apunta a destinos existentes. Las imágenes informativas tienen alternativas textuales; la marca decorativa usa `alt=""`. El formulario asocia cada control a una etiqueta y sus mensajes de error con `aria-describedby`.

CSS parte de una columna en móvil, centraliza colores y medidas en variables y utiliza Grid y Flexbox. A 640 px aparecen dos columnas de proyectos y tres características; a 1024 px se muestran navegación permanente, bloques en paralelo y tres tarjetas; a 1280 px se amplían la cabecera y el espacio del inicio. Los cambios responden al espacio que necesita el contenido, sin depender de modelos de dispositivos.

JavaScript incorpora menú con `aria-expanded`, cierre con Escape y traslado del foco a la sección seleccionada; filtros con `aria-pressed` y contador anunciado; validación con errores asociados, foco en el primer campo inválido y respuesta en una región viva. Se respeta la preferencia de movimiento reducido. Sin JavaScript quedan disponibles navegación, proyectos y programa; el registro de demostración permanece desactivado.

## Pruebas y resultados

La prueba `tests/verify.py` inicia un servidor temporal, usa Chromium con Playwright y guarda evidencia en `docs/resultados-pruebas.json`.

- **16 grupos de comprobaciones aprobados.** No se detectaron errores de JavaScript, solicitudes fallidas ni recursos externos.
- **HTML y JavaScript:** html-validate 11.16.2 sin errores; `node --check` aprobado.
- **Adaptación:** capturas completas a 390, 768 y 1440 px. Sin desbordamiento horizontal también a 320, 640, 1024, 1280 y 1920 px.
- **Teclado:** salto al contenido, foco visible, menú con Enter y Escape, llegada a la sección seleccionada y filtros con Espacio. Se corrigió la pérdida de foco al cerrar el menú móvil.
- **Formulario:** cuatro campos obligatorios, nombre con solo espacios, correo inválido, foco del primer error, caso válido y limpieza. Se comprobó que no transmite ni guarda datos en almacenamiento del navegador.
- **Accesibilidad:** axe-core 4.14.0, con reglas WCAG A/AA y buenas prácticas, no detectó infracciones en los tres anchos. Los símbolos decorativos que la herramienta no evalúa se revisaron por separado. Nueve combinaciones de texto/fondo superan 4,5:1; la menor medida es 5,06:1.
- **Ampliación:** texto al 200 % a 390 px sin desbordamiento. Reflujo equivalente a zoom del 200 % en pantalla de 1440 px mediante viewport de 720 píxeles CSS y DPR 2. No se presenta esta simulación como una prueba directa del zoom del navegador.
- **Alternativas:** contenido disponible sin JavaScript y desplazamiento suave desactivado con movimiento reducido.

## Mejoras y límites

Para una feria real, sustituir los proyectos y horarios de ejemplo, publicar el enlace de las salas virtuales y conectar el registro a un servicio con validación en servidor y consentimiento apropiado. El formulario actual es una demostración explícita, no una inscripción real.

Las pruebas se ejecutaron en Chromium. Como siguiente mejora, revisar con Firefox, WebKit y un lector de pantalla real. La auditoría automática complementa la revisión visual y no equivale a una certificación de accesibilidad.

**Entregables:** código en el repositorio, capturas `movil-390.png`, `tableta-768.png`, `escritorio-1440.png`, resultados reproducibles y este informe en PDF de dos páginas.
