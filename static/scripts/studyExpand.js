$(document).ready(function(){
    var expansion = {};
    var table = $("#studyTable").DataTable({
    "drawCallback": function ( settings ) {
                    var api = this.api();
                    var rows = api.rows( {page:'current'} ).nodes();
                    var last=null;
        
                    api.column(0, {page:'current'} ).data().each( function ( group, i ) {
                        var expand_rows = "";
                        study_details = expansion[$(rows).eq(i).attr("id")]
                        console.log(study_details);
                        if (!_.isEmpty(study_details)){
                            for (key in study_details){
                                linktag="<a style='color:#888888; text-decoration:none;' href='/viewset/"+study_details[key].id+":"+key+"'>"
                                expand_rows += "<tr class='group'><td>"+linktag+"preview</a></td>";
                                expand_rows += "<td>" + linktag + key + "</a></td>";
                                var date = study_details[key].timestamp;
                                expand_rows+= "<td>"+date+"</td></tr>"
                            }

                            $(rows).eq( i ).after(
                            '<tr class="group">'+
                                    '<th>Preview</th>'+
                                    '<th>DICOM name</th>'+
                                    '<th>Date Uploaded</th></tr>'+
                                    expand_rows
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
        else {
            $(this).html("&#8854;");
        }
        
        $.get(url, $.proxy(function( data, textStatus ) {
             if (textStatus === 'success') {
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
