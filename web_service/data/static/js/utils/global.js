define(['vue'], function(Vue) {

    // 兼容 Vue 初始化清理工作
    $('#tip').removeClass('hide');

        // 用户信息
    var user = JSON.parse(localStorage.getItem('authUser')),
        contentHeader = new Vue({
          el: '.content-header',
          data: {module: {}}
        }),
        // 设置模块信息
        initModule=function(module){
            contentHeader.module = module;
            // 设置当前侧栏菜单状态
            var parent=$('.sidebar-menu');
            $.each(module.path, function(i, item){
                var li=parent.children('li[data-module="'+item+'"]');
                if(li.length==0)li=parent.children('ul').children('ul>li[data-module="'+item+'"]');
                if(li.length==0)return;
                li.addClass('active');
                if(li.hasClass('treeview'))li.addClass('menu-open');
                parent=li;
            })
        },
        // 显示提示信息
        tip= new Vue({
             el: '#tip',
             data: {
                hide: true,
                title: '提示！',
                word: ''
             },
             methods: {
                showTip (word, title) {
                  clearTimeout(this.$options.timer);
                  if(title)this.title=title;
                  this.word = word,
                  this.hide = false,
                  setTimeout(this.hideTip, 3000)
                },
                hideTip(){
                  this.hide = true
                }
             }
         });
    new Vue({
      el: '.user',
      data: user
    });
    new Vue({
      el: '.user-panel',
      data: user
    });

    return {
        user: user,
        initModule: initModule,
        showTip: tip.showTip
    }
});