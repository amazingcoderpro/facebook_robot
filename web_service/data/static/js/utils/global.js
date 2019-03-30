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
                calloutDanger: true,
                title: '提示！',
                word: ''
             },
             methods: {
                showTip (msg) {
                  clearTimeout(this.$options.timer);
                  if(typeof msg == 'string')msg = {word: msg};
                  if(msg.title)this.title=msg.title;
                  this.word = msg.word,
                  this.hide = false,
                  this.calloutDanger = typeof msg.danger == 'undefined' || msg.danger,
                  setTimeout(this.hideTip, 3000)
                },
                hideTip(){
                  this.hide = true
                }
             }
         }),
         // 拼接 API，增加 token
        getAPI = function(url){
            return url +(url.indexOf('?')==-1?'?':'&') + 'access-token='+ user.token
         },
        _warningDialog=function(title, word, func){
            if($('#warning-dialog').length==0){
                var html=[];
                html.push('<div class="modal modal-warning fade" id="warning-dialog">'),
                html.push('<div class="modal-dialog"><div class="modal-content"><div class="modal-header">'),
                html.push('<button type="button" class="close" data-dismiss="modal" aria-label="Close">'),
                html.push('<span aria-hidden="true">&times;</span></button>'),
                html.push('<h4 class="modal-title">'),
                html.push(title),
                html.push('</h4></div><div class="modal-body"><p></p></div>'),
                html.push('<div class="modal-footer">'),
                html.push('<button type="button" class="btn btn-outline pull-left confirm" data-dismiss="modal">确认</button>'),
                html.push('<button type="button" class="btn btn-outline" data-dismiss="modal">取消</button>'),
                html.push('</div></div></div></div>'),
                $('body').append(html.join(''));
            }
            var dialog=$('#warning-dialog');
            dialog.find('.modal-body p').text(word);
            dialog.find('.confirm').off('click').on('click', func);
            dialog.modal();

        },
        dialog={
            warning: _warningDialog,
            deleteWarning: function(word, func){_warningDialog('删除确认', word, func)}
        },
        // 显示详情
        showDetail=function(cfg){
             $(cfg.div).removeClass('none').html(cfg.html),
             $.each(cfg.data, function(propName, value){$(cfg.div+' input[name="'+propName+'"]').val(value)});
             $.each(cfg.data, function(propName, value){$(cfg.div+' select[name="'+propName+'"]').val(value)});
             var showP=function(dict, parent){
                $.each(dict, function(propName, value){
                    if(typeof value == 'object')showP(value, parent+propName+'__')
                    else {
                        var p=$('#info p.'+parent+propName), fn=p.data('display');
                        p.text(typeof fn!='undefined' && typeof cfg[fn] != 'undefined'?cfg[fn](value):value)
                    }
                });
             };
             showP(cfg.data, '')
        };
    new Vue({
      el: '.user',
      data: user
    });
    new Vue({
      el: '.user-panel',
      data: user
    });
    if(!user.category.isAdmin)$('ul.sidebar-menu li.admin').remove();
    $('a.logout').on('click', function(){
        $.ajax({
            url: getAPI('/api/user/logout'),
            contentType: "application/json",
            method: 'get',
            success: function(data){
                location.assign('/user/login')
            }
        })
    });

    return {
        user: user,
        initModule: initModule,
        showTip: tip.showTip,
        dialog: dialog,
        getAPI: getAPI,
        showDetail: showDetail
    }
});