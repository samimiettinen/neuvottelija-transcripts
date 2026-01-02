// Import Firebase modules
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import {
    getAuth,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

// ===========================
// Firebase Configuration
// ===========================
let firebaseConfig;

// Load Firebase config from firebase_config.json
async function loadFirebaseConfig() {
    try {
        const response = await fetch('./firebase_config.json');
        if (!response.ok) {
            throw new Error('Firebase config file not found. Please create firebase_config.json from firebase_config.example.json');
        }
        firebaseConfig = await response.json();
        return firebaseConfig;
    } catch (error) {
        console.error('Error loading Firebase config:', error);
        showError('login', 'Virhe: Firebase-konfiguraatiota ei löydy. Luo firebase_config.json tiedosto.');
        return null;
    }
}

// Initialize Firebase
let app;
let auth;

async function initializeFirebase() {
    const config = await loadFirebaseConfig();
    if (!config) return false;

    try {
        app = initializeApp(config);
        auth = getAuth(app);
        console.log('Firebase initialized successfully');
        return true;
    } catch (error) {
        console.error('Error initializing Firebase:', error);
        showError('login', 'Virhe Firebase-alustuksessa: ' + error.message);
        return false;
    }
}

// ===========================
// DOM Elements
// ===========================
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const dashboard = document.getElementById('dashboard');

const showSignupBtn = document.getElementById('showSignup');
const showLoginBtn = document.getElementById('showLogin');

const loginFormElement = document.getElementById('login-form');
const signupFormElement = document.getElementById('signup-form');
const transcriptFormElement = document.getElementById('transcript-form');

const logoutBtn = document.getElementById('logout-btn');
const userEmailDisplay = document.getElementById('user-email');

const toggleLoginPassword = document.getElementById('toggle-login-password');
const toggleSignupPassword = document.getElementById('toggle-signup-password');

// ===========================
// Form Toggle Functions
// ===========================
function showLoginForm() {
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
}

function showSignupForm() {
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
}

function showDashboard(user) {
    loginForm.style.display = 'none';
    signupForm.style.display = 'none';
    dashboard.style.display = 'block';
    userEmailDisplay.textContent = user.email;
}

function hideAll() {
    loginForm.style.display = 'none';
    signupForm.style.display = 'none';
    dashboard.style.display = 'none';
}

function showAuthForms() {
    dashboard.style.display = 'none';
    loginForm.style.display = 'block';
    showLoginForm();
}

// ===========================
// Password Toggle Functions
// ===========================
function togglePasswordVisibility(inputId, toggleBtn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        toggleBtn.setAttribute('aria-label', 'Piilota salasana');
    } else {
        input.type = 'password';
        toggleBtn.setAttribute('aria-label', 'Näytä salasana');
    }
}

// ===========================
// UI Helper Functions
// ===========================
function showError(formType, message) {
    const errorElement = document.getElementById(`${formType}-error`);
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

function showSuccess(elementId, message) {
    const successElement = document.getElementById(elementId);
    successElement.textContent = message;
    successElement.style.display = 'block';
    setTimeout(() => {
        successElement.style.display = 'none';
    }, 5000);
}

function setButtonLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');

    if (isLoading) {
        button.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
    } else {
        button.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

function getFirebaseErrorMessage(errorCode) {
    const errorMessages = {
        'auth/invalid-email': 'Virheellinen sähköpostiosoite',
        'auth/user-disabled': 'Tämä käyttäjätili on poistettu käytöstä',
        'auth/user-not-found': 'Käyttäjää ei löydy',
        'auth/wrong-password': 'Väärä salasana',
        'auth/email-already-in-use': 'Sähköpostiosoite on jo käytössä',
        'auth/weak-password': 'Salasanan tulee olla vähintään 6 merkkiä pitkä',
        'auth/operation-not-allowed': 'Operaatio ei ole sallittu',
        'auth/too-many-requests': 'Liian monta yritystä. Yritä myöhemmin uudelleen',
        'auth/network-request-failed': 'Verkkovirhe. Tarkista internet-yhteys'
    };

    return errorMessages[errorCode] || `Virhe: ${errorCode}`;
}

// ===========================
// Authentication Functions
// ===========================
async function handleLogin(email, password) {
    try {
        setButtonLoading('login-btn', true);
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        console.log('Login successful:', userCredential.user.email);
        // showDashboard is called by onAuthStateChanged
    } catch (error) {
        console.error('Login error:', error);
        showError('login', getFirebaseErrorMessage(error.code));
    } finally {
        setButtonLoading('login-btn', false);
    }
}

async function handleSignup(email, password) {
    try {
        setButtonLoading('signup-btn', true);
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        console.log('Signup successful:', userCredential.user.email);
        // showDashboard is called by onAuthStateChanged
    } catch (error) {
        console.error('Signup error:', error);
        showError('signup', getFirebaseErrorMessage(error.code));
    } finally {
        setButtonLoading('signup-btn', false);
    }
}

async function handleLogout() {
    try {
        await signOut(auth);
        console.log('Logout successful');
        showAuthForms();
    } catch (error) {
        console.error('Logout error:', error);
        showError('transcript', 'Uloskirjautuminen epäonnistui: ' + error.message);
    }
}

// ===========================
// Cloud Function Call
// ===========================
async function callTranscriptFunction(youtubeUrl, idToken) {
    const region = firebaseConfig.cloudFunctionRegion;
    const project = firebaseConfig.cloudFunctionProject;
    const functionUrl = `https://${region}-${project}.cloudfunctions.net/runTranscript`;

    try {
        const response = await fetch(functionUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${idToken}`
            },
            body: JSON.stringify({
                youtube_url: youtubeUrl
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Cloud function error:', error);
        throw error;
    }
}

async function handleTranscriptSubmit(youtubeUrl) {
    try {
        setButtonLoading('transcript-btn', true);

        // Hide previous messages
        document.getElementById('transcript-result').style.display = 'none';
        document.getElementById('transcript-error').style.display = 'none';

        // Get output basename
        const outputBasenameInput = document.getElementById('output-basename');
        const outputBasename = outputBasenameInput ? outputBasenameInput.value.trim() : 'transcript_output';
        const finalFilename = outputBasename || 'transcript_output';

        // Get current user's ID token
        const user = auth.currentUser;
        if (!user) {
            showError('transcript', 'Sinun täytyy olla kirjautunut sisään');
            return;
        }

        const idToken = await user.getIdToken();
        console.log('Got ID token, calling Cloud Function...');

        // Call the Cloud Function
        const result = await callTranscriptFunction(youtubeUrl, idToken);

        console.log('Transcript result received');

        if (result.sbv_content) {
            // Create a Blob from the SBV content
            const blob = new Blob([result.sbv_content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);

            // Create temporary link and click it to download
            const a = document.createElement('a');
            a.href = url;
            a.download = `${finalFilename}.sbv`;
            document.body.appendChild(a);
            a.click();

            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showSuccess('transcript-result', `Transkriptio '${result.video_title || ''}' ladattu onnistuneesti tiedostoon ${finalFilename}.sbv!`);
        } else {
            showSuccess('transcript-result', 'Transkriptio valmis, mutta sisältö puuttuu vastauksesta.');
        }

        // Clear the url input but keep basename for convenience
        document.getElementById('youtube-url').value = '';

    } catch (error) {
        console.error('Transcript error:', error);
        showError('transcript', 'Virhe transkription luomisessa: ' + error.message);
    } finally {
        setButtonLoading('transcript-btn', false);
    }
}

// ===========================
// Event Listeners
// ===========================
function setupEventListeners() {
    // Form toggle buttons
    showSignupBtn.addEventListener('click', showSignupForm);
    showLoginBtn.addEventListener('click', showLoginForm);

    // Password toggles
    toggleLoginPassword.addEventListener('click', () => {
        togglePasswordVisibility('login-password', toggleLoginPassword);
    });

    toggleSignupPassword.addEventListener('click', () => {
        togglePasswordVisibility('signup-password', toggleSignupPassword);
    });

    // Login form
    loginFormElement.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        handleLogin(email, password);
    });

    // Signup form
    signupFormElement.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        handleSignup(email, password);
    });

    // Logout button
    logoutBtn.addEventListener('click', handleLogout);

    // Transcript form
    transcriptFormElement.addEventListener('submit', (e) => {
        e.preventDefault();
        const youtubeUrl = document.getElementById('youtube-url').value;
        handleTranscriptSubmit(youtubeUrl);
    });

    // Auth state observer
    onAuthStateChanged(auth, (user) => {
        if (user) {
            console.log('User is signed in:', user.email);
            showDashboard(user);
        } else {
            console.log('User is signed out');
            showAuthForms();
        }
    });
}

// ===========================
// Initialize App
// ===========================
async function init() {
    const initialized = await initializeFirebase();
    if (initialized) {
        setupEventListeners();
    }
}

// Start the app when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
