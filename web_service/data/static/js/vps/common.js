define(['utils/global'], function(global) {

    var
    // 显示任务名称
    displayStatus=function(status){
        if(status==-1)return 'disable';
        if(status==0)return 'idle';
        if(status < 10)return 'normal';
        return 'busy'
    },
    // 通过状态聚合
    groupByStatus=function(agents, array){
        var result={};
        $.each(agents, function(i, item){
            var status=displayStatus(item.status);
            if(status in result){
                result[status]['count']+=1,
                result[status]['items'].push(item)
            }else result[status] = {
                'count': 1,
                'items': [item]
            }
        });
        if(!array)return result;
        var arrayResult={'status': [], 'count': [], 'items': []};
        $.each(result, function(i, item){arrayResult['status'].push(i),arrayResult['count'].push(item['count']),
            arrayResult['items'].push(item['items'])});
        return arrayResult
    };

    return {
        displayStatus: displayStatus,
        groupByStatus: groupByStatus
    }
});