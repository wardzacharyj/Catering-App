document.addEventListener("DOMContentLoaded", function(event) {



    var btn_owner_staff = document.getElementById('btn_owner_staff');
    var btn_owner_events = document.getElementById('btn_owner_events');

    var owner_staff_entry = document.getElementById('owner_staff_entry');
    var owner_staff_list = document.getElementById('owner_staff_list');

    var owner_events_no_staff = document.getElementById('owner_events_no_staff');
    var owner_events_with_staff = document.getElementById('owner_events_with_staff');

    var ownerState = 0;
    btn_owner_staff.addEventListener("click",function(){

        if(ownerState == 1){
            ownerState = 0;

            console.log('Hide Events and Show Staff');

            owner_events_no_staff.classList.add('hidden');
            owner_events_with_staff.classList.add('hidden');

            owner_staff_entry.classList.remove('hidden');
            owner_staff_list.classList.remove('hidden');

        }
    });

    btn_owner_events.addEventListener("click",function(){

        if(ownerState == 0){
            ownerState = 1;

            console.log('Hide Staff and Show Events');

            owner_staff_entry.classList.add('hidden');
            owner_staff_list.classList.add('hidden');

            owner_events_no_staff.classList.remove("hidden");
            owner_events_with_staff.classList.remove("hidden");


        }
    });



    // ================================================================================




    var staff_events_owned = document.getElementById('');
    var staff_events_disowned = document.getElementById('');

    var customer_event_entry = document.getElementById('customer_event_entry')
    var customer_events = document.getElementById('');

});
