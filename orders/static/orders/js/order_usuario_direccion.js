(function () {
  function setDireccionOptions(select, items, selectedValue) {
    select.innerHTML = '';

    var emptyOption = document.createElement('option');
    emptyOption.value = '';
    emptyOption.textContent = '---------';
    select.appendChild(emptyOption);

    items.forEach(function (item) {
      var option = document.createElement('option');
      option.value = String(item.id);
      option.textContent = item.texto;
      if (selectedValue && String(selectedValue) === String(item.id)) {
        option.selected = true;
      }
      select.appendChild(option);
    });
  }

  function loadDirecciones(userSelect, direccionSelect, selectedValue) {
    var userId = userSelect.value;
    var endpoint = userSelect.dataset.direccionesUrl;

    if (!endpoint || !userId) {
      setDireccionOptions(direccionSelect, [], null);
      return;
    }

    fetch(endpoint + '?user_id=' + encodeURIComponent(userId), {
      credentials: 'same-origin'
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('No se pudo cargar direcciones');
        }
        return response.json();
      })
      .then(function (data) {
        var items = Array.isArray(data.direcciones) ? data.direcciones : [];
        setDireccionOptions(direccionSelect, items, selectedValue || direccionSelect.value);
      })
      .catch(function () {
        setDireccionOptions(direccionSelect, [], null);
      });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var userSelect = document.getElementById('id_user');
    var direccionSelect = document.getElementById('id_direccion_envio');

    if (!userSelect || !direccionSelect) {
      return;
    }

    var initialDireccion = direccionSelect.value;
    loadDirecciones(userSelect, direccionSelect, initialDireccion);

    userSelect.addEventListener('change', function () {
      loadDirecciones(userSelect, direccionSelect, null);
    });
  });
})();
