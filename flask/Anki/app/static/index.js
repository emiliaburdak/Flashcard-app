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


var audio = new Audio();
var lastClick = 0;

document.querySelectorAll('.speak').forEach(function(button) {
    button.addEventListener('click', function() {
        var now = Date.now();

        // Ignoruj kliknięcia, które są szybsze niż 2 sekund po poprzednim
        if (now - lastClick < 2000) {
            return;
        }

        lastClick = now;

        if (!audio.paused) {
            audio.pause();
        }

        var id = button.getAttribute('data-id');
        audio = new Audio('/speak/' + id);
        audio.play();
    });
});




