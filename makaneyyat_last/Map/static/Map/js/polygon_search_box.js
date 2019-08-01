var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
var selected_feature = null;
var filter_overlay_layer = new ol.Overlay({
	element:container,
	autoPan: true,
	autoPanAnimation: {
		duration: 250
	}
})
var id_counter=0;

map.on('singleclick', function (evt){
	var coordinate = evt.coordinate;

	let pixel = evt.pixel;

    map.forEachFeatureAtPixel(pixel, async function(feature, layer) {
        console.log(feature.getGeometry().getCoordinates())
        let geometry = 0;
        if(feature.getGeometry().getCoordinates().length > 20){
            geometry = feature.getGeometry().simplify(10)
        }else{
            geometry = feature.getGeometry()
        }

        var d = new Date(feature.getProperties()['date'])
        // selected_feature = feature
        if(geometry.getType()=="Polygon"){

            if(feature.getId()==undefined){
                feature.setId(id_counter);
                id_counter++;
            }
            selected_feature = feature
            filter_overlay_layer.setPosition(coordinate);


            // removeAllPoints(feature)

            map.addOverlay(filter_overlay_layer)
            let filters = await getFilters(geometry)
            if(Object.keys(filters.families).length>0){
                $('.no-data-result').hide()
                $('.search-box').show()
                 // console.log(container)
            }else{
                $('.no-data-result').show()
                $('.search-box').hide()
            }
            getSearchForm(d.getFullYear(),filters,feature.getProperties())
            document.getElementById('search-box-filter').addEventListener('click',getSearchQuery)
            document.getElementById('clear-points').addEventListener('click',clear_points);
            document.getElementById('clear-points').setAttribute('value',feature.getId());
            $('div#loader').hide();
        }
    })
})




closer.onclick = function() {
    filter_overlay_layer.setPosition(undefined);
    closer.blur();
    return false;
};


function getSearchForm(year,filters,properties){
    if(properties['level1']){
        $('#popup-content .search-box #level1-title').text('Level1: ')
        $('#popup-content .search-box #level1').text(properties['level1'])
    }
    if(properties['level2']){
        $('#popup-content .search-box #level2-title').text('Level2: ')
        $('#popup-content .search-box #level2').text(properties['level2'])
    }
    if(properties['level3']){
        $('#popup-content .search-box #level3-title').text('Level3: ')
        $('#popup-content .search-box #level3').text(properties['level3'])
    }
    if(properties['level4']){
        $('#popup-content .search-box #level4-title').text('Level4: ')
        $('#popup-content .search-box #level4').text(properties['level4'])
    }

    var familes_box = document.getElementById("checkboxes")
    familes_box.innerHTML=""
    var select_all_families = document.createElement('input')
    var br = document.createElement('br')
    select_all_families.setAttribute('type','checkbox')
    select_all_families.setAttribute('name','family')
    select_all_families.setAttribute('value','all_families')
    select_all_families.addEventListener('click',showCheckboxes)
    var all_name = document.createTextNode('All Families')
    familes_box.appendChild(select_all_families)
    familes_box.appendChild(all_name)
    familes_box.appendChild(br)
    for (var family in filters.families){
        var selected_family = document.createElement('input')
        var br = document.createElement('br')
        selected_family.setAttribute('type','checkbox')
        selected_family.setAttribute('name','family')
        selected_family.setAttribute('value',filters.families[family][0])
        var family_name = document.createTextNode(family + ' ' + filters.families[family][1])
        familes_box.appendChild(selected_family)
        familes_box.appendChild(family_name)
        familes_box.appendChild(br)
    }

    var year_search1 = document.getElementById("year-search1")
    year_search1.innerHTML = '';
    year_search1.innerHTML = year;
    var years_box = document.getElementById("checkboxes-years")
    years_box.innerHTML=""
    var select_all_years = document.createElement('input')
    var br = document.createElement('br')
    select_all_years.setAttribute('type','checkbox')
    select_all_years.setAttribute('name','year')
    select_all_years.setAttribute('value','all_years')
    select_all_years.addEventListener('click',showCheckboxesYears)
    var all_name = document.createTextNode('All Years')
    years_box.appendChild(select_all_years)
    years_box.appendChild(all_name)
    years_box.appendChild(br)
    for (var year in filters.years){
        var selected_year = document.createElement('input')
        var br = document.createElement('br')
        selected_year.setAttribute('type','checkbox')
        selected_year.setAttribute('name','year')
        selected_year.setAttribute('value',year)
        var year_name = document.createTextNode(year + ' ' + filters.years[year])
        years_box.appendChild(selected_year)
        years_box.appendChild(year_name)
        years_box.appendChild(br)
    }

}


function getPolygon(polygon){
    let gemotry =''
    gemotry = "POLYGON((";
    for (let index = 0; index < polygon.length - 1; index++) {
        let point = ol.proj.transform(polygon[index], "EPSG:3857", "EPSG:4326")
        // let point = polygon[index]
        gemotry += point[0] + ' ' + point[1] + ','
    }

    let lastPoint = ol.proj.transform(polygon[0], "EPSG:3857", "EPSG:4326")
    // let lastPoint = polygon[0]
    gemotry += lastPoint[0] + ' ' + lastPoint[1] + "))"
    return gemotry
}

async function getFilters(geometry){
    let url = "https://api.gbif.org/v1/occurrence/search?geometry=" + getPolygon(geometry.getCoordinates()[0]) + "&hasCoordinate=true&limit=1000&facet=familyKey&facet=year&familyKey.facetLimit=9999&year.facetLimit=9999"

    let filters = {
        'families':{},
        'years':{}
    };
    await axios.get(url)
            .then(async function (response) {
                    await response.data.results.forEach(function (ele) {
                    if(!filters.families[ele.family]){
                        filters.families[ele.family]=[ele.familyKey,getFacet(response.data.facets[1].counts,ele.familyKey)];
                    }
                    if(!filters.years[ele.year]){
                        filters.years[ele.year]=getFacet(response.data.facets[0].counts,ele.year);
                    }
                })
            })
            .catch(function (error) {
                console.log(error)
            });
    return filters;
}

function getFacet(counts,key){
    for(var index =0;index<counts.length;index++){
        if(counts[index].name==key){
            return counts[index].count
        }
    }
}



function getSearchQuery(){
    var selected_filters = [];
    var selected_years = [];
    if(!$('input[value=all_families]:checked').length==1){
        $('input[name=family]:checked').each(function(){
            selected_filters.push($(this).val())
        })
    }
    if(!$('input[value=all_years]:checked').length==1){
         $('input[name=year]:checked').each(function(){
            selected_years.push($(this).val())
        })
    }


    axios.get(prepareQuery(selected_feature,selected_filters,selected_years))
            .then(function (response) {
                console.log(response.data.results)
                load_points(response.data.results,selected_feature)
                load_gpif_filter_data(response.data.results);
            })
            .catch(function (error) {
                console.log(error)
            });
    filter_overlay_layer.setPosition(undefined);
}


function prepareQuery(selected_feature,selected_filter,selected_years){
    var url = "https://api.gbif.org/v1/occurrence/search?geometry=" + getPolygon(selected_feature.getGeometry().getCoordinates()[0]) + "&hasCoordinate=true&limit=1000"
    if(gbif_polygon_query_urls.indexOf(url)==-1){
        gbif_polygon_query_urls.push(url);
    }
    for (filter in selected_filter){
        var familyKey = "&familyKey="+selected_filter[filter]
        url+=familyKey
    }
    for (year in selected_years){
        var year_field = "&year="+selected_years[year]
        url+=year_field
    }
    return url
}


function load_points(result,selected_feature){
    var id_selected = selected_feature
    if(selected_feature!='search'){
        id_selected = selected_feature.getId()
    }
    if(layers['search_filter_'+id_selected]){
         layers['search_filter_'+id_selected].getSource().forEachFeature(function(ele){
              remove_gbif_data(ele.getId())
         })
    }

    map.removeLayer(layers['search_filter_'+ id_selected])
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
        feature.setId(coords['key'])
        searchResult.addFeature(feature);

    })
    layers['search_filter_'+ id_selected] = new ol.layer.Vector({
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

    map.addLayer(layers['search_filter_'+ id_selected]);

}

function clear_points(){
    layers['search_filter_'+this.value].getSource().forEachFeature(function(ele){
        remove_gbif_data(ele.getId())
    })
    map.removeLayer(layers['search_filter_'+this.value])
    filter_overlay_layer.setPosition(undefined);
}



var expanded = false;

function showCheckboxes() {
  var checkboxes = document.getElementById("checkboxes");
  if (!expanded) {
    checkboxes.style.display = "block";
    expanded = true;
  } else {
    checkboxes.style.display = "none";
    expanded = false;
  }
}

var expanded_year = false;
function showCheckboxesYears() {
  var checkboxes_years = document.getElementById("checkboxes-years");
  if (!expanded_year) {
    checkboxes_years.style.display = "block";
    expanded_year = true;
  } else {
    checkboxes_years.style.display = "none";
    expanded_year = false;
  }
}


function remove_gbif_data(id){
    var elements = $('#gpif tbody tr')
    for(var index=0;index < elements.length;index++){
       if(parseInt(elements[index].cells[0].innerText)==id){
           $(elements[index]).remove();
       }
    }
}


function load_gpif_filter_data(data) {
    // gpif_table.tBodies[0].innerHTML = '';
    data.forEach(function (element){
        add_gbif_row(element);
    })
}


