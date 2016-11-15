$(document).ready(function(){
    var expansion = {};
    var table = $("#studyTable").DataTable({
    "drawCallback": function ( settings ) {
                    var api = this.api();
                    var rows = api.rows( {page:'current'} ).nodes();
                    var last=null;
        
                    api.column(0, {page:'current'} ).data().each( function ( group, i ) {
                        if (expansion[$(rows).eq(i).attr("id")]){
                            $(rows).eq( i ).after(
                            '<tr class="group"><td colspan="4">'+expansion[$(rows).eq(i).attr("id")]+'</td></tr>'
                            );
                        }
                    });
    }
    });
                
    // on click expand or collapse the table row
    $(".LoadStudyDicoms").on("click", function(event) {
        event.preventDefault();
        var url = $(this).attr("href");
        if ($(this).html() == "⊖"){
            $(this).html("&#8853;");
            expansion[$(this).parents("tr").attr("id")] = undefined;
            table.draw();
            return     
        }
        else{
            $(this).html("&#8854;");
        }
        
        $.get(url, $.proxy(function( data, textStatus ) {
            console.log(textStatus);

            if (textStatus === 'success') {
                console.log(data);
                expansion[$(this).parents("tr").attr("id")] = data;
                table.draw();
            }
            
        },this)
             ).fail($.proxy(function() {
                 expansion[$(this).parents("tr").attr("id")] = "table error";
                 table.draw();
        },this));
    })
})
