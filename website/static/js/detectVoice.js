/**
 * This file is responsible to detect if voice signal is set
 */

console.log("detect voice is running...");

// Use this function with await in async, work like sleep in python
function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function checkVoiceSignal() {
  const response = await fetch(`/detectVoice`, {
    method: "POST",
  });

  if (!response.ok) {
    console.error(`Request failed with status ${response.status}`);
  } else {
    console.log(response);
    if (response["status"] == 200) {
      window.location.replace(response["url"]);
    }
  }
}

//continous loop checking payment status
async function autoDetect() {
  while (true) {
    await timeout(1500);
    await checkVoiceSignal();
  }
}

autoDetect();
