$(document).ready(function(){
    $('#loading').hide();
});

$('#publication-form-wrapper').on('click', '#add_author', (function( event ) {
    event.preventDefault();
    cloneMore($('tr.author:last'));
}));

$('#publication-form-wrapper').on('click', '.author-delete', function( event ) {
    event.preventDefault();
    var total = $('#id_form-TOTAL_FORMS').val();
    if(total > 1) {
        var form = $(event.target).closest('.author');
        $('#id_form-TOTAL_FORMS').val(total-1);
        $(form).remove();
    }
    else {
        alert('Publications must have at least 1 author.');
    }
});

$( "#publication-form-wrapper" ).on( "tabscreate", '#tabs', function( event, ui ) {
    $('#tabs .active').removeClass('active');
    $(ui.tab).addClass('active');
    $('#pub_type').val($(ui.tab).text());
});

$( "#publication-form-wrapper" ).on( "tabsactivate", '#tabs', function( event, ui ) {
        $(ui.oldTab).removeClass('active');
        $(ui.newTab).addClass('active');
        $('#pub_type').val($(ui.newTab).text());
});

function doisearch(showform) {
    $('#loading').show();
    var doi = $("#doi-field").val();
    if (showform === true) {
        doi = ''
    }
    $.ajax({
        url: '/finddoi',
        method: 'GET',
        data: {'doi': doi},
        success: function(result){
            $('#loading').hide();
            $("#publication-form-wrapper").html(result);
            setUpForm();
            $.each($('#id_model li label'), function(index, element) {
                newelem = $('<input/>');
                $(newelem).attr('id', 'ensemble_'+index);
                $(newelem).attr('name', 'ensemble');
                $(element).after(newelem);
            });
            if (showform === true) {
                $('.alert.alert-warning').hide();
            }
        },
        error: function(jqxhr, status, error){
            $('#loading').hide();
            alert("Ajax Failed");
        }
    });
}


function submitPublication() {
    var ensemble = []
    var active = $( "#tabs" ).tabs( "option", "active" );
    $.each($("#id_model input[name='ensemble']"), function(index, element){
        ensemble[index] = $(element).val()
    });
    $.ajax({
        type: 'POST',
        url: '/new',
        data: $('form').serialize(),
        success: function(result){
            window.location.replace("/review");
        },
    }).fail(function($xhr) {
        $("#publication-form-wrapper").html($xhr.responseText);
        setUpForm(active);
        $.each($('#id_model li label'), function(index, element) {
            newelem = $('<input/>');
            $(newelem).attr('id', 'ensemble_'+index);
            $(newelem).attr('name', 'ensemble');
            $(newelem).val(ensemble[index]);
            $(element).after(newelem);
        });
        window.scrollTo(0, 0);
    });
}

function setUpForm(active = 0) {
    $( "#tabs" ).tabs({ active: active });
    var count = parseInt($('#id_form-TOTAL_FORMS').val());
    for(i=0; i < count; i++) {
        $('#id_form-' + i + '-DELETE').closest('td').remove();
    }
}
