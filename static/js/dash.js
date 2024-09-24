document.addEventListener('DOMContentLoaded', () => {

    async function handleFileUpload(buttonId, fileInputId, formId, messageId, processUrl, dialogOptions) {
        const button = document.getElementById(buttonId);
        const fileInput = document.getElementById(fileInputId);
        const form = document.getElementById(formId);
        const message = document.getElementById(messageId);
        const acceptAttribute = fileInput.getAttribute('accept'); // Extrae el valor de 'accept'

        if (button && fileInput && form && message) {
            button.addEventListener('click', async () => {
                if ('showOpenFilePicker' in window) {
                    try {
                        const handles = await window.showOpenFilePicker({
                            multiple: true,
                            types: [
                                {
                                    description: dialogOptions.fileDescription || 'Archivos',
                                    accept: {
                                        '*/*': acceptAttribute.split(',').map(type => type.trim())
                                    },
                                },
                            ],
                        });

                        Swal.fire({
                            title: dialogOptions.title || 'Opciones',
                            html: dialogOptions.html || '',
                            focusConfirm: false,
                            confirmButtonText: dialogOptions.confirmButtonText || 'Subir Archivo',
                            preConfirm: () => {
                                
                                const formId = dialogOptions.title.replace(/\s/g, '') + 'OptionsForm';
                                const optionsForm = document.getElementById(formId);
                                // const optionsForm = document.getElementById('EasyCodeOptionsForm') || document.getElementById('runBatOptionsForm');
                                let options = {};
                                if (optionsForm) {
                                    // Captura el estado de los checkboxes
                                    const removeNetCheckbox = document.getElementById('removeNet');
                                    const formatHeadersCheckbox = document.getElementById('formatHeaders');
                                    options['remove_net'] = removeNetCheckbox ? removeNetCheckbox.checked : false;
                                    options['format_headers'] = formatHeadersCheckbox ? formatHeadersCheckbox.checked : false;

                                    // Captura los otros datos del formulario
                                    const formData = new FormData(optionsForm);
                                    for (const [key, value] of formData.entries()) {
                                        if (!options.hasOwnProperty(key)) {
                                            options[key] = value;
                                        }
                                    }
                                }
                                console.log("Form options (button dialog):", options); // Verifica los valores del formulario
                                return options;
                            }
                        }).then(async (result) => {
                            if (result.isConfirmed) {
                                Swal.fire({
                                    title: 'Procesando...',
                                    text: 'Por favor, espera mientras procesamos los archivos.',
                                    icon: 'info',
                                    allowOutsideClick: false,
                                    didOpen: () => {
                                        Swal.showLoading();
                                    }
                                });

                                const formData = new FormData();
                                Object.keys(result.value).forEach(key => formData.append(key, result.value[key]));

                                for (const handle of handles) {
                                    const file = await handle.getFile();
                                    const fileContent = await file.arrayBuffer();
                                    const blob = new Blob([fileContent], { type: file.type });
                                    formData.append('files[]', blob, file.name); // Usa 'files[]' para enviar un array
                                }

                                try {
                                    const response = await fetch(processUrl, {
                                        method: 'POST',
                                        body: formData
                                    });
                            
                                    const data = await response.json();
                            
                                    if (data.filePaths && data.filePaths.length > 0) {
                                        Swal.fire({
                                            title: 'Éxito',
                                            // html: `Archivos procesados correctamente. <br> ${data.filePaths.map(filePath => `<a href="/download/${filePath}" download class="btn btn-success m-1">Descargar ${filePath}</a>`).join('')}`, 
                                            html: `Archivos procesados correctamente.`,
                                            icon: 'success',
                                            // showConfirmButton: false 
                                            showCancelButton: true,
                                            confirmButtonText: 'Descargar Archivos',
                                            cancelButtonText: 'Cancelar'
                                        }).then((result) => {
                                            if (result.isConfirmed) {
                                                data.filePaths.forEach(filePath => {
                                                    // Crea un enlace temporal y simula un clic para descargar
                                                    const link = document.createElement('a');
                                                    link.href = `/download/${filePath}`;
                                                    link.download = filePath; // Asegura que el archivo se descargue
                                                    link.style.display = 'none'; // Oculta el enlace
                                                    document.body.appendChild(link);
                                                    link.click();
                                                    document.body.removeChild(link);
                                                });
                                                
                                                // Enviar solicitud para eliminar los archivos
                                                fetch('/delete-files', { // Asegúrate de que esta ruta esté definida en tu backend
                                                    method: 'POST',
                                                    headers: {
                                                        'Content-Type': 'application/json'
                                                    },
                                                    body: JSON.stringify({ filePaths: data.filePaths })
                                                })
                                                .then(response => response.json())
                                                .then(data => {
                                                    if (data.message) {
                                                        console.log(data.message); 
                                                    } else {
                                                        console.error('Error al eliminar los archivos en el servidor.');
                                                    }
                                                })
                                                .catch(error => {
                                                    console.error('Error al enviar la solicitud para eliminar archivos:', error);
                                                });
                                            }
                                        });
                                    } else {
                                        Swal.fire({
                                            title: 'Éxito',
                                            text: 'Archivos procesados correctamente, pero no se generaron archivos de salida.',
                                            icon: 'success'
                                        });
                                    }
                            
                                } catch (error) {
                                    Swal.close();
                                    Swal.fire({
                                        title: 'Error',
                                        text: `Ocurrió un error inesperado al procesar ${file.name}: ${error}`,
                                        icon: 'error'
                                    });
                                }
                            }
                        });

                    } catch (err) {
                        console.error('Error al leer los archivos:', err);
                    }
                } else {
                    fileInput.click();
                }
            });
        }
    }

    const uploadOptions = {
        EasyCode: {
            title: 'Opciones de EASY-CODING',
            options: [
                { label: 'Eliminar columnas NET_', id: 'removeNet', type: 'checkbox' },
                { label: 'Formatear encabezados', id: 'formatHeaders', type: 'checkbox' },
                { label: 'Nuevo encabezado', id: 'newHeader', type: 'text', value: 'InterviewID' }
            ]
        },
        runBat: {
            title: 'Opciones de RUN BAT',
            options: [
                { label: 'Ejecuacion', id: 'someOption', type: 'checkbox' }
            ]
        },
        NETOS: { 
            title: 'Opciones de Netos',
            options: [
                { 
                    label: 'Formato', 
                    id: 'formato', 
                    type: 'select', // Indicamos que es un combobox
                    options: [ // Opciones del combobox
                        { value: 'peru', label: 'Perú' },
                        { value: 'colombia', label: 'Colombia' },
                        { value: 'brasil', label: 'Brasil' },
                        { value: 'easy_coding', label: 'Easy Coding' }
                    ]
                }
            ]
        },
        mapeoSpss: {
            title: 'Opciones de Mapeo SPSS',
            options: [
                { label: 'Seleccionar variables', id: 'id', type: 'text' }
            ]
        },
        formateoArtifac: {
            title: 'Opciones de Formateo Artifac',
            options: [
                { label: 'Formateo Paralelo', id: 'formateoParalelo', type: 'checkbox' },
                { 
                    label: 'Plantilla', 
                    id: 'plantilla', 
                    type: 'select', // Indicamos que es un combobox
                    options: [ // Opciones del combobox
                        { value: 'PERU', label: 'Perú (PCT)' },
                        { value: 'BRASIL_INN', label: 'INN Brasil (NA +PCT)' },
                        { value: 'BRASIL_BHT', label: 'BHT BRASIL (NA +PCT)' }
                    ]
                }
            ]
        },
        valBddLdc: {
            title: 'Opciones de Validacion de Base de Datos VS LDC',
            options: [
                { label: 'Tipo de LDC', id: 'removeNet', type: 'checkbox' }
            ]
        }
    };
    
    // Función para generar el HTML de las opciones
    function generateOptionsHTML(options) {
        let html = `<form id="${options.title.replace(/\s/g, '')}OptionsForm">`; 
        for (const option of options.options) {
            if (option.type === 'select') { // Manejo especial para combobox
                html += `
                    <div>
                        <label for="${option.id}">${option.label}:</label>
                        <select id="${option.id}" name="${option.id.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase()}">`;
    
                for (const selectOption of option.options) {
                    html += `<option value="${selectOption.value}">${selectOption.label}</option>`;
                }
    
                html += `</select></div>`;
            } else { // Resto de tipos de opciones (checkbox, text, etc.)
                html += `
                    <div>
                        <label for="${option.id}">${option.label}:</label>
                        <input type="${option.type}" id="${option.id}" name="${option.id.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase()}" ${option.value ? `value="${option.value}"` : ''}>
                    </div>
                `;
            }
        }
        html += `</form>`;
        return html;
    }

    // Llamadas a handleFileUpload utilizando la configuración
    handleFileUpload('EasyCode', 'easycodeFileInput', 'easycodeForm', 'easycodeMessage', '/process-easycode-resumen', {
        title: uploadOptions.EasyCode.title,
        html: generateOptionsHTML(uploadOptions.EasyCode)
    });

    handleFileUpload('runBat', 'runBatFileInput', 'runBatForm', 'runBatMessage', '/run-bat-form', {
        title: uploadOptions.runBat.title,
        html: generateOptionsHTML(uploadOptions.runBat)
    });    

    handleFileUpload('NETOS', 'fileInput', 'uploadForm', 'message', '/run-python-script', {
        title: uploadOptions.NETOS.title,
        html: generateOptionsHTML(uploadOptions.NETOS)
    });  

    handleFileUpload('mapeoSpss', 'mapeoSpssFileInput', 'mapeoSpssForm', 'mapeoSpssMessage', '/mapeo-spss', {
        title: uploadOptions.mapeoSpss.title,
        html: generateOptionsHTML(uploadOptions.mapeoSpss)
    });  

    handleFileUpload('formateoArtifac', 'formateoArtifacFileInput', 'formateoArtifacForm', 'formateoArtifacMessage', '/formateo-artifac', {
        title: uploadOptions.formateoArtifac.title,
        html: generateOptionsHTML(uploadOptions.formateoArtifac)
    });  

    handleFileUpload('valBddLdc', 'valBddLdcFileInput', 'valBddLdcForm', 'valBddLdcMessage', '/val-bdd-ldc', {
        title: uploadOptions.valBddLdc.title,
        html: generateOptionsHTML(uploadOptions.valBddLdc)
    });  


});
