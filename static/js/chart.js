function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

var colors = [];
for (i = 0; i < 100; i++) {
    colors.push(getRandomColor());
}

function makeChart(data, ch, type) {
    var haveLabel = false;
    let x = [];
    let y = [];

    if (type == "pie"){
        haveLabel = true;
    }

    for(var i in data){
        let tempX
        let tempY

        if((typeof data[i] === "object")){
            tempX=Object.values(data[i])[0]
            tempY=Object.values(data[i])[1]
        }else{
            tempX = i
            tempY = data[i]
        }

        console.log(tempX + " "+ tempY)

        if (!isNaN(Number(tempY)))
            y.push(Number(tempY));
        else
            y.push(tempY);

        if (!isNaN(Number(tempX)))
            x.push(Number(tempX));
        else
            x.push(tempX);
    }

    var chart = new Chart(ch, {
        type: type,
        options: {
            maintainAspectRatio: true,
            responsive: true,
            legend: {
                display: haveLabel
            }
        },
        data: {
            labels: x,
            datasets: [
                {
                    logarithmic: false,
                    data: y,
                    backgroundColor: colors
                }
            ]
        }
    });
}

function makeTable(data, table) {
    console.log(data);
    new gridjs.Grid({
        data: data,
        pagination: {
            limit: 5
        },
        resizable: true,
        sort: true
    }).render(document.getElementById(table));
}