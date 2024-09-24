let users = [
    {nombre: 'Juan', apellido: 'Pérez', correo: 'juan@example.com', celular: '123456789'},
    {nombre: 'Ana', apellido: 'García', correo: 'ana@example.com', celular: '987654321'}
];

document.addEventListener('DOMContentLoaded', () => {
    loadUsers();

    document.getElementById('addUserBtn').addEventListener('click', () => {
        // Aquí puedes implementar la lógica para agregar un nuevo usuario
        alert("Función para agregar un nuevo usuario.");
    });
});

function loadUsers() {
    const tbody = document.getElementById('userTable').getElementsByTagName('tbody')[0];
    tbody.innerHTML = "";
    users.forEach((user, index) => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${user.nombre}</td>
            <td>${user.apellido}</td>
            <td>${user.correo}</td>
            <td>${user.celular}</td>
            <td>
                <button onclick="editUser(${index})">✏️ Editar</button>
                <button onclick="deleteUser(${index})">❌ Eliminar</button>
            </td>
        `;
    });
}

function filterUsers() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const tbody = document.getElementById('userTable').getElementsByTagName('tbody')[0];
    const rows = tbody.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const tdNombre = rows[i].getElementsByTagName('td')[0];
        const tdApellido = rows[i].getElementsByTagName('td')[1];
        if (tdNombre || tdApellido) {
            const txtValueNombre = tdNombre.textContent || tdNombre.innerText;
            const txtValueApellido = tdApellido.textContent || tdApellido.innerText;
            if (txtValueNombre.toLowerCase().indexOf(filter) > -1 || txtValueApellido.toLowerCase().indexOf(filter) > -1) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }
    }
}

function editUser(index) {
    const user = users[index];
    alert(`Editando: ${user.nombre} ${user.apellido}`);
}

function deleteUser(index) {
    users.splice(index, 1);
    loadUsers();
}
