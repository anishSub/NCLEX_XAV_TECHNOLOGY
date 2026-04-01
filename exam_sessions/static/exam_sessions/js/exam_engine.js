/* --- GLOBAL QUESTION COUNTER --- */
window.currentQuestionNumber = window.currentQuestionNumber || 0;

function buildQuestionShell(data, answerContent, metaContent = '') {
    return `
        <article class="exam-question-shell">
            <header class="exam-question-header">
                ${metaContent ? `<div class="exam-question-meta">${metaContent}</div>` : ''}
                <div class="q-header">
                    <p class="q-text">${data.text}</p>
                </div>
            </header>
            <section class="exam-answer-section">
                ${answerContent}
            </section>
        </article>
    `;
}

/* --- PART 1: THE SWITCH --- */
function renderQuestion(questionData) {
    try {
        console.log('🎯 renderQuestion called with ID:', questionData.id, 'Type:', questionData.type);

        // NORMALIZE QUESTION TYPE: Handle "HOT SPOT", "hot_spot", etc.
        const normalizedType = questionData.type.toUpperCase().replace(/\s+/g, '_');
        console.log(`🔄 Normalized Type: ${questionData.type} -> ${normalizedType}`);

        // Increment and update question counter
        window.currentQuestionNumber++;
        const counterElement = document.getElementById('current-q');
        if (counterElement) {
            counterElement.textContent = window.currentQuestionNumber;
        }

        // CRITICAL: Update global question metadata for validation
        window.activeQuestionId = questionData.id;
        window.activeQuestionType = normalizedType; // Use normalized type

        const layout = document.getElementById('exam-layout');
        const scenarioPanel = document.getElementById('scenario-panel');
        const displayArea = document.getElementById('question-display-area');

        if (questionData.is_case_study) {
            // SAFETY CHECK: Ensure scenario data exists
            if (!questionData.scenario) {
                console.error('❌ Case Study flag is TRUE but scenario data is MISSING!', questionData);
                // Fallback to standard layout to prevent crash
                layout.classList.remove('split-layout');
                scenarioPanel.classList.add('hidden');
            } else {
                layout.classList.add('split-layout');
                scenarioPanel.classList.remove('hidden');

                // Render exhibits with updates
                renderExhibits(
                    questionData.scenario.exhibits,
                    questionData.exhibit_updates || {}
                );

                // Show intro modal on first question of scenario
                if (questionData.scenario_question_number === 1) {
                    showScenarioIntro(questionData.scenario.title);
                }

                // Update progress indicator
                updateScenarioProgress(
                    questionData.scenario_question_number,
                    questionData.scenario.title,
                    questionData.clinical_judgment_function
                );
            }
        } else {
            layout.classList.remove('split-layout');
            scenarioPanel.classList.add('hidden');
        }

        switch (normalizedType) {
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
                console.log('🔥 Rendering HOT_SPOT question');
                displayArea.innerHTML = createHotSpotHTML(questionData);
                initHotSpotLogic();
                break;

            case 'HIGHLIGHT_TEXT':
                displayArea.innerHTML = createHighlightTextHTML(questionData);
                initHighlightTextLogic();
                break;

            default:
                console.error(`❌ Unknown Question Type: ${normalizedType}`);
                displayArea.innerHTML = `
                    <div class="alert alert-danger">
                        <h4>Error: Unknown Question Type</h4>
                        <p>The system received a question type it doesn't know how to render: <strong>${normalizedType}</strong> (Original: ${questionData.type})</p>
                        <p>ID: ${questionData.id}</p>
                    </div>
                `;
        }

        console.log('✅ renderQuestion SUCCESS');
    } catch (err) {
        console.error('❌ renderQuestion FAILED:', err);
        console.error('Stack:', err.stack);
    }
}

/* --- PART 2: THE BUILDER (NCLEX SINGLE COLUMN FORMAT) --- */
function createDragDropHTML(data) {
    // Get all well keys dynamically (well1, well2, well3, etc.)
    const wellKeys = Object.keys(data.options.answer_wells);

    // Combine ALL options into single list (NCLEX format)
    let allOptions = [];
    wellKeys.forEach(wellKey => {
        allOptions = allOptions.concat(data.options.answer_wells[wellKey]);
    });
    const uniqueOptions = [...new Set(allOptions)];
    const draggablesHTML = uniqueOptions.map(opt =>
        `<div class="draggable" draggable="true" data-val="${opt}">${opt}</div>`
    ).join('');

    // Replace [well1], [well2], [well3], etc. with drop zones
    let sentenceHTML = data.options.template;
    wellKeys.forEach((wellKey, index) => {
        const dropZone = `<div class="drop-zone" id="target-${wellKey}" data-well="${index + 1}"></div>`;
        sentenceHTML = sentenceHTML.replace(`[${wellKey}]`, dropZone);
    });

    return buildQuestionShell(
        data,
        `
            <div class="rationale-sentence">
                ${sentenceHTML}
            </div>
            <div class="answer-choices-header">Answer Choices</div>
            <div class="source-well-single">
                ${draggablesHTML}
            </div>
        `
    );
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

    return buildQuestionShell(
        data,
        `<div class="mcq-options-container">${optionsHTML}</div>`,
        `<span class="badge">Single Best Answer</span>`
    );
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

    return buildQuestionShell(
        data,
        `<div class="sata-options-container">${optionsHTML}</div>`,
        `<span class="badge sata-badge">Select All That Apply</span>`
    );
}

/* --- PART 3: THE INTERACTION (NCLEX FORMAT) --- */
function initDragAndDropLogic() {
    const draggables = document.querySelectorAll('.draggable');
    const dropZones = document.querySelectorAll('.drop-zone');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', () => draggable.classList.add('dragging'));
        draggable.addEventListener('dragend', () => draggable.classList.remove('dragging'));
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            zone.classList.add('hovered');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('hovered'));
        zone.addEventListener('drop', e => {
            const dragging = document.querySelector('.dragging');
            if (dragging) {
                // Allow ANY option to go in ANY well (real NCLEX behavior)
                zone.innerHTML = dragging.innerText;
                zone.dataset.selectedVal = dragging.dataset.val;
                // Hide the dragged item so it can only be used once
                dragging.style.opacity = '0.3';
                dragging.style.pointerEvents = 'none';
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

    return buildQuestionShell(
        data,
        `
            <div class="matrix-scroll-container">
                <table class="matrix-table">
                    ${headerHTML}
                    <tbody>${rowsHTML}</tbody>
                </table>
            </div>
        `,
        `<span class="badge">Matrix Multiple Response</span>`
    );
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

    return buildQuestionShell(
        data,
        `
            <div class="cloze-container">
                ${html}
            </div>
        `,
        `<span class="badge">Cloze Dropdown Rationale</span>`
    );
}


/* --- PART 2: THE HOT SPOT BUILDER --- */
function createHotSpotHTML(data) {
    // data.options format: { image_url: "/media/anatomy/chest.jpg" }

    // AUTO-FIX: Legacy images might be missing /media/ prefix
    let imageUrl = data.options.image_url;
    if (imageUrl && !imageUrl.startsWith('/media/') && !imageUrl.startsWith('http') && !imageUrl.startsWith('data:')) {
        if (imageUrl.startsWith('/')) {
            imageUrl = '/media' + imageUrl;
        } else {
            imageUrl = '/media/' + imageUrl;
        }
        console.log('🔧 Auto-fixed Hot Spot Image URL:', imageUrl);
    }

    return buildQuestionShell(
        data,
        `
            <div class="hotspot-frame">
                <div class="hotspot-instruction">🖱️ Point and click on the specific area in the diagram below to select your answer.</div>
                <div class="hotspot-wrapper">
                    <img src="${imageUrl}" id="hotspot-img" alt="Clinical Diagram">
                    <div id="click-marker" style="display: none;"></div>
                </div>
            </div>
        `,
        `<span class="badge">Hot Spot</span>`
    );
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

        console.log(`🎯 Hot Spot Clicked: x=${xPercent.toFixed(2)}%, y=${yPercent.toFixed(2)}%`);
        console.log(`💡 Copy this for Admin: {"center_x": ${xPercent.toFixed(2)}, "center_y": ${yPercent.toFixed(2)}, "radius": 5}`);
    });
}


/* --- PART 2: THE BUILDERS & INITIALIZERS --- */
function createHighlightTextHTML(data) {
    return buildQuestionShell(
        data,
        `
            <div class="chart-container">
                <div class="chart-header">Orders: 1215</div>
                <div class="chart-content">${data.options.formatted_text}</div>
            </div>
        `,
        `<span class="badge">Highlight Text</span>`
    );
}

function initHighlightTextLogic() {
    document.querySelectorAll('.highlightable').forEach((span, index) => {
        // CRITICAL FIX: Ensure span has an ID for the collector
        if (!span.id) {
            span.id = `hl-span-${index}`;
        }
        span.addEventListener('click', function () { this.classList.toggle('highlighted'); });
    });
}



// ========== SCENARIO EXHIBIT RENDERING ==========
function renderExhibits(baseExhibits, exhibitUpdates = {}) {
    const tabs = document.getElementById('scenario-tabs');
    const content = document.getElementById('scenario-content');

    // Merge base exhibits with question-specific updates
    const mergedExhibits = { ...baseExhibits, ...exhibitUpdates };

    // Track which tabs are new/updated for highlighting
    const updatedTabNames = Object.keys(exhibitUpdates);

    // Create Tab Buttons with "NEW" badges for updated tabs
    tabs.innerHTML = Object.keys(mergedExhibits).map(tabName => {
        const isNew = updatedTabNames.includes(tabName);
        const badgeHTML = isNew ? '<span class="new-badge">NEW</span>' : '';
        const tabClass = isNew ? 'tab-btn tab-updated' : 'tab-btn';

        return `
            <button class="${tabClass}" onclick="showTab('${tabName}')">
                ${tabName.replace(/_/g, ' ')} ${badgeHTML}
            </button>
        `;
    }).join('');

    // Store merged exhibits globally
    window.currentExhibits = mergedExhibits;

    // Default to show the first tab
    showTab(Object.keys(mergedExhibits)[0]);
}

function showTab(name) {
    const content = document.getElementById('scenario-content');
    const allTabs = document.querySelectorAll('.tab-btn');

    // Remove active class from all tabs
    allTabs.forEach(tab => tab.classList.remove('active'));

    // Add active class to clicked tab
    const clickedTab = Array.from(allTabs).find(tab =>
        tab.textContent.replace('NEW', '').trim() === name.replace(/_/g, ' ')
    );
    if (clickedTab) {
        clickedTab.classList.add('active');
    }

    // Display content
    content.innerHTML = window.currentExhibits[name];
}

// ========== SCENARIO UI ENHANCEMENTS ==========
function showScenarioIntro(title) {
    Swal.fire({
        icon: 'info',
        title: 'Unfolding Case Study',
        html: `
            <p><strong>${title}</strong></p>
            <p>You will answer 6 questions about this patient scenario.</p>
            <p>Review the exhibit tabs for clinical information.</p>
            <p style="font-size: 0.9em; color: #666; margin-top: 15px;">
                💡 Tip: New information may appear as you progress through the questions.
            </p>
        `,
        confirmButtonText: 'Begin Case Study',
        confirmButtonColor: '#004a99',
        allowOutsideClick: false
    });
}

function updateScenarioProgress(questionNum, scenarioTitle, cjFunction) {
    const scenarioPanel = document.getElementById('scenario-panel');

    // Remove existing progress indicator if any
    const existingProgress = scenarioPanel.querySelector('.scenario-progress');
    if (existingProgress) {
        existingProgress.remove();
    }

    // Create new progress indicator
    const progressHTML = `
        <div class="scenario-progress">
            <div class="scenario-title">📋 ${scenarioTitle}</div>
            <div class="scenario-question-num">Question ${questionNum} of 6</div>
            ${cjFunction ? `<div class="cj-function-badge"><strong>CJ Function:</strong> ${cjFunction}</div>` : ''}
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${(questionNum / 6) * 100}%"></div>
            </div>
        </div>
    `;

    // Insert at the top of scenario panel
    scenarioPanel.insertAdjacentHTML('afterbegin', progressHTML);
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


async function submitAnswer(sessionId, questionId, userAnswer, customUrl = null) {
    const url = customUrl || `/exam/api/session/${sessionId}/submit/`;

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
            // --- UPDATED: Success Modal ---
            let titleText = 'Exam Completed';
            let bodyText = 'The computer has determined your performance level with 95% certainty.';

            // Customize for Practice Mode
            if (window.practiceMode) {
                titleText = 'Practice Session Completed';
                bodyText = 'You have completed all questions in this session.';
            }

            Swal.fire({
                icon: 'success',
                title: titleText,
                text: bodyText,
                timer: 3000,
                showConfirmButton: false,
                allowOutsideClick: false
            }).then(() => {
                if (window.practiceMode) {
                    window.location.href = `/exam/practice/results/${sessionId}/`;
                } else {
                    window.location.href = `/exam/results/${sessionId}/`;
                }
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

async function handleUserSubmit(customUrl = null) {
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
    await submitAnswer(sessionId, questionId, answers, customUrl);

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
            // Dynamically collect all wells (well1, well2, well3, etc.)
            const dropZones = document.querySelectorAll('.drop-zone');
            const wellAnswers = {};
            let allFilled = true;

            dropZones.forEach(zone => {
                const wellId = zone.id.replace('target-', '');
                const value = zone.innerText.trim();

                if (value) {
                    wellAnswers[wellId] = value;
                } else {
                    allFilled = false;
                }
            });

            // Only return if ALL wells are filled
            if (allFilled && Object.keys(wellAnswers).length > 0) {
                answers = wellAnswers;
            }
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
