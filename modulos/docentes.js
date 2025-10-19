var accionDocente = "nuevo",
    idDocente = 0;

document.addEventListener("DOMContentLoaded", event => { 
    frmDocentes.addEventListener("submit", e => {
        e.preventDefault();
        guardarDocentes();
    });
    obtenerDocentes();
});

async function guardarDocentes(){
    let datos = {
        tabla : "docentes",
        accion: accionDocente,
        idDocente,
        codigo: txtCodigoDocente.value,
        nombre: txtNombreDocente.value,
        direccion: txtDireccionDocente.value,
        telefono: txtTelefonoDocente.value,
        email: txtEmailDocente.value,
        dui: txtDuiDocente.value,
        escalafon: txtEscalafonDocente.value
    };
    let response = await fetch("/docentes",{
        method: "POST",
        body: JSON.stringify(datos),
    });
    const respuesta = await response.json();

    if(respuesta.msg!="ok"){
        alertify.error(`Error al procesar docente: ${respuesta}`);
        return;
    }
    limpiarFormularioDocentes();
    obtenerDocentes();
}

function limpiarFormularioDocentes(){
    accionDocente = "nuevo";
    idDocente = 0;
    txtCodigoDocente.value = "";
    txtNombreDocente.value = "";
    txtDireccionDocente.value = "";
    txtTelefonoDocente.value = "";
    txtEmailDocente.value = "";
    txtDuiDocente.value = "";
    txtEscalafonDocente.value = "";
}

async function obtenerDocentes(){
    let response = await fetch("/docentes"),
        respuesta = await response.json();
    mostrarDatosDocentes(respuesta);
}

function mostrarDatosDocentes(docentes){
    let filas = "";
    docentes.forEach(docente=>{
        filas += `
            <tr onClick='mostrarDocente(${ JSON.stringify(docente) })'>
                <td>${docente.codigo}</td>
                <td>${docente.nombre}</td>
                <td>${docente.direccion ?? ""}</td>
                <td>${docente.telefono ?? ""}</td>
                <td>${docente.email ?? ""}</td>
                <td>${docente.dui ?? ""}</td>
                <td>${docente.escalafon ?? ""}</td>
                <td><button onClick='eliminarDocente(${ JSON.stringify(docente) }, event)' class="btn btn-danger btn-sm">ELIMINAR</button></td>
            </tr>
        `;
    });
    tblDocentes.innerHTML = filas;
}

function mostrarDocente(docente){
    accionDocente = "modificar";
    idDocente = docente.idDocente;
    txtCodigoDocente.value = docente.codigo ?? "";
    txtNombreDocente.value = docente.nombre ?? "";
    txtDireccionDocente.value = docente.direccion ?? "";
    txtTelefonoDocente.value = docente.telefono ?? "";
    txtEmailDocente.value = docente.email ?? "";
    txtDuiDocente.value = docente.dui ?? "";
    txtEscalafonDocente.value = docente.escalafon ?? "";
}

function eliminarDocente(docente, event){
    event.preventDefault();
    if(confirm(`Esta seguro de eliminar a ${docente.nombre}`)){
        idDocente = docente.idDocente;
        accionDocente = "eliminar";
        guardarDocentes();
    }
}
