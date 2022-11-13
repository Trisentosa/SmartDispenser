//return to home if user is inactive every x secondds
//interval if order is in the making during that xth seconds
function returnAfterInactive(seconds) {
  setInterval(async () => {
    const response = await fetch(`/waitUser`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error(`Request failed with status ${response.status}`);
    } else {
      let jsonData = await response.json();
      if (
        jsonData["orderSignal"] === false &&
        jsonData["irSignal"] === false &&
        jsonData["state"] === 1
      ) {
        window.location.replace("http://127.0.0.1:5000/");
      }
    }
  }, seconds * 1000);
}

//return to home if state is 0 (order done or manual access)
function returnAfterOrderFinished(seconds) {
  setInterval(async () => {
    const response = await fetch(`/waitUser`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error(`Request failed with status ${response.status}`);
    } else {
      let jsonData = await response.json();
      if (jsonData["state"] === 0) {
        window.location.replace("http://127.0.0.1:5000/");
      }
    }
  }, seconds * 1000);
}

returnAfterInactive(60);
returnAfterOrderFinished(2);
