// firebase_config.js
// SETUP INSTRUCTIONS:
// 1. Go to https://console.firebase.google.com/
// 2. Create a new project: "SmartStadiumOS"
// 3. Navigate to Realtime Database -> Create Database -> Start in Test Mode (for MVP)
// 4. Go to Project Settings -> General -> Web App (</>)
// 5. Copy your config keys into the object below.

import { initializeApp } from "firebase/app";
import { getDatabase, ref, set, onValue } from "firebase/database";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "smartstadiumos.firebaseapp.com",
  databaseURL: "https://smartstadiumos-default-rtdb.firebaseio.com",
  projectId: "smartstadiumos",
  storageBucket: "smartstadiumos.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:12345:web:abc"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// ---------------------------------------------------------
// EXAMPLES DUAL-SYNC FUNCTIONS (Backend <-> Frontend)
// ---------------------------------------------------------

/**
 * Sync Density Map to Firebase Realtime Database
 */
export const syncDensityToFirebase = (zoneName, occupancyDensity) => {
  const zoneRef = ref(database, 'stadium_density/' + zoneName);
  set(zoneRef, {
    density: occupancyDensity,
    timestamp: Date.now()
  });
};

/**
 * Listen for Critical Alerts from Central Command
 */
export const listenForAlerts = (callback) => {
  const alertsRef = ref(database, 'alerts/');
  onValue(alertsRef, (snapshot) => {
    const data = snapshot.val();
    if(data) {
       callback(data);
    }
  });
};

export { app, database };
