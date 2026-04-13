document.addEventListener("DOMContentLoaded", function () {
  var categoriaSelect = document.getElementById("id_categoria");
  var subcategoriaSelect = document.getElementById("id_subcategoria");

  if (!categoriaSelect || !subcategoriaSelect) {
    return;
  }

  var subcategoriasUrl = categoriaSelect.getAttribute("data-subcategorias-url");
  if (!subcategoriasUrl) {
    return;
  }

  var initialSubcategoriaId = subcategoriaSelect.value;

  function renderSubcategorias(subcategorias, selectedId) {
    subcategoriaSelect.innerHTML = "";

    var emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "---------";
    subcategoriaSelect.appendChild(emptyOption);

    subcategorias.forEach(function (subcategoria) {
      var option = document.createElement("option");
      option.value = String(subcategoria.id);
      option.textContent = subcategoria.nombre;
      if (selectedId && String(subcategoria.id) === String(selectedId)) {
        option.selected = true;
      }
      subcategoriaSelect.appendChild(option);
    });
  }

  function loadSubcategorias(categoriaId, selectedId) {
    if (!categoriaId) {
      renderSubcategorias([], null);
      return;
    }

    var url = new URL(subcategoriasUrl, window.location.origin);
    url.searchParams.set("categoria_id", categoriaId);

    fetch(url.toString(), {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("No se pudieron cargar las subcategorias");
        }
        return response.json();
      })
      .then(function (data) {
        renderSubcategorias(data.subcategorias || [], selectedId);
      })
      .catch(function () {
        renderSubcategorias([], null);
      });
  }

  categoriaSelect.addEventListener("change", function () {
    loadSubcategorias(categoriaSelect.value, null);
  });
  categoriaSelect.addEventListener("input", function () {
    loadSubcategorias(categoriaSelect.value, null);
  });

  loadSubcategorias(categoriaSelect.value, initialSubcategoriaId);
});
