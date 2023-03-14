function doTranslate() {
    document.getElementById('progress').style.display = "block";
    const from= document.getElementById('source_lang').value;
    const to= document.getElementById('target_lang').value;
    const text= document.getElementById('source_content').value;
    document.getElementById('status').innerText ='';
    fetch(`/api/translate/${from}/${to}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text
        })
    }).then(response => response.json())
        .then(result => {
            document.getElementById('target_content').innerText = result.translation
            document.getElementById('progress').style.display = "none";
            document.getElementById('status').innerText = `Translated in ${result.translationtime} seconds by ${result.model} model`
        })
}

document.addEventListener("DOMContentLoaded", () => {
    src_selector = document.getElementById('source_lang');
    tgt_selector = document.getElementById('target_lang');
    fetch(`/api/languages`).then(response => response.json())
        .then(languages => {
            src_selector.innerHTML = '';
            tgt_selector.innerHTML = '';
            for( lang in languages){
                const nameGenerator = new Intl.DisplayNames('en', { type: 'language' });
                const displayName = nameGenerator.of(lang);
                const el = document.createElement("option");
                el.textContent = displayName;
                el.value = lang;
                if (lang=='en'){
                    el.selected=true;
                }
                src_selector.appendChild(el);
            }
            for( lang in languages){
                const nameGenerator = new Intl.DisplayNames('en', { type: 'language' });
                const displayName = nameGenerator.of(lang);
                const el = document.createElement("option");
                el.textContent = displayName;
                el.value = lang;
                if (lang=='es'){
                    el.selected=true;
                }
                tgt_selector.appendChild(el);
            }
        })
});
