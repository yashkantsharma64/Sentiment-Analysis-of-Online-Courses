const b = document.getElementById("btn");
const u = document.getElementById("url");
let chartId = null;

b.addEventListener("click", function(e) {
    console.log("u.innerHTML = " + u.value);
    var videoID = u.value;
    var dat = { input: videoID };
    fetch('/yt.html/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dat)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received status:', data.status);
        console.log('Received score:', data.score);
        console.log('positive:', data.positive);
        console.log('negative:', data.negative);
        console.log('neutral:', data.neutral);
        var sum = data.positive + data.negative + data.neutral
        var chrt = document.getElementById("chartId").getContext("2d");
        if(chartId) {
            chartId.destroy();
        }
        chartId = new Chart(chrt, {
           type: 'pie',
           data: {
              labels: ['Positive', 'Negative', 'Neutral'],
              datasets: [{
                 label: "Sentiment Analysis",
                 data: [(data.positive/sum)*100, (data.negative/sum)*100, (data.neutral/sum)*100],
                 backgroundColor: ['green', 'red', 'blue'],
                 hoverOffset: 5
              }],
           },
           options: {
              responsive: false,
           },
        });
        const rev = document.getElementById('r-box');
        const sc = document.getElementById('s-box');
        rev.innerHTML = data.status;
        // let n = data.score.toString().substring(0, data.score.toString().length - 18);
        // let result = parseFloat(n);

        // console.log(result);
        sc.innerHTML = data.score;
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle any errors that occur during the AJAX request
    });
});