// ===============================
// Elements
// ===============================

const registerBtn = document.getElementById("registerBtn");

const usernameInput = document.getElementById("username");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirmPassword");

const status = document.getElementById("status");

// ===============================
// API URL
// ===============================

const API_URL = window.location.origin;

// ===============================
// Register
// ===============================

registerBtn.addEventListener("click", async () => {

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    // Validation

    if (
        username === "" ||
        email === "" ||
        password === "" ||
        confirmPassword === ""
    ) {

        status.innerHTML = "❌ Please fill all fields.";

        return;

    }

    if (password !== confirmPassword) {

        status.innerHTML = "❌ Passwords do not match.";

        return;

    }

    registerBtn.disabled = true;
    registerBtn.innerHTML = "Creating Account...";

    status.innerHTML = "Creating your account...";

    try {

        const response = await fetch(

            `${API_URL}/register?username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,

            {
                method: "POST"
            }

        );

        const data = await response.json();

        console.log("Register Response:", data);

        if (!response.ok || data.success !== true) {

            throw new Error(
                data.detail ||
                data.message ||
                "Registration failed."
            );

        }

        status.innerHTML =
            "✅ Registration Successful! Redirecting to Login...";

        setTimeout(() => {

            window.location.href = "/login";

        }, 1500);

    }

    catch (err) {

        console.error(err);

        status.innerHTML = "❌ " + err.message;

    }

    finally {

        registerBtn.disabled = false;

        registerBtn.innerHTML = "Register";

    }

});