// notas.js
var accionNota = "nuevo",
    idNota = 0;

document.addEventListener("DOMContentLoaded", () => {
  // Listeners del form si existen en el DOM
  if (typeof frmNotas !== "undefined"){
    frmNotas.addEventListener("submit", (e)=>{
      e.preventDefault();
      guardarNotas();
    });
  }

  if (typeof btnBuscarNota !== "undefined"){
    btnBuscarNota.addEventListener("click", (e)=>{
      e.preventDefault();
      if (typeof abrirVentana === "function") abrirVentana('busqueda_notas');
    });
  }

  // cargar combos
  cargarAlumnosCombo();
  cargarMateriasCombo();
});

// ---- Helpers ----
async function cargarAlumnosCombo(){
  try{
    const resp = await fetch("/alumnos");
    const lista = await resp.json();
    if (typeof cmbAlumno === "undefined") return;

    const selPrevio = cmbAlumno.value || "";
    let opts = `<option value="">-- Seleccione un alumno --</option>`;
    lista.forEach(a=>{
      const id = a.idAlumno ?? a.id ?? "";
      const nombre = a.nombre ?? a.nombre_alumno ?? "";
      opts += `<option value="${id}">${nombre}</option>`;
    });
    cmbAlumno.innerHTML = opts;
    if (selPrevio) cmbAlumno.value = selPrevio;
  }catch(err){
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("No se pudieron cargar los alumnos.");
  }
}

async function cargarMateriasCombo(){
  try{
    const resp = await fetch("/materias");
    const lista = await resp.json();
    if (typeof cmbMateria === "undefined") return;

    const selPrevio = cmbMateria.value || "";
    let opts = `<option value="">-- Seleccione una materia --</option>`;
    lista.forEach(m=>{
      const id = m.idMateria ?? m.id ?? "";
      const nombre = m.nombre ?? m.nombre_materia ?? "";
      opts += `<option value="${id}">${nombre}</option>`;
    });
    cmbMateria.innerHTML = opts;
    if (selPrevio) cmbMateria.value = selPrevio;
  }catch(err){
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("No se pudieron cargar las materias.");
  }
}

function limpiarFormularioNotas(){
  accionNota = "nuevo";
  idNota = 0;
  if (typeof cmbAlumno !== "undefined") cmbAlumno.value = "";
  if (typeof cmbMateria !== "undefined") cmbMateria.value = "";
  if (typeof txtNota !== "undefined") txtNota.value = "";
  if (typeof cmbAprobado !== "undefined") cmbAprobado.value = "";
}

// ---- CRUD ----
async function guardarNotas(){
  const accionLocal = accionNota;

  if (accionLocal === "eliminar"){
    const payload = { accion: "eliminar", idNota };
    const ok = await postNota(payload);
    if (ok){
      limpiarFormularioNotas();
      if (typeof obtenerNotas === "function") obtenerNotas();
      accionNota = "nuevo";
    }
    return ok;
  }

  const res = validarYNormalizarNota();
  if (!res.ok){
    if (typeof alertify !== "undefined") alertify.error(res.msg);
    return false;
  }

  const v = res.values;
  const payload = {
    accion: accionLocal,   // "nuevo" | "modificar"
    idNota,
    idAlumno: v.idAlumno,
    idMateria: v.idMateria,
    nota: v.nota,
    aprobado: v.aprobado
  };

  const ok = await postNota(payload);
  if (ok){
    limpiarFormularioNotas();
    if (typeof obtenerNotas === "function") obtenerNotas();
    accionNota = "nuevo";
  }
  return ok;
}

async function postNota(data){
  try{
    const response = await fetch("/notas", {
      method: "POST",
      body: JSON.stringify(data),
    });
    const r = await response.json();
    if (r.msg !== "ok"){
      if (typeof alertify !== "undefined") alertify.error(`Error al procesar nota: ${JSON.stringify(r)}`);
      return false;
    }
    if (typeof alertify !== "undefined"){
      const accionTxt = data.accion === "eliminar" ? "Eliminada" : (data.accion === "modificar" ? "Actualizada" : "Guardada");
      alertify.success(`Nota ${accionTxt} correctamente`);
    }
    return true;
  }catch(err){
    console.error(err);
    if (typeof alertify !== "undefined") alertify.error("Error de comunicación con el servidor.");
    return false;
  }
}

// Validación / Normalización
function validarYNormalizarNota(){
  const idAlumnoSel = (typeof cmbAlumno !== "undefined" ? (cmbAlumno.value || "").trim() : "");
  const idMateriaSel = (typeof cmbMateria !== "undefined" ? (cmbMateria.value || "").trim() : "");
  const notaStr = (typeof txtNota !== "undefined" ? (txtNota.value || "").trim() : "");
  const aprobadoSel = (typeof cmbAprobado !== "undefined" ? (cmbAprobado.value || "").trim() : "");

  if (!idAlumnoSel) return { ok:false, msg: "Debe seleccionar un ALUMNO." };
  if (!idMateriaSel) return { ok:false, msg: "Debe seleccionar una MATERIA." };
  if (!notaStr) return { ok:false, msg: "La NOTA es requerida." };

  const nota = Number(notaStr);
  if (!isFinite(nota)) return { ok:false, msg: "La NOTA debe ser numérica." };
  if (nota < 0 || nota > 100) return { ok:false, msg: "La NOTA debe estar entre 0 y 100." };

  if (typeof cmbAlumno !== "undefined") cmbAlumno.value = idAlumnoSel;
  if (typeof cmbMateria !== "undefined") cmbMateria.value = idMateriaSel;
  if (typeof txtNota !== "undefined") txtNota.value = String(nota);
  if (typeof cmbAprobado !== "undefined") cmbAprobado.value = aprobadoSel;

  return {
    ok:true,
    values:{
      idAlumno: Number(idAlumnoSel),
      idMateria: Number(idMateriaSel),
      nota,
      aprobado: (aprobadoSel || null)
    }
  };
}

// Cargar datos en el form desde la tabla de búsqueda
function mostrarNota(nota){
  accionNota = "modificar";
  idNota = nota.idNota ?? nota.id ?? 0;

  const idAlu = nota.idAlumno ?? "";
  const idMat = nota.idMateria ?? "";
  const valor = nota.nota ?? 0;
  const aprobado = nota.aprobado ?? "";

  if (typeof cmbAlumno !== "undefined"){
    if (!cmbAlumno.options.length){
      cargarAlumnosCombo().then(()=>{ cmbAlumno.value = String(idAlu); });
    }else{
      cmbAlumno.value = String(idAlu);
    }
  }

  if (typeof cmbMateria !== "undefined"){
    if (!cmbMateria.options.length){
      cargarMateriasCombo().then(()=>{ cmbMateria.value = String(idMat); });
    }else{
      cmbMateria.value = String(idMat);
    }
  }

  if (typeof txtNota !== "undefined") txtNota.value = valor;
  if (typeof cmbAprobado !== "undefined") cmbAprobado.value = aprobado;

  if (typeof alertify !== "undefined"){
    const nomA = nota.nombre_alumno ?? "";
    const nomM = nota.nombre_materia ?? "";
    alertify.success(`Nota de "${nomA}" en "${nomM}" cargada para editar`);
  }
}

// Eliminar desde tabla (uso externo si se desea)
function eliminarNota(nota, event){
  if (event){
    event.preventDefault();
    if (event.stopPropagation) event.stopPropagation();
  }
  const alumno = nota.nombre_alumno ?? "el alumno";
  const materia = nota.nombre_materia ?? "la materia";
  if (!confirm(`¿Eliminar la nota de "${alumno}" en "${materia}"?`)) return;

  idNota = nota.idNota ?? nota.id ?? 0;
  accionNota = "eliminar";
  guardarNotas();
}
