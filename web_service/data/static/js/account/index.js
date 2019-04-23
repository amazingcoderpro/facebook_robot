require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: '社交账号管理',
        sub: '新增、导入、管理社交账号',
        path: ['account']
    });
    var categories=[], url='/api/account/', detailHtml='', area_select_array='',
    newAccount=function(){
        var req={category: parseInt($('#modal-new select[name="category"]').find("option:selected").attr("id"))};
        $.each($('#modal-new input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
        req["active_area"]=parseInt($('select[name="save_active_name"]').find("option:selected").attr("id"));
        if(req.username=='')global.showTip('请输入社交账号名');
        else if(req.fullname=='')global.showTip('请输入社交账号姓名');
        // else if(req.email=='')global.showTip('请输入邮件地址');
        else if(req.pwd=='')global.showTip('请输入初始密码');
        else $.ajax({
            url: global.getAPI(url),
            contentType: "application/json",
            method: 'post',
            data: JSON.stringify(req),
            success: function(data){
                global.showTip({word: '社交账号添加成功', danger: false});
                dataTable.ajax.reload();
                $('#modal-new input').val(''),
                $('#modal-new').modal('hide')
            }
        });
    },
    modifyAccount=function(item){
        $('#detail').removeClass('none').html(detailHtml),
        $('#info .box-title').text(item.name+'基本信息'),
        $.each(item, function(propName, value){$('#info input[name="'+propName+'"]').val(value)});
        // $.each(item, function(propName, value){$('#info p.'+propName).text(value)});
        $('#info input[name="category"]').val(item.category.name).attr("id",item.category.category);
        var are_id=item.active_area;
        var el0=$('select[name="edit_active_name"]');
        $.each(area_select_array,function (i,item) {
            if(i==are_id){
                el0.append('<option id="'+item.id+'" value="'+item.name+'" selected>'+item.name+'</option>');
            }else {
                el0.append('<option id="'+item.id+'" value="'+item.name+'">'+item.name+'</option>');
            }
        });
        $('#info .save').on('click',function(){
            var req={};
            // Object.assign(req, item);
            $.each($('#detail input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
            req["category"]=parseInt($('#info input[name="category"]').attr("id"));
            req["owner"] = item.owner.id;
            req["active_area"]=parseInt($('select[name="edit_active_name"]').find("option:selected").attr("id"));
            if(req.fullname=='')global.showTip('请输入社交账号姓名');
            else $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'put',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: '社交账号信息更新成功', danger: false}),
                    dataTable.ajax.reload()
                },
                error: function(){global.showTip('社交账号信息更新失败，请稍后再试')}
            });
        })
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: 'ID',
                    data: 'id'
                },
                {
                    title: '区域',
                    data: 'area_name'
                },
                {
                    title: '类型',
                    data: 'category.name'
                },
                {
                    title: '账号',
                    data: 'account'
                },
                {
                    title: '可执行任务',
                    data: 'enable_tasks'
                },
                {
                    title: '状态',
                    data: 'status'
                },
                {
                    title: '所有者',
                    data: 'owner.fullname',
                    visible: global.user.category.isAdmin
                }
            ],
            onSingleRowClick: function(item){
                if(item)modifyAccount(item);
                else $('#detail').html('')
            },
            onButtonClick: function(button, table, item, id){
                if(button.hasClass('modify'))modifyAccount(item);
                else if(button.hasClass('delete'))
                    global.dialog.deleteWarning('是否删除社交账号？', function(){
                        $.ajax({
                            url: global.getAPI(url+id+'/'),
                            contentType: "application/json",
                            method: 'delete',
                            success: function(data){
                                global.showTip({word: '社交账号删除成功', danger: false});
                                dataTable.ajax.reload(),
                                $('#detail').html('')
                            }
                        });
                    });
            }
        });
        $('#modal-new .ok').on('click', newAccount);
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
                    el.append('<option id="'+item.category+'" value="'+item.name+'">'+item.name+'</option>')
                })
            }
        }),
        // 导出
        $('button.export').on('click', function(){
            window.open(global.getAPI(url+'?export=true'))
        }),
        // 批量导入
        $('#modal-import button.ok').on('click', function(){
            var file_data = $('#modal-import input').prop('files')[0];
            if(file_data == undefined)return;
            var form_data = new FormData();
            form_data.append('file', file_data);
            $.ajax({
                type: 'POST',
                url: global.getAPI(url+'?import=true'),
                contentType: false,
                processData: false,
                data: form_data,
                success:function(response) {
                    global.showTip({word: '社交账号批量成功', danger: false}),
                    dataTable.ajax.reload()
                }
            });
        });
        $.ajax({
            url: global.getAPI('/api/area/'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                area_select_array = data.data;
                var el0=$('select[name="save_active_name"]');
                $.each(area_select_array, function(i, item){
                    el0.append('<option id="'+item.id+'" value="'+item.name+'">'+item.name+'</option>');
                })
            }
        })
});