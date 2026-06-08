<!-- Shared settings logic for settings-control.html. Applies --sb-fz (reading-text
     scale) and --sb-cue-op (callout opacity) from localStorage BEFORE paint, wires
     the buttons + slider, and live-syncs across open tabs via the `storage` event.
     Include once per page, after the control markup. -->
<script>
(function(){
  var r=document.documentElement, FZ='sbFz', OP='sbCueOp', STEPS=[1,1.12,1.26,1.42];
  function cl(i){i=parseInt(i,10)||0;return Math.max(0,Math.min(STEPS.length-1,i));}
  function getFz(){try{return cl(localStorage.getItem(FZ))}catch(e){return 0}}
  function getOp(){try{var v=parseInt(localStorage.getItem(OP),10);return (v>=20&&v<=100)?v:60}catch(e){return 60}}
  function applyFz(i){r.style.setProperty('--sb-fz',STEPS[cl(i)]);}
  function applyOp(v){r.style.setProperty('--sb-cue-op',(v/100).toFixed(2));}
  applyFz(getFz()); applyOp(getOp());           /* before paint — no flash */
  function wire(){
    var fi=getFz();
    document.querySelectorAll('[data-fz]').forEach(function(b){b.addEventListener('click',function(){
      var a=b.dataset.fz; fi=(a==='inc')?cl(fi+1):(a==='dec')?cl(fi-1):0;
      applyFz(fi); try{localStorage.setItem(FZ,fi)}catch(e){}});});
    var s=document.querySelector('[data-op]');
    if(s){s.value=getOp(); s.addEventListener('input',function(){
      applyOp(s.value); try{localStorage.setItem(OP,s.value)}catch(e){}});}
  }
  if(document.readyState!=='loading')wire();else document.addEventListener('DOMContentLoaded',wire);
  window.addEventListener('storage',function(e){    /* change on one page -> all open tabs */
    if(e.key===FZ)applyFz(getFz());
    if(e.key===OP){applyOp(getOp()); var s=document.querySelector('[data-op]'); if(s)s.value=getOp();}});
})();
</script>
