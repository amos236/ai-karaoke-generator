// =====================================
// Elements
// =====================================

const loginBtn = document.getElementById("loginBtn");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const status = document.getElementById("status");
const loginTitle = document.getElementById("loginTitle");

// =====================================
// API URL
// =====================================

const API_URL = window.location.origin;

// =====================================
// Hidden Admin Login (10 Clicks)
// =====================================

let clickCount = 0;

if (loginTitle) {

    loginTitle.addEventListener("click", () => {

        clickCount++;

        console.log("Login Title Click:", clickCount);

        if (clickCount >= 10) {

            clickCount = 0;

            alert("Opening Admin Login...");

            window.location.href = "/admin-login";

        }

    });

} else {

    console.error("loginTitle element not found.");

}

// =====================================
// User Login
// =====================================

loginBtn.addEventListener("click", async () => {

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (username === "" || password === "") {

        status.innerHTML = "❌ Please enter username and password.";
        return;

    }

    loginBtn.disabled = true;
    loginBtn.innerHTML = "Logging in...";
    status.innerHTML = "Checking account...";

    try {

        const response = await fetch(

            `${API_URL}/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
            {
                method: "POST"
            }

        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.detail || "Login failed.");

        }

        if (!data.success) {

            throw new Error(data.message || "Login failed.");

        }

        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("username", data.username);
        localStorage.setItem("role", data.role);
        localStorage.setItem(
            "subscription_status",
            data.subscription_status
        );

        status.innerHTML = "✅ Login Successful";

        setTimeout(() => {

            window.location.href = "/dashboard";

        }, 1000);

    }

    catch (err) {

        status.innerHTML = "❌ " + err.message;

    }

    finally {

        loginBtn.disabled = false;
        loginBtn.innerHTML = "Login";

    }

});