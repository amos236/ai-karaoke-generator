// ==========================================
// AI Karaoke Generator
// subscribe.js
// ==========================================

// ----------------------------
// Elements
// ----------------------------

const upiId = document.getElementById("upiId");
const copyBtn = document.getElementById("copyBtn");

const transactionId = document.getElementById("transactionId");

const payBtn = document.getElementById("payBtn");

const dashboardBtn = document.getElementById("dashboardBtn");

const status = document.getElementById("status");

// ----------------------------
// API
// ----------------------------

const API_URL = window.location.origin;

// ----------------------------
// Logged User
// ----------------------------

const userId = localStorage.getItem("user_id");
const username = localStorage.getItem("username");

if (!userId) {

    alert("Please login first.");

    window.location.href = "/login";

}

// ----------------------------
// Welcome
// ----------------------------

status.innerHTML =
`Welcome <b>${username}</b><br><br>
Please pay <b>₹10</b> and submit your Transaction ID.`;

// ----------------------------
// Copy UPI
// ----------------------------

copyBtn.onclick = function () {

    navigator.clipboard.writeText(upiId.value);

    copyBtn.innerHTML = "Copied ✓";

    setTimeout(() => {

        copyBtn.innerHTML = "Copy";

    }, 2000);

};

// ----------------------------
// Submit Payment
// ----------------------------

payBtn.onclick = async function () {

    const txn = transactionId.value.trim();

    if (txn === "") {

        alert("Please enter Transaction ID.");

        transactionId.focus();

        return;

    }

    payBtn.disabled = true;

    payBtn.innerHTML = "Submitting...";

    status.innerHTML = "Submitting payment...";

    try {

        const response = await fetch(

            `${API_URL}/payment`,

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    user_id: Number(userId),

                    transaction_id: txn,

                    amount: 10

                })

            }

        );

        const data = await response.json();

        console.log("Payment Response");

        console.log(data);

        if (!response.ok) {

            if (typeof data.detail === "string") {

                throw new Error(data.detail);

            }

            throw new Error(JSON.stringify(data.detail));

        }

        status.innerHTML =

        "✅ Payment submitted successfully.<br><br>" +

        "Transaction ID : <b>" + txn + "</b><br><br>" +

        "Payment Status : <b>Pending</b><br><br>" +

        "Please wait until Admin approves your subscription.";

        transactionId.disabled = true;

        payBtn.innerHTML = "Submitted ✓";

    }

    catch (err) {

        console.error(err);

        status.innerHTML =

        "<span style='color:red'>❌ " +

        err.message +

        "</span>";

        payBtn.disabled = false;

        payBtn.innerHTML = "✅ I Have Paid ₹10";

    }

};

// ----------------------------
// Dashboard
// ----------------------------

dashboardBtn.onclick = function () {

    window.location.href = "/dashboard";

};