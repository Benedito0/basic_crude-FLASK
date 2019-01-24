function additem() {

    var item_name = document.getElementById("item_name").value;
    var item_category = document.getElementById("item_category").value;
    var item_descripton = document.getElementById("item_descripton").value;
    alert(item_descripton);

    if(item_name == "" && item_category == -1 && item_descripton == "") // the "choose a category" option has a value of -1
    {
        alert("YOu must fill all the fields!");
    }
    else
    {
          $.post("/add/item",
          {
            item_name: item_name,
            item_category: item_category,
            item_descripton: item_descripton
          },
          function(data, status){
            //alert("Data: " + data + "\nStatus: " + status);
          });

    }




  }