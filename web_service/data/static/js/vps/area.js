require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: 'VPS 所在地管理',
        sub: '新增、管理 VPS 位置',
        path: ['vps', 'area']
    });
    var categories=[], url='/api/area/', detailHtml='',
    newItem=function(){
        var req={};
        $.each($('#modal-new input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
        if(req.name=='')global.showTip('请输入区域名称');
        else $.ajax({
            url: global.getAPI(url),
            contentType: "application/json",
            method: 'post',
            data: JSON.stringify(req),
            success: function(data){
                global.showTip({word: 'VPS 所在地添加成功', danger: false});
                dataTable.ajax.reload();
                $('#modal-new input').val(''),
                $('#modal-new').modal('hide')
            }
        });
    },
    modifyItem=function(item){
        $('#detail').removeClass('none').html(detailHtml),
        $('#info .box-title').text(item.name+'的基本信息'),
        $.each(item, function(propName, value){$('#info input[name="'+propName+'"]').val(value)});
        $('#info .save').on('click',function(){
            var req={};
            Object.assign(req, item);
            $.each($('#detail input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
            if(req.fullname=='')global.showTip('请输入 VPS 所在地 姓名');
            else if(req.email=='')global.showTip('请输入邮件地址');
            else $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'put',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: 'VPS 所在地 信息更新成功', danger: false}),
                    dataTable.ajax.reload()
                },
                error: function(){global.showTip('VPS 所在地 信息更新失败，请稍后再试')}
            });
        })
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: '所在地名称',
                    data: 'name'
                },
                {
                    title: '描述',
                    data: 'description'
                }
            ],
            onSingleRowClick: function(item){
                if(item)modifyItem(item);
                else $('#detail').html('')
            },
            onButtonClick: function(button, table, item, id){
                if(button.hasClass('modify'))modifyItem(item);
                else if(button.hasClass('delete'))
                    global.dialog.deleteWarning('是否删除 VPS 所在地？', function(){
                        $.ajax({
                            url: global.getAPI(url+id+'/'),
                            contentType: "application/json",
                            method: 'delete',
                            success: function(data){
                                global.showTip({word: 'VPS 所在地删除成功', danger: false});
                                dataTable.ajax.reload(),
                                $('#detail').html('')
                            }
                        });
                    });
            }
        });
        $('#modal-new .ok').on('click', newItem)
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