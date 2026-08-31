/**
 * Hotel Aurora - Generador de la encuesta de usabilidad
 * Proyecto Integrador PUCE TEC
 *
 * COMO USARLO
 *   1. Entra a  https://script.google.com  con tu cuenta de Google
 *   2. Nuevo proyecto
 *   3. Borra todo lo que aparezca y pega este archivo completo
 *   4. Guarda (Ctrl+S) y presiona Ejecutar
 *   5. La primera vez Google pide permiso: Revisar permisos -> tu cuenta ->
 *      "Configuracion avanzada" -> "Ir a (nombre del proyecto)" -> Permitir
 *   6. Abre Ver -> Registro de ejecucion. Ahi salen los dos enlaces:
 *      el de editar y el que se comparte con los participantes
 *
 * El cuestionario SUS (System Usability Scale) alterna afirmaciones
 * positivas y negativas a proposito: detecta a quien responde en automatico
 * sin leer. NO cambies el orden ni la redaccion, porque la formula del
 * puntaje depende de que las impares sean positivas y las pares negativas.
 */

function crearEncuesta() {
  var form = FormApp.create('Prueba de usabilidad - Hotel Aurora');

  form.setDescription(
    'Gracias por ayudarnos. Esta encuesta toma unos 3 minutos.\n\n' +
    'No hay respuestas correctas ni incorrectas: estamos evaluando el ' +
    'sistema, no a ti. Si algo te costo trabajo, es informacion valiosa ' +
    'para nosotros.\n\n' +
    'Importante: responde despues de haber usado el sistema.');

  form.setCollectEmail(false);
  form.setProgressBar(true);

  // =====================================================================
  // SECCION 1 - Contexto del participante
  // =====================================================================
  form.addSectionHeaderItem()
      .setTitle('1. Sobre tu prueba')
      .setHelpText('Necesitamos saber en que condiciones usaste el sistema.');

  form.addMultipleChoiceItem()
      .setTitle('En que dispositivo probaste el sistema?')
      .setChoiceValues(['Celular', 'Tablet',
                        'Computador portatil', 'Computador de escritorio'])
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Que navegador usaste?')
      .setChoiceValues(['Chrome', 'Edge', 'Safari', 'Firefox'])
      .showOtherOption(true)
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Cuantas de las 5 tareas lograste completar sin ayuda?')
      .setHelpText('Buscar una habitacion, reservar, provocar un error, ' +
                   'encontrar tu codigo y cancelar.')
      .setChoiceValues(['0', '1', '2', '3', '4', '5'])
      .setRequired(true);

  // =====================================================================
  // SECCION 2 - Cuestionario SUS (10 afirmaciones, escala 1 a 5)
  // =====================================================================
  form.addPageBreakItem()
      .setTitle('2. Tu opinion del sistema')
      .setHelpText('Marca que tan de acuerdo estas con cada afirmacion. ' +
                   'Responde con tu primera impresion, sin pensarlo mucho.');

  var afirmaciones = [
    'Me resulto facil reservar una habitacion en este dispositivo.',
    'El sistema me parecio innecesariamente complejo.',
    'Los textos y botones se leian bien sin necesidad de hacer zoom.',
    'Necesite ayuda de alguien para completar la reserva.',
    'Las secciones del sitio se comportan de forma coherente entre si.',
    'Encontre incoherencias o elementos fuera de lugar en la pantalla.',
    'Creo que cualquier persona aprenderia a usarlo rapidamente.',
    'Me senti inseguro o insegura al confirmar la reserva.',
    'Los mensajes de error me dijeron con claridad como corregir el problema.',
    'Tuve que desplazarme horizontalmente o buscar contenido cortado.'
  ];

  for (var i = 0; i < afirmaciones.length; i++) {
    form.addScaleItem()
        .setTitle((i + 1) + '. ' + afirmaciones[i])
        .setBounds(1, 5)
        .setLabels('Muy en desacuerdo', 'Muy de acuerdo')
        .setRequired(true);
  }

  // =====================================================================
  // SECCION 3 - Preguntas abiertas
  // =====================================================================
  form.addPageBreakItem()
      .setTitle('3. Para terminar')
      .setHelpText('Estas tres son las que mas nos sirven para mejorar.');

  form.addTextItem()
      .setTitle('Hubo algun boton difícil de presionar? Cual?')
      .setHelpText('Si no hubo ninguno, escribe "ninguno".')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Alguna imagen o tabla se salio de la pantalla?')
      .setHelpText('Si no paso, escribe "no".')
      .setRequired(true);

  form.addScaleItem()
      .setTitle('Del 1 al 10, que tan probable es que recomiendes este sitio?')
      .setBounds(1, 10)
      .setLabels('Nada probable', 'Muy probable')
      .setRequired(true);

  form.addParagraphTextItem()
      .setTitle('Si pudieras cambiar una sola cosa del sistema, cual seria?')
      .setRequired(false);

  // =====================================================================
  // Resultado
  // =====================================================================
  Logger.log('=========================================================');
  Logger.log('FORMULARIO CREADO');
  Logger.log('');
  Logger.log('Enlace para EDITAR (solo tu):');
  Logger.log(form.getEditUrl());
  Logger.log('');
  Logger.log('Enlace para COMPARTIR con los participantes:');
  Logger.log(form.getPublishedUrl());
  Logger.log('=========================================================');
  Logger.log('Siguiente paso: abre el formulario, pestana Respuestas,');
  Logger.log('e icono verde de hoja de calculo para vincularla.');
}
