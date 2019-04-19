function abrir_script() {
    if (document.getElementById("script").style.display == "none") {
        document.getElementById("script").style.display = "block" }
    else {
        document.getElementById("script").style.display = "none" }
}

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.getElementById("myBtn").style.display = "block";
  } else {
    document.getElementById("myBtn").style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

function excluir_selection() {
    document.getElementById("pesquisa").value = "";

    var checkboxes, i;
    checkboxes = document.getElementsByClassName("cb");
    for (i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked == true) {
            document.getElementById("pesquisa").value = document.getElementById("pesquisa").value + "^# text = " + escapeRegExp(document.getElementById("text_" + checkboxes[i].id.split('_')[1]).innerHTML) + "$|";
        }
    }

    if (document.getElementById("nome_pesquisa_sel").value == "") {
    	var data = new Date().toLocaleString()
        document.getElementById("nome_pesquisa_sel").value = "Seleção " + data;
    }

    document.getElementById("nome_pesquisa").value = document.getElementById("nome_pesquisa_sel").value;

    document.getElementById("pesquisa").value = document.getElementById("pesquisa").value.rsplit('|',1)[0];
    document.getElementById("filtrar").click();
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&').replace('&amp;', '.'); // $& means the whole matched string
}

String.prototype.rsplit = function(sep, maxsplit) {
    var split = this.split(sep);
    return maxsplit ? [ split.slice(0, -maxsplit).join(sep) ].concat(split.slice(-maxsplit)) : split;
}

function filtraragora(n) {
    var checkboxes, i;
    checkboxes = document.getElementsByClassName("cb");

    for (i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = false;
    }

    document.getElementById("checkbox_" + n).checked = true;
    document.getElementById("filtrarsel").click();
}

function tudo(event) {
    var checkboxes, i, anotacoes;
    checkboxes = document.getElementsByClassName("cb");
    anotacoes = document.getElementsByClassName("anotacao");

    if (event == "marcar"){
        for (i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = true;
        }
    }

    if (event == "desmarcar"){
        for (i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = false;
        }
    }

    if (event == "abrir") {
        for (i = 0; i < anotacoes.length; i++) {
            if (anotacoes[i].value == "Mostrar anotação") {
                anotacoes[i].click();
            }
        }
    }

    if (event == "fechar") {
        for (i = 0; i < anotacoes.length; i++) {
            if (anotacoes[i].value == "Esconder anotação") {
                anotacoes[i].click();
            }
        }
    }

}

function mostrar(nome, botao) {
    if (document.getElementById(nome).style.display == "none"){
        document.getElementById(nome).style.display = "block"
        document.getElementById(botao).value = "Esconder anotação"
    } else {
        document.getElementById(nome).style.display = "none"
        document.getElementById(botao).value = "Mostrar anotação"
    }
}

function mostraropt(nome, botao) {
    if (document.getElementById(nome).style.display == "none"){
        document.getElementById(nome).style.display = "block"
        document.getElementById(botao).value = "Esconder opções"
    } else {
        document.getElementById(nome).style.display = "none"
        document.getElementById(botao).value = "Mostrar opções"
    }
}

function contexto(nome, botao) {
    if (document.getElementById(nome).style.display == "none"){
        document.getElementById(nome).style.display = "block"
        document.getElementById(botao).value = "Esconder contexto"
    } else {
        document.getElementById(nome).style.display = "none"
        document.getElementById(botao).value = "Mostrar contexto"
    }
}

function apagar() {
    if (confirm('Apagar interrogação "' + document.getElementById("combination").innerHTML.replace('&lt;', '<').replace('&gt;', '>') + '"?')) {
        window.location = "/cgi-bin/apagar.cgi?query=" + document.getElementById("apagar_link").value;
    }
}

function openCity(evt, cityName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";

    document.getElementById("fechartabs").style.display = "block"
}

function fechar_tabs() {
    var tablinks, i, tabcontent;

	tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

	document.getElementById('fechartabs').style.display = "none";

	tablinks = document.getElementById("tablinks");
	for (i = 0; i < tablinks.length; i++) {
           tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
}

function inquerito(ide) {
    document.getElementById(ide).submit()
}

function anotarudpipe(ide) {
    document.getElementById(ide).submit()
}

function drawtree(ide) {
    document.getElementById(ide).submit()
}

function load() {
    url = new URL(window.location.href);
    if (url.searchParams.get('page') == 'hide') {
        $('#easyPaginate').easyPaginate({
            paginateElement: 'nadanao',
        });
    } else {
        $('#easyPaginate').easyPaginate({
            paginateElement: '.container',
            elementsPerPage: 10,
            firstButton: false,
            lastButton: false,
            prevButton: true,
            nextButton: true,
        });
    }
}

function paginacao() {
    if (window.location.href.indexOf("?page=hide") != -1){
        window.location = window.location.pathname;
    } else {
        window.location = "?page=hide";
    }
}
