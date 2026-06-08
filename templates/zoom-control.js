<!-- Screen zoom/pan for every .sb-zoom on the page: wheel-zoom (centered on the
     cursor), +/−/맞춤 buttons, drag-to-pan, double-click reset. The matching
     buttons (.sb-zoomctl [data-z], .zlvl) live in the screen pane's caption.
     Include once per page. Pairs with the .sb-zoom / .sb-stage CSS. -->
<script>
(function(){
  function init(box){
    var stage=box.querySelector('.sb-stage'); if(!stage)return;
    var pane=box.closest('.sb-screenpane')||box.parentNode;
    var z=1,tx=0,ty=0,MIN=1,MAX=6,drag=false,sx=0,sy=0,btx=0,bty=0;
    var lbl=pane.querySelector('.zlvl');
    function clamp(){var r=box.getBoundingClientRect(),w=stage.offsetWidth*z,h=stage.offsetHeight*z;
      tx=Math.max(Math.min(0,r.width-w),Math.min(0,tx)); ty=Math.max(Math.min(0,r.height-h),Math.min(0,ty));}
    function apply(){clamp(); stage.style.transform='translate('+tx+'px,'+ty+'px) scale('+z+')';
      box.classList.toggle('zoomed',z>1); if(lbl)lbl.textContent=Math.round(z*100)+'%';}
    function zoomAt(cx,cy,nz){nz=Math.max(MIN,Math.min(MAX,nz)); var r=box.getBoundingClientRect(),
      ox=cx-r.left,oy=cy-r.top; tx=ox-(ox-tx)*(nz/z); ty=oy-(oy-ty)*(nz/z); z=nz; apply();}
    function reset(){z=1;tx=0;ty=0;apply();}
    box.addEventListener('wheel',function(e){e.preventDefault();
      zoomAt(e.clientX,e.clientY,z*(e.deltaY<0?1.15:1/1.15));},{passive:false});
    box.addEventListener('pointerdown',function(e){if(z<=1)return; drag=true; box.classList.add('dragging');
      sx=e.clientX;sy=e.clientY;btx=tx;bty=ty; try{box.setPointerCapture(e.pointerId)}catch(_){}});
    box.addEventListener('pointermove',function(e){if(!drag)return; tx=btx+(e.clientX-sx); ty=bty+(e.clientY-sy); apply();});
    function end(){drag=false; box.classList.remove('dragging');}
    box.addEventListener('pointerup',end); box.addEventListener('pointercancel',end);
    box.addEventListener('dblclick',function(e){e.preventDefault(); reset();});
    pane.querySelectorAll('[data-z]').forEach(function(b){b.addEventListener('click',function(){
      var r=box.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,a=b.dataset.z;
      if(a==='in')zoomAt(cx,cy,z*1.3); else if(a==='out')zoomAt(cx,cy,z/1.3); else reset();});});
    apply();
  }
  function boot(){document.querySelectorAll('.sb-zoom').forEach(init);}
  if(document.readyState!=='loading')boot();else document.addEventListener('DOMContentLoaded',boot);
})();
</script>
