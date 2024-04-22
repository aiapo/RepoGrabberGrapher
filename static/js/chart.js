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
        if (!isNaN(Number(data[i])))
            y.push(Number(data[i]));
        else
            y.push(data[i]);

        if (!isNaN(Number(i)))
            x.push(Number(i));
        else
            x.push(i);
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