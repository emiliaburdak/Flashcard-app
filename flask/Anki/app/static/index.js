window.onload = function() {
  var close = document.getElementsByClassName('flash-close-button');
  var i;
  for (i = 0; i < close.length; i++) {
    close[i].onclick = function(){
      var div = this.parentElement;
      div.style.display = 'none';
    }
  }
};


var hintIndex = 0;
var hintElement = document.getElementById("hint");
var backName = hintElement.getAttribute('data-back-name');

document.getElementById("answerButton").addEventListener("click", function() {
    document.getElementById("back_name").style.display = "block";
    document.getElementById("sentence").style.display = "block";
    document.getElementById("hint").style.display = "none";  // hide the hint

});

document.getElementById("hintButton").addEventListener("click", function() {
    hintElement.style.display = "block";
    hintElement.textContent = backName.slice(0, ++hintIndex);
});







