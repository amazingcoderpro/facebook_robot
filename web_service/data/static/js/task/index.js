require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: '任务管理',
        sub: '新增、管理任务',
        path: ['task', 'task']
    });
    var categories=[], url='/api/task/', detailHtml='',
    newTask=function(){
        var req={accounts: [], category: categories[parseInt($('#modal-new select[name="category"]').val())],
            scheduler: {
                mode: parseInt($('#modal-new select[name="scheduler"]').val()),
                interval: parseInt($('#modal-new select[name="scheduler"]').val()) * 3600,
                start_date: $('#modal-new input[name="schedulerBeginDate"]').val() + 'T' + $('#modal-new input[name="schedulerBeginTime"]').val(),
                end_date: $('#modal-new input[name="schedulerEndDate"]').val() + 'T' + $('#modal-new input[name="schedulerEndTime"]').val()
            }};
        if($('#modal-new select[name="intervalUnit"]').val()=='0')req.scheduler.interval*=24;
        if(isNaN(req.scheduler.interval))req.scheduler.interval=0;
        if(req.scheduler.start_date.length<15)req.scheduler.start_date=null;
        if(req.scheduler.end_date.length<15)req.scheduler.end_date=null;
        $.each($('#modal-new input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
        if(req.name=='')global.showTip('请输入任务名称');
        else if(req.limit_counts=='')global.showTip('请输入任务需求数');
        else if((req.scheduler.mode==1||req.scheduler.mode==2)&&(req.scheduler.interval==0))global.showTip('请设置执行间隔');
        else if((req.scheduler.mode==1||req.scheduler.mode==3)&&!req.scheduler.start_date)global.showTip('请设置启动时间');
        else if((req.scheduler.mode==1||req.scheduler.mode==2)&&!req.scheduler.end_date)global.showTip('请设置最晚停止时间');
        else {
            $.ajax({
                url: global.getAPI(url),
                contentType: "application/json",
                method: 'post',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: '任务添加成功', danger: false});
                    dataTable.ajax.reload();
                    $('#modal-new input').val(''),
                    $('#modal-new').modal('hide')
                }
            });
        }
    },
    modifyTask=function(item){
        global.showDetail({
            'div': '#detail',
            'html': detailHtml,
            'data': item,
            'displayScheduler': displayScheduler,
            'displayInterval': displayInterval
        }),
        $('#info .box-title').text(item.name+'的基本信息'),
        $('#info .save').on('click',function(){
            var req={};
//            Object.assign(req, item);
            $.each($('#detail input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
            if(req.name=='')global.showTip('请输入任务名称');
            else $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'patch',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: '任务信息更新成功', danger: false}),
                    dataTable.ajax.reload()
                },
                error: function(){global.showTip('任务信息更新失败，请稍后再试')}
            });
        })
    },
    schedulerMode = ['立即执行（只执行一次）',
                '间隔执行',
                '间隔执行，立即开始',
                '定时执行，指定时间执行'],
    // 显示调度类型
    displayScheduler=function(mode){
        return schedulerMode[mode]
    },
    // 显示间隔
    displayInterval=function(interval){
        interval /= 3600;
        if(interval / 24 >= 1)return interval / 24 + '天';
        return interval + '时'
    },
    // 调度类型切换
    onModeChange=function(){
        var mode=parseInt($('#modal-new select[name="scheduler"]').val()), switchEl=function(el, isShow){
            var group=$(el).parents('.form-group');
            if(isShow)group.removeClass('hide');
            else group.addClass('hide');
        };
        switchEl('#modal-new input[name="interval"]', mode==1||mode==2);
        switchEl('#modal-new input[name="schedulerBeginDate"]', mode==1||mode==3);
        switchEl('#modal-new input[name="schedulerEndDate"]', mode==1||mode==2);
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: '类型',
                    data: 'category.name'
                },
                {
                    title: '类型',
                    data: 'scheduler.mode',
                    render: displayScheduler
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
            ],
            onSingleRowClick: function(item){
                if(item)modifyTask(item);
                else $('#detail').html('')
            },
            onButtonClick: function(button, table, item, id){
                if(button.hasClass('modify'))modifyGroup(item);
                else if(button.hasClass('reset-password'))resetPwd(item);
                else if(button.hasClass('delete'))
                    global.dialog.deleteWarning('是否删除任务？', function(){
                        $.ajax({
                            url: global.getAPI(url+id+'/'),
                            contentType: "application/json",
                            method: 'delete',
                            success: function(data){
                                global.showTip({word: '任务删除成功', danger: false});
                                dataTable.ajax.reload(),
                                $('#detail').html('')
                            }
                        });
                    });
            }
        });
        $('#modal-new .ok').on('click', newTask)
        detailHtml=$('#detail').html(),
        $('#detail').html(''),
        $('input.pick-date').datepicker({
          autoclose: true,
          format: 'yyyy-mm-dd'
        }),
        $('.timepicker').timepicker({
          showInputs: false,
          showMeridian: false
        })
        $.ajax({
            url: global.getAPI('/api/taskCategories/'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                categories = data.data;
                var el=$('#modal-new select[name="category"]');
                $.each(categories, function(i, item){
                    el.append('<option value="'+i+'">'+item.name+'</option>')
                })
            }
        }),
        $.each(schedulerMode, function(i, item){$('#modal-new select[name="scheduler"]').append('<option value="'+i+'">'+item+'</option>')})
        $('#modal-new select[name="scheduler"]').on('change', onModeChange);
        onModeChange();
})