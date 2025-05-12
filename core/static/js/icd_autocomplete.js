const inp = document.getElementById("icd-code");
if (inp) {
  let timer;
  inp.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      fetch(`/ajax/icd11-autocomplete/?q=${encodeURIComponent(inp.value)}`)
        .then(r => r.json())
        .then(matches => {
          // TODO: replace this console.log with your dropdown rendering
          console.log(matches);  // [{code:"BA00", title:"Acute appendicitis"}, …]
        });
    }, 250);
  });
}
