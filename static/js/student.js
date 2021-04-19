window.onload = function(){
    var btn = document.getElementById('mybtn')
    var model = document.getElementById('model');
    var close = document.getElementById('close');
    var close1 = document.getElementById('close1');

    btn.onclick = function(){
        model.style.display = 'block';
    }

    close.onclick = function(){
        model.style.display = 'none';
    }

    close1.onclick = function(){
        model.style.display = 'none';
    }
}

$(document).ready(function() {
    $('#student').DataTable({
        "dom": '<"top">t<"bottom"ip><"clear">',
        "ordering": false,
    });
} );
