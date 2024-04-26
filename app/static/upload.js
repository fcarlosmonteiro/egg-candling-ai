function clearPreviewAndResults() {
    console.log("Clearing previews and results...");
    const previewDiv = document.getElementById('images-preview');
    const resultDiv = document.getElementById('classification-result');
    const fileInput = document.querySelector('input[type=file]');
    
    // Limpa o input do arquivo
    fileInput.value = '';
    
    // Remove todas as imagens de visualização
    previewDiv.innerHTML = '';
    
    // Limpa todos os resultados da classificação
    resultDiv.innerHTML = '';
}

function previewFiles(event) {
    const preview = document.getElementById('images-preview');
    const files = event.target.files;

    preview.innerHTML = ''; // Clear existing previews

    function readAndPreview(file) {
        if (/\.(jpe?g|png|gif)$/i.test(file.name)) {
            var reader = new FileReader();

            reader.onload = function(event) {
                var imageHtml = `
                    <div class="flex flex-col items-center m-2">
                        <img src="${event.target.result}" class="h-24 w-24 object-contain rounded-md shadow-lg" title="${file.name}" style="max-width:100%; height:auto;">
                    </div>
                `;
                preview.insertAdjacentHTML('beforeend', imageHtml);
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
    const fileInput = document.querySelector('input[type=file]');
    const previewDiv = document.getElementById('images-preview');
    const resultDiv = document.getElementById('classification-result');
    const clearButton = document.getElementById('clear-button');

    clearButton.addEventListener('click', clearPreviewAndResults);
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
            resultDiv.innerHTML = ''; // Limpa os resultados anteriores
            data.classificações.forEach((classificacao, index) => {
                // Atualize aqui para apresentar os resultados de maneira mais visual
                const color = classificacao === 'Fértil' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
                const resultHtml = `
                    <div class="flex items-center justify-between p-4 rounded shadow ${color}">
                        <span class="font-medium">Imagem ${index + 1}:</span>
                        <span class="text-xl">${classificacao}</span>
                    </div>
                `;
                resultDiv.insertAdjacentHTML('beforeend', resultHtml);
            });
        })
        .catch(error => {
            resultDiv.innerHTML = `<p class="text-red-600">Ocorreu um erro ao tentar classificar as imagens.</p>`;
        });
    });

    fileInput.addEventListener('change', previewFiles);
});
