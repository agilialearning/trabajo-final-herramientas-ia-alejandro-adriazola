/* Navegación compartida del taller. Sin dependencias, funciona sin internet. */
(function(){
  var stage=document.querySelector('.stage');
  var slides=[];
  var panel=document.createElement('div');panel.id='panel-notas';document.body.appendChild(panel);
  var btnNotas=document.createElement('button');btnNotas.id='btn-notas';btnNotas.textContent='Notas';document.body.appendChild(btnNotas);
  function notas(v){btnNotas.classList.toggle('on',panel.classList.toggle('visible',v))}
  btnNotas.addEventListener('click',function(){notas()});
  var cur=0;

  function escala(){
    var s=Math.min(innerWidth/1920,innerHeight/1080);
    stage.style.setProperty('--s',s);
  }
  function ir(n){
    cur=Math.max(0,Math.min(slides.length-1,n));
    slides.forEach(function(s,i){s.classList.toggle('active',i===cur)});
    var nt=slides[cur]&&slides[cur].querySelector('.notes');
    panel.innerHTML=nt?nt.innerHTML:'<i>Sin notas.</i>';
    try{history.replaceState(null,'','#'+(cur+1))}catch(e){}
  }
  function pantallaCompleta(){
    var d=document;
    if(d.fullscreenElement){d.exitFullscreen()}else if(d.documentElement.requestFullscreen){d.documentElement.requestFullscreen()}
  }
  function copiar(btn){
    var t=btn.parentNode.querySelector('pre.prompt').innerText;
    function ok(){btn.textContent='Copiado';btn.classList.add('ok');setTimeout(function(){btn.textContent='Copiar';btn.classList.remove('ok')},1800)}
    function respaldo(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();
      try{document.execCommand('copy');ok()}catch(e){}document.body.removeChild(a)}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(ok,respaldo)}else{respaldo()}
  }

  /* navegación del taller: barra (aparece al mover el mouse), H inicio, M mapa, G cuadrícula */
  var archivo=(location.pathname.split('/').pop()||'').replace(/\?.*$/,'');
  if(archivo&&!/\.html$/.test(archivo))archivo+='.html';  // en la web, Cloudflare quita el .html de la URL
  function irMapa(){location.href='mapa.html#'+archivo+':'+(cur+1)}
  var barra=document.createElement('nav');barra.id='barra-taller';
  barra.innerHTML='<a href="#" data-a="rejilla">Diapos</a><span>G · N · F</span>';
  document.body.appendChild(barra);
  var tOcultar;
  addEventListener('mousemove',function(){barra.classList.add('visible');clearTimeout(tOcultar);tOcultar=setTimeout(function(){barra.classList.remove('visible')},2200)});
  var rej=document.createElement('div');rej.id='rejilla';document.body.appendChild(rej);
  rej.innerHTML='<div class="rej-top"><b>'+document.title+'</b><span>Clic en una diapo · Esc para cerrar</span></div><div class="rej-lista"></div>';
  var lista=rej.querySelector('.rej-lista');

  /* (re)numera diapos, contadores y cuadrícula; se llama al cargar y cuando el editor mueve o quita diapos */
  function renumerar(){
    slides=[].slice.call(document.querySelectorAll('.slide'));
    lista.innerHTML=slides.map(function(s,i){
      var c=s.querySelector(':scope>.contador');if(!c){c=document.createElement('div');c.className='contador';s.appendChild(c)}
      c.innerHTML=(s.classList.contains('portada')?'':'<span class="firma">'+((window.TALLER_META&&TALLER_META.firma)||'')+'</span>')+'<span>'+(i+1)+' / '+slides.length+'</span>';
      var h=s.querySelector('h1'),e=s.querySelector('.eyebrow');
      var t=(h?h.textContent:(e?e.textContent:'Diapo '+(i+1))).replace(/\s+/g,' ').trim();
      var cls=s.classList.contains('oscuro')?' oscuro':s.classList.contains('arcilla')?' arcilla':'';
      return '<button class="rej-item'+cls+'" data-n="'+i+'"><i>'+(i+1)+'</i><small>'+(e?e.textContent:'')+'</small>'+t+'</button>'}).join('');
  }
  function rejilla(on){rej.classList.toggle('visible',on);if(on){var b=rej.querySelector('[data-n="'+cur+'"]');if(b){b.classList.add('on');b.scrollIntoView({block:'center'})}}}
  rej.addEventListener('click',function(e){var b=e.target.closest('.rej-item');if(b&&!rej.classList.contains('ordenar')){ir(+b.dataset.n);rejilla(false)}else if(e.target===rej)rejilla(false)});
  barra.addEventListener('click',function(e){var a=e.target.closest('[data-a]');if(!a)return;e.preventDefault();a.dataset.a==='mapa'?irMapa():a.dataset.a==='rejilla'?rejilla(true):null});

  addEventListener('resize',escala);
  addEventListener('hashchange',function(){var n=(parseInt(location.hash.slice(1),10)||1)-1;if(n!==cur)ir(n)});
  addEventListener('keydown',function(e){
    if(e.ctrlKey||e.metaKey||e.altKey)return;
    if(e.target.isContentEditable||/INPUT|TEXTAREA/.test(e.target.tagName))return;
    var k=e.key;
    if(rej.classList.contains('visible')){if(k==='Escape'||k==='g'||k==='G')rejilla(false);return}
    
    
    if(k==='g'||k==='G'){rejilla(true);return}
    if(k==='ArrowRight'||k==='ArrowDown'||k===' '||k==='PageDown'||k==='Enter'){e.preventDefault();ir(cur+1)}
    else if(k==='ArrowLeft'||k==='ArrowUp'||k==='PageUp'||k==='Backspace'){e.preventDefault();ir(cur-1)}
    else if(k==='Home'){ir(0)}else if(k==='End'){ir(slides.length-1)}
    else if(k==='n'||k==='N'){notas()}
    else if(k==='f'||k==='F'){pantallaCompleta()}
  });
  document.addEventListener('click',function(e){
    var b=e.target.closest('.copiar');
    if(b&&!document.body.classList.contains('editando')){copiar(b);return}
    if(document.body.classList.contains('editando'))return;
    if(e.target.closest('a,button,#panel-notas,#barra-taller,#rejilla'))return;
    ir(e.clientX<innerWidth*0.15?cur-1:cur+1);
  });

  renumerar();
  escala();
  ir((parseInt(location.hash.slice(1),10)||1)-1);

  /* API para el editor; el editor solo carga si se abrió con "Editar taller.bat" */
  window.PRES={archivo:archivo,slides:function(){return slides},cur:function(){return cur},ir:ir,renumerar:renumerar,
    rejilla:rejilla,rej:rej,panel:panel,notas:notas,barra:barra};
  if(location.protocol.indexOf('http')===0){
    fetch('/api/ping').then(function(r){if(r.ok){var s=document.createElement('script');s.src='assets/editar.js';document.body.appendChild(s)}}).catch(function(){});
  }
})();
