const ROBOT_API_URL = 'http://localhost:8000/robot';
const VISION_API_URL = 'http://localhost:8000/vision';
const FRAMEGRABBER_API_URL = 'http://localhost:8000/framegrabber';
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

// Load current model when page loads
document.addEventListener('DOMContentLoaded', loadCurrentModel);

document.getElementById('applyModel').addEventListener('click', async () => {
    const selectedModel = document.getElementById('modelSelect').value;
    if (!selectedModel) {
        alert('Пожалуйста, выберите модель');
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
            //alert('Модель успешно применена');
            
        } else {
            alert('Ошибка при применении модели');
        }
    } catch (error) {
        console.error('Error applying model:', error);
        alert('Ошибка при применении модели');
    }
});

async function loadCurrentExposure() {
    try {
        const response = await fetch(FRAMEGRABBER_API_URL + '/get_exposure');
        const data = await response.json();
        document.getElementById('currentExposure').textContent = data.exposure;
    } catch (error) {
        console.error('Error loading current exposure:', error);
    }
}

document.getElementById('calibrateCamera').addEventListener('click', calibrateMarkers);
async function calibrateMarkers() {
    try {
        const response = await fetch(FRAMEGRABBER_API_URL + '/calibrate', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            alert('Калибровка успешно завершена: ' + JSON.stringify(data));
        } else {
            alert('Ошибка при калибровке маркеров');
        }
    } catch (error) {
        console.error('Error calibrating markers:', error);
        alert('Ошибка при калибровке маркеров');
    }
}

document.getElementById('calibrateMarkers').addEventListener('click', calibrateMarkers);

document.getElementById('applyExposure').addEventListener('click', async () => {
    const exposureValue = document.getElementById('exposureValue').value;
    if (!exposureValue || exposureValue < 162 || exposureValue > 900000) {
        alert('Пожалуйста, введите корректное значение экспозиции (162-900000)');
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
            alert('Экспозиция успешно применена');
        } else {
            alert('Ошибка при применении экспозиции');
        }
    } catch (error) {
        console.error('Error applying exposure:', error);
        alert('Ошибка при применении экспозиции');
    }
});

// Load current exposure when page loads
document.addEventListener('DOMContentLoaded', loadCurrentExposure);

// Fetch models when page loads
document.addEventListener('DOMContentLoaded', fetchModels);
setInterval(() => {
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