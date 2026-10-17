/* Hermes support widget v1: iframe isolation, no host DOM modification. */
(function(){
  'use strict';
  const script=document.currentScript;
  if(!script||document.getElementById('hermes-support-launcher'))return;
  const origin=new URL(script.src).origin;
  const app=script.getAttribute('data-app')||'nmprp';
  if(!/^[a-z][a-z0-9_-]{1,31}$/.test(app))return;
  const root=document.createElement('div');root.id='hermes-support-launcher';
  root.style.cssText='position:fixed;bottom:20px;right:20px;z-index:2147483000;font:14px system-ui';
  const shadow=root.attachShadow({mode:'closed'});
  const button=document.createElement('button');button.type='button';button.textContent='💬 Hỗ trợ';
  button.setAttribute('aria-label','Mở trợ lý hỗ trợ Hermes');
  button.style.cssText='border:0;border-radius:999px;padding:14px 20px;background:#2259bc;color:#fff;box-shadow:0 3px 14px #0004;cursor:pointer;font:600 14px system-ui';
  const frame=document.createElement('iframe');
  frame.title='Hermes Support';
  frame.src=origin+'/chat?app='+encodeURIComponent(app);
  frame.setAttribute('loading','lazy');
  frame.setAttribute('referrerpolicy','no-referrer');
  frame.style.cssText='display:none;width:min(380px,calc(100vw - 32px));height:min(560px,calc(100vh - 100px));border:1px solid #ddd;border-radius:16px;box-shadow:0 8px 30px #0003;background:#fff;margin-bottom:12px';
  button.addEventListener('click',()=>{
    const open=frame.style.display==='none';frame.style.display=open?'block':'none';
    button.textContent=open?'✕ Đóng hỗ trợ':'💬 Hỗ trợ';
    button.setAttribute('aria-expanded',String(open));
  });
  shadow.append(frame,button);document.body.append(root);
})();
