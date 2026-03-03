// Vehicle Dashboard JavaScript

// WebSocket connection
let socket;
let currentData = {
    speed: 0,
    rpm: 0,
    coolant: 0,
    warning: false,
    connected: false
};

// Canvas contexts
let speedCanvas, speedCtx;
let rpmCanvas, rpmCtx;

// Animation variables
let targetSpeed = 0;
let currentSpeed = 0;
let targetRpm = 0;
let currentRpm = 0;

// Vehicle state
let engineRunning = false;
let currentTargetSpeed = 0;
let leftIndicatorActive = false;
let rightIndicatorActive = false;
let hazardActive = false;

// Pedal control
let acceleratorPressed = false;
let brakePressed = false;
let pedalInterval = null;
let decelerationInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Initialize WebSocket
    initWebSocket();
    
    // Initialize canvases
    speedCanvas = document.getElementById('speedCanvas');
    speedCtx = speedCanvas.getContext('2d');
    rpmCanvas = document.getElementById('rpmCanvas');
    rpmCtx = rpmCanvas.getContext('2d');
    
    // Start animation loop
    animate();
    
    // Add Enter key handler for custom command
    document.getElementById('customCommand').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendCustomCommand();
        }
    });
});

// WebSocket initialization
function initWebSocket() {
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('vehicle_update', function(data) {
        console.log('Received data:', data);
        updateDashboard(data);
    });
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.add('connected');
        indicator.classList.remove('disconnected');
        statusText.textContent = 'Connected';
    } else {
        indicator.classList.add('disconnected');
        indicator.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Update dashboard with new data
function updateDashboard(data) {
    currentData = data;
    
    // Update target values for smooth animation
    targetSpeed = data.speed || 0;
    targetRpm = data.rpm || 0;
    
    // Update temperature
    updateTemperature(data.coolant || 0);
    
    // Update warning lights
    updateWarningLights(data);
    
    // Update gear display
    updateGearDisplay(data.speed || 0);
    
    // Update connection status
    updateConnectionStatus(data.connected !== false);
}

// Draw speedometer gauge
function drawSpeedometer(speed) {
    const centerX = speedCanvas.width / 2;
    const centerY = speedCanvas.height / 2;
    const radius = 140;
    
    // Clear canvas
    speedCtx.clearRect(0, 0, speedCanvas.width, speedCanvas.height);
    
    // Draw outer circle
    speedCtx.beginPath();
    speedCtx.arc(centerX, centerY, radius + 10, 0, 2 * Math.PI);
    speedCtx.strokeStyle = '#333';
    speedCtx.lineWidth = 20;
    speedCtx.stroke();
    
    // Draw colored arc (active portion)
    const maxSpeed = 200;
    const startAngle = 0.75 * Math.PI;
    const endAngle = 2.25 * Math.PI;
    const speedAngle = startAngle + (speed / maxSpeed) * (endAngle - startAngle);
    
    speedCtx.beginPath();
    speedCtx.arc(centerX, centerY, radius + 10, startAngle, speedAngle);
    
    // Color gradient based on speed
    let color;
    if (speed < 60) {
        color = '#00ff00';
    } else if (speed < 120) {
        color = '#ffaa00';
    } else {
        color = '#ff0000';
    }
    
    speedCtx.strokeStyle = color;
    speedCtx.lineWidth = 20;
    speedCtx.stroke();
    
    // Draw tick marks
    for (let i = 0; i <= maxSpeed; i += 20) {
        const angle = startAngle + (i / maxSpeed) * (endAngle - startAngle);
        const isMajor = i % 40 === 0;
        
        const innerRadius = radius - (isMajor ? 25 : 15);
        const outerRadius = radius;
        
        const x1 = centerX + innerRadius * Math.cos(angle);
        const y1 = centerY + innerRadius * Math.sin(angle);
        const x2 = centerX + outerRadius * Math.cos(angle);
        const y2 = centerY + outerRadius * Math.sin(angle);
        
        speedCtx.beginPath();
        speedCtx.moveTo(x1, y1);
        speedCtx.lineTo(x2, y2);
        speedCtx.strokeStyle = '#888';
        speedCtx.lineWidth = isMajor ? 3 : 1;
        speedCtx.stroke();
        
        // Draw numbers for major ticks
        if (isMajor) {
            const textRadius = radius - 45;
            const textX = centerX + textRadius * Math.cos(angle);
            const textY = centerY + textRadius * Math.sin(angle);
            
            speedCtx.fillStyle = '#aaa';
            speedCtx.font = '14px Arial';
            speedCtx.textAlign = 'center';
            speedCtx.textBaseline = 'middle';
            speedCtx.fillText(i.toString(), textX, textY);
        }
    }
    
    // Draw needle
    const needleAngle = startAngle + (speed / maxSpeed) * (endAngle - startAngle);
    const needleLength = radius - 20;
    
    speedCtx.beginPath();
    speedCtx.moveTo(centerX, centerY);
    speedCtx.lineTo(
        centerX + needleLength * Math.cos(needleAngle),
        centerY + needleLength * Math.sin(needleAngle)
    );
    speedCtx.strokeStyle = '#ff0000';
    speedCtx.lineWidth = 3;
    speedCtx.stroke();
    
    // Draw center circle
    speedCtx.beginPath();
    speedCtx.arc(centerX, centerY, 10, 0, 2 * Math.PI);
    speedCtx.fillStyle = '#ff0000';
    speedCtx.fill();
    
    // Update digital display
    document.getElementById('speedValue').textContent = Math.round(speed);
}

// Draw tachometer gauge (RPM)
function drawTachometer(rpm) {
    const centerX = rpmCanvas.width / 2;
    const centerY = rpmCanvas.height / 2;
    const radius = 140;
    
    // Clear canvas
    rpmCtx.clearRect(0, 0, rpmCanvas.width, rpmCanvas.height);
    
    // Draw outer circle
    rpmCtx.beginPath();
    rpmCtx.arc(centerX, centerY, radius + 10, 0, 2 * Math.PI);
    rpmCtx.strokeStyle = '#333';
    rpmCtx.lineWidth = 20;
    rpmCtx.stroke();
    
    // Draw colored arc (active portion)
    const maxRpm = 8000;
    const startAngle = 0.75 * Math.PI;
    const endAngle = 2.25 * Math.PI;
    const rpmAngle = startAngle + (rpm / maxRpm) * (endAngle - startAngle);
    
    rpmCtx.beginPath();
    rpmCtx.arc(centerX, centerY, radius + 10, startAngle, rpmAngle);
    
    // Color gradient based on RPM
    let color;
    if (rpm < 3000) {
        color = '#00ff00';
    } else if (rpm < 6000) {
        color = '#ffaa00';
    } else {
        color = '#ff0000';
    }
    
    rpmCtx.strokeStyle = color;
    rpmCtx.lineWidth = 20;
    rpmCtx.stroke();
    
    // Draw tick marks
    for (let i = 0; i <= maxRpm; i += 1000) {
        const angle = startAngle + (i / maxRpm) * (endAngle - startAngle);
        const isMajor = i % 1000 === 0;
        
        const innerRadius = radius - (isMajor ? 25 : 15);
        const outerRadius = radius;
        
        const x1 = centerX + innerRadius * Math.cos(angle);
        const y1 = centerY + innerRadius * Math.sin(angle);
        const x2 = centerX + outerRadius * Math.cos(angle);
        const y2 = centerY + outerRadius * Math.sin(angle);
        
        rpmCtx.beginPath();
        rpmCtx.moveTo(x1, y1);
        rpmCtx.lineTo(x2, y2);
        rpmCtx.strokeStyle = '#888';
        rpmCtx.lineWidth = isMajor ? 3 : 1;
        rpmCtx.stroke();
        
        // Draw numbers for major ticks
        if (isMajor) {
            const textRadius = radius - 45;
            const textX = centerX + textRadius * Math.cos(angle);
            const textY = centerY + textRadius * Math.sin(angle);
            
            rpmCtx.fillStyle = '#aaa';
            rpmCtx.font = '14px Arial';
            rpmCtx.textAlign = 'center';
            rpmCtx.textBaseline = 'middle';
            rpmCtx.fillText((i / 1000).toString(), textX, textY);
        }
    }
    
    // Draw red zone (6000-8000 RPM)
    const redZoneStart = startAngle + (6000 / maxRpm) * (endAngle - startAngle);
    rpmCtx.beginPath();
    rpmCtx.arc(centerX, centerY, radius + 10, redZoneStart, endAngle);
    rpmCtx.strokeStyle = 'rgba(255, 0, 0, 0.3)';
    rpmCtx.lineWidth = 20;
    rpmCtx.stroke();
    
    // Draw needle
    const needleAngle = startAngle + (rpm / maxRpm) * (endAngle - startAngle);
    const needleLength = radius - 20;
    
    rpmCtx.beginPath();
    rpmCtx.moveTo(centerX, centerY);
    rpmCtx.lineTo(
        centerX + needleLength * Math.cos(needleAngle),
        centerY + needleLength * Math.sin(needleAngle)
    );
    rpmCtx.strokeStyle = '#ff0000';
    rpmCtx.lineWidth = 3;
    rpmCtx.stroke();
    
    // Draw center circle
    rpmCtx.beginPath();
    rpmCtx.arc(centerX, centerY, 10, 0, 2 * Math.PI);
    rpmCtx.fillStyle = '#ff0000';
    rpmCtx.fill();
    
    // Update digital display
    document.getElementById('rpmValue').textContent = Math.round(rpm);
}

// Update temperature display
function updateTemperature(temp) {
    const tempValue = document.getElementById('tempValue');
    const tempFill = document.getElementById('tempFill');
    
    tempValue.textContent = temp.toFixed(1);
    
    // Calculate fill percentage (assuming normal range 0-150°C)
    const fillPercent = Math.min((temp / 150) * 100, 100);
    tempFill.style.width = fillPercent + '%';
    
    // Change color based on temperature
    if (temp > 100) {
        tempValue.style.color = '#ff0000';
        tempValue.style.textShadow = '0 0 8px rgba(255, 0, 0, 0.6)';
    } else if (temp > 80) {
        tempValue.style.color = '#ffaa00';
        tempValue.style.textShadow = '0 0 8px rgba(255, 170, 0, 0.6)';
    } else {
        tempValue.style.color = '#00aaff';
        tempValue.style.textShadow = '0 0 8px rgba(0, 170, 255, 0.6)';
    }
}

// Update warning lights
function updateWarningLights(data) {
    const engineWarning = document.getElementById('engineWarning');
    const tempWarning = document.getElementById('tempWarning');
    
    // Engine warning (activate if RPM > 6000)
    if (data.rpm > 6000) {
        engineWarning.classList.add('active');
    } else {
        engineWarning.classList.remove('active');
    }
    
    // Temperature warning (activate if coolant > 100)
    if (data.coolant > 100) {
        tempWarning.classList.add('active');
    } else {
        tempWarning.classList.remove('active');
    }
}

// Smooth animation loop
function animate() {
    // Smooth interpolation for speed
    const speedDiff = targetSpeed - currentSpeed;
    currentSpeed += speedDiff * 0.1;
    
    // Smooth interpolation for RPM
    const rpmDiff = targetRpm - currentRpm;
    currentRpm += rpmDiff * 0.1;
    
    // Draw gauges
    drawSpeedometer(currentSpeed);
    drawTachometer(currentRpm);
    
    // Continue animation
    requestAnimationFrame(animate);
}

// Send command to STM32
function sendCommand(command) {
    console.log('Sending command:', command);
    socket.emit('send_command', { command: command });
}

// Send custom command
function sendCustomCommand() {
    const input = document.getElementById('customCommand');
    const command = input.value.trim();
    
    if (command) {
        sendCommand(command);
        input.value = '';
    }
}

// ============================================
// Vehicle Control Functions
// ============================================

// Engine Start/Stop
function toggleEngine() {
    engineRunning = !engineRunning;
    
    const engineSwitch = document.getElementById('engineSwitch');
    const engineSwitchButton = document.getElementById('engineSwitchButton');
    const engineSwitchText = document.getElementById('engineSwitchText');
    const engineStatus = document.getElementById('engineStatus');
    
    if (engineRunning) {
        engineSwitch.classList.add('on');
        engineStatus.classList.add('on');
        engineSwitchText.textContent = 'STOP';
        engineStatus.textContent = 'ENGINE ON';
        
        // Set initial idle speed when engine starts
        currentTargetSpeed = 0;
        sendCommand('veh speed 0');
    } else {
        engineSwitch.classList.remove('on');
        engineStatus.classList.remove('on');
        engineSwitchText.textContent = 'START';
        engineStatus.textContent = 'ENGINE OFF';
        
        // Stop the vehicle when engine is off
        currentTargetSpeed = 0;
        targetSpeed = 0;
        currentSpeed = 0;
        targetRpm = 0;
        currentRpm = 0;
        sendCommand('veh speed 0');
        
        // Stop any deceleration intervals
        if (decelerationInterval) {
            clearInterval(decelerationInterval);
            decelerationInterval = null;
        }
        
        // Turn off all indicators
        if (leftIndicatorActive || rightIndicatorActive || hazardActive) {
            toggleIndicator('off');
            if (hazardActive) toggleHazard();
        }
    }
}

// Pedal Controls
function pedalPressed(pedalType) {
    if (!engineRunning && pedalType === 'accelerator') {
        return; // Can't accelerate if engine is off
    }
    
    const pedal = document.getElementById(pedalType + 'Pedal');
    pedal.classList.add('pressed');
    
    if (pedalType === 'accelerator') {
        acceleratorPressed = true;
        // Stop natural deceleration if it's running
        if (decelerationInterval) {
            clearInterval(decelerationInterval);
            decelerationInterval = null;
        }
        startPedalControl();
    } else if (pedalType === 'brake') {
        brakePressed = true;
        // Stop natural deceleration if it's running
        if (decelerationInterval) {
            clearInterval(decelerationInterval);
            decelerationInterval = null;
        }
        startPedalControl();
    }
}

function pedalReleased(pedalType) {
    const pedal = document.getElementById(pedalType + 'Pedal');
    pedal.classList.remove('pressed');
    
    if (pedalType === 'accelerator') {
        acceleratorPressed = false;
        // Start natural deceleration when gas is released
        if (engineRunning && !brakePressed) {
            startNaturalDeceleration();
        }
    } else if (pedalType === 'brake') {
        brakePressed = false;
    }
    
    if (!acceleratorPressed && !brakePressed) {
        stopPedalControl();
    }
}

function startPedalControl() {
    if (pedalInterval) return; // Already running
    
    pedalInterval = setInterval(() => {
        if (acceleratorPressed && engineRunning) {
            // Increase speed (max 180 km/h)
            currentTargetSpeed = Math.min(currentTargetSpeed + 5, 180);
            sendCommand('veh speed ' + Math.round(currentTargetSpeed));
        }
        
        if (brakePressed) {
            // Decrease speed (min 0 km/h)
            currentTargetSpeed = Math.max(currentTargetSpeed - 8, 0);
            sendCommand('veh speed ' + Math.round(currentTargetSpeed));
        }
    }, 200); // Update every 200ms
}

function stopPedalControl() {
    if (pedalInterval) {
        clearInterval(pedalInterval);
        pedalInterval = null;
    }
}

// Natural deceleration when gas pedal is released
function startNaturalDeceleration() {
    // Clear any existing deceleration interval
    if (decelerationInterval) {
        clearInterval(decelerationInterval);
    }
    
    decelerationInterval = setInterval(() => {
        // Stop if brake is pressed or gas is pressed again
        if (brakePressed || acceleratorPressed) {
            clearInterval(decelerationInterval);
            decelerationInterval = null;
            return;
        }
        
        // Gradually decrease speed (slower than braking)
        if (currentTargetSpeed > 0) {
            currentTargetSpeed = Math.max(currentTargetSpeed - 2, 0);
            sendCommand('veh speed ' + Math.round(currentTargetSpeed));
        } else {
            // Stop deceleration when speed reaches 0
            clearInterval(decelerationInterval);
            decelerationInterval = null;
        }
    }, 500); // Update every 500ms for natural deceleration
}

// Indicator Controls
function toggleIndicator(direction) {
    if (!engineRunning) return; // Can't use indicators if engine is off
    
    const leftBtn = document.getElementById('leftIndicatorBtn');
    const rightBtn = document.getElementById('rightIndicatorBtn');
    const leftLight = document.getElementById('indicatorLeft');
    const rightLight = document.getElementById('indicatorRight');
    
    // Turn off hazards if they're on
    if (hazardActive) {
        toggleHazard();
    }
    
    if (direction === 'left') {
        leftIndicatorActive = !leftIndicatorActive;
        
        if (leftIndicatorActive) {
            leftBtn.classList.add('active');
            leftLight.classList.add('active');
            // Turn off right indicator
            rightIndicatorActive = false;
            rightBtn.classList.remove('active');
            rightLight.classList.remove('active');
        } else {
            leftBtn.classList.remove('active');
            leftLight.classList.remove('active');
        }
    } else if (direction === 'right') {
        rightIndicatorActive = !rightIndicatorActive;
        
        if (rightIndicatorActive) {
            rightBtn.classList.add('active');
            rightLight.classList.add('active');
            // Turn off left indicator
            leftIndicatorActive = false;
            leftBtn.classList.remove('active');
            leftLight.classList.remove('active');
        } else {
            rightBtn.classList.remove('active');
            rightLight.classList.remove('active');
        }
    } else if (direction === 'off') {
        // Turn off all indicators
        leftIndicatorActive = false;
        rightIndicatorActive = false;
        leftBtn.classList.remove('active');
        rightBtn.classList.remove('active');
        leftLight.classList.remove('active');
        rightLight.classList.remove('active');
    }
}

// Hazard Lights
function toggleHazard() {
    if (!engineRunning) return; // Can't use hazards if engine is off
    
    hazardActive = !hazardActive;
    
    const hazardBtn = document.querySelector('.hazard-btn');
    const leftBtn = document.getElementById('leftIndicatorBtn');
    const rightBtn = document.getElementById('rightIndicatorBtn');
    const leftLight = document.getElementById('indicatorLeft');
    const rightLight = document.getElementById('indicatorRight');
    
    if (hazardActive) {
        hazardBtn.classList.add('active');
        
        // Activate both indicators
        leftBtn.classList.add('active');
        rightBtn.classList.add('active');
        leftLight.classList.add('active');
        rightLight.classList.add('active');
        
        leftIndicatorActive = true;
        rightIndicatorActive = true;
    } else {
        hazardBtn.classList.remove('active');
        
        // Deactivate both indicators
        leftBtn.classList.remove('active');
        rightBtn.classList.remove('active');
        leftLight.classList.remove('active');
        rightLight.classList.remove('active');
        
        leftIndicatorActive = false;
        rightIndicatorActive = false;
    }
}

// Update gear display based on speed
function updateGearDisplay(speed) {
    const gearDisplay = document.getElementById('gearDisplay');
    
    if (!engineRunning) {
        gearDisplay.textContent = 'P';
        return;
    }
    
    if (speed === 0) {
        gearDisplay.textContent = 'N';
    } else if (speed < 20) {
        gearDisplay.textContent = '1';
    } else if (speed < 40) {
        gearDisplay.textContent = '2';
    } else if (speed < 60) {
        gearDisplay.textContent = '3';
    } else if (speed < 80) {
        gearDisplay.textContent = '4';
    } else if (speed < 100) {
        gearDisplay.textContent = '5';
    } else {
        gearDisplay.textContent = '6';
    }
}
