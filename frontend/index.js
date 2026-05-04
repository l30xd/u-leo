const API_URL = "/students";
const AUTH_TOKEN_KEY = "crud_auth_token";

function getAuthToken() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
        window.location.href = "/login.html";
    }
    return token;
}

function getAuthHeaders() {
    return {
        "content-type": "application/json",
        "Authorization": `Bearer ${getAuthToken()}`,
    };
}

function handleResponse(response) {
    if (response.status === 401) {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        window.location.href = "/login.html";
        return Promise.reject(new Error("No autorizado."));
    }
    return response.text().then(text => {
        if (!response.ok) {
            throw new Error(text || "Error en la operación");
        }
        return text ? JSON.parse(text) : null;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    getAuthToken();
    setupForm();
    loadStudents();
    setupLogout();
})

function setupLogout() {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem(AUTH_TOKEN_KEY);
            window.location.href = "/login.html";
        });
    }
}

const setupForm = () => {
    const form = document.getElementById("student-form");
    const cancelBtn = document.getElementById("cancel-btn");

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        saveStudent();
    })

    cancelBtn.addEventListener("click", () => {
        document.getElementById("student-form").reset();
        document.getElementById("student-id").value = "";
    })
}

function saveStudent() {
    const id = document.getElementById("student-id").value;
    const name = document.getElementById("name").value;
    const age = Number(document.getElementById("age").value);
    const grade = Number(document.getElementById("grade").value);

    const studentData = { name, age, grade }

    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/${id}` : `${API_URL}/`;

    fetch(url, {
        method: method,
        headers: getAuthHeaders(),
        body: JSON.stringify(studentData)
    })
    .then(handleResponse)
    .then(() => {
        alert("Estudiante guardado correctamente");
        loadStudents();
        document.getElementById("student-form").reset();
        document.getElementById("student-id").value = "";
    })
    .catch(error => {
        alert("Error: " + (error.message || error));
    })
}

function loadStudents() {
    fetch(`${API_URL}/`, {
        headers: getAuthHeaders(),
    })
    .then(handleResponse)
    .then(data => {
        const tableBody = document.getElementById("student-list");
        tableBody.innerHTML = "";
        if (!data || data.length === 0) {
            const emptyRow = document.createElement("tr");
            emptyRow.innerHTML = `
                <td colspan="4" style="text-align:center; color:#ddd; padding: 24px; background:#2a2a2a;">No hay estudiantes registrados aún.</td>
            `;
            tableBody.appendChild(emptyRow);
            return;
        }
        data.forEach(student => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${student.id}</td>
                <td>${student.name}</td>
                <td>${student.grade}</td>
                <td>
                    <button onclick="editStudent(${student.id})">Editar</button>
                    <button onclick="deleteStudent(${student.id})">Eliminar</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    })
    .catch(error => console.error("Error cargando estudiantes:", error));
}

function editStudent(id) {
    fetch(`${API_URL}/${id}`, {
        headers: getAuthHeaders(),
    })
    .then(handleResponse)
    .then(student => {
        document.getElementById("student-id").value = student.id;
        document.getElementById("name").value = student.name;
        document.getElementById("age").value = student.age;
        document.getElementById("grade").value = student.grade;
    })
    .catch(error => console.error("Error cargando estudiante:", error));
}

function deleteStudent(id) {
    if (confirm("¿Estás seguro de eliminar este estudiante?")) {
        fetch(`${API_URL}/${id}`, {
            method: "DELETE",
            headers: getAuthHeaders(),
        })
        .then(async response => {
            if (response.status === 401) {
                localStorage.removeItem(AUTH_TOKEN_KEY);
                window.location.href = "/login.html";
                return;
            }
            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || "Error eliminando estudiante");
            }
            alert("Estudiante eliminado");
            loadStudents();
        })
        .catch(error => {
            console.error("Error eliminando:", error);
            alert("Error eliminando estudiante: " + (error.message || error));
        });
    }
}