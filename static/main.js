function doTranslate() {
    document.getElementById('progress').style.display = "block";
    const from= document.getElementById('source_lang').value;
    const to= document.getElementById('target_lang').value;
    const text= document.getElementById('source_content').value;
    fetch('https://translate.wmcloud.org/api/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            from,
            to,
            text
        })
    }).then(response => response.json())
        .then(result => {
            document.getElementById('target_content').innerText = result.translation
            document.getElementById('progress').style.display = "none";
        })
}