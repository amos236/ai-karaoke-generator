// ===========================================
// AI Karaoke Generator
// Upload Script
// ===========================================

const convertBtn = document.getElementById("convertBtn");
const songFile = document.getElementById("songFile");
const status = document.getElementById("status");
const downloadSection = document.getElementById("downloadSection");
const downloadLink = document.getElementById("downloadLink");

const API_URL = window.location.origin;

const userId = localStorage.getItem("user_id");

if (!userId) {

    alert("Please login first.");

    location.href = "/login";

}

convertBtn.addEventListener("click", async () => {

    if (songFile.files.length === 0) {

        alert("Please select MP3 file.");

        return;

    }

    convertBtn.disabled = true;

    status.innerHTML = "Uploading...";

    downloadSection.style.display = "none";

    const formData = new FormData();

    formData.append("user_id", userId);

    formData.append("file", songFile.files[0]);

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        console.log("SERVER RESPONSE");

        console.log(data);

        if (!response.ok) {

            alert(JSON.stringify(data, null, 2));

            throw new Error(
                JSON.stringify(data)
            );

        }

        status.innerHTML = "Processing...";

        checkStatus(data.job_id);

    }

    catch (e) {

        console.error(e);

        status.innerHTML = e.message;

        convertBtn.disabled = false;

    }

});

async function checkStatus(jobId){

    const timer = setInterval(async()=>{

        const response = await fetch(`/status/${jobId}`);

        const data = await response.json();

        if(data.status==="completed"){

            clearInterval(timer);

            status.innerHTML="Completed";

            downloadSection.style.display="block";

            downloadLink.href=`/download/${jobId}`;

            convertBtn.disabled=false;

        }

        if(data.status==="failed"){

            clearInterval(timer);

            status.innerHTML=data.error;

            convertBtn.disabled=false;

        }

    },3000);

}