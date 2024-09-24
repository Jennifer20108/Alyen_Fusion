// Manejo de la visibilidad de las contraseñas
var eye = document.getElementById('Eye');
var input = document.getElementById('id_contrasena');
eye.addEventListener("click", function() {
    if (input.type == "password") {
        input.type = "text";
        eye.style.opacity = 0.8;
    } else {
        input.type = "password";
        eye.style.opacity = 0.2;
    }
});

var eye2 = document.getElementById('Eye2');
var input2 = document.getElementById('id_contrasena2');
eye2.addEventListener("click", function() {
    if (input2.type == "password") {
        input2.type = "text";
        eye2.style.opacity = 0.8;
    } else {
        input2.type = "password";
        eye2.style.opacity = 0.2;
    }
});

// Mostrar mensajes usando SweetAlert2
window.onload = function() {
    console.log("passwordError:", passwordError);
    console.log("error:", error);
    console.log("success:", success);

    if (passwordError) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: passwordError // Mostrar mensaje de contraseña incorrecta
        });
    } else if (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error
        });
    } 

    if (success) {
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            text: success
        });
    }
};
