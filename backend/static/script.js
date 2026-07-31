// =========================================
// JoshAI Karaoke Generator
// =========================================

const convertBtn = document.getElementById("convertBtn");
const songFile = document.getElementById("songFile");

const statusBox = document.getElementById("status");
const progressBar = document.querySelector(".bar");
const percent = document.querySelector(".percent");

const downloadSection = document.getElementById("downloadSection");
const downloadLink = document.getElementById("downloadLink");

let timer = null;

// =========================================
// Convert Button
// =========================================

convertBtn.addEventListener("click", async () => {

    const file = songFile.files[0];

    if (!file) {

        alert("Please choose an MP3 file.");

        return;

    }

    const userId = localStorage.getItem("user_id");

    if (!userId) {

        alert("Please login first.");

        window.location = "/login";

        return;

    }

    convertBtn.disabled = true;

    downloadSection.style.display = "none";

    progressBar.style.width = "5%";

    statusBox.innerHTML = "Uploading...";

    percent.innerHTML = "Uploading MP3...";

    const formData = new FormData();

    formData.append("user_id", userId);

    formData.append("file", file);

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.detail);

        }

        statusBox.innerHTML = "Upload Successful";

        progressBar.style.width = "15%";

        percent.innerHTML = "Waiting for AI...";

        checkStatus(data.job_id);

    }

    catch (err) {

        alert(err.message);

        convertBtn.disabled = false;

    }

});


// =========================================
// Status Polling
// =========================================

function checkStatus(jobId) {

    if (timer) {

        clearInterval(timer);

    }

    timer = setInterval(async () => {

        try {

            const response = await fetch(`/status/${jobId}`);

            if (response.status === 404) {

                clearInterval(timer);

                statusBox.innerHTML = "Job Not Found";

                percent.innerHTML = "Server lost the job.";

                convertBtn.disabled = false;

                return;

            }

            const data = await response.json();

            console.log(data);

            if (data.status === "queued") {

                progressBar.style.width = "20%";

                statusBox.innerHTML = "Queued";

                percent.innerHTML = "Waiting in queue...";

            }

            else if (data.status === "processing") {

                progressBar.style.width = "70%";

                statusBox.innerHTML = "Processing";

                percent.innerHTML = "Removing vocals...";

            }

            else if (data.status === "completed") {

                clearInterval(timer);

                progressBar.style.width = "100%";

                statusBox.innerHTML = "Completed";

                percent.innerHTML = "Download Ready";

                downloadLink.href = `/download/${jobId}`;

                downloadSection.style.display = "block";

                convertBtn.disabled = false;

            }

            else if (data.status === "failed") {

                clearInterval(timer);

                progressBar.style.width = "100%";

                statusBox.innerHTML = "Failed";

                percent.innerHTML = data.error;

                alert(data.error);

                convertBtn.disabled = false;

            }

        }

        catch (err) {

            clearInterval(timer);

            console.log(err);

            convertBtn.disabled = false;

        }

    }, 3000);

}