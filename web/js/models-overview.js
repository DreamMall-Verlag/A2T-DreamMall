// js/models-overview.js
// Modell-Übersicht JavaScript-Modul

// Load models overview on page load
async function loadModelsOverview() {
    console.log('🔄 Loading models overview...');
    const container = document.getElementById('modelsOverviewContent');
    
    if (!container) {
        console.error('❌ Models overview container not found');
        return;
    }
    
    try {
        const response = await fetch('/api/v1/models/overview');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📄 Models overview data received:', data);
        
        // Generate overview HTML
        const overviewHTML = generateModelsOverviewHTML(data);
        container.innerHTML = overviewHTML;
        console.log('✅ Models overview loaded successfully');
        
    } catch (error) {
        console.error('❌ Failed to load models overview:', error);
        container.innerHTML = generateErrorHTML(error.message);
    }
}

// Generate models overview HTML
function generateModelsOverviewHTML(data) {
    return `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            ${generateWhisperModelCard(data.models.whisper)}
            ${generatePyAnnoteModelCard(data.models.pyannote)}
            ${generateOllamaModelCard(data.models.ollama)}
        </div>
        ${generateServiceConfigCard(data)}
    `;
}

// Generate Whisper model card
function generateWhisperModelCard(whisper) {
    const statusClass = whisper.status === 'loaded' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
    const statusText = whisper.status === 'loaded' ? '✅ Geladen' : '❌ Nicht geladen';
    
    return `
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border-l-4 border-blue-500 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
                <h3 class="text-lg font-semibold text-blue-800 flex items-center">
                    🎤 Whisper
                    <span class="ml-2 px-2 py-1 text-xs font-medium rounded-full ${statusClass}">
                        ${statusText}
                    </span>
                </h3>
            </div>
            <div class="space-y-2 text-sm">
                <div><span class="font-medium">Modell:</span> ${whisper.current_model}</div>
                <div><span class="font-medium">Größe:</span> ${whisper.model_info?.size_mb || 'Unbekannt'} MB</div>
                <div><span class="font-medium">Geschwindigkeit:</span> ${whisper.model_info?.speed || 'Unbekannt'}</div>
                <div><span class="font-medium">Device:</span> ${whisper.device || 'CPU'}</div>
                <div class="pt-2">
                    <span class="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        ${Object.keys(whisper.available_models || {}).length} Modelle verfügbar
                    </span>
                </div>
            </div>
        </div>
    `;
}

// Generate PyAnnote model card
function generatePyAnnoteModelCard(pyannote) {
    const statusClass = pyannote.status === 'loaded' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
    const statusText = pyannote.status === 'loaded' ? '✅ Geladen' : '❌ Nicht geladen';
    
    const capabilitiesHTML = pyannote.capabilities?.map(cap => {
        const capText = cap === 'speaker_diarization' ? '🎯 Speaker-Erkennung' : 
                       cap === 'voice_activity_detection' ? '🔊 Sprach-Erkennung' : cap;
        return `<div class="text-xs text-green-600 bg-green-50 px-2 py-1 rounded inline-block mr-1 mb-1">${capText}</div>`;
    }).join('') || '<div class="text-xs text-gray-500">Keine Features verfügbar</div>';
    
    return `
        <div class="bg-gradient-to-r from-green-50 to-green-100 border-l-4 border-green-500 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
                <h3 class="text-lg font-semibold text-green-800 flex items-center">
                    👥 PyAnnote
                    <span class="ml-2 px-2 py-1 text-xs font-medium rounded-full ${statusClass}">
                        ${statusText}
                    </span>
                </h3>
            </div>
            <div class="space-y-2 text-sm">
                <div><span class="font-medium">Modell:</span> speaker-diarization-3.1</div>
                <div><span class="font-medium">HF Token:</span> ${pyannote.auth_token === 'configured' ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}</div>
                <div><span class="font-medium">Features:</span></div>
                <div class="ml-4 space-y-1">
                    ${capabilitiesHTML}
                </div>
            </div>
        </div>
    `;
}

// Generate Ollama model card
function generateOllamaModelCard(ollama) {
    const statusClass = ollama.status === 'available' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
    const statusText = ollama.status === 'available' ? '✅ Verfügbar' : '❌ Nicht verfügbar';
    
    const modelsHTML = ollama.available_models?.length > 0 ? `
        <div class="pt-2 max-h-24 overflow-y-auto">
            ${ollama.available_models.slice(0, 3).map(model => 
                `<div class="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded mb-1 truncate">
                    ${model.name} (${model.size_formatted})
                </div>`
            ).join('')}
            ${ollama.available_models.length > 3 ? 
                `<div class="text-xs text-purple-500">... und ${ollama.available_models.length - 3} weitere</div>` : ''
            }
        </div>
    ` : '';
    
    return `
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border-l-4 border-purple-500 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
                <h3 class="text-lg font-semibold text-purple-800 flex items-center">
                    🦙 Ollama
                    <span class="ml-2 px-2 py-1 text-xs font-medium rounded-full ${statusClass}">
                        ${statusText}
                    </span>
                </h3>
            </div>
            <div class="space-y-2 text-sm">
                <div><span class="font-medium">Server:</span> ${ollama.base_url}</div>
                <div><span class="font-medium">Standard:</span> ${ollama.default_model}</div>
                <div><span class="font-medium">Version:</span> ${ollama.server_version || 'Unbekannt'}</div>
                <div><span class="font-medium">Modelle:</span> ${ollama.available_models?.length || 0} geladen</div>
                ${modelsHTML}
            </div>
        </div>
    `;
}

// Generate service configuration card
function generateServiceConfigCard(data) {
    const audioFormatsHTML = data.configuration?.audio_formats?.map(format => 
        `<span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">${format.toUpperCase()}</span>`
    ).join('') || '<span class="text-xs text-gray-500">Keine Formate gefunden</span>';
    
    return `
        <div class="mt-6 bg-gray-50 rounded-lg p-4">
            <h4 class="text-md font-semibold text-gray-800 mb-3 flex items-center">
                ⚙️ Service-Konfiguration
            </h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                    <span class="font-medium text-gray-600">Sprache:</span>
                    <div class="text-gray-800">${data.configuration?.language || 'de'}</div>
                </div>
                <div>
                    <span class="font-medium text-gray-600">Status:</span>
                    <div class="text-green-600 font-medium">${data.service_status || 'unbekannt'}</div>
                </div>
                <div>
                    <span class="font-medium text-gray-600">Speicher (Whisper):</span>
                    <div class="text-gray-800">${data.memory_usage?.estimated_whisper_size || 'Unbekannt'}</div>
                </div>
                <div>
                    <span class="font-medium text-gray-600">Letztes Update:</span>
                    <div class="text-gray-800">${new Date(data.timestamp).toLocaleTimeString('de-DE')}</div>
                </div>
            </div>
            
            <div class="mt-3 pt-3 border-t border-gray-200">
                <span class="font-medium text-gray-600">Unterstützte Audio-Formate:</span>
                <div class="mt-1 flex flex-wrap gap-1">
                    ${audioFormatsHTML}
                </div>
            </div>
        </div>
    `;
}

// Generate error HTML
function generateErrorHTML(errorMessage) {
    return `
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-center">
                <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <div>
                    <h3 class="text-red-800 font-medium">Fehler beim Laden der Modell-Übersicht</h3>
                    <p class="text-red-600 text-sm mt-1">${errorMessage}</p>
                </div>
            </div>
            <button onclick="loadModelsOverview()" class="mt-3 text-red-600 hover:text-red-800 text-sm underline">
                🔄 Erneut versuchen
            </button>
        </div>
    `;
}

// Initialize models overview when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadModelsOverview);
} else {
    loadModelsOverview();
}

// Add refresh button functionality
document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refreshModelsOverview');
    if (refreshButton) {
        refreshButton.addEventListener('click', loadModelsOverview);
    }
});
