// login.js

document.addEventListener('DOMContentLoaded', () => {
    // Tab Switcher Elements
    const iconSwitcherContainer = document.getElementById('iconSwitcher');
    const activeIndicator = document.getElementById('activeIndicator');
    const keyAuthTab = document.getElementById('keyAuthTab');
    const linkAuthTab = document.getElementById('linkAuthTab');
    const keyAuthSection = document.getElementById('keyAuthSection');
    const linkAuthSection = document.getElementById('linkAuthSection');

    // Form Elements
    const accessCodeInput = document.getElementById('accessCode');
    const accessPasswordInput = document.getElementById('accessPassword');
    const accessCodeForm = document.getElementById('accessCodeForm');
    const validationMessageCode = document.getElementById('validationMessageCode');
    const validationMessagePassword = document.getElementById('validationMessagePassword');

    if (!iconSwitcherContainer || !activeIndicator || !keyAuthTab || !linkAuthTab || !keyAuthSection || !linkAuthSection || !accessCodeInput || !accessCodeForm) {
        console.error("One or more required page elements are missing from the DOM for the switcher or form.");
        return;
    }

    const keyIcon = keyAuthTab.querySelector('svg');
    const linkIcon = linkAuthTab.querySelector('svg');

    function updateIndicatorAndIcons(activeTab, inactiveTab, activeSvg, inactiveSvg) {
        const activeIconColor = 'text-sky-600';
        const inactiveIconColor = 'text-slate-500';

        activeIndicator.style.left = activeTab.offsetLeft + 'px';
        activeIndicator.style.width = activeTab.offsetWidth + 'px';

        activeSvg.classList.remove(inactiveIconColor);
        activeSvg.classList.add(activeIconColor);
        inactiveSvg.classList.remove(activeIconColor);
        inactiveSvg.classList.add(inactiveIconColor);
    }

    function switchAuthMethod(selectedMethod) {
        if (selectedMethod === 'key') {
            updateIndicatorAndIcons(keyAuthTab, linkAuthTab, keyIcon, linkIcon);
            keyAuthSection.classList.remove('hidden');
            linkAuthSection.classList.add('hidden');
        } else if (selectedMethod === 'link') {
            updateIndicatorAndIcons(linkAuthTab, keyAuthTab, linkIcon, keyIcon);
            linkAuthSection.classList.remove('hidden');
            keyAuthSection.classList.add('hidden');
        }
    }

    function initializeSwitcher() {
        const initialMethod = 'key';
        const defaultActiveTab = (initialMethod === 'key') ? keyAuthTab : linkAuthTab;

        activeIndicator.style.width = defaultActiveTab.offsetWidth + 'px';
        activeIndicator.style.left = defaultActiveTab.offsetLeft + 'px';

        switchAuthMethod(initialMethod);
    }

    keyAuthTab.addEventListener('click', () => switchAuthMethod('key'));
    linkAuthTab.addEventListener('click', () => switchAuthMethod('link'));
    window.addEventListener('load', initializeSwitcher);

    // --- Access Code Formatting & Basic Validation ---
    const format = [2, 2, 3, 3];
    const totalCodeLength = format.reduce((a, b) => a + b, 0);
    const maxLengthWithDashes = totalCodeLength + (format.length - 1);

    if (accessCodeInput) {
        accessCodeInput.setAttribute('maxlength', maxLengthWithDashes);

        accessCodeInput.addEventListener('input', function (e) {
            let input = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            let originalCursorPosition = e.target.selectionStart;
            let formattedInput = '';
            let rawIndex = 0;
            let dashesBeforeCursorInOriginal = (e.target.value.substring(0, originalCursorPosition).match(/-/g) || []).length;

            for (let i = 0; i < format.length; i++) {
                const segmentLength = format[i];
                if (rawIndex < input.length) {
                    const segment = input.substring(rawIndex, rawIndex + segmentLength);
                    formattedInput += segment;
                    rawIndex += segment.length;
                    if (rawIndex < input.length && i < format.length - 1) {
                        formattedInput += '-';
                    }
                } else {
                    break;
                }
            }
            e.target.value = formattedInput;

            let newCursorPosition = originalCursorPosition;
            let dashesInNewFormattedUpToOriginalRaw = (formattedInput.substring(0, Math.max(0, originalCursorPosition - dashesBeforeCursorInOriginal) + (formattedInput.match(/-/g) || []).length).match(/-/g) || []).length;

            if (e.inputType && e.inputType.startsWith('delete')) {
                newCursorPosition = originalCursorPosition;
            } else {
                newCursorPosition = (originalCursorPosition - dashesBeforeCursorInOriginal) + dashesInNewFormattedUpToOriginalRaw;
            }
            newCursorPosition = Math.max(0, Math.min(newCursorPosition, formattedInput.length));

            try {
                requestAnimationFrame(() => {
                    e.target.setSelectionRange(newCursorPosition, newCursorPosition);
                });
            } catch (error) {}

            if (validationMessageCode) {
                if (input.length > 0 && input.length < totalCodeLength) {
                    validationMessageCode.textContent = `Code requires ${totalCodeLength} characters.`;
                } else {
                    validationMessageCode.textContent = '';
                }
            }
        });
    }

    if (accessCodeForm) {
        accessCodeForm.addEventListener('submit', function (event) {
            event.preventDefault();

            if (validationMessageCode) validationMessageCode.textContent = '';
            if (validationMessagePassword) validationMessagePassword.textContent = '';

            const enteredRawCode = accessCodeInput ? accessCodeInput.value.replace(/-/g, '') : '';
            const enteredPassword = accessPasswordInput ? accessPasswordInput.value : '';

            if (enteredRawCode.length !== totalCodeLength) {
                if (validationMessageCode) validationMessageCode.textContent = 'Invalid code length. Please enter the full code.';
                if (accessCodeInput) accessCodeInput.focus();
                return;
            }

            const typeAndExtra = enteredRawCode.substring(7);
            if (typeAndExtra.length !== 3) {
                if (validationMessageCode) validationMessageCode.textContent = 'Invalid code format (suffix).';
                if (accessCodeInput) accessCodeInput.focus();
                return;
            }

            if (!enteredPassword && accessPasswordInput) {
                if (validationMessagePassword) validationMessagePassword.textContent = 'Password is required.';
                accessPasswordInput.focus();
                return;
            }

            alert('Form passed front-end validation. Ready to send to backend.');
        });
    }
});
