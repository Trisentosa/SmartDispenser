console.log("pump controller is running");

for (let index = 1; index < 7; index++) {
  $(`#pump${index}`).click(function () {
    $.post(`/pump/${index}`, function (data) {
      let msg = data["pump"] == true ? "ON" : "OFF";
      $(`#pump${index}`).text(`Pump ${index} : ${msg}`);
    });
  });
}
