// var info_table = document.getElementById('info-table');
// var ele_info_panel = document.getElementById('element-info');
// var full_display = true;
var draw;
var searchEnable = true;
var firstTime = true;
var gemotry = "";
let areaQueries = [];


// to prevent javascript from crash when makaneyya view call the script
if(document.getElementById("search")){
    document.getElementById("search").addEventListener('keyup', autocomplete)
    document.getElementById("search-btn").addEventListener('click', gbifSearch)
    document.getElementById("search-by-area-btn").addEventListener('click', enableSearchByArea)
}


// auto complete code
//fetch scientific names for autocomplete
function autocomplete() {
    let element = document.getElementById("search");
    if (element.value != "") {
        axios.get("https://api.gbif.org/v1/species/suggest?q=" + element.value)
            .then(function (response) {
                let result = response.data;
                let list = [];
                result.forEach(function (res) {
                    list.push(res.scientificName);
                })
                generateAutoCompList(list);
            })
            .catch(function (error) {
                console.log(error)
            });
    }
}

//display autocomplete list
function generateAutoCompList(names) {

    let autocmp = document.getElementsByClassName("autocomplete")[0]
    window.addEventListener('click', () => {
        autocmp.style.display = "none"
    })
    autocmp.style.display = "block";
    while (autocmp.firstChild) {
        autocmp.removeChild(autocmp.firstChild);
    }
    names.forEach((name) => {
        let li = document.createElement("li");
        li.addEventListener('click', (event) => {
            event.preventDefault()
            getName(li);
        })
        let text = document.createTextNode(name);
        li.appendChild(text);
        autocmp.appendChild(li);
    })
}

// set the selected name in the search box
function getName(element) {
    document.getElementById("search").value = element.innerHTML;
    document.getElementsByClassName("autocomplete")[0].style.display = "none";
}


function gbifSearch() {
    let searchType;
    let name = document.getElementById("search").value;

    if (name != "") {
        loadSearch(getGbifQuery(),searchType='text')
    }
}


function searchByArea() {
    let searchType;
    if (this.getFeatures()[this.getFeatures().length-1]) {
        let polygon = this.getFeatures()[this.getFeatures().length-1].getGeometry().getCoordinates()[0];
        gemotry = "POLYGON((";
        for (let index = 0; index < polygon.length - 1; index++) {
            let point = ol.proj.transform(polygon[index], "EPSG:3857", "EPSG:4326")
            gemotry += point[0] + ' ' + point[1] + ','
        }
        let lastPoint = ol.proj.transform(polygon[0], "EPSG:3857", "EPSG:4326")
        gemotry += lastPoint[0] + ' ' + lastPoint[1] + "))"
        // loadSearch(getGbifQueryByArea(gemotry),searchType='area');
    }
}

function getGbifQuery(){
    let query = document.getElementById("query-num").value;
    if (query == "") {
        query = 50;
    }
    let country = document.getElementById("country").value
    let name = document.getElementById("search").value;
    let url = "";
    if (name != ''){
        url = "https://api.gbif.org/v1/occurrence/search?scientificName=" + name + "&country=" + country + "&hasCoordinate=true&limit=" + query;
    }
    if (country == "" && name != '') {
        url = "https://api.gbif.org/v1/occurrence/search?scientificName=" + name + "&hasCoordinate=true&limit=" + query;
    }
    return url;
}

function getGbifQueryByArea(gemotry){
    areaQueries.push(gemotry);
    return "https://api.gbif.org/v1/occurrence/search?geometry=" + gemotry + "&hasCoordinate=true&limit=1000";
}


// search for the gbif by using two type of search
// search by text
// search by area
function loadSearch(url,searchType){
     axios.get(url)
            .then(function (response) {
                let result = response.data;
                // load_search_layer(result.results,searchType);
                // load_gpif_filter_data(result.results);
                load_points(result.results,'search')
                load_gpif_filter_data(result.results)
            })
            .catch(function (error) {
                console.log(error)
            });
}

// add search layer result to the map
function load_search_layer(result,searchType) {

    map.removeLayer(layers["searchResult"])
    let searchResult = new ol.source.Vector({
        format: new ol.format.GeoJSON({featureProjection: 'EPSG:4326'}),
        features: new ol.Collection(),
    });

    searchResult.clear();
    let points = []
    result.forEach(function (coords) {
        let feature = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.transform([coords.decimalLongitude, coords.decimalLatitude], "EPSG:4326", "EPSG:3857")),
            text:coords['acceptedScientificName']
        });
        searchResult.addFeature(feature);
    })

    if(searchType=="area"){
        layers["searchAreaResult"] = new ol.layer.Vector({
            source: searchResult,
            style: new ol.style.Style({
                image: new ol.style.Circle({
                  radius: 6,
                  stroke: new ol.style.Stroke({
                    color: 'lightgray',
                    width: 2
                  }),
                  fill: new ol.style.Fill({
                    color: 'red'
                  })
                })
              })
        });

        map.addLayer(layers["searchAreaResult"]);
    }else{
        layers["searchTextResult"] = new ol.layer.Vector({
            source: searchResult,
            style: style_function,
        });

        map.addLayer(layers["searchTextResult"]);
    }

}


// add gbif search result to the table
function load_gpif_data(data) {
    gpif_table.tBodies[0].innerHTML = '';
    data.forEach(function (element){
        add_gbif_row(element);
    })
}

// add each row to the table
function add_gbif_row(element){
    let tr = document.createElement('tr');
    let en_schema = ['basisOfRecord', 'scientificName', 'acceptedScientificName', 'stateProvince', 'year', 'month', 'day', 'country','datasetName','relation'];
    let ar_schema = ['basisOfRecord', 'scientificName', 'acceptedScientificName', 'stateProvince', 'year', 'month', 'day', 'country','datasetName','relation'];
    let schema = lang ? en_schema : ar_schema;
    let row = '<td>' + element.key + '</td>';
    // let row='';
    for (let i = 0; i < schema.length; i++) {
        if(schema[i]=='relation'){
            row += '<td>' + '<a href="https://www.gbif.org/species/'+ element['acceptedTaxonKey'] + '"> reference </a>' + '</td>';
        }else{
            row += '<td>' + element[schema[i]] + '</td>';
        }

    }
    tr.innerHTML = row;
    gpif_table.tBodies[0].appendChild(tr);
}

// toggle search button
function enableSearchByArea() {
    let searchByAreaBtn = document.getElementById("search-by-area-btn");
    // drawPolygon();
    if (searchEnable) {
        drawPolygon();
        // searchByAreaBtn.style.color = 'black';
        searchEnable = false;
    } else {
        // clearScreen();
        // searchByAreaBtn.style.color = 'white';
        searchEnable = true;
        map.removeInteraction(draw);
    }
}

function drawPolygon() {
    let vector = new ol.source.Vector({wrapX: false})
    draw = new ol.interaction.Draw({
        source: vector,
        type: "Polygon"
    });


    map.addInteraction(draw);
    layers["drawResult"] = new ol.layer.Vector({
        source: vector,
        style: style_function,
    });

    map.addLayer(layers["drawResult"]);
    vector.on('change', searchByArea);
    vector.on('change', function(){
        searchEnable = true;
        map.removeInteraction(draw);
    });
}

$(document).keyup(function(e){
     if(e.key === "Escape") {
        searchEnable = true;
        map.removeInteraction(draw);
    }
});











// convert geometries from list to string
function getGeometries(){
    return areaQueries.join(';');
}

// clear the result
function clearScreen() {
    layers["drawResult"].getSource().clear();
    map.removeLayer(layers["searchAreaResult"]);
    // layers["searchResult"].getSource().clear();

}








