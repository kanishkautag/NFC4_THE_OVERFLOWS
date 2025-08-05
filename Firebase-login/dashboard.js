// Import Firebase core and auth modules from CDN
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

// Your Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyDyt3r9AGcHkuvL37frfaKFzr9er18OGMI",
  authDomain: "clause-9d753.firebaseapp.com",
  projectId: "clause-9d753",
  storageBucket: "clause-9d753.firebasestorage.app",
  messagingSenderId: "490035572199",
  appId: "1:490035572199:web:531332d89e2a2e690ba142",
  measurementId: "G-DMWH6P65EW"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// UI Elements
const userNameEl = document.getElementById('user-name');
const userEmailEl = document.getElementById('user-email');
const logoutButton = document.getElementById("logout");

const evaluateButton = document.getElementById("evaluate");
const regenerateButton = document.getElementById("regenerate");
const promptInput = document.getElementById("prompt");
const resultsDiv = document.getElementById("results");
const promptList = document.getElementById('promptList');

let lastPrompt = '';

// --- Authentication Logic ---

// Handle logout
logoutButton.addEventListener("click", async () => {
    try {
        await signOut(auth);
        // Redirect to login page after logout
        window.location.href = "index.html";
    } catch (error) {
        console.error("Logout error:", error.message);
        alert("Logout failed: " + error.message);
    }
});

// Authentication state observer
onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in
        const email = user.email;
        const displayName = user.displayName || email.split('@')[0];

        userNameEl.textContent = displayName;
        userEmailEl.textContent = email;
    } else {
        // Not logged in -> redirect to login page
        window.location.href = 'index.html';
    }
});

// --- RAG Pipeline Logic ---

async function getEvaluation(prompt) {
    resultsDiv.innerHTML = "<p>Generating and assessing...</p>";
    regenerateButton.style.display = "none"; // Hide regenerate during new evaluation

    try {
        const user = auth.currentUser;
        if (!user) {
            resultsDiv.innerHTML = "<p style='color: red;'>Please log in to use this feature.</p>";
            return;
        }
        const idToken = await user.getIdToken();

        const response = await fetch("http://127.0.0.1:8000/evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${idToken}` // Include ID token
            },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "An unknown error occurred.");
        }

        const data = await response.json();
        resultsDiv.innerHTML = `
            <h4>Generated Clause</h4>
            <p>${data.clause}</p>
            <p><strong>Risk:</strong> ${data.risk}</p>
            <p><strong>Classification:</strong> ${data.classification}</p>
            <p><strong>Source:</strong> ${data.source}</p>
            <div>
                <strong>Feedback:</strong>
                ${data.feedback_options.map(option => `<button class="btn btn-outline-secondary btn-sm me-2">${option}</button>`).join('')}
            </div>
        `;
        regenerateButton.style.display = "inline-block"; // Show regenerate after results

        // Add prompt to sidebar
        const li = document.createElement('li');
        li.className = 'bg-gray-100 p-2 rounded';
        li.innerText = prompt;
        promptList.prepend(li);

    } catch (error) {
        console.error("Evaluation error:", error);
        resultsDiv.innerHTML = `<p style='color: red;'>Error: ${error.message}</p>`;
    }
}

evaluateButton.addEventListener("click", async () => {
    const prompt = promptInput.value;
    lastPrompt = prompt; // Store for regeneration
    getEvaluation(prompt);
});

regenerateButton.addEventListener("click", async () => {
    if (lastPrompt) {
        getEvaluation(lastPrompt);
    } else {
        resultsDiv.innerHTML = "<p style='color: orange;'>No previous prompt to regenerate.</p>";
    }
});
