define(['utils/global'], function(global) {

    var schedulerMode = ['立即执行（只执行一次）',
                '间隔执行',
                '间隔执行，立即开始',
                '定时执行，指定时间执行'],
    // 显示调度类型
    displayScheduler=function(mode){
        return schedulerMode[mode]
    },
    displayStatus=function(name){
        return {
            ''
        }[name]
    };

    return {
        schedulerMode: schedulerMode,
        displayScheduler: displayScheduler
    }
});