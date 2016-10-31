$(document).ready(function(){
    var filename = document.getElementById("filename");
    var submit = document.getElementById("upsubmit");

    function validateFilename(){
        if(filename.value.replace(/\W+/g, "") == '') {
            filename.setCustomValidity("Must enter a file name");
        } else {
            filename.setCustomValidity('');
        }
    }

    filename.onkeyup = validateFilename;
    submit.onkeyup = validateFilename;
})
