document.addEventListener("DOMContentLoaded", function () {


  const countrySelect = document.getElementById("country");
  const stateSelect = document.getElementById("state");
  const citySelect = document.getElementById("city");

  const passportRow = document.getElementById("passport_row");
  const passportInput = document.getElementById("id_passportNumber");

  const OTHER = "__other__";

  // ✅ Saved values from Django (important for refresh)
  const selectedCountry = countrySelect.dataset.selected || "";
  const selectedState = stateSelect.dataset.selected || "";
  const selectedCity = citySelect.dataset.selected || "";

  /* ---------------- MANUAL INPUT TOGGLE ---------------- */
function setupOther(selectId, inputId) {
  const select = document.getElementById(selectId);
  const input = document.getElementById(inputId);

  if (!select || !input) return;

  function toggleInput() {
    if (select.value === OTHER) {
      input.classList.remove("d-none");
      input.required = true;
    } else {
      input.classList.add("d-none");
      input.required = false;
      input.value = "";
    }
  }

  select.addEventListener("change", toggleInput);

  // Run once on load (important for refresh)
  toggleInput();
}

// Attach manual inputs
setupOther("country", "country_other");
setupOther("state", "state_other");
setupOther("city", "city_other");


document.querySelector("form").addEventListener("submit", function () {

  /* ---------------- OTHER (Country / State / City) ---------------- */
  ["country", "state", "city"].forEach(field => {
    const select = document.getElementById(field);
    const otherInput = document.getElementById(field + "_other");

    if (
      select &&
      otherInput &&
      select.value === OTHER &&
      otherInput.value.trim() !== ""
    ) {
      select.value = otherInput.value.trim();
    }
  });

  /* ---------------- PHONE COUNTRY CODE ---------------- */
  const codeSelect = document.getElementById("phone_country_code");
  const phoneInput = document.getElementById("id_phone_number");

  if (codeSelect && phoneInput) {
    const rawNumber = phoneInput.value.replace(/\D/g, "");

    if (rawNumber) {
      phoneInput.value = codeSelect.value + rawNumber;
    }
  }

});



  /* ---------------- PASSPORT TOGGLE ---------------- */
  function togglePassport() {
    const country = countrySelect.value;

    if (country && country !== "India") {
      passportRow.style.display = "flex";
      passportInput.required = true;
    } else {
      passportRow.style.display = "none";
      passportInput.required = false;
      passportInput.value = "";
    }
  }

  /* ---------------- OTHER OPTION ---------------- */
  function addOtherOption(select) {
    const option = document.createElement("option");
    option.value = OTHER;
    option.textContent = "Other (Enter manually)";
    select.appendChild(option);
  }

  /* ---------------- LOAD COUNTRIES ---------------- */
  fetch("https://countriesnow.space/api/v0.1/countries/positions")
    .then(res => res.json())
    .then(data => {

      countrySelect.innerHTML = '<option value="">Select Country</option>';

      data.data.forEach(country => {
        const option = document.createElement("option");
        option.value = country.name;
        option.textContent = country.name;

        // Restore selected country OR default India
        if (
          country.name === selectedCountry ||
          (!selectedCountry && country.name === "India")
        ) {
          option.selected = true;
        }

        countrySelect.appendChild(option);
      });

      addOtherOption(countrySelect);

      // 🔥 Load states for selected country
      countrySelect.dispatchEvent(new Event("change"));
    });

  /* ---------------- COUNTRY CHANGE ---------------- */
  countrySelect.addEventListener("change", function () {

    togglePassport();

    stateSelect.innerHTML = '<option value="">Select State</option>';
    citySelect.innerHTML = '<option value="">Select City</option>';

    if (!this.value || this.value === OTHER) {
      addOtherOption(stateSelect);
      addOtherOption(citySelect);
      return;
    }

    

    fetch("https://countriesnow.space/api/v0.1/countries/states", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ country: this.value })
    })
      .then(res => res.json())
      .then(data => {
        console.log("STATE API RESPONSE:", data); // 🔥 DEBUG
        data.data.states.forEach(state => {
          const option = document.createElement("option");
          option.value = state.name;
          option.textContent = state.name;

          // Restore selected state
          if (state.name === selectedState) {
            option.selected = true;
          }

          stateSelect.appendChild(option);
        });

        addOtherOption(stateSelect);

        // 🔥 Load cities for selected state
        if (selectedState) {
          stateSelect.dispatchEvent(new Event("change"));
        }
      });
  });

  /* ---------------- STATE CHANGE ---------------- */
  stateSelect.addEventListener("change", function () {

    citySelect.innerHTML = '<option value="">Select City</option>';

    if (!this.value || this.value === OTHER) {
      addOtherOption(citySelect);
      return;
    }

    fetch("https://countriesnow.space/api/v0.1/countries/state/cities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        country: countrySelect.value,
        state: this.value
      })
    })
      .then(res => res.json())
      .then(data => {
          console.log("CITY API RESPONSE:", data);
        data.data.forEach(city => {
          const option = document.createElement("option");
          option.value = city;
          option.textContent = city;

          // Restore selected city
          if (city === selectedCity) {
            option.selected = true;
          }

          citySelect.appendChild(option);
        });

        addOtherOption(citySelect);
      });
  });


/* ---------------- LOAD PHONE COUNTRY CODES (SAFE API) ---------------- */
fetch("https://countriesnow.space/api/v0.1/countries/codes")
  .then(res => res.json())
  .then(data => {

    const phoneCodeSelect = document.getElementById("phone_country_code");
    const phoneInput = document.getElementById("id_phone_number");

    if (!phoneCodeSelect) return;

    phoneCodeSelect.innerHTML = '<option value="">Code</option>';

    // Add codes
    data.data.forEach(country => {
      if (!country.dial_code) return;

      const option = document.createElement("option");
      option.value = country.dial_code;
      option.textContent = `${country.name} (${country.dial_code})`;
      phoneCodeSelect.appendChild(option);
    });

    // ---------------- RESTORE PHONE CODE + NUMBER ----------------
    if (phoneInput && phoneInput.value.trim().startsWith("+")) {

      const fullPhone = phoneInput.value.trim();

      // Create list of codes from dropdown
      const codes = Array.from(phoneCodeSelect.options)
        .map(opt => opt.value)
        .filter(v => v);

      // Sort longest first
      codes.sort((a, b) => b.length - a.length);

      for (const code of codes) {
        if (fullPhone.startsWith(code)) {
          phoneCodeSelect.value = code;
          phoneInput.value = fullPhone.slice(code.length);
          break;
        }
      }
    }

    // Default to India ONLY if nothing selected
    if (!phoneCodeSelect.value) {
      phoneCodeSelect.value = "+91";
    }

  })
  .catch(err => console.error("Phone code load error:", err));


});
