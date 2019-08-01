var makaneyya_form = document.getElementById('makaneyya-form');
var facets_widget = document.getElementById('map-facets');
var info_table = document.getElementById('info-table');
var full_display = false;

var search_history = []

if(makaneyya_form)
	makaneyya_form.onsubmit = createMakaneyya; 


var layers = {};
var csrftoken = getCookie('csrftoken'); 

//object that maintain the current selected page 
var page = {
'results':{},
'count': null,
'previous': null,
'next':null,
}

//makaneyya object
var makaneyya_obj={
  "elements": [],
  "point_elements":[],
  "linestring_elements": [],
  "multi_linestring_elements": [],
  "polygon_elements": [],
  "multi_polygon_elements": [],
  "tags": [],
  "lon": null,
  "lat": null,

}
//======================================== ==========================
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//load makaneuyya_obj with the URI of each data element
function prepare_elements(all_elements) {

	//this diectionary maps haystack results names to makaneyya model fields' names 
	var  haystack_to_model = {
		'DataElement': 'elements',
		'PointDataElement': 'point_elements',
		'LineStringDataElement': 'line_elements',
		'MultiLineStringDataElement': 'multi_line_elements',
		'PolygonDataElement': 'polygon_elements',
		'MultiPolygonDataElement': 'multi_polygon_elements',
	};
	//this diectionary maps haystack results names to the API collections' names
	var haystack_to_API = {
		'DataElement': 'dataElements',
		'PointDataElement': 'pointDataElements',
		'LineStringDataElement': 'lineStringDataElements',
		'MultiLineStringDataElement': 'multiLineStringDataElements',
		'PolygonDataElement': 'polygonDataElements',
		'MultiPolygonDataElement': 'multiPolygonDataElements',
	};  

	for(type in all_elements){
		makaneyya_obj[haystack_to_model[type]] = []
		if(all_elements[type]){
			var elements = all_elements[type].features?all_elements[type].features:all_elements[type];
			for(var i = 0, element;element = elements[i++];){
	        	makaneyya_obj[haystack_to_model[type]].push(base_api_url + haystack_to_API[type] + '/' + element.id +'/');
			};
		}
	}
       
}   


//function that snap the view's coordinated of the map
function snap_map(){
	mak_center = map.getView().getCenter();
	makaneyya_obj.lon = mak_center[0];
	makaneyya_obj.lat = mak_center[1];
}



//load list of geo elements on the map
function load_elements(elements,){

	//dictionary that map elments' types names into haystack types' names 
	var mapping = {
		"point_elements": 'PointDataElement',
		"line_elements": 'LineStringDataElement',
		"multi_line_elements": 'MultiLineStringDataElement',
		"polygon_elements": 'PolygonDataElement',
		"multi_polygon_elements": 'MultiPolygonDataElement',
	}; 
	for(type in mapping){
		if(layers[type]){
			map.removeLayer(layers[type]);	
			layers[type] = null;
		}
		//in case that makaneyya does not have this type of elemets
		if(!elements[mapping[type]])continue;
		var source = new ol.source.Vector({
		  format: new ol.format.GeoJSON({featureProjection:'EPSG:3857'}),
		  features: (new ol.format.GeoJSON({featureProjection:'EPSG:3857'})).readFeatures(elements[mapping[type]]),
		});
		layers[type] = new ol.layer.Vector({
	    	source: source,
	    	style: style_function,
		});
		map.addLayer(layers[type]);
	}
}


//function the initiate table loading 
function load_elements_table(elements){
	load_table([], true);
	for(type in elements){
		if(type == 'DataElement')
			load_table(elements[type], false);
		else
			load_table(elements[type]['features'], false);
	}
}

//function that initiate the search process.
//upon reponse from API it calls the functions that are reponsible of loading all data (geo, info) to the UI
function search(url = base_api_url + 'search/facets/', page_number = 1) {
	var parsed_url = url.split('?');
	if( parsed_url.length == 1){
		url += '?page=' + page_number;  
	}else{
		url += '&page=' + page_number;
	}
	axios.get(url).then(function(response) {
		search_history.push(url);
		var data = response.data;
		page = data['objects'];
		load_facets(data['fields']);
		load_elements(page.results);
		load_elements_table(page.results);
		load_pages_nav(page, page_number);

    }).catch(function(error){
		console.log(error);   
  	});
}


//return one step back on the search process
function search_backward(){
	if(search_history.length > 1){
		search_history.pop();
		search(search_history.pop());
	}
}

//function that chang the search page
function change_page(target, page_number){
	search(search_history[search_history.length -1], page_number);
}


//function that load to UI the nav for page selection
function load_pages_nav(page, current_page){

	var page_size = 200;
	html = "<nav aria-label='Page navigation'>" +
    	"<ul class='pagination'>";
	for(var i = 1; i <= Math.ceil(page.count / page_size); i++){
		html += '<li class="page-item' + (i == current_page?' active':'') + '" onclick="change_page(this,' + i +  ')" >'
		+ '<a href="#" class="page-link">' + i + '</a></li>';
	}
    html += '</ul></nav>';

    document.getElementById('page-nav').innerHTML = html;
}



function load_facets(facet_fields){
	
	facets_widget.innerHTML = '';
	for(var field in facet_fields){

		if(facet_fields[field].length == 0)continue;

		var field_list = document.createElement('UL');
		field_list.innerHTML += '<li class="facet-field text-capitalize">'+ field + '</li>'
		for(var i = 0; i < facet_fields[field].length; i++){
			var drill_down = document.createElement('A');
			drill_down.classList.add('facet-term');
			drill_down.setAttribute('data-field', facet_fields[field][i]['narrow_url']);
			drill_down.onclick = function(evt){
				search(evt.target.getAttribute('data-field'));
			};
			drill_down.innerHTML = facet_fields[field][i]['text'] + '<span class="badge badge-pill badge-secondary">'+ facet_fields[field][i]['count']+ '</span>';
			var li = document.createElement('LI');
			li.appendChild(drill_down);
			field_list.appendChild(li);		
		}

		facets_widget.appendChild(field_list);
	}
}

//button callback function for save maknehyaa
function createMakaneyya(event){
	event.preventDefault();

	prepare_elements(page.results);
	makaneyya_obj.title = document.getElementById('title').value;
	makaneyya_obj.description = document.getElementById('description').value;
	makaneyya_obj.tags = document.getElementById('tags').value.split(',');
	
	if(!makaneyya_obj.lon)
		snap_map();

	function csrfSafeMethod(method) {
		// these HTTP methods do not require CSRF protection
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}

	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			    xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
	
	$.ajax({
	type:'POST',
	traditional:true,
	url: base_api_url + 'makaneyyat/',
	data:makaneyya_obj,
	success:function(msg){
		alert('Makaneyya have been created successfully')
	},
	error:function(error){
		alert('Makaneyya not created error' + error)
		console.log(error)
	},
	dataType:'json',
	});

}

function init(){
	init_map();
	load_table_schema(info_table);
	init_feature_overlay();
	search();
}

init();
