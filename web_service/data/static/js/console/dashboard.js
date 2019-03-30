require(['vue', 'utils/global', 'utils/table', 'task/common'], function(Vue, global, table, taskCommon){
    global.initModule({
        title: '控制台',
        sub: 'Facebook Auto 驾驶舱',
        path: ['dashboard']
    });

    // 获取任务状态分布
    $.ajax({
        url: global.getAPI('/api/task/sum/'),
        contentType: "application/json",
        method: 'get',
        success: function(data){
            data = JSON.parse(data);
            var pieChartCanvas = $('#pieChart').get(0).getContext('2d'),
                pieChart = new Chart(pieChartCanvas),
                colors = ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de'],
                PieData = [];
            $.each(data.data, function(i, item){
                PieData.push({
                    value    : item['value'],
                    color    : colors[i % colors.length],
                    highlight: colors[i % colors.length],
                    label    : item['status']
                })
            });
            var pieOptions     = {
              //Boolean - Whether we should show a stroke on each segment
              segmentShowStroke    : true,
              //String - The colour of each segment stroke
              segmentStrokeColor   : '#fff',
              //Number - The width of each segment stroke
              segmentStrokeWidth   : 2,
              //Number - The percentage of the chart that we cut out of the middle
              percentageInnerCutout: 50, // This is 0 for Pie charts
              //Number - Amount of animation steps
              animationSteps       : 100,
              //String - Animation easing effect
              animationEasing      : 'easeOutBounce',
              //Boolean - Whether we animate the rotation of the Doughnut
              animateRotate        : true,
              //Boolean - Whether we animate scaling the Doughnut from the centre
              animateScale         : false,
              //Boolean - whether to make the chart responsive to window resizing
              responsive           : true,
              // Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
              maintainAspectRatio  : true,
              //String - A legend template
              legendTemplate       : '<ul class="<%=name.toLowerCase()%>-legend"><% for (var i=0; i<segments.length; i++){%><li><span style="background-color:<%=segments[i].fillColor%>"></span><%if(segments[i].label){%><%=segments[i].label%><%}%></li><%}%></ul>'
            }
            //Create pie or douhnut chart
            // You can switch between pie and douhnut using the method below.
            pieChart.Doughnut(PieData, pieOptions)
        }
    }),
    // 展示运行中的任务
    table.initTable('#runningTask table', {
        searching: false,
        ajax: {url: global.getAPI('/api/task/?status=running')},
        columns: [
            {
                title: '类型',
                data: 'category.name'
            },
            {
                title: '类型',
                data: 'scheduler.mode',
                render: taskCommon.displayScheduler
            },
            {
                title: '创建者',
                data: 'creator.fullname'
            },
            {
                title: '名称',
                data: 'name'
            },
            {
                title: '状态',
                data: 'status'
            }
        ]
    })
})