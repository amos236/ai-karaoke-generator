// ===========================================
// AI Karaoke Generator
// index.js
// ===========================================

// ===========================================
// Counter Animation
// ===========================================

const counters = document.querySelectorAll(".counter");

function startCounter() {

    counters.forEach(counter => {

        const target = Number(counter.dataset.target);

        let current = 0;

        const increment = Math.max(1, target / 120);

        function updateCounter() {

            current += increment;

            if (current < target) {

                counter.innerHTML = Math.floor(current);

                requestAnimationFrame(updateCounter);

            } else {

                counter.innerHTML = target.toLocaleString() + "+";

            }

        }

        updateCounter();

    });

}

let counterStarted = false;

window.addEventListener("scroll", () => {

    const section = document.querySelector(".counter-section");

    if (!section) return;

    const top = section.getBoundingClientRect().top;

    if (top < window.innerHeight - 100 && !counterStarted) {

        counterStarted = true;

        startCounter();

    }

});

// ===========================================
// Navbar Scroll
// ===========================================

const header = document.querySelector("header");

window.addEventListener("scroll", () => {

    if (!header) return;

    if (window.scrollY > 80) {

        header.style.background = "rgba(5,10,25,.95)";
        header.style.boxShadow = "0 10px 25px rgba(0,0,0,.35)";

    } else {

        header.style.background = "rgba(10,15,30,.75)";
        header.style.boxShadow = "none";

    }

});

// ===========================================
// Scroll Reveal
// ===========================================

const revealItems = document.querySelectorAll(
".feature-card,.counter-card,.review-card,.faq-item,.price-card,.about-grid div,.step"
);

revealItems.forEach(item => {

    item.style.opacity = "0";
    item.style.transform = "translateY(40px)";
    item.style.transition = ".8s";

});

function reveal() {

    revealItems.forEach(item => {

        const top = item.getBoundingClientRect().top;

        if (top < window.innerHeight - 80) {

            item.style.opacity = "1";
            item.style.transform = "translateY(0px)";

        }

    });

}

window.addEventListener("scroll", reveal);

reveal();

// ===========================================
// Hero Image Animation
// ===========================================

const heroImage = document.querySelector(".hero-right img");

if (heroImage) {

    document.addEventListener("mousemove", (e) => {

        const x = (e.clientX - window.innerWidth / 2) / 60;
        const y = (e.clientY - window.innerHeight / 2) / 60;

        heroImage.style.transform =
            `translate(${x}px, ${y}px)`;

    });

}

// ===========================================
// Button Hover
// ===========================================

document.querySelectorAll("button").forEach(btn => {

    btn.addEventListener("mouseenter", () => {

        btn.style.transform = "translateY(-3px)";
        btn.style.transition = ".3s";

    });

    btn.addEventListener("mouseleave", () => {

        btn.style.transform = "translateY(0px)";

    });

});

// ===========================================
// Smooth Scroll
// ===========================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        const href = this.getAttribute("href");

        if (href === "#") return;

        const target = document.querySelector(href);

        if (target) {

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});

// ===========================================
// Active Navigation
// ===========================================

const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll(".navbar a");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {

        if (window.scrollY >= section.offsetTop - 120) {

            current = section.id;

        }

    });

    navLinks.forEach(link => {

        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + current) {

            link.classList.add("active");

        }

    });

});

// ===========================================
// Floating Music Notes
// ===========================================

function createMusicNote() {

    const note = document.createElement("div");

    const icons = ["🎵", "🎶", "🎼"];

    note.innerHTML = icons[Math.floor(Math.random() * icons.length)];

    note.style.position = "fixed";
    note.style.left = Math.random() * 100 + "vw";
    note.style.bottom = "-40px";
    note.style.fontSize = (20 + Math.random() * 20) + "px";
    note.style.opacity = ".2";
    note.style.pointerEvents = "none";
    note.style.zIndex = "-1";
    note.style.transition = "transform 12s linear, opacity 12s linear";

    document.body.appendChild(note);

    setTimeout(() => {

        note.style.transform =
            "translateY(-120vh) rotate(360deg)";

        note.style.opacity = "0";

    }, 100);

    setTimeout(() => {

        note.remove();

    }, 12000);

}

setInterval(createMusicNote, 2500);

// ===========================================
// Footer Year
// ===========================================

const year = document.getElementById("year");

if (year) {

    year.innerHTML = new Date().getFullYear();

}

// ===========================================
// Login / Register Buttons
// ===========================================

const loginBtn = document.getElementById("loginBtn");

if (loginBtn) {

    loginBtn.addEventListener("click", () => {

        window.location.href = "/login";

    });

}

const registerBtn = document.getElementById("registerBtn");

if (registerBtn) {

    registerBtn.addEventListener("click", () => {

        window.location.href = "/register";

    });

}

// ===========================================
// Console
// ===========================================

console.clear();

console.log("==================================");
console.log("🎵 AI Karaoke Generator");
console.log("Frontend Loaded Successfully");
console.log("==================================");