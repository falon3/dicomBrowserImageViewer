$(document).ready(function(){

    $(".LoadStudyDicoms").on("click", function() {
        alert("clicked!")
        event.preventDefault();
        var url = $(this).attr("href");
        var hiddenRows = $(".hiddenRows");
        
        $.ajax({
            url: url,
            type : 'get',
            complete : function( qXHR, textStatus ) {
                // attach error case

                if (textStatus === 'success') {
                    var data = qXHR.responseText
                    hiddenRows.hide();
                    //hiddenRows.append(data);
                    //hiddenRows.fadeIn();
                }
            }
        });
    }

    filename.onkeyup = validateFilename;
    submit.onkeyup = validateFilename;
})
