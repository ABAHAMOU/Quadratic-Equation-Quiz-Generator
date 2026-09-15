let duree = 150;
let timerDiv = document.getElementById("timer");

let interval = setInterval(()=>{
    if(duree <= 0){
        clearInterval(interval);
        document.getElementById("exerciceForm").submit();
    } else{
        timerDiv.textContent = `⏳ Temps restant : ${duree}s`;
        duree--;
    }
},1000);