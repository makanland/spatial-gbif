var info_table = document.getElementById('info-table');
var makaneyya_info_widget = document.getElementById('makaneyya-info');
var ele_info_panel = document.getElementById('element-info');
var full_display = true;
var search_history = []

var base_text_style = {
  font: '12px Calibri,sans-serif',
  textAlign: 'center',
  offsetY: -15,
  fill: new ol.style.Fill({
    color: [0,0,0,1]
  }),
  stroke: new ol.style.Stroke({
    color: [255,255,255,0.5],
    width: 4
  })
};


init();

function init() {
    init_map();
    load_table_schema(info_table);
    load_table_gpif_schema(gpif_table);
    load_makanyya();
    init_feature_overlay();
}

async function load_makanyya() {
    let map_elements = {
        'point_element_size':0,
        'polygon_element_size':0,
        'multi_polygon_element_size':0,
        'line_element_size':0,
        'multi_line_element_size':0,
    }
     await axios.get(get_makaneya_api_url(),{ headers: { Authorization: api_key } })
        .then(function (response) {
            let makaneyya = response.data;
            map_elements = {
                'point_element_size':makaneyya.point_elements.count,
                'line_element_size':makaneyya.line_elements.count,
                'polygon_element_size':makaneyya.polygon_elements.count,
                'multi_line_element_size':makaneyya.multi_line_elements.count,
                'multi_polygon_element_size':makaneyya.multi_polygon_elements.count
            }

            search_history.push(get_makaneya_api_url())
            // load_default_table(makaneyya);
            load_pages_nav(makaneyya,1)
            setCount(makaneyya);

            if (makaneyya.gbifQuery.length > 0) {
                getGbifSearch(makaneyya.gbifQuery, "text");
            }

            if (makaneyya.gbifQueryByArea.length > 0) {
                getGbifSearch(makaneyya.gbifQuery, "text");
                let geometries = makaneyya.gbifQueryByArea.split(';');
                load_polygon_area_search(parseGeometries(geometries));
                geometries.forEach(function (gemo) {
                    getGbifSearch("https://api.gbif.org/v1/occurrence/search?geometry=" + gemo + "&hasCoordinate=true&limit=1000", "area");
                })
            }
        })
        .catch(function (error) {
            console.log(error)
        });



    axios.get(get_all_elements_url(map_elements),{ headers: { Authorization: api_key } })
        .then(function (response) {
            let makaneyya = response.data;
            search_history.push(get_makaneya_api_url())
            load_makanyya_layer(makaneyya);
            add_makaneyya_info(makaneyya);
        })
        .catch(function (error) {
            console.log(error)
        });
}

function get_all_elements_url(map_elements){
    let url = get_makaneya_api_url()+'/?'
    Object.keys(map_elements).forEach(function (key) {
        if (map_elements[key]>0){
            url+=key+'='+map_elements[key]+'&'
        }
    })
    return url
}

// function that reload the overlay of the map
function init_feature_overlay_create(options = {}){
  layers["overlay"] = new ol.layer.Vector({
    map: map,
    source: new ol.source.Vector({
      features: new ol.Collection(),
      useSpatialIndex: false // optional, might improve performance
    }),
    style: overlay_style_function,
    updateWhileAnimating: true, // optional, for instant visual feedback
    updateWhileInteracting: true // optional, for instant visual feedback
  });
}

//style function that bind a style to feature basing on its type
function overlay_style_function(feature){
  let style;
  let geom = feature.getGeometry();
  if (geom.getType() == 'Point') {
    let text = feature.get('text');
    base_text_style.text = text;
    // this is inefficient as it could create new style objects for the
    // same text.
    // A good exercise to see if you understand would be to add caching
    // of this text style

    style = new ol.style.Style({
      text: new ol.style.Text(base_text_style),
      zIndex: 2
    });
  }else{
    style =  highlight_styles[geom.getType()];
  }
  return [style];
}

function get_makaneya_api_url() {
    let parsedURL = document.URL.split("/");
    let id = parsedURL[parsedURL.length - 1];
    return encodeURI(base_api_url + 'makaneyyat/' + id);
};


//load Makaneyya layer into the map
function load_makanyya_layer(makaneyya) {
    let makaneyyat = new ol.source.Vector({
        format: new ol.format.GeoJSON({featureProjection: 'EPSG:3857'}),
        features: new ol.Collection(),
    });

    let center = ol.proj.transform([makaneyya.lat,makaneyya.lon], "EPSG:4326", "EPSG:3857");
    // console.log()
    // let center = [makaneyya.lon, makaneyya.lat];
    map.getView().setCenter(center);
    let geo_element_types = ['point_elements', 'elements', 'line_elements', 'polygon_elements', 'multi_polygon_elements'];
    for (let i in geo_element_types) {
        let type = geo_element_types[i];
        if(makaneyya[type]['count'] > 0){
            let makaneyyats =null;
            if(type=='elements'){
                makaneyyats = makaneyya[type]['results']
            }else{
                makaneyyats = makaneyya[type]['results']['features']
            }
            makaneyyats.forEach(function (elementURL) {
                let element = elementURL;
                //console.log(element)

                let feature  = null
                if(type != 'elements') {
                    feature = makaneyyat.getFormat().readFeature(element);
                }

                if (makaneyya.isGBIFMakanyyea && (type == 'polygon_elements' || type == 'multi_polygon_elements')) {
                    get_polygon_gbif_data(feature);
                }
                if(feature){
                    makaneyyat.addFeature(feature);
                }
        });
        }

    }

    // layers["overlay"].setSource(makaneyyat);

    layers["makaneyyat"] = new ol.layer.Vector({
        source: makaneyyat,
        style: style_function,
    });

    map.addLayer(layers["makaneyyat"]);
}

// // to load default elements into table
// function load_default_table(makaneyya){
//
//     let geo_element_types = ['point_elements', 'elements', 'line_elements', 'polygon_elements', 'multi_polygon_elements'];
//     for (let i in geo_element_types) {
//         let type = geo_element_types[i];
//         if(makaneyya[type]['count'] > 0){
//             let makaneyyats =null;
//             if(type=='elements'){
//                 makaneyyats = makaneyya[type]['results']
//             }else{
//                 makaneyyats = makaneyya[type]['results']['features']
//             }
//             makaneyyats.forEach(function (elementURL) {
//                 let element = elementURL;
//
//                 if(type != 'elements'){
//                     load_tableload_table([element['properties']], false);
//                 }else{
//                     load_table([element], false);
//                 }
//         });
//         }
//
//     }
// }

//get the points inside the polygons
function get_polygon_gbif_data(feature) {
    //convert the coordinates to be accepted in gbif api format
    feature.getGeometry().transform('EPSG:3857', 'EPSG:4326');
    let polygon = feature.getGeometry().getCoordinates()[0];

    let gemo = "POLYGON((";
    for (let index = 0; index < polygon.length - 1; index++) {
        let point = polygon[index]
        gemo += point[0] + ' ' + point[1] + ','
    }
    let lastPoint = polygon[0]
    gemo += lastPoint[0] + ' ' + lastPoint[1] + "))"
    feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
    getGbifSearch("https://api.gbif.org/v1/occurrence/search?geometry=" + gemo + "&hasCoordinate=true&limit=1000", "area");
}


//function that append the proprties of a dataelement of the makaneyya into the table
function add_makaneyya_info(makaneyya) {

    let info = {
        "title": makaneyya['title'],
        "description": makaneyya['description'],
        "author": makaneyya['author'],
        "date": makaneyya['date'],
        '#elements': makaneyya['elements'].length + makaneyya['point_elements'].length + makaneyya['line_elements'].length +
            makaneyya['polygon_elements'].length + makaneyya['multi_polygon_elements'].length,
    };

    for (let key in info) {
        let row = document.createElement('span');
        row.classList.add('makaneyya-info-row');
        row.innerHTML = '<strong>' + key.toUpperCase() + ':</strong> ' + info[key];
        makaneyya_info_widget.appendChild(row);
        makaneyya_info_widget.innerHTML += '<br><br>';

    }
    if (makaneyya['tags']) makaneyya_info_widget.innerHTML += "<br><h3>Tags</h3>";
    for (let i = 0; tag = makaneyya['tags'][i++];) {
        let tag_ele = document.createElement('span');
        tag_ele.classList.add('makaneyya-tag');
        tag_ele.innerHTML = '#' + tag;
        makaneyya_info_widget.appendChild(tag_ele);
        if (i != 0 && i % 2 == 0) makaneyya_info_widget.innerHTML += '<br>';
    }

}

function setCount(makaneyya) {
    document.getElementById("counter").innerText = get_makaneyya_count(makaneyya)
}

function get_makaneyya_count(makaneyya){
    return makaneyya.elements.count + makaneyya.point_elements.count + makaneyya.line_elements.count + makaneyya.multi_line_elements.count +
                makaneyya.polygon_elements.count + makaneyya.multi_polygon_elements.count
}

// to get the saved query in makaneyyat
function getGbifSearch(url, searchType) {
    var urls = url.split("||")
    if(urls.length>1){
        for (url in urls){
            axios.get(urls[url],{ headers: { Authorization: api_key } })
            .then(function (response) {
                let result = response.data;
                // load_pages_nav(result.results, page_number);
                load_search_layer(result.results, searchType);
                load_gpif_data(result.results);
            })
            .catch(function (error) {
                console.log(error)
            });
        }
    } else if (url.length > 0) {
        axios.get(url,{ headers: { Authorization: api_key } })
            .then(function (response) {
                let result = response.data;
                // load_pages_nav(result.results, page_number);
                load_search_layer(result.results, searchType);
                load_gpif_data(result.results);
            })
            .catch(function (error) {
                console.log(error)
            });
    }
}


// to draw the search area
function parseGeometries(geometries) {
    let polygons = [];
    geometries.forEach(function (gemo) {
        let coordinates = [];
        gemo = gemo.slice(9, gemo.length - 2);
        gemo.split(',').forEach(function (coord) {
            let subArray = [];
            subArray[0] = parseFloat(coord.split(' ')[0]);
            subArray[1] = parseFloat(coord.split(' ')[1]);
            coordinates.push(subArray);
        })
        polygons.push(coordinates);
    })
    return polygons;
}

function load_polygon_area_search(polygons) {
    let areaSearch = new ol.source.Vector({
        format: new ol.format.GeoJSON({featureProjection: 'EPSG:3857'}),
        features: new ol.Collection(),
    });
    polygons.forEach(function (polygon) {

        let feature = new ol.Feature({
            geometry: new ol.geom.Polygon([polygon])
        });

        feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
        areaSearch.addFeature(feature);
        // layers["overlay"].getSource().addFeature(feature);
    })


    layers["areaSearch"] = new ol.layer.Vector({
        source: areaSearch,
        style: style_function,
    });

    map.addLayer(layers["areaSearch"]);
}



//function that load to UI the nav for page selection
function load_pages_nav(makaneyya, current_page){
    let total_count = {
        'data_element_page':makaneyya.elements.count,
        'point_element_page':makaneyya.point_elements.count,
        'line_element_page':makaneyya.line_elements.count,
        'polygon_element_page':makaneyya.polygon_elements.count,
        'multi_line_element_page':makaneyya.multi_line_elements.count,
        'multi_polygon_element_page':makaneyya.multi_polygon_elements.count
    }

	let page_size = 100;
	html = "<nav aria-label='Page navigation'>" +
    	"<ul class='pagination'>";
	let nav  = document.createElement("nav")
    nav.setAttribute('aria-label','Page navigation')
    let ul = document.createElement("ul")
    ul.setAttribute('class','pagination')

	let counter = 1
	Object.keys(total_count).forEach(function (key){

	     for(let i = 1; i <= Math.ceil(total_count[key] / page_size); i++){
	         get_default_page(key)
	          // to load default table
	         let li = document.createElement("li")
             li.setAttribute('class','page-item')
             if (counter==current_page) li.classList.add('active')
             li.addEventListener('click',function(){
                get_page(this,key,i)
             })
             let span = document.createElement('span')
             span.setAttribute('class','page-link')
             let text = document.createTextNode(counter)
             span.append(text)
             li.append(span)
             ul.append(li)
            counter++;
        }
    })
    nav.append(ul)


    document.getElementById('page-nav').innerHTML = ''
    document.getElementById('page-nav').append(nav)
}

var get_default_page = (function() {
    var executed = false;
    return function(key,counter) {
        if (!executed) {
            executed = true;
            get_page(1,key,1)
        }
    };
})();


//function that chang the search page
function get_page(target,querey_search,i){
    let counter = 0;
	let url = search_history[search_history.length -1]
    var re = new RegExp(querey_search+'=[0-9]+',"g");
    url = url.replace(re,querey_search+'='+i)
    if(!url.match(re)){
        if(url.match(/\?/g)){
            counter++;
            url = url + '&' + querey_search +'='+i;
        }else{
            counter++;
            url = url + '/?' + querey_search +'='+i;
        }
    }
	// if(search_history.length==1)

	axios.get(url,{ headers: { Authorization: api_key } }).then(function(response) {
        let makaneyyat = response.data
        search_history.push(url);
        let geo_element_types = {
            'data_element_page':'elements',
            'point_element_page':'point_elements',
            'line_element_page':'line_elements',
            'polygon_element_page':'polygon_elements',
            'multi_line_element_page':'multi_line_elements',
            'multi_polygon_element_page':'multi_polygon_elements'
        };

        if(querey_search != 'data_element_page'){
             load_elements_table(makaneyyat[geo_element_types[querey_search]]['results']['features'],is_data_element=false);
        }else{
            load_elements_table(makaneyyat[geo_element_types[querey_search]]['results'],is_data_element=true);
        }
        if(target!=1){
            load_pages_nav(makaneyyat, parseInt(target.children[0].innerText))
        }
    }).catch(function(error){
        console.log(error);
    });

}

//function the initiate table loading
function load_elements_table(elements,is_data_element){

	load_table([], true, true);
	elements.forEach(function (element){
	    load_table([element], false, is_data_element);
    })
}

//
// //function that load to UI the nav for page selection
// function load_pages_nav(page, current_page){
//
//
//
//
// 	let page_size = 100;
// 	html = "<nav aria-label='Page navigation'>" +
//     	"<ul class='pagination'>";
// 	for(let i = 1; i <= Math.ceil(page.count / page_size); i++){
// 		html += '<li class="page-item' + (i == current_page?' active':'') + '" onclick="change_page(this,' + i +  ')" >'
// 		+ '<span class="page-link">' + i + '</span></li>';
// 	}
//     html += '</ul></nav>';
//
//     document.getElementById('page-nav').innerHTML = html;
// }
//
// function setCount(count){
// 	document.getElementById('counter').innerText = count
// }
//
// //function that chang the search page
// function change_page(target, page_number){
// 	let url = search_history[search_history.length -1]
// 	url = url.replace(/page=[0-9]+/,'page='+ page_number)
// 	axios.get(url,{ headers: { Authorization: api_key } }).then(function(response) {
// 			search_history.push(url);
// 			final_page = response.data;
// 			page = response.data;
// 			load_pages_nav(final_page, page_number);
// 			// load_elements(final_page.results);
// 			load_elements_table(final_page.results);
//
// 			setCount(final_page.count);
// 	    }).catch(function(error){
// 			console.log(error);
// 	  	});
//
// }

