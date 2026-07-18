// ===========================================
// AI Karaoke Generator Dashboard
// ===========================================

// ===========================================
// Elements
// ===========================================

const welcome = document.getElementById("welcome");
const subStatus = document.getElementById("subStatus");
const expiryDate = document.getElementById("expiryDate");

const subscribeBtn = document.getElementById("subscribeBtn");
const uploadBtn = document.getElementById("uploadBtn");
const logoutBtn = document.getElementById("logoutBtn");

// ===========================================
// API
// ===========================================

const API_URL = window.location.origin;

// ===========================================
// Logged User
// ===========================================

const userId = localStorage.getItem("user_id");
const username = localStorage.getItem("username");
const role = localStorage.getItem("role");

// ===========================================
// Login Check
// ===========================================

if (!userId) {

    alert("Please login first.");

    window.location.href = "/login";

}

// ===========================================
// Welcome
// ===========================================

welcome.innerHTML = `Welcome, ${username}`;

// ===========================================
// Load Profile
// ===========================================

async function loadProfile() {

    try {

        const response = await fetch(
            `${API_URL}/profile/${userId}`
        );

        const data = await response.json();

        console.log(data);

        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to load profile."
            );

        }

        // Subscription Status

        subStatus.innerHTML = data.subscription_status;

        // Expiry

        if (data.expiry_date) {

            expiryDate.innerHTML =
                new Date(data.expiry_date).toLocaleDateString();

        }

        else {

            expiryDate.innerHTML = "Not Active";

        }

        // ===================================
        // Admin
        // ===================================

        if (role === "admin") {

            subStatus.innerHTML = "Unlimited (Admin)";

            expiryDate.innerHTML = "Never";

            uploadBtn.disabled = false;

            uploadBtn.innerHTML = "🎵 Convert to Karaoke";

            subscribeBtn.style.display = "none";

            return;

        }

        // ===================================
        // Active Subscription
        // ===================================

        if (data.subscription_status.toLowerCase() === "active") {

            uploadBtn.disabled = false;

            uploadBtn.innerHTML = "🎵 Convert to Karaoke";

            subscribeBtn.style.display = "none";

        }

        // ===================================
        // Inactive
        // ===================================

        else {

            uploadBtn.disabled = true;

            uploadBtn.innerHTML = "Subscription Required";

            subscribeBtn.style.display = "inline-block";

        }

    }

    catch (err) {

        console.error(err);

        alert(err.message);

    }

}

loadProfile();

// ===========================================
// Subscribe
// ===========================================

subscribeBtn.onclick = function () {

    window.location.href = "/subscribe";

};

// ===========================================
// Convert to Karaoke
// ===========================================

uploadBtn.onclick = function () {

    if (uploadBtn.disabled) {

        alert("Please activate your subscription first.");

        return;

    }

    window.location.href = "/upload-page";

};

// ===========================================
// Logout
// ===========================================

logoutBtn.onclick = function () {

    localStorage.clear();

    window.location.href = "/login";

};