d3.json("/api/repos/countBy/push")
.then(function(data){
    makeChart(data.count,"chart1","pie");
});

d3.json("/api/repos/countBy/creation")
.then(function(data){
    makeChart(data.count,"chart2","pie");
});

d3.json("/api/repos/countBy/update")
.then(function(data){
    makeChart(data.count,"chart3","pie");
});

d3.json("/api/repos/countBy/size/binCount/50")
.then(function(data){
    makeChart(data,"chart7","bar");
});

d3.json("/api/repos/countBy/commit/binCount/15")
.then(function(data){
    makeChart(data,"chart5","bar");
});

d3.json("/api/repos/countBy/committer/binCount/15")
.then(function(data){
    makeChart(data,"chart6","bar");
});

d3.json("/api/repos/countBy/domain")
.then(function(data){
    makeChart(data.count,"chart4","pie");
});

$('#repositoriesTable').DataTable( {
    ajax: '/api/repos/list',
    dataSrc: 'data',
    columns: [
        { data: 'id' },
        { data: 'name' },
        { data: 'owner' },
        { data: 'url' },
        { data: 'description' },
        { data: 'primarylanguage' },
        { data: 'creationdate' },
        { data: 'updatedate' },
        { data: 'pushdate' },
        { data: 'isarchived' },
        { data: 'archivedat' },
        { data: 'isforked' },
        { data: 'isempty' },
        { data: 'islocked' },
        { data: 'isdisabled' },
        { data: 'istemplate' },
        { data: 'totalissueusers' },
        { data: 'totalmentionableusers' },
        { data: 'totalcommittercount' },
        { data: 'totalprojectsize' },
        { data: 'totalcommits' },
        { data: 'issuecount' },
        { data: 'forkcount' },
        { data: 'starcount' },
        { data: 'watchcount' },
        { data: 'branchname' },
        { data: 'domain' }
    ],
        responsive: true  
} );