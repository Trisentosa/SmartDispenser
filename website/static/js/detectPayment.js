/**
 * This file is responsible to detect if payment has been completed
 * REDACTED!!! Potentially unsafe, because handling payment detection in frontend
 */

//url:/https://api-m.sandbox.paypal.com/v2/checkout/orders/:order_id/capture

console.log("detect payment is running...");

// $(`#pump${index}`).click(function () {
//   $.post(`/pump/${index}`, function (data) {
//     let msg = data["pump"] == true ? "ON" : "OFF";
//     $(`#pump${index}`).text(`Pump ${index} : ${msg}`);
//   });
// });

// Use this function with await in async, work like sleep in python
function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function checkPaymentStatus(accessToken, orderID) {
  const response = await fetch(
    `https://api-m.sandbox.paypal.com/v2/checkout/orders/${orderID}/capture`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    console.log(`Request failed with status ${response.status}`);
  } else {
    // console.log(response);
    console.log("Request successful!");
    window.location.href = "/controller";
  }
}

//continous loop checking payment status
async function autoDetect(accessToken, orderID) {
  while (true) {
    await timeout(3000);
    await checkPaymentStatus(accessToken, orderID);
  }
}
