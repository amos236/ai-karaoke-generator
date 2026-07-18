// ======================================
// Elements
// ======================================

const username = document.getElementById("username");
const password = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");
const status = document.getElementById("status");

const API_URL = window.location.origin;

// ======================================
// Admin Login
// ======================================

loginBtn.addEventListener("click", adminLogin);

password.addEventListener("keypress", function (e) {

    if (e.key === "Enter") {

        adminLogin();

    }

});

async function adminLogin() {

    const user = username.value.trim();
    const pass = password.value.trim();

    if (user === "" || pass === "") {

        status.innerHTML = "❌ Enter username and password.";
        return;

    }

    loginBtn.disabled = true;
    loginBtn.innerHTML = "Checking...";
    status.innerHTML = "Verifying admin...";

    try {

        const response = await fetch(

            `${API_URL}/admin/login?username=${encodeURIComponent(user)}&password=${encodeURIComponent(pass)}`,

            {
                method: "POST"
            }

        );

        const data = await response.json();

        console.log(data);

        if (!response.ok) {

            throw new Error(data.detail || "Login failed.");

        }

        if (!data.success) {

            throw new Error(data.message || "Invalid credentials.");

        }

        // Save Admin Session

        localStorage.setItem("admin_logged_in", "true");
        localStorage.setItem("admin_id", data.user_id);
        localStorage.setItem("admin_username", data.username);
        localStorage.setItem("admin_role", "admin");

        status.innerHTML = "✅ Login Successful";

        setTimeout(() => {

            window.location.href = "/admin";

        }, 800);

    }

    catch (err) {

        console.error(err);

        status.innerHTML = "❌ " + err.message;

        loginBtn.disabled = false;
        loginBtn.innerHTML = "Login";

    }

}