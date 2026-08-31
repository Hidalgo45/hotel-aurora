/* ==========================================================================
   HOTEL AURORA - Capa 1 de validacion (navegador)
   Da respuesta inmediata al usuario. NO sustituye la validacion de Flask
   ni las restricciones de PostgreSQL: es la primera de tres capas.
   ========================================================================== */
(function () {
  "use strict";

  const hoy = new Date().toISOString().split("T")[0];

  /* --- 1. Coherencia entre fecha de entrada y de salida ------------------ */
  document.querySelectorAll("form").forEach(function (form) {
    const entrada = form.querySelector('input[name="checkin"]');
    const salida = form.querySelector('input[name="checkout"]');
    if (!entrada || !salida) return;

    entrada.min = hoy;

    function sincronizar() {
      // La salida nunca puede ser anterior o igual a la entrada
      const minimoSalida = new Date(entrada.value || hoy);
      minimoSalida.setDate(minimoSalida.getDate() + 1);
      salida.min = minimoSalida.toISOString().split("T")[0];

      if (salida.value && salida.value <= entrada.value) {
        salida.value = salida.min;
      }
      actualizarNoches(form, entrada.value, salida.value);
    }

    entrada.addEventListener("change", sincronizar);
    salida.addEventListener("change", function () {
      actualizarNoches(form, entrada.value, salida.value);
    });
    sincronizar();
  });

  function actualizarNoches(form, desde, hasta) {
    const destino = form.querySelector("[data-noches]");
    if (!destino || !desde || !hasta) return;
    const dias = Math.round((new Date(hasta) - new Date(desde)) / 86400000);
    destino.textContent = dias + (dias === 1 ? " noche" : " noches");
  }

  /* --- 2. Aviso de capacidad antes de enviar el formulario --------------- */
  const formReserva = document.querySelector("[data-form-reserva]");
  if (formReserva) {
    const capacidad = parseInt(formReserva.dataset.capacidad, 10);
    const adultos = formReserva.querySelector('[name="adultos"]');
    const ninos = formReserva.querySelector('[name="ninos"]');
    const aviso = formReserva.querySelector("[data-aviso-capacidad]");

    function revisarCapacidad() {
      const total = parseInt(adultos.value || 0, 10) + parseInt(ninos.value || 0, 10);
      const excede = total > capacidad;

      if (aviso) {
        aviso.hidden = !excede;
        aviso.textContent = excede
          ? "Seleccionaste " + total + " huespedes y esta habitacion admite " +
            capacidad + ". Reduce el numero de personas o elige una habitacion mas amplia."
          : "";
      }
      formReserva.querySelectorAll('button[type="submit"]').forEach(function (b) {
        b.disabled = excede;
      });
    }

    [adultos, ninos].forEach(function (campo) {
      if (campo) campo.addEventListener("input", revisarCapacidad);
    });
    revisarCapacidad();
  }

  /* --- 3. Confirmacion antes de una accion irreversible ------------------ */
  document.querySelectorAll("[data-confirmar]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.dataset.confirmar)) {
        e.preventDefault();
      }
    });
  });

  /* --- 4. Validacion de formato en vivo (cedula, correo) ---------------- */
  document.querySelectorAll("input[pattern]").forEach(function (campo) {
    campo.addEventListener("blur", function () {
      const valido = campo.checkValidity();
      campo.classList.toggle("is-invalid", !valido && campo.value !== "");
      campo.classList.toggle("is-valid", valido && campo.value !== "");
    });
  });
})();
