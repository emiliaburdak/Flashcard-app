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


document.getElementById("answerButton").addEventListener("click", function() {
    document.getElementById("back_name").style.display = "block";
    document.getElementById("sentence").style.display = "block";
});
