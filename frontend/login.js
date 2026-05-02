const AUTH_TOKEN_KEY = "crud_auth_token";
const API_AUTH_URL = "/auth";

function showMessage(message, isError = false) {
    const messageBox = document.getElementById("message");
    messageBox.textContent = message;
    messageBox.style.color = isError ? "#ff9999" : "#b3ffb3";
}

function clearMessage() {
    showMessage("");
}

document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem(AUTH_TOKEN_KEY)) {
        window.location.href = "/index.html";
        return;
    }

    const loginForm = document.getElementById("login-form");
    const otpForm = document.getElementById("otp-form");

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage();
        const email = document.getElementById("email").value.trim();
        if (!email) {
            showMessage("Ingresa un correo válido.", true);
            return;
        }

        try {
            const response = await fetch(`${API_AUTH_URL}/request-otp`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            showMessage("Código OTP enviado. Revisa tu correo.");
            otpForm.style.display = "block";
        } catch (error) {
            showMessage(error.message || "No se pudo enviar el OTP.", true);
        }
    });

    otpForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage();
        const email = document.getElementById("email").value.trim();
        const code = document.getElementById("otp").value.trim();

        if (!code || code.length !== 6) {
            showMessage("Ingresa un código OTP de 6 dígitos.", true);
            return;
        }

        try {
            const response = await fetch(`${API_AUTH_URL}/verify-otp`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, code }),
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const data = await response.json();
            localStorage.setItem(AUTH_TOKEN_KEY, data.token);
            window.location.href = "/index.html";
        } catch (error) {
            showMessage(error.message || "Código OTP incorrecto.", true);
        }
    });
});
