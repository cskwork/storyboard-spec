<!-- Lightbox viewer logic for lightbox.html. Any element with data-lb="<img-url>"
     (and optional data-title) opens the popup; the image opens fit-to-screen, then
     wheel/buttons/drag zoom from there. Esc / ✕ / backdrop close. Include once per page. -->
<script>
(function(){
  var lb=document.getElementById('sbLb'); if(!lb)return;
  var img=document.getElementById('sbLbImg'), zoom=document.getElementById('sbLbZoom'),
      stage=zoom.querySelector('.sb-stage'), title=document.getElementById('sbLbTitle'),
      lvl=lb.querySelector('.zlvl');
  var z=1,fit=1,tx=0,ty=0,drag=false,sx=0,sy=0,btx=0,bty=0;
  function apply(){stage.style.transform='translate('+tx+'px,'+ty+'px) scale('+z+')';
    if(lvl)lvl.textContent=Math.round(z/fit*100)+'%';}
  function fitNow(){var r=zoom.getBoundingClientRect();
    fit=Math.min(r.width/(img.naturalWidth||1), r.height/(img.naturalHeight||1))||1; z=fit;
    tx=(r.width-img.naturalWidth*z)/2; ty=(r.height-img.naturalHeight*z)/2; apply();}
  function open(src,t){img.src=src; title.textContent=t||''; lb.hidden=false;
    if(img.complete&&img.naturalWidth)fitNow(); else img.onload=fitNow;}
  function close(){lb.hidden=true; img.removeAttribute('src');}
  function zoomAt(cx,cy,nz){var mn=fit*0.5,mx=Math.max(1,fit)*8; nz=Math.max(mn,Math.min(mx,nz));
    var r=zoom.getBoundingClientRect(),ox=cx-r.left,oy=cy-r.top;
    tx=ox-(ox-tx)*(nz/z); ty=oy-(oy-ty)*(nz/z); z=nz; apply();}
  document.querySelectorAll('[data-lb]').forEach(function(b){b.addEventListener('click',function(e){
    e.preventDefault(); open(b.getAttribute('data-lb'), b.getAttribute('data-title'));});});
  lb.querySelectorAll('[data-lbclose]').forEach(function(b){b.addEventListener('click',close);});
  lb.addEventListener('click',function(e){if(e.target===lb)close();});
  document.addEventListener('keydown',function(e){if(!lb.hidden&&e.key==='Escape')close();});
  zoom.addEventListener('wheel',function(e){e.preventDefault();
    zoomAt(e.clientX,e.clientY,z*(e.deltaY<0?1.15:1/1.15));},{passive:false});
  zoom.addEventListener('pointerdown',function(e){drag=true;zoom.classList.add('dragging');
    sx=e.clientX;sy=e.clientY;btx=tx;bty=ty;try{zoom.setPointerCapture(e.pointerId)}catch(_){}});
  zoom.addEventListener('pointermove',function(e){if(!drag)return;tx=btx+(e.clientX-sx);ty=bty+(e.clientY-sy);apply();});
  function end(){drag=false;zoom.classList.remove('dragging');}
  zoom.addEventListener('pointerup',end); zoom.addEventListener('pointercancel',end);
  lb.querySelectorAll('[data-z]').forEach(function(b){b.addEventListener('click',function(){
    var r=zoom.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,a=b.dataset.z;
    if(a==='in')zoomAt(cx,cy,z*1.3); else if(a==='out')zoomAt(cx,cy,z/1.3); else fitNow();});});
  window.addEventListener('resize',function(){if(!lb.hidden)fitNow();});
})();
</script>
