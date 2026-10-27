/**
 * NoteSphere - Firebase Client Configuration
 * Replace the values below with your Firebase Project Web App config
 * from the Firebase Console: Project Settings -> General -> Your apps -> Web app
 */

const firebaseConfig = {
  apiKey: "AIzaSyB4Ur8VO7yf_UJ10mPDnItsgHAnLtloBqw",
  authDomain: "notesphere-cc.firebaseapp.com",
  projectId: "notesphere-cc",
  storageBucket: "notesphere-cc.firebasestorage.app",
  messagingSenderId: "644660468788",
  appId: "1:644660468788:web:684bef567425d693b23e61"

};


// Check if credentials are placeholders
const isFirebasePlaceholder = !firebaseConfig.apiKey || firebaseConfig.apiKey.includes("YOUR_FIREBASE");

let auth = null;

if (!isFirebasePlaceholder && typeof firebase !== "undefined") {
  try {
    firebase.initializeApp(firebaseConfig);
    auth = firebase.auth();
    console.log("[NoteSphere] Firebase Client Auth initialized successfully.");
  } catch (err) {
    console.warn("[NoteSphere] Firebase init warning:", err);
  }
} else {
  console.log("[NoteSphere] Running in Local Development Auth Mode (Dev Mock Tokens enabled).");
}
