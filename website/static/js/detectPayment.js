/**
 * This file is responsible to detect if payment has been completed
 */

//url:/https://api-m.sandbox.paypal.com/v2/checkout/orders/:order_id/capture

console.log("detect payment is running...");

function myFunc(t) {
  console.log(t);
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
    throw new Error(`Request failed with status ${response.status}`);
  }

  console.log(response);
  console.log("Request successful!");
}
