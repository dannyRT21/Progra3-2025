// usuarios.js
var accionUsuario = "nuevo",
    idUsuario = 0;

document.addEventListener("DOMContentLoaded", () => {
  if (typeof frmUsuarios !== "undefined") {
    frmUsuarios.addEventListener("submit", (e) => {
      e.preventDefault();
      guardarUsuarios();
    });
  }

  if (typeof btnBuscarUsuario !== "undefined") {
    btnBuscarUsuario.addEventListener("click", (e) => {
      e.preventDefault();
      if (typeof abrirVentana === "function") abrirVentana("busqueda_usuarios");
    });
  }

  if (typeof txtTelefonoUsuario !== "undefined") {
    txtTelefonoUsuario.addEventListener("input", (e) => {
      const d = e.target.value.replace(/\D/g, "").slice(0, 8);
      e.target.value = d.length > 4 ? d.slice(0, 4) + "-" + d.slice(4) : d;
    });
  }

  if (typeof obtenerUsuarios === "function" && typeof tblUsuarios !== "undefined") {
    obtenerUsuarios();
  }
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

function validarYNormalizarUsuario() {
  const usuario = (typeof txtUsuario !== "undefined" ? txtUsuario.value.trim() : "");
  const clave = (typeof txtClave !== "undefined" ? txtClave.value.trim() : "");
  const nombre = (typeof txtNombreUsuario !== "undefined" ? txtNombreUsuario.value.trim() : "");
  const direccion = (typeof txtDireccionUsuario !== "undefined" ? txtDireccionUsuario.value.trim() : "");
  let telefono = (typeof txtTelefonoUsuario !== "undefined" ? txtTelefonoUsuario.value.trim() : "");

  if (!usuario) return { ok: false, msg: "El USUARIO es requerido." };
  if (!nombre) return { ok: false, msg: "El NOMBRE es requerido." };
  if (accionUsuario === "nuevo" && !clave) return { ok: false, msg: "La CLAVE es requerida." };

  if (telefono) {
    const telDigits = telefono.replace(/\D/g, "").slice(0, 8);
    if (telDigits.length !== 8) return { ok: false, msg: "El TELÉFONO debe tener 8 dígitos (formato 1234-5678)." };
    telefono = telDigits.slice(0, 4) + "-" + telDigits.slice(4);
  }

  if (typeof txtTelefonoUsuario !== "undefined") txtTelefonoUsuario.value = telefono;

  return { ok: true, values: { usuario, clave, nombre, direccion, telefono } };
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
  idUsuario = u.idUsuario ?? u.id ?? 0;

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

function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
