// ==========================================
// Check Admin Login
// ==========================================

if (localStorage.getItem("admin_logged_in") !== "true") {

    window.location.href = "/admin-login";

}

// ==========================================
// API URL
// ==========================================

const API_URL = window.location.origin;

// ==========================================
// Load Dashboard
// ==========================================

window.onload = function () {

    loadDashboard();

};

// ==========================================
// Dashboard
// ==========================================

async function loadDashboard() {

    try {

        // Dashboard Statistics

        const statsResponse = await fetch(
            `${API_URL}/admin/dashboard`
        );

        const stats = await statsResponse.json();

        document.getElementById("totalUsers").innerHTML =
            stats.total_users;

        document.getElementById("activeUsers").innerHTML =
            stats.active_subscribers;

        document.getElementById("pendingPayments").innerHTML =
            stats.pending_payments;

        // Pending Payments

        const response = await fetch(
            `${API_URL}/admin/pending-payments`
        );

        const payments = await response.json();

        const table = document.getElementById("paymentTable");

        table.innerHTML = "";

        payments.forEach(payment => {

            table.innerHTML += `

<tr>

<td>${payment.id}</td>

<td>${payment.user_id}</td>

<td>${payment.transaction_id}</td>

<td>₹${payment.amount}</td>

<td>${payment.payment_status}</td>

<td>

<button
class="approve"
onclick="approvePayment(${payment.id})">

Approve

</button>

<button
class="reject"
onclick="rejectPayment(${payment.id})">

Reject

</button>

</td>

</tr>

`;

        });

    }

    catch (err) {

        console.error(err);

        alert("Unable to load dashboard.");

    }

}

// ==========================================
// Approve Payment
// ==========================================

async function approvePayment(id) {

    if (!confirm("Approve this payment?")) return;

    const response = await fetch(

        `${API_URL}/admin/approve/${id}`,

        {
            method: "POST"
        }

    );

    const data = await response.json();

    alert(data.message);

    loadDashboard();

}

// ==========================================
// Reject Payment
// ==========================================

async function rejectPayment(id) {

    if (!confirm("Reject this payment?")) return;

    const response = await fetch(

        `${API_URL}/admin/reject/${id}`,

        {
            method: "POST"
        }

    );

    const data = await response.json();

    alert(data.message);

    loadDashboard();

}

// ==========================================
// Logout
// ==========================================

document.getElementById("logoutBtn").addEventListener("click", () => {

    localStorage.removeItem("admin_logged_in");
    localStorage.removeItem("admin_id");
    localStorage.removeItem("admin_username");
    localStorage.removeItem("admin_role");

    window.location.href = "/admin-login";

});