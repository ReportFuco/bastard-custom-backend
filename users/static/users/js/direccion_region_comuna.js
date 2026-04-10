document.addEventListener("DOMContentLoaded", function () {
  var regionSelect = document.getElementById("id_region");
  var comunaSelect = document.getElementById("id_comuna");

  if (!regionSelect || !comunaSelect) {
    return;
  }

  var comunasUrl = regionSelect.getAttribute("data-comunas-url");
  if (!comunasUrl) {
    return;
  }

  var initialComunaId = comunaSelect.value;

  function renderComunas(comunas, selectedId) {
    comunaSelect.innerHTML = "";

    var emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "---------";
    comunaSelect.appendChild(emptyOption);

    comunas.forEach(function (comuna) {
      var option = document.createElement("option");
      option.value = String(comuna.id);
      option.textContent = comuna.nombre;
      if (selectedId && String(comuna.id) === String(selectedId)) {
        option.selected = true;
      }
      comunaSelect.appendChild(option);
    });
  }

  function loadComunas(regionId, selectedId) {
    if (!regionId) {
      renderComunas([], null);
      return;
    }

    var url = new URL(comunasUrl, window.location.origin);
    url.searchParams.set("region_id", regionId);

    fetch(url.toString(), {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("No se pudieron cargar las comunas");
        }
        return response.json();
      })
      .then(function (data) {
        renderComunas(data.comunas || [], selectedId);
      })
      .catch(function () {
        renderComunas([], null);
      });
  }

  regionSelect.addEventListener("change", function () {
    loadComunas(regionSelect.value, null);
  });

  loadComunas(regionSelect.value, initialComunaId);
});
