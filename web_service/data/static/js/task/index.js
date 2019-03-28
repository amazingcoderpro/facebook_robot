require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: '任务管理',
        sub: '新增、管理任务',
        path: ['task']
    });
    var categories=[], url='/api/task/', detailHtml='',
    newAccount=function(){
        var req={category: {name: $('#modal-new select[name="category"]').val()}};
        $.each($('#modal-new input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
        if(req.username=='')global.showTip('请输入任务名');
        else if(req.fullname=='')global.showTip('请输入任务姓名');
        else if(req.email=='')global.showTip('请输入邮件地址');
        else if(req.pwd=='')global.showTip('请输入初始密码');
        else $.ajax({
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
    },
    modifyAccount=function(item){
        $('#detail').removeClass('none').html(detailHtml),
        $('#info .box-title').text(item.name+'的基本信息'),
        $.each(item, function(propName, value){$('#info input[name="'+propName+'"]').val(value)});
        $('#info p.category').text(item.category.name);
        $('#info .save').on('click',function(){
            var req={};
            Object.assign(req, item);
            $.each($('#detail input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
            if(req.fullname=='')global.showTip('请输入任务姓名');
            else if(req.email=='')global.showTip('请输入邮件地址');
            else $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'put',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: '任务信息更新成功', danger: false}),
                    dataTable.ajax.reload()
                },
                error: function(){global.showTip('任务信息更新失败，请稍后再试')}
            });
        })
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: '类型',
                    data: 'category.name'
                },
                {
                    title: '姓名',
                    data: 'name'
                },
                {
                    title: '账号',
                    data: 'account'
                },
                {
                    title: '可执行任务',
                    data: 'enable_tasks'
                },
            ],
            onSingleRowClick: function(item){
                if(item)modifyAccount(item);
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
        $('#modal-new .ok').on('click', newAccount)
        detailHtml=$('#detail').html(),
        $('#detail').html(''),
        $.ajax({
            url: global.getAPI('/api/accountCategories/'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                categories = data.data;
                var el=$('#modal-new select[name="category"]');
                $.each(categories, function(i, item){
                    el.append('<option value="'+item.name+'">'+item.name+'</option>')
                })
            }
        })
})