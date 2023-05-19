css_boilerplate="""
<style type="text/css">
    body{font-family:sans-serif;font-size:16px;line-height:24px;}
    .quoteright{float:right;margin:1px 1px 5px 13.5px;border-left:6px solid #fafafa;border-right:6px solid #fafafa;box-shadow:0 0 0 1px #cacdd1;
    padding:6px 0;font-size:.84em;text-align:center;}
    .quote{font-size:.84em;margin-left: 18px;}
    a{text-decoration:none;color:#006bb1}
    .spoiler a{color:inherit;pointer-events:none;}
    .spoiler a.red{color:inherit;pointer-events:none;}
    .asscaps{font-variant:small-caps;}
    .hidden{opacity:35%;}
    a:hover{text-decoration:underline}
    a.red{color:#c60000}
    ul{margin-left:-14.4px;}
    .ad{border:1px solid black;text-align:center}
    .error{color:red;}
    .spoiler{border:1px dotted #7f7f7f;border-top:none;cursor:pointer;color:transparent;}
    .spoiler-reveal{border:1px dotted #7f7f7f;border-top:none;cursor:pointer;}
    .notelabel{vertical-align:super;font-size:smaller;cursor:pointer;}
    .note{font-size:smaller;cursor:pointer;}
    .notelabel{font-size:smaller;cursor:pointer;}
    .foldercontrol-closed::before{content:'\U0001F4C1';}
    .foldercontrol-closed{border:1px solid #cacdd1;border-radius:4px;cursor:pointer;display:inline-block;padding:4px 6px;margin-top:15px;}
    .foldercontrol-open::before{content:'\U0001F4C2';}
    .foldercontrol-open{border:1px solid #cacdd1;border-radius:4px;cursor:pointer;display:inline-block;padding:4px 6px;margin-top:15px;}
    .folder-closed{display:none}
    .typeahead{position:absolute;border:1px solid black;background:white}
    .suggestion{cursor:pointer}
    .suggestion:hover{background:#c0c0ff}
</style>
"""
js_boilerplate="""
<script type="text/javascript">
    ei=document.getElementById.bind(document);ec=document.getElementsByClassName.bind(document);ce=document.createElement.bind(document);
    function cea(et,attr){var e=ce(et);return Object.assign(e,attr)};function ceac(et,attr,c){var e=cea(et,attr);e.innerText=c;return e};
    ec2=(x,y)=>x.getElementsByClassName(y);function ab(e0,e){e0.parentNode.insertBefore(e,e0)}
    function rv(n){return document.querySelector("input[type='radio'][name="+n+"]:checked").value}
    async function fco(url,opt,cb){try{res=await fetch(url,opt);data=await res.text();cb(data)}catch(error){console.error("error in "+url+":",error)}}
    function show(e){e.style.display=""};function hide(e){e.style.display="none"}; function scrollTo(e){e.scrollIntoView({behavior:"smooth",block:"nearest"})}
    function fc(url,cb){fco(url,null,cb)};function fp(url,data,cb){fco(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)},cb)}
    function cetv(et,t,v){var e=ce(et);e.type=t;e.value=v;return e}
    function sc(c,t){es=[];for(e of ec(c)){es.push(e)};for(e of es){e.setAttribute("class",t)}}
    function toggleFolder(ev){e=ev.target;id=e.id;c=e.getAttribute("class");t=(c=="foldercontrol-closed")?"foldercontrol-open":"foldercontrol-closed";e.setAttribute("class",t);
        t2=(c=="foldercontrol-closed")?"folder-open":"folder-closed";
        if(id=="folderCtrlGlobal"){sc("foldercontrol-open",t);sc("foldercontrol-closed",t);sc("folder-closed",t2);sc("folder-open",t2)}
        else{e.nextElementSibling.setAttribute("class", t2)}}
    function toggleSpoiler(ev,e){if(e==ev.target || e.className!="spoiler-reveal"){e.className=e.className=="spoiler-reveal"?"spoiler":"spoiler-reveal"}}
    function togglenote(e){e.style.display=e.style.display=="none"?"inline":"none"}
    function addEvents(r){for(e of ec2(r,"spoiler")){e.addEventListener("click",function(e){return function(ev){toggleSpoiler(ev,e)}}(e))};
        for(e of ec2(r,"notelabel")){e.addEventListener("click",togglenote.bind(null,e.nextElementSibling))}
        for(e of ec2(r,"note")){e.addEventListener("click",togglenote.bind(null,e))}
        for(e of ec2(r,"example")){e.id="example"+e.dataset.idx}
        for(e of ec2(r,"foldercontrol-closed")){e.addEventListener("click",toggleFolder)}}
    function addRadio(e0,n,v,t){var e=cetv("input","radio",v);e.name=n;e.id=n+v;ab(e0,e);e.addEventListener("click",updFilter);var e2=ce("label");e2.setAttribute("for",n+v);
        e2.innerText=t;ab(e0,e2);return e}
    function addCheckbox(e0,n,t){var e=cea("input",{type:"checkbox",id:n,name:n});e.addEventListener("click",updFilter);ab(e0,e);var e2=ce("label");e2.setAttribute("for",n);
        e2.innerText=t;ab(e0,e2);return e}
    function dropdown(name,opts){var e=cea("select",{id:name},opts);for(var o in opts){e.appendChild(cea("option",{value:o,innerText:opts[o]}))};return e}
    function addHiddenControl(){var e0=ei("examples");addCheckbox(e0,"addHidden",i18n.addHidden);ab(e0,ce("br"))}
    function addFilterControl(){var e0=ei("examples");
        addRadio(e0,"filter","all",i18n.filterAll);tr=addRadio(e0,"filter","tropes",i18n.filterTropes);addRadio(e0,"filter","ymmv",i18n.filterYMMV);
        addRadio(e0,"filter","trivia",i18n.filterTrivia);tr.checked=true;ab(e0,ce("br"));}
    function addSortControl(){e0=ei("examples");tr=addRadio(e0,"sort","az",i18n.sortAZ);addRadio(e0,"sort","ctimeDn",i18n.sortCtimeDn);addRadio(e0,"sort","ctimeUp",i18n.sortCtimeUp);
        addRadio(e0,"sort","mtimeDn",i18n.sortMtimeDn);addRadio(e0,"sort","mtimeUp",i18n.sortMtimeUp);
        tr.checked=true}
    function init(){addEvents(document);addHiddenControl();if(ei("nxp").dataset.side==1)addFilterControl();if(ei("nxp").dataset.side<2)addSortControl()}
    editing=false;
    function addEditBtn(e,idx,cb){if(e.innerHTML=="")e.innerHTML=i18n["empty"+["Title","Description","Quote","Image","Stinger"][idx]];e.style.border="1px solid black";
        c=cetv("input","button",i18n.editExample);c.style="float:right;";c.addEventListener("click",cb.bind(null,idx));e.insertBefore(c,e.firstChild)}
    function addEditBtnForExs(){for(var e of ec("example"))addEditBtn(e,parseInt(e.dataset.idx),editEx);}
    function makeAdder(e){e.innerHTML=i18n.newExample;e.style.border="1px solid black";c=cetv("input","button",i18n.addExample);c.style="float:right;";c.addEventListener("click",addEx);
        e.insertBefore(c,e.firstChild);}
    function getTypeaheadBox(){var e=ei("typeahead");if(e)return e;e=cea("div",{id:"typeahead",classList:"typeahead"});hide(e);document.body.append(e);return e}
    function edit(){if(editing)return;editing=true;addEditBtnForExs();for(var e of ec("block"))addEditBtn(e,parseInt(e.dataset.bt),editBl);e=ei("nxp");makeAdder(e);getTypeaheadBox()}
    function esf(idx){return idx==null?"New":(""+idx)}
    function addEditor(e,idx,prefix,suffix,elems,previewFn,saveFn){
        e.innerHTML="";
        g=ce("div");g.id=prefix+"editor"+suffix;
        for(elem of elems)g.appendChild(elem);
        c=ce("textarea");c.style.width="80%";c.style.height="300px";
        c.id=prefix+"edit"+suffix;g.appendChild(c);g.appendChild(ce("br"));
        c=cetv("input","button",i18n.preview);c.id=prefix+"getprv"+suffix;c.addEventListener("click",previewFn.bind(null,idx));g.appendChild(c);
        c=ce("span");c.id=prefix+"err"+suffix;c.classList+="error";g.appendChild(c);
        e.appendChild(g);scrollTo(g);
        g=ce("div");g.id=prefix+"preview"+suffix;hide(g);
        c=ce("div");c.id=prefix+"previewCont"+suffix;g.appendChild(c);
        c=cetv("input","button",i18n.backToEdit);c.addEventListener("click",backEdit.bind(null,prefix,suffix));g.appendChild(c);
        c=cetv("input","button",i18n.save);c.addEventListener("click",saveFn.bind(null,idx));g.appendChild(c);
        c=ce("span");c.id=prefix+"sverr"+suffix;c.classList+="error";g.appendChild(c);
        e.appendChild(g);
    }
    function addBlEditor(e,idx){addEditor(e,idx,"bl",""+idx,[],previewBl,saveBl)}
    function addExEditor(e,idx){
        suffix=esf(idx);
        editorElems=[];
        var addPicker=function(label,prefix,side){
            var c=ce("label");c.innerHTML=label+" ";editorElems.push(c);
            c=cetv("input","text","");c.id=prefix+suffix;c.size=50;c.addEventListener("keyup", typeAhead.bind(null,c,side,idx));
            var tg=ce("div");tg.style.display="inline-block";tg.appendChild(c);editorElems.push(tg);editorElems.push(ce("br"));
        }
        addPicker(i18n.exSrc,"src",0);
        addPicker(i18n.exTgt,"tgt",1);
        editorElems=editorElems.concat([
            cea("label",{for:"playWithType"+suffix,innerText:i18n.playingWith+" "}),dropdown("playWithType"+suffix,i18n.playingWithType),ce("br")]);
        var addCheckbox=function(label,prefix){
            editorElems.push(cea("input",{type:"checkbox",id:prefix+suffix,name:prefix+suffix}));
            var e=ce("label");e.setAttribute("for",prefix+suffix);e.innerText=label;
            editorElems.push(e);
            editorElems.push(ce("br"));
        }
        addCheckbox(i18n.exAsym,"asym");
        addCheckbox(i18n.hideEx,"hide");
        if(mod){
            addCheckbox(i18n.lockEx,"lock");
            addCheckbox(i18n.embargoEx,"embargo");
        }
        addEditor(e,idx,"ex",suffix,editorElems,preview,saveEx);
    }
    function lockEditor(idx){suffix=esf(idx);for(var en of["src","tgt","playWithType","asym","hide","exedit"]){ei(en+suffix).setAttribute("disabled", true)};ei("exgetprv"+suffix).remove()}
    function typeAhead(e,s,idx){txt=e.value;if(txt.length>=1){fc("/api/v1/typeahead?query="+txt+"&side="+s+"&lang="+lang,typeAheadResp.bind(null,e))}}
    function typeAheadResp(e,cont){lst=getTypeaheadBox();e.parentNode.insertBefore(lst,e.nextSibling);lst.innerHTML="";
        cont=JSON.parse(cont);for(it of cont.results){sg=ce("div");sg.classList+="suggestion";sg.innerText=it.displayName+" ("+it.name+")";
        sg.addEventListener("click",(name=>ev=>{hide(lst);e.value=name})(it.name));lst.appendChild(sg)}show(lst);
    }
    function editEx(idx){e=ei("example"+idx);addExEditor(e,idx);ei("exedit"+esf(idx)).value=i18n.loading;fc("/api/v1/example"+(idx==null?"":"/"+idx)+"?lang="+lang+"&side="+ei("nxp").dataset.side,fillEditEx)}
    function editBl(idx){e=ei("block"+idx);addBlEditor(e,idx);ei("bledit"+esf(idx)).value=i18n.loading;fc("/api/v1/page/"+ei("nxp").dataset.pi+"/block/"+idx+"?lang="+lang,fillEditBl.bind(null,idx))}
    function addEx(){e=ei("nxp");addExEditor(e,null);ei(e.dataset.side==1?"tgtNew":"srcNew").value=e.dataset.title}
    function fillEditEx(cont){cont=JSON.parse(cont);idx=cont.id;ei("exedit"+idx).value=cont.content;ei("src"+idx).value=cont.linkSource;ei("tgt"+idx).value=cont.linkTarget;
        if(cont.asym)ei("asym"+idx).checked=true;ei("playWithType"+idx).value=cont.play;ei("hide"+idx).checked=cont.hide;if(mod){ei("lock"+idx).checked=cont.lock;ei("embargo"+idx).checked=cont.embargo}
        if(cont.lock&&!mod)lockEditor(idx)}
    function fillEditBl(idx,cont){cont=JSON.parse(cont);ei("bledit"+idx).value=cont.content}
    function postEx(idx,needSave,cb){suf=esf(idx);var ex={id:idx,linkSource:ei("src"+suf).value,linkTarget:ei("tgt"+suf).value,content:ei("exedit"+suf).value,
        save:needSave,pageSide:ei("nxp").dataset.side,asym:ei("asym"+suf).checked,hide:ei("hide"+suf).checked,play:ei("playWithType"+suf).value};if(mod){ex.lock=ei("lock"+suf).checked;
        ex.embargo=ei("embargo"+suf).checked}fp("/api/v1/example"+(idx==null?"":"/"+idx)+"?lang="+lang,ex,cb)}
    function postBl(idx,needSave,cb){fp("/api/v1/page/"+ei("nxp").dataset.pi+"/block/"+idx+"?lang="+lang,{content:ei("bledit"+idx).value,save:needSave},cb)}
    function preview(idx){postEx(idx,false,previewResp.bind(null,idx,"ex"))}
    function saveEx(idx){postEx(idx,true,saveResp.bind(null,idx,"ex"))}
    function addError(e,cont){e.innerText=cont.error;if("badLinks"in cont){var fst=1;for(lnk of cont.badLinks){if(!fst)e.appendChild(cea("span",{innerText:", "}));fst=0;
        e.appendChild(cea("a",{innerText:lnk,href:"/createPage?lang="+lang+"&path="+lnk,target:"_blank"}));}}}
    function previewResp(idx,prefix,cont){suf=esf(idx);cont=JSON.parse(cont);if("error" in cont){addError(ei(prefix+"err"+suf),cont)}else{
        ei(prefix+"sverr"+suf).innerText="";
        idx=cont.id;hide(ei(prefix+"editor"+suf));e=ei(prefix+"previewCont"+suf);e.innerHTML=cont.content;addEvents(e);show(ei(prefix+"preview"+suf));scrollTo(e);}}
    function previewBlResp(idx,cont){cont=JSON.parse(cont);if("error" in cont){addError(ei("blerr"+idx),cont)}else{
        ei("blsverr"+idx).innerText="";hide(ei("bleditor"+idx));e=ei("blpreviewCont"+idx);e.innerHTML=cont.content;addEvents(e);show(ei("blpreview"+idx));scrollTo(e);}}
    function backEdit(prefix,suffix){ei(prefix+"err"+suffix).innerText="";var e=ei(prefix+"editor"+suffix);show(e);scrollTo(e);hide(ei(prefix+"preview"+suffix))}
    function saveResp(idx,prefix,cont){suf=esf(idx);cont=JSON.parse(cont);if("error" in cont){addError(ei(prefix+"sverr"+suf),cont)}else{
        if(idx==null){e=ce("div");e.id="example"+cont.id;p=ei("nxp");e0=ei("examples");e0.insertBefore(e,e0.firstChild);makeAdder(p);
        }else{e=ei("example"+suf)}e.innerHTML=cont.content;addEditBtn(e,cont.id,editEx)}}
    function previewBl(idx){postBl(idx,false,previewBlResp.bind(null,idx))}
    function saveBl(idx){postBl(idx,true,saveBlResp.bind(null,idx))}
    function saveBlResp(idx,cont){cont=JSON.parse(cont);if("error" in cont){addError(ei("blsverr"+idx),cont)}else{
        e=ei("block"+idx);e.innerHTML=cont.content;addEditBtn(e,idx,editBl)}}
    function updFilter(n,v){e=ei("nxp");fc("/api/v1/page/"+e.dataset.pi+"/exampleHtml?lang="+lang+"&"+(e.dataset.side==1?("filter="+rv("filter")+"&"):"")+"sort="+rv("sort")+
        "&addHidden="+ei("addHidden").checked,updEx)}
    function updEx(cont){e=ei("examples");e.innerHTML=cont;addEvents(e);if(editing)addEditBtnForExs()}
</script>
"""
boilerplate=css_boilerplate+js_boilerplate
