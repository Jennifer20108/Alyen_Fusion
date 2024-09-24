document.addEventListener('DOMContentLoaded', () => {

    async function handleFileUpload(buttonId, fileInputId, formId, messageId, processUrl, dialogOptions) {
        const button = document.getElementById(buttonId);
        const fileInput = document.getElementById(fileInputId);
        const form = document.getElementById(formId);
        const message = document.getElementById(messageId);

        if (button && fileInput && form && message) {
            button.addEventListener('click', async () => {
                if ('showOpenFilePicker' in window) {
                    try {
                        const handles = await window.showOpenFilePicker({
                            multiple: true,
                            types: [
                                {
                                    description: dialogOptions.fileDescription || 'Archivos',
                                    accept: { 'application/octet-stream': ['.mtd'] },
                                },
                            ],
                        });

                        Swal.fire({
                            title: dialogOptions.title || 'Opciones',
                            html: dialogOptions.html || '',
                            focusConfirm: false,
                            confirmButtonText: dialogOptions.confirmButtonText || 'Subir Archivo',
                            preConfirm: () => {
                                const optionsForm = document.getElementById('easycodeOptionsForm') || document.getElementById('runBatOptionsForm');
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

                                for (const handle of handles) {
                                    const file = await handle.getFile();
                                    const formData = new FormData();

                                    // Añade los datos del formulario a FormData
                                    Object.keys(result.value).forEach(key => formData.append(key, result.value[key]));

                                    const fileContent = await file.arrayBuffer();
                                    const blob = new Blob([fileContent], { type: file.type });
                                    formData.append('file', blob, file.name);

                                    try {
                                        const response = await fetch(processUrl, {
                                            method: 'POST',
                                            body: formData
                                        });

                                        const data = await response.json();

                                        Swal.fire({
                                            title: 'Éxito',
                                            text: 'Archivo procesado correctamente.',
                                            icon: 'success',
                                            showCancelButton: true,
                                            confirmButtonText: 'Descargar Archivo',
                                            cancelButtonText: 'Cancelar'
                                        }).then((result) => {
                                            if (result.isConfirmed) {
                                                window.location.href = `/download/${data.filePath}`;
                                            }
                                        });

                                    } catch (error) {
                                        Swal.close();
                                        Swal.fire({
                                            title: 'Error',
                                            text: `Ocurrió un error inesperado al procesar ${file.name}: ${error}`,
                                            icon: 'error'
                                        });
                                    }
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

            fileInput.addEventListener('change', () => {
                const files = fileInput.files;
                if (files.length === 0) {
                    Swal.fire({
                        title: 'No File Selected',
                        text: 'Por favor, selecciona uno o más archivos antes de continuar.',
                        icon: 'warning',
                    });
                    return;
                }

                Swal.fire({
                    title: dialogOptions.title || 'Opciones',
                    html: dialogOptions.html || '',
                    focusConfirm: false,
                    confirmButtonText: dialogOptions.confirmButtonText || 'Subir Archivo',
                    preConfirm: () => {
                        const optionsForm = document.getElementById('easycodeOptionsForm') || document.getElementById('runBatOptionsForm');
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
                        console.log("Form options (file input):", options); // Verifica los valores del formulario
                        return options;
                    }
                }).then(result => {
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

                        const formData = new FormData(form);
                        Object.keys(result.value).forEach(key => formData.append(key, result.value[key]));

                        for (const file of files) {
                            formData.append('file', file);
                        }

                        fetch(processUrl, {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            Swal.close();
                            if (data.error) {
                                Swal.fire({
                                    title: 'Error',
                                    text: `Ocurrió un error: ${data.message}`,
                                    icon: 'error'
                                });
                            } else {
                                Swal.fire({
                                    title: 'Éxito',
                                    text: 'Archivo procesado correctamente.',
                                    icon: 'success',
                                    showCancelButton: true,
                                    confirmButtonText: 'Descargar Archivo',
                                    cancelButtonText: 'Cancelar'
                                }).then((result) => {
                                    if (result.isConfirmed) {
                                        window.location.href = `/download/${data.filePath}`;
                                    }
                                });
                            }
                        })
                        .catch(error => {
                            Swal.close();
                            Swal.fire({
                                title: 'Error',
                                text: `Ocurrió un error inesperado: ${error}`,
                                icon: 'error'
                            });
                        });
                    }
                });
            });
        }
    }

    // Opciones personalizadas para EASY-CODING:
    const easyCodingOptions = {
        title: 'Opciones de EASY-CODING',
        html: `
            <form id="easycodeOptionsForm">
                <div>
                    <label for="removeNet">Eliminar columnas NET_:</label>
                    <input type="checkbox" id="removeNet" name="remove_net">
                </div>
                <div>
                    <label for="formatHeaders">Formatear encabezados:</label>
                    <input type="checkbox" id="formatHeaders" name="format_headers">
                </div>
                <div>
                    <label for="newHeader">Nuevo encabezado:</label>
                    <input type="text" id="newHeader" name="new_header" value="InterviewID">
                </div>
            </form>
        `,
    };

    handleFileUpload('EasyCode', 'easycodeFileInput', 'easycodeForm', 'easycodeMessage', '/process-easycode-resumen', easyCodingOptions);

    // Opciones personalizadas para RUN BAT:
    const runBatOptions = {
        title: 'Opciones de RUN BAT',
        html: `
            <form id="runBatOptionsForm">
                <div>
                    <label for="someOption">Alguna opción:</label>
                    <input type="checkbox" id="someOption" name="some_option">
                </div>
            </form>
        `,
        confirmButtonText: 'Generar Script'
    };

    handleFileUpload('runBat', 'runBatFileInput', 'runBatForm', 'runBatMessage', '/run-bat-form', runBatOptions);
    handleFileUpload('NETOS', 'fileInput', 'uploadForm', 'message', '/run-python-script', runBatOptions);
    handleFileUpload('mapeoSpss', 'mapeoSpssFileInput', 'mapeoSpssForm', 'mapeoSpssMessage', '/mapeo-spss', runBatOptions);
    handleFileUpload('formateoArtifac', 'formateoArtifacFileInput', 'formateoArtifacForm', 'formateoArtifacMessage', '/formateo-artifac', runBatOptions);
    handleFileUpload('valBddLdc', 'valBddLdcFileInput', 'valBddLdcForm', 'valBddLdcMessage', '/val-bdd-ldc', runBatOptions);
});
