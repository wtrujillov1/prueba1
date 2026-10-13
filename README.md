# Proyecta · Feria de proyectos estudiantiles

Sitio académico para la **Universidad Politécnica Salesiana**, con fecha **18 de octubre de 2026** y modalidad **remota**. Incluye cinco secciones: inicio, la feria, proyectos, programa y participación. Los proyectos y los horarios son ejemplos editables; el horario se expresa en hora de Ecuador (UTC−5).

## Ejecutar

El sitio utiliza HTML5, CSS y JavaScript nativos. No necesita compilación, paquetes de ejecución, claves ni servicios externos. Las ilustraciones SVG y la fuente están incluidas localmente.

```sh
cd /workspace/prueba1
python3 -m http.server 8000 --bind 127.0.0.1
```

También puede abrirse `index.html` directamente en un navegador. Para publicarlo, sirve el contenido de esta carpeta en un alojamiento estático con HTTPS.

## Archivos y entregables

- `index.html`: estructura semántica y contenido.
- `styles.css`: variables, estilos mobile first y adaptaciones a 640, 1024 y 1280 px.
- `script.js`: menú adaptable, filtros y validación accesible.
- `assets/`: ilustraciones propias y Space Grotesk, distribuida con su licencia SIL OFL.
- [Informe técnico de dos páginas](docs/informe-tecnico.pdf).
- Capturas completas: [390 px](docs/capturas/movil-390.png), [768 px](docs/capturas/tableta-768.png) y [1440 px](docs/capturas/escritorio-1440.png).
- [Resultados de las pruebas](docs/resultados-pruebas.json) y [pruebas reproducibles](tests/verify.py).

## Verificación

La aplicación no depende de estas herramientas; son auxiliares para las pruebas. La máquina actual dispone de Chromium y Playwright. En otra máquina, instala las herramientas en un entorno virtual y en una carpeta temporal:

```sh
python3 -m venv /tmp/proyecta-venv
/tmp/proyecta-venv/bin/pip install -r tests/requirements.txt
/tmp/proyecta-venv/bin/python -m playwright install chromium
npm install --prefix /tmp/proyecta-validation --cache /tmp/proyecta-npm-cache --no-audit --no-fund --package-lock=false html-validate@11.16.2 axe-core@4.14.0
/tmp/proyecta-validation/node_modules/.bin/html-validate index.html
node --check script.js
/tmp/proyecta-venv/bin/python tests/verify.py --axe /tmp/proyecta-validation/node_modules/axe-core/axe.min.js
```

La prueba usa `/usr/bin/chromium` cuando existe; en caso contrario, usa el navegador de Playwright. Puede elegirse otro ejecutable con `PROYECTA_CHROMIUM`. El script inicia y cierra su propio servidor temporal, comprueba comportamientos reales y regenera capturas y resultados. No transmite los datos de prueba.

Se verifican navegación con teclado, foco, menú y Escape, filtros, validación, etiquetas, jerarquía de encabezados, recursos locales, contraste, ausencia de desbordamiento, ampliación del texto al 200 %, reflujo equivalente a zoom del 200 %, movimiento reducido y funcionamiento sin JavaScript. La auditoría automática complementa la revisión visual; no constituye una certificación de accesibilidad ni una prueba de todos los navegadores.

## Personalizar y recibir inscripciones

Edita los textos, equipos, proyectos, horarios y enlace del evento en `index.html`. La identidad visual se configura mediante las variables de `styles.css`.

El formulario es una **demostración de validación**, identificada como tal en la interfaz. No envía ni conserva datos y no confirma inscripciones reales. Sin JavaScript permanece desactivado para evitar envíos accidentales. Para usarlo en una feria real, conecta un servicio de registro, añade validación en el servidor y sustituye la confirmación de demostración por el consentimiento correspondiente. Publica también el enlace real de acceso a las salas virtuales.
