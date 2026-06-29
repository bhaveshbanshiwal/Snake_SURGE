document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('pathCanvas');
    const ctx = canvas.getContext('2d');
    const PIXELS_PER_METER = 50.0;
    const CANVAS_CX = canvas.width / 2;
    const CANVAS_CY = canvas.height / 2;

    let targetPath = [];
    let actualPath = [];
    let robotPose = {x: 0, y: 0, yaw: 0};
    let segments = [];
    
    let isDrawing = false;
    let isRunning = false;

    // --- System Stats Polling ---
    async function updateSystemStats() {
        try {
            const res = await fetch('/api/system_stats');
            const data = await res.json();
            document.getElementById('sys-cpu').textContent = `${data.cpu.toFixed(1)}%`;
            document.getElementById('sys-ram').textContent = `${data.ram.toFixed(1)}%`;
            document.getElementById('sys-temp').textContent = typeof data.temp === 'number' ? `${data.temp.toFixed(1)}°C` : data.temp;
        } catch (e) {
            console.error('Stats error:', e);
        }
    }
    setInterval(updateSystemStats, 2000);
    updateSystemStats();

    // --- Status & Telemetry Polling ---
    async function updateStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            isRunning = data.is_running;
            document.getElementById('conn-status').textContent = data.status;
            document.getElementById('status-dot').className = isRunning ? 'dot active' : 'dot';
            document.getElementById('btn-connect').textContent = isRunning ? 'Disconnect Engine' : 'Connect Engine';

            robotPose = data.robot_pose;
            actualPath = data.actual_path;
            segments = data.segments || [];
            
            // Update Telemetry UI
            const grid = document.getElementById('telemetry-grid');
            grid.innerHTML = '';
            
            const dxlIds = Object.keys(data.telemetry).map(Number).sort((a,b) => a - b);
            
            for (const id of dxlIds) {
                const m = data.telemetry[id];
                const deg = ((m.position - 2048) * (360.0 / 4096.0)).toFixed(1);
                const torque = (m.load * (0.22 / 1500.0)).toFixed(3);
                
                const box = document.createElement('div');
                box.className = 'telem-box';
                box.innerHTML = `
                    <div class="motor-id">MOTOR ${id}</div>
                    <div class="data-row"><span>Angle:</span> <span>${deg}°</span></div>
                    <div class="data-row"><span>Speed:</span> <span>${m.velocity}</span></div>
                    <div class="data-row"><span>Torque:</span> <span>${torque} Nm</span></div>
                `;
                grid.appendChild(box);
            }
            
            renderCanvas();
        } catch (e) {
            console.error('Status error:', e);
        }
    }
    setInterval(updateStatus, 100);

    // --- Controls ---
    document.getElementById('btn-connect').addEventListener('click', async () => {
        const engine = document.querySelector('input[name="engine"]:checked').value;
        await fetch('/api/connect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({engine: engine})
        });
    });

    document.getElementById('btn-clear').addEventListener('click', async () => {
        targetPath = [];
        actualPath = [];
        await sendPath();
        renderCanvas();
    });

    document.getElementById('btn-generate').addEventListener('click', async () => {
        const funcStr = document.getElementById('math-func').value;
        const a = parseFloat(document.getElementById('math-a').value);
        const b = parseFloat(document.getElementById('math-b').value);
        
        targetPath = [];
        try {
            const safeFunc = funcStr
                .replace(/sin/g, 'Math.sin')
                .replace(/cos/g, 'Math.cos')
                .replace(/tan/g, 'Math.tan')
                .replace(/abs/g, 'Math.abs')
                .replace(/sqrt/g, 'Math.sqrt');
                
            for (let x = a; x <= b; x += 0.1) {
                let y = eval(safeFunc.replace(/x/g, `(${x})`));
                targetPath.push([x, y]);
            }
            await sendPath();
            renderCanvas();
        } catch (e) {
            alert('Invalid math function');
        }
    });

    async function sendPath() {
        await fetch('/api/set_path', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: targetPath})
        });
    }

    // --- Canvas Drawing ---
    canvas.addEventListener('mousedown', (e) => {
        isDrawing = true;
        addPoint(e);
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDrawing) addPoint(e);
    });

    canvas.addEventListener('mouseup', async () => {
        isDrawing = false;
        await sendPath();
    });

    function addPoint(e) {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const worldX = (mouseX - CANVAS_CX) / PIXELS_PER_METER;
        const worldY = (CANVAS_CY - mouseY) / PIXELS_PER_METER;
        
        targetPath.push([worldX, worldY]);
        renderCanvas();
    }

    function renderCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let x = 0; x <= canvas.width; x += PIXELS_PER_METER) {
            ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height);
        }
        for (let y = 0; y <= canvas.height; y += PIXELS_PER_METER) {
            ctx.moveTo(0, y); ctx.lineTo(canvas.width, y);
        }
        ctx.stroke();

        // Draw axes
        ctx.strokeStyle = '#666';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(CANVAS_CX, 0); ctx.lineTo(CANVAS_CX, canvas.height);
        ctx.moveTo(0, CANVAS_CY); ctx.lineTo(canvas.width, CANVAS_CY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw Target Path (Blue)
        if (targetPath.length > 1) {
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 3;
            ctx.beginPath();
            for (let i = 0; i < targetPath.length; i++) {
                const px = CANVAS_CX + (targetPath[i][0] * PIXELS_PER_METER);
                const py = CANVAS_CY - (targetPath[i][1] * PIXELS_PER_METER);
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();
        }

        // Draw Actual Path (Pink)
        if (actualPath.length > 1) {
            ctx.strokeStyle = '#ff007f';
            ctx.lineWidth = 2;
            ctx.beginPath();
            for (let i = 0; i < actualPath.length; i++) {
                const px = CANVAS_CX + (actualPath[i][0] * PIXELS_PER_METER);
                const py = CANVAS_CY - (actualPath[i][1] * PIXELS_PER_METER);
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();
        }

        // Draw Snake Segments (if available from SIM)
        if (segments && segments.length > 1) {
            ctx.strokeStyle = '#cc0000';
            ctx.lineWidth = 12;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.beginPath();
            for (let i = 0; i < segments.length; i++) {
                const px = CANVAS_CX + (segments[i][0] * PIXELS_PER_METER);
                const py = CANVAS_CY - (segments[i][1] * PIXELS_PER_METER);
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();
            ctx.lineCap = 'butt'; // reset
        }

        // Draw Robot Position (Red Dot)
        const rx = CANVAS_CX + (robotPose.x * PIXELS_PER_METER);
        const ry = CANVAS_CY - (robotPose.y * PIXELS_PER_METER);
        ctx.fillStyle = '#ff4040';
        ctx.beginPath();
        ctx.arc(rx, ry, 6, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Initial Render
    renderCanvas();
});
