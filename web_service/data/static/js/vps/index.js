require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: 'Agent 管理',
        sub: '新增、管理 Agent',
        path: ['vps', 'agent']
    });
    var categories=[], url='/api/agent/', detailHtml='',
    newAccount=function(){
        var req={};
        $.each(['input', 'select'], function(k, el){$.each($('#modal-new '+el), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()})});
        $.ajax({
            url: global.getAPI(url),
            contentType: "application/json",
            method: 'post',
            data: JSON.stringify(req),
            success: function(data){
                global.showTip({word: 'Agent 添加成功', danger: false});
                dataTable.ajax.reload();
                $('#modal-new input').val(''),
                $('#modal-new').modal('hide')
            }
        });
    },
    modifyItem=function(item){
        $('#detail').removeClass('none').html(detailHtml),
        $('#info .box-title').text(item.queue_name+'的基本信息'),
        $.each(item, function(propName, value){$('#info input[name="'+propName+'"]').val(value),$('#info select[name="'+propName+'"]').val(value)});
        $('#info .save').on('click',function(){
            var req={};
            Object.assign(req, item);
            $.each(['input', 'select'], function(k, el){$.each($('#detail '+el), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()})});
            $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'put',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: 'Agent 信息更新成功', danger: false}),
                    dataTable.ajax.reload()
                },
                error: function(){global.showTip('Agent 信息更新失败，请稍后再试')}
            });
        })
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: '列队名',
                    data: 'queue_name'
                },
                {
                    title: '状态',
                    data: 'status',
                    render: function(data){
                        switch(data){
                            case '0': return 'idle';
                            case '1': return 'normal';
                            case '2': return 'busy';
                            default:
                                return 'disable'
                        }
                    }
                },
                {
                    title: '所在地',
                    data: 'area'
                }
            ],
            onSingleRowClick: function(item){
                if(item)modifyItem(item);
                else $('#detail').html('')
            },
            onButtonClick: function(button, table, item, id){
                if(button.hasClass('modify'))modifyItem(item);
                else if(button.hasClass('delete'))
                    global.dialog.deleteWarning('是否删除 Agent？', function(){
                        $.ajax({
                            url: global.getAPI(url+id+'/'),
                            contentType: "application/json",
                            method: 'delete',
                            success: function(data){
                                global.showTip({word: 'Agent 删除成功', danger: false});
                                dataTable.ajax.reload(),
                                $('#detail').html('')
                            }
                        });
                    });
            }
        });
        $('#modal-new .ok').on('click', newAccount),
        $.ajax({
            url: global.getAPI('/api/area/'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                categories = data.data;
                var el=$('select[name="area"]');
                $.each(categories, function(i, item){
                    el.append('<option value="'+item.name+'">'+item.name+'</option>')
                }),
                detailHtml=$('#detail').html(),
                $('#detail').html('')
            }
        })
})