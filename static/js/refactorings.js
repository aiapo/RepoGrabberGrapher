d3.json("/api/refactorings/groupBy/all/countBy/type")
.then(function(data){
    makeChart(data.count,"chart1","bar");
});

d3.json("/api/refactorings/groupBy/all/countBy/year")
.then(function(data){
    makeChart(data.count,"chart2","bar");
});

d3.json("/api/refactorings/groupBy/desktop/countBy/type")
.then(function(data){
    makeChart(data.count,"chart3","bar");
});

d3.json("/api/refactorings/groupBy/desktop/countBy/year")
.then(function(data){
    makeChart(data.count,"chart4","bar");
});

d3.json("/api/refactorings/groupBy/mobile/countBy/type")
.then(function(data){
    makeChart(data.count,"chart5","bar");
});

d3.json("/api/refactorings/groupBy/mobile/countBy/year")
.then(function(data){
    makeChart(data.count,"chart6","bar");
});

d3.json("/api/refactorings/groupBy/web/countBy/type")
.then(function(data){
    makeChart(data.count,"chart7","bar");
});

d3.json("/api/refactorings/groupBy/web/countBy/year")
.then(function(data){
    makeChart(data.count,"chart8","bar");
});