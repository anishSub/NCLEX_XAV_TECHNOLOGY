/* --- GLOBAL QUESTION COUNTER --- */
window.currentQuestionNumber = window.currentQuestionNumber || 0;

/* --- PART 1: THE SWITCH --- */
function renderQuestion(questionData) {
    try {
        console.log('🎯 renderQuestion called with ID:', questionData.id, 'Type:', questionData.type);

        // Increment and update question counter
        window.currentQuestionNumber++;
        const counterElement = document.getElementById('current-q');
        if (counterElement) {
            counterElement.textContent = window.currentQuestionNumber;
        }

        // CRITICAL: Update global question metadata for validation
        window.activeQuestionId = questionData.id;
        window.activeQuestionType = questionData.type;

        const layout = document.getElementById('exam-layout');
        const scenarioPanel = document.getElementById('scenario-panel');
        const displayArea = document.getElementById('question-display-area');

        if (questionData.is_case_study) {
            layout.classList.add('split-layout');
            scenarioPanel.classList.remove('hidden');
            renderExhibits(questionData.scenario.exhibits);
        } else {
            layout.classList.remove('split-layout');
            scenarioPanel.classList.add('hidden');
        }

        switch (questionData.type) {
            case 'DRAG_DROP_RATIONALE':
                displayArea.innerHTML = createDragDropHTML(questionData);
                initDragAndDropLogic();
                break;
            case 'SATA':
                displayArea.innerHTML = createSATAHTML(questionData);
                break;
            case 'MATRIX_MULTIPLE': // New Case for the Grid
                displayArea.innerHTML = createMatrixMultipleHTML(questionData);
                break;
            case 'MCQ':
                displayArea.innerHTML = createMCQHTML(questionData);
                break;
            case 'DROPDOWN_RATIONALE':
                displayArea.innerHTML = createDropdownRationaleHTML(questionData);
                break;

            case 'HOT_SPOT':
                displayArea.innerHTML = createHotSpotHTML(questionData);
                initHotSpotLogic();
                break;

            case 'HIGHLIGHT_TEXT':
                displayArea.innerHTML = createHighlightTextHTML(questionData);
                initHighlightTextLogic();
                break;
        }

        console.log('✅ renderQuestion SUCCESS');
    } catch (err) {
        console.error('❌ renderQuestion FAILED:', err);
        console.error('Stack:', err.stack);
    }
}

/* --- PART 2: THE BUILDER --- */
function createDragDropHTML(data) {
    const well1 = data.options.answer_wells.well1.map(opt =>
        `<div class="draggable" draggable="true" data-val="${opt}">${opt}</div>`
    ).join('');

    const well2 = data.options.answer_wells.well2.map(opt =>
        `<div class="draggable" draggable="true" data-val="${opt}">${opt}</div>`
    ).join('');

    return `
      <div class="rationale-sentence">
            The client is at risk for 
            <div class="drop-zone" id="target-well1" data-well="1"></div> 
            due to 
            <div class="drop-zone" id="target-well2" data-well="2"></div>.
        </div>
        <div class="wells-grid">
            <div class="source-well" id="source-well1">${well1}</div>
            <div class="source-well" id="source-well2">${well2}</div>
        </div>
    `;
}

//createMCQHTML function. Without this, standard multiple-choice questions won't render at all.
function createMCQHTML(data) {
    const optionsHTML = data.options.map(opt => `
        <div class="mcq-option">
            <label class="radio-container">
                <input type="radio" name="mcq-choice" value="${opt.id}">
                <span class="radiomark"></span>
                <span class="option-text">${opt.text}</span>
            </label>
        </div>
    `).join('');

    return `
        <div class="q-header"><p class="q-text">${data.text}</p></div>
        <div class="mcq-options-container">${optionsHTML}</div>
    `;
}


/* --- NEW PART: THE SATA BUILDER --- */
function createSATAHTML(data) {
    // data.options is your JSONField array: [{"id": "A", "text": "Mark the site"}, ...]
    const optionsHTML = data.options.map(opt => `
        <div class="sata-option">
            <label class="checkbox-container">
                <input type="checkbox" name="sata-choice" value="${opt.id}">
                <span class="checkmark"></span>
                <span class="option-text">${opt.text}</span>
            </label>
        </div>
    `).join('');

    return `
        <div class="q-header">
            <span class="badge sata-badge">Select All That Apply</span>
            <p class="q-text">${data.text}</p>
        </div>
        <div class="sata-options-container">
            ${optionsHTML}
        </div>
    `;
}

/* --- PART 3: THE INTERACTION --- */
function initDragAndDropLogic() {
    const draggables = document.querySelectorAll('.draggable');
    const dropZones = document.querySelectorAll('.drop-zone');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', () => draggable.classList.add('dragging'));
        draggable.addEventListener('dragend', () => draggable.classList.remove('dragging'));
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('hovered'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('hovered'));
        zone.addEventListener('drop', e => {
            const dragging = document.querySelector('.dragging');
            // Check if the dragged item belongs to the correct Well
            if (dragging.parentElement.id.includes(zone.dataset.well)) {
                zone.innerHTML = dragging.innerText;
                zone.dataset.selectedVal = dragging.dataset.val; // Store for submission
            }
            zone.classList.remove('hovered');
        });
    });
}


/* --- PART 3: THE MATRIX BUILDER --- */
function createMatrixMultipleHTML(data) {
    // data.options: { 
    //   rows: ["Fever", "Confusion", "Urinary Frequency"], 
    //   columns: ["Diabetic Ketoacidosis", "Urinary Tract Infection", "HHS"] 
    // }
    const { rows, columns } = data.options;

    const headerHTML = `
        <thead>
            <tr>
                <th>Findings</th>
                ${columns.map(col => `<th>${col}</th>`).join('')}
            </tr>
        </thead>
    `;

    const rowsHTML = rows.map((rowText, rowIndex) => {
        const cells = columns.map((colText, colIndex) => `
            <td class="matrix-cell">
                <input type="checkbox" 
                      name="matrix-row-${rowIndex}" 
                      data-row="${rowText}" 
                      data-col="${colText}">
            </td>
        `).join('');

        return `<tr><td class="row-label">${rowText}</td>${cells}</tr>`;
    }).join('');

    return `
        <div class="q-header">
            <span class="badge">Matrix Multiple Response</span>
            <p class="q-text">${data.text}</p>
        </div>
        <div class="matrix-scroll-container">
            <table class="matrix-table">
                ${headerHTML}
                <tbody>${rowsHTML}</tbody>
            </table>
        </div>
    `;
}


/* --- PART 2: THE DROPDOWN BUILDER --- */
function createDropdownRationaleHTML(data) {
    // data.options format: { 
    //   template: "A priority concern for the client is [dropdown1] as evidenced by [dropdown2] and [dropdown3].",
    //   dropdowns: {
    //      "dropdown1": ["Dehydration", "Infection", "Hypoglycemia"],
    //      "dropdown2": ["Fever", "Thirst"],
    //      "dropdown3": ["Tachycardia", "Dry skin"]
    //   }
    // }
    let html = data.options.template;

    // Replace the [dropdownX] placeholders with actual HTML select tags
    Object.keys(data.options.dropdowns).forEach(key => {
        const optionsHTML = data.options.dropdowns[key].map(opt =>
            `<option value="${opt}">${opt}</option>`
        ).join('');

        const selectTag = `
            <select class="cloze-select" id="${key}">
                <option value="" disabled selected>Select...</option>
                ${optionsHTML}
            </select>
        `;
        html = html.replace(`[${key}]`, selectTag);
    });

    return `
        <div class="q-header">
            <span class="badge">Cloze Dropdown Rationale</span>
            <p class="q-text">${data.text}</p>
        </div>
        <div class="cloze-container">
            ${html}
        </div>
    `;
}


/* --- PART 2: THE HOT SPOT BUILDER --- */
function createHotSpotHTML(data) {
    // data.options format: { image_url: "/media/anatomy/chest.jpg" }
    return `
        <div class="q-header">
            <span class="badge">Hot Spot</span>
            <p class="q-text">${data.text}</p>
        </div>
        <div class="hotspot-wrapper">
            <img src="${data.options.image_url}" id="hotspot-img" alt="Clinical Diagram">
            <div id="click-marker" style="display: none;"></div>
        </div>
    `;
}



/* --- PART 3: THE INTERACTION --- */
function initHotSpotLogic() {
    const img = document.getElementById('hotspot-img');
    const marker = document.getElementById('click-marker');

    img.addEventListener('click', function (e) {
        const rect = img.getBoundingClientRect();

        // Calculate click position as percentages (0-100)
        const xPercent = ((e.clientX - rect.left) / rect.width) * 100;
        const yPercent = ((e.clientY - rect.top) / rect.height) * 100;

        // Save coordinates to a hidden dataset for the collector
        img.dataset.lastX = xPercent.toFixed(2);
        img.dataset.lastY = yPercent.toFixed(2);

        // Visual feedback: Place a marker where the user clicked
        marker.style.left = xPercent + "%";
        marker.style.top = yPercent + "%";
        marker.style.display = "block";
    });
}


/* --- PART 2: THE BUILDERS & INITIALIZERS --- */
function createHighlightTextHTML(data) {
    return `
        <div class="q-header"><span class="badge">Highlight Text</span><p>${data.text}</p></div>
        <div class="chart-container">
            <div class="chart-header">Orders: 1215</div>
            <div class="chart-content">${data.options.formatted_text}</div>
        </div>`;
}

function initHighlightTextLogic() {
    document.querySelectorAll('.highlightable').forEach(span => {
        span.addEventListener('click', function () { this.classList.toggle('highlighted'); });
    });
}



// for scenario based questions
function renderExhibits(exhibits) {
    const tabs = document.getElementById('scenario-tabs');
    const content = document.getElementById('scenario-content');

    // Create Tab Buttons for each key in the JSON (History, Vitals, etc.)
    tabs.innerHTML = Object.keys(exhibits).map(tabName =>
        `<button class="tab-btn" onclick="showTab('${tabName}')">${tabName.replace('_', ' ')}</button>`
    ).join('');

    // Default to show the first tab
    window.currentExhibits = exhibits;
    showTab(Object.keys(exhibits)[0]);
}

function showTab(name) {
    document.getElementById('scenario-content').innerHTML = window.currentExhibits[name];
}





let totalSeconds = 5 * 60 * 60; // 5 Hours

function startTimer() {
    const timerDisplay = document.getElementById('timer');
    const interval = setInterval(() => {
        let hours = Math.floor(totalSeconds / 3600);
        let minutes = Math.floor((totalSeconds % 3600) / 60);
        let seconds = totalSeconds % 60;

        timerDisplay.innerText = `${hours}:${minutes}:${seconds}`;

        if (totalSeconds <= 0) {
            clearInterval(interval);
            alert("Time is up!");
            submitFinalResult(); // End exam
        }
        totalSeconds--;
    }, 1000);
}

// Function to send answer to Django and get the next adaptive question
//This logic handles the background communication so the page never has to refresh.
/* 2. How this fits into your Mock Test workflowStudent Clicks "Submit": Your JS captures the answer (e.g., which boxes were checked in a SATA question).fetch() kicks in: It sends the data to the API URL you defined in urls.py.Django Processes: The NCLEXScoringService grades the answer, and the NCLEXAdaptiveEngine updates the student's Theta ($\theta$) and Standard Error.Stopping Rule Check: Django checks if the 95% Confidence Interval has cleared the passing line.Response: Django sends back a JSON package. Your JS receives it and either changes the question on the screen or ends the test. */


async function submitAnswer(sessionId, questionId, userAnswer) {
    const url = `/exam/api/session/${sessionId}/submit/`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                question_id: questionId,
                user_answer: userAnswer
            })
        });

        const data = await response.json();

        console.log('=== API RESPONSE DEBUG ===');
        console.log('Response status:', response.status);
        console.log('Data:', data);
        console.log('Status field:', data.status);
        console.log('Has next_question?:', !!data.next_question);

        if (data.status === "CONTINUE") {
            console.log('✅ CONTINUE - Rendering next question');
            console.log('Next question data:', data.next_question);
            // Smoothly move to next question
            renderQuestion(data.next_question);

        } else if (data.status === "FINISHED") {
            // --- UPDATED: Beautiful Success Modal ---
            Swal.fire({
                icon: 'success',
                title: 'Exam Completed',
                text: 'The computer has determined your performance level with 95% certainty.',
                timer: 3000,
                showConfirmButton: false,
                allowOutsideClick: false
            }).then(() => {
                window.location.href = `/exam/results/${sessionId}/`;
            });

        } else if (data.status === "EXPIRED") {
            // --- OPTIONAL: Added SweetAlert for Expiration too ---
            Swal.fire({
                icon: 'error',
                title: "Time's Up!",
                text: "The 5-hour limit has been reached. Redirecting to results.",
                confirmButtonText: 'View Results'
            }).then(() => {
                window.location.href = `/exam/results/${sessionId}/`;
            });
        }
    } catch (error) {
        console.error("Error submitting answer:", error);
        Swal.fire({
            icon: 'error',
            title: 'Connection Error',
            text: 'Could not reach the server. Please check your Docker containers.'
        });
    }
}

/* --- We will modify your submission trigger. Instead of just sending the data, we will first check if the answer is empty. If it is, we show a beautiful warning. If the student has selected an answer, we can even show a "Processing..." loader while your 95% Confidence Engine calculates the next question.--- */
/* --- UPDATED SUBMISSION TRIGGER --- */

async function handleUserSubmit() {
    const currentQuestionType = window.activeQuestionType; // Ensure you store this on render
    const sessionId = window.activeSessionId;
    const questionId = window.activeQuestionId;

    // 1. Get the data from our fixed collector
    const answers = getSelectedAnswers(currentQuestionType);

    // Debug logging
    console.log('=== SUBMIT DEBUG ===');
    console.log('Question Type:', currentQuestionType);
    console.log('Answers:', answers);
    console.log('Is Array?:', Array.isArray(answers));
    if (Array.isArray(answers)) console.log('Array Length:', answers.length);

    // 2. If nothing is selected, show a beautiful SweetAlert
    // Check for null/undefined, empty string, OR empty array (for SATA questions)
    if (!answers || answers === '' || (Array.isArray(answers) && answers.length === 0)) {
        Swal.fire({
            icon: 'warning',
            title: 'Empty Answer',
            text: 'Please select an answer before proceeding to the next question.',
            confirmButtonColor: '#004a99',
            confirmButtonText: 'Got it!'
        });
        return;
    }

    // 3. Transform the submit button to show loading state
    const submitBtn = document.querySelector('.submit-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
            <div style="width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
            <span>Processing...</span>
        </div>
    `;

    // 4. Send to your Django API
    await submitAnswer(sessionId, questionId, answers);

    // 5. Restore the button after the response
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
}



/* --- PART 3: THE COLLECTOR (Complete) --- */
function getSelectedAnswers(type) {
    let answers = null;

    switch (type) {
        case 'HOT_SPOT':
            const img = document.getElementById('hotspot-img');
            // Ensure the user actually clicked before collecting
            if (img && img.dataset.lastX && img.dataset.lastY) {
                answers = {
                    x: parseFloat(img.dataset.lastX),
                    y: parseFloat(img.dataset.lastY)
                };
            }
            break;

        case 'SATA':
            const checkboxes = document.querySelectorAll('input[name="sata-choice"]:checked');
            answers = Array.from(checkboxes).map(cb => cb.value);
            break;

        case 'DRAG_DROP_RATIONALE':
            // Now this matches the IDs in our fixed builder
            const w1 = document.getElementById('target-well1').innerText.trim();
            const w2 = document.getElementById('target-well2').innerText.trim();
            // BOTH wells must be filled
            if (w1 && w2) answers = { well1: w1, well2: w2 };
            break;

        case 'DROPDOWN_RATIONALE':
            const dropdownResults = {};
            let dropdownCount = 0;
            document.querySelectorAll('.cloze-select').forEach(select => {
                if (select.value) {
                    dropdownResults[select.id] = select.value;
                    dropdownCount++;
                }
            });
            if (dropdownCount > 0) answers = dropdownResults;
            break;

        case 'MATRIX_MULTIPLE':
            const matrixChoices = [];
            const checkedBoxes = document.querySelectorAll('.matrix-table input[type="checkbox"]:checked');
            checkedBoxes.forEach(box => {
                matrixChoices.push({
                    finding: box.dataset.row,
                    diagnosis: box.dataset.col
                });
            });
            if (matrixChoices.length > 0) answers = matrixChoices;
            break;

        case 'HIGHLIGHT_TEXT':
            const highlightedIds = [];
            document.querySelectorAll('.highlightable.highlighted').forEach(span => {
                highlightedIds.push(span.id);
            });
            if (highlightedIds.length > 0) answers = highlightedIds;
            break;

        case 'MCQ':
            const selectedRadio = document.querySelector('input[name="mcq-choice"]:checked');
            console.log('MCQ Debug - Selected Radio:', selectedRadio);
            console.log('MCQ Debug - All radios:', document.querySelectorAll('input[name="mcq-choice"]'));
            console.log('MCQ Debug - All checked radios:', document.querySelectorAll('input[type="radio"]:checked'));
            if (selectedRadio) {
                answers = selectedRadio.value;
                console.log('MCQ Debug - Selected value:', answers);
            }
            break;
    }

    // Return the collected answers (validation handled in handleSubmit)
    return answers;
}