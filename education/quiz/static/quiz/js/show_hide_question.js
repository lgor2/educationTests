document.getElementById("question_type").addEventListener("change", function () {
  var selectedItem = this.value;

  var divs = document.querySelectorAll("div.question_type");
  divs.forEach(function (div) {
    div.style.display = "none";
  });

  document.getElementById("q_" + selectedItem).style.display = "block";
});