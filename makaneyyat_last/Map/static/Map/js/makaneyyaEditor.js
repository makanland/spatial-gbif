var makaneyya_form = document.getElementById('makaneyya-form');
var facets_widget = document.getElementById('map-facets');
var info_table = document.getElementById('info-table');

var full_display = false;
var counter = 0
var search_history = []
let facet_counts = []
var gbif_polygon_query_urls = [];

if (makaneyya_form)
    makaneyya_form.onsubmit = createMakaneyya;

var layersTypes = {};
var csrftoken = getCookie('csrftoken');

//object that maintain the current selected page 
var page = {
    'results': {},
    'count': null,
    'previous': null,
    'next': null,
}

var selectedElements = {
    'results': {},
    'count': null,
    'previous': null,
    'next': null,
};
//makaneyya object
var makaneyya_obj = {
    "elements": [],
    "point_elements": [],
    "line_elements": [],
    "multi_line_elements": [],
    "polygon_elements": [],
    "multi_polygon_elements": [],
    "tags": [],
    "lon": null,
    "lat": null,
}

var categories = {
    "source": {},
    "subject": {},
    'level1': {},
    'level2': {},
    'level3': {},
    'level4': {},
    'year': {},
};

var categories_counter = {
    "source": 0,
    "subject": 0,
    'level1': 0,
    'level2': 0,
    'level3': 0,
    'level4': 0,
    'year': 0,
};

var map_center = ol.proj.transform([35.024549, 32.066549], 'EPSG:4326', 'EPSG:3857');
var map_zoom = 10;
var lang = true;

//used to reload the table with same elements but for different attribute
var table_data = []

var tile_sources = {
    OSM: new ol.source.OSM(),
    Stamen: new ol.source.Stamen({layer: 'terrain-background'}),
    Bing: new ol.source.BingMaps({
        key: ' AixJpONnZC80xs7_Q_076pCxhe2aOOQbdKOqxRorqYK2SnFp3fKKaMs3KAHMvsVN',
        imagerySet: 'Aerial',
    }),
};

var layers = {
    'tile': null,
    'overlay': null,
};

var display_text = 'title';

var styles = {
    'Point': new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            stroke: new ol.style.Stroke({
                color: 'white',
                width: 2
            }),
            fill: new ol.style.Fill({
                color: 'green'
            })
        })
    }),
    'Polygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'blue',
            width: 1
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 255, 0.1)'
        })
    }),
};

var highlight_styles = {
    MultiPolygon: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: [255, 0, 0, 0.6],
            width: 2
        }),
        fill: new ol.style.Fill({
            color: [255, 0, 0, 0.2]
        }),
        zIndex: 1,
        text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            fill: new ol.style.Fill({color: '#000'}),
            stroke: new ol.style.Stroke({
                color: '#fff', width: 2
            }),
        }),
    }),
};

var highlight_styles = {
    'Polygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: [255, 0, 0, 0.6],
            width: 2
        }),
        fill: new ol.style.Fill({
            color: [255, 0, 0, 0.2]
        }),
        zIndex: 1,
        text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            fill: new ol.style.Fill({color: '#000'}),
            stroke: new ol.style.Stroke({
                color: '#fff', width: 2
            }),
        }),
    }),
    'MultiPolygon': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: [255, 0, 0, 0.6],
            width: 2
        }),
        fill: new ol.style.Fill({
            color: [255, 0, 0, 0.2]
        }),
        zIndex: 1,
        text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            fill: new ol.style.Fill({color: '#000'}),
            stroke: new ol.style.Stroke({
                color: '#fff', width: 2
            }),
        }),
    }),
    'LineString': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: [255, 0, 0, 0.6],
            width: 2
        }),
        fill: new ol.style.Fill({
            color: [255, 0, 0, 0.2]
        }),
        zIndex: 1,
        text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            fill: new ol.style.Fill({color: '#000'}),
            stroke: new ol.style.Stroke({
                color: '#fff', width: 2
            }),
        }),
    }),
    'MultiLineString': new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: [255, 0, 0, 0.6],
            width: 2
        }),
        fill: new ol.style.Fill({
            color: [255, 0, 0, 0.2]
        }),
        zIndex: 1,
        text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            fill: new ol.style.Fill({color: '#000'}),
            stroke: new ol.style.Stroke({
                color: '#fff', width: 2
            }),
        }),
    }),
    'Point': new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            stroke: new ol.style.Stroke({
                color: 'lightgray',
                width: 2
            }),
            fill: new ol.style.Fill({
                color: 'green'
            })
        })
    })
};

var base_text_style = {
    font: '12px Calibri,sans-serif',
    textAlign: 'center',
    offsetY: -15,
    fill: new ol.style.Fill({
        color: [0, 0, 0, 1]
    }),
    stroke: new ol.style.Stroke({
        color: [255, 255, 255, 0.5],
        width: 4
    })
};


init();

function init() {
    init_map();
    load_table_schema(info_table);
    load_table_gpif_schema(gpif_table);
    init_feature_overlay_create();
    getCategories();
    // reload_layers();
}


function init_map(options = {}, center = map_center, zoom = map_zoom) {
    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: tile_sources["Stamen"],
            }),
        ],
        view: new ol.View({
            center: map_center,
            zoom: map_zoom,
        }),
        interactions: ol.interaction.defaults({mouseWheelZoom: false}),
    });
};

//function that change the language of info table
function change_lang() {
    lang = !lang;
    load_table_schema(info_table);
    load_table_gpif_schema(gpif_table);
    load_table(table_data);
}

//function to set the appropriate table schema basing on the language
function load_table_schema(table) {
    let en_schema = ['ID', 'Title', 'Creator', 'Scientific Name', 'Description', 'Publisher', 'Date', 'Relation', 'Source', 'Language'];
    let ar_schema = ['الهوية', 'العنوان', 'الموضوع', 'الوصف', 'المصدر', 'الحق', 'التاريخ'];
    let schema = lang ? en_schema : ar_schema;
    let head = table.createTHead();
    head.innerHTML = "";
    let row = head.insertRow(0);
    for (let i = 0; i < schema.length; i++) {
        row.innerHTML += '<th>' + schema[i] + '</th>';
    }
}

function load_table_gpif_schema(table) {
    let en_schema = ['Key', 'basisOfRecord', 'scientificName', 'acceptedScientificName', 'stateProvince', 'year', 'month', 'day', 'country', 'datasetName', 'relation'];
    let ar_schema = ['الهوية', 'العنوان', 'الموضوع', 'الوصف', 'المصدر', 'الحق', 'التاريخ'];
    let schema = lang ? en_schema : ar_schema;
    let head = table.createTHead();
    head.innerHTML = "";
    let row = head.insertRow(0);
    for (let i = 0; i < schema.length; i++) {
        row.innerHTML += '<th>' + schema[i] + '</th>';
    }
}

//function that control loading of elements to table by either flushing its content
//or appending to its current data e.i. table_data
function load_table(elements, overwrite = true) {

    if (overwrite) {
        info_table.tBodies[0].innerHTML = '';
        table_data = [];
    }
    for (let i = 0, ele; ele = elements[i++];) {
        add_feature_info(ele);
        table_data.push(ele);
    }
}

//function that single row to table with two language options
function add_feature_info(element) {
    let tr = document.createElement('tr');
    let en_schema = ['title', 'creator', 'identifier', 'description', 'publisher', 'date', 'relation', 'source', 'language'];
    let ar_schema = ['ar_title', 'ar_subject', 'ar_description', 'ar_source', 'ar_rights', 'date'];
    let schema = lang ? en_schema : ar_schema;
    let row = '<td>' + element.id + '</td>';
    for (let i = 0; i < schema.length; i++) {
        if (element.properties)
            row += '<td>' + element.properties[schema[i]] + '</td>';
        else {
            if (schema[i] == 'identifier' && element[schema[i]] != 'NONE' && element[schema[i]]) {
                row += '<td> <a href="' + element[schema[i]].split('||')[1].trim() + '"  target="_blank" >' + element[schema[i]].split('||')[0].trim() + '</a></td>'
            } else {
                row += '<td>' + element[schema[i]] + '</td>';
            }

        }
    }
    tr.innerHTML = row;
    info_table.tBodies[0].appendChild(tr);
}

// function that reload the overlay of the map
function init_feature_overlay_create(options = {}) {
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
function overlay_style_function(feature) {
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
    } else {
        style = highlight_styles[geom.getType()];
    }
    return [style];
}

//function that initiate the search process.
//upon reponse from API it calls the functions that are reponsible of loading all data (geo, info) to the UI
async function getCategories(url = base_api_url + 'categories/', page_number = 1) {

    let parsed_url = url.split('?');

    if (parsed_url.length == 1) {
        url += '?page=' + page_number;
    } else {
        url += '&page=' + page_number;
    }
    for (category in categories) {
        await get_sub_categories(url, category, categories);
    }
}


async function get_sub_categories(url, category, categories) {

    let tempUrl = url + '&category=' + category;
    await axios.get(tempUrl, {headers: {Authorization: api_key}}).then(function (response) {
        let sub_categories = response.data;
        render_categories(category, sub_categories);
    }).catch(function (error) {
        console.log(error);
    });
}

function render_categories(category, sub_categories) {

    let div = document.createElement('DIV');
    div.setAttribute('style', "margin-top: 5px;")
    div.innerHTML += '<label class="facet-field text-capitalize">' + category + '</label>';
    let expand_collapse_button = document.createElement('button');
    expand_collapse_button.setAttribute('id', category + '_ex_co');
    expand_collapse_button.setAttribute('onclick', "expand_collapse_div('" + category + "')");
    expand_collapse_button.setAttribute('class', 'expand-collapse')
    expand_collapse_button.innerHTML = '-';
    div.appendChild(expand_collapse_button);
    let category_div = document.createElement('DIV');
    category_div.setAttribute('id', category + '_div');
    category_div.setAttribute('style', "display: block;")
    let category_ul = document.createElement('UL');
    category_ul.setAttribute('style', "padding-left: 0px;");
    let ele_count = []
    for (let sub_category in sub_categories) {

        //console.log(sub_categories[sub_category]['categoryName'])
        if (sub_categories[sub_category].length == 0 || sub_categories[sub_category]['categoryName'] == '')
            continue;

        categories[category][sub_categories[sub_category]['categoryId']] = 0;
        let sub_category_input_element = document.createElement("INPUT");
        sub_category_input_element.classList.add('facet-term');
        sub_category_input_element.setAttribute('type', 'checkbox');
        sub_category_input_element.setAttribute('value', sub_categories[sub_category]['categoryName']);
        sub_category_input_element.setAttribute('onclick', "search('" + category + "','" + sub_categories[sub_category]['categoryId'] + "',this)");
        sub_category_input_element.setAttribute('data-field', sub_categories[sub_category]['categoryId']);
        let li = document.createElement('LI');
        li.appendChild(sub_category_input_element);
        li.innerHTML += sub_categories[sub_category]['categoryName'] + '<span class="badge badge-pill badge-secondary">' + sub_categories[sub_category]['total'] + '</span>'
        ele_count[sub_categories[sub_category]['categoryName']] = sub_categories[sub_category]['total']

        category_ul.appendChild(li);

        category_div.appendChild(category_ul);
        div.appendChild(category_div);
        facets_widget.appendChild(div);
    }
    facet_counts[category] = ele_count
    return true;
}


function search(category, sub_category, checkboxCategory, url = base_api_url + 'dataElementsMerge/', page_number = 1) {
    let exclude_field = category
    show_hide_loader($('.loading-mask.loader'))
    if (checkboxCategory.checked) {
        categories[category][sub_category] = 1;
        categories_counter[category] += 1;
    } else {
        categories[category][sub_category] = 0;
        categories_counter[category] -= 1;
    }


    let parsed_url = url.split('?');
    if (parsed_url.length == 1) {
        url += '?page=' + page_number;
    } else {
        url += '&page=' + page_number;
    }
    let atLeastOneSelected = false;
    for (category in categories) {
        temp = "";
        for (sub_category in categories[category]) {
            if (categories[category][sub_category] == 1) {
                atLeastOneSelected = true;
                temp += sub_category + '___';
            }
        }
        if (temp != "") {
            url += '&' + category + '=' + temp.substring(0, (temp.length - 3));
        }
    }

    if (atLeastOneSelected) {
        axios.get(url, {headers: {Authorization: api_key}}).then(function (response) {
            search_history.push(url);
            final_page = response.data;
            page = response.data;
            //selectedElements = response.data;
            //selectedElements = jQuery.extend(true, {}, final_page);
            //console.log(selectedElements);
            load_pages_nav(final_page, page_number);
            load_elements(final_page.results);
            load_elements_table(final_page.results);
            counter = final_page.count
            setCount(final_page.count);
            update_categories_counts(final_page.facet_count.fields, atLeastOneSelected);
            show_hide_loader($('.loading-mask.loader'))
            let oneSelected = atLesatOneSelected()
            if (oneSelected) {
                rest_facet_count_one_cateogry(oneSelected)
            }
        }).catch(function (error) {
            console.log(error);
        });
    } else {
        counter = 0
        setCount(0)
        load_elements({});
        load_elements_table({});
        load_pages_nav({}, 0);
        reset_facet_counts()
        show_hide_loader($('.loading-mask.loader'))
    }
}

// update categories count for every query
function update_categories_counts(facet_fields, atLeastOneSelected) {
    let category_ids = ['source', 'subject', 'level1', 'level2', 'level3', 'level4', 'year']
    let inputs = []
    for (let index = 0; index < category_ids.length; index++) {
        if (categories_counter[category_ids[index]] > 0 && atLeastOneSelected) {
            continue;
        }
        inputs = $('#' + category_ids[index] + '_div input')
        // convert the array to directory to improve searching on every facet
        let size = facet_fields[category_ids[index]].length
        for (let j = 0; j < size; j++) {
            facet_fields[category_ids[index]][facet_fields[category_ids[index]][j][0]] = facet_fields[category_ids[index]][j][1]
            delete facet_fields[category_ids[index]][j]
        }
        for (let j = 0; j < inputs.length; j++) {
            let text = $(inputs[j]).val()
            $($(inputs[j]).parent().children()[1]).text(facet_fields[category_ids[index]][text])
        }
    }
}

//check if at least one selecte
function atLesatOneSelected() {
    let category_ids = ['source', 'subject', 'level1', 'level2', 'level3', 'level4', 'year']
    let selected = []
    for (let index = 0; index < category_ids.length; index++) {
        if (categories_counter[category_ids[index]] > 0) {
            selected.push(category_ids[index])
        }
    }
    if (selected.length == 1) {
        return selected[0]
    } else {
        return false;
    }
}

function rest_facet_count_one_cateogry(category) {
    let category_ids = ['source', 'subject', 'level1', 'level2', 'level3', 'level4', 'year']
    let inputs = []

    inputs = $('#' + category + '_div input')
    // convert the array to directory to improve searching on every facet
    for (let j = 0; j < inputs.length; j++) {
        let text = $(inputs[j]).val()
        $($(inputs[j]).parent().children()[1]).text(facet_counts[category][text])
    }


}

//
function reset_facet_counts() {
    let category_ids = ['source', 'subject', 'level1', 'level2', 'level3', 'level4', 'year']
    let inputs = []
    for (let index = 0; index < category_ids.length; index++) {
        inputs = $('#' + category_ids[index] + '_div input')
        // convert the array to directory to improve searching on every facet
        for (let j = 0; j < inputs.length; j++) {
            let text = $(inputs[j]).val()
            $($(inputs[j]).parent().children()[1]).text(facet_counts[category_ids[index]][text])
        }
    }
}

//load list of geo elements on the map
function load_elements(elements,) {

    //dictionary that map elments' types names into haystack types' names
    let mapping = {
        "point_elements": 'PointDataElement',
        "line_elements": 'LineStringDataElement',
        "multi_line_elements": 'MultiLineStringDataElement',
        "polygon_elements": 'PolygonDataElement',
        "multi_polygon_elements": 'MultiPolygonDataElement',
    };
    for (type in mapping) {
        if (layersTypes[type]) {
            map.removeLayer(layersTypes[type]);
            layersTypes[type] = null;
        }
        //in case that makaneyya does not have this type of elemets
        if (!elements[mapping[type]]) continue;
        let source = new ol.source.Vector({
            format: new ol.format.GeoJSON({featureProjection: 'EPSG:3857'}),
            features: (new ol.format.GeoJSON({featureProjection: 'EPSG:3857'})).readFeatures(elements[mapping[type]]),
        });
        layersTypes[type] = new ol.layer.Vector({
            source: source,
            // style: style_function,
        });
        map.addLayer(layersTypes[type]);
    }
}


//style function contain the basic styling
function style_function(feature) {
    let style;
    let geom = feature.getGeometry();
    style = styles[geom.getType()];

    return style ? [style] : null;
}

//function the initiate table loading
function load_elements_table(elementss) {

    load_table([], true);
    for (type in elementss) {
        if (type == 'DataElement') {
            load_table(elementss[type], false);
        } else {
            load_table(elementss[type]['features'], false);
        }
    }
}

//function that load to UI the nav for page selection
function load_pages_nav(page, current_page) {

    let page_size = 100;
    html = "<nav aria-label='Page navigation'>" +
        "<ul class='pagination'>";
    for (let i = 1; i <= Math.ceil(page.count / page_size); i++) {
        html += '<li class="page-item' + (i == current_page ? ' active' : '') + '" onclick="change_page(this,' + i + ')" >'
            + '<span class="page-link">' + i + '</span></li>';
    }
    html += '</ul></nav>';

    document.getElementById('page-nav').innerHTML = html;
}

function setCount(count) {
    document.getElementById('counter').innerText = count
}

//function that chang the search page
function change_page(target, page_number) {
    let url = search_history[search_history.length - 1]
    url = url.replace(/page=[0-9]+/, 'page=' + page_number)
    axios.get(url, {headers: {Authorization: api_key}}).then(function (response) {
        search_history.push(url);
        final_page = response.data;
        page = response.data;
        load_pages_nav(final_page, page_number);
        // load_elements(final_page.results);
        load_elements_table(final_page.results);

        setCount(final_page.count);
    }).catch(function (error) {
        console.log(error);
    });

}

//button callback function for save maknehyaa
async function createMakaneyya(event) {
    event.preventDefault();

    await get_all_elements().then(async data => {
        await prepare_elements(data);
    })

    // prepare_elements(page.results);
    makaneyya_obj.title = document.getElementById('title').value;
    makaneyya_obj.description = document.getElementById('description').value;
    makaneyya_obj.tags = document.getElementById('tags').value.split(',');
    makaneyya_obj.gbifQuery = getGbifQuery() + "||" + get_gbif_polygon_query_urls();
    makaneyya_obj.gbifQueryByArea = getGeometries();

    if (!makaneyya_obj.lon)
        snap_map();

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                xhr.setRequestHeader("Authorization", "Api-Key C3Sau3vx.hQ22Ta97R1DpeWPySMXKKcvQHYvGI2cj")
            }
        }
    });

    $.ajax({
        type: 'POST',
        traditional: true,
        url: base_api_url + 'makaneyyat/',
        data: JSON.stringify(makaneyya_obj),
        contentType: 'application/json; charset=utf-8',
        success: function (msg) {
            alert('Makaneyya have been created successfully')
        },
        error: function (error) {
            alert('Makaneyya not created error' + error)
            console.log(error)
        },
        dataType: 'json',
    });
}

//load makaneuyya_obj with the URI of each data element
function prepare_elements(all_elements) {
    //this diectionary maps haystack results names to makaneyya model fields' names
    let haystack_to_model = {
        'DataElement': 'elements',
        'PointDataElement': 'point_elements',
        'LineStringDataElement': 'line_elements',
        'MultiLineStringDataElement': 'multi_line_elements',
        'PolygonDataElement': 'polygon_elements',
        'MultiPolygonDataElement': 'multi_polygon_elements',
    };
    //this diectionary maps haystack results names to the API collections' names
    let haystack_to_API = {
        'DataElement': 'dataElements',
        'PointDataElement': 'pointDataElements',
        'LineStringDataElement': 'lineStringDataElements',
        'MultiLineStringDataElement': 'multiLineStringDataElements',
        'PolygonDataElement': 'polygonDataElements',
        'MultiPolygonDataElement': 'multiPolygonDataElements',
    };

    for (type in all_elements) {
        makaneyya_obj[haystack_to_model[type]] = []
        if (all_elements[type]) {
            let elements = all_elements[type].features ? all_elements[type].features : all_elements[type];
            for (let i = 0, element; element = elements[i++];) {
                // makaneyya_obj[haystack_to_model[type]].push(base_api_url + haystack_to_API[type] + '/' + element.id +'/');
                makaneyya_obj[haystack_to_model[type]].push(element.id);
            }
            ;
        }
    }
}


//function that snap the view's coordinated of the map
function snap_map() {
    mak_center = map.getView().getCenter();
    let center = ol.proj.transform(mak_center, "EPSG:3857", "EPSG:4326");
    makaneyya_obj.lon = center[1];
    makaneyya_obj.lat = center[0];
}

// if full_display is set to true the element info will be displayed
// on ele_info_panel, else only tooltip will be displayed
map.on('pointermove', function (browserEvent) {

    // first clear any existing features in the overlay
    layers["overlay"].getSource().clear();

    if (full_display)
        ele_info_panel.innerHTML = '';
    let coordinate = browserEvent.coordinate;
    let pixel = browserEvent.pixel;
    $('#geometry-name .value').text('');
    // then for each feature at the mouse position ...
    map.forEachFeatureAtPixel(pixel, function (feature, layer) {
        // check the layer property, if it is not set then it means we
        // are over an OverlayFeature and we can ignore this feature
        if (!layer) {
            return;
        }

        if (full_display)
            display_ele_info(feature);

        let geometry = feature.getGeometry();
        let point;
        switch (geometry.getType()) {
            case 'MultiPolygon':
                let poly = geometry.getPolygons().reduce(function (left, right) {
                    return left.getArea() > right.getArea() ? left : right;
                });
                point = poly.getInteriorPoint().getCoordinates();
                break;
            case 'Polygon':
                point = geometry.getInteriorPoint().getCoordinates();
                break;
            default:
                point = geometry.getClosestPoint(coordinate);
        }
        // create a new feature to display the text
        let layer_name = get_layer_name(layer);
        let feature_text = feature.get(display_text);

        $('#geometry-name .value').text(feature_text)
        // text_feature = new ol.Feature({
        //   geometry: new ol.geom.Point(point),
        //   text: feature_text != 'null'?feature_text:'',
        // });

        // and add it to the featureOverlay.  Also add the feature itself
        // layers["overlay"].getSource().addFeature(text_feature);
        layers["overlay"].getSource().addFeature(feature);
    });
});

// using jQuery
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function expand_collapse_div(category) {
    if (document.getElementById(category + '_div').style.display == 'block') {
        document.getElementById(category + '_div').style.display = 'none';
        document.getElementById(category + '_ex_co').innerHTML = '+';
    } else {
        document.getElementById(category + '_div').style.display = 'block';
        document.getElementById(category + '_ex_co').innerHTML = '-';
    }
}


//function that reload the tile layer basing on user choice
function reload_tile_layer() {

    let base_map = document.getElementById("select-base-map");
    let option = base_map.options[base_map.selectedIndex].value;

    let tile = new ol.layer.Tile({
        source: tile_sources[option],
    });

    map.getLayers().setAt(0, tile);
}

function update_display_text() {
    let select = document.getElementById("select-display-text");
    let option = select.options[select.selectedIndex].value;

    display_text = option
}

function get_layer_name(layer) {
    for (key in layers) {
        if (layers[key] == layer) {
            return key;
        }
    }
}


show_hide_loader($('.loading-mask.loader'))

function show_hide_loader(element) {
    if ($(element).is(":hidden")) {
        $(element).show()
        // $(element).parent().css('overflow-y','hidden')
    } else {
        $(element).hide()
        // $(element).parent().css('overflow-y','scroll')
    }
}


// the code belwo should improved

function get_all_elements(url = base_api_url + 'dataElementsMerge/?page_size=' + counter) {
    for (category in categories) {
        temp = "";
        for (sub_category in categories[category]) {
            if (categories[category][sub_category] == 1) {
                atLeastOneSelected = true;
                temp += sub_category + '___';
            }
        }
        if (temp != "") {
            url += '&' + category + '=' + temp.substring(0, (temp.length - 3));
        }
    }

    return axios.get(url, {headers: {Authorization: api_key}}).then(response => {
        return final_page.results
    }).catch(function (error) {
        console.log(error);
    });
}

function get_gbif_polygon_query_urls() {
    return gbif_polygon_query_urls.join("||")
}