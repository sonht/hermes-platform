const login=document.getElementById('login'),panel=document.getElementById('panel'),error=document.getElementById('error');
const labels={faq:'FAQ',bug:'Bug',ux:'UX/UI',feature:'Yêu cầu tính năng',ai_quality:'Chất lượng AI'};
async function load(){
  const r=await fetch('/api/admin/summary',{credentials:'same-origin',cache:'no-store'});
  if(!r.ok){login.hidden=false;panel.hidden=true;return}
  const data=await r.json();login.hidden=true;panel.hidden=false;
  const totals=Object.fromEntries(Object.keys(labels).map(k=>[k,0]));
  for(const row of data.rows){if(row.kind in totals)totals[row.kind]+=row.count}
  const cards=document.getElementById('cards');cards.replaceChildren();
  for(const [kind,label] of Object.entries(labels)){
    const div=document.createElement('div');div.className='card';
    const title=document.createElement('strong');title.textContent=label;
    const value=document.createElement('div');value.className='number';value.textContent=totals[kind];
    div.append(title,value);cards.append(div)
  }
  const tbody=document.getElementById('rows');tbody.replaceChildren();
  for(const row of data.rows){
    const tr=document.createElement('tr');
    for(const value of [row.app,labels[row.kind]||row.kind,row.count]){
      const td=document.createElement('td');td.textContent=value;tr.append(td)
    }tbody.append(tr)
  }
}
document.getElementById('auth').addEventListener('submit',async e=>{
  e.preventDefault();error.textContent='';
  const password=document.getElementById('password').value;
  try{
    const r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({password})});
    document.getElementById('password').value='';
    if(!r.ok){const body=await r.json();throw Error(body.error||'Đăng nhập thất bại')}
    await load();
  }catch(err){error.textContent=err.message}
});
load().catch(()=>{error.textContent='Chưa kết nối được hệ thống thống kê.'});
