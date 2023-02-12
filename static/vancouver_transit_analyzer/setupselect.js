function update_fields() {
    const urlParams = new URLSearchParams(window.location.search);

    var disp_data = urlParams.get("disp_data");
    var disp_time = urlParams.get("disp_times");
    var start_date_val = urlParams.get("start_date");
    var end_date_val = urlParams.get("end_date");

    if (start_date_val) {
        document.getElementById('start_date').value = start_date_val;
    }
    if (end_date_val) {
        document.getElementById('end_date').value = start_date_val;
    }
    if (disp_data) {
        if (disp_data == "All") {
            document.getElementById('all').checked = true;
            document.getElementById('between').checked = false;
        } else if (disp_data == "Between") {
            document.getElementById('all').checked = false;
            document.getElementById('between').checked = true;
        }
    }
    if (disp_time) {
        if (disp_time == "All") {
            document.getElementById('allhours').checked = true;
            document.getElementById('peak').checked = false;
        } else if (disp_time == "Peak") {
            document.getElementById('allhours').checked = false;
            document.getElementById('peak').checked = true;
        }
    }

}
function radio_update() {
    if (document.getElementById('all').checked) {
        document.getElementById('date_div').style.visibility = "hidden";
    } else {
        document.getElementById('date_div').style.visibility = "visible";
    }

    document.getElementById('start_date').max = new Date().toISOString().split("T")[0];
    document.getElementById('end_date').value = new Date().toISOString().split("T")[0];
    document.getElementById('end_date').max = new Date().toISOString().split("T")[0];
}

update_fields();
radio_update();



