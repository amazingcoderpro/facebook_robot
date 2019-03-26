define(['utils/global'], function(global) {

    var getValue=function(data, path){
        path=path.split('.'),$.each(path, function(i,item){data=data[item]});
        return data;
    },
    initCheckbox=function(pattern, data, path){
        $(pattern).prop('checked', getValue(data, path));
    },
    boolFromCheckbox=function(pattern, data, path){

    },
    _onFormChange=function(){$($(this).data('change-pattern')).addClass('btn-primary')},
    highLightButton=function(pattern){
        if(typeof(pattern)==='undefined')pattern='button.save';
        $('input').on('change',_onFormChange).data('change-pattern', pattern),
        $('textarea').on('change',_onFormChange).data('change-pattern', pattern),
        $('select').on('change',_onFormChange).data('change-pattern', pattern),
        $('input[type="checkbox"]').on('click', _onFormChange).data('change-pattern', pattern),
        $('input[type="radio"]').on('click', _onFormChange).data('change-pattern', pattern);
    }


    return {
        initCheckbox: initCheckbox,
        highLightButton: highLightButton,
        onFormChange: _onFormChange
    }
});