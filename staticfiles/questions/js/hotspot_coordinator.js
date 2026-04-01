const hsAdmin = (function ($) {
  'use strict';

  /**
   * NUCLEAR Hot Spot Coordinator for Django Admin
   * Supports: Clipboard Paste, File Upload (Base64), Inline/Standalone support.
   */

  function log(msg, obj) {
    console.log(`%c[HS-COORD] ${msg}`, 'background: #17a2b8; color: white; padding: 2px 5px; border-radius: 3px;', obj || '');
  }

  function findElementByLabel(labelText) {
    const labels = document.querySelectorAll('label');
    for (const label of labels) {
      if (label.innerText.includes(labelText)) {
        const targetId = label.getAttribute('for');
        if (targetId) return document.getElementById(targetId);
      }
    }
    return null;
  }

  function initForForm(prefix) {
    log(`Initializing for prefix: ${prefix || 'standalone'}`);

    let typeField = prefix ? document.querySelector(`#id_${prefix}-question_type`) : document.querySelector('#id_question_type');
    let textField = prefix ? document.querySelector(`#id_${prefix}-text`) : document.querySelector('#id_text');
    let optionsField = prefix ? document.querySelector(`#id_${prefix}-options`) : document.querySelector('#id_options');
    let correctField = prefix ? document.querySelector(`#id_${prefix}-correct_option_ids`) : document.querySelector('#id_correct_option_ids');

    // Fallback: Find by label if IDs are weird
    if (!typeField) typeField = findElementByLabel('Question type');
    if (!optionsField) optionsField = findElementByLabel('Options');
    if (!correctField) correctField = findElementByLabel('Correct option IDs');

    if (!typeField || !optionsField || !correctField) {
      log('❌ Missing required fields. Skipping this section.', { typeField, optionsField, correctField });
      return;
    }

    const containerId = prefix ? `hs-tool-${prefix}` : 'hs-tool-standalone';
    if (document.getElementById(containerId)) return;

    log(`✅ Found all fields for ${prefix || 'standalone'}. Creating tool...`);

    // Create the Tool HTML
    const container = document.createElement('div');
    container.id = containerId;
    container.className = 'hotspot-tool-container';
    container.style.cssText = `
      width: 100%;
      max-width: 100%;
      margin: 0 0 15px 0;
      padding: 15px;
      background: #f8f9fa;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      box-sizing: border-box;
      clear: both;
      font-family: Arial, sans-serif;
      display: none;
    `;

    container.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px;">
                <h2 style="margin: 0; color: #117a8b; font-size: 1.4rem; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.8rem;">🎯</span> Hot Spot Coordinator Tool
                </h2>
                <span style="background: #17a2b8; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">NCLEX POINT-AND-CLICK</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px;">
                <!-- Step 1: Image Setup -->
                <div style="border-right: 1px solid #eee; padding-right: 20px;">
                    <h3 style="font-size: 1rem; color: #333; margin-top: 0;">1. Add Your Image</h3>
                    <p style="font-size: 0.85rem; color: #666; margin-bottom: 15px;">Paste a URL OR upload/paste a file below.</p>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: bold; font-size: 0.8rem; margin-bottom: 5px;">Image URL</label>
                        <input type="text" class="hs-url-input" placeholder="https://..." style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>

                    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                        <button type="button" class="hs-load-btn" style="flex: 1; background: #117a8b; color: white; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold;">Load URL</button>
                        <input type="file" class="hs-file-input" style="display: none;" accept="image/*">
                        <button type="button" class="hs-browse-btn" style="flex: 1; background: #6c757d; color: white; border: none; padding: 10px; border-radius: 6px; cursor: pointer; font-weight: bold;">Browse File</button>
                    </div>

                    <div style="background: #f8f9fa; border: 2px dashed #ccc; padding: 15px; text-align: center; border-radius: 8px; font-size: 0.85rem; color: #999; margin-bottom: 20px;">
                        💡 Tip: You can also <strong>Paste (Ctrl+V)</strong> an image file directly while this tool is open!
                    </div>

                    <div style="margin-top: 20px;">
                        <label style="display: block; font-weight: bold; font-size: 0.8rem; margin-bottom: 5px;">2. Hit Zone Size (Radius %)</label>
                        <input type="range" class="hs-radius-slider" min="1" max="25" value="5" style="width: 100%;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #999;">
                            <span>Precise (1%)</span>
                            <span class="hs-radius-val">5%</span>
                            <span>Large (25%)</span>
                        </div>
                    </div>
                </div>

                <!-- Step 2: Point & Click -->
                <div>
                    <h3 style="font-size: 1rem; color: #333; margin-top: 0;">2. Select the Answer Zone</h3>
                    <div class="hs-status" style="margin-bottom: 10px; font-weight: bold; font-size: 0.9rem; color: #dc3545; min-height: 1.2rem;">Waiting for image...</div>
                    
                    <div class="hs-viewbox" style="border: 2px solid #ddd; background: #eee; min-height: 300px; display: flex; align-items: center; justify-content: center; border-radius: 8px; overflow: hidden; padding: 10px;">
                        <!-- TIGHT WRAPPER: Ensures marker is positioned relative to IMAGE, not the flexbox container -->
                        <div style="position: relative; display: inline-block; line-height: 0;">
                            <img class="hs-target-img" style="max-width: 100%; display: none; cursor: crosshair;">
                            <div class="hs-marker" style="position: absolute; border: 3px solid #ff0000; background: rgba(255,0,0,0.3); border-radius: 50%; display: none; transform: translate(-50%, -50%); pointer-events: none; box-shadow: 0 0 10px rgba(0,0,0,0.5); z-index: 100;">
                                <div style="position: absolute; top:50%; left:50%; width: 4px; height:4px; background: #fff; border-radius:50%; transform: translate(-50%, -50%);"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

    // Style and Placement
    // Try to find the best place to insert the tool
    // For Hot Spot Module with virtual field, insert after the image_file input
    const virtualImageInput = document.getElementById('id_image_file');
    let insertTarget = null;

    if (virtualImageInput) {
      // Special case: insert after the virtual image field's row
      insertTarget = virtualImageInput.closest('.form-row') || virtualImageInput.closest('.form-group') || virtualImageInput.parentNode;
      log('Found virtual image field, inserting tool after it.');
    } else {
      // Standard/Inline case: Insert AFTER 'Question Text' if possible, otherwise fallback
      if (textField) {
        insertTarget = textField.closest('.form-row') || textField.closest('.form-group') || textField.parentNode;
        log('Found Question Text field, inserting tool after it.');
      } else {
        insertTarget = correctField.closest('.form-row') || correctField.closest('.form-group') || correctField.parentNode;
        log('Could not find Question Text, falling back to Correct Options field.');
      }
    }

    if (!insertTarget) {
      log('Could not find insert target. Appending to form.');
      insertTarget = optionsField.parentNode;
    }

    // Insert after the target
    if (insertTarget.nextSibling) {
      insertTarget.parentNode.insertBefore(container, insertTarget.nextSibling);
    } else {
      insertTarget.parentNode.appendChild(container);
    }

    // Sub-Elements
    const urlInput = container.querySelector('.hs-url-input');
    const loadBtn = container.querySelector('.hs-load-btn');
    const browseBtn = container.querySelector('.hs-browse-btn');
    const fileInput = container.querySelector('.hs-file-input');
    const radSlider = container.querySelector('.hs-radius-slider');
    const radVal = container.querySelector('.hs-radius-val');
    const img = container.querySelector('.hs-target-img');
    const marker = container.querySelector('.hs-marker');
    const status = container.querySelector('.hs-status');

    // --- SPECIAL HANDLING FOR HOT SPOT MODULE (Virtual Field) ---
    // virtualImageInput was already detected above during container placement
    if (virtualImageInput) {
      log('✨ Configuring Hot Spot Module with virtual image field.');

      // 1. Hide the raw JSON fields immediately
      const optRow = optionsField.closest('.form-row');
      const corRow = correctField.closest('.form-row');
      if (optRow) optRow.style.display = 'none';
      if (corRow) corRow.style.display = 'none';

      // 2. Bind the virtual field to our tool
      virtualImageInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
          log('📂 File selected! Loading into visual tool...');
          const reader = new FileReader();
          reader.onload = (re) => {
            // Force show the tool
            container.style.display = 'block';
            // Load image into the visual card
            setLocalImage(re.target.result, true);
          };
          reader.readAsDataURL(file);
        }
      });

      // 3. Force tool visible immediately (even before upload) so user sees the card
      container.style.display = 'block';
    }

    function updateVisibility() {
      // Robustly get text from Select or Select2
      let text = "";
      if (typeField.tagName === 'SELECT') {
        text = typeField.options[typeField.selectedIndex]?.text || "";
      } else if (typeField.value) {
        // Fallback for weird widgets
      }

      // If text is empty, maybe try to read the rendered Select2 text if it exists
      if (!text && typeField.id) {
        const select2Container = document.querySelector(`#select2-${typeField.id}-container`);
        if (select2Container) text = select2Container.innerText;
      }

      text = text.toUpperCase();
      const value = typeField.value;

      log(`Checking visibility. Text: "${text}", Value: "${value}"`);

      // Rows to toggle
      const optionsRow = optionsField.closest('.form-row') || optionsField.closest('.form-group') || optionsField.parentNode;
      const correctRow = correctField.closest('.form-row') || correctField.closest('.form-group') || correctField.parentNode;

      // Check both Display Name (Text) and Value (Code) for robustness
      // OR if we found the virtualImageInput, we assume we are in the correct mode
      if (text.includes('HOT SPOT') || text.includes('HOT_SPOT') || value === 'HOT_SPOT' || virtualImageInput) {
        container.style.display = 'block';

        // HIDE raw fields for cleaner UI (Enforce hiding again to be safe)
        if (optionsRow) optionsRow.style.display = 'none';
        if (correctRow) correctRow.style.display = 'none';

        // Try to recover URL if it already exists in Options
        try {
          const opts = JSON.parse(optionsField.value);
          if (opts.image_url) {
            // If we haven't loaded it yet (and user didn't just upload a new one)
            // We can check if img.src is empty or different?
            // Just set it. setLocalImage handles repeated calls fine.
            if (!img.src || img.style.display === 'none') {
              urlInput.value = opts.image_url;
              setLocalImage(opts.image_url);
            }
          }
        } catch (e) { }

        // Try to recover Coords if they exist
        try {
          const coords = JSON.parse(correctField.value);
          if (coords.center_x && coords.center_y) {
            img.dataset.savedCoords = JSON.stringify(coords);
          }
        } catch (e) { }

      } else {
        // Only hide if NOT in virtual mode
        if (!virtualImageInput) {
          container.style.display = 'none';
          if (optionsRow) optionsRow.style.display = '';
          if (correctRow) correctRow.style.display = '';
        }
      }
    }

    // Event Binding - Use jQuery to catch Select2 changes and standard changes
    $(typeField).on('change select2:select', updateVisibility);

    // Initial check
    setTimeout(updateVisibility, 500); // Small delay to let Select2 render if needed

    // Image Handling
    function setLocalImage(source, isBase64 = false) {
      status.innerText = '⌛ Processing...';
      status.style.color = '#666';

      // AUTO-FIX: If URL is missing /media/ prefix (legacy data), add it
      if (source && !isBase64 && !source.startsWith('/media/') && !source.startsWith('http') && !source.startsWith('data:')) {
        if (source.startsWith('/')) {
          source = '/media' + source; // /hotspot_images -> /media/hotspot_images
        } else {
          source = '/media/' + source; // hotspot_images -> /media/hotspot_images
        }
        log('🔧 Auto-fixed Image URL:', source);
      }

      img.src = source;
      img.style.display = 'block';

      img.onload = () => {
        status.innerText = '✅ READY: Click the image to set the correct answer!';
        status.style.color = '#198754';

        // Restore marker if saved coords exist
        if (img.dataset.savedCoords) {
          try {
            const coords = JSON.parse(img.dataset.savedCoords);
            const r = coords.radius || 5;
            radSlider.value = r;
            radVal.innerText = `${r}%`;

            marker.style.left = coords.center_x + '%';
            marker.style.top = coords.center_y + '%';
            marker.style.width = (r * 2) + '%';
            marker.style.height = (r * 2) + '%';
            marker.style.display = 'block';
            status.innerText = `🎯 Restored: X:${coords.center_x}%, Y:${coords.center_y}%`;
          } catch (e) { log('Error restoring coords', e); }
        }

        // Update Parent Options JSON
        try {
          const newOptions = { "image_url": source };
          optionsField.value = JSON.stringify(newOptions, null, 4);
          optionsField.style.background = '#e8f5e9';
          setTimeout(() => optionsField.style.background = '', 1000);
        } catch (e) { log('Error updating options field', e); }
      };

      img.onerror = () => {
        status.innerText = '❌ Failed to load image. Check the source.';
        status.style.color = '#dc3545';
      };
    }

    loadBtn.onclick = () => {
      const url = urlInput.value.trim();
      if (url) setLocalImage(url);
    };

    browseBtn.onclick = () => fileInput.click();

    fileInput.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (re) => setLocalImage(re.target.result, true);
        reader.readAsDataURL(file);
      }
    };

    // GLOBAL Clipboard Paste Handler
    window.addEventListener('paste', (e) => {
      // Only handle if this specific container is visible
      if (container.style.display === 'none') return;

      const items = e.clipboardData.items;
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const blob = items[i].getAsFile();
          const reader = new FileReader();
          reader.onload = (re) => {
            log('✨ Image pasted successfully from clipboard!');
            setLocalImage(re.target.result, true);
          };
          reader.readAsDataURL(blob);
        }
      }
    });

    // Click Logic
    img.onclick = function (e) {
      // SET ACTIVE INSTANCE FOR KEYBOARD CONTROL
      activeInstance = {
        marker: marker,
        correctField: correctField,
        radSlider: radSlider,
        status: status
      };

      const rect = img.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      const r = parseInt(radSlider.value);

      // Set Marker
      marker.style.left = x + '%';
      marker.style.top = y + '%';
      marker.style.display = 'block';
      marker.style.width = (r * 2) + '%';
      marker.style.height = (r * 2) + '%';

      // Sync to Correct Answer field
      const result = {
        "center_x": parseFloat(x.toFixed(2)),
        "center_y": parseFloat(y.toFixed(2)),
        "radius": r
      };
      correctField.value = JSON.stringify(result, null, 4);
      correctField.style.background = '#e1f5fe';
      setTimeout(() => correctField.style.background = '', 1000);

      status.innerText = `🎯 Target SAVED: X:${x.toFixed(1)}%, Y:${y.toFixed(1)}% (Radius ${r}%)`;
      status.style.color = '#0056b3';

      // Visual feedback that keyboard is active
      status.innerText += " (Arrow Keys Active)";
    };

    radSlider.oninput = (e) => {
      const r = e.target.value;
      radVal.innerText = `${r}%`;
      if (marker.style.display === 'block') {
        marker.style.width = (r * 2) + '%';
        marker.style.height = (r * 2) + '%';
        // Trigger an update to the JSON with the new radius
        const x = parseFloat(marker.style.left);
        const y = parseFloat(marker.style.top);
        const result = {
          "center_x": parseFloat(x.toFixed(2)),
          "center_y": parseFloat(y.toFixed(2)),
          "radius": parseInt(r)
        };
        correctField.value = JSON.stringify(result, null, 4);
      }
    };
  }

  function scan() {
    log('Scanning page for fields...');

    // 1. Standalone
    initForForm(null);

    // 2. Inlines (Scenario questions)
    // Support both 'questions_set' (default) and 'questions' (related_name) prefixes
    const selectors = [
      '[id^="id_questions_set-"][id$="-question_type"]',
      '[id^="id_questions-"][id$="-question_type"]'
    ];

    const inlines = document.querySelectorAll(selectors.join(','));
    inlines.forEach(el => {
      // Extract prefix responsibly: id_questions-0-question_type -> questions-0
      const parts = el.id.split('-');
      if (parts.length >= 3) {
        // Reconstruct the middle part (prefix-index)
        // id (0) _ prefix (1) - index (2) - field (3) ... roughly
        // Better strategy: remove 'id_' from start and '-question_type' from end
        const prefix = el.id.replace(/^id_/, '').replace(/-question_type$/, '');
        initForForm(prefix);
      }
    });
  }

  // Run on load - with jQuery safety check
  function initialize() {
    // Auto-detect if we are on the specific "Hot Spot Question" admin page
    if (document.body.classList.contains('model-hotspotquestion')) {
      log('🎯 Detected Hot Spot Question Admin Page! forcing init...');
      initForForm(null); // Force init for standalone form

      // Slight delay to ensure visibility is forced open even if question type is hidden
      setTimeout(() => {
        const container = document.getElementById('hs-tool-standalone');
        if (container) container.style.display = 'block';
      }, 100);
    } else {
      scan();
    }

    // Handle dynamic inline adding (if jQuery is available)
    if (typeof $ !== 'undefined' && $.fn) {
      $(document).on('formset:added', (e, $row, formsetName) => {
        // Check for either the standard set or the related_name set
        if (formsetName === 'questions_set' || formsetName === 'questions') {
          log(`Detected new scenario question added (${formsetName}). Initializing tool...`);
          const typeField = $row.find('[id$="-question_type"]');
          const id = typeField.attr('id');
          if (id) {
            const prefix = id.replace(/^id_/, '').replace(/-question_type$/, '');
            initForForm(prefix);
          }
        }
      });
    }
  }

  // Safe initialization - wait for DOM and optionally jQuery
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    // DOM already loaded
    initialize();
  }

  // Shared State for Keyboard Control
  let activeInstance = null;

  // KEYBOARD CONTROLS (Global Listener)
  document.addEventListener('keydown', (e) => {
    if (!activeInstance) return; // No active tool selected

    // Only handle Arrow Keys
    if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;

    e.preventDefault(); // Prevent scrolling

    // Step size: Shift = 2.0%, Normal = 0.5%
    const step = e.shiftKey ? 2.0 : 0.5;

    // Get current coords from marker style (source of truth)
    let currentX = parseFloat(activeInstance.marker.style.left) || 50;
    let currentY = parseFloat(activeInstance.marker.style.top) || 50;

    switch (e.key) {
      case 'ArrowUp': currentY -= step; break;
      case 'ArrowDown': currentY += step; break;
      case 'ArrowLeft': currentX -= step; break;
      case 'ArrowRight': currentX += step; break;
    }

    // Clamp between 0 and 100
    currentX = Math.max(0, Math.min(100, currentX));
    currentY = Math.max(0, Math.min(100, currentY));

    // Update UI
    activeInstance.marker.style.left = currentX + '%';
    activeInstance.marker.style.top = currentY + '%';

    // Update JSON
    const r = parseInt(activeInstance.radSlider.value);
    const result = {
      "center_x": parseFloat(currentX.toFixed(2)),
      "center_y": parseFloat(currentY.toFixed(2)),
      "radius": r
    };

    activeInstance.correctField.value = JSON.stringify(result, null, 4);

    // Flash status
    activeInstance.status.innerText = `🎮 Nudging: X:${currentX.toFixed(2)}%, Y:${currentY.toFixed(2)}%`;
    activeInstance.status.style.color = '#e67e22'; // Orange for manual control
  });

  return { refresh: scan };
})(typeof django !== 'undefined' && django.jQuery ? django.jQuery : (typeof jQuery !== 'undefined' ? jQuery : undefined));
