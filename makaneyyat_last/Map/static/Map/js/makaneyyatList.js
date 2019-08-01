function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    let regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


//function that populate the search fields of makaneyya-list.html when page reload
function populate_form_fields(form_id, names){
	let elements = document.getElementById(form_id).elements;
	for(var i = 0, element; element = elements[i++];){
		if(element.name in names)
			element.value = getParameterByName(element.name);
	}
}

populate_form_fields('makaneyyat-filter-form', ['author', 'title', 'tags']);