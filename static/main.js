let allLanguages = {}

let languageNames = {}

function getSupportedLanguages() {
    return fetch(`/api/languages`).then(response => response.json())
}

function list_models() {
    const from = document.getElementById('source_lang').value;
    const to = document.getElementById('target_lang').value;
    const models = allLanguages[from][to];
    const model_selector = document.getElementById('mtmodel');
    model_selector.innerHTML = '';

    for (let i = 0; i < models.length; i++) {
        const el = document.createElement("option");
        if (i == 0 && models.length > 1) {
            el.textContent = `${models[i]} (default)`;
        } else {
            el.textContent = models[i];
        }
        el.value = models[i];
        model_selector.appendChild(el);
    }
    // Disable selector if there is only one model
    model_selector.disabled = models.length === 1;
}

function getLanguageNames() {
    return fetch('https://en.wikipedia.org/w/api.php?action=query&liprop=autonym|name&meta=languageinfo&uselang=en&format=json&origin=*')
        .then(response => response.json())
        .then(queryResult => queryResult.query.languageinfo)
}

function detectLanguage(text) {
    // langid api expects a single line of text.
    const firstline = text.split('\n')[0]
    return fetch('https://api.wikimedia.org/service/lw/inference/v1/models/langid:predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text:firstline
        })
    }).then(response => response.json()).then(result => result.wikicode)
}

function doTranslate() {
    document.getElementById('progress').style.display = "block";
    const from = document.getElementById('source_lang').value;
    const to = document.getElementById('target_lang').value;
    const model = document.getElementById('mtmodel').value;
    let text;
    if (mint_format=='html'){
        text = document.getElementById('source_content').innerHTML;
    }else if (mint_format=='svg'){
        text = document.getElementById('source_content').innerHTML;
    } else{
        text = document.getElementById('source_content').value;
    }
    document.getElementById('status').innerText = '';
    fetch(`/api/translate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            source_language: from,
            target_language: to,
            format: mint_format,
            model: model,
            content: text,
        })
    }).then(response => {
        if (!response.ok) {
            throw new Error('Server returned ' + response.status);
        }
        return response.json();
    })
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
        document.getElementById('status').innerText = `Translated in ${result.translationtime.toFixed(2)} seconds by ${result.model} model`
    })
    .catch(error => {
        // Error handling
        console.error('An error occurred:', error);
        // Display an error message to the user
        document.getElementById('status').innerText = 'An error occurred. Please try again.';
    }).finally(()=>{
        document.getElementById('progress').style.display = "none";
    });
}

function listSupportedTargetLanguages(sourceLang, allPairs) {
    const tgt_selector = document.getElementById('target_lang');
    const currentSelection = tgt_selector.value || 'es';
    tgt_selector.innerHTML = '';
    const targetLangs = allPairs[sourceLang];
    let languageNameMap = new Map()

    for (langCode in targetLangs) {
        languageNameMap.set(languageNames[langCode]?.name || langCode, langCode);
    }
    const sortedLanguageNames = [...languageNameMap.keys()].sort(Intl.Collator().compare);
    for (const displayName of sortedLanguageNames) {
        const langCode = languageNameMap.get(displayName);
        const el = document.createElement("option");
        el.textContent = displayName;
        el.value = langCode;
        if (langCode == currentSelection) {
            el.selected = true;
        }
        tgt_selector.appendChild(el);
    }

    tgt_selector.addEventListener("change", function () {
        document.getElementById('target_content').innerText = ""
        list_models();
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const src_selector = document.getElementById('source_lang');
    const sourceElement = document.getElementById('source_content');
    languageNames = await getLanguageNames()
    allLanguages = await  getSupportedLanguages()

    src_selector.innerHTML = '';

    let languageNameMap = new Map()

    for (langCode in allLanguages) {
        languageNameMap.set(languageNames[langCode]?.name || langCode, langCode);
    }
    const sortedLanguageNames = [...languageNameMap.keys()].sort(Intl.Collator().compare);
    for (const displayName of sortedLanguageNames) {
        const langCode = languageNameMap.get(displayName);
        const el = document.createElement("option");
        el.textContent = displayName;
        el.value = langCode;
        if (langCode == 'en') {
            el.selected = true;
        }
        src_selector.appendChild(el);
    }
    listSupportedTargetLanguages('en', allLanguages)
    src_selector.addEventListener("change", () => {
        const from = document.getElementById('source_lang').value;
        listSupportedTargetLanguages(from, allLanguages)
        list_models();
    });

    sourceElement.addEventListener("input", () => {
        detectLanguage(sourceElement.value).then(language => {
            src_selector.value = language;
            src_selector.dispatchEvent(new Event('change'));
        })
    });
    list_models();
});
