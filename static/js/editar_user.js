
// Función para abrir el modal y cargar los datos
function abrirModalEditar(usuario) {
    document.getElementById('userId').value = usuario.id;
    document.getElementById('nombre').value = usuario.nombre;
    document.getElementById('apellido').value = usuario.apellido;
    document.getElementById('correo').value = usuario.correo;
    document.getElementById('celular').value = usuario.celular;
    document.getElementById('direccion').value = usuario.direccion;
    document.getElementById('tipo_user').value = usuario.tipo_user;
    document.getElementById('estado_user').value = usuario.estado_user;
    document.getElementById("editUserModal").style.display = "block"; // Muestra el modal
}

const modal = document.getElementById("editUserModal");
const closeButton = document.querySelector(".close");

closeButton.addEventListener("click", function() {
    modal.style.display = "none"; // Cierra el modal
});

window.addEventListener("click", function(event) {
    if (event.target == modal) {
        modal.style.display = "none"; // Cierra el modal si se hace clic fuera de él
    }
});
