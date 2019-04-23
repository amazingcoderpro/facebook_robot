require(['vue', 'utils/global', 'utils/table', 'utils/form'], function(Vue, global, table, form){
    global.initModule({
        title: 'Agent 管理',
        sub: '新增、管理 Agent',
        path: ['vps', 'agent']
    });
    var categories=[], url='/api/agent/', detailHtml='',
    newAccount=function(){
        var req={};
        $.each(['input', 'select','textarea'],
            function(k, el){
                $.each($('#modal-new '+el),
                    function(i, item){
                        item=$(item);
                        // req[item.attr('name')]=item.val().trim()
                          req[item.attr('name')]=item.val().trim()
                    })
        });
        req["status"]=parseInt(req["status"]);
        req["configure"]=req["save_configure"];
        req["active_area"]=parseInt($('select[name="save_area"]').find("option:selected").attr("id"));
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
        $('#info .box-title').text(item.active_area+'基本信息'),
        $.each(item, function(propName, value){$('#info input[name="'+propName+'"]').val(value),$('#info select[name="'+propName+'"]').val(value)});
        $('select[name="edit_area"] option').each(function () {
            if($(this).val() == item.area_name) {
                $(this).attr("selected","selected");
            }
        });
        $("textarea[name='edit_configure']").val(item.configure);
        $('#info .save').on('click',function(){
            var req={};
            Object.assign(req, item);
            $.each(['input', 'select'], function(k, el){$.each($('#detail '+el), function(i, item){item=$(item),req[item.attr('name')]=item.val().trim()})});
            req.active_area=parseInt($('select[name="edit_area"]').find("option:selected").attr("id"));
            req.status=parseInt(req.status);
            req.configure=$("textarea[name='edit_configure']").val();
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
    };
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
                var el=$('select[name="save_area"]');
                var edit_area=$('select[name="edit_area"]');
                $.each(categories, function(i, item){
                    el.append('<option id="'+item.id+'" value="'+item.name+'">'+item.name+'</option>');
                    edit_area.append('<option id="'+item.id+'" value="'+item.name+'">'+item.name+'</option>');
                }),
                detailHtml=$('#detail').html(),
                $('#detail').html('')
            }
        })
});