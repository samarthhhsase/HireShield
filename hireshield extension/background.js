/**
 * HireShield Background Service Worker (Optional)
 * 
 * Manages extension lifecycle and background synchronization.
 */

chrome.runtime.onInstalled.addListener(() => {
  console.log("HireShield Extension v1.0.0 installed successfully.");
});
