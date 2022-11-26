let voiceButton = $("#voiceButton");
let voiceText = $("#voiceText");
let voiceLogo = $("#voiceLogo");

$.get("/voiceActive", function (voiceActive) {
  let isActive = voiceActive["isActive"];
  changeButtonStyle(isActive);
});

voiceButton.click(function () {
  $.post("/voiceActive", function (voiceActive) {
    let isActive = voiceActive["isActive"];
    changeButtonStyle(isActive);
  });
});

function changeButtonStyle(isActive) {
  if (isActive) {
    voiceLogo.text("record_voice_over");
    voiceButton.removeClass("btn-secondary").addClass("btn-info");
    voiceText.text("Voice: ON");
  } else {
    voiceLogo.text("voice_over_off");
    voiceButton.removeClass("btn-info").addClass("btn-secondary");
    voiceText.text("Voice: OFF");
  }
}
