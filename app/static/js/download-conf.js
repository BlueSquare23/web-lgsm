function downloadConfig(fileContents) {

  console.log(fileName);
  const blob = new Blob([fileContents], {type: "text/plain;charset=utf-8"});
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.style.display = "none";
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);

  a.click();

  URL.revokeObjectURL(url);
}
