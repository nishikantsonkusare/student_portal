function show_model(id){
    model_id = 'model'+id;
    var model = document.getElementById(model_id);
    
    model.style.display = 'block';
}

function closeEvent(id){
    model_id = 'model'+id.split("_")[1];
    var model = document.getElementById(model_id);
    model.style.display = 'none';
}
