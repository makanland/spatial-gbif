var map_center =  ol.proj.transform([35.024549, 32.066549], 'EPSG:4326', 'EPSG:3857');
var map_zoom =  10;
var lang = true;
var gpif_table = document.getElementById('gpif-table');
var api_key = "Api-Key C3Sau3vx.hQ22Ta97R1DpeWPySMXKKcvQHYvGI2cj"
//used to reload the table with same elements but for different attribute
var table_data = []

var tile_sources = {
  OSM : new ol.source.OSM(), 
  Stamen: new ol.source.Stamen({ layer:'terrain-background' }),
  Bing: new ol.source.BingMaps({
          key:' AixJpONnZC80xs7_Q_076pCxhe2aOOQbdKOqxRorqYK2SnFp3fKKaMs3KAHMvsVN',
          imagerySet: 'Aerial',
  }),
};


var layers = {
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
  'Polygon': new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: [255,0,0,0.6],
      width: 2
    }),
    fill: new ol.style.Fill({
      color: [255,0,0,0.2]
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
    color: [0,0,0,1]
  }),
  stroke: new ol.style.Stroke({
    color: [255,255,255,0.5],
    width: 4
  })
};

//style function contain the basic styling 
function style_function(feature){
  let style;
  let geom = feature.getGeometry();
  style =  styles[geom.getType()];
  
  return style?[style]:null;
}

//style function that bind a style to feature basing on its type
function overlay_style_function(feature){
  let style = [];
  let geom = feature.getGeometry();
  base_text_style.text = feature.getKeys().includes(display_text)?feature.get(display_text):" ";
  // this is inefficient as it could create new style objects for the
  // same text.
  // A good exercise to see if you understand would be to add caching
  // of this text style
  style.push(new ol.style.Style({
    text: new ol.style.Text(base_text_style),
    zIndex: 3
  }));

  if(highlight_styles[geom.getType()])
    style.push(highlight_styles[geom.getType()]);
  
  return style;
  
}

//function that reload the overlay of the map 
function init_feature_overlay(options = {}){
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


function init_map(options = {}, center = map_center, zoom = map_zoom){
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
    interactions: ol.interaction.defaults({mouseWheelZoom:false}),
  });
};


//function that reload the tile layer basing on user choice
function reload_tile_layer(){

  let base_map = document.getElementById("select-base-map");
  let option = base_map.options[base_map.selectedIndex].value;

  let tile = new ol.layer.Tile({
    source: tile_sources[option],
  });

  map.getLayers().setAt(0, tile);

}


//function that single row to table with two language options 
function add_feature_info(element){
 let tr = document.createElement('tr');
  let en_schema = ['title','creator','identifier','description','publisher','date','source','language'];
  let ar_schema = ['ar_title', 'ar_subject', 'ar_description', 'ar_source', 'ar_rights', 'date'];
  let schema = lang?en_schema:ar_schema;
  let row = '<td>' + element.id + '</td>';
  for(let i = 0 ;i < schema.length; i++){
    if(element.properties)
      row += '<td>' +element.properties[schema[i]] +'</td>';
    else {
    	if(schema[i]=='identifier' && element[schema[i]] != 'NONE' && element[schema[i]]){
    		row += '<td> <a href="' + element[schema[i]].split('||')[1].trim() + '"  target="_blank" >' + element[schema[i]].split('||')[0].trim() + '</a></td>'
		}else {
    		row += '<td>' + element[schema[i]] + '</td>';
		}

	}
  }
  tr.innerHTML = row;
  info_table.tBodies[0].appendChild(tr);
}


//function to set the appropriate table schema basing on the language
function load_table_schema(table){
  let en_schema = ['ID','Title','Creator','Scientific Name','Description','Publisher','Date','Source','Language'];
  let ar_schema = ['الهوية','العنوان', 'الموضوع', 'الوصف', 'المصدر', 'الحق', 'التاريخ'];
  let schema = lang?en_schema:ar_schema;
  let head = table.createTHead();
  head.innerHTML = "";
  let row = head.insertRow(0);
  for(let i = 0; i < schema.length; i++){
    row.innerHTML += '<th>' + schema[i] + '</th>';
  } 
}

function load_table_gpif_schema(table){
  let en_schema = ['Key','basisOfRecord', 'scientificName', 'acceptedScientificName', 'stateProvince', 'year', 'month', 'day', 'country','datasetName','relation'];
  let ar_schema = ['الهوية','العنوان', 'الموضوع', 'الوصف', 'المصدر', 'الحق', 'التاريخ'];
  let schema = lang?en_schema:ar_schema;
  let head = table.createTHead();
  head.innerHTML = "";
  let row = head.insertRow(0);
  for(let i = 0; i < schema.length; i++){
    row.innerHTML += '<th>' + schema[i] + '</th>';
  }
}

//function that control loading of elements to table by either flushing its content
//or appending to its current data e.i. table_data
function load_table(elements, overwrite = true, is_data_element){

  if(overwrite){
    info_table.tBodies[0].innerHTML = '';
    table_data = [];
  }
  if(!is_data_element){
      let id = elements[0]['id']
      elements = elements[0]['properties']
      elements['id'] = id
      elements = [elements]
  }
  for(let i=0, ele; ele = elements[i++];){
    add_feature_info(ele);
    table_data.push(ele);
  }
}

//function that change the language of info table
function change_lang(){
  lang = !lang;
  load_table_schema(info_table);
  load_table_gpif_schema(gpif_table);
  load_table(table_data);
}

