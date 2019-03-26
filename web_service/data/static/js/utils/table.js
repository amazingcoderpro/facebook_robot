define(['utils/global'], function(global) {

    var getItemById=function(dataList, id){
            for(var i=0;i<dataList.length;i++)
                if(dataList[i].id==id)
                    return dataList[i];
            return null;
        },
        initTable=function(pattern, config){
            var dataList=[], table,
                singleRowButtons=$(pattern+'Buttons button.single-row'),
                multipleRowButtons=$(pattern + 'Buttons button.multiple-row'),
                selectAllButton=$(pattern +'Buttons button.select-all');
            if(typeof config === 'undefined')config={};
            config.showRowNumber = true;
            if('ajax' in config){
                config.serverSide = true
                var ajax = config.ajax;
                ajax.contentType = 'application/json'
                ajax.type = 'GET'
                ajax.data = function (d) {return 'query=' + JSON.stringify(d)}
                ajax.dataSrc = function(json){
                    dataList=json.data;
                    table.dataList=dataList;
                    if (typeof(config.onDataSuccess) !== 'undefined')
                        config.onDataSuccess(dataList, json);
                    $.each(dataList, function(i,item){item.DT_RowId=item.id, item.DT_Index=i});
                    return dataList;
                }
            }else if('data' in config);
            if (!('language' in config))
                config.language = {'url': '//cdn.datatables.net/plug-ins/1.10.19/i18n/Chinese.json'};
            table=$(pattern).DataTable(config),
                switchMultiSelection=function(){
                    var multi=$(this).prop('checked');
                    table.multipleRowSelection=multi;
                    if(multi){
                        singleRowButtons.addClass('none'),
                        multipleRowButtons.removeClass('none'),
                        selectAllButton.removeClass('none')
                    }else{
                        singleRowButtons.removeClass('none'),
                        multipleRowButtons.addClass('none'),
                        selectAllButton.addClass('none')
                    }

                },
                afterMultiSelected=function(){
                    if(table.rows('.selected').data().length>=2)multipleRowButtons.addClass('btn-primary').prop('disabled', false);
                    else multipleRowButtons.removeClass('btn-primary').prop('disabled', true)
                };
            $(pattern + ' tbody').on( 'click', 'tr', function () {
                if(table.multipleRowSelection){
                    $(this).toggleClass('selected'),
                    afterMultiSelected()
                }else{
                    var buttons=$(pattern + 'Buttons button.single-row');
                    if ($(this).hasClass('selected')){
                        $(this).removeClass('selected');
                        singleRowButtons.removeClass('btn-primary').prop('disabled', true);
                    }else {
                        table.$('tr.selected').removeClass('selected');
                        var id=table.row(this).id();
                        if(typeof id !== 'undefined'){
                            $(this).addClass('selected');
                            singleRowButtons.addClass('btn-primary').prop('disabled', false);
                            if('undefined' !== typeof config.onDataSelected){
                                var item=getItemById(dataList, id);
                                if(item)config.onDataSelected(item, id, table);
                            }
                        }
                    }
                    if('undefined' !== typeof config.onSingleRowClick){
                        if(table.row('.selected').length==0)config.onSingleRowClick(null);
                        else config.onSingleRowClick(getItemById(dataList, table.row('.selected').id()));
                    }
                }
            }),
            singleRowButtons.prop('disabled', true).on('click', function(){
                if(table.row('.selected').length==0)return;
                var id=table.row('.selected').id(),item=getItemById(dataList, id);
                if(!item)return;
                if('undefined' !== typeof config.onButtonClick)config.onButtonClick($(this), table, item, id);
            }),
            multipleRowButtons.prop('disabled', true).on('click', function(){
                var data=table.rows('.selected').data();
                if(data.length<2)return;
                if('undefined' !== typeof config.onMultipleButtonClick)config.onMultipleButtonClick($(this), table, data);
            }),
            $(pattern + 'Buttons input.multiple-row-selection').on('click', switchMultiSelection),
            selectAllButton.on('click',function(){
                table.rows('').every(function (rowIdx, tableLoop, rowLoop ){$(this.node()).toggleClass('selected')}),
                afterMultiSelected()
            }),
            switchMultiSelection();
            return table
        };

    return {
        initTable: initTable
    }
});