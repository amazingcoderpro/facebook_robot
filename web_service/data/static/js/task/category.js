require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: '任务类型管理',
        sub: '新增、配置任务类型',
        path: ['task', 'category']
    });
    var categories=[], url='/api/taskCategories/', detailHtml='',
    getParam=function(div, source){
        var req={};
        if(source)Object.assign(req, source);
        $.each($(div + ' input'), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()});
        if(req.name=='')global.showTip('请输入任务类型名称');
        else if(req.processor=='')global.showTip('请输入任务函数');
        else return req;
        return null;
    },
    newItem=function(){
        var req=getParam('#modal-new');
        if(!req)return;
        $.ajax({
            url: global.getAPI(url),
            contentType: "application/json",
            method: 'post',
            data: JSON.stringify(req),
            success: function(data){
                global.showTip({word: '任务类型添加成功', danger: false});
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
            var req=getParam('#detail', item);
            if(!req)return;
            $.ajax({
                url: global.getAPI(url+item.id+'/'),
                contentType: "application/json",
                method: 'put',
                data: JSON.stringify(req),
                success: function(data){
                    global.showTip({word: '任务类型信息更新成功', danger: false}),
                    dataTable.ajax.reload()
                },
                error: function(){global.showTip('任务类型信息更新失败，请稍后再试')}
            });
        })
    },
    dataTable=table.initTable('#dataTable', {
            ajax: {url: global.getAPI(url)},
            columns: [
                {
                    title: '类型名称',
                    data: 'name'
                },
                {
                    title: '任务函数',
                    data: 'processor'
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
                    global.dialog.deleteWarning('是否删除任务类型？', function(){
                        $.ajax({
                            url: global.getAPI(url+id+'/'),
                            contentType: "application/json",
                            method: 'delete',
                            success: function(data){
                                global.showTip({word: '任务类型删除成功', danger: false});
                                dataTable.ajax.reload(),
                                $('#detail').html('')
                            }
                        });
                    });
            }
        });
        $('#modal-new .ok').on('click', newItem)
        detailHtml=$('#detail').html(),
        $('#detail').html('')
})