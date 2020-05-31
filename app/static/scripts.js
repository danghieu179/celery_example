function createRectangle() {
    var width = document.getElementById('width');
    var height = document.getElementById('height');
    var error_width = document.getElementById('error_width');
    var error_height = document.getElementById('error_height');
    var error_rectangle = document.getElementById('error_rectangle');
    error_width.innerHTML = "";
    error_height.innerHTML = "";
    if (width.value === "" && height.value === "") {
        error_width.innerHTML = "This field is requeired";
        error_height.innerHTML = "This field is requeired";
        return;
    }
    if (width.value === "") {
        return error_width.innerHTML = "This field is requeired";
    }
    if (height.value === "") {
        return error_height.innerHTML = "This field is requeired";
    }
    var body = {
        'width': width.value,
        'height': height.value
    }
    axios.post('/createrectangle', body)
        .then(function (response) {
            rectangle_id.innerHTML = response.data.rectangle_id
            error_rectangle.innerHTML = response.data.error_rectangle
        })
        .catch(function (error) {
            console.log(error);
        });
}
function computeRectangle() {
    var rectangle = document.getElementById('rectangle');
    var area = document.getElementById('area');
    var perimeter = document.getElementById('perimeter');
    var result_width = document.getElementById('result_width');
    var result_height = document.getElementById('result_height');
    var error = document.getElementById('error');
    if (rectangle.value === "") {
        error.innerHTML = "This field is requeired";
        return;
    }
    var body = {
        'rectangle_id': rectangle.value,
    }
    axios.post('/computerectangle', body)
        .then(function (response) {
            area.innerHTML = response.data.area
            perimeter.innerHTML = response.data.perimeter
            result_width.innerHTML = response.data.width
            result_height.innerHTML = response.data.height
            error.innerHTML = response.data.error
        })
        .catch(function (error) {
            console.log(error);
        });
}

function getRectangle() {
    var rectangle = document.getElementById('rectangle');
    var area = document.getElementById('area');
    var perimeter = document.getElementById('perimeter');
    var result_width = document.getElementById('result_width');
    var result_height = document.getElementById('result_height');
    var error = document.getElementById('error');
    if (rectangle.value === "") {
        error.innerHTML = "This field is requeired";
        return;
    }
    var body = {
        'rectangle_id': rectangle.value,
    }
    axios.get('/computerectangle', {params: body})
        .then(function (response) {
            area.innerHTML = response.data.area
            perimeter.innerHTML = response.data.perimeter
            result_width.innerHTML = response.data.width
            result_height.innerHTML = response.data.height
            error.innerHTML = response.data.error
        })
        .catch(function (error) {
            console.log(error);
        });
}
function onlyNumber(e) {
    let keyCode = (e.keyCode ? e.keyCode : e.which);
    // only allow number
    if ((keyCode < 48 || keyCode > 57)) {
        e.preventDefault();
    }
}

function onPasteOnlyNumber(e) {
    let isnum = /^\d+$/.test(e.clipboardData.getData("Text"));
    // only allow number
    if (!isnum) {
        e.preventDefault();
    }
}