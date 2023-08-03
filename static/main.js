let allLanguages = {}

function getSupportedLanguages() {
    return fetch(`/api/languages`).then(response => response.json())
}

function detectLanguage(text) {
    return fetch(`/api/detectlang`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text
        })
    }).then(response => response.json()).then(result => result.language)
}

function doTranslate() {
    document.getElementById('progress').style.display = "block";
    const from = document.getElementById('source_lang').value;
    const to = document.getElementById('target_lang').value;
    let text;
    if (mint_format=='html'){
        text = document.getElementById('source_content').innerHTML;
    }else if (mint_format=='svg'){
        text = document.getElementById('source_content').innerHTML;
    } else{
        text = document.getElementById('source_content').value;
    }
    document.getElementById('status').innerText = '';
    fetch(`/api/translate/${from}/${to}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            [mint_format]:text
        })
    }).then(response => response.json())
        .then(result => {
            document.getElementById('target_content').setAttribute("lang", to)
            if (mint_format==='html'){
                document.getElementById('target_content').innerHTML= result.translation.trim()
            } else if (mint_format==='webpage'){
                const downloadLink = document.createElement('a')
                downloadLink.setAttribute('href', 'data:text/html;charset=utf-8,' + encodeURIComponent(result.translation));
                downloadLink.setAttribute('download', 'translation.html');
                downloadLink.textContent = 'Download';
                document.getElementById('results').appendChild(downloadLink)
            } else if (mint_format==='svg'){
                document.getElementById('target_content').innerHTML= result.translation.trim()
            } else {
                document.getElementById('target_content').textContent = result.translation
            }
            document.getElementById('progress').style.display = "none";
            document.getElementById('status').innerText = `Translated in ${result.translationtime.toFixed(2)} seconds by ${result.model} model`
        })
}

function listSupportedTargetLanguages(sourceLang, allPairs) {
    const tgt_selector = document.getElementById('target_lang');
    const currentSelection = tgt_selector.value || 'es';
    tgt_selector.innerHTML = '';
    const targetLangs = allPairs[sourceLang];
    for (lang in targetLangs) {
        const nameGenerator = new Intl.DisplayNames('en', { type: 'language' });
        const displayName = nameGenerator.of(lang);
        const el = document.createElement("option");
        el.textContent = displayName;
        el.value = lang;
        if (lang == currentSelection ) {
            el.selected = true;
        }
        tgt_selector.appendChild(el);
    }
    tgt_selector.addEventListener("change", function () {
        document.getElementById('target_content').innerText = ""
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const src_selector = document.getElementById('source_lang');
    const sourceElement = document.getElementById('source_content');

    getSupportedLanguages().then(languages => {
        allLanguages = languages
        src_selector.innerHTML = '';

        for (lang in languages) {
            const nameGenerator = new Intl.DisplayNames('en', { type: 'language' });
            const displayName = nameGenerator.of(lang);
            const el = document.createElement("option");
            el.textContent = displayName;
            el.value = lang;
            if (lang == 'en') {
                el.selected = true;
            }
            src_selector.appendChild(el);
        }
        listSupportedTargetLanguages('en', allLanguages)
    })

    src_selector.addEventListener("change", () => {
        const from = document.getElementById('source_lang').value;
        listSupportedTargetLanguages(from, allLanguages)
    });

    sourceElement.addEventListener("input", () => {
        detectLanguage(sourceElement.value).then(language => {
            src_selector.value = language;
            src_selector.dispatchEvent(new Event('change'));
        })
    });
});
