/**
 * This file is responsible to detect if payment has been completed
 */

//url:/https://api-m.sandbox.paypal.com/v2/checkout/orders/:order_id/capture

console.log("detect payment is running...");

// Use this function with await in async, work like sleep in python
function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function checkPaymentStatus() {
  const response = await fetch(`/detectPayment`, {
    method: "POST",
    // headers: {
    //   Authorization: `Bearer ${accessToken}`,
    //   "Content-Type": "application/json",
    // },
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
    await timeout(3000);
    await checkPaymentStatus();
  }
}

autoDetect();
