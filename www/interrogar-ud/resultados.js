$(window).on('beforeunload', function() {
    $('#loading-bg').show();
    $('#loading-image').show();
    setTimeout(waitTooMuch, 20000);
});

function enviar() {
    $('[class=field]').each(function(i){
        if ($(this).val() == $('#' + $(this).attr('name')).text().replace("<br>", '').replace('</div>', '').replace('<div>', '')) {
            this.remove();
        } else {
            $(this).val($('#' + $(this).attr('name')).text().replace("<br>", '').replace('</div>', '').replace('<div>', ''));
        }
    });
    document.getElementById('dados_inquerito').submit();
};

function encodeUrl(s){
    return s
        .replace(/ /g, '%20')
        .replace(/#/g, '%23')
        .replace(/\$/g, '%24')
        .replace(/&/g, "%26")
        .replace(/@/g, "%40")
        .replace(/`/g, "%60")
        .replace(/\//g, "%2F")
        .replace(/:/g, "%3A")
        .replace(/;/g, "%3B")
        .replace(/</g, "%3C")
        .replace(/=/g, "%3D")
        .replace(/>/g, "%3E")
        .replace(/\?/g, "%3F")
        .replace(/\[/g, "%5B")
        .replace(/\\/g, "%5C")
        .replace(/]/g, "%5D")
        .replace(/\^/g, "%5E")
        .replace(/{/g, "%7B")
        .replace(/\|/g, "%7C")
        .replace(/}/g, "%7D")
        .replace(/~/g, "%7E")
        .replace(/\"/g, "%22")
        .replace(/'/g, "%27")
        .replace(/\+/g, "%2B")
        .replace(/,/g, "%2C");
};

function waitTooMuch(){
    if ($('#loading-bg').is(':visible')){
        if (/interrogar\.cgi/.test(window.location.href)) {
            if (!$('.toggleSalvar').is(':checked')) {
                $('#loading-bg').append('<div style="width: 30vw; font-weight:500; margin:60vh auto;">Caso a busca esteja demorando muito, você pode optar por <a href=\'../cgi-bin/interrogar.cgi?corpus=' + $('.conllu').val() + '&save=True&go=True&params=' + encodeUrl($('.pesquisa').val()) + '\'>salvar a busca</a> e ela aparecerá na página de interrogações recentes quando concluir, mesmo que você feche esta página.')
            } else {
                $('#loading-bg').append('<div style="width: 30vw; font-weight:500; margin:60vh auto;">Caso a busca esteja demorando muito, você pode <a href="javascript:window.close()">fechar esta página</a> ou acompanhar o progresso na página de <a href="../cgi-bin/interrogatorio.cgi">interrogações recentes</a>.</div>');
            }
        }
    }
};

$(window).on('unload', function() {
    $('#loading-bg').hide();
    $('#loading-image').hide();
});

$(window).ready(function(){
    $('#loading-bg').hide();
    $('#loading-image').hide();
});

function pesquisaChange(){
    $('.queryString').hide();
    $('.normalQuery').show();
    if ($("#pesquisa").val()){
        $('.clearPesquisa').show();
    } else {
        $('.clearPesquisa').hide();
    };
    if ($('.toggleDist').is(':checked')) {
        if (/^5 /.test($('#pesquisa').val())) {
            $('.dist').show();
            $('.notDist').hide();
        } else {
            $('.dist').hide();
            $('.notDist').show();
        };
    };
};

function pesquisa(numero) {
    document.getElementById('pesquisa').value = document.getElementById(numero).innerHTML.replace(/&amp;/g, '&').replace(/&gt;/g, '>');
    pesquisaChange();
};

$(document).on('keydown', function(e){
    if (e.key === "Escape") {
        $('.endInquerito').click();
    }
});

$(document).ready(function(){

    $('.desfazerFiltro').click(function(){
        if (confirm('Todos os filtros posteriores ao "' + $(this).attr('nomeFiltro') +  '" serão apagados também. Continuar?')){
            window.location = $(this).attr('link');
        }
    });

    $('.tablinks').click(function(){
        $('.tablinks').css('background-color', 'transparent');
        $('.filterDiv').hide();
        $('#script').hide();
        $('.selectSome').hide();
        $('.inqueritoSome').hide();
        $('.viewDist').hide();
        if ($('.tab' + $(this).attr('tab')).is(":visible")){
            $('.tab' + $(this).attr('tab')).hide();
        } else {
            $(this).css('background-color', 'lightgray');
            $('.tabcontent').hide();
            $('#' + $(this).attr('tabid')).show();
        };
    });

    $('.filterAnchor').click(function(){
        $('.filterDiv').hide();
        $('.' + $(this).attr('tab')).show();
    });

    $('[tab=newSearchFilter]').click(function(){
        $('#pesquisa_filtro').focus();
    });

    $('[tab=selectionFilter]').click(function(){
        $('#nome_pesquisa_sel').focus();
    });

    $lastDistribution = "";

    $('.toggleSalvar, .toggleRapida').click(function(){
        $('#enviar').val($(this).attr('label'));
    });

    $('.sendInterrogar').on('submit', function(event){
        if (! $('#enviar').is(":visible")){
            event.preventDefault();
            if ($lastDistribution){
                if ($('.dist').is(':visible')){
                    $lastDistribution.click();
                };
            };
        };
    });

    $('.addCondition').click(function(){
        if (! $('#pesquisa').val()){
          $('#pesquisa').val('5 ');
        } else {
          $('#pesquisa').val($('#pesquisa').val() + ' and ');
        };
        $('#pesquisa').val($('#pesquisa').val() + $('.token').val() + "." + $('.atribute').val() + " " + $('.evaluation').val() + ' "' + $('.value').val() + '"');
        $('.value').val('');
        $('.pesquisa').focus();
        pesquisaChange();
    });

    $('.addBoldCondition').click(function(){
        if (! $('#pesquisa').val()){
          $('#pesquisa').val('5 ');
        } else {
          $('#pesquisa').val($('#pesquisa').val() + ' and ');
        };
        $('#pesquisa').val($('#pesquisa').val().replace(/\s@/g, " "));
        $('#pesquisa').val($('#pesquisa').val() + "@" + $('.token').val() + "." + $('.atribute').val() + " " + $('.evaluation').val() + ' "' + $('.value').val() + '"');
        $('.value').val('');
        $('.pesquisa').focus();
        pesquisaChange();
    });

    $('.clearCondition, .clearPesquisa').click(function(){
        $('#pesquisa').val('');
        pesquisaChange();
    });

    $('.value').keydown(function(event){
        if (event.which == 13 || event.keyCode == 13) {
            event.preventDefault();
            $('.addCondition').click();
        };
    });

    $('.evaluation').change(function(){
        if ($('.evaluation').val() == '=='){
            $('.ade').html(' a ');
        } else {
            $('.ade').html(' de ');
        };
    });

    $('#pesquisa').on('keyup', function(){pesquisaChange()});

    $('.toggleDist').on('click', function(){
        if (/^5 /.test($('#pesquisa').val())) {
            $('.dist').show();
            $('.notDist').hide();
        } else {
            $('.dist').hide();
            $('.notDist').show();
        }
    });

    $('.toggle:checked').click();

    $('.verDist').click(function(){
        if ($('#pesquisa').length){
            $('#html_dist').val($('#pesquisa').val().replace(/^5 /, ""));
            $('#expressao_dist').val($('#pesquisa').val());
            $('#corpus_dist').val($('.conllu').val());
            $lastDistribution = $(this);
            $('.verDist').css('color', '');
            $(this).css('color', 'rgba(255,105,30,1)');
        };
        dist($(this).html());
    });

    $('.drag').draggable({
        zIndex: 100,
        revert: true,
        opacity: 0.35,
        appendTo: "body",
        refreshPositions: true,
      },);
      
    $('tr').droppable({
        hoverClass: "drop-hover",
        drop: function(event, ui) {
            var classes = ui.draggable.attr('class');
            if ($(this).children('.id').html() != ui.draggable.siblings(".id").html()){
                ui.draggable.html($(this).children('.id').html());
            };
        }
    });

    $(document).on('keydown', function(event){
        if ((event.keyCode == 10 || event.keyCode == 13) && event.ctrlKey) {
            event.preventDefault();
            $('#sendAnnotation').click();
        };
    });

    $('.notPipe').click(function(){
        document.execCommand('selectAll');
    });

    $('.annotationValue').on('keydown', function(event){
        $td = $(this);
        if (event.keyCode == 38) {
            event.preventDefault();
            $linha = parseInt($td.attr('id').split("-")[0]) - 1;
            $coluna = $td.attr('id').split("-")[1];
            $('#' + $linha + '-' + $coluna).focus();
        };

        if (event.keyCode == 40) {
            event.preventDefault();
            $linha = parseInt($td.attr('id').split("-")[0]) + 1;
            $coluna = $td.attr('id').split("-")[1];
            $('#' + $linha + '-' + $coluna).focus();
        };
    });

});


function dist(coluna){
    if (! $('#pesquisa').length){
        document.getElementById("corpus_dist").value = document.getElementById("corpus").innerHTML
        document.getElementById("expressao_dist").value = document.getElementById("expressao").innerHTML
    }
    document.getElementById("coluna_dist").value = coluna
    $("#dist").submit()
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
    document.getElementById("pesquisa_filtro").value = "";

    var checkboxes, i, negrito;
    checkboxes = document.getElementsByClassName("cb");
    document.getElementById("pesquisa_filtro").value = "1 ";
    for (i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked == true) {
            if (document.getElementById("text_" + checkboxes[i].id.split(/_/)[1]).innerHTML.indexOf("<b>") !== -1){
                negrito = document.getElementById("text_" + checkboxes[i].id.split(/_/)[1]).innerHTML.substring(document.getElementById("text_" + checkboxes[i].id.split(/_/)[1]).innerHTML.indexOf('<b>')).split(/<\/b>/)[0].replace(/<.*?>/g, '');
            } else { negrito = ""; };
            document.getElementById("pesquisa_filtro").value = document.getElementById("pesquisa_filtro").value + "^# text = " + escapeRegExp(document.getElementById("text_" + checkboxes[i].id.split('_')[1]).innerHTML.replace(/<.*?>/g, '')) + "$|";
        };
    };

    if (document.getElementById("nome_pesquisa_sel").value == "") {
    	var data = new Date().toLocaleString()
        document.getElementById("nome_pesquisa_sel").value = "Seleção " + data;
    }

    document.getElementById("nome_pesquisa").value = document.getElementById("nome_pesquisa_sel").value;

    document.getElementById("pesquisa_filtro").value = document.getElementById("pesquisa_filtro").value.rsplit('|',1)[0];
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

function contexto(sent_id, id, corpus) {
    window.open( 
        "../cgi-bin/contexto.py?id=" + id + "&sent_id=" + sent_id + "&corpus=" + corpus, "_blank"); 
}

function apagar() {
    if (confirm('Apagar interrogação "' + document.getElementById("combination").innerHTML.replace('&lt;', '<').replace('&gt;', '>') + '"?')) {
        window.location = "../cgi-bin/apagar.cgi?query=" + document.getElementById("apagar_link").value;
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
