const HOST = window.location.hostname;
const ROBOT_API_URL = `http://${HOST}:8000/robot`;
const VISION_API_URL = `http://${HOST}:8000/vision`;
const FRAMEGRABBER_API_URL = `http://${HOST}:8000/framegrabber`;
const LOGIC_API_URL = `http://${HOST}:8000/logic`;

// Добавьте эту функцию в начало файла после объявления констант
function showNotification(message, type = 'info') {
    // Show popup notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Styles for popup notification
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px';
    notification.style.borderRadius = '5px';
    notification.style.backgroundColor = type === 'error' ? '#ff4444' : '#44ff44';
    notification.style.color = '#fff';
    notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    notification.style.zIndex = '1000';
    notification.style.transition = 'opacity 0.5s ease-in-out';
    
    document.body.appendChild(notification);
    
    // Add to log container
    const logMessages = document.getElementById('logMessages');
    const logEntry = document.createElement('div');
    logEntry.className = `log-message log-${type}`;
    
    // Add timestamp
    const timestamp = new Date().toLocaleTimeString();
    const timestampSpan = document.createElement('span');
    timestampSpan.className = 'log-timestamp';
    timestampSpan.textContent = `[${timestamp}]`;
    
    // Add message
    const messageSpan = document.createElement('span');
    messageSpan.textContent = ` ${message}`;
    
    logEntry.appendChild(timestampSpan);
    logEntry.appendChild(messageSpan);
    
    // Add to top of log
    if (logMessages.firstChild) {
        logMessages.insertBefore(logEntry, logMessages.firstChild);
    } else {
        logMessages.appendChild(logEntry);
    }
    
    // Remove popup notification after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 3000);
}

// Function to fetch models from API
async function fetchModels() {
    try {
        const response = await fetch(VISION_API_URL + '/get_models'); // Adjust URL as needed
        const models = await response.json();
        populateModelDropdown(models);
    } catch (error) {
        console.error('Error fetching models:', error);
    }
}

function populateModelDropdown(models) {
    const modelSelect = document.getElementById('modelSelect');
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model; 
        option.textContent = model; 
        modelSelect.appendChild(option);
    });
}

async function loadCurrentModel() {
    try {
        const response = await fetch(VISION_API_URL + '/get_model');
        const data = await response.json();
        document.getElementById('currentModel').textContent = data.model;
    } catch (error) {
        console.error('Error loading current model:', error);
    }
}

async function loadCurrentExposure() {
    try {
        const response = await fetch(FRAMEGRABBER_API_URL + '/get_exposure');
        const data = await response.json();
        document.getElementById('currentExposure').textContent = data.exposure;
        document.getElementById('exposureValue').value = data.exposure;
    } catch (error) {
        console.error('Error loading current exposure:', error);
    }
}

async function loadCurrentConfidence() {
    console.log('Loading current confidence...');
    try {
        while (!document.getElementById('currentModel').textContent) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        const currentModel = document.getElementById('currentModel').textContent;
        console.log('Current model:', currentModel);
        const response = await fetch(`${VISION_API_URL}/get_confidence?model=${currentModel}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        const data = await response.json();
        console.log('Current confidence:', data.confidence);
        document.getElementById('currentConfidence').textContent = data.confidence;
        document.getElementById('confidenceValue').value = data.confidence;
    } catch (error) {
        console.error('Error loading current confidence:', error);
    }
}

async function loadObjectList() {
    console.log('Loading object list...');
    try {
        const response = await fetch(VISION_API_URL + '/get_objects');
        const objects = await response.json();
        console.log('Objects:', objects);
        const objectList = document.getElementById('objectList');
        objectList.innerHTML = ''; // Clear existing list

        objects.forEach(obj => {
            const listItem = document.createElement('li');
            const [model, subclass, confidence, coordinates] = obj;
            const [x, y, angle] = coordinates.length === 3 ? coordinates : [...coordinates, null];
            listItem.innerHTML = `
                <div style="border: 1px solid #000; padding: 5px; margin: 5px 0">
                    <div>Модель: ${model}</div>
                    <div>Подкласс: ${subclass}</div>
                    <div>Вероятность: ${confidence}</div>
                    <div>Координаты: (${x}, ${y})${angle !== null ? `, Угол: ${angle}` : ''}</div>
                </div>
            `;
            objectList.appendChild(listItem);
        });

        // Update object count
        const objectCount = objects.length;
        const objectCountHeader = document.querySelector('.controls h3');
        objectCountHeader.textContent = `Список объектов (Всего: ${objectCount})`;
    } catch (error) {
        console.error('Error loading object list:', error);
    }
}

async function loadDisplaySettings() {
    try {
        const displayBoxResponse = await fetch(VISION_API_URL + '/get_display_box', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        const displayPoseResponse = await fetch(VISION_API_URL + '/get_display_pose', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        const displayCoordinatesResponse = await fetch(VISION_API_URL + '/get_display_coordinates', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        const displayConfidenceResponse = await fetch(VISION_API_URL + '/get_display_confidence', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        const displayBoxData = await displayBoxResponse.json();
        const displayPoseData = await displayPoseResponse.json();
        const displayCoordinatesData = await displayCoordinatesResponse.json();
        const displayConfidenceData = await displayConfidenceResponse.json();

        console.log('Display settings:', displayBoxData, displayPoseData, displayCoordinatesData, displayConfidenceData);

        document.getElementById('displayBox').checked = displayBoxData.display_box;
        document.getElementById('displayPose').checked = displayPoseData.display_pose;
        document.getElementById('displayCoordinates').checked = displayCoordinatesData.display_coordinates;
        document.getElementById('displayConfidence').checked = displayConfidenceData.display_confidence;
    } catch (error) {
        console.error('Error loading display settings:', error);
    }
}

document.getElementById('sendCommand').addEventListener('click', async () => {
    console.log('Sending command to robot...');
    try {
        const response = await fetch(LOGIC_API_URL + '/next_object', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        console.log(response);
        if (response.ok) {
            const data = await response.json();
            console.log('Next object:', data);
            const [class_id, , , [x, y, a]] = data;
            const robotResponse = await fetch(`${ROBOT_API_URL}/pick?class_id=${class_id}&x=${x}&y=${y}&a=${a}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
            });

            if (robotResponse.ok) {
                showNotification(`Команда успешно отправлена роботу: x=${x}, y=${y}, a=${a}`);
            } else {
                showNotification('Ошибка при отправке команды роботу', 'error');
            }
        } else {
            showNotification('Ошибка при получении следующего объекта', 'error');
        }
    } catch (error) {
        console.error('Error sending command to robot:', error);
        showNotification('Ошибка при отправке команды роботу', 'error');
    }
});

document.getElementById('applyModel').addEventListener('click', async () => {
    const selectedModel = document.getElementById('modelSelect').value;
    if (!selectedModel) {
        showNotification('Пожалуйста, выберите модель', 'error');
        return;
    }

    try {
        const response = await fetch(`${VISION_API_URL}/set_model?model=${selectedModel}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            document.getElementById('currentModel').textContent = selectedModel;
            await loadCurrentConfidence(); // Update confidence after model change
        } else {
            showNotification('Ошибка при применении модели', 'error');
        }
    } catch (error) {
        console.error('Error applying model:', error);
        showNotification('Ошибка при применении модели', 'error');
    }
});

document.getElementById('getOKResponse').addEventListener('click', async () => {
    try {
        const response = await fetch(`${ROBOT_API_URL}/measurement?result=true`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Ответ OK успешно отправлен');
        } else {
            showNotification('Ошибка при отправке ответа OK', 'error');
        }
    } catch (error) {
        console.error('Error sending OK response:', error);
        showNotification('Ошибка при отправке ответа OK', 'error');
    }
});

document.getElementById('getNGResponse').addEventListener('click', async () => {
    try {
        const response = await fetch(`${ROBOT_API_URL}/measurement?result=false`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Ответ NG успешно отправлен');
        } else {
            showNotification('Ошибка при отправке ответа OK', 'error');
        }
    } catch (error) {
        console.error('Error sending NG response:', error);
        showNotification('Ошибка при отправке ответа NG', 'error');
    }
});

document.getElementById('applyConfidence').addEventListener('click', async () => {
    const confidenceValue = document.getElementById('confidenceValue').value;
    if (!confidenceValue || confidenceValue < 0 || confidenceValue > 1) {
        showNotification('Пожалуйста, введите корректное значение уверенности (0-1)');
        return;
    }

    try {
        const currentModel = document.getElementById('currentModel').textContent;
        const response = await fetch(`${VISION_API_URL}/set_confidence?model=${currentModel}&confidence=${confidenceValue}`, {
            method: 'GET',
            headers: {
            'accept': 'application/json',
            }
        });

        if (response.ok) {
            document.getElementById('currentConfidence').textContent = confidenceValue;
            // !!!
            showNotification('Значение уверенности успешно применено');
        } else {
            showNotification('Ошибка при применении значения уверенности', 'error');
        }
    } catch (error) {
        console.error('Error applying confidence:', error);
        showNotification('Ошибка при применении значения уверенности', 'error');
    }
});

document.getElementById('calibrateCamera').addEventListener('click', async () => {
    try {
        const response = await fetch(FRAMEGRABBER_API_URL + '/calibrate', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            showNotification('Калибровка успешно завершена: ' + JSON.stringify(data));
        } else {
            showNotification('Ошибка при калибровке маркеров', 'error');
        }
    } catch (error) {
        console.error('Error calibrating markers:', error);
        showNotification('Ошибка при калибровке маркеров', 'error');
    }
});

document.getElementById('resetCamera').addEventListener('click', async () => {
    try {
        const response = await fetch(FRAMEGRABBER_API_URL + '/uncalibrate', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Сброс калибровки успешно завершен');
        } else {
            showNotification('Ошибка при сбросе калибровки', 'error');
        }
    } catch (error) {
        console.error('Error uncalibrating camera:', error);
        showNotification('Ошибка при сбросе калибровки', 'error');
    }
});

document.getElementById('applyExposure').addEventListener('click', async () => {
    const exposureValue = document.getElementById('exposureValue').value;
    if (!exposureValue || exposureValue < 162 || exposureValue > 900000) {
        showNotification('Пожалуйста, введите корректное значение экспозиции (162-900000)');
        return;
    }

    try {
        const response = await fetch(`${FRAMEGRABBER_API_URL}/set_exposure?exposure=${exposureValue}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            document.getElementById('currentExposure').textContent = exposureValue;
            // !!!
            showNotification('Экспозиция успешно применена');
        } else {
            showNotification('Ошибка при применении экспозиции', 'error');
        }
    } catch (error) {
        console.error('Error applying exposure:', error);
        showNotification('Ошибка при применении экспозиции', 'error');
    }
});

document.getElementById('displayBox').addEventListener('change', async (event) => {
    try {
        const response = await fetch(`${VISION_API_URL}/set_display_box?display_box=${event.target.checked}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Параметр отображения рамки успешно изменен');
        } else {
            showNotification('Ошибка при изменении параметра отображения рамки', 'error');
        }
    } catch (error) {
        console.error('Error changing display box parameter:', error);
        showNotification('Ошибка при изменении параметра отображения рамки', 'error');
    }
});

document.getElementById('displayPose').addEventListener('change', async (event) => {
    try {
        const response = await fetch(`${VISION_API_URL}/set_display_pose?display_pose=${event.target.checked}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Параметр отображения позы успешно изменен');
        } else {
            showNotification('Ошибка при изменении параметра отображения позы', 'error');
        }
    } catch (error) {
        console.error('Error changing display pose parameter:', error);
        showNotification('Ошибка при изменении параметра отображения позы', 'error');
    }
});

document.getElementById('displayCoordinates').addEventListener('change', async (event) => {
    try {
        const response = await fetch(`${VISION_API_URL}/set_display_coordinates?display_coordinates=${event.target.checked}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Параметр отображения координат успешно изменен');
        } else {
            showNotification('Ошибка при изменении параметра отображения координат', 'error');
        }
    } catch (error) {
        console.error('Error changing display coordinates parameter:', error);
        showNotification('Ошибка при изменении параметра отображения координат', 'error');
    }
});

document.getElementById('displayConfidence').addEventListener('change', async (event) => {
    try {
        const response = await fetch(`${VISION_API_URL}/set_display_confidence?display_confidence=${event.target.checked}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });

        if (response.ok) {
            showNotification('Параметр отображения уверенности успешно изменен');
        } else {
            showNotification('Ошибка при изменении параметра отображения уверенности', 'error');
        }
    } catch (error) {
        console.error('Error changing display confidence parameter:', error);
        showNotification('Ошибка при изменении параметра отображения уверенности', 'error');
    }
});

document.addEventListener('DOMContentLoaded', loadDisplaySettings);
document.addEventListener('DOMContentLoaded', loadCurrentModel);
document.addEventListener('DOMContentLoaded', loadCurrentExposure);
document.addEventListener('DOMContentLoaded', loadCurrentConfidence);
document.addEventListener('DOMContentLoaded', fetchModels);

setInterval(() => {
    loadObjectList();
    const robot_status = document.querySelector('.robot-status .status-dot');
    console.log("Checking robot connection...");
    fetch(ROBOT_API_URL + '/connection')
        .then(response => response.json())
        .then(data => {
            if (data.connected) {
                robot_status.classList.remove('status-red');
                robot_status.classList.add('status-green');
            }
            else {
                robot_status.classList.remove('status-green');
                robot_status.classList.add('status-red');
            }
        }
        )
        .catch(error => console.error('Error:', error));
}, 1000);