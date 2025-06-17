// Progress: https://youtu.be/3PHXvlpOkf4?feature=shared&t=948
const colors = ["green", "red", "rgba(133,122,200)", "#f15025"];
const btn = document.getElementById("btn");
const color = document.querySelector(".color");

btn.addEventListener("click", function () {
    //get random number between 0 and 3 color[0...3]
    const randomNumber = 2;
    document.object.style.backgroundColor = colors[randomNumber];
    color.textContent = colors[randomNumber]

});