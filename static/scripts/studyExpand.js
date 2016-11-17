$(document).ready(function(){
    var expansion = {};
    
    var table = $("#studyTable").DataTable({
        "drawCallback": function ( settings ) {
            var api = this.api();
            var rows = api.rows( {page:'current'} ).nodes();
            var last=null;

            api.column(0, {page:'current'} ).data().each( function ( group, i ) {
                var expand_rows = "";
                var id = $(rows).eq(i).attr("id")
                var study_details = expansion[id];
                if (!_.isEmpty(study_details)){
                    for (key in study_details){
                        linktag="<a style='color:#888888; text-decoration:none;' href='/viewset/"+study_details[key].id+":"+key+"'>"
                        expand_rows += "<tr class='group'><td>"+linktag+"preview</a></td>";
                        expand_rows += "<td>" + linktag + key + "</a></td>";
                        var date = study_details[key].timestamp;
                        expand_rows += "<td>"+date+"</td>"
                        expand_rows += "<td id='"+key+"'><button id='eraseIcon'><img style='width:20px; height:20px;' src='/static/BinIcon.png'></button></td></tr>"
                    }
                    var className = $(rows).eq(i).attr("class");
                    var element = $('<tr class="expanded ' + 
                                    className + '">' +
                                    '<td colspan="5" style="padding:0;"><div><table width="100%" cellspacing="1" rules="cols">' +
                                    '<tr><th width="33%">Preview</th>' +
                                    '<th width="33%">DICOM name</th>' +
                                    '<th width="33%">Date Uploaded</th>' +
                                    '<th width="20%"></th></tr>'+
                                    expand_rows +
                                    '</table></div></td></tr>');
                    $(rows).eq(i).after(element);
                    $("#eraseIcon", element).click(function(event) {
                        var keyName = $(this).parent().attr("id")
                        alert(keyName);
                        alert(study_details[keyName].id);
                        
                    });
                }
            });
            
                     
        }
    });
       
        
    // on click expand or collapse the table row
    $(".LoadStudyDicoms").on("click", function(event) {
        event.preventDefault();
        var url = $(this).attr("href");
        var id = $(this).parents("tr").attr("id");
        if ($(this).html() == "⊖"){
            $(this).html("&#8853;");
            expansion[id] = undefined;
            table.draw();
            return     
        }
        else {
            $(this).html("&#8854;");
        }
        
        $.get(url, function(data) {
            expansion[id] = data;
            table.draw();
        }).fail(function() {
             expansion[id] = "table error";
             table.draw();
        });
    })
})
