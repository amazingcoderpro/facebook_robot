
require([], function(){
  localStorage.setItem('authUser', null);
  var username=localStorage.getItem("authUsername"), showTip=function(msg){
     $('.callout').removeClass('hide').find('p').text(msg)
  };
  if(username){
    $('input[type="email"]').val(username),
    $('input[type="checkbox').prop('checked', true)
  }
    $('input').iCheck({
      checkboxClass: 'icheckbox_square-blue',
      radioClass: 'iradio_square-blue',
      increaseArea: '20%' /* optional */
    });


    function on_login(){

        var param = {
            username: $('input[type="email"]').val().trim(),
            password: $('input[type="password"]').val().trim()
        };
        if(param.username==='')showTip('请输入用户名');
        else if (param.password==='')showTip('请输入用户密码');
        else $.post({
            type: "POST",
            url: '/api/user/auth',
            data: JSON.stringify(param),
            success: function(req){
              if($('input[type="checkbox').prop('checked')){
                 localStorage.setItem("authUsername", param.username);
              }
              localStorage.setItem('authUser', JSON.stringify(req)),
              window.location.assign('/console/dashboard')
            },

            dataType: 'json'
        }).fail(function(req){
                alert('用户名或密码错误！')
        })
    }


    document.onkeydown=function(event){
        var code = event.keyCode;
        if(code ==13){
            on_login()
        }
    }

    $('button[type="button"]').on('click', function(){
        on_login()
     });
});

