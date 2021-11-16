function copyToClipboard() {
  let copyText = document.getElementById("myInput");
  navigator.clipboard.writeText(copyText.value);

}
