/*
AUTHOR: JAY SAWANT
PROJECT: DTTDC (CAR BOOKING)

THIS IS A SCRIPT FOR PHONE NUMBER VALIDATIONS
*/

document.addEventListener("DOMContentLoaded", function () {

  const input = document.getElementById("id_phone_number");
  if (!input) return; // ✅ prevent crash

  const form = input.closest("form");
  const errorBox = document.getElementById("phone-error");

  const iti = window.intlTelInput(input, {
    initialCountry: "in",
    separateDialCode: true,
    nationalMode: false,
    utilsScript:
      "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.19/js/utils.js",
  });

  function showError(message) {
    input.classList.add("is-invalid");
    errorBox.textContent = message;
    errorBox.classList.remove("d-none");
    input.scrollIntoView({ behavior: "smooth", block: "center" });
    input.focus();
  }

  function clearError() {
    input.classList.remove("is-invalid");
    errorBox.textContent = "";
    errorBox.classList.add("d-none");
  }

  // 🔒 BLOCK ALPHABETS
  input.addEventListener("keypress", function (e) {
    const char = String.fromCharCode(e.which);
    if (!/[0-9]/.test(char)) {
      e.preventDefault();
    }
  });

  // 🔒 BLOCK INVALID PASTE
  input.addEventListener("paste", function (e) {
    const pasted = (e.clipboardData || window.clipboardData).getData("text");
    if (!/^\d+$/.test(pasted.replace(/\s+/g, ""))) {
      e.preventDefault();
    }
  });

  // 🔄 Clear error on typing
  input.addEventListener("input", clearError);
  input.addEventListener("change", clearError);

  // ✅ FORM SUBMIT VALIDATION
  if (form) {
    form.addEventListener("submit", function (e) {

      if (!iti.isValidNumber()) {
        e.preventDefault();

        let msg = "Enter a valid phone number.";
        const errorCode = iti.getValidationError();

        if (errorCode === intlTelInputUtils.validationError.TOO_SHORT) {
          msg = "Phone number is too short.";
        } else if (errorCode === intlTelInputUtils.validationError.TOO_LONG) {
          msg = "Phone number is too long.";
        } else if (errorCode === intlTelInputUtils.validationError.INVALID_COUNTRY_CODE) {
          msg = "Invalid country code.";
        }

        showError(msg);
        return;
      }

      // ✅ valid → convert to E.164
      input.value = iti.getNumber();
    });
  }

});