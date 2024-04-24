function previewFiles(event) {
    console.log("Previewing files...");  // Log para verificar a chamada da função
    const preview = document.getElementById('images-preview');
    const files = event.target.files;

    while (preview.firstChild) {
        preview.removeChild(preview.firstChild);
    }

    function readAndPreview(file) {
        if (/\.(jpe?g|png|gif)$/i.test(file.name)) {
            var reader = new FileReader();

            reader.onload = function(event) {
                var img = new Image();
                img.height = 100; // Altura fixa
                img.width = 100; // Largura fixa para manter a proporção
                img.style.objectFit = 'cover'; // Isso garante que a imagem cubra o espaço sem distorcer
                img.title = file.name;
                img.src = event.target.result;
                preview.appendChild(img);
            };

            reader.readAsDataURL(file);
        }
    }

    if (files) {
        [].forEach.call(files, readAndPreview);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById("upload-form");
    const resultDiv = document.getElementById("classification-result");
    const fileInput = document.querySelector('input[type=file]');
    const previewDiv = document.getElementById('images-preview');
    const clearButton = document.getElementById('clear-button');

    clearButton.addEventListener('click', function() {
        // Limpar o formulário
        uploadForm.reset();
        // Remover imagens de visualização
        while (previewDiv.firstChild) {
            previewDiv.removeChild(previewDiv.firstChild);
        }
        // Limpar resultados da classificação
        resultDiv.innerHTML = '';
    });

    uploadForm.addEventListener("submit", function(e) {
        e.preventDefault();

        const formData = new FormData(uploadForm);
        const actionUrl = uploadForm.getAttribute("action");

        fetch(actionUrl, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            let output = '';
            data.classificações.forEach((classificacao, index) => {
                output += `<p>Imagem ${index + 1}: ${classificacao}</p>`;
            });
            resultDiv.innerHTML = output;
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            resultDiv.innerHTML = `<p>Ocorreu um erro ao tentar classificar as imagens.</p>`;
        });
    });

    fileInput.addEventListener('change', previewFiles);
});
