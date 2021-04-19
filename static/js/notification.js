$(document).ready(function() {
    $('#notification').DataTable({
        "dom": '<"top">t<"bottom"ip><"clear">',
        "ordering": false,
    });
} );

// function close(close_id){
//     console.log(close_id);
//     console.log(id.split("_")[1]);
//     // model_id = 'model'+id;
//     // var model = document.getElementById(model_id);
//     // model.style.display = 'none';
// }

function clickEvent(id){
    model_id = 'model'+id;
    var model = document.getElementById(model_id);
    model.style.display = 'block';
}

function closeEvent(id){
    model_id = 'model'+id.split("_")[1];
    var model = document.getElementById(model_id);
    model.style.display = 'none';
}
