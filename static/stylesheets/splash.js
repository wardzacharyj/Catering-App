document.addEventListener("DOMContentLoaded", function(event) {

    var banner = document.getElementById("login-banner");
    var name_field = document.getElementById("input_name");
    var btn_sign_up = document.getElementById("btn_signup");
    var btn_sign_in = document.getElementById("btn_login");

    var switch_config = document.getElementById("switch-config");

    var pos = 0;

    switch_config.addEventListener("change", function(){
        if(pos == 0){
            btn_sign_in.classList.add("hidden");
            name_field.classList.remove("hidden");
            btn_sign_up.classList.remove("hidden");
            banner.textContent = "Sign Up";
            pos = 1;
        }
        else {
            btn_sign_in.classList.remove("hidden");
            name_field.classList.add("hidden");
            btn_sign_up.classList.add("hidden");
            banner.textContent = "Login";

            pos = 0;
        }

    });

});