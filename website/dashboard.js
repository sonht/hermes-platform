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
  await Promise.all([loadReports(),loadFaqCandidates()]);
}
async function loadReports(){
  const r=await fetch('/api/admin/reports',{credentials:'same-origin',cache:'no-store'});
  if(!r.ok)return;
  const body=await r.json(),tbody=document.getElementById('reports');tbody.replaceChildren();
  for(const item of body.rows){
    const tr=document.createElement('tr');
    for(const value of [item.day,item.app,labels[item.kind]||item.kind,item.summary,item.status]){
      const td=document.createElement('td');td.textContent=value;tr.append(td)
    }
    const td=document.createElement('td'),select=document.createElement('select');
    for(const [value,label] of [['new','Mới'],['reviewed','Đã xem'],['resolved','Đã xử lý']]){
      const option=document.createElement('option');option.value=value;option.textContent=label;select.append(option)
    }
    select.value=item.status;
    select.addEventListener('change',async()=>{
      select.disabled=true;
      try{
        const res=await fetch('/api/admin/report/status',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:item.id,status:select.value})});
        if(!res.ok)throw Error('Không cập nhật được trạng thái');
        await loadReports();
      }catch(err){alert(err.message);select.value=item.status}finally{select.disabled=false}
    });
    td.append(select);tr.append(td);tbody.append(tr)
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

async function loadFaqCandidates(){
  const r=await fetch('/api/admin/faq/candidates',{credentials:'same-origin',cache:'no-store'});
  if(!r.ok)return;
  const data=await r.json(),tbody=document.getElementById('faq-candidates');tbody.replaceChildren();
  for(const item of data.rows){
    const tr=document.createElement('tr');
    for(const value of [item.app,item.question,item.count,'Chờ biên tập']){
      const td=document.createElement('td');td.textContent=value;tr.append(td)
    }tbody.append(tr)
  }
}
