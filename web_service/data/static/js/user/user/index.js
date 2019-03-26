require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: '用户管理',
        sub: '管理普通用户、设置管理员、授权可执行任务',
        path: ['user']
    });
    var categories=[], url='/api/users/', detailHtml='',
    newUser=function(){
        var req={};
        $.each($('#modal-new input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
        if(req.username=='')general.showTip('请输入用户名');
        else if(req.fullname=='')general.showTip('请输入用户姓名');
        else if(req.email=='')general.showTip('请输入邮件地址');
        else if(req.pwd=='')general.showTip('请输入初始密码');
        else $.ajax({
            url: global.getAPI(url),
            contentType: "application/json",
            method: 'post',
            data: JSON.stringify(req),
            success: function(data){
                general.showTip('用户添加成功');
                table.ajax.reload();
                $('#modal-new input').val(''),
                $('#modal-new').modal('hide')
            }
        });
    },
    modifyUser=function(item){
        $('#detail').removeClass('none').html(detailHtml),
        $('#info .box-title').text(item.fullname+'的基本信息'),
        $.each(item, function(i, propName){$('#info input[name="'+propName+'"]').val(item[propName])});
        $('#info p.username').text(item.username);
        $('#info .save').on('click',function(){
            var req={};
        $.each($('#info input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
            $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'patch',
                data: JSON.stringify(req),
                success: function(data){
                    general.showTip('用户信息更新成功'),
                    table.ajax.reload()
                },
                error: function(){general.showTip('用户信息更新失败，请稍后再试')}
            });
        })
    },
    resetPwd=function(item){
        var dialog='#modal-reset'
        $(dialog+' input').val(''),
        $(dialog+' .ok').off('click').on('click', function(){
            var req={password: $(dialog+' input').val().trim()};
            if(req.password=='')general.showTip('请输入初始密码');
            else $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'patch',
                data: JSON.stringify(req),
                success: function(data){
                    general.showTip('用户密码重置成功，请及时通知对方');
                    $(dialog+' input').val(''),
                    $(dialog).modal('hide')
                }
            });
        }),
        $(dialog).modal('show')
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
                    data: 'fullname'
                },
                {
                    title: '邮箱',
                    data: 'email'
                },
                {
                    title: '可执行任务',
                    data: 'enable_tasks'
                },
            ],
            onSingleRowClick: function(item){
                if(item)modifyUser(item);
                else $('#detail').html('')
            },
            onButtonClick: function(button, table, item, id){
                if(button.hasClass('modify'))modifyGroup(item);
                else if(button.hasClass('reset-password'))resetPwd(item);
                else if(button.hasClass('delete'))
                    general.dialog.deleteWarning('是否删除用户？', function(){
                        $.ajax({
                            url: general.getAPI(url+id+'/'),
                            contentType: "application/json",
                            method: 'delete',
                            success: function(data){
                                general.showTip('用户删除成功');
                                dataTable.ajax.reload(),
                                $('#detail').html('')
                            }
                        });
                    });
            }
        });
        $('#modal-new .ok').on('click', newUser)
        detailHtml=$('#detail').html(),
        $('#detail').html(''),
        $.ajax({
            url: general.getAPI('/api/userCategories/'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                categories = data.data;
                var el=$('#modal-new select[name="category"]');
                $.each(categories, function(i, item){
                    el.append('<option value="'+item.category+'">'+item.name+'</option>')
                })
            }
        })
})