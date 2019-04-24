require(['vue', 'utils/global', 'utils/table', 'task/common', 'vps/common'], function(Vue, global, table, taskCommon, vpsCommon){
    global.initModule({
        title: '控制台',
        sub: 'Facebook Auto 状态舱',
        path: ['dashboard']
    });

    // 获取任务状态分布
    $.ajax({
        url: global.getAPI('/api/task/sum/'),
        contentType: "application/json",
        method: 'get',
        success: function(data){
            if(typeof data=='string')data = JSON.parse(data);
            var labels=[], values=[];
            $.each(data.data, function(i,item){labels.push(item['status']),values.push(item['value'])})

            new Chart($('#taskStatus').get(0).getContext('2d'),{
                "type": "doughnut",
                "data":{
                    "labels":labels,
                    "datasets":[{
                        "label":"My First Dataset",
                        "data":values,
                        "backgroundColor":['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de']
                    }]
                }
            })
        }
    });
    // 获取 Agent 状态
    if(global.user.category.isAdmin)
    $.ajax({
        url: global.getAPI('/api/area/?all=true'),
        contentType: "application/json",
        method: 'get',
        success: function(data){
            if(typeof data=='string')data = JSON.parse(data);
            data = vpsCommon.groupByStatus(data, true);
            new Chart($('#agentStatus').get(0).getContext('2d'), {
            type: 'bar',
            data: {
                labels: data['name'],
                datasets: [{
                    label: '# of Votes',
                    data: data['running_tasks'],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                legend: {
                    display: false
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        })
        }
    });
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
                data: 'creator.fullname',
                visible: global.user.category.isAdmin
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