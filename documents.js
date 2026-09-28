(() => {
'use strict';
const DEFAULT_LOGO = '__DEFAULT_LOGO_DATA_URL__';
const $ = (s, root=document) => root.querySelector(s);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const displayText = value => escapeHtml(value).replace(/\n/g, '<br>');
const localDate = () => { const d=new Date(); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); };
const currentMonth = () => localDate().slice(0,7).replace('-','/');
const docLabels = {procuration:'Procuration',diagnostic:'Diagnostic terrain',orientation:'Orientation support'};
const spaceNames = ['Comptabilité','Direction','Préfecture','Professeur','Titulaire','Parental','Promoteur'];
const defaultCommon = {company:'NETUBEX SARL',department:'Département Administratif',city:'Kasumbalesa, République Démocratique du Congo',address:'',phone:'',email:'',logo:DEFAULT_LOGO};
const commonKey='netubex_documents_common_v1';
const storageKey=type=>'netubex_documents_'+type+'_v1';
const counterKey=type=>'netubex_documents_seq_'+type+'_'+currentMonth().replace('/','_');
let active='procuration', common=load(commonKey,defaultCommon), currentDoc=null, toastTimer=null;
function storageGet(key){try{return window.localStorage.getItem(key)}catch{return null}}
function storageSet(key,value){try{window.localStorage.setItem(key,value);return true}catch{return false}}
function load(key,fallback){try{return {...fallback,...JSON.parse(storageGet(key)||'{}')}}catch{return {...fallback}}}
function nextReference(type){const n=Number(storageGet(counterKey(type))||1);const code=type==='procuration'?'PRO':type==='diagnostic'?'DIAG':'ORI';return 'NTX/ADM/'+code+'/'+currentMonth()+'/'+String(n).padStart(3,'0')}
function defaults(type){
 const today=localDate();
 if(type==='procuration')return {reference:nextReference(type),generated:false,signer:'Makangila Kiema Dieu Merci',signerRole:'Chef de Département',delegates:[{name:'',role:'Délégué(e) / Chargé(e) de mission'}],locations:'',mission:'Effectuer la visite d’orientation, de prise de contact et de suivi de terrain prévue ce mercredi 23 septembre 2026, à compter de 09h30.',missionDate:'2026-09-23',missionTime:'09:30',writtenDate:today};
 if(type==='diagnostic')return {reference:nextReference(type),generated:false,visitDate:today,startTime:'09:00',endTime:'10:00',school:'',schoolAddress:'',contactPerson:'',contactRole:'',contact:'',agent:'',objective:'Effectuer la collecte des données, le diagnostic technique et fonctionnel, ainsi que le suivi de terrain.',spaces:Object.fromEntries(spaceNames.map(n=>[n,{state:'Bon',observations:'',problems:''}])),frequentErrors:'',technicalProblems:'',usageProblems:'',recommendations:'',technicalHandoff:'',actions:'',summary:'',agentValidator:'',schoolValidator:'',validationDate:today};
 return {reference:nextReference(type),generated:false,orientationDate:today,time:'09:00',school:'',agent:'',userName:'',userRole:'',userContact:'',workspace:'',reason:'Nouvelle utilisation',reasonDetail:'',difficulty:'',space:'Comptabilité',proposedOrientation:'',instructions:'',recommendedSupport:'',followupDate:'',followupOwner:'',followupMode:'présentiel',observations:'',agentValidator:'',userValidator:'',validationDate:today}
}
function loadDoc(type){const base=defaults(type), saved=load(storageKey(type),{});const merged={...base,...saved};if(type==='diagnostic')merged.spaces={...base.spaces,...(saved.spaces||{})};if(type==='procuration'&&!Array.isArray(merged.delegates))merged.delegates=base.delegates;return merged}
function saveCommon(){if(!storageSet(commonKey,JSON.stringify(common)))showToast('Le navigateur bloque le stockage local. Le logo et les coordonnées ne pourront pas être conservés après fermeture.')}
function saveDoc(){if(!storageSet(storageKey(active),JSON.stringify(currentDoc)))showToast('Le navigateur bloque le stockage local. Les données ne pourront pas être conservées après fermeture.')}
function field(label,key,value='',type='text',options=null,full=false,isCommon=false){
 const cls=full?'field full':'field', attr=isCommon?'data-common="'+key+'"':'data-key="'+key+'"';
 let control='';
 if(type==='textarea')control='<textarea '+attr+' rows="3">'+escapeHtml(value)+'</textarea>';
 else if(type==='select')control='<select '+attr+'>'+options.map(v=>'<option value="'+escapeHtml(v)+'" '+(v===value?'selected':'')+'>'+escapeHtml(v)+'</option>').join('')+'</select>';
 else control='<input '+attr+' type="'+type+'" value="'+escapeHtml(value)+'">';
 return '<label class="'+cls+'">'+label+control+'</label>';
}
function group(title,fields,open=false){return '<details '+(open?'open':'')+'><summary>'+title+'</summary><div class="fields">'+fields+'</div></details>'}
function commonFields(){return '<label class="field full">Logo NETUBEX SARL<input id="logoUpload" type="file" accept="image/*"><span class="hint">Choisissez une image. Elle sera réduite puis conservée sur cet appareil.</span></label>'+field('Nom de la société','company',common.company,'text',null,false,true)+field('Département','department',common.department,'text',null,false,true)+field('Ville / siège','city',common.city,'text',null,true,true)+field('Adresse complète','address',common.address,'text',null,true,true)+field('Téléphone','phone',common.phone,'tel',null,false,true)+field('Email','email',common.email,'email',null,false,true)}
function proGroups(){
 const delegates=(currentDoc.delegates||[]).map((d,i)=>'<div class="delegate-form"><label class="field">Nom complet<input data-delegate="'+i+'" data-part="name" value="'+escapeHtml(d.name)+'"></label><label class="field">Rôle<input data-delegate="'+i+'" data-part="role" value="'+escapeHtml(d.role)+'"></label><button class="btn btn-light remove-delegate" type="button" data-remove="'+i+'">Supprimer</button></div>').join('');
 return group('1. Référence',field('Numéro de référence','reference',currentDoc.reference,'text',null,true))+group('2. Délégués / chargés de mission',delegates+'<button class="btn btn-add" id="addDelegate" type="button">+ Ajouter un délégué</button>')+group('3. Mission',field('Lieu(x) de mission (un lieu par ligne)','locations',currentDoc.locations,'textarea',null,true)+field('Objet de la mission','mission',currentDoc.mission,'textarea',null,true)+field('Date de la mission','missionDate',currentDoc.missionDate,'date')+field('Heure de la mission','missionTime',currentDoc.missionTime,'time')+field('Date de rédaction / Fait à','writtenDate',currentDoc.writtenDate,'date'))+group('4. Signataire',field('Nom du signataire','signer',currentDoc.signer)+field('Fonction du signataire','signerRole',currentDoc.signerRole));
}
function diagnosticGroups(){
 const spaces=spaceNames.map((name,i)=>{const v=currentDoc.spaces?.[name]||{state:'Bon',observations:'',problems:''};return group('3.'+(i+1)+' '+name,field('État','spaceState_'+i,v.state,'select',['Bon','Moyen','À améliorer','Critique'])+field('Observations','spaceObs_'+i,v.observations,'textarea',null,true)+field('Problèmes constatés','spaceProblems_'+i,v.problems,'textarea',null,true))}).join('');
 return group('1. Informations générales',field('Date de la visite','visitDate',currentDoc.visitDate,'date')+field('Heure de début','startTime',currentDoc.startTime,'time')+field('Heure de fin','endTime',currentDoc.endTime,'time')+field('Nom de l’établissement','school',currentDoc.school)+field('Adresse de l’établissement','schoolAddress',currentDoc.schoolAddress,'text',null,true)+field('Personne rencontrée','contactPerson',currentDoc.contactPerson)+field('Fonction','contactRole',currentDoc.contactRole)+field('Contact (téléphone / email)','contact',currentDoc.contact)+field('Agent NETUBEX en charge','agent',currentDoc.agent),true)+group('2. Objectif de la visite',field('Objectif','objective',currentDoc.objective,'textarea',null,true))+group('3. Diagnostic par espace',spaces)+group('4. Erreurs fréquentes constatées',field('Erreurs fréquentes','frequentErrors',currentDoc.frequentErrors,'textarea',null,true))+group('5. Problèmes techniques',field('Problèmes techniques','technicalProblems',currentDoc.technicalProblems,'textarea',null,true))+group('6. Problèmes liés à l’utilisation',field('Problèmes d’utilisation','usageProblems',currentDoc.usageProblems,'textarea',null,true))+group('7. Recommandations du support',field('Recommandations','recommendations',currentDoc.recommendations,'textarea',null,true))+group('8. Points à transmettre à l’équipe technique',field('Transmission technique','technicalHandoff',currentDoc.technicalHandoff,'textarea',null,true))+group('9. Actions réalisées sur place',field('Actions réalisées','actions',currentDoc.actions,'textarea',null,true))+group('10. Synthèse de la visite',field('Synthèse','summary',currentDoc.summary,'textarea',null,true))+group('11. Validation et signatures',field('Agent NETUBEX : nom et fonction','agentValidator',currentDoc.agentValidator)+field('Responsable établissement : nom et fonction','schoolValidator',currentDoc.schoolValidator)+field('Date de validation','validationDate',currentDoc.validationDate,'date'));
}
function orientationGroups(){
 return group('1. Informations générales',field('Date de l’orientation','orientationDate',currentDoc.orientationDate,'date')+field('Heure','time',currentDoc.time,'time')+field('Établissement','school',currentDoc.school)+field('Agent NETUBEX','agent',currentDoc.agent),true)+group('2. Identification de l’utilisateur',field('Nom complet','userName',currentDoc.userName)+field('Fonction / rôle','userRole',currentDoc.userRole)+field('Contact','userContact',currentDoc.userContact)+field('Espace de travail','workspace',currentDoc.workspace))+group('3. Motif de l’orientation',field('Motif','reason',currentDoc.reason,'select',['Nouvelle utilisation','Problème technique','Demande de formation','Réorientation','Autre'])+field('Précision','reasonDetail',currentDoc.reasonDetail,'textarea',null,true))+group('4. Difficulté ou besoin identifié',field('Difficulté / besoin','difficulty',currentDoc.difficulty,'textarea',null,true))+group('5. Espace concerné',field('Espace','space',currentDoc.space,'select',spaceNames))+group('6. Orientation proposée',field('Orientation','proposedOrientation',currentDoc.proposedOrientation,'textarea',null,true))+group('7. Instructions à suivre',field('Une instruction par ligne','instructions',currentDoc.instructions,'textarea',null,true))+group('8. Accompagnement recommandé',field('Accompagnement','recommendedSupport',currentDoc.recommendedSupport,'textarea',null,true))+group('9. Suivi de l’utilisateur',field('Date de suivi prévue','followupDate',currentDoc.followupDate,'date')+field('Responsable du suivi','followupOwner',currentDoc.followupOwner)+field('Modalité','followupMode',currentDoc.followupMode,'select',['présentiel','téléphone','email','à distance']))+group('10. Observations',field('Observations','observations',currentDoc.observations,'textarea',null,true))+group('11. Validation et signatures',field('Agent NETUBEX : nom et fonction','agentValidator',currentDoc.agentValidator)+field('Utilisateur : nom et fonction','userValidator',currentDoc.userValidator)+field('Date de validation','validationDate',currentDoc.validationDate,'date'));
}
function renderForm(){
 const title=docLabels[active], groups=active==='procuration'?proGroups():active==='diagnostic'?diagnosticGroups():orientationGroups();
 $('#formHost').innerHTML='<div class="form-top"><h2>'+title+'</h2><p>Complétez les sections. L’aperçu se met à jour automatiquement.</p><span class="ref-pill">'+escapeHtml(currentDoc.reference)+'</span></div><div class="form-content">'+group('En-tête et coordonnées NETUBEX SARL',commonFields(),true)+groups+'<div class="form-actions"><button class="btn btn-light" id="resetForm" type="button">Réinitialiser le formulaire</button><button class="btn btn-primary" id="generateDoc" type="button" '+(currentDoc.generated?'disabled':'')+'>'+(currentDoc.generated?'Référence réservée':'Générer le document')+'</button></div><p class="hint">Les données de chaque document sont enregistrées dans le stockage local de ce navigateur.</p></div>';
 bindForm();
}
function value(key){return currentDoc[key]||''}
function prettyDate(value){if(!value)return '';const d=new Date(value+'T00:00:00');return Number.isNaN(d.getTime())?value:d.toLocaleDateString('fr-FR',{day:'2-digit',month:'2-digit',year:'numeric'})}
function shown(value){return value&&String(value).trim()?displayText(value):'<span class="empty-value">À compléter</span>'}
function section(title,content){return '<section class="doc-section"><div class="doc-section-title">'+title+'</div><div>'+content+'</div></section>'}
function labeled(label,v){return '<p><b>'+label+' :</b> '+shown(v)+'</p>'}
function signature(name,label){return '<div class="signature-box"><div class="signature-name">'+shown(name)+'</div><div class="signature-line">'+label+'</div></div>'}
function commonHeader(){
 const logo=common.logo||DEFAULT_LOGO;
 return '<div class="letterhead"><img src="'+escapeHtml(logo)+'" alt="Logo"><div><b>'+shown(common.company)+'</b><br>'+shown(common.department)+'<br>'+shown(common.city)+'</div></div>';
}
function commonFooter(){
 const contact=[common.address,common.phone,common.email].filter(Boolean).map(escapeHtml).join(' &nbsp;•&nbsp; ');
 return '<footer class="paper-footer"><div class="footer-rule"></div><div class="footer-contact">'+(contact||'Adresse • Téléphone • Email')+'</div><div class="refline"><span>Réf. : '+escapeHtml(value('reference'))+'</span><span class="preview-page-count">Page 1 / 1</span></div></footer>';
}
function proPreview(){
 const delegates=(currentDoc.delegates||[]).filter(d=>String(d.name||'').trim());
 const delegateText=delegates.length?'<ul>'+delegates.map(d=>'<li><b>'+shown(d.name)+'</b>'+(String(d.role||'').trim()?' — '+shown(d.role):'')+'</li>').join('')+'</ul>':'';
 const places=value('locations').split(/\n/).map(s=>s.trim()).filter(Boolean);
 return '<div class="doc-kicker">PROCURATION N° '+escapeHtml(value('reference'))+'</div><h2 class="doc-title">MANDAT DE REPRÉSENTATION</h2><p>Je soussigné(e), <b>'+shown(value('signer'))+'</b>, agissant en qualité de <b>'+shown(value('signerRole'))+'</b> pour '+shown(common.company)+', donne par la présente mandat aux personnes désignées ci-dessous :</p>'+delegateText+'<p>À l’effet de représenter '+shown(common.company)+' dans le cadre de la mission suivante :</p>'+section('OBJET DE LA MISSION','<p>'+shown(value('mission'))+'</p>')+section('LIEU(X) DE LA MISSION',places.length?'<ul>'+places.map(p=>'<li>'+shown(p)+'</li>').join('')+'</ul>':'<p>'+shown('')+'</p>')+'<div class="doc-meta"><span>Date : '+shown(prettyDate(value('missionDate')))+' • Heure : '+shown(value('missionTime'))+'</span></div><p>Le présent mandat est établi pour servir et valoir ce que de droit, dans le cadre de la mission indiquée ci-dessus.</p><div class="signature-grid">'+signature((delegates[0]&&delegates[0].name)||'','Le / la mandataire')+signature(value('signer'),'Le mandant — '+escapeHtml(value('signerRole')))+' </div><p class="place-date">Fait à '+shown(common.city)+' , le '+shown(prettyDate(value('writtenDate')))+'.</p>';
}
function diagPreview(){
 let html='<div class="doc-kicker">FICHE DE COLLECTE ET DIAGNOSTIC TERRAIN</div><h2 class="doc-title">DIAGNOSTIC TERRAIN</h2>'+section('1. INFORMATIONS GÉNÉRALES','<div class="doc-meta"><span>Date : '+shown(prettyDate(value('visitDate')))+' • '+shown(value('startTime'))+' – '+shown(value('endTime'))+'</span></div>'+labeled('Établissement',value('school'))+labeled('Adresse',value('schoolAddress'))+labeled('Personne rencontrée',value('contactPerson'))+labeled('Fonction',value('contactRole'))+labeled('Contact',value('contact'))+labeled('Agent NETUBEX',value('agent')))+section('2. OBJECTIF DE LA VISITE','<p>'+shown(value('objective'))+'</p>')+'<section class="doc-section"><div class="doc-section-title">3. DIAGNOSTIC PAR ESPACE</div>';
 spaceNames.forEach((name,i)=>{const s=currentDoc.spaces?.[name]||{};html+='<div class="space-block"><div class="space-title">3.'+(i+1)+' '+escapeHtml(name)+' — État : '+shown(s.state)+'</div><p><b>Observations :</b> '+shown(s.observations)+'</p><p><b>Problèmes constatés :</b> '+shown(s.problems)+'</p></div>'});
 html+='</section>'+section('4. ERREURS FRÉQUENTES CONSTATÉES','<p>'+shown(value('frequentErrors'))+'</p>')+section('5. PROBLÈMES TECHNIQUES','<p>'+shown(value('technicalProblems'))+'</p>')+section('6. PROBLÈMES LIÉS À L’UTILISATION','<p>'+shown(value('usageProblems'))+'</p>')+section('7. RECOMMANDATIONS DU SUPPORT','<p>'+shown(value('recommendations'))+'</p>')+section('8. POINTS À TRANSMETTRE À L’ÉQUIPE TECHNIQUE','<p>'+shown(value('technicalHandoff'))+'</p>')+section('9. ACTIONS RÉALISÉES SUR PLACE','<p>'+shown(value('actions'))+'</p>')+section('10. SYNTHÈSE DE LA VISITE','<p>'+shown(value('summary'))+'</p>')+section('11. VALIDATION ET SIGNATURES','<p>Date de validation : '+shown(prettyDate(value('validationDate')))+'</p><div class="signature-grid">'+signature(value('agentValidator'),'Agent NETUBEX')+signature(value('schoolValidator'),'Responsable de l’établissement')+'</div>');
 return html;
}
function orientationPreview(){
 let instructions=value('instructions').split(/\n/).map(s=>s.trim()).filter(Boolean), list=instructions.length?'<ol>'+instructions.map(s=>'<li>'+shown(s)+'</li>').join('')+'</ol>':'<p>'+shown('')+'</p>';
 return '<div class="doc-kicker">FICHE D’ORIENTATION DES UTILISATEURS — SUPPORT</div><h2 class="doc-title">ORIENTATION SUPPORT</h2>'+section('1. INFORMATIONS GÉNÉRALES','<div class="doc-meta"><span>Date : '+shown(prettyDate(value('orientationDate')))+' • Heure : '+shown(value('time'))+'</span></div>'+labeled('Établissement',value('school'))+labeled('Agent NETUBEX',value('agent')))+section('2. IDENTIFICATION DE L’UTILISATEUR',labeled('Nom complet',value('userName'))+labeled('Fonction / rôle',value('userRole'))+labeled('Contact',value('userContact'))+labeled('Espace de travail',value('workspace')))+section('3. MOTIF DE L’ORIENTATION',labeled('Motif',value('reason'))+labeled('Précision',value('reasonDetail')))+section('4. DIFFICULTÉ OU BESOIN IDENTIFIÉ','<p>'+shown(value('difficulty'))+'</p>')+section('5. ESPACE CONCERNÉ','<p>'+shown(value('space'))+'</p>')+section('6. ORIENTATION PROPOSÉE','<p>'+shown(value('proposedOrientation'))+'</p>')+section('7. INSTRUCTIONS À SUIVRE',list)+section('8. ACCOMPAGNEMENT RECOMMANDÉ','<p>'+shown(value('recommendedSupport'))+'</p>')+section('9. SUIVI DE L’UTILISATEUR',labeled('Date de suivi prévue',prettyDate(value('followupDate')))+labeled('Responsable du suivi',value('followupOwner'))+labeled('Modalité',value('followupMode')))+section('10. OBSERVATIONS','<p>'+shown(value('observations'))+'</p>')+section('11. VALIDATION ET SIGNATURES','<p>Date de validation : '+shown(prettyDate(value('validationDate')))+'</p><div class="signature-grid">'+signature(value('agentValidator'),'Agent NETUBEX')+signature(value('userValidator'),'Utilisateur')+'</div>');
}
function renderPreview(){
 const body=active==='procuration'?proPreview():active==='diagnostic'?diagPreview():orientationPreview();
 const paper=$('#paper');
 paper.innerHTML=commonHeader()+body+commonFooter();
 const logo=$('#brandLogo');if(logo)logo.src=common.logo||DEFAULT_LOGO;
 requestAnimationFrame(()=>{const footer=paper.querySelector('.paper-footer'),style=getComputedStyle(paper);const footerTop=footer?footer.getBoundingClientRect().top-paper.getBoundingClientRect().top:0;const contentHeight=Math.max(1,footerTop-parseFloat(style.paddingTop||0));const pageHeight=257*96/25.4;const pages=Math.max(1,Math.ceil((contentHeight-1)/pageHeight));const count=paper.querySelector('.preview-page-count');if(count)count.textContent='Page 1 / '+pages;});
}
function updatePreviewAndStorage(){saveDoc();renderPreview()}
function bindForm(){
 const host=$('#formHost');
 host.oninput=e=>{const t=e.target;if(t.dataset.common){common[t.dataset.common]=t.value;saveCommon();renderPreview();return}
  if(t.dataset.delegate!==undefined){const i=Number(t.dataset.delegate),part=t.dataset.part;currentDoc.delegates[i][part]=t.value;saveDoc();renderPreview();return}
  if(t.dataset.key){const key=t.dataset.key;if(key.startsWith('spaceState_')||key.startsWith('spaceObs_')||key.startsWith('spaceProblems_')){const bits=key.split('_'),i=Number(bits[1]),name=spaceNames[i];if(!currentDoc.spaces[name])currentDoc.spaces[name]={};currentDoc.spaces[name][key.startsWith('spaceState_')?'state':key.startsWith('spaceObs_')?'observations':'problems']=t.value}else currentDoc[key]=t.value;saveDoc();renderPreview();}
 };
 host.onchange=e=>{if(e.target.matches('select,input[type="date"],input[type="time"]'))e.target.dispatchEvent(new Event('input',{bubbles:true}))};
 host.onclick=e=>{
  const remove=e.target.closest('[data-remove]');if(remove){currentDoc.delegates.splice(Number(remove.dataset.remove),1);saveDoc();renderForm();renderPreview();return}
  if(e.target.id==='addDelegate'){currentDoc.delegates.push({name:'',role:'Délégué(e) / Chargé(e) de mission'});saveDoc();renderForm();renderPreview();return}
  if(e.target.id==='resetForm'){resetDocument();return}
  if(e.target.id==='generateDoc'){reserveReference();return}
 };
 const upload=$('#logoUpload');if(upload)upload.onchange=handleLogoUpload;
}
function showToast(message){const el=$('#toast');if(!el)return;el.textContent=message;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),3400)}
function resetDocument(){currentDoc=defaults(active);saveDoc();renderForm();renderPreview();showToast('Le formulaire a été réinitialisé.')}
function reserveReference(){
 if(currentDoc.generated){showToast('Cette référence a déjà été réservée.');return}
 const n=Number(storageGet(counterKey(active))||1);storageSet(counterKey(active),String(n+1));currentDoc.generated=true;currentDoc.generatedAt=new Date().toISOString();saveDoc();renderForm();renderPreview();showToast('Document généré. La référence est réservée.');
}
function handleLogoUpload(e){
 const file=e.target.files&&e.target.files[0];if(!file)return;
 if(!file.type.startsWith('image/')){showToast('Choisissez un fichier image.');return}
 if(file.size>8*1024*1024){showToast('L’image doit faire moins de 8 Mo.');return}
 const reader=new FileReader();
 reader.onerror=()=>showToast('Impossible de lire cette image.');
 reader.onload=()=>{const img=new Image();img.onerror=()=>showToast('Ce format d’image ne peut pas être utilisé.');
  img.onload=()=>{const maxW=900,maxH=500,ratio=Math.min(1,maxW/img.width,maxH/img.height),w=Math.max(1,Math.round(img.width*ratio)),h=Math.max(1,Math.round(img.height*ratio)),canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;const ctx=canvas.getContext('2d');ctx.fillStyle='#ffffff';ctx.fillRect(0,0,w,h);ctx.drawImage(img,0,0,w,h);common.logo=canvas.toDataURL('image/jpeg',0.82);saveCommon();renderPreview();showToast('Logo enregistré sur cet appareil.');};
  img.src=reader.result;
 };
 reader.readAsDataURL(file);
}
async function exportPdf(){
 if(!window.html2canvas||!window.jspdf||typeof window.jspdf.jsPDF!=='function'){showToast('La biblioth\u00e8que PDF n\u2019est pas disponible. Utilisez le bouton Imprimer.');return}
 const button=$('#exportPdf');button.disabled=true;button.innerHTML='<span>\u23f3</span> G\u00e9n\u00e9ration\u2026';
 let clone,holder;
 try{
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  const paper=$('#paper');
  const pdfFooter=paper.querySelector('.paper-footer');if(pdfFooter)pdfFooter.remove();
  clone=paper.cloneNode(true);if(pdfFooter)paper.appendChild(pdfFooter);
  clone.id='pdfCapture';
  clone.style.cssText='position:relative;width:170mm;min-height:0;height:auto;padding:0;margin:0;box-shadow:none;overflow:visible;background:#fff;color:#111;font-family:"Times New Roman",Georgia,serif;';
  holder=document.createElement('div');
  holder.style.cssText='position:fixed;left:-9999px;top:0;width:170mm;background:#fff;z-index:-1;';
  holder.appendChild(clone);document.body.appendChild(holder);
  clone.querySelectorAll('.empty-value').forEach(n=>n.remove());
  const canvas=await window.html2canvas(clone,{scale:2,backgroundColor:'#ffffff',useCORS:true,logging:false,windowWidth:642});
  const pdf=new window.jspdf.jsPDF({orientation:'portrait',unit:'mm',format:'a4',compress:true});
  /* Hauteur de contenu par page = 297 - 20 (marge haut) - 28 (marge bas + pied) = 249mm */
  const pageHeightPx=Math.floor(249*canvas.width/170);
  const totalPages=Math.max(1,Math.ceil(canvas.height/pageHeightPx));
  /* Trouve la meilleure ligne de coupe : remonte depuis idealY pour trouver une ligne blanche */
  function findBreakRow(idealY){
   if(idealY>=canvas.height)return canvas.height;
   const scanPx=Math.min(100,idealY);
   const ctx2=canvas.getContext('2d');
   const d=ctx2.getImageData(0,idealY-scanPx,canvas.width,scanPx+1).data;
   let bestRow=idealY,bestScore=-1;
   for(let r=scanPx;r>=0;r--){
    let w=0;
    for(let c=0;c<canvas.width;c++){const i=(r*canvas.width+c)*4;if(d[i]>=243&&d[i+1]>=243&&d[i+2]>=243)w++;}
    const score=w/canvas.width;
    if(score>bestScore){bestScore=score;bestRow=idealY-scanPx+r;}
    if(score>=0.98)break;
   }
   return bestRow;
  }
  let curY=0;
  for(let i=0;i<totalPages;i++){
   if(i>0)pdf.addPage('a4','portrait');
   const idealEnd=curY+pageHeightPx;
   const actualEnd=i===totalPages-1?canvas.height:findBreakRow(Math.min(idealEnd,canvas.height));
   const h=actualEnd-curY;
   const slice=document.createElement('canvas');slice.width=canvas.width;slice.height=h;
   slice.getContext('2d').drawImage(canvas,0,curY,canvas.width,h,0,0,canvas.width,h);
   const imgH=h/(canvas.width/170);
   pdf.addImage(slice.toDataURL('image/jpeg',0.88),'JPEG',20,20,170,imgH);
   pdf.setDrawColor(85,85,85);pdf.setLineWidth(0.25);pdf.line(20,274,190,274);
   pdf.setFont('times','normal');pdf.setFontSize(9);
   const contact=[common.address,common.phone,common.email].filter(Boolean).join(' \u2022 ')||'Adresse \u2022 T\u00e9l\u00e9phone \u2022 Email';
   pdf.text(contact.slice(0,130),20,279,{maxWidth:170});
   pdf.text('R\u00e9f. : '+currentDoc.reference,20,285);
   pdf.text('Page '+(i+1)+' / '+totalPages,190,285,{align:'right'});
   curY=actualEnd;
  }
  const slug=String(currentDoc.reference||active).replace(/[^A-Za-z0-9_-]+/g,'_');
  pdf.save('NETUBEX_'+slug+'.pdf');showToast('Le PDF a \u00e9t\u00e9 t\u00e9l\u00e9charg\u00e9.');
 }catch(error){console.error(error);showToast('L\u2019export PDF a \u00e9chou\u00e9. Essayez le bouton Imprimer.')}
 finally{if(holder)holder.remove();button.disabled=false;button.innerHTML='<span>\u2193</span> Exporter en PDF'}
}
function setActive(type){
 if(type===active)return;active=type;currentDoc=loadDoc(active);
 document.querySelectorAll('#docTabs [data-doc]').forEach(b=>b.classList.toggle('active',b.dataset.doc===active));
 renderForm();renderPreview();
}
function init(){
 currentDoc=loadDoc(active);renderForm();renderPreview();
 $('#docTabs').addEventListener('click',e=>{const b=e.target.closest('[data-doc]');if(b)setActive(b.dataset.doc)});
 $('#exportPdf').addEventListener('click',exportPdf);
 $('#printDoc').addEventListener('click',()=>window.print());
 $('#toolbarReset').addEventListener('click',resetDocument);
 if(!storageSet('__netubex_storage_check','1'))showToast('Le stockage local est bloqué : la conservation des formulaires peut être limitée.');else{try{window.localStorage.removeItem('__netubex_storage_check')}catch{}}
}
init();
})(); 




