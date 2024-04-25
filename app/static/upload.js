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
            let output = '';
            data.classificações.forEach((classificacao, index) => {
                output += `<p class="bg-gray-100 rounded p-2 shadow">Imagem ${index + 1}: ${classificacao}</p>`;
            });
            resultDiv.innerHTML = output;
        })
        .catch(error => {
            resultDiv.innerHTML = `<p class="text-red-600">Ocorreu um erro ao tentar classificar as imagens.</p>`;
        });
    });

    fileInput.addEventListener('change', previewFiles);
});
