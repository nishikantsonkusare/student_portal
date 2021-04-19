function validationForm(){
    var mob = document.getElementById('mob');
    var npass = document.getElementById('npass');
    var cnfpass = document.getElementById('cnfpass');
    var file = document.getElementById("img").files[0];
    var testmob = /^\d{10}$/;


    if (!mob.value.match(testmob)){
        document.getElementById('mob_error').innerHTML = "Please entered valid mobile number."
        return false;
    }
    if(npass.value != ''){
        if(npass.value.length <= 3){
            
            document.getElementById('npass_error').innerHTML = 'Password must be greater than 3 character.'
            return false;
        }
        if(npass.value.length >=20){
            document.getElementById('npass_error').innerHTML = 'Password must be smaller than 20 character.'
            return false;
        }
        if(npass.value != cnfpass.value){
            document.getElementById('cnf_error').innerHTML = 'Confirm password must be same to new password.'
            return false;
        }
    }
    if(file != ""){

        if (file.size >= 5242880){
            document.getElementById('img_error').innerHTML = 'File must be less than 5MB.'
            return false;
        }
    }
    return true;
}