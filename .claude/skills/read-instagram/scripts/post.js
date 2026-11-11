(()=>{const CODE="__CODE__";let hit=null;
const walk=o=>{if(hit||!o||typeof o!=="object")return;if(o.code===CODE&&(o.image_versions2||o.carousel_media)){hit=o;return}for(const k in o)walk(o[k])};
for(const s of document.querySelectorAll("script[type=\"application/json\"]")){if(!s.textContent.includes(CODE))continue;try{walk(JSON.parse(s.textContent))}catch(e){}if(hit)break}
if(!hit)return JSON.stringify({err:"notfound"});
const best=m=>{const c=(m.image_versions2||{}).candidates||[];c.sort((a,b)=>b.width*b.height-a.width*a.height);return c[0]?c[0].url:null};
const items=(hit.carousel_media||[hit]).map(m=>({url:best(m),video:!!m.video_versions,alt:m.accessibility_caption||""}));
return JSON.stringify({code:CODE,owner:(hit.user||hit.owner||{}).username,taken_at:hit.taken_at,likes:hit.like_count,comments:hit.comment_count,
caption:(hit.caption||{}).text||"",usertags:((hit.usertags||{}).in||[]).map(t=>t.user.username),items})})()
