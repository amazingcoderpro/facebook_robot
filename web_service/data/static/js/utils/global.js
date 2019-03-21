define(['vue'], function(Vue) {
        // 用户信息
    var user = JSON.parse(localStorage.getItem('authUser')),
        contentHeader = new Vue({
          el: '.content-header',
          data: {module: {}}
        }),
        mainSidebar = new Vue({
          el: '.main-sidebar',
          data: {
            user: user,
            module: {}
          }
        }),
        // 设置模块信息
        initModule=function(module){
            mainSidebar.module = contentHeader.module = module
        };
    new Vue({
      el: '.user',
      data: user
    });

    return {
        user: user,
        initModule: initModule
    }
});