<!-- Lightbox viewer for lightbox.html. Two trigger kinds (both open the same popup):
       · data-lb="<img-url>"      → opens an image fit-to-screen (Mode A / Figma export)
       · data-lb-stage="<sel>"    → clones a .sb-stage (replica markup or wireframe) — works
                                     when there is no exported image (Mode B, or app-CSS replica)
     optional data-title on either. Zoom = wheel + buttons; drag to pan; Esc/✕/backdrop close.
     Include once per page. -->
<script>
(function(){
  var lb=document.getElementById('sbLb'); if(!lb)return;
  var zoom=document.getElementById('sbLbZoom'),
      stage=document.getElementById('sbLbStage')||zoom.querySelector('.sb-stage'),
      title=document.getElementById('sbLbTitle'), lvl=lb.querySelector('.zlvl');
  var IMG='<img id="sbLbImg" alt="원본 화면" draggable="false" />';
  var mode='img', z=1,fit=1,tx=0,ty=0,drag=false,sx=0,sy=0,btx=0,bty=0;
  function apply(){stage.style.transform='translate('+tx+'px,'+ty+'px) scale('+z+')';
    if(lvl)lvl.textContent=Math.round(z/fit*100)+'%';}
  function fitNow(){var r=zoom.getBoundingClientRect(),w,h;
    if(mode==='img'){var img=document.getElementById('sbLbImg');w=(img&&img.naturalWidth)||1;h=(img&&img.naturalHeight)||1;}
    else{w=stage.offsetWidth||1;h=stage.offsetHeight||1;}
    fit=Math.min(r.width/w, r.height/h)||1; z=fit; tx=(r.width-w*z)/2; ty=(r.height-h*z)/2; apply();}
  function openImg(src,t){mode='img'; stage.style.position=''; stage.style.background=''; stage.style.padding='';
    stage.innerHTML=IMG; var img=document.getElementById('sbLbImg'); title.textContent=t||''; lb.hidden=false;
    if(img.complete&&img.naturalWidth)fitNow(); else img.onload=fitNow; img.src=src;}
  function openStage(sel,t){mode='stage'; var s=document.querySelector(sel||'.sb-screen .sb-stage');
    stage.style.position='absolute'; stage.style.top='0'; stage.style.left='0';
    stage.style.background='#fff'; stage.style.padding='18px';
    stage.innerHTML=s?s.innerHTML:''; title.textContent=t||'원본 보기'; lb.hidden=false; requestAnimationFrame(fitNow);}
  function close(){lb.hidden=true; stage.innerHTML='';}
  function zoomAt(cx,cy,nz){var mn=fit*0.5,mx=Math.max(1,fit)*8; nz=Math.max(mn,Math.min(mx,nz));
    var r=zoom.getBoundingClientRect(),ox=cx-r.left,oy=cy-r.top;
    tx=ox-(ox-tx)*(nz/z); ty=oy-(oy-ty)*(nz/z); z=nz; apply();}
  document.querySelectorAll('[data-lb]').forEach(function(b){b.addEventListener('click',function(e){
    e.preventDefault(); openImg(b.getAttribute('data-lb'), b.getAttribute('data-title'));});});
  document.querySelectorAll('[data-lb-stage]').forEach(function(b){b.addEventListener('click',function(e){
    e.preventDefault(); openStage(b.getAttribute('data-lb-stage'), b.getAttribute('data-title'));});});
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
