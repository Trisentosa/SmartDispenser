let voiceButton = $("#voiceButton");
let voiceText = $("#voiceText");
let voiceLogo = $("#voiceLogo");

voiceButton.click(function () {
  voiceLogo.text("record_voice_over");
  voiceButton.removeClass("btn-secondary").addClass("btn-info");
  voiceText.text("Voice: ON");
});
