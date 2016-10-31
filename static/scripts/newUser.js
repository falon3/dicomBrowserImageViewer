
$(document).ready(function(){
    $('#logout').hide();
    var password = document.getElementById("password")
    , confirm_password = document.getElementById("confirm_password");

    function validatePassword(){
        if(password.value != confirm_password.value) {
            confirm_password.setCustomValidity("Passwords Don't Match");
        } else {
            confirm_password.setCustomValidity('');
        }
    }

    confirm_password.onkeyup = validatePassword;
    password.onkeyup = validatePassword;
    submit.onkeyup = validatePassword;
})
