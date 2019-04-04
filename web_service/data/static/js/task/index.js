require(['vue', 'utils/global', 'utils/table', 'utils/form', 'task/common'], function(Vue, global, table, form, taskCommon){
    global.initModule({
        title: '任务管理',
        sub: '新增、管理任务',
        path: ['task', 'task']
    });
    var categories=[], url='/api/task/', detailHtml='',
    newTask=function(){
        var req={accounts: [], category: null, configure: {}, scheduler: null}, intervalUnit=parseInt($('#modal-new select[name="intervalUnit"]').val());
        $.each($('#modal-new').find('input,textarea,select'), function(i, item){
            item=$(item);
            var name=item.attr('name');
            if(name.substr(0, 10) == 'configure_')req.configure[name.substr(10)] = item.attr('type')=='checkbox'?item.prop('checked'):item.val().trim();
            else req[name]=item.attr('type')=='checkbox'?item.prop('checked'):item.val().trim()});
        req.category = categories[parseInt($('#modal-new select[name="category"]').val())];
        req.scheduler = {
            mode: parseInt($('#modal-new select[name="scheduler"]').val()),
            interval: parseInt($('#modal-new input[name="interval"]').val()),
            start_date: $('#modal-new input[name="schedulerBeginDate"]').val() + ' ' + $('#modal-new input[name="schedulerBeginTime"]').val(),//+'+08:00',
            end_date: $('#modal-new input[name="schedulerEndDate"]').val() + ' ' + $('#modal-new input[name="schedulerEndTime"]').val()//+'+08:00'
        };
        if(intervalUnit==0)req.scheduler.interval*=86400;
        else if(intervalUnit==1)req.scheduler.interval*=3600;
        else req.scheduler.interval *= 60;
        if(isNaN(req.scheduler.interval))req.scheduler.interval=0;
        if(req.scheduler.start_date.length<15)req.scheduler.start_date=null;
        if(req.scheduler.end_date.length<15)req.scheduler.end_date=null;
        if(req.name=='')global.showTip('请输入任务名称');
        else if(req.limit_counts=='')global.showTip('请输入任务需求数');
        else if(req.accounts_num=='')global.showTip('请输入任务账号数');
        else if((req.scheduler.mode==1||req.scheduler.mode==2)&&(req.scheduler.interval==0))global.showTip('请设置执行间隔');
        else if((req.scheduler.mode==1||req.scheduler.mode==2)&&intervalUnit==2&&req.scheduler.interval<300)global.showTip('时间间隔不能小于5分钟');
        else if(/*(req.scheduler.mode==1||*/req.scheduler.mode==3&&!req.scheduler.start_date)global.showTip('请设置启动时间');
//        else if((req.scheduler.mode==1||req.scheduler.mode==2)&&!req.scheduler.end_date)global.showTip('请设置最晚停止时间');
        else if(!isValidConfig(req.configure, req.category.cfg));
        else {
            req.configure = JSON.stringify(req.configure),
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
        var canEditEndDate = [1, 2].indexOf(item.scheduler.mode)>=0 && ['new', 'pending', 'pausing', 'running'].indexOf(item.status)>=0;
        global.showDetail({
            'div': '#detail',
            'html': detailHtml,
            'data': item,
            'displayScheduler': taskCommon.displayScheduler,
            'displayInterval': displayInterval
        }),
        $('#info .box-title').text(item.name+'的基本信息');
        if(canEditEndDate){
            $('#detail input.pick-date').val(item.scheduler.end_date?item.scheduler.end_date.substr(0,10):'').datepicker({
              autoclose: true,
              format: 'yyyy-mm-dd'
            }),
            $('#detail .timepicker').timepicker({
              showInputs: false,
              showMeridian: false,
              defaultTime: item.scheduler.end_date?item.scheduler.end_date.substr(11, 8):'10:00:00'
            }),
            $('.form-group.end-date').find('p').remove()
        }else $('.form-group.end-date').find('.input-group').remove();
        $('#detail p.configure').html(displayConfigure(item.configure, item.category)),
        table.initTable('#accountTable', {
            ajax: {url: global.getAPI(url+item.id+'/account/')},
            columns: [
                {
                    title: '类型',
                    data: 'account.category.name'
                },
                {
                    title: '姓名',
                    data: 'account.name'
                },
                {
                    title: '账号',
                    data: 'account.account'
                },
                {
                    title: '状态',
                    data: 'account.status'
                }
            ]
        }),
        $('#accountTableButtons button.export').on('click', function(){
            window.open(global.getAPI(url+item.id+'/account/?export=true'))
        }),
        $('#info .save').on('click',function(){
            var req={};
//            Object.assign(req, item);
            $.each($('#detail input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
            if(canEditEndDate)
                req.scheduler={end_date: $('#detail input[name="schedulerEndDate"]').val() + ' ' + $('#detail input[name="schedulerEndTime"]').val()}//+'+08:00'}
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
    updateStatus=function(id, newStatus, successMsg){
        $.ajax({
            url: global.getAPI(url+id+'/'),
            contentType: "application/json",
            method: 'patch',
            data: JSON.stringify({status:newStatus}),
            success: function(data){
                global.showTip({word: successMsg, danger: false});
                dataTable.ajax.reload(),
                $('#detail').html('')
            }
        });
    },
    // 任务启动停止
    start_stop=function(item){
        if(item.status=='running')updateStatus(item.id, 'pausing', '任务暂停成功')
        else if(item.status=='pausing')updateStatus(item.id, 'running', '任务启动成功')
    },
    // 显示间隔
    displayInterval=function(interval){
        if(interval / 86400 >= 1)return interval / 86400 +'天';
        else if(interval / 3600 >= 1) return interval / 3600 + '小时';
        return (interval / 60).toFixed(1) + '分钟';
    },
    // 任务类型改变
    onCategoryChange=function(){
        // 处理自定义配置字段
        var cps=$('#modal-new .custom-params'), html=[];
        cps.html('');
        $.each(categories[parseInt($('#modal-new select[name="category"]').val())].cfg, function(i, item){
            html.push('<div class="form-group">');
            if(item.dataType == 'bool')
                html.push('<label><input type="checkbox" name="configure_'+ item.name +'">'+item.title+'</label>');
            else{
                html.push('<label>'+item.title+'</label>');
                if(item.dataType == 'string' && typeof item.options != 'undefined'){
                    html.push('<select name="configure_'+ item.name +'" class="form-control">');
                    $.each(item.options, function(j,option){html.push('<option>'+ option +'</option>')})
                    html.push('</select>')
                }else{
                    html.push('<input type="'+{str: 'text', int: 'tel', float: 'number'}[item.dataType] +'" ');
                    if(['int', 'float'].indexOf(item.dataType)>=0)html.push(' value="'+item.defaultValue+'" ');
                    html.push('class="form-control" name="configure_'+ item.name +'">')
                }
            }
            html.push('</div>')
        }),
        cps.html(html.join(''))
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
//        $('input.pick-date').datepicker('setDate', new Date()),
        $('.timepicker').timepicker('setTime', '08:00')
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: 'ID',
                    data: 'id'
                },
                {
                    title: '名称',
                    data: 'name'
                },
                {
                    title: '状态',
                    data: 'status'
                },
                {
                    title: '类型',
                    data: 'category.name'
                },
                {
                    title: '调度类型',
                    data: 'scheduler.mode',
                    render: taskCommon.displayScheduler
                },
                {
                    title: '创建者',
                    data: 'creator.fullname',
                    visible: global.user.category.isAdmin
                }
            ],
            onSingleRowClick: function(item){
                if(item){
                    modifyTask(item);
                    var button=$('button.start-stop');
                    if(['running', 'pausing'].indexOf(item.status)>=0)
                        button.removeClass('hide').text(item.status=='running'?'暂停':'启动')
                    else button.addClass('hide')
                }else $('#detail').html('');
            },
            onButtonClick: function(button, table, item, id){
                if(button.hasClass('modify'))modifyGroup(item);
                else if(button.hasClass('reset-password'))resetPwd(item);
                else if(button.hasClass('start-stop'))start_stop(item);
                else if(button.hasClass('delete'))
                    global.dialog.deleteWarning('是否取消任务？', function(){
                        updateStatus(id, 'cancelled', '任务取消成功')
                    });
            }
        }),
        // 转换类型自定义参数配置
        parseConfigure=function(cfg){
            var params = [];
            $.each(cfg.split('\n'), function(i, item){
                item = item.trim();
                if(item == '')return;
                item = item.split(':');
                var result = {
                    name: item[0],
                    title: item[1],
                    dataType: item[2],
                    defaultValue: item[3]
                };
                if(result.dataType=='bool')
                    result.defaultValue = result.defaultValue.toLowerCase() == 'true';
                else if (['int', 'float'].indexOf(result.dataType)>=0){
                    result.defaultValue = result.dataType == 'int' ? parseInt(result.defaultValue): parseFloat(result.defaultValue);
                    if(cfg.length==5){
                        var minMax = item[4].split('|');
                        result.min = result.dataType == 'int' ? parseInt(minMax[0]): parseFloat(minMax[0]);
                        if(minMax.length==2)
                            result.max = result.dataType == 'int' ? parseInt(minMax[1]): parseFloat(minMax[1]);
                    }
                }else if(result.dataType == 'string' && cfg.length==5)
                    result.options = item[4].split('|');
                params.push(result)
            })
            return params
        },
        // 验证自定义配置是否有效
        isValidConfig=function(configure, cfg){
            for(var i=0;i<cfg.length;i++){
                var field = cfg[i];
                if(typeof configure[field.name] == 'undefined')configure[field.name]=field.defaultValue;
                else{
                    var value = configure[field.name];
                    if(['int', 'float'].indexOf(field.dataType)>=0){
                        configure[field.name] = field.dataType == 'int'?parseInt(value):parseFloat(value);
                        value = configure[field.name];
                        if(isNaN(value)){
                            global.showTip(field.title+'没有输入正确的数字');
                            return false
                        }else if(typeof field.min == 'undefined' && value < field.min){
                            global.showTip(field.title+'没有输入不能小于'+field.min);
                            return false
                        }else if(typeof field.max == 'undefined' && value > field.max){
                            global.showTip(field.title+'没有输入不能大于'+field.max);
                            return false
                        }
                    }else if(field.dataType == 'string' && value == '')
                        configure[field.name] = field.defaultValue
                }
            }
            return true
        },
        // 显示自定义配置字段信息
        displayConfigure=function(configure, category){
            if(category.configure==''||category.configure=='{}')return;
            if(typeof category.cfg == 'undefined')category.cfg = parseConfigure(category.configure);
            try{configure = JSON.parse(configure)}catch(e){return '';}
            var html=[];
            $.each(category.cfg, function(i, item){
                if(typeof configure[item.name] == 'undefined')return;
                try{html.push('<p>'+item.title+': '+ configure[item.name])}catch(e){}
            })
            return html.join('')
        };
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
        // 获取任务类型
        $.ajax({
            url: global.getAPI('/api/taskCategories/'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                categories = data.data;
                var el=$('#modal-new select[name="category"]');
                $.each(categories, function(i, item){
                    item.cfg = parseConfigure(item.configure),
                    el.append('<option value="'+i+'">'+item.name+'</option>')
                }),
                onCategoryChange()
            }
        }),
        $.each(taskCommon.schedulerMode, function(i, item){$('#modal-new select[name="scheduler"]').append('<option value="'+i+'">'+item+'</option>')})
        $('#modal-new select[name="category"]').on('change', onCategoryChange);
        $('#modal-new select[name="scheduler"]').on('change', onModeChange);
        $('button.new').on('click', function(){
            $('#modal-new').modal('show'),
            onCategoryChange(), onModeChange()
        })
})