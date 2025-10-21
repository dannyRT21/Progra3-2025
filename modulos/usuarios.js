// usuarios.js
var accionUsuario = "nuevo",
    idUsuario = 0;

document.addEventListener("DOMContentLoaded", event => {
  if (typeof frmUsuarios !== "undefined") {
    frmUsuarios.addEventListener("submit", (e) => {
      e.preventDefault();
      guardarUsuarios();
    });
  }
  obtenerUsuarios();
});
  
function limpiarFormularioUsuarios() {
  accionUsuario = "nuevo";
  idUsuario = 0;
  if (typeof txtUsuario !== "undefined") txtUsuario.value = "";
  if (typeof txtClave !== "undefined") txtClave.value = "";
  if (typeof txtNombreUsuario !== "undefined") txtNombreUsuario.value = "";
  if (typeof txtDireccionUsuario !== "undefined") txtDireccionUsuario.value = "";
  if (typeof txtTelefonoUsuario !== "undefined") txtTelefonoUsuario.value = "";
}

async function guardarUsuarios() {
  const accionLocal = accionUsuario;
  let payload;

  if (accionLocal === "eliminar") {
    payload = { accion: "eliminar", idUsuario };
  } else {
    const res = validarYNormalizarUsuario();
    if (!res.ok) {
      if (typeof alertify !== "undefined") alertify.error(res.msg);
      return false;
    }

    const v = res.values;
    if (accionLocal === "modificar" && !v.clave) {
      const msg = "La CLAVE es requerida al modificar.";
      if (typeof alertify !== "undefined") alertify.error(msg);
      return false;
    }

    payload = {
      accion: accionLocal,
      idUsuario,
      usuario: v.usuario,
      clave: v.clave,
      nombre: v.nombre,
      direccion: v.direccion,
      telefono: v.telefono
    };
  }

  try {
    const resp = await fetch("/usuarios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const r = await resp.json();

    if (r.msg !== "ok") {
      if (typeof alertify !== "undefined") alertify.error(`Error al procesar usuario: ${r.msg || JSON.stringify(r)}`);
      return false;
    }

    limpiarFormularioUsuarios();
    if (typeof obtenerUsuarios === "function") obtenerUsuarios();
    accionUsuario = "nuevo";

    if (typeof alertify !== "undefined" && accionLocal !== "eliminar")
      alertify.success("Usuario guardado correctamente");

    return true;

  } catch (err) {
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("Error de red o del servidor.");
    return false;
  }
}

async function obtenerUsuarios() {
  try {
    const resp = await fetch("/usuarios");
    const lista = await resp.json();
    mostrarDatosUsuarios(lista);
  } catch (err) {
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("Error al obtener usuarios.");
  }
}

function mostrarDatosUsuarios(lista) {
  if (typeof tblUsuarios === "undefined") return;
  let filas = "";
  lista.forEach(u => {
    filas += `
      <tr onClick='mostrarUsuario(${JSON.stringify(u)})'>
        <td>${escapeHtml(u.usuario)}</td>
        <td>${escapeHtml(u.nombre)}</td>
        <td>${escapeHtml(u.direccion ?? "")}</td>
        <td>${escapeHtml(u.telefono ?? "")}</td>
        <td>
          <button type="button"
                  onClick='eliminarUsuario(${JSON.stringify(u)}, event)'
                  class="btn btn-outline-danger btn-sm">ELIMINAR</button>
        </td>
      </tr>`;
  });
  tblUsuarios.innerHTML = filas;
}

function mostrarUsuario(u) {
  accionUsuario = "modificar";
  if (typeof txtUsuario !== "undefined") txtUsuario.value = u.usuario ?? "";
  if (typeof txtClave !== "undefined") txtClave.value = "";
  if (typeof txtNombreUsuario !== "undefined") txtNombreUsuario.value = u.nombre ?? "";
  if (typeof txtDireccionUsuario !== "undefined") txtDireccionUsuario.value = u.direccion ?? "";
  if (typeof txtTelefonoUsuario !== "undefined") txtTelefonoUsuario.value = u.telefono ?? "";

  if (typeof alertify !== "undefined") alertify.success(`Usuario "${u.nombre}" cargado para editar`);
}

function eliminarUsuario(u, event) {
  if (event) {
    event.preventDefault();
    if (event.stopPropagation) event.stopPropagation();
  }
  if (!confirm(`¿Está seguro de eliminar al usuario ${u.nombre}?`)) return;

  idUsuario = u.idUsuario ?? u.id ?? 0;
  accionUsuario = "eliminar";
  guardarUsuarios();
}
  window.escapeHtml = function (str){
    if (str === null || str === undefined) return "";
    return String(str)
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll('"',"&quot;")
      .replaceAll("'","&#039;");
  };

