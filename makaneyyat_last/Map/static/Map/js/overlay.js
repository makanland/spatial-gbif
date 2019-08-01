
//update the display text (on hover event) of the features
function update_display_text(){

  let select = document.getElementById("select-display-text");
  display_text = select.options[select.selectedIndex].value;

}

//if full_display is set to true the element info will be displayed
//on ele_info_panel, else only tooltip will be displayed
map.on('pointermove', function(browserEvent) {
  // first clear any existing features in the overlay
  layers["overlay"].getSource().clear();
  
  if(full_display)
    ele_info_panel.innerHTML = '';
  let coordinate = browserEvent.coordinate;
  let pixel = browserEvent.pixel;
  // then for each feature at the mouse position ...
  map.forEachFeatureAtPixel(pixel, function(feature, layer) {
    // check the layer property, if it is not set then it means we
    // are over an OverlayFeature and we can ignore this feature
    if (!layer)return;
    
    if(full_display)
      display_ele_info(feature);
    layers["overlay"].getSource().addFeature(feature);
  
  });
});


//function the display the info of an element on the right-panel 
function display_ele_info(ele){
  html = "";
  let schema = ['title','creator','description','date'];
  for(let i = 0, field; field = schema[i++];){
    if(ele.get(field))
      // field =
      html += '<div id="element-info-row"><span class="element-info-head">'+ field[0].toUpperCase()+field.slice(1) + '</span><p>'+ ele.get(field) + '</p></div>';
  }
  ele_info_panel.innerHTML = html;
}

