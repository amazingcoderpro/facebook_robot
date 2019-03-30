define(['utils/global'], function(global) {

    var schedulerMode = ['立即执行（只执行一次）',
                '间隔执行',
                '间隔执行，立即开始',
                '定时执行，指定时间执行'],
    // 显示调度类型
    displayScheduler=function(mode){
        return schedulerMode[mode]
    },
    // 显示任务名称
    displayStatus=function(name){
        return {
            pending: '等待执行',
            failed: '失败',
            succeed: '成功',
            running: '运行',
            pausing: '暂停',
            'new': '新新，还没处理'
        }[name]
    };

    return {
        schedulerMode: schedulerMode,
        displayScheduler: displayScheduler
    }
});