// materias.js
var accionMateria = "nuevo",
    idMateria = 0;

document.addEventListener("DOMContentLoaded", () => {
  // Listeners del form
  if (typeof frmMaterias !== "undefined"){
    frmMaterias.addEventListener("submit", (e)=>{
      e.preventDefault();
      guardarMaterias();
    });
  }

  if (typeof btnBuscarMateria !== "undefined"){
    btnBuscarMateria.addEventListener("click", (e)=>{
      e.preventDefault();
      if (typeof abrirVentana === "function") abrirVentana('busqueda_materias');
    });
  }

  if (typeof txtCodigoMateria !== "undefined"){
    txtCodigoMateria.addEventListener("input", (e)=>{
      e.target.value = (e.target.value || "").slice(0,10);
    });
  }

  // cargar combo docentes
  cargarDocentesCombo();
});

// ---- Helpers ----
async function cargarDocentesCombo(){
  try{
    const resp = await fetch("/docentes");
    const lista = await resp.json();
    if (typeof cmbDocente === "undefined") return;

    const selPrevio = cmbDocente.value || "";
    let opts = `<option value="">-- Seleccione un docente --</option>`;
    lista.forEach(d=>{
      const id = d.idDocente ?? d.id ?? "";
      const nombre = d.nombre ?? d.nombre_docente ?? "";
      opts += `<option value="${id}">${nombre}</option>`;
    });
    cmbDocente.innerHTML = opts;
    if (selPrevio) cmbDocente.value = selPrevio;
  }catch(err){
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("No se pudieron cargar los docentes.");
  }
}

function limpiarFormularioMaterias(){
  accionMateria = "nuevo";
  idMateria = 0;
  if (typeof txtCodigoMateria !== "undefined") txtCodigoMateria.value = "";
  if (typeof txtNombreMateria !== "undefined") txtNombreMateria.value = "";
  if (typeof cmbDocente !== "undefined") cmbDocente.value = "";
}

// ---- CRUD ----
async function guardarMaterias(){
  const accionLocal = accionMateria;

  if (accionLocal === "eliminar"){
    const payload = { accion: "eliminar", idMateria };
    const ok = await postMateria(payload);
    if (ok){
      limpiarFormularioMaterias();
      if (typeof obtenerMaterias === "function") obtenerMaterias();
      accionMateria = "nuevo";
    }
    return ok;
  }

  const res = validarYNormalizarMateria();
  if (!res.ok){
    if (typeof alertify !== "undefined") alertify.error(res.msg);
    return false;
  }

  const v = res.values;
  const payload = {
    accion: accionLocal, // "nuevo" | "modificar"
    idMateria,
    codigo: v.codigo,
    nombre: v.nombre,
    idDocente: v.idDocente
  };

  const ok = await postMateria(payload);
  if (ok){
    limpiarFormularioMaterias();
    if (typeof obtenerMaterias === "function") obtenerMaterias();
    accionMateria = "nuevo";
  }
  return ok;
}

async function postMateria(data){
  try{
    const response = await fetch("/materias", {
      method: "POST",
      body: JSON.stringify(data),
    });
    const r = await response.json();
    if (r.msg !== "ok"){
      if (typeof alertify !== "undefined") alertify.error(`Error al procesar materia: ${JSON.stringify(r)}`);
      return false;
    }
    if (typeof alertify !== "undefined"){
      const accionTxt = data.accion === "eliminar" ? "Eliminada" : (data.accion === "modificar" ? "Actualizada" : "Guardada");
      alertify.success(`Materia ${accionTxt} correctamente`);
    }
    return true;
  }catch(err){
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("Error de comunicación con el servidor.");
    return false;
  }
}

// Validación / Normalización
function validarYNormalizarMateria(){
  const codigo = (typeof txtCodigoMateria !== "undefined" ? (txtCodigoMateria.value || "").trim() : "");
  const nombre = (typeof txtNombreMateria !== "undefined" ? (txtNombreMateria.value || "").trim() : "");
  const idDocenteSel = (typeof cmbDocente !== "undefined" ? (cmbDocente.value || "").trim() : "");

  if (!codigo) return { ok:false, msg: "El CÓDIGO es requerido." };
  if (codigo.length > 10) return { ok:false, msg: "El CÓDIGO debe tener como máximo 10 caracteres." };
  if (!nombre) return { ok:false, msg: "El NOMBRE es requerido." };
  if (!idDocenteSel) return { ok:false, msg: "Debe seleccionar un DOCENTE." };

  if (typeof txtCodigoMateria !== "undefined") txtCodigoMateria.value = codigo;
  if (typeof txtNombreMateria !== "undefined") txtNombreMateria.value = nombre;
  if (typeof cmbDocente !== "undefined") cmbDocente.value = idDocenteSel;

  return {
    ok:true,
    values:{
      codigo,
      nombre,
      idDocente: Number(idDocenteSel)
    }
  };
}

// Cargar datos en el form desde la tabla de búsqueda
function mostrarMateria(materia){
  accionMateria = "modificar";
  idMateria = materia.idMateria ?? materia.id ?? 0;

  const codigo = materia.codigo ?? "";
  const nombre = materia.nombre ?? materia.nombre_materia ?? "";
  const idDoc = materia.idDocente ?? materia.id_docente ?? "";

  if (typeof txtCodigoMateria !== "undefined") txtCodigoMateria.value = codigo;
  if (typeof txtNombreMateria !== "undefined") txtNombreMateria.value = nombre;

  if (typeof cmbDocente !== "undefined"){
    if (!cmbDocente.options.length){
      cargarDocentesCombo().then(()=>{ cmbDocente.value = idDoc; });
    }else{
      cmbDocente.value = idDoc;
    }
  }
  if (typeof alertify !== "undefined") alertify.success(`Materia "${nombre}" cargada para editar`);
}

// Eliminar desde tabla (si se desea usar fuera de la vista de búsqueda)
function eliminarMateria(materia, event){
  if (event){
    event.preventDefault();
    if (event.stopPropagation) event.stopPropagation();
  }
  const nombreMateria = materia.nombre ?? materia.nombre_materia ?? "la materia";
  if (!confirm(`¿Está seguro de eliminar "${nombreMateria}"?`)) return;

  idMateria = materia.idMateria ?? materia.id ?? 0;
  accionMateria = "eliminar";
  guardarMaterias();
}
